
"""add placement drive uniqueness and fix claim embedding index"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "03270e766569"
down_revision: Union[str, Sequence[str], None] = "a12345678901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "claim_embeddings",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.drop_constraint(
        "claim_embeddings_claim_id_key",
        "claim_embeddings",
        type_="unique",
    )

    op.create_index(
        "ix_claim_embeddings_claim_id",
        "claim_embeddings",
        ["claim_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_claim_embeddings_claim_id",
        table_name="claim_embeddings",
    )

    op.create_unique_constraint(
        "claim_embeddings_claim_id_key",
        "claim_embeddings",
        ["claim_id"],
        postgresql_nulls_not_distinct=False,
    )

    op.alter_column(
        "claim_embeddings",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )
