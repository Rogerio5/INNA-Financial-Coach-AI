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


CompletionDecision = Literal[
    "completed",
    "already_completed",
]


SQL_LOCK_RECEIPT_FOR_COMPLETION = """
SELECT
    receipt.update_id,
    receipt.status,
    receipt.attempt_count,
    receipt.claim_token,

    (
        receipt.lease_expires_at > NOW()
    ) AS lease_active
FROM public.telegram_update_receipts AS receipt
WHERE
    receipt.update_id = %(update_id)s
FOR UPDATE;
"""


SQL_COMPLETE_OWNED_JOB = """
UPDATE public.telegram_update_jobs AS job
SET
    status = 'completed',

    payload_ciphertext = NULL,
    payload_nonce = NULL,
    payload_key_id = NULL,

    locked_at = NULL,
    lock_expires_at = NULL,
    lock_token = NULL,

    completed_at = NOW(),
    dead_lettered_at = NULL,

    last_error_code = NULL,
    updated_at = NOW()
WHERE
    job.update_id = %(update_id)s
    AND job.status = 'processing'
    AND job.lock_token = %(lock_token)s
    AND job.lock_expires_at > NOW()
RETURNING
    job.update_id,
    job.status,
    job.attempt_count,
    job.max_attempts,
    job.payload_version,

    (
        job.payload_ciphertext IS NULL
        AND job.payload_nonce IS NULL
        AND job.payload_key_id IS NULL
    ) AS payload_cleared,

    (
        job.locked_at IS NULL
        AND job.lock_expires_at IS NULL
        AND job.lock_token IS NULL
    ) AS ownership_cleared,

    (
        job.completed_at IS NOT NULL
    ) AS completed_at_set;
"""


SQL_COMPLETE_OWNED_RECEIPT = """
UPDATE public.telegram_update_receipts AS receipt
SET
    status = 'completed',

    completed_at = NOW(),
    failed_at = NULL,
    last_error_code = NULL,

    lease_expires_at = NOW()
WHERE
    receipt.update_id = %(update_id)s
    AND receipt.status = 'processing'
    AND receipt.claim_token = %(lock_token)s
    AND receipt.lease_expires_at > NOW()
RETURNING
    receipt.update_id,
    receipt.status,
    receipt.attempt_count,

    (
        receipt.completed_at IS NOT NULL
    ) AS completed_at_set,

    (
        receipt.lease_expires_at <= NOW()
    ) AS lease_closed;
"""


SQL_SELECT_COMPLETED_JOB_STATE = """
SELECT
    job.update_id,
    job.status,
    job.attempt_count,
    job.max_attempts,
    job.payload_version,

    (
        job.payload_ciphertext IS NULL
        AND job.payload_nonce IS NULL
        AND job.payload_key_id IS NULL
    ) AS payload_cleared,

    (
        job.locked_at IS NULL
        AND job.lock_expires_at IS NULL
        AND job.lock_token IS NULL
    ) AS ownership_cleared,

    (
        job.completed_at IS NOT NULL
    ) AS completed_at_set
FROM public.telegram_update_jobs AS job
WHERE
    job.update_id = %(update_id)s;
"""


