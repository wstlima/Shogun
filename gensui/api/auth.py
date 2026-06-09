"""Auth API — admin login and session management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin
from gensui.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    admin: dict


class AdminProfile(BaseModel):
    id: str
    email: str
    role: str
    display_name: str


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate an admin user and return a JWT token."""
    auth = AuthService(db)
    admin = await auth.authenticate(req.email, req.password)
    if admin is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = AuthService.create_token(str(admin.id), admin.email, admin.role)

    return LoginResponse(
        token=token,
        admin={
            "id": str(admin.id),
            "email": admin.email,
            "role": admin.role,
            "display_name": admin.display_name,
        },
    )


@router.get("/me")
async def get_profile(admin: dict = Depends(get_current_admin)):
    """Get the current admin's profile."""
    return admin


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Change the current admin's password."""
    auth = AuthService(db)
    user = await auth.get_by_id(uuid.UUID(admin["id"]))
    if user is None:
        raise HTTPException(status_code=404, detail="Admin not found")

    if not AuthService.verify_password(req.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    user.password_hash = AuthService.hash_password(req.new_password)
    await db.commit()
    return {"status": "ok", "message": "Password changed successfully"}


@router.patch("/profile")
async def update_profile(
    req: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Update the current admin's profile."""
    auth = AuthService(db)
    user = await auth.get_by_id(uuid.UUID(admin["id"]))
    if user is None:
        raise HTTPException(status_code=404, detail="Admin not found")

    if req.display_name is not None:
        user.display_name = req.display_name

    await db.commit()
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "display_name": user.display_name,
    }
