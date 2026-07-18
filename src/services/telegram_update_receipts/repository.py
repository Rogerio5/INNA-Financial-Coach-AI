from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from src.database.connection import (
    cursor_postgres,
)


SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

ERROR_CODE_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._:-]{0,63}$"
)


SQL_INSERT_RECEIPT = """
INSERT INTO public.telegram_update_receipts (
    update_id,
    update_fingerprint,
    claim_token,
    status,
    attempt_count,
    first_received_at,
    last_received_at,
    claimed_at,
    lease_expires_at,
    completed_at,
    failed_at,
    last_error_code
)
VALUES (
    %(update_id)s,
    %(update_fingerprint)s,
    %(claim_token)s,
    'processing',
    1,
    NOW(),
    NOW(),
    NOW(),
    NOW() + (
        %(lease_seconds)s
        * INTERVAL '1 second'
    ),
    NULL,
    NULL,
    NULL
)
ON CONFLICT (
    update_id
)
DO NOTHING
RETURNING
    update_id,
    status,
    attempt_count;
"""


SQL_LOCK_EXISTING_RECEIPT = """
SELECT
    update_id,
    update_fingerprint,
    claim_token,
    status,
    attempt_count,
    (
        status = 'processing'
        AND lease_expires_at > NOW()
    ) AS lease_active
FROM public.telegram_update_receipts
WHERE update_id = %(update_id)s
FOR UPDATE;
"""


SQL_TOUCH_RECEIPT = """
UPDATE public.telegram_update_receipts
SET
    last_received_at = NOW()
WHERE update_id = %(update_id)s;
"""


SQL_RECLAIM_RECEIPT = """
UPDATE public.telegram_update_receipts
SET
    claim_token = %(claim_token)s,
    status = 'processing',
    attempt_count = attempt_count + 1,
    last_received_at = NOW(),
    claimed_at = NOW(),
    lease_expires_at = NOW() + (
        %(lease_seconds)s
        * INTERVAL '1 second'
    ),
    completed_at = NULL,
    failed_at = NULL,
    last_error_code = NULL
WHERE
    update_id = %(update_id)s
    AND update_fingerprint =
        %(update_fingerprint)s
RETURNING
    update_id,
    status,
    attempt_count;
"""


SQL_COMPLETE_RECEIPT = """
UPDATE public.telegram_update_receipts
SET
    status = 'completed',
    last_received_at = NOW(),
    lease_expires_at = NOW(),
    completed_at = NOW(),
    failed_at = NULL,
    last_error_code = NULL
WHERE
    update_id = %(update_id)s
    AND status = 'processing'
    AND claim_token = %(claim_token)s
RETURNING
    update_id,
    status,
    attempt_count;
"""


SQL_FAIL_RECEIPT = """
UPDATE public.telegram_update_receipts
SET
    status = 'failed',
    last_received_at = NOW(),
    lease_expires_at = NOW(),
    completed_at = NULL,
    failed_at = NOW(),
    last_error_code = %(error_code)s
WHERE
    update_id = %(update_id)s
    AND status = 'processing'
    AND claim_token = %(claim_token)s
RETURNING
    update_id,
    status,
    attempt_count;
"""


class TelegramUpdateReceiptRepositoryError(
    RuntimeError
):
    """
    Erro sanitizado no acesso aos receipts Telegram.
    """


class TelegramUpdateFingerprintConflictError(
    TelegramUpdateReceiptRepositoryError
):
    """
    O update_id já existe associado a outro conteúdo.
    """


