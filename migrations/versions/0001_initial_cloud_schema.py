"""Initial tenant-scoped cloud schema.

Revision ID: 0001_initial_cloud_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_cloud_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ors_principals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "ors_sessions",
        sa.Column("token_hash", sa.String(length=64), primary_key=True),
        sa.Column("principal_id", sa.String(length=36), sa.ForeignKey("ors_principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ors_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("ors_principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ors_datasets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("sheet_name", sa.String(length=255), nullable=True),
        sa.Column("columns_json", sa.JSON(), nullable=False),
        sa.Column("rows_json", sa.JSON(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "ors_analyses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_key", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "ors_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), sa.ForeignKey("ors_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("ors_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_ors_projects_owner_updated", "ors_projects", ["owner_id", "updated_at"])
    op.create_index("ix_ors_datasets_project_created", "ors_datasets", ["project_id", "created_at"])
    op.create_index("ix_ors_analyses_project_created", "ors_analyses", ["project_id", "created_at"])
    op.create_index("ix_ors_jobs_project_created", "ors_jobs", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ors_jobs_project_created", table_name="ors_jobs")
    op.drop_index("ix_ors_analyses_project_created", table_name="ors_analyses")
    op.drop_index("ix_ors_datasets_project_created", table_name="ors_datasets")
    op.drop_index("ix_ors_projects_owner_updated", table_name="ors_projects")
    op.drop_table("ors_jobs")
    op.drop_table("ors_analyses")
    op.drop_table("ors_datasets")
    op.drop_table("ors_projects")
    op.drop_table("ors_sessions")
    op.drop_table("ors_principals")
