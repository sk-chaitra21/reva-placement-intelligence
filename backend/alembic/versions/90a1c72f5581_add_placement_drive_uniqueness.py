"""add placement drive uniqueness

Revision ID: 90a1c72f5581
Revises: 0873086b58ef
Create Date: 2026-09-20 00:36:49.998298

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "90a1c72f5581"
down_revision: Union[str, Sequence[str], None] = "0873086b58ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_placement_drive_identity",
        "placement_drives",
        [
            "company_id",
            "academic_year",
            "drive_date",
            "title",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_placement_drive_identity",
        "placement_drives",
        type_="unique",
    )