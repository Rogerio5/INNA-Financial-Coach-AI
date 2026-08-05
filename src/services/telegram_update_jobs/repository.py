from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from src.database.connection import cursor_postgres


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

KEY_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")

ERROR_CODE_PATTERN = re.compile(r"^[a-z0-9._:-]{1,64}$")


MIN_CIPHERTEXT_BYTES = 16
MAX_CIPHERTEXT_BYTES = 1_048_576
NONCE_BYTES = 12

MIN_LEASE_SECONDS = 5
MAX_LEASE_SECONDS = 3_600

MAX_RETRY_DELAY_SECONDS = 86_400
MAX_RECOVERY_BATCH = 500


SQL_INSERT_JOB = """
INSERT INTO public.telegram_update_jobs (
    update_id,
    payload_ciphertext,
    payload_nonce,
    payload_key_id,
    payload_version,
    max_attempts
)
VALUES (
    %(update_id)s,
    %(payload_ciphertext)s,
    %(payload_nonce)s,
    %(payload_key_id)s,
    %(payload_version)s,
    %(max_attempts)s
)
ON CONFLICT (update_id) DO NOTHING
RETURNING
    update_id,
    status,
    attempt_count,
    max_attempts,
    payload_version;
"""


SQL_SELECT_JOB = """
SELECT
    update_id,
    status,
    attempt_count,
    max_attempts,
    payload_version
FROM public.telegram_update_jobs
WHERE update_id = %(update_id)s
FOR UPDATE;
"""


SQL_CLAIM_NEXT_JOB = """
WITH candidate AS (
    SELECT
        update_id
    FROM public.telegram_update_jobs
    WHERE
        status = 'queued'
        AND available_at <= NOW()
        AND attempt_count < max_attempts
    ORDER BY
        available_at,
        created_at,
        update_id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
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
    last_error_code = NULL,
    updated_at = NOW()
FROM candidate
WHERE
    job.update_id = candidate.update_id
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


SQL_RENEW_JOB_LEASE = """
UPDATE public.telegram_update_jobs
SET
    locked_at = NOW(),
    lock_expires_at = (
        NOW()
        + (
            %(lease_seconds)s
            * INTERVAL '1 second'
        )
    ),
    updated_at = NOW()
WHERE
    update_id = %(update_id)s
    AND status = 'processing'
    AND lock_token = %(lock_token)s
    AND lock_expires_at > NOW()
RETURNING
    update_id,
    status,
    attempt_count,
    max_attempts,
    payload_version;
"""


SQL_COMPLETE_JOB = """
UPDATE public.telegram_update_jobs
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
    update_id = %(update_id)s
    AND status = 'processing'
    AND lock_token = %(lock_token)s
    AND lock_expires_at > NOW()
RETURNING
    update_id,
    status,
    attempt_count,
    max_attempts,
    payload_version;
"""


SQL_RETRY_OR_DEAD_LETTER_JOB = """
UPDATE public.telegram_update_jobs
SET
    status = CASE
        WHEN attempt_count >= max_attempts
            THEN 'dead_letter'
        ELSE 'queued'
    END,

    available_at = CASE
        WHEN attempt_count >= max_attempts
            THEN available_at
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
        WHEN attempt_count >= max_attempts
            THEN NOW()
        ELSE NULL
    END,

    last_error_code = %(error_code)s,
    updated_at = NOW()
WHERE
    update_id = %(update_id)s
    AND status = 'processing'
    AND lock_token = %(lock_token)s
    AND lock_expires_at > NOW()
RETURNING
    update_id,
    status,
    attempt_count,
    max_attempts,
    payload_version;
"""


SQL_RECOVER_EXPIRED_JOBS = """
WITH expired AS (
    SELECT
        update_id
    FROM public.telegram_update_jobs
    WHERE
        status = 'processing'
        AND lock_expires_at <= NOW()
    ORDER BY
        lock_expires_at,
        update_id
    FOR UPDATE SKIP LOCKED
    LIMIT %(limit)s
)
UPDATE public.telegram_update_jobs AS job
SET
    status = CASE
        WHEN job.attempt_count >= job.max_attempts
            THEN 'dead_letter'
        ELSE 'queued'
    END,

    available_at = CASE
        WHEN job.attempt_count >= job.max_attempts
            THEN job.available_at
        ELSE NOW()
    END,

    locked_at = NULL,
    lock_expires_at = NULL,
    lock_token = NULL,

    completed_at = NULL,

    dead_lettered_at = CASE
        WHEN job.attempt_count >= job.max_attempts
            THEN NOW()
        ELSE NULL
    END,

    last_error_code = 'telegram.worker_lease_expired',
    updated_at = NOW()
FROM expired
WHERE
    job.update_id = expired.update_id
RETURNING
    job.update_id,
    job.status,
    job.attempt_count,
    job.max_attempts,
    job.payload_version;
"""


class TelegramUpdateJobRepositoryError(RuntimeError):
    """
    Erro sanitizado da camada PostgreSQL.
    """


class TelegramUpdateJobOwnershipError(TelegramUpdateJobRepositoryError):
    """
    O worker não possui um lease válido.
    """


class TelegramUpdateJobValidationError(ValueError):
    """
    Entrada rejeitada antes do banco.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateJobRecord:
    update_id: int
    status: str
    attempt_count: int
    max_attempts: int
    payload_version: int

    def to_safe_dict(
        self,
    ) -> dict[str, int | str]:
        return {
            "update_id": self.update_id,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "max_attempts": self.max_attempts,
            "payload_version": self.payload_version,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateJobLease:
    update_id: int
    attempt_count: int
    max_attempts: int
    payload_version: int

    payload_ciphertext: bytes = field(repr=False)

    payload_nonce: bytes = field(repr=False)

    payload_key_id: str = field(repr=False)

    lock_token: str = field(repr=False)

    def to_safe_dict(
        self,
    ) -> dict[str, int | str]:
        return {
            "update_id": self.update_id,
            "status": "processing",
            "attempt_count": self.attempt_count,
            "max_attempts": self.max_attempts,
            "payload_version": self.payload_version,
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
        raise TelegramUpdateJobValidationError(f"{field_name} inválido.")

    return value


def _validate_update_id(
    value: Any,
) -> int:
    return _validate_integer(
        value,
        field_name="update_id",
        minimum=0,
        maximum=9_223_372_036_854_775_807,
    )


def _validate_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise TelegramUpdateJobValidationError(f"{field_name} inválido.")

    return value


def _validate_key_id(
    value: Any,
) -> str:
    if not isinstance(value, str) or KEY_ID_PATTERN.fullmatch(value) is None:
        raise TelegramUpdateJobValidationError("payload_key_id inválido.")

    return value


def _validate_error_code(
    value: Any,
) -> str:
    if not isinstance(value, str) or ERROR_CODE_PATTERN.fullmatch(value) is None:
        raise TelegramUpdateJobValidationError("error_code inválido.")

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
        raise TelegramUpdateJobValidationError(f"{field_name} inválido.")

    normalized = bytes(value)

    if not (minimum <= len(normalized) <= maximum):
        raise TelegramUpdateJobValidationError(f"{field_name} inválido.")

    return normalized


def _record_from_row(
    row: Any,
) -> TelegramUpdateJobRecord:
    try:
        status = str(row["status"])

        if status not in {
            "queued",
            "processing",
            "completed",
            "dead_letter",
        }:
            raise ValueError

        attempt_count = int(row["attempt_count"])

        max_attempts = int(row["max_attempts"])

        payload_version = int(row["payload_version"])

        if (
            attempt_count < 0
            or max_attempts < 1
            or attempt_count > max_attempts
            or payload_version < 1
        ):
            raise ValueError

        return TelegramUpdateJobRecord(
            update_id=int(row["update_id"]),
            status=status,
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            payload_version=payload_version,
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateJobRepositoryError(
            "O banco retornou um job Telegram inválido."
        ) from None


def _lease_from_row(
    row: Any,
) -> TelegramUpdateJobLease:
    try:
        lease = TelegramUpdateJobLease(
            update_id=int(row["update_id"]),
            attempt_count=int(row["attempt_count"]),
            max_attempts=int(row["max_attempts"]),
            payload_version=int(row["payload_version"]),
            payload_ciphertext=bytes(row["payload_ciphertext"]),
            payload_nonce=bytes(row["payload_nonce"]),
            payload_key_id=str(row["payload_key_id"]),
            lock_token=str(row["lock_token"]),
        )

        _validate_bytes(
            lease.payload_ciphertext,
            field_name="payload_ciphertext",
            minimum=MIN_CIPHERTEXT_BYTES,
            maximum=MAX_CIPHERTEXT_BYTES,
        )

        _validate_bytes(
            lease.payload_nonce,
            field_name="payload_nonce",
            minimum=NONCE_BYTES,
            maximum=NONCE_BYTES,
        )

        _validate_key_id(lease.payload_key_id)

        _validate_sha256(
            lease.lock_token,
            field_name="lock_token",
        )

        if (
            lease.attempt_count < 1
            or lease.max_attempts < 1
            or lease.attempt_count > lease.max_attempts
            or lease.payload_version < 1
        ):
            raise ValueError

        return lease

    except (
        KeyError,
        TypeError,
        ValueError,
        TelegramUpdateJobValidationError,
    ):
        raise TelegramUpdateJobRepositoryError(
            "O banco retornou um lease Telegram inválido."
        ) from None


def _set_timeouts(
    cursor: Any,
) -> None:
    cursor.execute("SET LOCAL lock_timeout = '3000ms';")

    cursor.execute("SET LOCAL statement_timeout = '5000ms';")


def enqueue_telegram_update_job(
    *,
    update_id: int,
    payload_ciphertext: bytes,
    payload_nonce: bytes,
    payload_key_id: str,
    payload_version: int = 1,
    max_attempts: int = 5,
) -> TelegramUpdateJobRecord:
    normalized_update_id = _validate_update_id(update_id)

    normalized_ciphertext = _validate_bytes(
        payload_ciphertext,
        field_name="payload_ciphertext",
        minimum=MIN_CIPHERTEXT_BYTES,
        maximum=MAX_CIPHERTEXT_BYTES,
    )

    normalized_nonce = _validate_bytes(
        payload_nonce,
        field_name="payload_nonce",
        minimum=NONCE_BYTES,
        maximum=NONCE_BYTES,
    )

    normalized_key_id = _validate_key_id(payload_key_id)

    normalized_version = _validate_integer(
        payload_version,
        field_name="payload_version",
        minimum=1,
        maximum=32_767,
    )

    normalized_max_attempts = _validate_integer(
        max_attempts,
        field_name="max_attempts",
        minimum=1,
        maximum=20,
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_INSERT_JOB,
                {
                    "update_id": (normalized_update_id),
                    "payload_ciphertext": (normalized_ciphertext),
                    "payload_nonce": (normalized_nonce),
                    "payload_key_id": (normalized_key_id),
                    "payload_version": (normalized_version),
                    "max_attempts": (normalized_max_attempts),
                },
            )

            row = cursor.fetchone()

            if row is None:
                cursor.execute(
                    SQL_SELECT_JOB,
                    {
                        "update_id": (normalized_update_id),
                    },
                )

                row = cursor.fetchone()

            if row is None:
                raise TelegramUpdateJobRepositoryError(
                    "O job Telegram não foi localizado."
                )

            return _record_from_row(row)

    except (
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível enfileirar o update Telegram."
        ) from None


def claim_next_telegram_update_job(
    *,
    lock_token: str,
    lease_seconds: int = 120,
) -> TelegramUpdateJobLease | None:
    normalized_token = _validate_sha256(
        lock_token,
        field_name="lock_token",
    )

    normalized_lease = _validate_integer(
        lease_seconds,
        field_name="lease_seconds",
        minimum=MIN_LEASE_SECONDS,
        maximum=MAX_LEASE_SECONDS,
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_CLAIM_NEXT_JOB,
                {
                    "lock_token": (normalized_token),
                    "lease_seconds": (normalized_lease),
                },
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return _lease_from_row(row)

    except (
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível obter um job Telegram."
        ) from None


def renew_telegram_update_job_lease(
    *,
    update_id: int,
    lock_token: str,
    lease_seconds: int = 120,
) -> TelegramUpdateJobRecord:
    normalized_update_id = _validate_update_id(update_id)

    normalized_token = _validate_sha256(
        lock_token,
        field_name="lock_token",
    )

    normalized_lease = _validate_integer(
        lease_seconds,
        field_name="lease_seconds",
        minimum=MIN_LEASE_SECONDS,
        maximum=MAX_LEASE_SECONDS,
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_RENEW_JOB_LEASE,
                {
                    "update_id": (normalized_update_id),
                    "lock_token": (normalized_token),
                    "lease_seconds": (normalized_lease),
                },
            )

            row = cursor.fetchone()

            if row is None:
                raise TelegramUpdateJobOwnershipError(
                    "O lease do job não está mais ativo."
                )

            return _record_from_row(row)

    except (
        TelegramUpdateJobOwnershipError,
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível renovar o job Telegram."
        ) from None


def complete_telegram_update_job(
    *,
    update_id: int,
    lock_token: str,
) -> TelegramUpdateJobRecord:
    normalized_update_id = _validate_update_id(update_id)

    normalized_token = _validate_sha256(
        lock_token,
        field_name="lock_token",
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_COMPLETE_JOB,
                {
                    "update_id": (normalized_update_id),
                    "lock_token": (normalized_token),
                },
            )

            row = cursor.fetchone()

            if row is None:
                raise TelegramUpdateJobOwnershipError(
                    "O lease do job não está mais ativo."
                )

            return _record_from_row(row)

    except (
        TelegramUpdateJobOwnershipError,
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível concluir o job Telegram."
        ) from None


def retry_or_dead_letter_telegram_update_job(
    *,
    update_id: int,
    lock_token: str,
    error_code: str,
    retry_delay_seconds: int,
) -> TelegramUpdateJobRecord:
    normalized_update_id = _validate_update_id(update_id)

    normalized_token = _validate_sha256(
        lock_token,
        field_name="lock_token",
    )

    normalized_error = _validate_error_code(error_code)

    normalized_delay = _validate_integer(
        retry_delay_seconds,
        field_name="retry_delay_seconds",
        minimum=0,
        maximum=MAX_RETRY_DELAY_SECONDS,
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_RETRY_OR_DEAD_LETTER_JOB,
                {
                    "update_id": (normalized_update_id),
                    "lock_token": (normalized_token),
                    "error_code": (normalized_error),
                    "retry_delay_seconds": (normalized_delay),
                },
            )

            row = cursor.fetchone()

            if row is None:
                raise TelegramUpdateJobOwnershipError(
                    "O lease do job não está mais ativo."
                )

            return _record_from_row(row)

    except (
        TelegramUpdateJobOwnershipError,
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível reagendar o job Telegram."
        ) from None


def recover_expired_telegram_update_jobs(
    *,
    limit: int = 100,
) -> tuple[
    TelegramUpdateJobRecord,
    ...,
]:
    normalized_limit = _validate_integer(
        limit,
        field_name="limit",
        minimum=1,
        maximum=MAX_RECOVERY_BATCH,
    )

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_timeouts(cursor)

            cursor.execute(
                SQL_RECOVER_EXPIRED_JOBS,
                {
                    "limit": (normalized_limit),
                },
            )

            rows = cursor.fetchall()

            return tuple(_record_from_row(row) for row in rows)

    except (
        TelegramUpdateJobRepositoryError,
        TelegramUpdateJobValidationError,
    ):
        raise

    except Exception:
        raise TelegramUpdateJobRepositoryError(
            "Não foi possível recuperar jobs Telegram."
        ) from None


__all__ = [
    "ERROR_CODE_PATTERN",
    "KEY_ID_PATTERN",
    "MAX_CIPHERTEXT_BYTES",
    "MAX_LEASE_SECONDS",
    "MAX_RECOVERY_BATCH",
    "MAX_RETRY_DELAY_SECONDS",
    "MIN_CIPHERTEXT_BYTES",
    "MIN_LEASE_SECONDS",
    "NONCE_BYTES",
    "SHA256_PATTERN",
    "SQL_CLAIM_NEXT_JOB",
    "SQL_COMPLETE_JOB",
    "SQL_INSERT_JOB",
    "SQL_RECOVER_EXPIRED_JOBS",
    "SQL_RENEW_JOB_LEASE",
    "SQL_RETRY_OR_DEAD_LETTER_JOB",
    "SQL_SELECT_JOB",
    "TelegramUpdateJobLease",
    "TelegramUpdateJobOwnershipError",
    "TelegramUpdateJobRecord",
    "TelegramUpdateJobRepositoryError",
    "TelegramUpdateJobValidationError",
    "claim_next_telegram_update_job",
    "complete_telegram_update_job",
    "enqueue_telegram_update_job",
    "recover_expired_telegram_update_jobs",
    "renew_telegram_update_job_lease",
    "retry_or_dead_letter_telegram_update_job",
]
