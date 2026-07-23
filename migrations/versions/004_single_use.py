"""Single-use tokens.

Adds `max_uses` (nullable int — NULL means unlimited, matching today's
behavior for every existing token) and `use_count` (defaults to 0) to
`tokens`. A token with max_uses set is treated as exhausted (state
USED_UP, same as GONE from the guest's perspective) once use_count
reaches max_uses — see app/routers/guest.py.

Revision ID: 004
Revises: 003
Create Date: 2026-07-24
"""
from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE tokens ADD COLUMN max_uses INTEGER")
    op.execute("ALTER TABLE tokens ADD COLUMN use_count INTEGER NOT NULL DEFAULT 0")


def downgrade() -> None:
    op.execute("ALTER TABLE tokens RENAME TO _tokens_old")
    op.execute("""
        CREATE TABLE tokens (
            id                   TEXT PRIMARY KEY,
            slug                 TEXT UNIQUE NOT NULL,
            label                TEXT NOT NULL,
            created_at           INTEGER NOT NULL,
            expires_at           INTEGER NOT NULL,
            revoked              INTEGER NOT NULL DEFAULT 0,
            last_accessed        INTEGER,
            rate_limit_rpm       INTEGER NOT NULL DEFAULT 30,
            ip_allowlist         TEXT,
            starts_at            INTEGER,
            recurrence           TEXT,
            notify_service       TEXT,
            notify_lead_seconds  INTEGER,
            notify_sent          INTEGER NOT NULL DEFAULT 0,
            bound_secret         TEXT,
            bound_claimed_at     INTEGER
        )
    """)
    op.execute("""
        INSERT INTO tokens (id, slug, label, created_at, expires_at, revoked,
                            last_accessed, rate_limit_rpm, ip_allowlist,
                            starts_at, recurrence, notify_service,
                            notify_lead_seconds, notify_sent, bound_secret,
                            bound_claimed_at)
        SELECT id, slug, label, created_at, expires_at, revoked,
               last_accessed, rate_limit_rpm, ip_allowlist,
               starts_at, recurrence, notify_service,
               notify_lead_seconds, notify_sent, bound_secret,
               bound_claimed_at
        FROM _tokens_old
    """)
    op.execute("DROP TABLE _tokens_old")
    op.execute("CREATE INDEX IF NOT EXISTS idx_tokens_slug ON tokens(slug)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expires_at ON tokens(expires_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_tokens_starts_at ON tokens(starts_at)")
