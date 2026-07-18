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

__all__ = [
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
