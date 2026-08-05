from __future__ import annotations

import hashlib
import json
import re
import secrets
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from . import repository


MAX_CANONICAL_UPDATE_BYTES = 1_000_000

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

ALLOWED_FAILURE_CODES = frozenset(
    {
        "telegram.processing_failed",
        "telegram.delivery_failed",
    }
)


class TelegramUpdateReceiptServiceError(RuntimeError):
    """
    Erro sanitizado da camada de serviço.
    """


class TelegramUpdateReceiptValidationError(TelegramUpdateReceiptServiceError):
    """
    O update ou argumento recebido é inválido.
    """


class TelegramUpdateReceiptConflictError(TelegramUpdateReceiptServiceError):
    """
    O mesmo update_id foi associado a outro
    conteúdo autenticado.
    """


class TelegramUpdateReceiptUnavailableError(TelegramUpdateReceiptServiceError):
    """
    O armazenamento de receipts está indisponível.
    """


class TelegramUpdateReceiptOwnershipError(TelegramUpdateReceiptServiceError):
    """
    O worker perdeu a propriedade do lease.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateProcessingLease:
    """
    Lease opaco entregue somente ao worker que
    deve processar o update.

    Token e fingerprint não aparecem no repr nem
    nas representações seguras.
    """

    update_id: int
    attempt_count: int

    claim_token: str = field(
        repr=False,
    )

    update_fingerprint: str = field(
        repr=False,
    )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "attempt_count": (self.attempt_count),
            "lease_owned": True,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateClaimDecision:
    update_id: int

    status: Literal[
        "claimed",
        "reclaimed",
        "in_progress",
        "duplicate",
    ]

    attempt_count: int

    lease: TelegramUpdateProcessingLease | None = field(
        default=None,
        repr=False,
    )

    @property
    def should_process(
        self,
    ) -> bool:
        return self.lease is not None

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
            "status": self.status,
            "attempt_count": (self.attempt_count),
            "should_process": (self.should_process),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateTransitionOutcome:
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
            "update_id": self.update_id,
            "status": self.status,
            "attempt_count": (self.attempt_count),
        }


def _extract_update_id(
    update: Mapping[str, Any],
) -> int:
    value = update.get("update_id")

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TelegramUpdateReceiptValidationError("O update Telegram é inválido.")

    return value


def serialize_telegram_update_canonical(
    update: Mapping[str, Any],
) -> bytes:
    """
    Serializa o update de forma determinística.

    Não registra nem devolve o conteúdo original.
    """
    if not isinstance(
        update,
        Mapping,
    ):
        raise TelegramUpdateReceiptValidationError("O update Telegram é inválido.")

    try:
        serialized = json.dumps(
            dict(update),
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        ).encode("utf-8")

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        raise TelegramUpdateReceiptValidationError(
            "O update Telegram é inválido."
        ) from None

    if not (2 <= len(serialized) <= MAX_CANONICAL_UPDATE_BYTES):
        raise TelegramUpdateReceiptValidationError(
            "O update Telegram possui tamanho inválido."
        )

    return serialized


def fingerprint_telegram_update(
    update: Mapping[str, Any],
) -> str:
    serialized = serialize_telegram_update_canonical(update)

    return hashlib.sha256(serialized).hexdigest()


def _generate_claim_token() -> str:
    token = secrets.token_hex(32)

    if not SHA256_PATTERN.fullmatch(token):
        raise TelegramUpdateReceiptServiceError(
            "Não foi possível criar um lease seguro."
        )

    return token


def claim_authenticated_telegram_update(
    update: Mapping[str, Any],
    *,
    lease_seconds: int = 120,
) -> TelegramUpdateClaimDecision:
    """
    Solicita um claim durável para um update cujo
    webhook já foi autenticado.
    """
    if not isinstance(
        update,
        Mapping,
    ):
        raise TelegramUpdateReceiptValidationError("O update Telegram é inválido.")

    update_id = _extract_update_id(update)

    fingerprint = fingerprint_telegram_update(update)

    claim_token = _generate_claim_token()

    try:
        result = repository.claim_telegram_update(
            update_id=update_id,
            update_fingerprint=(fingerprint),
            claim_token=claim_token,
            lease_seconds=(lease_seconds),
        )

    except ValueError:
        raise TelegramUpdateReceiptValidationError(
            "Não foi possível validar o claim do update Telegram."
        ) from None

    except repository.TelegramUpdateFingerprintConflictError:
        raise TelegramUpdateReceiptConflictError(
            "O update Telegram conflita com um registro existente."
        ) from None

    except repository.TelegramUpdateReceiptRepositoryError:
        raise TelegramUpdateReceiptUnavailableError(
            "O controle de updates Telegram está temporariamente indisponível."
        ) from None

    lease = None

    if result.should_process:
        returned_token = result.claim_token

        if returned_token != claim_token:
            raise TelegramUpdateReceiptServiceError(
                "O repositório retornou um lease inválido."
            )

        lease = TelegramUpdateProcessingLease(
            update_id=result.update_id,
            attempt_count=(result.attempt_count),
            claim_token=claim_token,
            update_fingerprint=(fingerprint),
        )

    return TelegramUpdateClaimDecision(
        update_id=result.update_id,
        status=result.status,
        attempt_count=(result.attempt_count),
        lease=lease,
    )


def _validate_lease(
    lease: Any,
) -> TelegramUpdateProcessingLease:
    if not isinstance(
        lease,
        TelegramUpdateProcessingLease,
    ):
        raise TelegramUpdateReceiptValidationError("O lease Telegram é inválido.")

    if (
        isinstance(
            lease.update_id,
            bool,
        )
        or not isinstance(
            lease.update_id,
            int,
        )
        or lease.update_id < 0
    ):
        raise TelegramUpdateReceiptValidationError("O lease Telegram é inválido.")

    if not SHA256_PATTERN.fullmatch(lease.claim_token):
        raise TelegramUpdateReceiptValidationError("O lease Telegram é inválido.")

    if not SHA256_PATTERN.fullmatch(lease.update_fingerprint):
        raise TelegramUpdateReceiptValidationError("O lease Telegram é inválido.")

    return lease


def complete_authenticated_telegram_update(
    lease: TelegramUpdateProcessingLease,
) -> TelegramUpdateTransitionOutcome:
    validated_lease = _validate_lease(lease)

    try:
        result = repository.complete_telegram_update(
            update_id=(validated_lease.update_id),
            claim_token=(validated_lease.claim_token),
        )

    except repository.TelegramUpdateClaimOwnershipError:
        raise TelegramUpdateReceiptOwnershipError(
            "O lease Telegram não está mais ativo."
        ) from None

    except repository.TelegramUpdateReceiptRepositoryError:
        raise TelegramUpdateReceiptUnavailableError(
            "Não foi possível concluir o update Telegram."
        ) from None

    return TelegramUpdateTransitionOutcome(
        update_id=result.update_id,
        status="completed",
        attempt_count=(result.attempt_count),
    )


def fail_authenticated_telegram_update(
    lease: TelegramUpdateProcessingLease,
    *,
    error_code: str = ("telegram.processing_failed"),
) -> TelegramUpdateTransitionOutcome:
    validated_lease = _validate_lease(lease)

    if (
        not isinstance(
            error_code,
            str,
        )
        or error_code not in ALLOWED_FAILURE_CODES
    ):
        raise TelegramUpdateReceiptValidationError(
            "O código de falha Telegram é inválido."
        )

    try:
        result = repository.fail_telegram_update(
            update_id=(validated_lease.update_id),
            claim_token=(validated_lease.claim_token),
            error_code=error_code,
        )

    except repository.TelegramUpdateClaimOwnershipError:
        raise TelegramUpdateReceiptOwnershipError(
            "O lease Telegram não está mais ativo."
        ) from None

    except repository.TelegramUpdateReceiptRepositoryError:
        raise TelegramUpdateReceiptUnavailableError(
            "Não foi possível registrar a falha do update Telegram."
        ) from None

    return TelegramUpdateTransitionOutcome(
        update_id=result.update_id,
        status="failed",
        attempt_count=(result.attempt_count),
    )


__all__ = [
    "ALLOWED_FAILURE_CODES",
    "MAX_CANONICAL_UPDATE_BYTES",
    "TelegramUpdateClaimDecision",
    "TelegramUpdateProcessingLease",
    "TelegramUpdateReceiptConflictError",
    "TelegramUpdateReceiptOwnershipError",
    "TelegramUpdateReceiptServiceError",
    "TelegramUpdateReceiptUnavailableError",
    "TelegramUpdateReceiptValidationError",
    "TelegramUpdateTransitionOutcome",
    "claim_authenticated_telegram_update",
    "complete_authenticated_telegram_update",
    "fail_authenticated_telegram_update",
    "fingerprint_telegram_update",
    "serialize_telegram_update_canonical",
]
