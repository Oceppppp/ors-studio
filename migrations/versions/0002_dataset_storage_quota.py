"""Track normalized dataset storage usage for per-principal quotas.

Revision ID: 0002_dataset_storage_quota
Revises: 0001_initial_cloud_schema
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_dataset_storage_quota"
down_revision = "0001_initial_cloud_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ors_datasets",
        sa.Column("storage_bytes", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("ors_datasets", "storage_bytes")
