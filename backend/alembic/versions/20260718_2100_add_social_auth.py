"""add social auth tables

Revision ID: 20260718_2100
Revises: 20260718_1900
Create Date: 2026-07-18 21:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260718_2100"
down_revision: str | None = "20260718_1900"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

oauth_provider = postgresql.ENUM("GOOGLE", "GITHUB", name="oauth_provider", create_type=False)
oauth_purpose = postgresql.ENUM("LOGIN", "LINK", name="oauth_purpose", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    oauth_provider.create(bind, checkfirst=True)
    oauth_purpose.create(bind, checkfirst=True)

    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), server_default="false", nullable=False),
    )
    op.alter_column("users", "password_hash", existing_type=sa.String(length=512), nullable=True)

    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", oauth_provider, nullable=False),
        sa.Column("provider_user_id", sa.String(length=191), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=False),
        sa.Column("provider_username", sa.String(length=255), nullable=True),
        sa.Column("provider_display_name", sa.String(length=255), nullable=True),
        sa.Column("email_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        sa.UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )
    op.create_index("ix_oauth_accounts_user_id", "oauth_accounts", ["user_id"])

    op.create_table(
        "oauth_states",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("state_hash", sa.String(length=128), nullable=False),
        sa.Column("provider", oauth_provider, nullable=False),
        sa.Column("purpose", oauth_purpose, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("redirect_path", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_hash"),
    )
    op.create_index("ix_oauth_states_expires_at", "oauth_states", ["expires_at"])
    op.create_index("ix_oauth_states_state_hash", "oauth_states", ["state_hash"])

    op.create_table(
        "oauth_login_tickets",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ticket_hash", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", oauth_provider, nullable=False),
        sa.Column("redirect_path", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_hash"),
    )
    op.create_index("ix_oauth_login_tickets_expires_at", "oauth_login_tickets", ["expires_at"])
    op.create_index("ix_oauth_login_tickets_ticket_hash", "oauth_login_tickets", ["ticket_hash"])


def downgrade() -> None:
    bind = op.get_bind()
    null_password_count = bind.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE password_hash IS NULL")
    ).scalar_one()
    if null_password_count:
        raise RuntimeError(
            "Cannot downgrade while social-only users with NULL password_hash exist."
        )

    op.drop_index("ix_oauth_login_tickets_ticket_hash", table_name="oauth_login_tickets")
    op.drop_index("ix_oauth_login_tickets_expires_at", table_name="oauth_login_tickets")
    op.drop_table("oauth_login_tickets")

    op.drop_index("ix_oauth_states_state_hash", table_name="oauth_states")
    op.drop_index("ix_oauth_states_expires_at", table_name="oauth_states")
    op.drop_table("oauth_states")

    op.drop_index("ix_oauth_accounts_user_id", table_name="oauth_accounts")
    op.drop_table("oauth_accounts")

    op.alter_column("users", "password_hash", existing_type=sa.String(length=512), nullable=False)
    op.drop_column("users", "email_verified")

    oauth_purpose.drop(bind, checkfirst=True)
    oauth_provider.drop(bind, checkfirst=True)