class TelegramUpdateWorkerOwnershipError(
    TelegramUpdateWorkerError
):
    """
    O worker não possui mais o lease necessário.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerCompletionOutcome:
    update_id: int

    decision: CompletionDecision

    job_status: Literal[
        "completed",
    ]

    receipt_status: Literal[
        "completed",
    ]

    job_attempt_count: int
    job_max_attempts: int
    receipt_attempt_count: int

    payload_cleared: bool
    ownership_cleared: bool

    @property
    def completed(
        self,
    ) -> bool:
        return self.decision in {
            "completed",
            "already_completed",
        }

    @property
    def idempotent_replay(
        self,
    ) -> bool:
        return (
            self.decision
            == "already_completed"
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "decision": self.decision,
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
            "payload_cleared": (
                self.payload_cleared
            ),
            "ownership_cleared": (
                self.ownership_cleared
            ),
            "completed": self.completed,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class _OwnedReceiptCompletionSnapshot:
    update_id: int
    status: str
    attempt_count: int

    claim_token: str = field(
        repr=False
    )

    lease_active: bool = False


@dataclass(
    frozen=True,
    slots=True,
)
class _CompletedJobSnapshot:
    update_id: int
    status: str

    attempt_count: int
    max_attempts: int
    payload_version: int

    payload_cleared: bool
    ownership_cleared: bool
    completed_at_set: bool


@dataclass(
    frozen=True,
    slots=True,
)
class _CompletedReceiptSnapshot:
    update_id: int
    status: str
    attempt_count: int

    completed_at_set: bool
    lease_closed: bool


def _validate_completion_lease(
    lease: Any,
) -> TelegramUpdateWorkerLease:
    if not isinstance(
        lease,
        TelegramUpdateWorkerLease,
    ):
        raise TelegramUpdateWorkerValidationError(
            "Lease do worker inválido."
        )

    _validate_integer(
        lease.update_id,
        field_name="update_id",
        minimum=0,
        maximum=(
            9_223_372_036_854_775_807
        ),
    )

    if lease.job_status != "processing":
        raise TelegramUpdateWorkerValidationError(
            "O job não está em processamento."
        )

    if lease.receipt_status != "processing":
        raise TelegramUpdateWorkerValidationError(
            "O receipt não está em processamento."
        )

    job_attempt_count = _validate_integer(
        lease.job_attempt_count,
        field_name="job_attempt_count",
        minimum=1,
        maximum=20,
    )

    job_max_attempts = _validate_integer(
        lease.job_max_attempts,
        field_name="job_max_attempts",
        minimum=1,
        maximum=20,
    )

    receipt_attempt_count = _validate_integer(
        lease.receipt_attempt_count,
        field_name="receipt_attempt_count",
        minimum=1,
        maximum=1_000_000,
    )

    if (
        job_attempt_count
        > job_max_attempts
    ):
        raise TelegramUpdateWorkerValidationError(
            "As tentativas do job são inválidas."
        )

    if (
        receipt_attempt_count
        < job_attempt_count
    ):
        raise TelegramUpdateWorkerValidationError(
            "As tentativas do receipt "
            "estão atrasadas."
        )

    _validate_integer(
        lease.payload_version,
        field_name="payload_version",
        minimum=1,
        maximum=32_767,
    )

    if (
        not isinstance(
            lease.payload_key_id,
            str,
        )
        or KEY_ID_PATTERN.fullmatch(
            lease.payload_key_id
        )
        is None
    ):
        raise TelegramUpdateWorkerValidationError(
            "payload_key_id inválido."
        )

    if (
        not isinstance(
            lease.lock_token,
            str,
        )
        or SHA256_PATTERN.fullmatch(
            lease.lock_token
        )
        is None
    ):
        raise TelegramUpdateWorkerValidationError(
            "lock_token inválido."
        )

    return lease


def _owned_receipt_completion_from_row(
    row: Any,
) -> _OwnedReceiptCompletionSnapshot:
    try:
        update_id = int(
            row["update_id"]
        )

        status = str(
            row["status"]
        )

        attempt_count = int(
            row["attempt_count"]
        )

        claim_token = str(
            row["claim_token"]
        )

        lease_active = bool(
            row["lease_active"]
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
        or status not in {
            "processing",
            "completed",
            "failed",
        }
        or attempt_count < 1
        or SHA256_PATTERN.fullmatch(
            claim_token
        )
        is None
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt inválido."
        )

    return _OwnedReceiptCompletionSnapshot(
        update_id=update_id,
        status=status,
        attempt_count=attempt_count,
        claim_token=claim_token,
        lease_active=lease_active,
    )


def _completed_job_from_row(
    row: Any,
) -> _CompletedJobSnapshot:
    try:
        snapshot = _CompletedJobSnapshot(
            update_id=int(
                row["update_id"]
            ),
            status=str(
                row["status"]
            ),
            attempt_count=int(
                row["attempt_count"]
            ),
            max_attempts=int(
                row["max_attempts"]
            ),
            payload_version=int(
                row["payload_version"]
            ),
            payload_cleared=bool(
                row["payload_cleared"]
            ),
            ownership_cleared=bool(
                row["ownership_cleared"]
            ),
            completed_at_set=bool(
                row["completed_at_set"]
            ),
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um job "
            "concluído inválido."
        ) from None

    if (
        snapshot.update_id < 0
        or snapshot.status != "completed"
        or snapshot.attempt_count < 1
        or snapshot.max_attempts < 1
        or snapshot.attempt_count
        > snapshot.max_attempts
        or snapshot.payload_version < 1
        or not snapshot.payload_cleared
        or not snapshot.ownership_cleared
        or not snapshot.completed_at_set
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O job não foi concluído "
            "de forma consistente."
        )

    return snapshot


def _completed_receipt_from_row(
    row: Any,
) -> _CompletedReceiptSnapshot:
    try:
        snapshot = (
            _CompletedReceiptSnapshot(
                update_id=int(
                    row["update_id"]
                ),
                status=str(
                    row["status"]
                ),
                attempt_count=int(
                    row["attempt_count"]
                ),
                completed_at_set=bool(
                    row["completed_at_set"]
                ),
                lease_closed=bool(
                    row["lease_closed"]
                ),
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt "
            "concluído inválido."
        ) from None

    if (
        snapshot.update_id < 0
        or snapshot.status != "completed"
        or snapshot.attempt_count < 1
        or not snapshot.completed_at_set
        or not snapshot.lease_closed
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O receipt não foi concluído "
            "de forma consistente."
        )

    return snapshot



def _validate_completed_job_matches_lease(
    *,
    lease: TelegramUpdateWorkerLease,
    job: _CompletedJobSnapshot,
) -> None:
    """
    Confirma que o resultado retornado pelo banco
    corresponde exatamente ao lease do worker.

    A validação acontece antes da atualização do
    receipt para garantir rollback com o erro
    correto em caso de estado inconsistente.
    """
    if job.update_id != lease.update_id:
        raise TelegramUpdateWorkerConsistencyError(
            "O job concluído pertence "
            "a outro update."
        )

    if (
        job.attempt_count
        != lease.job_attempt_count
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "A tentativa concluída não "
            "corresponde ao lease."
        )

    if (
        job.max_attempts
        != lease.job_max_attempts
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O limite de tentativas do job "
            "não corresponde ao lease."
        )

    if (
        job.payload_version
        != lease.payload_version
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "A versão do payload não "
            "corresponde ao lease."
        )

def _build_completion_outcome(
    *,
    lease: TelegramUpdateWorkerLease,
    decision: CompletionDecision,
    job: _CompletedJobSnapshot,
    receipt_attempt_count: int,
) -> TelegramUpdateWorkerCompletionOutcome:
    _validate_completed_job_matches_lease(
        lease=lease,
        job=job,
    )

    if (
        job.update_id
        != lease.update_id
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O job concluído pertence "
            "a outro update."
        )

    if (
        job.attempt_count
        != lease.job_attempt_count
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "A tentativa concluída não "
            "corresponde ao lease."
        )

    return TelegramUpdateWorkerCompletionOutcome(
        update_id=lease.update_id,
        decision=decision,
        job_status="completed",
        receipt_status="completed",
        job_attempt_count=(
            job.attempt_count
        ),
        job_max_attempts=(
            job.max_attempts
        ),
        receipt_attempt_count=(
            receipt_attempt_count
        ),
        payload_cleared=(
            job.payload_cleared
        ),
        ownership_cleared=(
            job.ownership_cleared
        ),
    )


def complete_authenticated_telegram_update_job_atomic(
    lease: TelegramUpdateWorkerLease,
) -> TelegramUpdateWorkerCompletionOutcome:
    """
    Conclui atomicamente o job e o receipt.

    A ordem de bloqueio permanece receipt -> job,
    igual ao ingresso e ao claim do worker.

    Uma repetição com o mesmo lease, após uma
    confirmação de commit perdida, retorna
    already_completed sem repetir o processamento.
    """
    normalized_lease = (
        _validate_completion_lease(
            lease
        )
    )

    parameters = {
        "update_id": (
            normalized_lease.update_id
        ),
        "lock_token": (
            normalized_lease.lock_token
        ),
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_transaction_timeouts(
                cursor
            )

            cursor.execute(
                SQL_LOCK_RECEIPT_FOR_COMPLETION,
                {
                    "update_id": (
                        normalized_lease.update_id
                    ),
                },
            )

            receipt_row = cursor.fetchone()

            if receipt_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt do worker "
                    "não foi localizado."
                )

            owned_receipt = (
                _owned_receipt_completion_from_row(
                    receipt_row
                )
            )

            if (
                owned_receipt.update_id
                != normalized_lease.update_id
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "O receipt pertence "
                    "a outro update."
                )

            if (
                owned_receipt.claim_token
                != normalized_lease.lock_token
            ):
                raise TelegramUpdateWorkerOwnershipError(
                    "O worker não possui mais "
                    "o receipt."
                )

            if (
                owned_receipt.status
                == "completed"
            ):
                cursor.execute(
                    SQL_SELECT_COMPLETED_JOB_STATE,
                    {
                        "update_id": (
                            normalized_lease.update_id
                        ),
                    },
                )

                completed_job_row = (
                    cursor.fetchone()
                )

                if completed_job_row is None:
                    raise (
                        TelegramUpdateWorkerConsistencyError(
                            "Receipt concluído sem "
                            "job correspondente."
                        )
                    )

                completed_job = (
                    _completed_job_from_row(
                        completed_job_row
                    )
                )

                return _build_completion_outcome(
                    lease=normalized_lease,
                    decision="already_completed",
                    job=completed_job,
                    receipt_attempt_count=(
                        owned_receipt
                        .attempt_count
                    ),
                )

            if (
                owned_receipt.status
                != "processing"
            ):
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt não está mais "
                    "em processamento."
                )

            if not owned_receipt.lease_active:
                raise TelegramUpdateWorkerOwnershipError(
                    "O lease do receipt expirou."
                )

            cursor.execute(
                SQL_COMPLETE_OWNED_JOB,
                parameters,
            )

            completed_job_row = (
                cursor.fetchone()
            )

            if completed_job_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O lease do job não "
                    "está mais ativo."
                )

            completed_job = (
                _completed_job_from_row(
                    completed_job_row
                )
            )

            _validate_completed_job_matches_lease(
                lease=normalized_lease,
                job=completed_job,
            )

            cursor.execute(
                SQL_COMPLETE_OWNED_RECEIPT,
                parameters,
            )

            completed_receipt_row = (
                cursor.fetchone()
            )

            if completed_receipt_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt não pôde "
                    "ser concluído."
                )

            completed_receipt = (
                _completed_receipt_from_row(
                    completed_receipt_row
                )
            )

            if (
                completed_receipt.update_id
                != normalized_lease.update_id
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "O receipt concluído pertence "
                    "a outro update."
                )

            if (
                completed_receipt.attempt_count
                < completed_job.attempt_count
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "As tentativas do receipt "
                    "estão atrás do job."
                )

            return _build_completion_outcome(
                lease=normalized_lease,
                decision="completed",
                job=completed_job,
                receipt_attempt_count=(
                    completed_receipt
                    .attempt_count
                ),
            )

    except (
        TelegramUpdateWorkerConsistencyError,
        TelegramUpdateWorkerOwnershipError,
        TelegramUpdateWorkerValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível concluir "
            "o job Telegram."
        ) from None

FailureDecision = Literal[
    "retry_scheduled",
    "dead_lettered",
    "already_retry_scheduled",
    "already_dead_lettered",
]


WORKER_ERROR_CODE_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._:-]{0,63}$"
)


SQL_LOCK_RECEIPT_FOR_FAILURE = """
SELECT
    receipt.update_id,
    receipt.status,
    receipt.attempt_count,
    receipt.claim_token,
    receipt.last_error_code,

    (
        receipt.status = 'processing'
        AND receipt.lease_expires_at > NOW()
    ) AS lease_active
FROM public.telegram_update_receipts AS receipt
WHERE
    receipt.update_id = %(update_id)s
FOR UPDATE;
"""


SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB = """
UPDATE public.telegram_update_jobs AS job
SET
    status = CASE
        WHEN
            %(force_dead_letter)s
            OR job.attempt_count >= job.max_attempts
        THEN 'dead_letter'
        ELSE 'queued'
    END,

    available_at = CASE
        WHEN
            %(force_dead_letter)s
            OR job.attempt_count >= job.max_attempts
        THEN job.available_at
        ELSE (
            NOW()
            + (
                %(retry_delay_seconds)s
                * INTERVAL '1 second'
            )
        )
    END,

    locked_at = NULL,
    lock_expires_at = NULL,
    lock_token = NULL,

    completed_at = NULL,

    dead_lettered_at = CASE
        WHEN
            %(force_dead_letter)s
            OR job.attempt_count >= job.max_attempts
        THEN NOW()
        ELSE NULL
    END,

    last_error_code = %(error_code)s,
    updated_at = NOW()
WHERE
    job.update_id = %(update_id)s
    AND job.status = 'processing'
    AND job.lock_token = %(lock_token)s
    AND job.lock_expires_at > NOW()

    AND job.attempt_count = (
        %(job_attempt_count)s
    )

    AND job.max_attempts = (
        %(job_max_attempts)s
    )

    AND job.payload_version = (
        %(payload_version)s
    )
RETURNING
    job.update_id,
    job.status,
    job.attempt_count,
    job.max_attempts,
    job.payload_version,
    job.last_error_code,

    (
        job.payload_ciphertext IS NOT NULL
        AND job.payload_nonce IS NOT NULL
        AND job.payload_key_id IS NOT NULL
    ) AS payload_retained,

    (
        job.locked_at IS NULL
        AND job.lock_expires_at IS NULL
        AND job.lock_token IS NULL
    ) AS ownership_cleared,

    (
        job.completed_at IS NULL
    ) AS completed_at_cleared,

    (
        job.status = 'queued'
        AND job.dead_lettered_at IS NULL
    ) AS retry_state_valid,

    (
        job.status = 'dead_letter'
        AND job.dead_lettered_at IS NOT NULL
    ) AS dead_letter_state_valid;
"""


SQL_FAIL_OWNED_RECEIPT = """
UPDATE public.telegram_update_receipts AS receipt
SET
    status = 'failed',

    last_received_at = NOW(),
    lease_expires_at = NOW(),

    completed_at = NULL,
    failed_at = NOW(),

    last_error_code = %(error_code)s
WHERE
    receipt.update_id = %(update_id)s
    AND receipt.status = 'processing'
    AND receipt.claim_token = %(lock_token)s
    AND receipt.lease_expires_at > NOW()
RETURNING
    receipt.update_id,
    receipt.status,
    receipt.attempt_count,
    receipt.last_error_code,

    (
        receipt.completed_at IS NULL
    ) AS completed_at_cleared,

    (
        receipt.failed_at IS NOT NULL
    ) AS failed_at_set,

    (
        receipt.lease_expires_at <= NOW()
    ) AS lease_closed;
"""


SQL_SELECT_FAILED_JOB_STATE = """
SELECT
    job.update_id,
    job.status,
    job.attempt_count,
    job.max_attempts,
    job.payload_version,
    job.last_error_code,

    (
        job.payload_ciphertext IS NOT NULL
        AND job.payload_nonce IS NOT NULL
        AND job.payload_key_id IS NOT NULL
    ) AS payload_retained,

    (
        job.locked_at IS NULL
        AND job.lock_expires_at IS NULL
        AND job.lock_token IS NULL
    ) AS ownership_cleared,

    (
        job.completed_at IS NULL
    ) AS completed_at_cleared,

    (
        job.status = 'queued'
        AND job.dead_lettered_at IS NULL
    ) AS retry_state_valid,

    (
        job.status = 'dead_letter'
        AND job.dead_lettered_at IS NOT NULL
    ) AS dead_letter_state_valid
FROM public.telegram_update_jobs AS job
WHERE
    job.update_id = %(update_id)s;
"""


@dataclass(
    frozen=True,
    slots=True,
)
class _FailureReceiptSnapshot:
    update_id: int
    status: str
    attempt_count: int

    last_error_code: str | None

    claim_token: str = field(
        repr=False
    )

    lease_active: bool = False


@dataclass(
    frozen=True,
    slots=True,
)
class _FailedJobSnapshot:
    update_id: int
    status: Literal[
        "queued",
        "dead_letter",
    ]

    attempt_count: int
    max_attempts: int
    payload_version: int

    last_error_code: str

    payload_retained: bool
    ownership_cleared: bool
    completed_at_cleared: bool

    retry_state_valid: bool
    dead_letter_state_valid: bool


@dataclass(
    frozen=True,
    slots=True,
)
class _FailedReceiptResult:
    update_id: int

    status: Literal[
        "failed",
    ]

    attempt_count: int
    last_error_code: str

    completed_at_cleared: bool
    failed_at_set: bool
    lease_closed: bool


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerFailureOutcome:
    update_id: int

    decision: FailureDecision

    job_status: Literal[
        "queued",
        "dead_letter",
    ]

    receipt_status: Literal[
        "failed",
    ]

    job_attempt_count: int
    job_max_attempts: int
    receipt_attempt_count: int

    payload_version: int
    last_error_code: str

    retry_delay_seconds: int | None

    payload_retained: bool
    ownership_cleared: bool

    @property
    def retry_scheduled(
        self,
    ) -> bool:
        return self.job_status == "queued"

    @property
    def dead_lettered(
        self,
    ) -> bool:
        return self.job_status == "dead_letter"

    @property
    def terminal(
        self,
    ) -> bool:
        return self.dead_lettered

    @property
    def idempotent_replay(
        self,
    ) -> bool:
        return self.decision in {
            "already_retry_scheduled",
            "already_dead_lettered",
        }

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "decision": self.decision,
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
            "last_error_code": (
                self.last_error_code
            ),
            "retry_delay_seconds": (
                self.retry_delay_seconds
            ),
            "payload_retained": (
                self.payload_retained
            ),
            "ownership_cleared": (
                self.ownership_cleared
            ),
            "retry_scheduled": (
                self.retry_scheduled
            ),
            "dead_lettered": (
                self.dead_lettered
            ),
            "terminal": self.terminal,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }


def _validate_worker_error_code(
    value: Any,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TelegramUpdateWorkerValidationError(
            "error_code inválido."
        )

    normalized = value.strip()

    if (
        normalized != value
        or WORKER_ERROR_CODE_PATTERN.fullmatch(
            normalized
        )
        is None
    ):
        raise TelegramUpdateWorkerValidationError(
            "error_code inválido."
        )

    return normalized


def _validate_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise TelegramUpdateWorkerValidationError(
            f"{field_name} inválido."
        )

    return value


def _failure_receipt_from_row(
    row: Any,
) -> _FailureReceiptSnapshot:
    try:
        update_id = int(
            row["update_id"]
        )

        status = str(
            row["status"]
        )

        attempt_count = int(
            row["attempt_count"]
        )

        claim_token = str(
            row["claim_token"]
        )

        raw_error = row.get(
            "last_error_code"
        )

        last_error_code = (
            None
            if raw_error is None
            else str(raw_error)
        )

        lease_active = bool(
            row["lease_active"]
        )

    except (
        AttributeError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt "
            "de falha inválido."
        ) from None

    if (
        update_id < 0
        or status not in {
            "processing",
            "completed",
            "failed",
        }
        or attempt_count < 1
        or SHA256_PATTERN.fullmatch(
            claim_token
        )
        is None
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt "
            "de falha inválido."
        )

    if (
        last_error_code is not None
        and WORKER_ERROR_CODE_PATTERN.fullmatch(
            last_error_code
        )
        is None
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O receipt contém error_code inválido."
        )

    return _FailureReceiptSnapshot(
        update_id=update_id,
        status=status,
        attempt_count=attempt_count,
        claim_token=claim_token,
        last_error_code=last_error_code,
        lease_active=lease_active,
    )


def _failed_job_from_row(
    row: Any,
) -> _FailedJobSnapshot:
    try:
        status = str(
            row["status"]
        )

        snapshot = _FailedJobSnapshot(
            update_id=int(
                row["update_id"]
            ),
            status=status,
            attempt_count=int(
                row["attempt_count"]
            ),
            max_attempts=int(
                row["max_attempts"]
            ),
            payload_version=int(
                row["payload_version"]
            ),
            last_error_code=str(
                row["last_error_code"]
            ),
            payload_retained=bool(
                row["payload_retained"]
            ),
            ownership_cleared=bool(
                row["ownership_cleared"]
            ),
            completed_at_cleared=bool(
                row["completed_at_cleared"]
            ),
            retry_state_valid=bool(
                row["retry_state_valid"]
            ),
            dead_letter_state_valid=bool(
                row["dead_letter_state_valid"]
            ),
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um job "
            "de falha inválido."
        ) from None

    if snapshot.status not in {
        "queued",
        "dead_letter",
    }:
        raise TelegramUpdateWorkerConsistencyError(
            "O job retornou estado "
            "de falha inválido."
        )

    if (
        snapshot.update_id < 0
        or snapshot.attempt_count < 1
        or snapshot.max_attempts < 1
        or snapshot.attempt_count
        > snapshot.max_attempts
        or snapshot.payload_version < 1
        or WORKER_ERROR_CODE_PATTERN.fullmatch(
            snapshot.last_error_code
        )
        is None
        or not snapshot.payload_retained
        or not snapshot.ownership_cleared
        or not snapshot.completed_at_cleared
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O job não foi finalizado "
            "de forma consistente."
        )

    if (
        snapshot.status == "queued"
        and (
            not snapshot.retry_state_valid
            or snapshot.dead_letter_state_valid
        )
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O estado de retry é inconsistente."
        )

    if (
        snapshot.status == "dead_letter"
        and (
            not snapshot.dead_letter_state_valid
            or snapshot.retry_state_valid
        )
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O estado dead-letter é inconsistente."
        )

    return snapshot


def _failed_receipt_result_from_row(
    row: Any,
) -> _FailedReceiptResult:
    try:
        result = _FailedReceiptResult(
            update_id=int(
                row["update_id"]
            ),
            status=str(
                row["status"]
            ),
            attempt_count=int(
                row["attempt_count"]
            ),
            last_error_code=str(
                row["last_error_code"]
            ),
            completed_at_cleared=bool(
                row["completed_at_cleared"]
            ),
            failed_at_set=bool(
                row["failed_at_set"]
            ),
            lease_closed=bool(
                row["lease_closed"]
            ),
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou um receipt "
            "falho inválido."
        ) from None

    if (
        result.update_id < 0
        or result.status != "failed"
        or result.attempt_count < 1
        or WORKER_ERROR_CODE_PATTERN.fullmatch(
            result.last_error_code
        )
        is None
        or not result.completed_at_cleared
        or not result.failed_at_set
        or not result.lease_closed
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O receipt não foi marcado "
            "como falho corretamente."
        )

    return result


def _validate_failed_job_matches_lease(
    *,
    lease: TelegramUpdateWorkerLease,
    job: _FailedJobSnapshot,
    error_code: str,
) -> None:
    if job.update_id != lease.update_id:
        raise TelegramUpdateWorkerConsistencyError(
            "O job de falha pertence "
            "a outro update."
        )

    if (
        job.attempt_count
        != lease.job_attempt_count
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "A tentativa do job não "
            "corresponde ao lease."
        )

    if (
        job.max_attempts
        != lease.job_max_attempts
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O limite de tentativas não "
            "corresponde ao lease."
        )

    if (
        job.payload_version
        != lease.payload_version
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "A versão do payload não "
            "corresponde ao lease."
        )

    if job.last_error_code != error_code:
        raise TelegramUpdateWorkerConsistencyError(
            "O error_code persistido não confere."
        )


def _build_failure_outcome(
    *,
    lease: TelegramUpdateWorkerLease,
    decision: FailureDecision,
    job: _FailedJobSnapshot,
    receipt_attempt_count: int,
    retry_delay_seconds: int | None,
    error_code: str,
) -> TelegramUpdateWorkerFailureOutcome:
    _validate_failed_job_matches_lease(
        lease=lease,
        job=job,
        error_code=error_code,
    )

    if receipt_attempt_count < job.attempt_count:
        raise TelegramUpdateWorkerConsistencyError(
            "As tentativas do receipt "
            "estão atrás do job."
        )

    return TelegramUpdateWorkerFailureOutcome(
        update_id=lease.update_id,
        decision=decision,
        job_status=job.status,
        receipt_status="failed",
        job_attempt_count=(
            job.attempt_count
        ),
        job_max_attempts=(
            job.max_attempts
        ),
        receipt_attempt_count=(
            receipt_attempt_count
        ),
        payload_version=(
            job.payload_version
        ),
        last_error_code=error_code,
        retry_delay_seconds=(
            retry_delay_seconds
        ),
        payload_retained=(
            job.payload_retained
        ),
        ownership_cleared=(
            job.ownership_cleared
        ),
    )


def retry_or_dead_letter_authenticated_telegram_update_job_atomic(
    lease: TelegramUpdateWorkerLease,
    *,
    error_code: str,
    retry_delay_seconds: int,
    force_dead_letter: bool = False,
) -> TelegramUpdateWorkerFailureOutcome:
    """
    Finaliza atomicamente uma tentativa com falha.

    Falha recuperável:
        job processing -> queued
        receipt processing -> failed

    Falha definitiva ou tentativas esgotadas:
        job processing -> dead_letter
        receipt processing -> failed

    O payload permanece criptografado tanto em
    queued quanto em dead_letter, conforme o
    contrato da migration 004.

    Uma repetição com o mesmo lease e error_code
    retorna um resultado idempotente quando o
    commit anterior já tiver sido confirmado.
    """
    normalized_lease = (
        _validate_completion_lease(
            lease
        )
    )

    normalized_error = (
        _validate_worker_error_code(
            error_code
        )
    )

    normalized_delay = _validate_integer(
        retry_delay_seconds,
        field_name="retry_delay_seconds",
        minimum=0,
        maximum=(
            job_repository
            .MAX_RETRY_DELAY_SECONDS
        ),
    )

    normalized_force = _validate_boolean(
        force_dead_letter,
        field_name="force_dead_letter",
    )

    parameters = {
        "update_id": (
            normalized_lease.update_id
        ),
        "lock_token": (
            normalized_lease.lock_token
        ),
        "error_code": normalized_error,
        "retry_delay_seconds": (
            normalized_delay
        ),
        "force_dead_letter": (
            normalized_force
        ),
        "job_attempt_count": (
            normalized_lease
            .job_attempt_count
        ),
        "job_max_attempts": (
            normalized_lease
            .job_max_attempts
        ),
        "payload_version": (
            normalized_lease
            .payload_version
        ),
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_transaction_timeouts(
                cursor
            )

            cursor.execute(
                SQL_LOCK_RECEIPT_FOR_FAILURE,
                {
                    "update_id": (
                        normalized_lease.update_id
                    ),
                },
            )

            receipt_row = cursor.fetchone()

            if receipt_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt do worker "
                    "não foi localizado."
                )

            receipt = (
                _failure_receipt_from_row(
                    receipt_row
                )
            )

            if (
                receipt.update_id
                != normalized_lease.update_id
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "O receipt pertence "
                    "a outro update."
                )

            if (
                receipt.claim_token
                != normalized_lease.lock_token
            ):
                raise TelegramUpdateWorkerOwnershipError(
                    "O worker não possui mais "
                    "o receipt."
                )

            if receipt.status == "failed":
                if (
                    receipt.last_error_code
                    != normalized_error
                ):
                    raise TelegramUpdateWorkerConsistencyError(
                        "O receipt já foi finalizado "
                        "com outro error_code."
                    )

                cursor.execute(
                    SQL_SELECT_FAILED_JOB_STATE,
                    {
                        "update_id": (
                            normalized_lease.update_id
                        ),
                    },
                )

                existing_job_row = (
                    cursor.fetchone()
                )

                if existing_job_row is None:
                    raise TelegramUpdateWorkerConsistencyError(
                        "Receipt falho sem "
                        "job correspondente."
                    )

                existing_job = (
                    _failed_job_from_row(
                        existing_job_row
                    )
                )

                replay_decision: FailureDecision

                if existing_job.status == "queued":
                    replay_decision = (
                        "already_retry_scheduled"
                    )

                else:
                    replay_decision = (
                        "already_dead_lettered"
                    )

                return _build_failure_outcome(
                    lease=normalized_lease,
                    decision=replay_decision,
                    job=existing_job,
                    receipt_attempt_count=(
                        receipt.attempt_count
                    ),
                    retry_delay_seconds=None,
                    error_code=normalized_error,
                )

            if receipt.status != "processing":
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt não está mais "
                    "em processamento."
                )

            if not receipt.lease_active:
                raise TelegramUpdateWorkerOwnershipError(
                    "O lease do receipt expirou."
                )

            cursor.execute(
                SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB,
                parameters,
            )

            failed_job_row = cursor.fetchone()

            if failed_job_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O lease do job não "
                    "está mais ativo."
                )

            failed_job = _failed_job_from_row(
                failed_job_row
            )

            _validate_failed_job_matches_lease(
                lease=normalized_lease,
                job=failed_job,
                error_code=normalized_error,
            )

            cursor.execute(
                SQL_FAIL_OWNED_RECEIPT,
                parameters,
            )

            failed_receipt_row = (
                cursor.fetchone()
            )

            if failed_receipt_row is None:
                raise TelegramUpdateWorkerOwnershipError(
                    "O receipt não pôde "
                    "ser marcado como falho."
                )

            failed_receipt = (
                _failed_receipt_result_from_row(
                    failed_receipt_row
                )
            )

            if (
                failed_receipt.update_id
                != normalized_lease.update_id
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "O receipt falho pertence "
                    "a outro update."
                )

            if (
                failed_receipt.last_error_code
                != normalized_error
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "O error_code do receipt "
                    "não confere."
                )

            if failed_job.status == "queued":
                decision: FailureDecision = (
                    "retry_scheduled"
                )

                outcome_delay: int | None = (
                    normalized_delay
                )

            else:
                decision = "dead_lettered"
                outcome_delay = None

            return _build_failure_outcome(
                lease=normalized_lease,
                decision=decision,
                job=failed_job,
                receipt_attempt_count=(
                    failed_receipt
                    .attempt_count
                ),
                retry_delay_seconds=(
                    outcome_delay
                ),
                error_code=normalized_error,
            )

    except (
        TelegramUpdateWorkerConsistencyError,
        TelegramUpdateWorkerOwnershipError,
        TelegramUpdateWorkerValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível finalizar "
            "a falha do job Telegram."
        ) from None

RecoveryJobStatus = Literal[
    "queued",
    "dead_letter",
]


RECOVERY_ERROR_CODE = (
    "telegram.worker_lease_expired"
)


SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS = """
WITH candidates AS (
    SELECT
        job.update_id,
        job.lock_token
            AS previous_lock_token
    FROM public.telegram_update_jobs AS job
    INNER JOIN
        public.telegram_update_receipts
        AS receipt
        ON receipt.update_id = job.update_id
    WHERE
        job.status = 'processing'
        AND job.lock_expires_at <= NOW()
        AND job.lock_token IS NOT NULL

        AND receipt.status = 'processing'
        AND receipt.lease_expires_at <= NOW()
        AND receipt.claim_token = job.lock_token
    ORDER BY
        job.lock_expires_at,
        job.update_id
    FOR UPDATE OF receipt SKIP LOCKED
    LIMIT %(limit)s
),

updated_jobs AS (
    UPDATE public.telegram_update_jobs AS job
    SET
        status = CASE
            WHEN
                job.attempt_count
                >= job.max_attempts
            THEN 'dead_letter'
            ELSE 'queued'
        END,

        available_at = CASE
            WHEN
                job.attempt_count
                >= job.max_attempts
            THEN job.available_at
            ELSE NOW()
        END,

        locked_at = NULL,
        lock_expires_at = NULL,
        lock_token = NULL,

        completed_at = NULL,

        dead_lettered_at = CASE
            WHEN
                job.attempt_count
                >= job.max_attempts
            THEN NOW()
            ELSE NULL
        END,

        last_error_code =
            'telegram.worker_lease_expired',

        updated_at = NOW()
    FROM candidates AS candidate
    WHERE
        job.update_id = candidate.update_id
        AND job.status = 'processing'

        AND job.lock_token = (
            candidate.previous_lock_token
        )

        AND job.lock_expires_at <= NOW()
    RETURNING
        job.update_id,
        job.status,
        job.attempt_count,
        job.max_attempts,
        job.payload_version,
        job.last_error_code,

        candidate.previous_lock_token
            AS previous_lock_token,

        (
            job.payload_ciphertext
                IS NOT NULL
            AND job.payload_nonce
                IS NOT NULL
            AND job.payload_key_id
                IS NOT NULL
        ) AS payload_retained,

        (
            job.locked_at IS NULL
            AND job.lock_expires_at IS NULL
            AND job.lock_token IS NULL
        ) AS ownership_cleared
),

updated_receipts AS (
    UPDATE
        public.telegram_update_receipts
        AS receipt
    SET
        status = 'failed',

        last_received_at = NOW(),
        lease_expires_at = NOW(),

        completed_at = NULL,
        failed_at = NOW(),

        last_error_code =
            'telegram.worker_lease_expired'
    FROM updated_jobs AS job
    WHERE
        receipt.update_id = job.update_id
        AND receipt.status = 'processing'

        AND receipt.claim_token = (
            job.previous_lock_token
        )

        AND receipt.lease_expires_at <= NOW()
    RETURNING
        receipt.update_id,
        receipt.attempt_count,
        receipt.last_error_code,

        (
            receipt.completed_at IS NULL
        ) AS completed_at_cleared,

        (
            receipt.failed_at IS NOT NULL
        ) AS failed_at_set,

        (
            receipt.lease_expires_at <= NOW()
        ) AS lease_closed
),

paired AS (
    SELECT
        job.update_id,
        job.status,
        job.attempt_count,
        job.max_attempts,
        job.payload_version,
        job.last_error_code,
        job.payload_retained,
        job.ownership_cleared,

        receipt.attempt_count
            AS receipt_attempt_count,

        receipt.completed_at_cleared,
        receipt.failed_at_set,
        receipt.lease_closed
    FROM updated_jobs AS job
    INNER JOIN updated_receipts AS receipt
        ON receipt.update_id = job.update_id
)

SELECT
    COALESCE(
        (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'update_id',
                        paired.update_id,

                    'status',
                        paired.status,

                    'attempt_count',
                        paired.attempt_count,

                    'max_attempts',
                        paired.max_attempts,

                    'payload_version',
                        paired.payload_version,

                    'last_error_code',
                        paired.last_error_code,

                    'payload_retained',
                        paired.payload_retained,

                    'ownership_cleared',
                        paired.ownership_cleared,

                    'receipt_attempt_count',
                        paired.receipt_attempt_count,

                    'completed_at_cleared',
                        paired.completed_at_cleared,

                    'failed_at_set',
                        paired.failed_at_set,

                    'lease_closed',
                        paired.lease_closed
                )
                ORDER BY paired.update_id
            )
            FROM paired
        ),
        '[]'::jsonb
    ) AS records,

    (
        SELECT COUNT(*)
        FROM candidates
    ) AS candidate_count,

    (
        SELECT COUNT(*)
        FROM updated_jobs
    ) AS job_count,

    (
        SELECT COUNT(*)
        FROM updated_receipts
    ) AS receipt_count;
