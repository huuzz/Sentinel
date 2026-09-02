"""persist public AI analysis results

Revision ID: 20260902_03
Revises: 20260902_02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260902_03"
down_revision: str | None = "20260902_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_analyses",
        sa.Column("alert_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("likely_attack", sa.String(200), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_references", postgresql.JSONB(), nullable=False),
        sa.Column("recommended_actions", postgresql.JSONB(), nullable=False),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alert_id"),
    )
    op.create_index("ix_ai_analyses_alert_id", "ai_analyses", ["alert_id"], unique=True)


def downgrade() -> None:
    op.drop_table("ai_analyses")
