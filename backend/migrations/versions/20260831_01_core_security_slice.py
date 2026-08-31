"""Create security events, alerts, and evidence links."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260831_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    severity = postgresql.ENUM(
        "LOW", "MEDIUM", "HIGH", "CRITICAL", name="alertseverity", create_type=False
    )
    status = postgresql.ENUM(
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
        "DISMISSED",
        name="alertstatus",
        create_type=False,
    )
    severity.create(op.get_bind())
    status.create(op.get_bind())
    op.create_table(
        "security_events",
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("outcome", sa.String(32)),
        sa.Column("user_identifier", sa.String(254)),
        sa.Column("source_ip", sa.String(45)),
        sa.Column("endpoint", sa.String(500)),
        sa.Column("http_method", sa.String(10)),
        sa.Column("status_code", sa.Integer()),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_security_events"),
    )
    for name, columns in (
        ("ix_security_events_timestamp", ["timestamp"]),
        ("ix_security_events_event_type", ["event_type"]),
        ("ix_security_events_source_ip", ["source_ip"]),
        ("ix_security_events_outcome", ["outcome"]),
        ("ix_security_events_user_identifier", ["user_identifier"]),
        ("ix_security_events_source_ip_timestamp", ["source_ip", "timestamp"]),
        ("ix_security_events_event_type_timestamp", ["event_type", "timestamp"]),
    ):
        op.create_index(name, "security_events", columns)
    op.create_table(
        "alerts",
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", severity, nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("detection_rule", sa.String(100), nullable=False),
        sa.Column("rule_version", sa.String(20), nullable=False),
        sa.Column("deduplication_key", sa.String(300), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_alerts"),
        sa.UniqueConstraint("deduplication_key", name="uq_alerts_deduplication_key"),
    )
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_detection_rule", "alerts", ["detection_rule"])
    op.create_table(
        "alert_events",
        sa.Column("alert_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["security_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("alert_id", "event_id", name="pk_alert_events"),
        sa.UniqueConstraint("alert_id", "event_id", name="uq_alert_events_alert_id"),
    )


def downgrade() -> None:
    op.drop_table("alert_events")
    op.drop_table("alerts")
    op.drop_table("security_events")
    postgresql.ENUM(name="alertstatus").drop(op.get_bind())
    postgresql.ENUM(name="alertseverity").drop(op.get_bind())
