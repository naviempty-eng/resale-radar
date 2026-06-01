"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=False),
        sa.Column("country", sa.String(length=40), nullable=False),
        sa.Column("platform", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("size", sa.String(length=80), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("purchase_price", sa.Integer(), nullable=False),
        sa.Column("shipping_price", sa.Integer(), nullable=False),
        sa.Column("total_price_rub", sa.Integer(), nullable=False),
        sa.Column("avito_price", sa.Integer(), nullable=False),
        sa.Column("expected_profit", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("seller_is_suspicious", sa.Boolean(), nullable=False),
        sa.Column("authenticity_risk", sa.String(length=40), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_authenticity_risk"), "items", ["authenticity_risk"], unique=False)
    op.create_index(op.f("ix_items_brand"), "items", ["brand"], unique=False)
    op.create_index(op.f("ix_items_category"), "items", ["category"], unique=False)
    op.create_index(op.f("ix_items_country"), "items", ["country"], unique=False)
    op.create_index(op.f("ix_items_platform"), "items", ["platform"], unique=False)
    op.create_index(op.f("ix_items_seller_is_suspicious"), "items", ["seller_is_suspicious"], unique=False)
    op.create_index(op.f("ix_items_title"), "items", ["title"], unique=False)

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_favorites_user_item"),
    )
    op.create_index(op.f("ix_favorites_item_id"), "favorites", ["item_id"], unique=False)
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)

    op.create_table(
        "instructions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_instructions_item_id"), "instructions", ["item_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_instructions_item_id"), table_name="instructions")
    op.drop_table("instructions")
    op.drop_index(op.f("ix_favorites_user_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_item_id"), table_name="favorites")
    op.drop_table("favorites")
    op.drop_index(op.f("ix_items_title"), table_name="items")
    op.drop_index(op.f("ix_items_seller_is_suspicious"), table_name="items")
    op.drop_index(op.f("ix_items_platform"), table_name="items")
    op.drop_index(op.f("ix_items_country"), table_name="items")
    op.drop_index(op.f("ix_items_category"), table_name="items")
    op.drop_index(op.f("ix_items_brand"), table_name="items")
    op.drop_index(op.f("ix_items_authenticity_risk"), table_name="items")
    op.drop_table("items")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
