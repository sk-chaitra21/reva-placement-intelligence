from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EligibilityCriteria(Base):
    __tablename__ = "eligibility_criteria"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    placement_drive_id: Mapped[int] = mapped_column(
        ForeignKey("placement_drives.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    minimum_cgpa: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    eligible_branches: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    graduation_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    backlog_allowed: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    other_criteria: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )