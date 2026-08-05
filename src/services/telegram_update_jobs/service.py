from __future__ import annotations

import base64
import json
import os
import re
import secrets
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)


AES_256_KEY_BYTES = 32
AES_GCM_NONCE_BYTES = 12
AES_GCM_TAG_BYTES = 16

PAYLOAD_VERSION = 1

MAX_CANONICAL_UPDATE_BYTES = 1_000_000
MAX_CIPHERTEXT_BYTES = MAX_CANONICAL_UPDATE_BYTES + AES_GCM_TAG_BYTES

MAX_TELEGRAM_UPDATE_ID = 9_223_372_036_854_775_807

DEFAULT_RETRY_BASE_SECONDS = 5
DEFAULT_RETRY_MAX_SECONDS = 3_600
MAX_RETRY_DELAY_SECONDS = 86_400

KEYS_ENV_NAME = "INNA_TELEGRAM_UPDATE_ENCRYPTION_KEYS_JSON"

ACTIVE_KEY_ENV_NAME = "INNA_TELEGRAM_UPDATE_ENCRYPTION_ACTIVE_KEY_ID"


KEY_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")

LOCK_TOKEN_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class TelegramUpdateJobServiceError(RuntimeError):
    """
    Erro sanitizado da camada de serviço.
    """


class TelegramUpdateJobValidationError(TelegramUpdateJobServiceError):
    """
    Entrada inválida ou payload incompatível.
    """


class TelegramUpdateJobConfigurationError(TelegramUpdateJobServiceError):
    """
    Configuração criptográfica inválida.
    """


class TelegramUpdateJobEncryptionError(TelegramUpdateJobServiceError):
    """
    Falha sanitizada durante a criptografia.
    """


class TelegramUpdateJobDecryptionError(TelegramUpdateJobServiceError):
    """
    Falha sanitizada durante a descriptografia.
    """


def _validate_key_id(
    value: Any,
) -> str:
    if not isinstance(value, str) or KEY_ID_PATTERN.fullmatch(value) is None:
        raise TelegramUpdateJobValidationError("Identificador de chave inválido.")

    return value


def _validate_update_id(
    value: Any,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > MAX_TELEGRAM_UPDATE_ID
    ):
        raise TelegramUpdateJobValidationError("update_id inválido.")

    return value


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


def _validate_aes_key(
    value: Any,
) -> bytes:
    return _validate_bytes(
        value,
        field_name="chave AES-256",
        minimum=AES_256_KEY_BYTES,
        maximum=AES_256_KEY_BYTES,
    )


def _decode_base64url_key(
    value: Any,
) -> bytes:
    if not isinstance(value, str) or not value.strip():
        raise TelegramUpdateJobConfigurationError("Chave criptográfica inválida.")

    encoded = value.strip()

    padding = "=" * ((-len(encoded)) % 4)

    try:
        decoded = base64.b64decode(
            encoded + padding,
            altchars=b"-_",
            validate=True,
        )

    except Exception:
        raise TelegramUpdateJobConfigurationError(
            "Chave criptográfica inválida."
        ) from None

    try:
        return _validate_aes_key(decoded)

    except TelegramUpdateJobValidationError:
        raise TelegramUpdateJobConfigurationError(
            "A chave deve possuir 256 bits."
        ) from None


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramUpdateEncryptionKeyring:
    active_key_id: str

    keys: Mapping[
        str,
        bytes,
    ] = field(repr=False)

    def __post_init__(
        self,
    ) -> None:
        try:
            active_key_id = _validate_key_id(self.active_key_id)

        except TelegramUpdateJobValidationError:
            raise TelegramUpdateJobConfigurationError("Chave ativa inválida.") from None

        if not isinstance(self.keys, Mapping) or not self.keys:
            raise TelegramUpdateJobConfigurationError(
                "Nenhuma chave criptográfica configurada."
            )

        normalized_keys: dict[
            str,
            bytes,
        ] = {}

        for raw_key_id, raw_key in self.keys.items():
            try:
                key_id = _validate_key_id(raw_key_id)

                key = _validate_aes_key(raw_key)

            except TelegramUpdateJobValidationError:
                raise TelegramUpdateJobConfigurationError(
                    "Keyring criptográfico inválido."
                ) from None

            normalized_keys[key_id] = key

        if active_key_id not in normalized_keys:
            raise TelegramUpdateJobConfigurationError(
                "A chave ativa não existe no keyring."
            )

        object.__setattr__(
            self,
            "active_key_id",
            active_key_id,
        )

        object.__setattr__(
            self,
            "keys",
            MappingProxyType(normalized_keys),
        )

    def get_key(
        self,
        key_id: str,
    ) -> bytes:
        normalized_key_id = _validate_key_id(key_id)

        key = self.keys.get(normalized_key_id)

        if key is None:
            raise TelegramUpdateJobConfigurationError(
                "Chave criptográfica não disponível."
            )

        return key


@dataclass(
    frozen=True,
    slots=True,
)
class EncryptedTelegramUpdatePayload:
    update_id: int
    payload_key_id: str
    payload_version: int

    payload_ciphertext: bytes = field(repr=False)

    payload_nonce: bytes = field(repr=False)

    def to_safe_dict(
        self,
    ) -> dict[str, int | str]:
        return {
            "update_id": self.update_id,
            "payload_key_id": (self.payload_key_id),
            "payload_version": (self.payload_version),
            "encrypted": True,
        }


def load_telegram_update_keyring_from_env() -> TelegramUpdateEncryptionKeyring:
    keys_json = os.getenv(
        KEYS_ENV_NAME,
        "",
    ).strip()

    active_key_id = os.getenv(
        ACTIVE_KEY_ENV_NAME,
        "",
    ).strip()

    if not keys_json:
        raise TelegramUpdateJobConfigurationError(f"{KEYS_ENV_NAME} não configurada.")

    if not active_key_id:
        raise TelegramUpdateJobConfigurationError(
            f"{ACTIVE_KEY_ENV_NAME} não configurada."
        )

    try:
        raw_keys = json.loads(keys_json)

    except (
        TypeError,
        ValueError,
    ):
        raise TelegramUpdateJobConfigurationError("JSON do keyring inválido.") from None

    if not isinstance(raw_keys, dict) or not raw_keys:
        raise TelegramUpdateJobConfigurationError("O keyring deve ser um objeto JSON.")

    decoded_keys: dict[
        str,
        bytes,
    ] = {}

    for raw_key_id, raw_encoded_key in raw_keys.items():
        try:
            key_id = _validate_key_id(raw_key_id)

        except TelegramUpdateJobValidationError:
            raise TelegramUpdateJobConfigurationError(
                "Identificador de chave inválido."
            ) from None

        decoded_keys[key_id] = _decode_base64url_key(raw_encoded_key)

    return TelegramUpdateEncryptionKeyring(
        active_key_id=active_key_id,
        keys=decoded_keys,
    )


def canonicalize_telegram_update(
    update: Any,
) -> tuple[
    int,
    bytes,
]:
    if not isinstance(
        update,
        dict,
    ):
        raise TelegramUpdateJobValidationError("Update Telegram inválido.")

    update_id = _validate_update_id(update.get("update_id"))

    try:
        canonical_payload = json.dumps(
            update,
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
        UnicodeError,
    ):
        raise TelegramUpdateJobValidationError(
            "Update Telegram não serializável."
        ) from None

    if not canonical_payload or len(canonical_payload) > MAX_CANONICAL_UPDATE_BYTES:
        raise TelegramUpdateJobValidationError(
            "Update Telegram excede o tamanho permitido."
        )

    return (
        update_id,
        canonical_payload,
    )


def _build_authenticated_data(
    *,
    update_id: int,
    payload_key_id: str,
    payload_version: int,
) -> bytes:
    normalized_update_id = _validate_update_id(update_id)

    normalized_key_id = _validate_key_id(payload_key_id)

    normalized_version = _validate_integer(
        payload_version,
        field_name="payload_version",
        minimum=1,
        maximum=32_767,
    )

    return (
        "inna.telegram.update-job"
        f"|version={normalized_version}"
        f"|update_id={normalized_update_id}"
        f"|key_id={normalized_key_id}"
    ).encode("utf-8")


def encrypt_authenticated_telegram_update(
    update: Any,
    *,
    keyring: TelegramUpdateEncryptionKeyring | None = None,
) -> EncryptedTelegramUpdatePayload:
    resolved_keyring = (
        keyring if keyring is not None else load_telegram_update_keyring_from_env()
    )

    update_id, plaintext = canonicalize_telegram_update(update)

    key_id = resolved_keyring.active_key_id

    key = resolved_keyring.get_key(key_id)

    nonce = secrets.token_bytes(AES_GCM_NONCE_BYTES)

    authenticated_data = _build_authenticated_data(
        update_id=update_id,
        payload_key_id=key_id,
        payload_version=PAYLOAD_VERSION,
    )

    try:
        ciphertext = AESGCM(key).encrypt(
            nonce,
            plaintext,
            authenticated_data,
        )

    except Exception:
        raise TelegramUpdateJobEncryptionError(
            "Não foi possível criptografar o update Telegram."
        ) from None

    if len(ciphertext) > MAX_CIPHERTEXT_BYTES:
        raise TelegramUpdateJobEncryptionError(
            "Payload criptografado excede o tamanho permitido."
        )

    return EncryptedTelegramUpdatePayload(
        update_id=update_id,
        payload_key_id=key_id,
        payload_version=PAYLOAD_VERSION,
        payload_ciphertext=ciphertext,
        payload_nonce=nonce,
    )


