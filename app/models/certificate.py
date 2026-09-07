from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Certificate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "certificates"
    __table_args__ = (
        CheckConstraint("status IN ('valid', 'revoked', 'expired')", name="ck_certificates_status"),
    )

    certificate_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    intern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False, default="CEASER")
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="valid")
    certificate_document: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    offer_letter_document: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    certificate_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    offer_letter_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
