"""Add inspection workflow audit tables.

Revision ID: 0002_inspection_workflow
Revises: 0001_initial_schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_inspection_workflow"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = postgresql.JSONB()
    op.create_table(
        "inspections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("status", sa.String(40), nullable=False, server_default="ASSESSMENT_READY"),
        sa.Column("final_outcome", sa.String(50)),
        sa.Column("verified_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("final_remarks", sa.Text()),
        sa.Column("product_data", json_type, nullable=False),
        sa.Column("assessment_data", json_type, nullable=False),
        sa.Column("evidence_data", json_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_inspections_status", "inspections", ["status"])
    op.create_table(
        "inspection_findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inspection_id", sa.Integer(), sa.ForeignKey("inspections.id"), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="AI"),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("applicable_rule", sa.String(100)),
        sa.Column("original_ai_status", sa.String(50)),
        sa.Column("ai_confidence", sa.Float()),
        sa.Column("ai_evidence", json_type),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("officer_decision", sa.String(50)),
        sa.Column("officer_comment", sa.Text()),
        sa.Column("verified_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("evidence_data", json_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_inspection_findings_inspection_id", "inspection_findings", ["inspection_id"])
    op.create_table(
        "inspection_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inspection_id", sa.Integer(), sa.ForeignKey("inspections.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rule", sa.String(100)),
        sa.Column("status", sa.String(50)),
        sa.Column("evidence_data", json_type, nullable=False),
        sa.Column("officer_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_inspection_observations_inspection_id", "inspection_observations", ["inspection_id"])
    op.add_column("evidence", sa.Column("source", sa.String(20), nullable=False, server_default="AI"))
    op.add_column("evidence", sa.Column("finding_id", sa.Integer(), sa.ForeignKey("inspection_findings.id")))


def downgrade() -> None:
    op.drop_column("evidence", "finding_id")
    op.drop_column("evidence", "source")
    op.drop_table("inspection_observations")
    op.drop_table("inspection_findings")
    op.drop_table("inspections")