"""


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerRecoveryRecord:
    update_id: int

    job_status: RecoveryJobStatus

    job_attempt_count: int
    job_max_attempts: int
    receipt_attempt_count: int

    payload_version: int
    last_error_code: str

    payload_retained: bool
    ownership_cleared: bool

    @property
    def dead_lettered(
        self,
    ) -> bool:
        return (
            self.job_status
            == "dead_letter"
        )

    @property
    def retry_scheduled(
        self,
    ) -> bool:
        return (
            self.job_status
            == "queued"
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "job_status": self.job_status,
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
            "last_error_code": (
                self.last_error_code
            ),
            "payload_retained": (
                self.payload_retained
            ),
            "ownership_cleared": (
                self.ownership_cleared
            ),
            "retry_scheduled": (
                self.retry_scheduled
            ),
            "dead_lettered": (
                self.dead_lettered
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerRecoveryBatch:
    records: tuple[
        TelegramUpdateWorkerRecoveryRecord,
        ...,
    ]

    @property
    def total(
        self,
    ) -> int:
        return len(
            self.records
        )

    @property
    def retried(
        self,
    ) -> int:
        return sum(
            record.retry_scheduled
            for record in self.records
        )

    @property
    def dead_lettered(
        self,
    ) -> int:
        return sum(
            record.dead_lettered
            for record in self.records
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "total": self.total,
            "retried": self.retried,
            "dead_lettered": (
                self.dead_lettered
            ),
            "records": [
                record.to_safe_dict()
                for record in self.records
            ],
        }


def _recovery_record_from_row(
    row: Any,
) -> TelegramUpdateWorkerRecoveryRecord:
    try:
        status = str(
            row["status"]
        )

        record = (
            TelegramUpdateWorkerRecoveryRecord(
                update_id=int(
                    row["update_id"]
                ),
                job_status=status,
                job_attempt_count=int(
                    row["attempt_count"]
                ),
                job_max_attempts=int(
                    row["max_attempts"]
                ),
                receipt_attempt_count=int(
                    row[
                        "receipt_attempt_count"
                    ]
                ),
                payload_version=int(
                    row["payload_version"]
                ),
                last_error_code=str(
                    row["last_error_code"]
                ),
                payload_retained=bool(
                    row["payload_retained"]
                ),
                ownership_cleared=bool(
                    row["ownership_cleared"]
                ),
            )
        )

        completed_at_cleared = bool(
            row["completed_at_cleared"]
        )

        failed_at_set = bool(
            row["failed_at_set"]
        )

        lease_closed = bool(
            row["lease_closed"]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "O banco retornou recuperação "
            "Telegram inválida."
        ) from None

    if record.job_status not in {
        "queued",
        "dead_letter",
    }:
        raise TelegramUpdateWorkerConsistencyError(
            "A recuperação retornou "
            "status inválido."
        )

    if (
        record.update_id < 0
        or record.job_attempt_count < 1
        or record.job_max_attempts < 1
        or record.job_attempt_count
        > record.job_max_attempts
        or record.receipt_attempt_count
        < record.job_attempt_count
        or record.payload_version < 1
        or record.last_error_code
        != RECOVERY_ERROR_CODE
        or not record.payload_retained
        or not record.ownership_cleared
        or not completed_at_cleared
        or not failed_at_set
        or not lease_closed
    ):
        raise TelegramUpdateWorkerConsistencyError(
            "Job e receipt não foram "
            "recuperados consistentemente."
        )

    return record


def recover_expired_authenticated_telegram_update_jobs_atomic(
    *,
    limit: int = 100,
) -> TelegramUpdateWorkerRecoveryBatch:
    """
    Recupera atomicamente leases expirados.

    A transação bloqueia primeiro os receipts,
    atualiza os jobs e marca os receipts como
    failed usando o mesmo ownership anterior.

    Jobs com tentativas restantes voltam a queued.
    Jobs esgotados vão para dead_letter.
    """
    normalized_limit = _validate_integer(
        limit,
        field_name="limit",
        minimum=1,
        maximum=(
            job_repository
            .MAX_RECOVERY_BATCH
        ),
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
                SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS,
                {
                    "limit": normalized_limit,
                },
            )

            summary_row = cursor.fetchone()

            if summary_row is None:
                raise TelegramUpdateWorkerConsistencyError(
                    "O banco não retornou o "
                    "resumo da recuperação."
                )

            try:
                candidate_count = int(
                    summary_row[
                        "candidate_count"
                    ]
                )

                job_count = int(
                    summary_row[
                        "job_count"
                    ]
                )

                receipt_count = int(
                    summary_row[
                        "receipt_count"
                    ]
                )

                raw_records = (
                    summary_row["records"]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                raise (
                    TelegramUpdateWorkerConsistencyError(
                        "O banco retornou resumo "
                        "de recuperação inválido."
                    )
                ) from None

            if (
                candidate_count < 0
                or job_count < 0
                or receipt_count < 0
                or candidate_count
                != job_count
                or job_count
                != receipt_count
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "A recuperação de jobs e "
                    "receipts ficou divergente."
                )

            if not isinstance(
                raw_records,
                list,
            ):
                raise TelegramUpdateWorkerConsistencyError(
                    "A lista de recuperação "
                    "é inválida."
                )

            records = tuple(
                _recovery_record_from_row(
                    row
                )
                for row in raw_records
            )

            if len(records) != candidate_count:
                raise TelegramUpdateWorkerConsistencyError(
                    "A quantidade recuperada "
                    "não corresponde ao resumo."
                )

            return (
                TelegramUpdateWorkerRecoveryBatch(
                    records=records,
                )
            )

    except (
        TelegramUpdateWorkerConsistencyError,
        TelegramUpdateWorkerValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateWorkerUnavailableError(
            "Não foi possível recuperar "
            "leases Telegram expirados."
        ) from None

__all__ = [
    "RECOVERY_ERROR_CODE",
    "SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS",
    "TelegramUpdateWorkerRecoveryBatch",
    "TelegramUpdateWorkerRecoveryRecord",
    "recover_expired_authenticated_telegram_update_jobs_atomic",
    "FailureDecision",
    "SQL_FAIL_OWNED_RECEIPT",
    "SQL_LOCK_RECEIPT_FOR_FAILURE",
    "SQL_RETRY_OR_DEAD_LETTER_OWNED_JOB",
    "SQL_SELECT_FAILED_JOB_STATE",
    "TelegramUpdateWorkerFailureOutcome",
    "WORKER_ERROR_CODE_PATTERN",
    "retry_or_dead_letter_authenticated_telegram_update_job_atomic",
    "SQL_COMPLETE_OWNED_JOB",
    "SQL_COMPLETE_OWNED_RECEIPT",
    "SQL_LOCK_RECEIPT_FOR_COMPLETION",
    "SQL_SELECT_COMPLETED_JOB_STATE",
    "TelegramUpdateWorkerCompletionOutcome",
    "TelegramUpdateWorkerOwnershipError",
    "complete_authenticated_telegram_update_job_atomic",
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
