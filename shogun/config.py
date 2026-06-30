"""Shogun application settings.

Loads configuration from environment variables / .env file.
All paths, credentials, and feature flags are centralized here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Root configuration for the Shogun runtime."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "production"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ui_port: int = 7860

    # ── Database (SQLite by default) ────────────
    database_url: str = f"sqlite+aiosqlite:///{PROJECT_ROOT}/data/shogun.db"

    # ── Qdrant (Embedded by default) ──────
    qdrant_url: str | None = None
    qdrant_path: Path = PROJECT_ROOT / "data" / "qdrant"

    # ── Security ─────────────────────────────────────────────
    secret_key: str = "change-me-to-a-random-64-char-string"
    vault_encryption_key: str = "change-me-to-a-fernet-base64-key"

    # ── Storage Paths ────────────────────────────────────────
    vault_path: Path = PROJECT_ROOT / "vault"
    log_path: Path = PROJECT_ROOT / "logs"
    config_path: Path = PROJECT_ROOT / "configs"
    uploads_path: Path = PROJECT_ROOT / "data" / "uploads"
    mado_path: Path = PROJECT_ROOT / "data" / "mado"
    ronin_path: Path = PROJECT_ROOT / "data" / "ronin"
    office_path: Path = PROJECT_ROOT / "data" / "office"

    # ── Telegram ─────────────────────────────────────────────
    telegram_bot_token: str | None = None
    telegram_allowed_chat_ids: str | None = None

    # ── GitHub (for update checker on private repos) ─────────
    github_token: str | None = None

    # ── Gensui Membership ────────────────────────────────────
    gensui_enabled: bool = False
    gensui_server_url: str = "http://localhost:8787"
    gensui_enrollment_token: str | None = None
    gensui_instance_name: str = "Shogun Instance"
    gensui_environment: str = "development"
    gensui_heartbeat_interval_seconds: int = 15
    gensui_command_poll_interval_seconds: int = 5
    gensui_policy_sync_interval_seconds: int = 30
    gensui_disconnect_behavior: str = "CONTINUE_LAST_POLICY"
    gensui_telemetry_mode: str = "STANDARD"
    gensui_data_path: Path = PROJECT_ROOT / "data"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def ensure_directories(self) -> None:
        """Create required filesystem directories if they don't exist."""
        for directory in [
            PROJECT_ROOT / "data",
            self.qdrant_path,
            self.vault_path,
            self.vault_path / "skills",
            self.vault_path / "snapshots",
            self.vault_path / "backups",
            self.log_path,
            self.config_path,
            self.uploads_path,
            # Mado browser automation directories
            self.mado_path,
            self.mado_path / "profiles",
            self.mado_path / "downloads",
            self.mado_path / "sessions",
            self.mado_path / "cache",
            self.mado_path / "screenshots",
            # Ronin desktop automation directories
            self.ronin_path,
            self.ronin_path / "screenshots",
            # Office App Mode directories
            self.office_path,
            self.office_path / "temp",
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
