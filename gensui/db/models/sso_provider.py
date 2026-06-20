"""SSO/OIDC provider configuration model.

Stores configuration for external identity providers:
- OpenID Connect (Keycloak, Auth0, Okta, Azure AD, Google)
- SAML 2.0 (future)
- SPIFFE/SPIRE trust domains (future)
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class SSOProvider(Base, UUIDMixin):
    """An OIDC/SSO identity provider configuration."""

    __tablename__ = "sso_providers"

    # ── Provider Identity ────────────────────────────────────
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False, default="oidc")
    # Types: oidc, saml, spiffe

    # ── OIDC Configuration ───────────────────────────────────
    issuer_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    client_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    client_secret_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    discovery_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # .well-known/openid-configuration

    # ── Token Configuration ──────────────────────────────────
    scopes: Mapped[str] = mapped_column(String(500), nullable=False, default="openid profile email")
    audience: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # ── Claim Mapping ────────────────────────────────────────
    claim_mapping_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    # e.g. {"email": "email", "name": "preferred_username", "role": "realm_access.roles"}

    # ── Role Mapping ─────────────────────────────────────────
    default_role: Mapped[str] = mapped_column(String(50), nullable=False, default="readonly")
    role_mapping_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    # e.g. {"gensui_admin": "admin", "gensui_auditor": "auditor", "gensui_operator": "operator"}

    # ── Auto-Provisioning ────────────────────────────────────
    auto_create_users: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_activate_users: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_domains: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Comma-separated list of allowed email domains

    # ── Status ───────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Primary provider is used for the login page SSO button

    # ── Metadata ─────────────────────────────────────────────
    created_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
