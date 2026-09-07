from __future__ import annotations

from pathlib import Path
import re

from sqlalchemy.orm import Session

from app.core.config.settings import BACKEND_ROOT
from app.models.certificate import Certificate
from app.schemas.certificate import CERTIFICATE_ID_PATTERN, PublicCertificateResponse
from app.services.storage_service import StorageService


_CERTIFICATE_ID = re.compile(CERTIFICATE_ID_PATTERN)
_BUNDLED_ROOT = (BACKEND_ROOT / "app" / "assets" / "certificates").resolve()


class CertificateService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def normalize_id(certificate_id: str) -> str:
        normalized = str(certificate_id or "").strip().upper()
        if not _CERTIFICATE_ID.fullmatch(normalized):
            raise ValueError("malformed_certificate_id")
        return normalized

    def find(self, certificate_id: str) -> Certificate | None:
        normalized = self.normalize_id(certificate_id)
        return self.db.query(Certificate).filter(Certificate.certificate_id == normalized).one_or_none()

    def public_record(self, certificate: Certificate, *, public_base_url: str) -> PublicCertificateResponse:
        certificate_id = certificate.certificate_id
        api_base = public_base_url.rstrip("/")
        verification_base = "https://www.heyceaser.in"
        return PublicCertificateResponse(
            certificate_id=certificate_id,
            intern_name=certificate.intern_name,
            role=certificate.role,
            organization=certificate.organization,
            issue_date=certificate.issue_date,
            status=certificate.status,
            verification_url=f"{verification_base}/verify/{certificate_id}",
            certificate_url=(
                f"{api_base}/certificates/{certificate_id}/documents/certificate"
                if certificate.certificate_public and certificate.certificate_document
                else None
            ),
            offer_letter_url=(
                f"{api_base}/certificates/{certificate_id}/documents/offer-letter"
                if certificate.offer_letter_public and certificate.offer_letter_document
                else None
            ),
        )

    def public_document(self, certificate: Certificate, kind: str) -> tuple[bytes, str]:
        if certificate.status != "valid":
            raise PermissionError("certificate_not_valid")
        if kind == "certificate":
            storage_path = certificate.certificate_document if certificate.certificate_public else None
            filename = f"{certificate.certificate_id}.pdf"
        elif kind == "offer-letter":
            storage_path = certificate.offer_letter_document if certificate.offer_letter_public else None
            filename = f"{certificate.certificate_id}-offer-letter.pdf"
        else:
            raise ValueError("unsupported_document_kind")
        if not storage_path:
            raise FileNotFoundError(kind)
        return self._read_controlled_document(storage_path), filename

    @staticmethod
    def _read_controlled_document(storage_path: str) -> bytes:
        if storage_path.startswith("bundled://"):
            relative = storage_path.removeprefix("bundled://")
            candidate = (_BUNDLED_ROOT / relative).resolve()
            if _BUNDLED_ROOT not in candidate.parents or not candidate.is_file():
                raise FileNotFoundError(relative)
            return candidate.read_bytes()
        if storage_path.startswith(("local://certificates/", "supabase://")):
            return StorageService().read_bytes(storage_path)
        raise PermissionError("unapproved_certificate_storage")
