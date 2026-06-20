"""Enterprise Identity Service — service accounts, API keys, and SSO/OIDC management.

Provides:
- Service account CRUD with hashed API keys
- API key generation and validation
- SSO/OIDC provider CRUD
- OIDC token validation (via provider discovery)
- Role mapping from external claims
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.config import gensui_settings
from gensui.db.models.service_account import ServiceAccount
from gensui.db.models.sso_provider import SSOProvider

log = logging.getLogger("gensui.identity")


class IdentityService:
    """Manages service accounts and SSO providers."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ══════════════════════════════════════════════════════════
    # Service Accounts
    # ══════════════════════════════════════════════════════════

    @staticmethod
    def _hash_api_key(key: str) -> str:
        """Hash an API key using HMAC-SHA256."""
        return hmac.new(
            gensui_settings.gensui_jwt_secret.encode("utf-8"),
            key.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def generate_api_key() -> str:
        """Generate a cryptographically secure API key."""
        return f"gsk_{secrets.token_urlsafe(48)}"

    async def create_service_account(
        self,
        name: str,
        description: str | None = None,
        role: str = "readonly",
        scopes: dict | None = None,
        rate_limit_rpm: int = 60,
        expires_at: datetime | None = None,
        created_by: str | None = None,
    ) -> tuple[ServiceAccount, str]:
        """Create a service account and return (account, raw_api_key).

        The raw API key is only returned once — it cannot be retrieved later.
        """
        raw_key = self.generate_api_key()
        key_hash = self._hash_api_key(raw_key)
        key_prefix = raw_key[:12]

        sa = ServiceAccount(
            name=name,
            description=description,
            api_key_hash=key_hash,
            api_key_prefix=key_prefix,
            role=role,
            scopes_json=scopes,
            rate_limit_rpm=rate_limit_rpm,
            expires_at=expires_at,
            created_by=created_by,
        )
        self.session.add(sa)
        await self.session.flush()
        await self.session.refresh(sa)

        log.info("Created service account '%s' (role=%s, prefix=%s)", name, role, key_prefix)
        return sa, raw_key

    async def validate_api_key(self, api_key: str) -> ServiceAccount | None:
        """Validate an API key and return the service account if valid."""
        key_hash = self._hash_api_key(api_key)

        result = await self.session.execute(
            select(ServiceAccount)
            .where(ServiceAccount.api_key_hash == key_hash)
            .where(ServiceAccount.is_active == True)
        )
        sa = result.scalars().first()

        if sa is None:
            return None

        # Check expiry
        if sa.expires_at and sa.expires_at < datetime.now(timezone.utc):
            log.warning("API key for '%s' has expired", sa.name)
            return None

        # Update usage stats
        sa.last_used_at = datetime.now(timezone.utc)
        sa.usage_count = (sa.usage_count or 0) + 1
        await self.session.flush()

        return sa

    async def list_service_accounts(self) -> list[ServiceAccount]:
        """List all service accounts."""
        result = await self.session.execute(
            select(ServiceAccount).order_by(ServiceAccount.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_service_account(self, sa_id: uuid.UUID) -> ServiceAccount | None:
        """Get a service account by ID."""
        result = await self.session.execute(
            select(ServiceAccount).where(ServiceAccount.id == sa_id)
        )
        return result.scalars().first()

    async def update_service_account(
        self,
        sa_id: uuid.UUID,
        **kwargs,
    ) -> ServiceAccount | None:
        """Update a service account."""
        sa = await self.get_service_account(sa_id)
        if sa is None:
            return None

        for key, value in kwargs.items():
            if hasattr(sa, key) and key not in ("id", "api_key_hash", "api_key_prefix"):
                setattr(sa, key, value)

        sa.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(sa)
        return sa

    async def revoke_service_account(self, sa_id: uuid.UUID) -> bool:
        """Revoke (deactivate) a service account."""
        sa = await self.get_service_account(sa_id)
        if sa is None:
            return False
        sa.is_active = False
        sa.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        log.info("Revoked service account '%s'", sa.name)
        return True

    async def rotate_api_key(self, sa_id: uuid.UUID) -> tuple[ServiceAccount, str] | None:
        """Rotate the API key for a service account."""
        sa = await self.get_service_account(sa_id)
        if sa is None:
            return None

        raw_key = self.generate_api_key()
        sa.api_key_hash = self._hash_api_key(raw_key)
        sa.api_key_prefix = raw_key[:12]
        sa.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(sa)

        log.info("Rotated API key for service account '%s'", sa.name)
        return sa, raw_key

    # ══════════════════════════════════════════════════════════
    # SSO / OIDC Providers
    # ══════════════════════════════════════════════════════════

    async def create_sso_provider(
        self,
        name: str,
        provider_type: str = "oidc",
        issuer_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        discovery_url: str | None = None,
        scopes: str = "openid profile email",
        audience: str | None = None,
        claim_mapping: dict | None = None,
        default_role: str = "readonly",
        role_mapping: dict | None = None,
        auto_create_users: bool = False,
        auto_activate_users: bool = False,
        allowed_domains: str | None = None,
        is_primary: bool = False,
        created_by: str | None = None,
    ) -> SSOProvider:
        """Create an SSO/OIDC provider configuration."""
        # Encrypt client secret (simple XOR for now — replace with real encryption in production)
        encrypted_secret = None
        if client_secret:
            encrypted_secret = self._encrypt_secret(client_secret)

        provider = SSOProvider(
            name=name,
            provider_type=provider_type,
            issuer_url=issuer_url,
            client_id=client_id,
            client_secret_encrypted=encrypted_secret,
            discovery_url=discovery_url or (f"{issuer_url}/.well-known/openid-configuration" if issuer_url else None),
            scopes=scopes,
            audience=audience,
            claim_mapping_json=claim_mapping,
            default_role=default_role,
            role_mapping_json=role_mapping,
            auto_create_users=auto_create_users,
            auto_activate_users=auto_activate_users,
            allowed_domains=allowed_domains,
            is_primary=is_primary,
            created_by=created_by,
        )
        self.session.add(provider)
        await self.session.flush()
        await self.session.refresh(provider)

        log.info("Created SSO provider '%s' (%s)", name, provider_type)
        return provider

    async def list_sso_providers(self) -> list[SSOProvider]:
        """List all SSO providers."""
        result = await self.session.execute(
            select(SSOProvider).order_by(SSOProvider.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_sso_provider(self, provider_id: uuid.UUID) -> SSOProvider | None:
        """Get an SSO provider by ID."""
        result = await self.session.execute(
            select(SSOProvider).where(SSOProvider.id == provider_id)
        )
        return result.scalars().first()

    async def get_primary_sso_provider(self) -> SSOProvider | None:
        """Get the primary (login page) SSO provider."""
        result = await self.session.execute(
            select(SSOProvider)
            .where(SSOProvider.is_primary == True)
            .where(SSOProvider.is_active == True)
        )
        return result.scalars().first()

    async def update_sso_provider(
        self,
        provider_id: uuid.UUID,
        **kwargs,
    ) -> SSOProvider | None:
        """Update an SSO provider."""
        provider = await self.get_sso_provider(provider_id)
        if provider is None:
            return None

        # Handle client_secret specially (encrypt)
        if "client_secret" in kwargs:
            secret = kwargs.pop("client_secret")
            if secret:
                provider.client_secret_encrypted = self._encrypt_secret(secret)

        for key, value in kwargs.items():
            if hasattr(provider, key) and key not in ("id", "client_secret_encrypted"):
                setattr(provider, key, value)

        provider.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(provider)
        return provider

    async def delete_sso_provider(self, provider_id: uuid.UUID) -> bool:
        """Delete an SSO provider."""
        provider = await self.get_sso_provider(provider_id)
        if provider is None:
            return False
        await self.session.delete(provider)
        await self.session.flush()
        log.info("Deleted SSO provider '%s'", provider.name)
        return True

    async def validate_oidc_token(self, token: str, provider_id: uuid.UUID | None = None) -> dict | None:
        """Validate an OIDC token against a configured provider.

        Returns the decoded claims if valid, None otherwise.
        This is a simplified implementation — production should use
        proper JWKS verification from the provider's discovery endpoint.
        """
        import jwt as pyjwt

        # Get provider
        if provider_id:
            provider = await self.get_sso_provider(provider_id)
        else:
            provider = await self.get_primary_sso_provider()

        if provider is None:
            return None

        try:
            # Decode without verification first to get the header
            unverified = pyjwt.decode(token, options={"verify_signature": False})

            # Basic validation
            if provider.audience and unverified.get("aud") != provider.audience:
                log.warning("OIDC token audience mismatch")
                return None

            if provider.issuer_url and unverified.get("iss") != provider.issuer_url:
                log.warning("OIDC token issuer mismatch")
                return None

            # Map claims
            claims = {}
            mapping = provider.claim_mapping_json or {
                "email": "email",
                "name": "preferred_username",
            }
            for local_key, remote_key in mapping.items():
                claims[local_key] = unverified.get(remote_key)

            # Map role
            role_mapping = provider.role_mapping_json or {}
            external_roles = []
            # Try to extract roles from common claim paths
            for path in ["realm_access.roles", "roles", "groups"]:
                parts = path.split(".")
                val = unverified
                for p in parts:
                    if isinstance(val, dict):
                        val = val.get(p)
                if isinstance(val, list):
                    external_roles.extend(val)

            mapped_role = provider.default_role
            for ext_role, int_role in role_mapping.items():
                if ext_role in external_roles:
                    mapped_role = int_role
                    break

            claims["role"] = mapped_role
            claims["provider_id"] = str(provider.id)
            claims["provider_name"] = provider.name

            return claims

        except Exception as e:
            log.error("OIDC token validation failed: %s", e)
            return None

    # ── Encryption helpers ───────────────────────────────────

    @staticmethod
    def _encrypt_secret(value: str) -> str:
        """Simple obfuscation of secrets at rest.

        NOTE: In production, use proper AES-256-GCM encryption
        with a hardware-backed key. This is a basic XOR obfuscation
        suitable for development environments.
        """
        key = gensui_settings.gensui_jwt_secret.encode("utf-8")
        result = []
        for i, char in enumerate(value.encode("utf-8")):
            result.append(char ^ key[i % len(key)])
        return result.__class__(result).hex()

    @staticmethod
    def _decrypt_secret(encrypted: str) -> str:
        """Reverse the obfuscation."""
        key = gensui_settings.gensui_jwt_secret.encode("utf-8")
        data = bytes.fromhex(encrypted)
        result = []
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result).decode("utf-8")
