"""add experience type

Revision ID: 0873086b58ef
Revises: e46ceb6c07cb
Create Date: 2026-09-19 23:07:02.937090

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0873086b58ef"
down_revision: Union[str, Sequence[str], None] = "e46ceb6c07cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the column temporarily as nullable
    op.add_column(
        "experiences",
        sa.Column(
            "experience_type",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # Give existing experiences a safe default category
    op.execute(
        """
        UPDATE experiences
        SET experience_type = 'PLACEMENT_EXPERIENCE'
        WHERE experience_type IS NULL
        """
    )

    # Make the column mandatory after existing rows are populated
    op.alter_column(
        "experiences",
        "experience_type",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "experiences",
        "experience_type",
    )