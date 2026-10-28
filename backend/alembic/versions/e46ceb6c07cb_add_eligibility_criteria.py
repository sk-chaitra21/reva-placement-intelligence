"""add eligibility criteria

Revision ID: e46ceb6c07cb
Revises: dd0df303481e
Create Date: 2026-09-19 20:44:11.754164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e46ceb6c07cb"
down_revision: Union[str, Sequence[str], None] = "dd0df303481e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "eligibility_criteria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "placement_drive_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "minimum_cgpa",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "eligible_branches",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "graduation_year",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "backlog_allowed",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "other_criteria",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["placement_drive_id"],
            ["placement_drives.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_eligibility_criteria_placement_drive_id"),
        "eligibility_criteria",
        ["placement_drive_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_eligibility_criteria_placement_drive_id"),
        table_name="eligibility_criteria",
    )

    op.drop_table("eligibility_criteria")
