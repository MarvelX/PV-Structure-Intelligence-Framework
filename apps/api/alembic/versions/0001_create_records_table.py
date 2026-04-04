from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_records_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("workspace", sa.String(length=32), nullable=False),
        sa.Column("title_zh", sa.String(length=255), nullable=False),
        sa.Column("title_en", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("tags", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("manual_override", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("input_json", sa.Text(), nullable=False),
        sa.Column("output_json", sa.Text(), nullable=False),
        sa.Column("exports_json", sa.Text(), nullable=False),
        sa.Column("links_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_records_workspace", "records", ["workspace"], unique=False)
    op.create_index("ix_records_status", "records", ["status"], unique=False)
    op.create_index("ix_records_created_at", "records", ["created_at"], unique=False)
    op.create_index("ix_records_updated_at", "records", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_records_updated_at", table_name="records")
    op.drop_index("ix_records_created_at", table_name="records")
    op.drop_index("ix_records_status", table_name="records")
    op.drop_index("ix_records_workspace", table_name="records")
    op.drop_table("records")
