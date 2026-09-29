from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class DocumentVerificationStatus(
    str,
    Enum,
):
    NOT_AVAILABLE = "not_available"
    PERSISTED_UNVERIFIED = "persisted_unverified"
    VERIFIED = "verified"
    REQUIRES_REVIEW = "requires_review"


@dataclass(frozen=True)
class DocumentVerificationResult:
    status: DocumentVerificationStatus
    document_verified: bool
    document_content_trusted: bool
    persisted_receipt_present: bool
    validation_present: bool
    extraction_status: str | None
    evidence: tuple[str, ...]
    blocking_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status":
                self.status.value,

            "document_verified":
                self.document_verified,

            "document_content_trusted":
                self.document_content_trusted,

            "persisted_receipt_present":
                self.persisted_receipt_present,

            "validation_present":
                self.validation_present,

            "extraction_status":
                self.extraction_status,

            "evidence":
                list(self.evidence),

            "blocking_reasons":
                list(self.blocking_reasons),
        }


def _string_list(
    value: Any,
) -> list[str]:

    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        str(item)
        for item in value
        if isinstance(
            item,
            str,
        )
    ]


def verify_receipt_document(
    *,
    persisted_receipt_present: bool,
    validation_metadata:
        Mapping[str, Any]
        |
        None,
) -> DocumentVerificationResult:
    """
    Deterministic verification layer.

    Important security invariant:
    document_content_trusted always remains False.

    Verification means that operational evidence
    was successfully checked. It does NOT mean
    document text can be trusted as instructions.
    """

    evidence: list[str] = []
    blocking: list[str] = []

    if not persisted_receipt_present:

        blocking.append(
            "RECEIPT_NOT_PERSISTED"
        )

        return DocumentVerificationResult(
            status=
                DocumentVerificationStatus
                .NOT_AVAILABLE,

            document_verified=False,

            document_content_trusted=False,

            persisted_receipt_present=False,

            validation_present=False,

            extraction_status=None,

            evidence=tuple(evidence),

            blocking_reasons=
                tuple(blocking),
        )


    evidence.append(
        "PERSISTED_RECEIPT_PRESENT"
    )


    if not isinstance(
        validation_metadata,
        Mapping,
    ):

        blocking.append(
            "RECEIPT_VALIDATION_NOT_AVAILABLE"
        )

        return DocumentVerificationResult(
            status=
                DocumentVerificationStatus
                .PERSISTED_UNVERIFIED,

            document_verified=False,

            document_content_trusted=False,

            persisted_receipt_present=True,

            validation_present=False,

            extraction_status=None,

            evidence=tuple(evidence),

            blocking_reasons=
                tuple(blocking),
        )


    evidence.append(
        "RECEIPT_VALIDATION_PRESENT"
    )


    extraction_status = str(
        validation_metadata.get(
            "extraction_status",
            "",
        )
        or
        ""
    ).strip().lower()

    extraction_status_value = (
        extraction_status
        or
        None
    )


    if extraction_status:
        evidence.append(
            "EXTRACTION_STATUS:"
            + extraction_status
        )


    warnings = _string_list(
        validation_metadata.get(
            "warnings"
        )
    )

    inconsistencies = _string_list(
        validation_metadata.get(
            "inconsistencies"
        )
    )


    if (
        bool(
            validation_metadata.get(
                "has_inconsistencies",
                False,
            )
        )
        and
        not inconsistencies
    ):
        inconsistencies.append(
            "UNSPECIFIED_INCONSISTENCY"
        )


    if (
        extraction_status
        !=
        "extracted"
    ):
        blocking.append(
            "EXTRACTION_NOT_VERIFIED"
        )


    for warning in warnings:
        blocking.append(
            "WARNING:"
            + warning
        )


    for inconsistency in inconsistencies:
        blocking.append(
            "INCONSISTENCY:"
            + inconsistency
        )


    if blocking:

        return DocumentVerificationResult(
            status=
                DocumentVerificationStatus
                .REQUIRES_REVIEW,

            document_verified=False,

            document_content_trusted=False,

            persisted_receipt_present=True,

            validation_present=True,

            extraction_status=
                extraction_status_value,

            evidence=tuple(evidence),

            blocking_reasons=
                tuple(blocking),
        )


    evidence.append(
        "DOCUMENT_OPERATIONALLY_VERIFIED"
    )


    return DocumentVerificationResult(
        status=
            DocumentVerificationStatus
            .VERIFIED,

        document_verified=True,

        document_content_trusted=False,

        persisted_receipt_present=True,

        validation_present=True,

        extraction_status=
            extraction_status_value,

        evidence=tuple(evidence),

        blocking_reasons=(),
    )