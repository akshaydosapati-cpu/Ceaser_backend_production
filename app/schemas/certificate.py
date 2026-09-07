from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


CERTIFICATE_ID_PATTERN = r"^CEASER-INT-[0-9]{4}-[0-9]{3,6}$"


class CertificateVerifyRequest(BaseModel):
    certificate_id: str = Field(min_length=1, max_length=64, pattern=CERTIFICATE_ID_PATTERN)

    @field_validator("certificate_id", mode="before")
    @classmethod
    def normalize_certificate_id(cls, value: object) -> str:
        return str(value or "").strip().upper()


class PublicCertificateResponse(BaseModel):
    certificate_id: str
    intern_name: str
    role: str
    organization: str
    issue_date: date
    status: Literal["valid", "revoked", "expired"]
    verification_url: str
    certificate_url: str | None = None
    offer_letter_url: str | None = None
