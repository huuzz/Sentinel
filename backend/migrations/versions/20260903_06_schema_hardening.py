"""Align timestamp nullability and evidence uniqueness with model contracts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_06"
down_revision: str | None = "20260903_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table, column in (
        ("security_events", "created_at"),
        ("alerts", "created_at"),
        ("alerts", "updated_at"),
    ):
        op.execute(sa.text(f"UPDATE {table} SET {column} = now() WHERE {column} IS NULL"))
        op.alter_column(table, column, existing_type=sa.DateTime(timezone=True), nullable=False)
    # Early demo databases predate the explicit evidence uniqueness constraint.
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_alert_events_alert_id'
                AND conrelid = 'alert_events'::regclass
            ) THEN
                ALTER TABLE alert_events ADD CONSTRAINT uq_alert_events_alert_id
                UNIQUE (alert_id, event_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    for table, column in (
        ("security_events", "created_at"),
        ("alerts", "created_at"),
        ("alerts", "updated_at"),
    ):
        op.alter_column(table, column, existing_type=sa.DateTime(timezone=True), nullable=True)
