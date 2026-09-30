"""
ChurnSense AI — Application Configuration
Centralized settings loaded from environment variables.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Compute absolute paths so pydantic-settings finds .env regardless of
# which directory uvicorn / alembic is launched from.
# This file is at: backend/app/core/config.py
# backend/ root is two levels up from here.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)

# Search order: backend/.env first, then project root .env
_ENV_FILES = (
    os.path.join(_BACKEND_DIR, ".env"),   # backend/.env  (if you copy it here)
    os.path.join(_PROJECT_ROOT, ".env"),  # project root .env  (where it actually lives)
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "ChurnSense AI"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False

    # ── Security ─────────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ── Database ─────────────────────────────────────────────────
    # Defaults use churnsense_user — matches the PostgreSQL user created during setup.
    # These are overridden by DATABASE_URL / SYNC_DATABASE_URL in .env.
    database_url: str = "postgresql+asyncpg://churnsense_user:churnsense_pass@localhost:5432/churnsense"
    sync_database_url: str = "postgresql://churnsense_user:churnsense_pass@localhost:5432/churnsense"

    # ── CORS ─────────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    # ── File Upload ───────────────────────────────────────────────
    upload_dir: str = os.path.join(_BACKEND_DIR, "uploads")
    max_upload_size_mb: int = 50

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    # ── ML ───────────────────────────────────────────────────────
    model_store_path: str = os.path.join(_PROJECT_ROOT, "ml", "models")
    max_training_time_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
