"""API dependencies — database sessions, auth guards, role enforcement."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.db.engine import get_async_session
from gensui.services.auth_service import AuthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session."""
    async for session in get_async_session():
        yield session


async def get_current_admin(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Extract and validate the current admin from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split("Bearer ")[1]
    try:
        payload = AuthService.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    auth = AuthService(db)
    admin = await auth.get_by_id(uuid.UUID(admin_id))
    if admin is None or not admin.is_active:
        raise HTTPException(status_code=401, detail="Admin account not found or inactive")

    return {
        "id": str(admin.id),
        "email": admin.email,
        "role": admin.role,
        "display_name": admin.display_name,
    }


def require_role(*allowed_roles: str):
    """Dependency factory that requires the admin to have one of the specified roles."""

    async def _check(admin: dict = Depends(get_current_admin)) -> dict:
        if admin["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{admin['role']}' is not authorized for this operation. "
                       f"Required: {', '.join(allowed_roles)}",
            )
        return admin

    return _check


# ── Shogun Membership Auth ───────────────────────────────────

async def get_shogun_identity(
    x_shogun_id: str = Header(None),
    x_shogun_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Validate a Shogun instance's identity from request headers."""
    if not x_shogun_id:
        raise HTTPException(status_code=401, detail="Missing X-Shogun-Id header")

    from gensui.services.member_service import MemberService
    svc = MemberService(db)

    try:
        member = await svc.get_by_id(uuid.UUID(x_shogun_id))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Shogun ID format")

    if member is None:
        raise HTTPException(status_code=401, detail="Unknown Shogun instance")

    if member.enrollment_status != "active":
        raise HTTPException(status_code=403, detail=f"Shogun enrollment status: {member.enrollment_status}")

    return {
        "shogun_id": str(member.id),
        "instance_name": member.instance_name,
        "enrollment_status": member.enrollment_status,
    }
