from __future__ import annotations

from hashlib import sha256

from ...repository import (
    ReimbursementRepository,
)

from ..repository import (
    ReceiptRepository,
)

from ..security import (
    MAX_RECEIPT_BYTES,
)

from ..storage import (
    LocalReceiptStorage,
)

from .extractor import (
    extract_receipt_content,
)

from .models import (
    ReceiptExtractionRecord,
)

from .repository import (
    ReceiptExtractionRepository,
)

from .validation import (
    build_validation_metadata,
    validate_extraction_against_reimbursement,
)


class ReceiptExtractionService:

    def __init__(
        self,
        *,
        receipt_repository: ReceiptRepository,
        extraction_repository:
            ReceiptExtractionRepository,
        storage: LocalReceiptStorage,
        reimbursement_repository:
            ReimbursementRepository | None = None,
    ) -> None:

        self.receipt_repository = (
            receipt_repository
        )

        self.extraction_repository = (
            extraction_repository
        )

        self.storage = storage

        self.reimbursement_repository = (
            reimbursement_repository
        )

    def _require_receipt(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ):

        receipt = (
            self.receipt_repository.get(
                tenant_id=tenant_id,
                receipt_id=receipt_id,
            )
        )

        if receipt is None:

            raise LookupError(
                "RECEIPT_NOT_FOUND"
            )

        return receipt

    def _load_verified_content(
        self,
        receipt,
    ) -> bytes:

        path = self.storage.resolve(
            receipt.storage_reference
        )

        if not path.exists():

            raise LookupError(
                "RECEIPT_BINARY_NOT_FOUND"
            )

        with path.open(
            "rb"
        ) as handle:

            content = handle.read(
                MAX_RECEIPT_BYTES
                + 1
            )

        if (
            len(content)
            >
            MAX_RECEIPT_BYTES
        ):

            raise ValueError(
                "RECEIPT_STORED_FILE_TOO_LARGE"
            )

        if (
            len(content)
            !=
            receipt.size_bytes
        ):

            raise ValueError(
                "RECEIPT_INTEGRITY_MISMATCH"
            )

        calculated_sha256 = (
            sha256(
                content
            )
            .hexdigest()
        )

        if (
            calculated_sha256
            !=
            receipt.sha256
        ):

            raise ValueError(
                "RECEIPT_INTEGRITY_MISMATCH"
            )

        return content

    def extract_local(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptExtractionRecord:

        receipt = self._require_receipt(
            tenant_id=tenant_id,
            receipt_id=receipt_id,
        )

        content = (
            self._load_verified_content(
                receipt
            )
        )

        extraction = (
            extract_receipt_content(
                receipt=receipt,
                content=content,
            )
        )

        self.extraction_repository.save(
            extraction
        )

        return extraction

    def prepare_local_and_validate(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ):

        if (
            self.reimbursement_repository
            is None
        ):

            raise RuntimeError(
                "REIMBURSEMENT_REPOSITORY_REQUIRED"
            )

        receipt = self._require_receipt(
            tenant_id=tenant_id,
            receipt_id=receipt_id,
        )

        reimbursement = (
            self.reimbursement_repository.get(
                tenant_id=tenant_id,
                reimbursement_id=
                    receipt.reimbursement_id,
            )
        )

        if reimbursement is None:

            raise LookupError(
                "REIMBURSEMENT_NOT_FOUND"
            )

        content = (
            self._load_verified_content(
                receipt
            )
        )

        extraction = (
            extract_receipt_content(
                receipt=receipt,
                content=content,
            )
        )

        validated = (
            validate_extraction_against_reimbursement(
                reimbursement=
                    reimbursement,

                extraction=
                    extraction,
            )
        )

        reimbursement.metadata[
            "receipt_validation"
        ] = build_validation_metadata(
            validated
        )

        reimbursement.touch()

        return (
            validated,
            reimbursement,
        )


    def extract_local_and_validate(
        self,
        *,
        tenant_id: str,
        receipt_id: str,
    ) -> ReceiptExtractionRecord:

        (
            validated,
            reimbursement,
        ) = self.prepare_local_and_validate(
            tenant_id=tenant_id,
            receipt_id=receipt_id,
        )

        self.extraction_repository.save(
            validated
        )

        self.reimbursement_repository.save(
            reimbursement
        )

        return validated
