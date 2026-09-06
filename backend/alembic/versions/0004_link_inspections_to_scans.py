"""Link inspections to their source scans.

Revision ID: 0004_link_inspections_to_scans
Revises: 0003_consolidate_reports
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_link_inspections_to_scans"
down_revision = "0003_consolidate_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inspections", sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id")))
    op.create_index("ix_inspections_scan_id", "inspections", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_inspections_scan_id", table_name="inspections")
    op.drop_column("inspections", "scan_id")