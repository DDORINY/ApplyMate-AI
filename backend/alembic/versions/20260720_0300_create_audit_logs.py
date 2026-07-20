"""create audit logs

Revision ID: 20260720_0300
Revises: 20260720_0200
Create Date: 2026-07-20 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260720_0300"
down_revision: str | None = "20260720_0200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("result", sa.String(length=30), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("audit_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_action_created", "audit_logs", ["user_id", "action", "created_at"])
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_request_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_resource", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_action_created", table_name="audit_logs")
    op.drop_table("audit_logs")
