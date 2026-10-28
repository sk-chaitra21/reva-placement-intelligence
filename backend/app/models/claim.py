from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("experiences.id"),
        nullable=False,
        index=True,
    )

    claim_text: Mapped[str] = mapped_column(Text)
    evidence_text: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
)

    claim_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )