from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "academic_year",
            "drive_date",
            "title",
            name="uq_placement_drive_identity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    drive_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )