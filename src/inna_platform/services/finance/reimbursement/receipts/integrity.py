from __future__ import annotations

import hmac
import re

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping, Sequence


from .models import (
    ReceiptRecord,
)

from .storage import (
    LocalReceiptStorage,
)


INTEGRITY_VERSION = "2b10c7-v1"

INTEGRITY_WARNING = (
    "RECEIPT_INTEGRITY_NOT_VERIFIED"
)

SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

READ_CHUNK_BYTES = 1024 * 1024


def utc_now() -> datetime:

    return datetime.now(
        timezone.utc
    )


@dataclass(frozen=True)
class ReceiptIntegrityResult:

    integrity_verified: bool

    checked_receipt_count: int

    verified_receipt_ids: tuple[str, ...]

    evidence: tuple[str, ...]

    blocking_reasons: tuple[str, ...]

    checked_at: datetime

    version: str = (
        INTEGRITY_VERSION
    )


    def as_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "integrity_verified":
                self.integrity_verified,

            "checked_receipt_count":
                self.checked_receipt_count,

            "verified_receipt_ids":
                list(
                    self.verified_receipt_ids
                ),

            "evidence":
                list(
                    self.evidence
                ),

            "blocking_reasons":
                list(
                    self.blocking_reasons
                ),

            "checked_at":
                self.checked_at.isoformat(),

            "version":
                self.version,

            "physical_file_rehashed":
                True,

            "document_content_trusted":
                False,

            "automatic_approval":
                False,

            "human_review_required":
                True,
        }


def receipt_integrity_capabilities(
) -> dict[str, Any]:

    return {
        "version":
            "reimbursement-2b10c7",

        "physical_file_rehash":
            True,

        "expected_sha256_comparison":
            True,

        "size_comparison":
            True,

        "storage_reference_validation":
            True,

        "tenant_reimbursement_binding":
            True,

        "fail_closed_on_mismatch":
            True,

        "integrity_evidence":
            True,

        "document_content_trusted":
            False,

        "automatic_approval":
            False,

        "auto_transition_to_approved":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,
    }


def _append_unique(
    values: list[str],
    value: str,
) -> None:

    if value not in values:

        values.append(
            value
        )


def _file_sha256_and_size(
    path,
) -> tuple[str, int]:

    digest = sha256()

    total = 0

    with path.open(
        "rb"
    ) as handle:

        while True:

            chunk = handle.read(
                READ_CHUNK_BYTES
            )

            if not chunk:

                break

            digest.update(
                chunk
            )

            total += len(
                chunk
            )

    return (
        digest.hexdigest(),
        total,
    )


def verify_persisted_receipt_integrity(
    *,
    tenant_id: str,
    reimbursement_id: str,
    receipts:
        Sequence[ReceiptRecord],
    storage:
        LocalReceiptStorage,
) -> ReceiptIntegrityResult:
    """
    Revalidates the persisted physical receipt bytes.

    Security properties:
    - record must belong to the requested tenant;
    - record must belong to the requested reimbursement;
    - storage reference must remain inside the storage root;
    - physical file must still exist;
    - file size must match persisted metadata;
    - SHA-256 must match persisted metadata;
    - document content remains untrusted.
    """

    expected_tenant = str(
        tenant_id or ""
    ).strip()

    expected_reimbursement = str(
        reimbursement_id or ""
    ).strip()

    receipt_list = list(
        receipts or ()
    )

    evidence: list[str] = []

    blocking: list[str] = []

    verified_ids: list[str] = []

    checked_at = utc_now()


    if not receipt_list:

        blocking.append(
            "RECEIPT_NOT_PERSISTED"
        )

        return ReceiptIntegrityResult(
            integrity_verified=False,

            checked_receipt_count=0,

            verified_receipt_ids=(),

            evidence=(),

            blocking_reasons=
                tuple(
                    blocking
                ),

            checked_at=
                checked_at,
        )


    evidence.append(
        "PERSISTED_RECEIPT_COUNT:"
        + str(
            len(
                receipt_list
            )
        )
    )


    for receipt in receipt_list:

        receipt_id = str(
            receipt.receipt_id
            or
            ""
        ).strip()


        # ----------------------------------------------------
        # Tenant / reimbursement binding.
        # ----------------------------------------------------

        if (
            str(
                receipt.tenant_id
                or
                ""
            ).strip()
            !=
            expected_tenant
        ):

            _append_unique(
                blocking,

                "RECEIPT_TENANT_MISMATCH:"
                + receipt_id,
            )

            continue


        if (
            str(
                receipt.reimbursement_id
                or
                ""
            ).strip()
            !=
            expected_reimbursement
        ):

            _append_unique(
                blocking,

                "RECEIPT_REIMBURSEMENT_MISMATCH:"
                + receipt_id,
            )

            continue


        _append_unique(
            evidence,

            "RECEIPT_SCOPE_VERIFIED:"
            + receipt_id,
        )


        # ----------------------------------------------------
        # Persisted SHA-256 format.
        # ----------------------------------------------------

        expected_sha256 = str(
            receipt.sha256
            or
            ""
        ).strip().lower()


        if (
            SHA256_PATTERN.fullmatch(
                expected_sha256
            )
            is None
        ):

            _append_unique(
                blocking,

                "RECEIPT_SHA256_INVALID:"
                + receipt_id,
            )

            continue


        # ----------------------------------------------------
        # Storage reference confinement.
        # ----------------------------------------------------

        try:

            candidate = storage.resolve(
                receipt.storage_reference
            )

        except Exception:

            _append_unique(
                blocking,

                "RECEIPT_STORAGE_REFERENCE_INVALID:"
                + receipt_id,
            )

            continue


        _append_unique(
            evidence,

            "RECEIPT_STORAGE_REFERENCE_VERIFIED:"
            + receipt_id,
        )


        # ----------------------------------------------------
        # Physical file availability.
        # ----------------------------------------------------

        try:

            available = (
                candidate.exists()
                and
                candidate.is_file()
            )

        except OSError:

            available = False


        if not available:

            _append_unique(
                blocking,

                "RECEIPT_FILE_NOT_AVAILABLE:"
                + receipt_id,
            )

            continue


        # ----------------------------------------------------
        # Physical rehash.
        # ----------------------------------------------------

        try:

            (
                actual_sha256,
                actual_size,
            ) = _file_sha256_and_size(
                candidate
            )

        except OSError:

            _append_unique(
                blocking,

                "RECEIPT_FILE_READ_FAILED:"
                + receipt_id,
            )

            continue


        # ----------------------------------------------------
        # Size binding.
        # ----------------------------------------------------

        expected_size = int(
            receipt.size_bytes
        )


        if (
            actual_size
            !=
            expected_size
        ):

            _append_unique(
                blocking,

                "RECEIPT_SIZE_MISMATCH:"
                + receipt_id,
            )

        else:

            _append_unique(
                evidence,

                "RECEIPT_SIZE_VERIFIED:"
                + receipt_id,
            )


        # ----------------------------------------------------
        # SHA-256 binding.
        # ----------------------------------------------------

        if not hmac.compare_digest(
            actual_sha256,
            expected_sha256,
        ):

            _append_unique(
                blocking,

                "RECEIPT_SHA256_MISMATCH:"
                + receipt_id,
            )

        else:

            _append_unique(
                evidence,

                "RECEIPT_SHA256_VERIFIED:"
                + receipt_id,
            )


        if (
            actual_size
            ==
            expected_size
            and
            hmac.compare_digest(
                actual_sha256,
                expected_sha256,
            )
        ):

            verified_ids.append(
                receipt_id
            )


    verified = (
        not blocking
        and
        len(
            verified_ids
        )
        ==
        len(
            receipt_list
        )
    )


    if verified:

        evidence.append(
            "PERSISTED_RECEIPT_INTEGRITY_VERIFIED"
        )


    return ReceiptIntegrityResult(
        integrity_verified=
            verified,

        checked_receipt_count=
            len(
                receipt_list
            ),

        verified_receipt_ids=
            tuple(
                verified_ids
            ),

        evidence=
            tuple(
                evidence
            ),

        blocking_reasons=
            tuple(
                blocking
            ),

        checked_at=
            checked_at,
    )


def bind_receipt_integrity_to_validation_metadata(
    *,
    validation_metadata:
        Mapping[str, Any]
        |
        None,

    integrity_result:
        ReceiptIntegrityResult
        |
        None,
) -> Mapping[str, Any] | None:
    """
    Bridges integrity failure into the existing deterministic
    document-verification pipeline.

    Existing callers that do not supply a storage/integrity
    result preserve their previous behavior.
    """

    if integrity_result is None:

        return validation_metadata


    if integrity_result.integrity_verified:

        return validation_metadata


    if isinstance(
        validation_metadata,
        Mapping,
    ):

        result = dict(
            validation_metadata
        )

    else:

        result = {}


    raw_warnings = result.get(
        "warnings"
    )

    warnings = []

    if isinstance(
        raw_warnings,
        list,
    ):

        warnings = [
            str(item)
            for item
            in raw_warnings
            if isinstance(
                item,
                str,
            )
        ]


    if (
        INTEGRITY_WARNING
        not in warnings
    ):

        warnings.append(
            INTEGRITY_WARNING
        )


    result[
        "warnings"
    ] = warnings


    return result