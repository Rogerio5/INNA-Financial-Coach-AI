from __future__ import annotations

from dataclasses import replace

import pytest

from src.services.telegram_update_jobs import (
    execution,
)

from src.services.telegram_update_jobs import (
    service as crypto_service,
)

from src.services.telegram_update_jobs import (
    worker,
)


UPDATE_ID = 91001
LOCK_TOKEN = "a" * 64

KEY_ID_V1 = "inna.telegram.v1"
KEY_ID_V2 = "inna.telegram.v2"

KEY_V1 = b"a" * 32
KEY_V2 = b"b" * 32


UPDATE = {
    "update_id": UPDATE_ID,
    "message": {
        "message_id": 77,
        "chat": {
            "id": 555,
        },
        "text": ("Quero organizar meu orçamento."),
        "entities": [
            {
                "type": "bold",
                "offset": 0,
                "length": 5,
            },
        ],
    },
}


def make_keyring(
    *,
    active_key_id=KEY_ID_V1,
    include_v1=True,
    include_v2=False,
):
    keys = {}

    if include_v1:
        keys[KEY_ID_V1] = KEY_V1

    if include_v2:
        keys[KEY_ID_V2] = KEY_V2

    return crypto_service.TelegramUpdateEncryptionKeyring(
        active_key_id=active_key_id,
        keys=keys,
    )


def make_lease(
    *,
    update=UPDATE,
    keyring=None,
):
    resolved_keyring = keyring if keyring is not None else make_keyring()

    encrypted = crypto_service.encrypt_authenticated_telegram_update(
        update,
        keyring=resolved_keyring,
    )

    return worker.TelegramUpdateWorkerLease(
        update_id=encrypted.update_id,
        job_status="processing",
        receipt_status="processing",
        job_attempt_count=1,
        job_max_attempts=5,
        receipt_attempt_count=1,
        payload_version=(encrypted.payload_version),
        payload_key_id=(encrypted.payload_key_id),
        payload_ciphertext=(encrypted.payload_ciphertext),
        payload_nonce=(encrypted.payload_nonce),
        lock_token=LOCK_TOKEN,
    )


def decrypt(
    *,
    lease=None,
    keyring=None,
):
    return execution.decrypt_authenticated_telegram_worker_lease(
        lease=(lease if lease is not None else make_lease()),
        keyring=(keyring if keyring is not None else make_keyring()),
    )


def test_decrypts_authenticated_worker_lease():
    payload = decrypt()

    restored = payload.to_processing_dict()

    assert restored == UPDATE
    assert payload.update_id == UPDATE_ID
    assert payload.job_attempt_count == 1
    assert payload.job_max_attempts == 5


def test_safe_output_contains_only_metadata():
    payload = decrypt()

    safe = payload.to_safe_dict()

    assert safe["update_id"] == UPDATE_ID
    assert safe["decrypted"] is True

    assert "message" not in safe
    assert "payload" not in safe
    assert "lock_token" not in safe
    assert "payload_ciphertext" not in safe
    assert "payload_nonce" not in safe


def test_repr_hides_decrypted_content():
    payload = decrypt()

    representation = repr(payload)

    assert "Quero organizar meu orçamento" not in representation

    assert LOCK_TOKEN not in representation
    assert "payload_ciphertext" not in representation
    assert "payload_nonce" not in representation


def test_processing_copy_is_independent():
    payload = decrypt()

    first = payload.to_processing_dict()
    second = payload.to_processing_dict()

    first["message"]["text"] = "alterado"
    first["message"]["entities"].append(
        {
            "type": "italic",
        }
    )

    assert second["message"]["text"] == UPDATE["message"]["text"]

    assert len(second["message"]["entities"]) == 1


def test_internal_payload_is_immutable():
    payload = decrypt()

    with pytest.raises(TypeError):
        payload._payload["update_id"] = 10

    with pytest.raises(TypeError):
        payload._payload["message"]["text"] = "alterado"


def test_nested_lists_are_restored_as_lists():
    payload = decrypt()

    restored = payload.to_processing_dict()

    assert isinstance(
        restored["message"]["entities"],
        list,
    )


def test_rotated_keyring_decrypts_old_payload():
    old_keyring = make_keyring(
        active_key_id=KEY_ID_V1,
        include_v1=True,
    )

    lease = make_lease(
        keyring=old_keyring,
    )

    rotated_keyring = make_keyring(
        active_key_id=KEY_ID_V2,
        include_v1=True,
        include_v2=True,
    )

    payload = decrypt(
        lease=lease,
        keyring=rotated_keyring,
    )

    assert payload.to_processing_dict() == UPDATE


def test_tampered_ciphertext_is_rejected():
    lease = make_lease()

    tampered = bytearray(lease.payload_ciphertext)

    tampered[-1] ^= 1

    invalid_lease = replace(
        lease,
        payload_ciphertext=bytes(tampered),
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError):
        decrypt(lease=invalid_lease)


def test_tampered_nonce_is_rejected():
    lease = make_lease()

    tampered = bytearray(lease.payload_nonce)

    tampered[0] ^= 1

    invalid_lease = replace(
        lease,
        payload_nonce=bytes(tampered),
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError):
        decrypt(lease=invalid_lease)


def test_wrong_update_id_is_rejected():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        update_id=UPDATE_ID + 1,
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError):
        decrypt(lease=invalid_lease)


def test_unknown_key_is_rejected():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        payload_key_id=KEY_ID_V2,
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError):
        decrypt(lease=invalid_lease)


def test_unsupported_version_is_rejected():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        payload_version=2,
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError):
        decrypt(lease=invalid_lease)


def test_missing_environment_keyring_is_sanitized(
    monkeypatch,
):
    lease = make_lease()

    monkeypatch.delenv(
        crypto_service.KEYS_ENV_NAME,
        raising=False,
    )

    monkeypatch.delenv(
        crypto_service.ACTIVE_KEY_ENV_NAME,
        raising=False,
    )

    with pytest.raises(execution.TelegramUpdateExecutionConfigurationError) as captured:
        (execution.decrypt_authenticated_telegram_worker_lease(lease))

    assert crypto_service.KEYS_ENV_NAME not in str(captured.value)


def test_wrong_lease_type_is_rejected():
    with pytest.raises(execution.TelegramUpdateExecutionValidationError):
        (
            execution.decrypt_authenticated_telegram_worker_lease(
                {
                    "update_id": UPDATE_ID,
                },
                keyring=make_keyring(),
            )
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    [
        ("job_status", "queued"),
        ("receipt_status", "failed"),
        ("job_attempt_count", 0),
        ("job_max_attempts", 0),
        ("receipt_attempt_count", 0),
        ("payload_version", 0),
        ("payload_key_id", "invalid key"),
        ("lock_token", "short"),
    ],
    ids=[
        "job-status",
        "receipt-status",
        "job-attempt",
        "job-max-attempts",
        "receipt-attempt",
        "payload-version",
        "key-id",
        "lock-token",
    ],
)
def test_invalid_lease_metadata_is_rejected(
    field_name,
    invalid_value,
):
    lease = make_lease()

    invalid_lease = replace(
        lease,
        **{
            field_name: invalid_value,
        },
    )

    with pytest.raises(execution.TelegramUpdateExecutionValidationError):
        decrypt(lease=invalid_lease)


def test_receipt_attempts_cannot_trail_job():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        job_attempt_count=3,
        receipt_attempt_count=2,
    )

    with pytest.raises(execution.TelegramUpdateExecutionValidationError):
        decrypt(lease=invalid_lease)


def test_invalid_ciphertext_size_is_rejected():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        payload_ciphertext=b"x",
    )

    with pytest.raises(execution.TelegramUpdateExecutionValidationError):
        decrypt(lease=invalid_lease)


def test_invalid_nonce_size_is_rejected():
    lease = make_lease()

    invalid_lease = replace(
        lease,
        payload_nonce=b"short",
    )

    with pytest.raises(execution.TelegramUpdateExecutionValidationError):
        decrypt(lease=invalid_lease)


def test_payload_depth_limit_is_enforced():
    nested = {
        "value": "fim",
    }

    for _ in range(execution.MAX_JSON_DEPTH + 2):
        nested = {
            "next": nested,
        }

    deep_update = {
        "update_id": UPDATE_ID,
        "payload": nested,
    }

    lease = make_lease(
        update=deep_update,
    )

    with pytest.raises(execution.TelegramUpdateExecutionPayloadError):
        decrypt(lease=lease)


def test_decryption_error_does_not_expose_payload():
    lease = make_lease()

    tampered = bytearray(lease.payload_ciphertext)

    tampered[-1] ^= 1

    invalid_lease = replace(
        lease,
        payload_ciphertext=bytes(tampered),
    )

    with pytest.raises(execution.TelegramUpdateExecutionDecryptionError) as captured:
        decrypt(lease=invalid_lease)

    message = str(captured.value)

    assert "Quero organizar meu orçamento" not in message

    assert LOCK_TOKEN not in message
    assert repr(invalid_lease.payload_ciphertext) not in message


def test_payload_metadata_preserves_key_version():
    payload = decrypt()

    assert payload.payload_version == 1
    assert payload.payload_key_id == KEY_ID_V1
