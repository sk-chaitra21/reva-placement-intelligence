
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    placement_drive_id: Mapped[int] = mapped_column(
        ForeignKey("placement_drives.id"),
        nullable=False,
        index=True,
    )

    contributor_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    experience_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False,
    )

    provenance: Mapped[str] = mapped_column(
        String(30),
        default="SELF_REPORTED",
        server_default="SELF_REPORTED",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
