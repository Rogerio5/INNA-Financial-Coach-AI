from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Literal

from src.database.connection import (
    cursor_postgres,
)

from . import repository as job_repository
from . import service as crypto_service


ReceiptWorkerState = Literal[
    "processing",
]

JobWorkerState = Literal[
    "processing",
]


SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

KEY_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._:-]{1,64}$"
)


SQL_SELECT_CLAIMABLE_RECEIPT = """
SELECT
    receipt.update_id,
    receipt.status AS receipt_status,
    receipt.attempt_count
        AS receipt_attempt_count
FROM public.telegram_update_jobs AS job
INNER JOIN public.telegram_update_receipts AS receipt
    ON receipt.update_id = job.update_id
WHERE
    job.status = 'queued'
    AND job.available_at <= NOW()
    AND job.attempt_count < job.max_attempts
    AND receipt.status IN (
        'processing',
        'failed'
    )
ORDER BY
    job.available_at,
    job.created_at,
    job.update_id
FOR UPDATE OF receipt SKIP LOCKED
LIMIT 1;
"""


SQL_CLAIM_JOB_BY_UPDATE_ID = """
UPDATE public.telegram_update_jobs AS job
SET
    status = 'processing',
    attempt_count = job.attempt_count + 1,

    locked_at = NOW(),

    lock_expires_at = (
        NOW()
        + (
            %(lease_seconds)s
            * INTERVAL '1 second'
        )
    ),

    lock_token = %(lock_token)s,

    completed_at = NULL,
    dead_lettered_at = NULL,
    last_error_code = NULL,

    updated_at = NOW()
WHERE
    job.update_id = %(update_id)s
    AND job.status = 'queued'
    AND job.available_at <= NOW()
    AND job.attempt_count < job.max_attempts
RETURNING
    job.update_id,
    job.attempt_count,
    job.max_attempts,
    job.payload_version,
    job.payload_ciphertext,
    job.payload_nonce,
    job.payload_key_id,
    job.lock_token;
"""


SQL_TRANSFER_RECEIPT_TO_WORKER = """
UPDATE public.telegram_update_receipts AS receipt
SET
    status = 'processing',

    claim_token = %(lock_token)s,

    attempt_count = GREATEST(
        receipt.attempt_count,
        %(job_attempt_count)s
    ),

    claimed_at = NOW(),

    lease_expires_at = (
        NOW()
        + (
            %(lease_seconds)s
            * INTERVAL '1 second'
        )
    ),

    completed_at = NULL,
    failed_at = NULL,
    last_error_code = NULL
WHERE
    receipt.update_id = %(update_id)s
    AND receipt.status IN (
        'processing',
        'failed'
    )
RETURNING
    receipt.update_id,
    receipt.status,
    receipt.attempt_count,
    receipt.claim_token;
"""


class TelegramUpdateWorkerError(
    RuntimeError
):
    """
    Erro sanitizado da camada do worker.
    """


class TelegramUpdateWorkerValidationError(
    TelegramUpdateWorkerError
):
    """
    Configuração operacional inválida.
    """


class TelegramUpdateWorkerConsistencyError(
    TelegramUpdateWorkerError
):
    """
    Receipt e job possuem estados incompatíveis.
    """


class TelegramUpdateWorkerUnavailableError(
    TelegramUpdateWorkerError
):
    """
    PostgreSQL ou fila temporariamente indisponíveis.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class _ReceiptCandidate:
    update_id: int

    receipt_status: str
    receipt_attempt_count: int


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerLease:
    update_id: int

    job_status: JobWorkerState
    receipt_status: ReceiptWorkerState

    job_attempt_count: int
    job_max_attempts: int
    receipt_attempt_count: int

    payload_version: int
    payload_key_id: str

    payload_ciphertext: bytes = field(
        repr=False
    )

    payload_nonce: bytes = field(
        repr=False
    )

    lock_token: str = field(
        repr=False
    )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "job_status": self.job_status,
            "receipt_status": (
                self.receipt_status
            ),
            "job_attempt_count": (
                self.job_attempt_count
            ),
            "job_max_attempts": (
                self.job_max_attempts
            ),
            "receipt_attempt_count": (
                self.receipt_attempt_count
            ),
            "payload_version": (
                self.payload_version
            ),
            "payload_key_id": (
                self.payload_key_id
            ),
            "encrypted": True,
        }


def _validate_integer(
    value: Any,
    *,
    field_name: str,
    minimum: int,
    maximum: int,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > maximum
    ):
        raise TelegramUpdateWorkerValidationError(
            f"{field_name} inválido."
        )

    return value


def _validate_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:
    if (
        not isinstance(value, str)
        or SHA256_PATTERN.fullmatch(value)
        is None
    ):
        raise TelegramUpdateWorkerConsistencyError(
            f"{field_name} inválido."
        )

    return value


def _validate_key_id(
    value: Any,
) -> str:
    if (
        not isinstance(value, str)
        or KEY_ID_PATTERN.fullmatch(value)
        is None
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "payload_key_id inválido."
        )

    return value


def _validate_bytes(
    value: Any,
    *,
    field_name: str,
    minimum: int,
    maximum: int,
) -> bytes:
    if not isinstance(
        value,
        (
            bytes,
            bytearray,
            memoryview,
        ),
    ):
        raise TelegramUpdateWorkerConsistencyError(
            f"{field_name} inválido."
        )

    normalized = bytes(
        value
    )

    if not (
        minimum
        <= len(normalized)
        <= maximum
    ):
        raise TelegramUpdateWorkerConsistencyError(
            f"{field_name} inválido."
        )

    return normalized


def _set_transaction_timeouts(
    cursor: Any,
) -> None:
    cursor.execute(
        "SET LOCAL lock_timeout = '3000ms';"
    )

    cursor.execute(
        "SET LOCAL statement_timeout = '5000ms';"
    )


def _candidate_from_row(
    row: Any,
) -> _ReceiptCandidate:
    try:
        update_id = int(
            row["update_id"]
        )

        receipt_status = str(
            row["receipt_status"]
        )

        receipt_attempt_count = int(
            row["receipt_attempt_count"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt inválido."
        ) from None

    if (
        update_id < 0
        or receipt_status
        not in {
            "processing",
            "failed",
        }
        or receipt_attempt_count < 1
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt inválido."
        )

    return _ReceiptCandidate(
        update_id=update_id,
        receipt_status=receipt_status,
        receipt_attempt_count=(
            receipt_attempt_count
        ),
    )


def _worker_lease_from_rows(
    *,
    candidate: _ReceiptCandidate,
    job_row: Any,
    receipt_row: Any,
) -> TelegramUpdateWorkerLease:
    try:
        job_update_id = int(
            job_row["update_id"]
        )

        job_attempt_count = int(
            job_row["attempt_count"]
        )

        job_max_attempts = int(
            job_row["max_attempts"]
        )

        payload_version = int(
            job_row["payload_version"]
        )

        payload_ciphertext = _validate_bytes(
            job_row["payload_ciphertext"],
            field_name="payload_ciphertext",
            minimum=(
                job_repository
                .MIN_CIPHERTEXT_BYTES
            ),
            maximum=(
                job_repository
                .MAX_CIPHERTEXT_BYTES
            ),
        )

        payload_nonce = _validate_bytes(
            job_row["payload_nonce"],
            field_name="payload_nonce",
            minimum=(
                job_repository
                .NONCE_BYTES
            ),
            maximum=(
                job_repository
                .NONCE_BYTES
            ),
        )

        payload_key_id = _validate_key_id(
            job_row["payload_key_id"]
        )

        lock_token = _validate_sha256(
            job_row["lock_token"],
            field_name="lock_token",
        )

        receipt_update_id = int(
            receipt_row["update_id"]
        )

        receipt_status = str(
            receipt_row["status"]
        )

        receipt_attempt_count = int(
            receipt_row["attempt_count"]
        )

        receipt_claim_token = (
            _validate_sha256(
                receipt_row["claim_token"],
                field_name="claim_token",
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        TelegramUpdateWorkerConsistencyError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um lease inválido."
        ) from None

    if (
        job_update_id != candidate.update_id
        or receipt_update_id
        != candidate.update_id
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "Job e receipt pertencem "
            "a updates diferentes."
        )

    if (
        job_attempt_count < 1
        or job_max_attempts < 1
        or job_attempt_count
        > job_max_attempts
        or payload_version < 1
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "Tentativas ou versão inválidas."
        )

    if receipt_status != "processing":
        raise TelegramUpdateWorkerConsistencyError(
            "Receipt não foi transferido "
            "ao worker."
        )

    if receipt_attempt_count < 1:
        raise TelegramUpdateWorkerConsistencyError(
            "Tentativas do receipt inválidas."
        )

    if receipt_attempt_count < job_attempt_count:
        raise TelegramUpdateWorkerConsistencyError(
            "Tentativas do receipt estão "
            "atrás do job."
        )

    if receipt_claim_token != lock_token:
        raise TelegramUpdateWorkerConsistencyError(
            "A propriedade do job e do "
            "receipt não coincide."
        )

    return TelegramUpdateWorkerLease(
        update_id=candidate.update_id,
        job_status="processing",
        receipt_status="processing",
        job_attempt_count=(
            job_attempt_count
        ),
        job_max_attempts=(
            job_max_attempts
        ),
        receipt_attempt_count=(
            receipt_attempt_count
        ),
        payload_version=payload_version,
        payload_key_id=payload_key_id,
        payload_ciphertext=(
            payload_ciphertext
        ),
        payload_nonce=payload_nonce,
        lock_token=lock_token,
    )


def claim_next_authenticated_telegram_update_job_atomic(
    *,
    lease_seconds: int = 120,
) -> TelegramUpdateWorkerLease | None:
    """
    Obtém a propriedade atômica do próximo job
    Telegram e de seu receipt correspondente.

    A ordem de bloqueio é receipt -> job, igual
    à ordem adotada pelo ingresso atômico. Isso
    reduz risco de deadlock entre webhook e worker.

    O mesmo token e o mesmo prazo de lease são
    utilizados nos dois registros.
    """
    normalized_lease = _validate_integer(
        lease_seconds,
        field_name="lease_seconds",
        minimum=(
            job_repository
            .MIN_LEASE_SECONDS
        ),
        maximum=(
            job_repository
            .MAX_LEASE_SECONDS
        ),
    )

    try:
        lock_token = (
            crypto_service
            .generate_telegram_update_job_lock_token()
        )

    except Exception:
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível gerar "
            "a propriedade do worker."
        ) from None

    if (
        not isinstance(lock_token, str)
        or SHA256_PATTERN.fullmatch(
            lock_token
        )
        is None
    ):
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível gerar "
            "a propriedade do worker."
        )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_transaction_timeouts(
                cursor
            )

            cursor.execute(
                SQL_SELECT_CLAIMABLE_RECEIPT
            )

            candidate_row = (
                cursor.fetchone()
            )

            if candidate_row is None:
                return None

            candidate = (
                _candidate_from_row(
                    candidate_row
                )
            )

            cursor.execute(
                SQL_CLAIM_JOB_BY_UPDATE_ID,
                {
                    "update_id": (
                        candidate.update_id
                    ),
                    "lock_token": lock_token,
                    "lease_seconds": (
                        normalized_lease
                    ),
                },
            )

            job_row = cursor.fetchone()

            if job_row is None:
                raise (
                    TelegramUpdateWorkerConsistencyError(
                        "O job deixou de estar "
                        "disponível durante o claim."
                    )
                )

            try:
                job_attempt_count = int(
                    job_row["attempt_count"]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                raise (
                    TelegramUpdateWorkerConsistencyError(
                        "O banco retornou tentativas "
                        "do job inválidas."
                    )
                ) from None

            cursor.execute(
                SQL_TRANSFER_RECEIPT_TO_WORKER,
                {
                    "update_id": (
                        candidate.update_id
                    ),
                    "lock_token": lock_token,
                    "lease_seconds": (
                        normalized_lease
                    ),
                    "job_attempt_count": (
                        job_attempt_count
                    ),
                },
            )

            receipt_row = (
                cursor.fetchone()
            )

            if receipt_row is None:
                raise (
                    TelegramUpdateWorkerConsistencyError(
                        "O receipt não pôde ser "
                        "transferido ao worker."
                    )
                )

            return _worker_lease_from_rows(
                candidate=candidate,
                job_row=job_row,
                receipt_row=receipt_row,
            )

    except (
        TelegramUpdateWorkerConsistencyError,
        TelegramUpdateWorkerValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível obter "
            "um job Telegram."
        ) from None


__all__ = [
    "SQL_CLAIM_JOB_BY_UPDATE_ID",
    "SQL_SELECT_CLAIMABLE_RECEIPT",
    "SQL_TRANSFER_RECEIPT_TO_WORKER",
    "TelegramUpdateWorkerConsistencyError",
    "TelegramUpdateWorkerError",
    "TelegramUpdateWorkerLease",
    "TelegramUpdateWorkerUnavailableError",
    "TelegramUpdateWorkerValidationError",
    "claim_next_authenticated_telegram_update_job_atomic",
]
