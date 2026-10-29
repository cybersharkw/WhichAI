"""Create datasets and test cases.

Revision ID: 0001
Revises: None
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_datasets"),
    )
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("reference_answer", sa.Text(), nullable=False),
        sa.Column("evaluation_criteria", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"], ["datasets.id"],
            name="fk_test_cases_dataset_id_datasets", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_test_cases"),
    )
    op.create_index("ix_test_cases_dataset_id", "test_cases", ["dataset_id"])


def downgrade() -> None:
    op.drop_index("ix_test_cases_dataset_id", table_name="test_cases")
    op.drop_table("test_cases")
    op.drop_table("datasets")
