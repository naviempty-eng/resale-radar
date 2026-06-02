"""add premium_until

Revision ID: 0002_add_premium_until
Revises: 0001_initial_schema
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_premium_until"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("premium_until", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "premium_until")
