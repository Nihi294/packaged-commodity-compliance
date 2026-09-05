"""Create initial SahiPack schema.

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="officer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table("products",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(255)), sa.Column("category", sa.String(120)), sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table("rules",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()),
        sa.Column("rule_definition", postgresql.JSONB()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("uq_rules_code", "rules", ["code"], unique=True)

    timestamp_columns = [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]
    op.create_table("scans", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")), sa.Column("status", sa.String(50), nullable=False, server_default="pending"), *timestamp_columns)
    op.create_index("ix_scans_user_created_at", "scans", ["user_id", "created_at"])
    op.create_table("images", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("file_path", sa.String(500), nullable=False), sa.Column("image_type", sa.String(50)), *timestamp_columns)
    op.create_table("ocr_results", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("image_id", sa.Integer(), sa.ForeignKey("images.id")), sa.Column("raw_text", sa.Text(), nullable=False), sa.Column("confidence", sa.Float()), *timestamp_columns)
    op.create_table("extracted_declarations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("declaration_type", sa.String(100), nullable=False), sa.Column("value", sa.Text()), sa.Column("source_data", postgresql.JSONB()), *timestamp_columns)
    op.create_table("rule_results", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("rule_id", sa.Integer(), sa.ForeignKey("rules.id"), nullable=False), sa.Column("passed", sa.Boolean(), nullable=False), sa.Column("details", postgresql.JSONB()), *timestamp_columns)
    op.create_table("violations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("rule_result_id", sa.Integer(), sa.ForeignKey("rule_results.id")), sa.Column("message", sa.Text(), nullable=False), sa.Column("severity", sa.String(50), nullable=False, server_default="medium"), *timestamp_columns)
    op.create_table("reports", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("file_path", sa.String(500)), sa.Column("status", sa.String(50), nullable=False, server_default="pending"), *timestamp_columns)
    op.create_table("inspection_history", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id")), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("action", sa.String(100), nullable=False), sa.Column("notes", sa.Text()), *timestamp_columns)
    op.create_table("evidence", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False), sa.Column("rule_result_id", sa.Integer(), sa.ForeignKey("rule_results.id")), sa.Column("violation_id", sa.Integer(), sa.ForeignKey("violations.id")), sa.Column("file_path", sa.String(500), nullable=False), sa.Column("description", sa.Text()), *timestamp_columns)


def downgrade() -> None:
    for table in ("evidence", "inspection_history", "reports", "violations", "rule_results", "extracted_declarations", "ocr_results", "images", "scans", "rules", "products", "users"):
        op.drop_table(table)