class TelegramUpdateClaimOwnershipError(
    TelegramUpdateReceiptRepositoryError
):
    """
    O worker não possui mais o claim atual.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateClaimResult:
    update_id: int

    status: Literal[
        "claimed",
        "reclaimed",
        "in_progress",
        "duplicate",
    ]

    attempt_count: int

    claim_token: str | None

    @property
    def should_process(
        self,
    ) -> bool:
        return self.status in {
            "claimed",
            "reclaimed",
        }

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        """
        Representação apropriada para logs.

        O claim_token nunca é incluído.
        """
        return {
            "status": self.status,
            "attempt_count": (
                self.attempt_count
            ),
            "should_process": (
                self.should_process
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateLifecycleResult:
    update_id: int

    status: Literal[
        "completed",
        "failed",
    ]

    attempt_count: int

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "status": self.status,
            "attempt_count": (
                self.attempt_count
            ),
        }


def _validar_update_id(
    update_id: Any,
) -> int:
    if (
        isinstance(update_id, bool)
        or not isinstance(update_id, int)
        or update_id < 0
    ):
        raise ValueError(
            "update_id inválido."
        )

    return update_id


def _validar_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not SHA256_PATTERN.fullmatch(
            value
        )
    ):
        raise ValueError(
            f"{field_name} inválido."
        )

    return value


def _validar_lease_seconds(
    value: Any,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 5 <= value <= 900
    ):
        raise ValueError(
            "lease_seconds inválido."
        )

    return value


def _validar_error_code(
    value: Any,
) -> str:
    if (
        not isinstance(value, str)
        or not ERROR_CODE_PATTERN.fullmatch(
            value
        )
    ):
        raise ValueError(
            "error_code inválido."
        )

    return value


def _validar_attempt_count(
    value: Any,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou attempt_count inválido."
        )

    return value


def _extrair_update_id(
    row: Mapping[str, Any],
) -> int:
    try:
        return _validar_update_id(
            row["update_id"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou update_id inválido."
        ) from None


def _extrair_status_banco(
    row: Mapping[str, Any],
) -> str:
    try:
        status = row["status"]

    except (
        KeyError,
        TypeError,
    ):
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou status inválido."
        ) from None

    if status not in {
        "processing",
        "completed",
        "failed",
    }:
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou status inválido."
        )

    return status


def _resultado_claim(
    row: Mapping[str, Any],
    *,
    status: Literal[
        "claimed",
        "reclaimed",
        "in_progress",
        "duplicate",
    ],
    claim_token: str | None,
) -> TelegramUpdateClaimResult:
    try:
        attempt_count = (
            _validar_attempt_count(
                row["attempt_count"]
            )
        )

    except (
        KeyError,
        TypeError,
    ):
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou receipt inválido."
        ) from None

    return TelegramUpdateClaimResult(
        update_id=_extrair_update_id(
            row
        ),
        status=status,
        attempt_count=attempt_count,
        claim_token=claim_token,
    )


def _resultado_lifecycle(
    row: Mapping[str, Any],
    *,
    expected_status: Literal[
        "completed",
        "failed",
    ],
) -> TelegramUpdateLifecycleResult:
    database_status = (
        _extrair_status_banco(
            row
        )
    )

    if database_status != expected_status:
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou transição inválida."
        )

    try:
        attempt_count = (
            _validar_attempt_count(
                row["attempt_count"]
            )
        )

    except (
        KeyError,
        TypeError,
    ):
        raise TelegramUpdateReceiptRepositoryError(
            "O banco retornou receipt inválido."
        ) from None

    return TelegramUpdateLifecycleResult(
        update_id=_extrair_update_id(
            row
        ),
        status=expected_status,
        attempt_count=attempt_count,
    )


def claim_telegram_update(
    *,
    update_id: int,
    update_fingerprint: str,
    claim_token: str,
    lease_seconds: int = 120,
) -> TelegramUpdateClaimResult:
    """
    Tenta assumir o processamento de um update.

    O SELECT FOR UPDATE serializa concorrência
    entre diferentes instâncias da aplicação.
    """
    normalized_update_id = (
        _validar_update_id(
            update_id
        )
    )

    normalized_fingerprint = (
        _validar_sha256(
            update_fingerprint,
            field_name=(
                "update_fingerprint"
            ),
        )
    )

    normalized_claim_token = (
        _validar_sha256(
            claim_token,
            field_name="claim_token",
        )
    )

    normalized_lease = (
        _validar_lease_seconds(
            lease_seconds
        )
    )

    parameters = {
        "update_id": (
            normalized_update_id
        ),
        "update_fingerprint": (
            normalized_fingerprint
        ),
        "claim_token": (
            normalized_claim_token
        ),
        "lease_seconds": (
            normalized_lease
        ),
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                "SET LOCAL lock_timeout "
                "= '3000ms';"
            )

            cursor.execute(
                "SET LOCAL statement_timeout "
                "= '5000ms';"
            )

            cursor.execute(
                SQL_INSERT_RECEIPT,
                parameters,
            )

            inserted = cursor.fetchone()

            if inserted is not None:
                return _resultado_claim(
                    inserted,
                    status="claimed",
                    claim_token=(
                        normalized_claim_token
                    ),
                )

            cursor.execute(
                SQL_LOCK_EXISTING_RECEIPT,
                {
                    "update_id": (
                        normalized_update_id
                    ),
                },
            )

            existing = cursor.fetchone()

            if existing is None:
                raise (
                    TelegramUpdateReceiptRepositoryError(
                        "Receipt não localizado após "
                        "conflito de update_id."
                    )
                )

            try:
                existing_fingerprint = (
                    existing[
                        "update_fingerprint"
                    ]
                )

            except (
                KeyError,
                TypeError,
            ):
                raise (
                    TelegramUpdateReceiptRepositoryError(
                        "O banco retornou fingerprint "
                        "inválido."
                    )
                ) from None

            if (
                existing_fingerprint
                != normalized_fingerprint
            ):
                raise (
                    TelegramUpdateFingerprintConflictError(
                        "O update_id já está associado "
                        "a outro conteúdo."
                    )
                )

            database_status = (
                _extrair_status_banco(
                    existing
                )
            )

            if database_status == "completed":
                cursor.execute(
                    SQL_TOUCH_RECEIPT,
                    {
                        "update_id": (
                            normalized_update_id
                        ),
                    },
                )

                return _resultado_claim(
                    existing,
                    status="duplicate",
                    claim_token=None,
                )

            lease_active = bool(
                existing.get(
                    "lease_active",
                    False,
                )
            )

            if (
                database_status == "processing"
                and lease_active
            ):
                cursor.execute(
                    SQL_TOUCH_RECEIPT,
                    {
                        "update_id": (
                            normalized_update_id
                        ),
                    },
                )

                return _resultado_claim(
                    existing,
                    status="in_progress",
                    claim_token=None,
                )

            cursor.execute(
                SQL_RECLAIM_RECEIPT,
                parameters,
            )

            reclaimed = cursor.fetchone()

            if reclaimed is None:
                raise (
                    TelegramUpdateReceiptRepositoryError(
                        "Não foi possível recuperar "
                        "o receipt Telegram."
                    )
                )

            return _resultado_claim(
                reclaimed,
                status="reclaimed",
                claim_token=(
                    normalized_claim_token
                ),
            )

    except (
        TelegramUpdateFingerprintConflictError,
        TelegramUpdateReceiptRepositoryError,
    ):
        raise

    except Exception:
        raise TelegramUpdateReceiptRepositoryError(
            "Não foi possível registrar o "
            "update Telegram."
        ) from None


def complete_telegram_update(
    *,
    update_id: int,
    claim_token: str,
) -> TelegramUpdateLifecycleResult:
    normalized_update_id = (
        _validar_update_id(
            update_id
        )
    )

    normalized_claim_token = (
        _validar_sha256(
            claim_token,
            field_name="claim_token",
        )
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                "SET LOCAL lock_timeout "
                "= '3000ms';"
            )

            cursor.execute(
                "SET LOCAL statement_timeout "
                "= '5000ms';"
            )

            cursor.execute(
                SQL_COMPLETE_RECEIPT,
                {
                    "update_id": (
                        normalized_update_id
                    ),
                    "claim_token": (
                        normalized_claim_token
                    ),
                },
            )

            row = cursor.fetchone()

            if row is None:
                raise (
                    TelegramUpdateClaimOwnershipError(
                        "O claim não está mais ativo."
                    )
                )

            return _resultado_lifecycle(
                row,
                expected_status="completed",
            )

    except (
        TelegramUpdateClaimOwnershipError,
        TelegramUpdateReceiptRepositoryError,
    ):
        raise

    except Exception:
        raise TelegramUpdateReceiptRepositoryError(
            "Não foi possível concluir o "
            "update Telegram."
        ) from None


def fail_telegram_update(
    *,
    update_id: int,
    claim_token: str,
    error_code: str,
) -> TelegramUpdateLifecycleResult:
    normalized_update_id = (
        _validar_update_id(
            update_id
        )
    )

    normalized_claim_token = (
        _validar_sha256(
            claim_token,
            field_name="claim_token",
        )
    )

    normalized_error_code = (
        _validar_error_code(
            error_code
        )
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                "SET LOCAL lock_timeout "
                "= '3000ms';"
            )

            cursor.execute(
                "SET LOCAL statement_timeout "
                "= '5000ms';"
            )

            cursor.execute(
                SQL_FAIL_RECEIPT,
                {
                    "update_id": (
                        normalized_update_id
                    ),
                    "claim_token": (
                        normalized_claim_token
                    ),
                    "error_code": (
                        normalized_error_code
                    ),
                },
            )

            row = cursor.fetchone()

            if row is None:
                raise (
                    TelegramUpdateClaimOwnershipError(
                        "O claim não está mais ativo."
                    )
                )

            return _resultado_lifecycle(
                row,
                expected_status="failed",
            )

    except (
        TelegramUpdateClaimOwnershipError,
        TelegramUpdateReceiptRepositoryError,
    ):
        raise

    except Exception:
        raise TelegramUpdateReceiptRepositoryError(
            "Não foi possível marcar a falha do "
            "update Telegram."
        ) from None


__all__ = [
    "ERROR_CODE_PATTERN",
    "SHA256_PATTERN",
    "SQL_COMPLETE_RECEIPT",
    "SQL_FAIL_RECEIPT",
    "SQL_INSERT_RECEIPT",
    "SQL_LOCK_EXISTING_RECEIPT",
    "SQL_RECLAIM_RECEIPT",
    "SQL_TOUCH_RECEIPT",
    "TelegramUpdateClaimOwnershipError",
    "TelegramUpdateClaimResult",
    "TelegramUpdateFingerprintConflictError",
    "TelegramUpdateLifecycleResult",
    "TelegramUpdateReceiptRepositoryError",
    "claim_telegram_update",
    "complete_telegram_update",
    "fail_telegram_update",
]
