"""Outlook Adapter — COM-only automation for Microsoft Outlook.

Outlook has no pure-Python alternative for creating drafts and sending email
through the user's configured Exchange/IMAP/SMTP account. All operations go
through the STA COM thread pool.

Design: Composite-first API. ``create_draft()`` accepts all fields in a single
call to minimize COM calls. Refinement tools allow incremental changes.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

log = logging.getLogger("shogun.office.adapters.outlook")


# ── Draft Tracking ───────────────────────────────────────────────────


class DraftResult:
    """Result of creating or modifying an Outlook draft."""

    def __init__(self, draft_id: str, entry_id: str = "", subject: str = ""):
        self.draft_id = draft_id
        self.entry_id = entry_id
        self.subject = subject

    def to_dict(self) -> dict:
        return {
            "draft_id": self.draft_id,
            "entry_id": self.entry_id,
            "subject": self.subject,
        }


# Track drafts in memory (COM MailItem EntryIDs keyed by our draft_id)
_draft_registry: dict[str, str] = {}  # draft_id → EntryID


# ── COM Functions (all synchronous, run via STA pool) ────────────────


def _com_create_draft(
    recipients: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    body_format: str = "html",
    attachments: list[str] | None = None,
) -> dict[str, str]:
    """Create an Outlook draft email via COM.

    Must be called on the STA thread pool.

    Returns dict with draft_id and entry_id.
    """
    import win32com.client

    outlook = win32com.client.Dispatch("Outlook.Application")
    # olMailItem = 0
    mail = outlook.CreateItem(0)

    # Recipients
    mail.To = "; ".join(recipients)
    if cc:
        mail.CC = "; ".join(cc)
    if bcc:
        mail.BCC = "; ".join(bcc)

    # Subject and Body
    mail.Subject = subject
    if body_format.lower() == "html":
        mail.HTMLBody = body
    else:
        mail.Body = body

    # Attachments
    if attachments:
        for att_path in attachments:
            abs_path = str(Path(att_path).resolve())
            if Path(abs_path).exists():
                mail.Attachments.Add(abs_path)
            else:
                log.warning("Attachment not found, skipping: %s", att_path)

    # Save as draft
    mail.Save()

    draft_id = f"draft_{uuid.uuid4().hex[:12]}"
    entry_id = mail.EntryID

    _draft_registry[draft_id] = entry_id

    log.info("Created Outlook draft: %s (to=%s, subject=%s)", draft_id, recipients, subject)
    return {
        "draft_id": draft_id,
        "entry_id": entry_id,
        "subject": subject,
    }


def _com_get_draft(draft_id: str) -> Any:
    """Retrieve a saved draft by its tracked draft_id.

    Must be called on the STA thread pool.
    Returns the COM MailItem object.
    """
    import win32com.client

    entry_id = _draft_registry.get(draft_id)
    if not entry_id:
        raise ValueError(f"Draft '{draft_id}' not found. It may have been sent or deleted.")

    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    try:
        mail = namespace.GetItemFromID(entry_id)
        return mail
    except Exception as exc:
        raise ValueError(f"Could not retrieve draft '{draft_id}': {exc}")


def _com_set_recipients(draft_id: str, recipients: list[str]) -> None:
    """Update the recipients of a draft."""
    mail = _com_get_draft(draft_id)
    mail.To = "; ".join(recipients)
    mail.Save()
    log.debug("Updated recipients for draft %s", draft_id)


def _com_set_subject(draft_id: str, subject: str) -> None:
    """Update the subject of a draft."""
    mail = _com_get_draft(draft_id)
    mail.Subject = subject
    mail.Save()
    log.debug("Updated subject for draft %s", draft_id)


def _com_set_body(draft_id: str, body: str, body_format: str = "html") -> None:
    """Update the body of a draft."""
    mail = _com_get_draft(draft_id)
    if body_format.lower() == "html":
        mail.HTMLBody = body
    else:
        mail.Body = body
    mail.Save()
    log.debug("Updated body for draft %s", draft_id)


def _com_attach_file(draft_id: str, file_path: str) -> None:
    """Attach a file to a draft."""
    mail = _com_get_draft(draft_id)
    abs_path = str(Path(file_path).resolve())
    if not Path(abs_path).exists():
        raise FileNotFoundError(f"Attachment file not found: {file_path}")
    mail.Attachments.Add(abs_path)
    mail.Save()
    log.info("Attached file to draft %s: %s", draft_id, Path(abs_path).name)


def _com_save_draft(draft_id: str) -> None:
    """Explicitly save a draft."""
    mail = _com_get_draft(draft_id)
    mail.Save()
    log.debug("Saved draft %s", draft_id)


def _com_open_draft_for_review(draft_id: str) -> None:
    """Make Outlook visible and display the draft for human review."""
    mail = _com_get_draft(draft_id)
    mail.Display()
    log.info("Opened draft %s for human review", draft_id)


def _com_send(draft_id: str) -> None:
    """Send a draft email.

    This is a HIGH-RISK operation — should only be called after
    ToolGate CONFIRM flow and posture check.
    """
    mail = _com_get_draft(draft_id)
    mail.Send()
    # Remove from tracking
    _draft_registry.pop(draft_id, None)
    log.info("Sent email from draft %s", draft_id)


def _com_get_draft_metadata(draft_id: str) -> dict[str, Any]:
    """Get metadata about a draft."""
    mail = _com_get_draft(draft_id)
    return {
        "draft_id": draft_id,
        "to": mail.To,
        "cc": mail.CC or "",
        "bcc": mail.BCC or "",
        "subject": mail.Subject,
        "body_length": len(mail.Body or ""),
        "has_html_body": bool(mail.HTMLBody),
        "attachment_count": mail.Attachments.Count,
        "attachments": [mail.Attachments.Item(i + 1).FileName for i in range(mail.Attachments.Count)],
        "created": str(mail.CreationTime),
    }


# ── Async Wrappers ───────────────────────────────────────────────────


async def create_draft(
    recipients: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    body_format: str = "html",
    attachments: list[str] | None = None,
) -> DraftResult:
    """Create an Outlook draft email — composite, single-call API."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        result = await run_com(
            _com_create_draft, recipients, subject, body,
            cc, bcc, body_format, attachments,
        )
        return DraftResult(
            draft_id=result["draft_id"],
            entry_id=result["entry_id"],
            subject=result["subject"],
        )


async def set_recipients(draft_id: str, recipients: list[str]) -> None:
    """Update draft recipients."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_set_recipients, draft_id, recipients)


async def set_subject(draft_id: str, subject: str) -> None:
    """Update draft subject."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_set_subject, draft_id, subject)


async def set_body(draft_id: str, body: str, body_format: str = "html") -> None:
    """Update draft body."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_set_body, draft_id, body, body_format)


async def attach_file(draft_id: str, file_path: str) -> None:
    """Attach a file to a draft."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_attach_file, draft_id, file_path)


async def save_draft(draft_id: str) -> None:
    """Save a draft."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_save_draft, draft_id)


async def open_draft_for_review(draft_id: str) -> None:
    """Open a draft in Outlook for human review."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_open_draft_for_review, draft_id)


async def send_with_confirmation(draft_id: str) -> None:
    """Send an email. HIGH-RISK — requires ToolGate CONFIRM flow."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        await run_com(_com_send, draft_id)


async def get_draft_metadata(draft_id: str) -> dict[str, Any]:
    """Get draft metadata."""
    from shogun.office.com_thread_pool import run_com, office_lock
    async with office_lock("outlook"):
        return await run_com(_com_get_draft_metadata, draft_id)
