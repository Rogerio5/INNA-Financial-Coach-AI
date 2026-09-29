from __future__ import annotations

import hmac
import json

from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from typing import Any, Mapping

from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
)


IDEMPOTENCY_VERSION = "2b11a2-v1"

IDEMPOTENCY_KEY_MAX_LENGTH = 200


class IdempotencyKeyError(
    ValueError
):
    pass


class IdempotencyConflictError(
    ValueError
):
    pass


@dataclass(
    frozen=True
)
class IdempotencyContext:

    key_hash: str

    operation: str

    actor_id: str

    payload_fingerprint: str


def _canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )


def _sha256_text(
    value: str,
) -> str:

    return sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def build_idempotency_context(
    *,
    idempotency_key: str | None,
    operation: str | None,
    actor_id: str,
    payload: Any = None,
) -> IdempotencyContext | None:

    if idempotency_key is None:
        return None

    key = str(
        idempotency_key
    ).strip()

    if (
        not key
        or
        len(key)
        >
        IDEMPOTENCY_KEY_MAX_LENGTH
    ):
        raise IdempotencyKeyError(
            "IDEMPOTENCY_KEY_INVALID"
        )

    operation_value = str(
        operation or ""
    ).strip()

    if not operation_value:
        raise IdempotencyKeyError(
            "IDEMPOTENCY_OPERATION_REQUIRED"
        )

    actor_value = str(
        actor_id or ""
    ).strip()

    if not actor_value:
        raise IdempotencyKeyError(
            "IDEMPOTENCY_ACTOR_REQUIRED"
        )

    canonical_payload = (
        _canonical_json(
            payload
            if payload is not None
            else {}
        )
    )

    return IdempotencyContext(
        key_hash=
            _sha256_text(
                key
            ),

        operation=
            operation_value,

        actor_id=
            actor_value,

        payload_fingerprint=
            _sha256_text(
                canonical_payload
            ),
    )


def assert_replay_compatible(
    *,
    context: IdempotencyContext,
    stored_operation: str,
    stored_actor_id: str,
    stored_payload_fingerprint: str,
) -> None:

    compatible = (
        hmac.compare_digest(
            context.operation,
            str(
                stored_operation
            ),
        )
        and
        hmac.compare_digest(
            context.actor_id,
            str(
                stored_actor_id
            ),
        )
        and
        hmac.compare_digest(
            context.payload_fingerprint,
            str(
                stored_payload_fingerprint
            ),
        )
    )

    if not compatible:
        raise IdempotencyConflictError(
            "IDEMPOTENCY_KEY_CONFLICT"
        )


def decode_json_object(
    value: Any,
) -> dict[str, Any]:

    if value is None:
        return {}

    if isinstance(
        value,
        Mapping,
    ):
        return dict(
            value
        )

    if isinstance(
        value,
        str,
    ):

        parsed = json.loads(
            value
        )

        if not isinstance(
            parsed,
            dict,
        ):
            raise ValueError(
                "IDEMPOTENCY_JSON_OBJECT_REQUIRED"
            )

        return parsed

    try:

        result = dict(
            value
        )

    except Exception as exc:

        raise ValueError(
            "IDEMPOTENCY_JSON_OBJECT_REQUIRED"
        ) from exc

    return result


def _json_safe(
    value: Any,
) -> Any:

    if value is None:
        return None

    if isinstance(
        value,
        (
            datetime,
            date,
        ),
    ):
        return value.isoformat()

    return value


def _metadata_value(
    value: Any,
) -> dict[str, Any]:

    if value is None:
        return {}

    if isinstance(
        value,
        Mapping,
    ):

        return json.loads(
            json.dumps(
                dict(value),
                ensure_ascii=False,
                default=str,
            )
        )

    if isinstance(
        value,
        str,
    ):

        parsed = json.loads(
            value
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

    raise ValueError(
        "REIMBURSEMENT_METADATA_INVALID"
    )


def reimbursement_snapshot(
    reimbursement:
        ReimbursementRequest,
) -> dict[str, Any]:

    return {
        "id":
            reimbursement.id,

        "tenant_id":
            reimbursement.tenant_id,

        "user_id":
            reimbursement.user_id,

        "amount":
            reimbursement.amount,

        "currency":
            reimbursement.currency,

        "category":
            reimbursement.category,

        "description":
            reimbursement.description,

        "merchant":
            reimbursement.merchant,

        "expense_date":
            _json_safe(
                reimbursement.expense_date
            ),

        "receipt_reference":
            reimbursement.receipt_reference,

        "source_type":
            reimbursement.source_type,

        "source_reference":
            reimbursement.source_reference,

        "status":
            reimbursement.status.value,

        "requires_human_review":
            reimbursement.requires_human_review,

        "metadata":
            _metadata_value(
                reimbursement.metadata
            ),

        "submitted_at":
            _json_safe(
                reimbursement.submitted_at
            ),

        "created_at":
            _json_safe(
                reimbursement.created_at
            ),

        "updated_at":
            _json_safe(
                reimbursement.updated_at
            ),
    }


def database_row_snapshot(
    row: Mapping[str, Any],
) -> dict[str, Any]:

    return {
        "id":
            str(
                row[
                    "reimbursement_id"
                ]
            ),

        "tenant_id":
            str(
                row[
                    "tenant_id"
                ]
            ),

        "user_id":
            str(
                row[
                    "user_id"
                ]
            ),

        "amount":
            int(
                row[
                    "amount_minor"
                ]
            ),

        "currency":
            str(
                row[
                    "currency"
                ]
            ),

        "category":
            str(
                row[
                    "category"
                ]
            ),

        "description":
            str(
                row[
                    "description"
                ]
            ),

        "merchant":
            row.get(
                "merchant"
            ),

        "expense_date":
            _json_safe(
                row.get(
                    "expense_date"
                )
            ),

        "receipt_reference":
            row.get(
                "receipt_reference"
            ),

        "source_type":
            str(
                row.get(
                    "source_type"
                )
                or
                "finance"
            ),

        "source_reference":
            row.get(
                "source_reference"
            ),

        "status":
            str(
                row[
                    "status"
                ]
            ),

        "requires_human_review":
            bool(
                row.get(
                    "requires_human_review",
                    True,
                )
            ),

        "metadata":
            _metadata_value(
                row.get(
                    "metadata"
                )
            ),

        "submitted_at":
            _json_safe(
                row.get(
                    "submitted_at"
                )
            ),

        "created_at":
            _json_safe(
                row[
                    "created_at"
                ]
            ),

        "updated_at":
            _json_safe(
                row[
                    "updated_at"
                ]
            ),
    }


def _parse_datetime(
    value: Any,
) -> datetime | None:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value

    raw = str(
        value
    ).strip()

    if raw.endswith(
        "Z"
    ):
        raw = (
            raw[:-1]
            +
            "+00:00"
        )

    return datetime.fromisoformat(
        raw
    )


def reimbursement_from_snapshot(
    snapshot: Mapping[str, Any],
) -> ReimbursementRequest:

    data = dict(
        snapshot
    )

    created_at = (
        _parse_datetime(
            data.get(
                "created_at"
            )
        )
    )

    updated_at = (
        _parse_datetime(
            data.get(
                "updated_at"
            )
        )
    )

    if created_at is None:
        raise ValueError(
            "IDEMPOTENCY_CREATED_AT_REQUIRED"
        )

    if updated_at is None:
        raise ValueError(
            "IDEMPOTENCY_UPDATED_AT_REQUIRED"
        )

    return ReimbursementRequest(
        id=
            str(
                data[
                    "id"
                ]
            ),

        tenant_id=
            str(
                data[
                    "tenant_id"
                ]
            ),

        user_id=
            str(
                data[
                    "user_id"
                ]
            ),

        amount=
            int(
                data[
                    "amount"
                ]
            ),

        currency=
            str(
                data[
                    "currency"
                ]
            ),

        category=
            str(
                data[
                    "category"
                ]
            ),

        description=
            str(
                data[
                    "description"
                ]
            ),

        merchant=
            data.get(
                "merchant"
            ),

        expense_date=
            data.get(
                "expense_date"
            ),

        receipt_reference=
            data.get(
                "receipt_reference"
            ),

        source_type=
            str(
                data.get(
                    "source_type"
                )
                or
                "finance"
            ),

        source_reference=
            data.get(
                "source_reference"
            ),

        status=
            ReimbursementStatus(
                str(
                    data[
                        "status"
                    ]
                )
            ),

        requires_human_review=
            bool(
                data.get(
                    "requires_human_review",
                    True,
                )
            ),

        metadata=
            _metadata_value(
                data.get(
                    "metadata"
                )
            ),

        submitted_at=
            _parse_datetime(
                data.get(
                    "submitted_at"
                )
            ),

        created_at=
            created_at,

        updated_at=
            updated_at,
    )


def idempotency_capabilities(
) -> dict[str, Any]:

    return {
        "version":
            IDEMPOTENCY_VERSION,

        "idempotency_key":
            True,

        "tenant_scoped":
            True,

        "reimbursement_scoped":
            True,

        "operation_scoped":
            True,

        "actor_bound":
            True,

        "payload_fingerprint":
            True,

        "response_snapshot":
            True,

        "duplicate_transition_prevention":
            True,

        "duplicate_audit_prevention":
            True,

        "raw_key_persisted":
            False,

        "automatic_approval":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,
    }