from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
import secrets
from typing import Any, Literal

from src.database.connection import (
    cursor_postgres,
)

from src.services.telegram_update_receipts import (
    repository as receipt_repository,
)

from src.services.telegram_update_receipts import (
    service as receipt_service,
)

from . import repository as job_repository
from . import service as crypto_service


MIN_RECEIPT_LEASE_SECONDS = 5
MAX_RECEIPT_LEASE_SECONDS = 900

MIN_JOB_ATTEMPTS = 1
MAX_JOB_ATTEMPTS = 20

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


IngressDecision = Literal[
    "enqueued",
    "already_enqueued",
    "in_progress",
    "duplicate",
]

ReceiptState = Literal[
    "claimed",
    "reclaimed",
    "processing",
    "completed",
]

JobState = Literal[
    "queued",
    "processing",
    "completed",
    "dead_letter",
]


class TelegramUpdateIngressError(RuntimeError):
    """
    Erro sanitizado da entrada durável.
    """


class TelegramUpdateIngressValidationError(TelegramUpdateIngressError):
    """
    Update ou configuração operacional inválida.
    """


class TelegramUpdateIngressConflictError(TelegramUpdateIngressError):
    """
    O update_id já pertence a outro conteúdo.
    """


class TelegramUpdateIngressConsistencyError(TelegramUpdateIngressError):
    """
    Receipt e job possuem estados incompatíveis.
    """


class TelegramUpdateIngressConfigurationError(TelegramUpdateIngressError):
    """
    Configuração criptográfica indisponível.
    """


class TelegramUpdateIngressUnavailableError(TelegramUpdateIngressError):
    """
    A entrada durável está temporariamente indisponível.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateIngressOutcome:
    update_id: int

    decision: IngressDecision
    receipt_state: ReceiptState

    receipt_attempt_count: int

    job_state: JobState | None
    job_attempt_count: int | None

    job_created: bool

    @property
    def accepted(
        self,
    ) -> bool:
        return self.decision in {
            "enqueued",
            "already_enqueued",
            "in_progress",
        }

    @property
    def duplicate(
        self,
    ) -> bool:
        return self.decision == "duplicate"

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "decision": self.decision,
            "receipt_state": (self.receipt_state),
            "receipt_attempt_count": (self.receipt_attempt_count),
            "job_state": self.job_state,
            "job_attempt_count": (self.job_attempt_count),
            "job_created": (self.job_created),
            "accepted": self.accepted,
            "duplicate": self.duplicate,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class _ReceiptSnapshot:
    update_id: int
    status: str
    attempt_count: int

    update_fingerprint: str | None = None
    lease_active: bool = False


@dataclass(
    frozen=True,
    slots=True,
)
class _JobSnapshot:
    update_id: int
    status: JobState

    attempt_count: int
    max_attempts: int
    payload_version: int


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
        raise (TelegramUpdateIngressValidationError(f"{field_name} inválido."))

    return value


def _validate_fingerprint(
    value: Any,
) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise (TelegramUpdateIngressValidationError("Fingerprint do update inválido."))

    return value


def _generate_claim_token() -> str:
    token = secrets.token_hex(32)

    if SHA256_PATTERN.fullmatch(token) is None:
        raise TelegramUpdateIngressError("Não foi possível gerar o claim_token.")

    return token


def _set_transaction_timeouts(
    cursor: Any,
) -> None:
    cursor.execute("SET LOCAL lock_timeout = '3000ms';")

    cursor.execute("SET LOCAL statement_timeout = '5000ms';")


def _receipt_snapshot_from_row(
    row: Any,
) -> _ReceiptSnapshot:
    try:
        update_id = int(row["update_id"])

        status = str(row["status"])

        attempt_count = int(row["attempt_count"])

        fingerprint_value = None

        if "update_fingerprint" in row and row["update_fingerprint"] is not None:
            fingerprint_value = str(row["update_fingerprint"])

        lease_active = bool(
            row.get(
                "lease_active",
                False,
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise (
            TelegramUpdateIngressConsistencyError(
                "O banco retornou um receipt inválido."
            )
        ) from None

    if (
        update_id < 0
        or status
        not in {
            "processing",
            "completed",
            "failed",
        }
        or attempt_count < 1
    ):
        raise TelegramUpdateIngressConsistencyError(
            "O banco retornou um receipt inválido."
        )

    if fingerprint_value is not None:
        try:
            fingerprint_value = _validate_fingerprint(fingerprint_value)

        except TelegramUpdateIngressValidationError:
            raise (
                TelegramUpdateIngressConsistencyError(
                    "O banco retornou fingerprint inválido."
                )
            ) from None

    return _ReceiptSnapshot(
        update_id=update_id,
        status=status,
        attempt_count=attempt_count,
        update_fingerprint=(fingerprint_value),
        lease_active=lease_active,
    )


def _job_snapshot_from_row(
    row: Any,
) -> _JobSnapshot:
    try:
        update_id = int(row["update_id"])

        status = str(row["status"])

        attempt_count = int(row["attempt_count"])

        max_attempts = int(row["max_attempts"])

        payload_version = int(row["payload_version"])

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise (
            TelegramUpdateIngressConsistencyError("O banco retornou um job inválido.")
        ) from None

    if status not in {
        "queued",
        "processing",
        "completed",
        "dead_letter",
    }:
        raise TelegramUpdateIngressConsistencyError("O banco retornou um job inválido.")

    if (
        update_id < 0
        or attempt_count < 0
        or max_attempts < 1
        or attempt_count > max_attempts
        or payload_version < 1
    ):
        raise TelegramUpdateIngressConsistencyError("O banco retornou um job inválido.")

    return _JobSnapshot(
        update_id=update_id,
        status=status,
        attempt_count=attempt_count,
        max_attempts=max_attempts,
        payload_version=payload_version,
    )


def _select_existing_job(
    cursor: Any,
    *,
    update_id: int,
) -> _JobSnapshot | None:
    cursor.execute(
        job_repository.SQL_SELECT_JOB,
        {
            "update_id": update_id,
        },
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return _job_snapshot_from_row(row)


def _build_duplicate_outcome(
    cursor: Any,
    *,
    receipt: _ReceiptSnapshot,
) -> TelegramUpdateIngressOutcome:
    existing_job = _select_existing_job(
        cursor,
        update_id=receipt.update_id,
    )

    if existing_job is not None and existing_job.status != "completed":
        raise (
            TelegramUpdateIngressConsistencyError(
                "Receipt concluído possui job ativo ou incompatível."
            )
        )

    return TelegramUpdateIngressOutcome(
        update_id=receipt.update_id,
        decision="duplicate",
        receipt_state="completed",
        receipt_attempt_count=(receipt.attempt_count),
        job_state=(existing_job.status if existing_job is not None else None),
        job_attempt_count=(
            existing_job.attempt_count if existing_job is not None else None
        ),
        job_created=False,
    )


def _ensure_encrypted_job(
    cursor: Any,
    *,
    update: dict[str, Any],
    update_id: int,
    receipt_state: ReceiptState,
    receipt_attempt_count: int,
    max_attempts: int,
    keyring: (crypto_service.TelegramUpdateEncryptionKeyring | None),
) -> TelegramUpdateIngressOutcome:
    encrypted = crypto_service.encrypt_authenticated_telegram_update(
        update,
        keyring=keyring,
    )

    if encrypted.update_id != update_id:
        raise TelegramUpdateIngressConsistencyError(
            "Identidade criptográfica do update inválida."
        )

    cursor.execute(
        job_repository.SQL_INSERT_JOB,
        {
            "update_id": update_id,
            "payload_ciphertext": (encrypted.payload_ciphertext),
            "payload_nonce": (encrypted.payload_nonce),
            "payload_key_id": (encrypted.payload_key_id),
            "payload_version": (encrypted.payload_version),
            "max_attempts": max_attempts,
        },
    )

    row = cursor.fetchone()

    job_created = row is not None

    if row is None:
        cursor.execute(
            job_repository.SQL_SELECT_JOB,
            {
                "update_id": update_id,
            },
        )

        row = cursor.fetchone()

    if row is None:
        raise TelegramUpdateIngressConsistencyError(
            "O job não foi criado nem localizado."
        )

    job = _job_snapshot_from_row(row)

    if job.update_id != update_id:
        raise TelegramUpdateIngressConsistencyError(
            "O banco retornou outro job Telegram."
        )

    if job.status == "completed":
        raise TelegramUpdateIngressConsistencyError(
            "Receipt pendente possui job concluído."
        )

    if job.status == "dead_letter":
        raise TelegramUpdateIngressConsistencyError(
            "O update possui job em dead-letter."
        )

    if job_created:
        decision: IngressDecision = "enqueued"

    elif job.status == "processing":
        decision = "in_progress"

    else:
        decision = "already_enqueued"

    return TelegramUpdateIngressOutcome(
        update_id=update_id,
        decision=decision,
        receipt_state=receipt_state,
        receipt_attempt_count=(receipt_attempt_count),
        job_state=job.status,
        job_attempt_count=(job.attempt_count),
        job_created=job_created,
    )


def enqueue_authenticated_telegram_update_atomic(
    update: Mapping[str, Any],
    *,
    receipt_lease_seconds: int = 120,
    max_attempts: int = 5,
    keyring: (crypto_service.TelegramUpdateEncryptionKeyring | None) = None,
) -> TelegramUpdateIngressOutcome:
    """
    Registra o receipt e o job criptografado na
    mesma transação PostgreSQL.

    O webhook deve chamar esta função somente após
    a autenticação do segredo do Telegram.

    Nenhum payload, nonce, chave, fingerprint ou
    token de claim é retornado.
    """
    if not isinstance(
        update,
        Mapping,
    ):
        raise TelegramUpdateIngressValidationError("O update Telegram é inválido.")

    normalized_lease = _validate_integer(
        receipt_lease_seconds,
        field_name="receipt_lease_seconds",
        minimum=MIN_RECEIPT_LEASE_SECONDS,
        maximum=MAX_RECEIPT_LEASE_SECONDS,
    )

    normalized_max_attempts = _validate_integer(
        max_attempts,
        field_name="max_attempts",
        minimum=MIN_JOB_ATTEMPTS,
        maximum=MAX_JOB_ATTEMPTS,
    )

    normalized_update = dict(update)

    try:
        update_id, _ = crypto_service.canonicalize_telegram_update(normalized_update)

    except crypto_service.TelegramUpdateJobValidationError:
        raise (
            TelegramUpdateIngressValidationError("O update Telegram é inválido.")
        ) from None

    try:
        update_fingerprint = receipt_service.fingerprint_telegram_update(
            normalized_update
        )

    except Exception:
        raise (
            TelegramUpdateIngressValidationError("Não foi possível validar o update.")
        ) from None

    normalized_fingerprint = _validate_fingerprint(update_fingerprint)

    claim_token = _generate_claim_token()

    receipt_parameters = {
        "update_id": update_id,
        "update_fingerprint": (normalized_fingerprint),
        "claim_token": claim_token,
        "lease_seconds": normalized_lease,
    }

    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            _set_transaction_timeouts(cursor)

            cursor.execute(
                receipt_repository.SQL_INSERT_RECEIPT,
                receipt_parameters,
            )

            inserted_receipt_row = cursor.fetchone()

            if inserted_receipt_row is not None:
                inserted_receipt = _receipt_snapshot_from_row(inserted_receipt_row)

                return _ensure_encrypted_job(
                    cursor,
                    update=normalized_update,
                    update_id=update_id,
                    receipt_state="claimed",
                    receipt_attempt_count=(inserted_receipt.attempt_count),
                    max_attempts=(normalized_max_attempts),
                    keyring=keyring,
                )

            cursor.execute(
                receipt_repository.SQL_LOCK_EXISTING_RECEIPT,
                {
                    "update_id": update_id,
                },
            )

            existing_row = cursor.fetchone()

            if existing_row is None:
                raise (
                    TelegramUpdateIngressConsistencyError(
                        "O receipt não foi criado nem localizado."
                    )
                )

            existing = _receipt_snapshot_from_row(existing_row)

            if existing.update_id != update_id:
                raise (
                    TelegramUpdateIngressConsistencyError(
                        "O banco retornou outro receipt."
                    )
                )

            if existing.update_fingerprint != normalized_fingerprint:
                raise (
                    TelegramUpdateIngressConflictError(
                        "O update_id já está associado a outro conteúdo."
                    )
                )

            if existing.status == "completed":
                cursor.execute(
                    receipt_repository.SQL_TOUCH_RECEIPT,
                    {
                        "update_id": update_id,
                    },
                )

                return _build_duplicate_outcome(
                    cursor,
                    receipt=existing,
                )

            if existing.status == "processing" and existing.lease_active:
                cursor.execute(
                    receipt_repository.SQL_TOUCH_RECEIPT,
                    {
                        "update_id": update_id,
                    },
                )

                return _ensure_encrypted_job(
                    cursor,
                    update=normalized_update,
                    update_id=update_id,
                    receipt_state="processing",
                    receipt_attempt_count=(existing.attempt_count),
                    max_attempts=(normalized_max_attempts),
                    keyring=keyring,
                )

            cursor.execute(
                receipt_repository.SQL_RECLAIM_RECEIPT,
                receipt_parameters,
            )

            reclaimed_row = cursor.fetchone()

            if reclaimed_row is None:
                raise (
                    TelegramUpdateIngressConsistencyError(
                        "Não foi possível recuperar o receipt Telegram."
                    )
                )

            reclaimed = _receipt_snapshot_from_row(reclaimed_row)

            return _ensure_encrypted_job(
                cursor,
                update=normalized_update,
                update_id=update_id,
                receipt_state="reclaimed",
                receipt_attempt_count=(reclaimed.attempt_count),
                max_attempts=(normalized_max_attempts),
                keyring=keyring,
            )

    except (
        TelegramUpdateIngressConflictError,
        TelegramUpdateIngressConsistencyError,
        TelegramUpdateIngressValidationError,
    ):
        raise

    except crypto_service.TelegramUpdateJobConfigurationError:
        raise (
            TelegramUpdateIngressConfigurationError(
                "A criptografia da fila não está configurada."
            )
        ) from None

    except crypto_service.TelegramUpdateJobEncryptionError:
        raise (
            TelegramUpdateIngressUnavailableError(
                "Não foi possível proteger o update Telegram."
            )
        ) from None

    except Exception:
        raise (
            TelegramUpdateIngressUnavailableError(
                "Não foi possível registrar o update Telegram."
            )
        ) from None


__all__ = [
    "MAX_JOB_ATTEMPTS",
    "MAX_RECEIPT_LEASE_SECONDS",
    "MIN_JOB_ATTEMPTS",
    "MIN_RECEIPT_LEASE_SECONDS",
    "TelegramUpdateIngressConfigurationError",
    "TelegramUpdateIngressConflictError",
    "TelegramUpdateIngressConsistencyError",
    "TelegramUpdateIngressError",
    "TelegramUpdateIngressOutcome",
    "TelegramUpdateIngressUnavailableError",
    "TelegramUpdateIngressValidationError",
    "enqueue_authenticated_telegram_update_atomic",
]