def decrypt_authenticated_telegram_update(
    *,
    update_id: int,
    payload_ciphertext: bytes,
    payload_nonce: bytes,
    payload_key_id: str,
    payload_version: int,
    keyring: TelegramUpdateEncryptionKeyring | None = None,
) -> dict[str, Any]:
    normalized_update_id = _validate_update_id(update_id)

    normalized_ciphertext = _validate_bytes(
        payload_ciphertext,
        field_name="payload_ciphertext",
        minimum=AES_GCM_TAG_BYTES,
        maximum=MAX_CIPHERTEXT_BYTES,
    )

    normalized_nonce = _validate_bytes(
        payload_nonce,
        field_name="payload_nonce",
        minimum=AES_GCM_NONCE_BYTES,
        maximum=AES_GCM_NONCE_BYTES,
    )

    normalized_key_id = _validate_key_id(payload_key_id)

    normalized_version = _validate_integer(
        payload_version,
        field_name="payload_version",
        minimum=1,
        maximum=32_767,
    )

    if normalized_version != PAYLOAD_VERSION:
        raise TelegramUpdateJobDecryptionError("Versão criptográfica não suportada.")

    resolved_keyring = (
        keyring if keyring is not None else load_telegram_update_keyring_from_env()
    )

    try:
        key = resolved_keyring.get_key(normalized_key_id)

    except TelegramUpdateJobConfigurationError:
        raise TelegramUpdateJobDecryptionError(
            "Chave criptográfica não disponível."
        ) from None

    authenticated_data = _build_authenticated_data(
        update_id=normalized_update_id,
        payload_key_id=normalized_key_id,
        payload_version=normalized_version,
    )

    try:
        plaintext = AESGCM(key).decrypt(
            normalized_nonce,
            normalized_ciphertext,
            authenticated_data,
        )

    except InvalidTag:
        raise TelegramUpdateJobDecryptionError(
            "Autenticidade do payload inválida."
        ) from None

    except Exception:
        raise TelegramUpdateJobDecryptionError(
            "Não foi possível descriptografar o update Telegram."
        ) from None

    try:
        update = json.loads(plaintext.decode("utf-8"))

    except (
        TypeError,
        ValueError,
        UnicodeError,
    ):
        raise TelegramUpdateJobDecryptionError(
            "Payload descriptografado inválido."
        ) from None

    if not isinstance(
        update,
        dict,
    ):
        raise TelegramUpdateJobDecryptionError("Payload descriptografado inválido.")

    decrypted_update_id = update.get("update_id")

    if decrypted_update_id != normalized_update_id:
        raise TelegramUpdateJobDecryptionError("Identidade do update não confere.")

    return update


def generate_telegram_update_job_lock_token() -> str:
    token = secrets.token_hex(32)

    if LOCK_TOKEN_PATTERN.fullmatch(token) is None:
        raise TelegramUpdateJobServiceError("Não foi possível gerar o lock_token.")

    return token


def calculate_telegram_update_retry_delay(
    *,
    attempt_count: int,
    base_seconds: int = (DEFAULT_RETRY_BASE_SECONDS),
    max_seconds: int = (DEFAULT_RETRY_MAX_SECONDS),
) -> int:
    normalized_attempt = _validate_integer(
        attempt_count,
        field_name="attempt_count",
        minimum=1,
        maximum=20,
    )

    normalized_base = _validate_integer(
        base_seconds,
        field_name="base_seconds",
        minimum=1,
        maximum=MAX_RETRY_DELAY_SECONDS,
    )

    normalized_max = _validate_integer(
        max_seconds,
        field_name="max_seconds",
        minimum=1,
        maximum=MAX_RETRY_DELAY_SECONDS,
    )

    if normalized_base > normalized_max:
        raise TelegramUpdateJobValidationError(
            "base_seconds não pode ser maior que max_seconds."
        )

    exponent = normalized_attempt - 1

    delay = normalized_base * (2**exponent)

    return min(
        delay,
        normalized_max,
    )


__all__ = [
    "ACTIVE_KEY_ENV_NAME",
    "AES_256_KEY_BYTES",
    "AES_GCM_NONCE_BYTES",
    "DEFAULT_RETRY_BASE_SECONDS",
    "DEFAULT_RETRY_MAX_SECONDS",
    "EncryptedTelegramUpdatePayload",
    "KEYS_ENV_NAME",
    "MAX_CANONICAL_UPDATE_BYTES",
    "MAX_CIPHERTEXT_BYTES",
    "PAYLOAD_VERSION",
    "TelegramUpdateEncryptionKeyring",
    "TelegramUpdateJobConfigurationError",
    "TelegramUpdateJobDecryptionError",
    "TelegramUpdateJobEncryptionError",
    "TelegramUpdateJobServiceError",
    "TelegramUpdateJobValidationError",
    "calculate_telegram_update_retry_delay",
    "canonicalize_telegram_update",
    "decrypt_authenticated_telegram_update",
    "encrypt_authenticated_telegram_update",
    "generate_telegram_update_job_lock_token",
    "load_telegram_update_keyring_from_env",
]
