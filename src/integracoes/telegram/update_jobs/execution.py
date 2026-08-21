from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import math
import re
from types import MappingProxyType
from typing import Any

from . import repository as job_repository
from . import service as crypto_service
from . import worker as worker_module


MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 100_000

MAX_UPDATE_ID = (
    9_223_372_036_854_775_807
)

SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)

KEY_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._:-]{1,64}$"
)


class TelegramUpdateExecutionError(
    RuntimeError
):
    """
    Erro sanitizado da preparação do worker.
    """


class TelegramUpdateExecutionValidationError(
    TelegramUpdateExecutionError
):
    """
    Lease inválido ou incompatível.
    """


class TelegramUpdateExecutionConfigurationError(
    TelegramUpdateExecutionError
):
    """
    Keyring criptográfico indisponível.
    """


class TelegramUpdateExecutionDecryptionError(
    TelegramUpdateExecutionError
):
    """
    Falha de autenticidade ou descriptografia.
    """


class TelegramUpdateExecutionPayloadError(
    TelegramUpdateExecutionError
):
    """
    Payload descriptografado fora do contrato.
    """


@dataclass(
    slots=True,
)
class _NodeBudget:
    remaining: int = MAX_JSON_NODES

    def consume(
        self,
    ) -> None:
        self.remaining -= 1

        if self.remaining < 0:
            raise TelegramUpdateExecutionPayloadError(
                "O payload excede a complexidade permitida."
            )


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
        raise TelegramUpdateExecutionValidationError(
            f"{field_name} inválido."
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
        raise TelegramUpdateExecutionValidationError(
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
        raise TelegramUpdateExecutionValidationError(
            f"{field_name} inválido."
        )

    return normalized


def _validate_worker_lease(
    lease: Any,
) -> worker_module.TelegramUpdateWorkerLease:
    if not isinstance(
        lease,
        worker_module.TelegramUpdateWorkerLease,
    ):
        raise TelegramUpdateExecutionValidationError(
            "Lease do worker inválido."
        )

    _validate_integer(
        lease.update_id,
        field_name="update_id",
        minimum=0,
        maximum=MAX_UPDATE_ID,
    )

    if lease.job_status != "processing":
        raise TelegramUpdateExecutionValidationError(
            "O job não está em processamento."
        )

    if lease.receipt_status != "processing":
        raise TelegramUpdateExecutionValidationError(
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

    if job_attempt_count > job_max_attempts:
        raise TelegramUpdateExecutionValidationError(
            "As tentativas do job são inválidas."
        )

    if receipt_attempt_count < job_attempt_count:
        raise TelegramUpdateExecutionValidationError(
            "As tentativas do receipt estão atrasadas."
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
        raise TelegramUpdateExecutionValidationError(
            "payload_key_id inválido."
        )

    _validate_bytes(
        lease.payload_ciphertext,
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

    _validate_bytes(
        lease.payload_nonce,
        field_name="payload_nonce",
        minimum=(
            job_repository.NONCE_BYTES
        ),
        maximum=(
            job_repository.NONCE_BYTES
        ),
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
        raise TelegramUpdateExecutionValidationError(
            "lock_token inválido."
        )

    return lease


def _freeze_json_value(
    value: Any,
    *,
    depth: int,
    budget: _NodeBudget,
) -> Any:
    budget.consume()

    if depth > MAX_JSON_DEPTH:
        raise TelegramUpdateExecutionPayloadError(
            "O payload excede a profundidade permitida."
        )

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        int,
    ):
        return value

    if isinstance(
        value,
        float,
    ):
        if not math.isfinite(
            value
        ):
            raise TelegramUpdateExecutionPayloadError(
                "O payload contém número inválido."
            )

        return value

    if isinstance(
        value,
        str,
    ):
        return value

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze_json_value(
                item,
                depth=depth + 1,
                budget=budget,
            )
            for item in value
        )

    if isinstance(
        value,
        dict,
    ):
        frozen: dict[str, Any] = {}

        for raw_key, raw_value in value.items():
            if not isinstance(
                raw_key,
                str,
            ):
                raise TelegramUpdateExecutionPayloadError(
                    "O payload contém chave inválida."
                )

            frozen[
                raw_key
            ] = _freeze_json_value(
                raw_value,
                depth=depth + 1,
                budget=budget,
            )

        return MappingProxyType(
            frozen
        )

    raise TelegramUpdateExecutionPayloadError(
        "O payload contém tipo incompatível."
    )


def _thaw_json_value(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Mapping,
    ):
        return {
            key: _thaw_json_value(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
        return [
            _thaw_json_value(
                item
            )
            for item in value
        ]

    return deepcopy(
        value
    )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateWorkerPayload:
    update_id: int

    job_attempt_count: int
    job_max_attempts: int
    receipt_attempt_count: int

    payload_version: int
    payload_key_id: str

    _payload: Mapping[
        str,
        Any,
    ] = field(
        repr=False,
        compare=False,
    )

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self._payload,
            Mapping,
        ):
            raise TelegramUpdateExecutionPayloadError(
                "Payload interno inválido."
            )

        internal_update_id = (
            self._payload.get(
                "update_id"
            )
        )

        if (
            isinstance(
                internal_update_id,
                bool,
            )
            or internal_update_id
            != self.update_id
        ):
            raise TelegramUpdateExecutionPayloadError(
                "A identidade do payload não confere."
            )

    def to_processing_dict(
        self,
    ) -> dict[str, Any]:
        """
        Entrega ao processador uma cópia mutável.

        Alterações feitas pelo processador não
        afetam a cópia protegida mantida nesta
        instância.
        """
        restored = _thaw_json_value(
            self._payload
        )

        if not isinstance(
            restored,
            dict,
        ):
            raise TelegramUpdateExecutionPayloadError(
                "Payload interno inválido."
            )

        return restored

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "update_id": self.update_id,
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
            "decrypted": True,
        }


def decrypt_authenticated_telegram_worker_lease(
    lease: worker_module.TelegramUpdateWorkerLease,
    *,
    keyring: (
        crypto_service
        .TelegramUpdateEncryptionKeyring
        | None
    ) = None,
) -> TelegramUpdateWorkerPayload:
    """
    Valida e descriptografa um lease pertencente
    ao worker.

    O conteúdo descriptografado permanece fora
    de repr, logs e retornos seguros. Uma cópia
    mutável só é criada por to_processing_dict().
    """
    normalized_lease = _validate_worker_lease(
        lease
    )

    try:
        decrypted = (
            crypto_service
            .decrypt_authenticated_telegram_update(
                update_id=(
                    normalized_lease.update_id
                ),
                payload_ciphertext=(
                    normalized_lease
                    .payload_ciphertext
                ),
                payload_nonce=(
                    normalized_lease
                    .payload_nonce
                ),
                payload_key_id=(
                    normalized_lease
                    .payload_key_id
                ),
                payload_version=(
                    normalized_lease
                    .payload_version
                ),
                keyring=keyring,
            )
        )

    except (
        crypto_service
        .TelegramUpdateJobConfigurationError
    ):
        raise TelegramUpdateExecutionConfigurationError(
            "O keyring da fila não está configurado."
        ) from None

    except (
        crypto_service
        .TelegramUpdateJobDecryptionError
    ):
        raise TelegramUpdateExecutionDecryptionError(
            "O payload do job não pôde ser autenticado."
        ) from None

    except (
        crypto_service
        .TelegramUpdateJobServiceError
    ):
        raise TelegramUpdateExecutionDecryptionError(
            "O payload do job não pôde ser processado."
        ) from None

    except Exception:
        raise TelegramUpdateExecutionDecryptionError(
            "O payload do job não pôde ser processado."
        ) from None

    if not isinstance(
        decrypted,
        dict,
    ):
        raise TelegramUpdateExecutionPayloadError(
            "O payload descriptografado é inválido."
        )

    decrypted_update_id = decrypted.get(
        "update_id"
    )

    if (
        isinstance(
            decrypted_update_id,
            bool,
        )
        or decrypted_update_id
        != normalized_lease.update_id
    ):
        raise TelegramUpdateExecutionPayloadError(
            "A identidade do payload não confere."
        )

    try:
        frozen_payload = _freeze_json_value(
            decrypted,
            depth=0,
            budget=_NodeBudget(),
        )

    except TelegramUpdateExecutionPayloadError:
        raise

    except Exception:
        raise TelegramUpdateExecutionPayloadError(
            "O payload descriptografado é inválido."
        ) from None

    if not isinstance(
        frozen_payload,
        Mapping,
    ):
        raise TelegramUpdateExecutionPayloadError(
            "O payload descriptografado é inválido."
        )

    return TelegramUpdateWorkerPayload(
        update_id=(
            normalized_lease.update_id
        ),
        job_attempt_count=(
            normalized_lease
            .job_attempt_count
        ),
        job_max_attempts=(
            normalized_lease
            .job_max_attempts
        ),
        receipt_attempt_count=(
            normalized_lease
            .receipt_attempt_count
        ),
        payload_version=(
            normalized_lease
            .payload_version
        ),
        payload_key_id=(
            normalized_lease
            .payload_key_id
        ),
        _payload=frozen_payload,
    )


__all__ = [
    "MAX_JSON_DEPTH",
    "MAX_JSON_NODES",
    "TelegramUpdateExecutionConfigurationError",
    "TelegramUpdateExecutionDecryptionError",
    "TelegramUpdateExecutionError",
    "TelegramUpdateExecutionPayloadError",
    "TelegramUpdateExecutionValidationError",
    "TelegramUpdateWorkerPayload",
    "decrypt_authenticated_telegram_worker_lease",
]
