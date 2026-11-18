
"""create claim embeddings table"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "a12345678901"
down_revision = "90a1c72f5581"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "claim_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "claim_id",
            sa.Integer(),
            sa.ForeignKey("claims.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("embedding_model", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "claim_id",
            name="claim_embeddings_claim_id_key",
        ),
    )


def downgrade():
    op.drop_table("claim_embeddings")
