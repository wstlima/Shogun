"""Calendar service for CalDAV synchronization."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import uuid
from typing import Any

import caldav
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.email_account import EmailAccount
from shogun.schemas.channels import CalendarEventCreate, CalendarEventResponse
from shogun.services.base_service import BaseService
from shogun.services.email_service import decrypt_password


def parse_ical_date(val: str) -> datetime:
    val = val.strip()
    if "T" in val:
        if val.endswith("Z"):
            dt = datetime.strptime(val, "%Y%m%dT%H%M%SZ")
            return dt.replace(tzinfo=timezone.utc)
        else:
            try:
                return datetime.strptime(val, "%Y%m%dT%H%M%S")
            except ValueError:
                # Handle dates with offset or subseconds
                clean_val = val.split("+")[0].split("-")[0]
                return datetime.strptime(clean_val[:15], "%Y%m%dT%H%M%S")
    else:
        dt = datetime.strptime(val[:8], "%Y%m%d")
        return dt.replace(tzinfo=timezone.utc)


def parse_ical(ical_text: str) -> dict[str, Any]:
    """Parse raw iCalendar text into dict."""
    lines = ical_text.replace("\r\n ", "").replace("\r\n\t", "").splitlines()
    data: dict[str, Any] = {
        "location": "",
        "description": "",
        "all_day": False,
    }
    for line in lines:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key_clean = key.split(";")[0].upper()
        val = val.replace("\\,", ",").replace("\\;", ";").replace("\\N", "\n").replace("\\n", "\n")

        if key_clean == "SUMMARY":
            data["title"] = val
        elif key_clean == "DTSTART":
            data["start"] = parse_ical_date(val)
            if "VALUE=DATE" in key.upper():
                data["all_day"] = True
        elif key_clean == "DTEND":
            data["end"] = parse_ical_date(val)
        elif key_clean == "LOCATION":
            data["location"] = val
        elif key_clean == "DESCRIPTION":
            data["description"] = val
        elif key_clean == "UID":
            data["id"] = val
    return data


class CalendarService(BaseService[EmailAccount]):
    """Service to handle CalDAV calendar operations governed by Katana permissions."""

    def __init__(self, session: AsyncSession):
        super().__init__(EmailAccount, session)

    async def get_account(self) -> EmailAccount | None:
        """Fetch the single calendar account configuration."""
        result = await self.session.execute(select(self.model).limit(1))
        return result.scalars().first()

    async def get_events(self, start_date: datetime, end_date: datetime) -> list[CalendarEventResponse]:
        """Fetch events in a date range via CalDAV."""
        acc = await self.get_account()
        if not acc:
            raise HTTPException(status_code=404, detail="No email/calendar account configured")
        if not acc.perm_read_calendar:
            raise HTTPException(status_code=403, detail="Permission denied: perm_read_calendar is disabled")
        if acc.calendar_provider == "none" or not acc.caldav_url:
            return []

        password = decrypt_password(acc.encrypted_password)

        def _fetch():
            client = caldav.DAVClient(
                url=acc.caldav_url,
                username=acc.username,
                password=password,
            )
            principal = client.principal()
            calendars = principal.calendars()

            parsed_events = []
            for cal in calendars:
                events = cal.date_search(start=start_date, end=end_date)
                for ev in events:
                    try:
                        info = parse_ical(ev.data)
                        if "id" not in info:
                            continue
                        parsed_events.append(CalendarEventResponse(
                            id=info["id"],
                            title=info.get("title", "(No Title)"),
                            start=info["start"],
                            end=info.get("end", info["start"]),
                            location=info.get("location"),
                            description=info.get("description"),
                            all_day=info.get("all_day", False),
                            color=acc.provider,
                        ))
                    except Exception:
                        pass
            return parsed_events

        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch calendar: {str(e)}")

    async def create_event(self, data: CalendarEventCreate) -> CalendarEventResponse:
        """Create an event via CalDAV."""
        acc = await self.get_account()
        if not acc:
            raise HTTPException(status_code=404, detail="No email/calendar account configured")
        if not acc.perm_create_events:
            raise HTTPException(status_code=403, detail="Permission denied: perm_create_events is disabled")
        if acc.calendar_provider == "none" or not acc.caldav_url:
            raise HTTPException(status_code=400, detail="Calendar integration is not configured or enabled")

        password = decrypt_password(acc.encrypted_password)
        uid = str(uuid.uuid4())

        def _create():
            client = caldav.DAVClient(
                url=acc.caldav_url,
                username=acc.username,
                password=password,
            )
            principal = client.principal()
            calendars = principal.calendars()
            if not calendars:
                raise Exception("No calendars found on the server.")

            calendar = calendars[0]  # default to first calendar

            dtstamp_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            start_str = data.start.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            end_str = data.end.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

            event_ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Shogun//NONSGML Calendar//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp_str}
SUMMARY:{data.title}
DTSTART:{start_str}
DTEND:{end_str}
DESCRIPTION:{data.description or ""}
LOCATION:{data.location or ""}
END:VEVENT
END:VCALENDAR"""

            calendar.add_event(event_ical)
            return CalendarEventResponse(
                id=uid,
                title=data.title,
                start=data.start,
                end=data.end,
                location=data.location,
                description=data.description,
                all_day=data.all_day,
                color=acc.provider,
            )

        try:
            return await asyncio.to_thread(_create)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

    async def update_event(self, event_id: str, data: CalendarEventCreate) -> CalendarEventResponse:
        """Update an event by deleting and re-creating it with the same ID."""
        acc = await self.get_account()
        if not acc:
            raise HTTPException(status_code=404, detail="No email/calendar account configured")
        if not acc.perm_edit_events:
            raise HTTPException(status_code=403, detail="Permission denied: perm_edit_events is disabled")
        if acc.calendar_provider == "none" or not acc.caldav_url:
            raise HTTPException(status_code=400, detail="Calendar integration is not configured or enabled")

        password = decrypt_password(acc.encrypted_password)

        def _update():
            client = caldav.DAVClient(
                url=acc.caldav_url,
                username=acc.username,
                password=password,
            )
            principal = client.principal()
            calendars = principal.calendars()

            # Delete existing
            deleted = False
            for cal in calendars:
                try:
                    ev = cal.event_by_uid(event_id)
                    ev.delete()
                    deleted = True
                    break
                except Exception:
                    pass

            if not deleted:
                raise Exception("Event to update was not found.")

            # Create new with same ID
            calendar = calendars[0]
            dtstamp_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            start_str = data.start.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            end_str = data.end.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

            event_ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Shogun//NONSGML Calendar//EN
BEGIN:VEVENT
UID:{event_id}
DTSTAMP:{dtstamp_str}
SUMMARY:{data.title}
DTSTART:{start_str}
DTEND:{end_str}
DESCRIPTION:{data.description or ""}
LOCATION:{data.location or ""}
END:VEVENT
END:VCALENDAR"""

            calendar.add_event(event_ical)
            return CalendarEventResponse(
                id=event_id,
                title=data.title,
                start=data.start,
                end=data.end,
                location=data.location,
                description=data.description,
                all_day=data.all_day,
                color=acc.provider,
            )

        try:
            return await asyncio.to_thread(_update)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

    async def delete_event(self, event_id: str) -> dict[str, Any]:
        """Delete an event via CalDAV."""
        acc = await self.get_account()
        if not acc:
            raise HTTPException(status_code=404, detail="No email/calendar account configured")
        if not acc.perm_delete_events:
            raise HTTPException(status_code=403, detail="Permission denied: perm_delete_events is disabled")
        if acc.calendar_provider == "none" or not acc.caldav_url:
            raise HTTPException(status_code=400, detail="Calendar integration is not configured or enabled")

        password = decrypt_password(acc.encrypted_password)

        def _delete():
            client = caldav.DAVClient(
                url=acc.caldav_url,
                username=acc.username,
                password=password,
            )
            principal = client.principal()
            calendars = principal.calendars()

            deleted = False
            for cal in calendars:
                try:
                    ev = cal.event_by_uid(event_id)
                    ev.delete()
                    deleted = True
                    break
                except Exception:
                    pass

            if not deleted:
                raise Exception("Event was not found or could not be deleted.")
            return {"ok": True, "message": "Event deleted successfully."}

        try:
            return await asyncio.to_thread(_delete)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")
