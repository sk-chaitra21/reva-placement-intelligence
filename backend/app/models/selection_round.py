from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SelectionRound(Base):
    __tablename__ = "selection_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)

    placement_drive_id: Mapped[int] = mapped_column(
        ForeignKey("placement_drives.id"),
        nullable=False,
        index=True,
    )

    round_number: Mapped[int] = mapped_column(Integer)
    round_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )