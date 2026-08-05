from __future__ import annotations

import base64
import json
import re

import pytest

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)

from src.services.telegram_update_jobs import (
    service,
)


KEY_ID_V1 = "inna.telegram.v1"
KEY_ID_V2 = "inna.telegram.v2"

KEY_V1 = b"a" * 32
KEY_V2 = b"b" * 32

UPDATE_ID = 123456789


def make_keyring(
    *,
    active_key_id: str = KEY_ID_V1,
    include_v1: bool = True,
    include_v2: bool = False,
):
    keys = {}

    if include_v1:
        keys[KEY_ID_V1] = KEY_V1

    if include_v2:
        keys[KEY_ID_V2] = KEY_V2

    return service.TelegramUpdateEncryptionKeyring(
        active_key_id=active_key_id,
        keys=keys,
    )


def make_update(
    update_id: int = UPDATE_ID,
):
    return {
        "update_id": update_id,
        "message": {
            "message_id": 100,
            "chat": {
                "id": 200,
            },
            "text": ("Quero organizar minhas finanças."),
        },
    }


def make_aad(
    *,
    update_id: int,
    key_id: str = KEY_ID_V1,
    version: int = 1,
) -> bytes:
    return (
        "inna.telegram.update-job"
        f"|version={version}"
        f"|update_id={update_id}"
        f"|key_id={key_id}"
    ).encode("utf-8")


def test_keyring_accepts_valid_aes_256_key():
    keyring = make_keyring()

    assert keyring.active_key_id == KEY_ID_V1

    assert keyring.get_key(KEY_ID_V1) == KEY_V1


def test_keyring_repr_hides_secret_keys():
    keyring = make_keyring()

    representation = repr(keyring)

    assert repr(KEY_V1) not in representation
    assert "keys=" not in representation


def test_keyring_rejects_empty_keys():
    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.TelegramUpdateEncryptionKeyring(
            active_key_id=KEY_ID_V1,
            keys={},
        )


def test_keyring_rejects_missing_active_key():
    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.TelegramUpdateEncryptionKeyring(
            active_key_id=KEY_ID_V2,
            keys={
                KEY_ID_V1: KEY_V1,
            },
        )


def test_keyring_rejects_invalid_key_id():
    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.TelegramUpdateEncryptionKeyring(
            active_key_id="invalid key",
            keys={
                "invalid key": KEY_V1,
            },
        )


def test_keyring_rejects_wrong_key_length():
    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.TelegramUpdateEncryptionKeyring(
            active_key_id=KEY_ID_V1,
            keys={
                KEY_ID_V1: b"x" * 31,
            },
        )


def test_get_key_rejects_unknown_key():
    keyring = make_keyring()

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        keyring.get_key(KEY_ID_V2)


def test_load_keyring_from_environment(
    monkeypatch,
):
    encoded_key = base64.urlsafe_b64encode(KEY_V1).decode("ascii").rstrip("=")

    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        json.dumps(
            {
                KEY_ID_V1: encoded_key,
            }
        ),
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    keyring = service.load_telegram_update_keyring_from_env()

    assert keyring.get_key(KEY_ID_V1) == KEY_V1


def test_environment_rejects_missing_keys(
    monkeypatch,
):
    monkeypatch.delenv(
        service.KEYS_ENV_NAME,
        raising=False,
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_environment_rejects_missing_active_key(
    monkeypatch,
):
    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        "{}",
    )

    monkeypatch.delenv(
        service.ACTIVE_KEY_ENV_NAME,
        raising=False,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_environment_rejects_invalid_json(
    monkeypatch,
):
    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        "{invalid-json",
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_environment_rejects_non_object_json(
    monkeypatch,
):
    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        '["not", "an", "object"]',
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_environment_rejects_invalid_base64(
    monkeypatch,
):
    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        json.dumps(
            {
                KEY_ID_V1: "***invalid***",
            }
        ),
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_environment_rejects_wrong_key_length(
    monkeypatch,
):
    encoded_key = base64.urlsafe_b64encode(b"x" * 31).decode("ascii").rstrip("=")

    monkeypatch.setenv(
        service.KEYS_ENV_NAME,
        json.dumps(
            {
                KEY_ID_V1: encoded_key,
            }
        ),
    )

    monkeypatch.setenv(
        service.ACTIVE_KEY_ENV_NAME,
        KEY_ID_V1,
    )

    with pytest.raises(service.TelegramUpdateJobConfigurationError):
        service.load_telegram_update_keyring_from_env()


def test_canonicalization_is_stable():
    first = {
        "message": {
            "text": "teste",
            "chat": {
                "id": 10,
            },
        },
        "update_id": UPDATE_ID,
    }

    second = {
        "update_id": UPDATE_ID,
        "message": {
            "chat": {
                "id": 10,
            },
            "text": "teste",
        },
    }

    first_id, first_payload = service.canonicalize_telegram_update(first)

    second_id, second_payload = service.canonicalize_telegram_update(second)

    assert first_id == second_id
    assert first_payload == second_payload


def test_canonicalization_preserves_unicode():
    update = {
        "update_id": UPDATE_ID,
        "message": {
            "text": "Educação financeira 💰",
        },
    }

    _, payload = service.canonicalize_telegram_update(update)

    decoded = payload.decode("utf-8")

    assert "Educação financeira" in decoded
    assert "💰" in decoded


def test_nonserializable_update_is_rejected():
    update = {
        "update_id": UPDATE_ID,
        "invalid": {
            "set-value",
        },
    }

    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.canonicalize_telegram_update(update)


def test_nan_value_is_rejected():
    update = {
        "update_id": UPDATE_ID,
        "value": float("nan"),
    }

    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.canonicalize_telegram_update(update)


def test_oversized_update_is_rejected():
    update = {
        "update_id": UPDATE_ID,
        "message": {
            "text": ("x" * (service.MAX_CANONICAL_UPDATE_BYTES + 1)),
        },
    }

    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.canonicalize_telegram_update(update)


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        "telegram-update",
    ],
    ids=[
        "none",
        "list",
        "string",
    ],
)
def test_invalid_update_container_is_rejected(
    value,
):
    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.canonicalize_telegram_update(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        -1,
        "123",
        9_223_372_036_854_775_808,
    ],
    ids=[
        "missing",
        "boolean",
        "negative",
        "string",
        "overflow",
    ],
)
def test_invalid_update_id_is_rejected(
    value,
):
    update = {
        "update_id": value,
    }

    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.canonicalize_telegram_update(update)


def test_encrypt_and_decrypt_round_trip():
    keyring = make_keyring()
    update = make_update()

    encrypted = service.encrypt_authenticated_telegram_update(
        update,
        keyring=keyring,
    )

    decrypted = service.decrypt_authenticated_telegram_update(
        update_id=encrypted.update_id,
        payload_ciphertext=(encrypted.payload_ciphertext),
        payload_nonce=(encrypted.payload_nonce),
        payload_key_id=(encrypted.payload_key_id),
        payload_version=(encrypted.payload_version),
        keyring=keyring,
    )

    assert decrypted == update


def test_encrypted_payload_hides_sensitive_fields():
    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=make_keyring(),
    )

    safe = encrypted.to_safe_dict()
    representation = repr(encrypted)

    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe
    assert repr(encrypted.payload_ciphertext) not in representation

    assert repr(encrypted.payload_nonce) not in representation


def test_encryption_creates_nonce_and_ciphertext():
    update = make_update()

    _, canonical = service.canonicalize_telegram_update(update)

    encrypted = service.encrypt_authenticated_telegram_update(
        update,
        keyring=make_keyring(),
    )

    assert len(encrypted.payload_nonce) == service.AES_GCM_NONCE_BYTES

    assert encrypted.payload_ciphertext != canonical

    assert len(encrypted.payload_ciphertext) == (
        len(canonical) + service.AES_GCM_TAG_BYTES
    )


def test_encryption_uses_active_key():
    keyring = make_keyring(
        active_key_id=KEY_ID_V2,
        include_v1=True,
        include_v2=True,
    )

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=keyring,
    )

    assert encrypted.payload_key_id == KEY_ID_V2


def test_old_key_remains_available_after_rotation():
    old_keyring = make_keyring(
        active_key_id=KEY_ID_V1,
        include_v1=True,
        include_v2=False,
    )

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=old_keyring,
    )

    rotated_keyring = make_keyring(
        active_key_id=KEY_ID_V2,
        include_v1=True,
        include_v2=True,
    )

    decrypted = service.decrypt_authenticated_telegram_update(
        update_id=encrypted.update_id,
        payload_ciphertext=(encrypted.payload_ciphertext),
        payload_nonce=(encrypted.payload_nonce),
        payload_key_id=(encrypted.payload_key_id),
        payload_version=(encrypted.payload_version),
        keyring=rotated_keyring,
    )

    assert decrypted == make_update()


def test_tampered_ciphertext_is_rejected():
    keyring = make_keyring()

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=keyring,
    )

    tampered = bytearray(encrypted.payload_ciphertext)

    tampered[-1] ^= 1

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=encrypted.update_id,
            payload_ciphertext=bytes(tampered),
            payload_nonce=encrypted.payload_nonce,
            payload_key_id=encrypted.payload_key_id,
            payload_version=encrypted.payload_version,
            keyring=keyring,
        )


def test_tampered_nonce_is_rejected():
    keyring = make_keyring()

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=keyring,
    )

    tampered_nonce = bytearray(encrypted.payload_nonce)

    tampered_nonce[0] ^= 1

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=encrypted.update_id,
            payload_ciphertext=(encrypted.payload_ciphertext),
            payload_nonce=bytes(tampered_nonce),
            payload_key_id=encrypted.payload_key_id,
            payload_version=encrypted.payload_version,
            keyring=keyring,
        )


def test_wrong_update_id_breaks_authenticated_data():
    keyring = make_keyring()

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=keyring,
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=UPDATE_ID + 1,
            payload_ciphertext=(encrypted.payload_ciphertext),
            payload_nonce=encrypted.payload_nonce,
            payload_key_id=encrypted.payload_key_id,
            payload_version=encrypted.payload_version,
            keyring=keyring,
        )


def test_unknown_key_id_is_rejected():
    keyring = make_keyring()

    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=keyring,
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=encrypted.update_id,
            payload_ciphertext=(encrypted.payload_ciphertext),
            payload_nonce=encrypted.payload_nonce,
            payload_key_id=KEY_ID_V2,
            payload_version=encrypted.payload_version,
            keyring=keyring,
        )


def test_unsupported_payload_version_is_rejected():
    encrypted = service.encrypt_authenticated_telegram_update(
        make_update(),
        keyring=make_keyring(),
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=encrypted.update_id,
            payload_ciphertext=(encrypted.payload_ciphertext),
            payload_nonce=encrypted.payload_nonce,
            payload_key_id=encrypted.payload_key_id,
            payload_version=2,
            keyring=make_keyring(),
        )


def test_decrypted_payload_must_be_object():
    nonce = b"n" * 12

    ciphertext = AESGCM(KEY_V1).encrypt(
        nonce,
        b"[]",
        make_aad(update_id=UPDATE_ID),
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=UPDATE_ID,
            payload_ciphertext=ciphertext,
            payload_nonce=nonce,
            payload_key_id=KEY_ID_V1,
            payload_version=1,
            keyring=make_keyring(),
        )


def test_decrypted_internal_update_id_must_match():
    nonce = b"n" * 12

    plaintext = json.dumps(
        {
            "update_id": UPDATE_ID + 1,
        },
        separators=(",", ":"),
    ).encode("utf-8")

    ciphertext = AESGCM(KEY_V1).encrypt(
        nonce,
        plaintext,
        make_aad(update_id=UPDATE_ID),
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=UPDATE_ID,
            payload_ciphertext=ciphertext,
            payload_nonce=nonce,
            payload_key_id=KEY_ID_V1,
            payload_version=1,
            keyring=make_keyring(),
        )


def test_invalid_utf8_payload_is_rejected():
    nonce = b"n" * 12

    ciphertext = AESGCM(KEY_V1).encrypt(
        nonce,
        b"\xff\xfe",
        make_aad(update_id=UPDATE_ID),
    )

    with pytest.raises(service.TelegramUpdateJobDecryptionError):
        service.decrypt_authenticated_telegram_update(
            update_id=UPDATE_ID,
            payload_ciphertext=ciphertext,
            payload_nonce=nonce,
            payload_key_id=KEY_ID_V1,
            payload_version=1,
            keyring=make_keyring(),
        )


def test_lock_token_has_secure_format():
    token = service.generate_telegram_update_job_lock_token()

    assert len(token) == 64

    assert re.fullmatch(
        r"[0-9a-f]{64}",
        token,
    )


def test_lock_tokens_are_unique():
    tokens = {service.generate_telegram_update_job_lock_token() for _ in range(100)}

    assert len(tokens) == 100


@pytest.mark.parametrize(
    (
        "attempt_count",
        "expected_delay",
    ),
    [
        (1, 5),
        (2, 10),
        (3, 20),
        (4, 40),
        (5, 80),
    ],
)
def test_retry_delay_uses_exponential_backoff(
    attempt_count,
    expected_delay,
):
    result = service.calculate_telegram_update_retry_delay(attempt_count=attempt_count)

    assert result == expected_delay


def test_retry_delay_is_capped():
    result = service.calculate_telegram_update_retry_delay(attempt_count=20)

    assert result == service.DEFAULT_RETRY_MAX_SECONDS


def test_retry_delay_supports_custom_values():
    result = service.calculate_telegram_update_retry_delay(
        attempt_count=4,
        base_seconds=3,
        max_seconds=100,
    )

    assert result == 24


@pytest.mark.parametrize(
    "value",
    [
        0,
        21,
        True,
        "1",
    ],
    ids=[
        "zero",
        "too-high",
        "boolean",
        "string",
    ],
)
def test_invalid_attempt_count_is_rejected(
    value,
):
    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.calculate_telegram_update_retry_delay(attempt_count=value)


@pytest.mark.parametrize(
    "value",
    [
        0,
        True,
        "5",
    ],
    ids=[
        "zero",
        "boolean",
        "string",
    ],
)
def test_invalid_base_seconds_is_rejected(
    value,
):
    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.calculate_telegram_update_retry_delay(
            attempt_count=1,
            base_seconds=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        True,
        "60",
    ],
    ids=[
        "zero",
        "boolean",
        "string",
    ],
)
def test_invalid_max_seconds_is_rejected(
    value,
):
    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.calculate_telegram_update_retry_delay(
            attempt_count=1,
            max_seconds=value,
        )


def test_base_seconds_cannot_exceed_maximum():
    with pytest.raises(service.TelegramUpdateJobValidationError):
        service.calculate_telegram_update_retry_delay(
            attempt_count=1,
            base_seconds=100,
            max_seconds=10,
        )
