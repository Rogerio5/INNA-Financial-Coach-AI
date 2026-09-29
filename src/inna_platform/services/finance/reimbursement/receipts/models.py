from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


@dataclass(frozen=True)
class ReceiptRecord:
    tenant_id: str
    reimbursement_id: str
    uploaded_by_user_id: str

    original_filename: str
    safe_filename: str

    mime_type: str
    size_bytes: int
    sha256: str

    storage_reference: str

    receipt_id: str = field(
        default_factory=lambda:
            str(uuid4())
    )

    untrusted_content: bool = True

    validation_version: str = (
        "receipt-security-v1"
    )

    created_at: datetime = field(
        default_factory=utc_now
    )