from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Basic meeting metadata
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    saved_file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Processing outputs
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stored as JSON string or plain text initially.
    # We'll decide in Step 2/3 whether to keep these as text or move to JSON columns.
    key_decisions: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_items: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional metadata
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )