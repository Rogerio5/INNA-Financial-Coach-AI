from __future__ import annotations

from dataclasses import (
    dataclass,
    replace,
)

from functools import lru_cache
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from src.inna_platform.services.finance.finance_access_gate import (
    get_financeiro_entitled_user,
)

from ..audit.audit_service import (
    PostgresReimbursementAuditService,
    ReimbursementAuditService,
)

from ..corporate.context import (
    CorporateContext,
    resolve_corporate_context,
)

from ..corporate.rbac import (
    can_review_reimbursements,
)

from ..corporate.repository import (
    CorporateRepository,
    PostgresCorporateRepository,
)

from ..db_schema import (
    ensure_reimbursement_schema,
)

from ..models import (
    ReimbursementRequest,
    ReimbursementStatus,
)

from ..repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)

from .models import ReceiptRecord

from .repository import (
    PostgresReceiptRepository,
    ReceiptRepository,
)

from .security import (
    MAX_RECEIPT_BYTES,
    ReceiptValidationError,
    inspect_receipt,
    sanitize_original_filename,
)

from .storage import (
    LocalReceiptStorage,
    build_safe_filename,
)


router = APIRouter(
    tags=[
        "Finance Reimbursement Receipts"
    ]
)


UPLOAD_ALLOWED_STATUSES = {
    ReimbursementStatus.DRAFT,
    ReimbursementStatus.SUBMITTED,
    ReimbursementStatus.NEEDS_INFORMATION,
}


@dataclass
class ReceiptApiRuntime:
    reimbursement_repository: ReimbursementRepository
    corporate_repository: CorporateRepository
    receipt_repository: ReceiptRepository

    audit: (
        ReimbursementAuditService
        |
        PostgresReimbursementAuditService
    )

    storage: LocalReceiptStorage


@lru_cache(maxsize=1)
def get_receipt_api_runtime(
) -> ReceiptApiRuntime:

    ensure_reimbursement_schema()

    return ReceiptApiRuntime(
        reimbursement_repository=
            PostgresReimbursementRepository(),

        corporate_repository=
            PostgresCorporateRepository(),

        receipt_repository=
            PostgresReceiptRepository(),

        audit=
            PostgresReimbursementAuditService(),

        storage=
            LocalReceiptStorage(),
    )


def _user_id(
    user: dict,
) -> str:

    user_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not user_id:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Identidade autenticada inválida",
        )

    return user_id


def _context(
    *,
    user: dict,
    runtime: ReceiptApiRuntime,
) -> CorporateContext:

    user_id = _user_id(
        user
    )

    try:

        context = resolve_corporate_context(
            repository=
                runtime.corporate_repository,

            user_id=
                user_id,
        )

    except ValueError as exc:

        if (
            str(exc)
            ==
            "MULTIPLE_ORGANIZATIONS_REQUIRE_SELECTION"
        ):

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=
                    "MULTIPLE_ORGANIZATIONS_REQUIRE_SELECTION",
            ) from exc

        raise

    if context is None:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "ORGANIZATION_MEMBERSHIP_REQUIRED",
        )

    return context


def _request(
    *,
    runtime: ReceiptApiRuntime,
    organization_id: str,
    reimbursement_id: str,
) -> ReimbursementRequest:

    reimbursement = (
        runtime
        .reimbursement_repository
        .get(
            tenant_id=
                organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if reimbursement is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Reembolso não encontrado",
        )

    return reimbursement


def _owned_request(
    *,
    runtime: ReceiptApiRuntime,
    context: CorporateContext,
    reimbursement_id: str,
) -> ReimbursementRequest:

    reimbursement = _request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        reimbursement_id=
            reimbursement_id,
    )

    if (
        reimbursement.user_id
        !=
        context.user_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Reembolso não encontrado",
        )

    return reimbursement


def _readable_request(
    *,
    runtime: ReceiptApiRuntime,
    context: CorporateContext,
    reimbursement_id: str,
) -> ReimbursementRequest:

    reimbursement = _request(
        runtime=runtime,

        organization_id=
            context.organization_id,

        reimbursement_id=
            reimbursement_id,
    )

    if (
        reimbursement.user_id
        ==
        context.user_id
    ):

        return reimbursement

    if can_review_reimbursements(
        context.member
    ):

        return reimbursement

    raise HTTPException(
        status_code=
            status.HTTP_404_NOT_FOUND,

        detail=
            "Reembolso não encontrado",
    )


def _serialize(
    receipt: ReceiptRecord,
) -> dict:

    return {
        "receipt_id":
            receipt.receipt_id,

        "reimbursement_id":
            receipt.reimbursement_id,

        "uploaded_by_user_id":
            receipt.uploaded_by_user_id,

        "original_filename":
            receipt.original_filename,

        "mime_type":
            receipt.mime_type,

        "size_bytes":
            receipt.size_bytes,

        "sha256":
            receipt.sha256,

        "untrusted_content":
            receipt.untrusted_content,

        "validation_version":
            receipt.validation_version,

        "created_at":
            receipt.created_at.isoformat(),
    }


@router.post(
    "/{reimbursement_id}/receipts",
    status_code=
        status.HTTP_201_CREATED,
)
async def upload_receipt(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    file: UploadFile = File(...),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReceiptApiRuntime = Depends(
        get_receipt_api_runtime
    ),
):

    context = _context(
        user=user,
        runtime=runtime,
    )

    reimbursement = _owned_request(
        runtime=runtime,
        context=context,
        reimbursement_id=reimbursement_id,
    )

    if (
        reimbursement.status
        not in
        UPLOAD_ALLOWED_STATUSES
    ):

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "RECEIPT_UPLOAD_STATUS_NOT_ALLOWED",
        )

    try:

        content = await file.read(
            MAX_RECEIPT_BYTES
            + 1
        )

    finally:

        await file.close()

    try:

        inspection = inspect_receipt(
            content
        )

    except ReceiptValidationError as exc:

        raise HTTPException(
            status_code=
                exc.status_code,

            detail=
                exc.code,
        ) from exc

    existing = (
        runtime
        .receipt_repository
        .list_for_reimbursement(
            tenant_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    if any(
        item.sha256 == inspection.sha256
        for item in existing
    ):

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "RECEIPT_DUPLICATE",
        )

    receipt_id = str(
        uuid4()
    )

    safe_filename = build_safe_filename(
        receipt_id=
            receipt_id,

        extension=
            inspection.extension,
    )

    provisional = ReceiptRecord(
        receipt_id=
            receipt_id,

        tenant_id=
            context.organization_id,

        reimbursement_id=
            reimbursement_id,

        uploaded_by_user_id=
            context.user_id,

        original_filename=
            sanitize_original_filename(
                file.filename
            ),

        safe_filename=
            safe_filename,

        mime_type=
            inspection.mime_type,

        size_bytes=
            inspection.size_bytes,

        sha256=
            inspection.sha256,

        storage_reference=
            "pending",
    )

    try:

        storage_reference = (
            runtime.storage.save(
                record=
                    provisional,

                content=
                    content,
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "RECEIPT_STORAGE_WRITE_FAILED",
        ) from exc

    receipt = replace(
        provisional,
        storage_reference=
            storage_reference,
    )

    receipt_saved = False
    request_updated = False

    try:

        runtime.receipt_repository.save(
            receipt
        )

        receipt_saved = True

        updated_request = replace(
            reimbursement,

            receipt_reference=
                receipt.receipt_id,
        )

        updated_request.touch()

        runtime.reimbursement_repository.save(
            updated_request
        )

        request_updated = True

        runtime.audit.record(
            tenant_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,

            action=
                "reimbursement.receipt.uploaded",

            actor_id=
                context.user_id,

            details={
                "receipt_id":
                    receipt.receipt_id,

                "mime_type":
                    receipt.mime_type,

                "size_bytes":
                    receipt.size_bytes,

                "sha256":
                    receipt.sha256,

                "untrusted_content":
                    True,
            },
        )

    except Exception as exc:

        if request_updated:

            try:

                runtime.reimbursement_repository.save(
                    reimbursement
                )

            except Exception:
                pass

        if receipt_saved:

            try:

                runtime.receipt_repository.delete(
                    tenant_id=
                        context.organization_id,

                    receipt_id=
                        receipt.receipt_id,
                )

            except Exception:
                pass

        try:

            runtime.storage.delete(
                storage_reference
            )

        except Exception:
            pass

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "RECEIPT_UPLOAD_PERSISTENCE_FAILED",
        ) from exc

    return {
        "ok":
            True,

        "receipt":
            _serialize(
                receipt
            ),

        "reimbursement": {
            "reimbursement_id":
                reimbursement_id,

            "receipt_reference":
                receipt.receipt_id,
        },
    }


@router.get(
    "/{reimbursement_id}/receipts",
)
def list_receipts(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReceiptApiRuntime = Depends(
        get_receipt_api_runtime
    ),
):

    context = _context(
        user=user,
        runtime=runtime,
    )

    _readable_request(
        runtime=runtime,
        context=context,
        reimbursement_id=reimbursement_id,
    )

    receipts = (
        runtime
        .receipt_repository
        .list_for_reimbursement(
            tenant_id=
                context.organization_id,

            reimbursement_id=
                reimbursement_id,
        )
    )

    return {
        "ok":
            True,

        "count":
            len(receipts),

        "receipts": [
            _serialize(item)
            for item
            in receipts
        ],
    }


@router.get(
    "/{reimbursement_id}/receipts/{receipt_id}",
)
def get_receipt(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    receipt_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReceiptApiRuntime = Depends(
        get_receipt_api_runtime
    ),
):

    context = _context(
        user=user,
        runtime=runtime,
    )

    _readable_request(
        runtime=runtime,
        context=context,
        reimbursement_id=reimbursement_id,
    )

    receipt = (
        runtime
        .receipt_repository
        .get(
            tenant_id=
                context.organization_id,

            receipt_id=
                receipt_id,
        )
    )

    if (
        receipt is None
        or
        receipt.reimbursement_id
        !=
        reimbursement_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "RECEIPT_NOT_FOUND",
        )

    return {
        "ok":
            True,

        "receipt":
            _serialize(
                receipt
            ),
    }


# SABINO_REIMBURSEMENT_PHASE_2B4_EXTRACTION_API_START

from functools import lru_cache as _extraction_lru_cache

from .extraction.models import (
    ReceiptExtractionRecord as _ReceiptExtractionRecord,
)

from .extraction.repository import (
    PostgresReceiptExtractionRepository as _PostgresReceiptExtractionRepository,
    ReceiptExtractionRepository as _ReceiptExtractionRepository,
)

from .extraction.service import (
    ReceiptExtractionService as _ReceiptExtractionService,
)

from .extraction.persistence import (
    persist_validated_extraction as _persist_validated_extraction,
)


@_extraction_lru_cache(maxsize=1)
def get_receipt_extraction_repository(
) -> _ReceiptExtractionRepository:

    return (
        _PostgresReceiptExtractionRepository()
    )


def _serialize_extraction(
    extraction: _ReceiptExtractionRecord,
) -> dict:

    return {
        "extraction_id":
            extraction.extraction_id,

        "receipt_id":
            extraction.receipt_id,

        "reimbursement_id":
            extraction.reimbursement_id,

        "merchant_name":
            extraction.merchant_name,

        "merchant_tax_id":
            extraction.merchant_tax_id,

        "document_number":
            extraction.document_number,

        "expense_date": (
            extraction.expense_date.isoformat()
            if extraction.expense_date
            else None
        ),

        "expense_time": (
            extraction.expense_time.isoformat()
            if extraction.expense_time
            else None
        ),

        "currency":
            extraction.currency,

        "subtotal_minor":
            extraction.subtotal_minor,

        "tax_minor":
            extraction.tax_minor,

        "total_minor":
            extraction.total_minor,

        "payment_method":
            extraction.payment_method,

        "confidence":
            extraction.confidence,

        "warnings":
            list(
                extraction.warnings
            ),

        "inconsistencies":
            list(
                extraction.inconsistencies
            ),

        "extraction_status":
            extraction.extraction_status.value,

        "extractor":
            extraction.extractor,

        "extractor_version":
            extraction.extractor_version,

        "document_content_trusted":
            False,

        "human_review_required":
            True,
    }


@router.post(
    "/{reimbursement_id}/receipts/{receipt_id}/extract",
)
def extract_receipt(
    reimbursement_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    receipt_id: str = Path(
        min_length=1,
        max_length=100,
    ),

    user: dict = Depends(
        get_financeiro_entitled_user
    ),

    runtime: ReceiptApiRuntime = Depends(
        get_receipt_api_runtime
    ),

    extraction_repository:
        _ReceiptExtractionRepository = Depends(
            get_receipt_extraction_repository
        ),
):

    context = _context(
        user=user,
        runtime=runtime,
    )

    reimbursement = _owned_request(
        runtime=runtime,
        context=context,
        reimbursement_id=reimbursement_id,
    )

    if (
        reimbursement.status
        not in
        UPLOAD_ALLOWED_STATUSES
    ):

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "RECEIPT_EXTRACTION_STATUS_NOT_ALLOWED",
        )

    receipt = (
        runtime.receipt_repository.get(
            tenant_id=
                context.organization_id,

            receipt_id=
                receipt_id,
        )
    )

    if (
        receipt is None
        or
        receipt.reimbursement_id
        !=
        reimbursement_id
    ):

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "RECEIPT_NOT_FOUND",
        )

    service = (
        _ReceiptExtractionService(
            receipt_repository=
                runtime.receipt_repository,

            extraction_repository=
                extraction_repository,

            storage=
                runtime.storage,

            reimbursement_repository=
                runtime.reimbursement_repository,
        )
    )

    try:

        (
            extraction,
            prepared_reimbursement,
        ) = (
            service.prepare_local_and_validate(
                tenant_id=
                    context.organization_id,

                receipt_id=
                    receipt_id,
            )
        )

        _persist_validated_extraction(
            extraction_repository=
                extraction_repository,

            reimbursement_repository=
                runtime.reimbursement_repository,

            audit=
                runtime.audit,

            reimbursement=
                prepared_reimbursement,

            extraction=
                extraction,

            actor_id=
                context.user_id,
        )

    except LookupError as exc:

        code = str(
            exc
        )

        if code in {
            "RECEIPT_NOT_FOUND",
            "RECEIPT_BINARY_NOT_FOUND",
            "REIMBURSEMENT_NOT_FOUND",
        }:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    code,
            ) from exc

        raise

    except ValueError as exc:

        code = str(
            exc
        )

        if code in {
            "RECEIPT_STORED_FILE_TOO_LARGE",
            "RECEIPT_INTEGRITY_MISMATCH",
            "EXTRACTION_TENANT_MISMATCH",
            "EXTRACTION_REIMBURSEMENT_MISMATCH",
        }:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=
                    code,
            ) from exc

        raise

    return {
        "ok":
            True,

        "extraction":
            _serialize_extraction(
                extraction
            ),

        "analysis_ready":
            True,

        "human_review_required":
            True,

        "automatic_approval":
            False,
    }


# SABINO_REIMBURSEMENT_PHASE_2B4_EXTRACTION_API_END

