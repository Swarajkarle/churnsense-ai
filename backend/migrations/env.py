"""
ChurnSense AI — Alembic Migration Environment

Configured for SQLAlchemy 2.x async project.

Key design:
- Alembic ALWAYS uses a sync psycopg2 connection (for both autogenerate and upgrade).
  asyncpg is only for FastAPI runtime — it is NOT used here.
- ORM models are imported so Alembic can detect all 14 tables via Base.metadata.
- DB URL is read from SYNC_DATABASE_URL env var (never hardcoded).
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Add backend/ to sys.path so `from app.xxx import ...` works ─────────────
# This file lives at backend/migrations/env.py
# backend/ needs to be on the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Load .env file manually ──────────────────────────────────────────────────
# Needed because Alembic runs outside of the FastAPI process
_env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

# ── Import ORM models ────────────────────────────────────────────────────────
# These imports register all ORM classes on Base.metadata so Alembic
# can detect every table when running --autogenerate.
from app.core.database import Base         # noqa: E402
import app.models.orm                      # noqa: E402  (registers all 14 models)

# ── Alembic Config ───────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Target metadata — tells Alembic which tables to track ───────────────────
target_metadata = Base.metadata

# ── Resolve the sync URL (psycopg2) ─────────────────────────────────────────
# Alembic must use a SYNC driver. We use SYNC_DATABASE_URL from .env.
# If not set, fall back to the sqlalchemy.url in alembic.ini.
SYNC_URL = os.environ.get(
    "SYNC_DATABASE_URL",
    config.get_main_option("sqlalchemy.url"),
)

# Override the URL in the config so engine_from_config picks it up
config.set_main_option("sqlalchemy.url", SYNC_URL)


# ── Offline mode ─────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Generate migration SQL without a live DB connection."""
    context.configure(
        url=SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ──────────────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Connect to the live DB (sync psycopg2) and run migrations."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

