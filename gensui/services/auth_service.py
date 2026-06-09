"""Auth service — JWT generation, password hashing, admin management."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.config import gensui_settings
from gensui.db.models.admin_user import AdminUser


class AuthService:
    """Authentication and admin user management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Password Hashing ─────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    # ── JWT Tokens ───────────────────────────────────────────

    @staticmethod
    def create_token(admin_id: str, email: str, role: str) -> str:
        """Create a JWT access token."""
        payload = {
            "sub": admin_id,
            "email": email,
            "role": role,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=gensui_settings.gensui_jwt_expire_hours),
            "jti": uuid.uuid4().hex,
        }
        return jwt.encode(
            payload,
            gensui_settings.gensui_jwt_secret,
            algorithm=gensui_settings.gensui_jwt_algorithm,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token."""
        return jwt.decode(
            token,
            gensui_settings.gensui_jwt_secret,
            algorithms=[gensui_settings.gensui_jwt_algorithm],
        )

    # ── Admin CRUD ───────────────────────────────────────────

    async def get_by_email(self, email: str) -> AdminUser | None:
        """Fetch an admin user by email."""
        result = await self.session.execute(
            select(AdminUser).where(AdminUser.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, admin_id: uuid.UUID) -> AdminUser | None:
        """Fetch an admin user by ID."""
        result = await self.session.execute(
            select(AdminUser).where(AdminUser.id == admin_id)
        )
        return result.scalars().first()

    async def authenticate(self, email: str, password: str) -> AdminUser | None:
        """Authenticate an admin user. Returns the user if valid, None otherwise."""
        user = await self.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        # Update last login
        user.last_login_at = datetime.now(timezone.utc).isoformat()
        await self.session.flush()
        return user

    async def create_admin(
        self,
        email: str,
        password: str,
        display_name: str = "Admin",
        role: str = "admin",
    ) -> AdminUser:
        """Create a new admin user."""
        admin = AdminUser(
            email=email,
            password_hash=self.hash_password(password),
            display_name=display_name,
            role=role,
        )
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)
        return admin

    async def list_admins(self) -> list[AdminUser]:
        """List all admin users."""
        result = await self.session.execute(
            select(AdminUser).where(AdminUser.is_active == True)
        )
        return list(result.scalars().all())
