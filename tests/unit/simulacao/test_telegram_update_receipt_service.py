from __future__ import annotations

import math
from unittest.mock import MagicMock

import pytest

from src.services.telegram_update_receipts import (
    repository,
    service,
)


CLAIM_TOKEN = "c" * 64
FINGERPRINT = "a" * 64


def _update() -> dict:
    return {
        "update_id": 1001,
        "message": {
            "message_id": 77,
            "chat": {
                "id": 123456,
            },
            "text": "Olá, INNA",
        },
    }


def test_canonical_serialization_is_stable():
    first = {
        "update_id": 1001,
        "message": {
            "text": "Olá",
            "message_id": 77,
        },
    }

    second = {
        "message": {
            "message_id": 77,
            "text": "Olá",
        },
        "update_id": 1001,
    }

    assert (
        service.serialize_telegram_update_canonical(
            first
        )
        ==
        service.serialize_telegram_update_canonical(
            second
        )
    )


def test_fingerprint_is_stable_and_sha256():
    first = service.fingerprint_telegram_update(
        _update()
    )

    second = service.fingerprint_telegram_update(
        dict(
            reversed(
                list(
                    _update().items()
                )
            )
        )
    )

    assert first == second
    assert len(first) == 64

    assert all(
        character in "0123456789abcdef"
        for character in first
    )


def test_unicode_is_serialized_as_utf8():
    serialized = (
        service.serialize_telegram_update_canonical(
            _update()
        )
    )

    assert "Olá".encode(
        "utf-8"
    ) in serialized


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        "update",
        1001,
    ],
)
def test_non_mapping_update_is_rejected(
    value,
):
    with pytest.raises(
        service.TelegramUpdateReceiptValidationError
    ):
        service.serialize_telegram_update_canonical(
            value
        )


def test_nan_is_rejected():
    update = _update()

    update["value"] = math.nan

    with pytest.raises(
        service.TelegramUpdateReceiptValidationError
    ):
        service.serialize_telegram_update_canonical(
            update
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        -1,
        "1001",
    ],
)
def test_invalid_update_id_is_rejected(
    value,
):
    update = _update()

    update["update_id"] = value

    with pytest.raises(
        service.TelegramUpdateReceiptValidationError
    ):
        service.claim_authenticated_telegram_update(
            update
        )


def test_claim_generates_token_and_fingerprint(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        service.secrets,
        "token_hex",
        lambda size: (
            CLAIM_TOKEN
            if size == 32
            else ""
        ),
    )

    def fake_claim(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return (
            repository
            .TelegramUpdateClaimResult(
                update_id=1001,
                status="claimed",
                attempt_count=1,
                claim_token=(
                    CLAIM_TOKEN
                ),
            )
        )

    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        fake_claim,
    )

    decision = (
        service.claim_authenticated_telegram_update(
            _update(),
            lease_seconds=120,
        )
    )

    assert decision.status == "claimed"
    assert decision.should_process is True

    assert captured[
        "claim_token"
    ] == CLAIM_TOKEN

    assert captured[
        "update_fingerprint"
    ] == (
        service.fingerprint_telegram_update(
            _update()
        )
    )

    assert captured[
        "lease_seconds"
    ] == 120

    assert decision.lease is not None

    assert decision.lease.claim_token == (
        CLAIM_TOKEN
    )


@pytest.mark.parametrize(
    "status",
    [
        "duplicate",
        "in_progress",
    ],
)
def test_non_process_decision_has_no_lease(
    monkeypatch,
    status,
):
    monkeypatch.setattr(
        service.secrets,
        "token_hex",
        lambda _size: CLAIM_TOKEN,
    )

    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        MagicMock(
            return_value=(
                repository
                .TelegramUpdateClaimResult(
                    update_id=1001,
                    status=status,
                    attempt_count=2,
                    claim_token=None,
                )
            )
        ),
    )

    decision = (
        service.claim_authenticated_telegram_update(
            _update()
        )
    )

    assert decision.status == status
    assert decision.should_process is False
    assert decision.lease is None


def test_reclaimed_decision_has_new_lease(
    monkeypatch,
):
    monkeypatch.setattr(
        service.secrets,
        "token_hex",
        lambda _size: CLAIM_TOKEN,
    )

    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        MagicMock(
            return_value=(
                repository
                .TelegramUpdateClaimResult(
                    update_id=1001,
                    status="reclaimed",
                    attempt_count=3,
                    claim_token=(
                        CLAIM_TOKEN
                    ),
                )
            )
        ),
    )

    decision = (
        service.claim_authenticated_telegram_update(
            _update()
        )
    )

    assert decision.status == "reclaimed"
    assert decision.should_process is True
    assert decision.lease is not None
    assert decision.lease.attempt_count == 3


def test_repository_cannot_replace_generated_token(
    monkeypatch,
):
    monkeypatch.setattr(
        service.secrets,
        "token_hex",
        lambda _size: CLAIM_TOKEN,
    )

    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        MagicMock(
            return_value=(
                repository
                .TelegramUpdateClaimResult(
                    update_id=1001,
                    status="claimed",
                    attempt_count=1,
                    claim_token="d" * 64,
                )
            )
        ),
    )

    with pytest.raises(
        service.TelegramUpdateReceiptServiceError
    ):
        service.claim_authenticated_telegram_update(
            _update()
        )


def test_fingerprint_conflict_is_mapped(
    monkeypatch,
):
    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        MagicMock(
            side_effect=(
                repository
                .TelegramUpdateFingerprintConflictError(
                    "sensitive conflict"
                )
            )
        ),
    )

    with pytest.raises(
        service.TelegramUpdateReceiptConflictError
    ) as captured:
        service.claim_authenticated_telegram_update(
            _update()
        )

    assert (
        "sensitive conflict"
        not in str(
            captured.value
        )
    )


def test_repository_failure_is_sanitized(
    monkeypatch,
):
    secret_error = (
        "postgresql://user:"
        "super-secret@database/inna"
    )

    monkeypatch.setattr(
        service.repository,
        "claim_telegram_update",
        MagicMock(
            side_effect=(
                repository
                .TelegramUpdateReceiptRepositoryError(
                    secret_error
                )
            )
        ),
    )

    with pytest.raises(
        service.TelegramUpdateReceiptUnavailableError
    ) as captured:
        service.claim_authenticated_telegram_update(
            _update()
        )

    message = str(
        captured.value
    )

    assert "super-secret" not in message
    assert "postgresql://" not in message


def _lease():
    return (
        service.TelegramUpdateProcessingLease(
            update_id=1001,
            attempt_count=2,
            claim_token=CLAIM_TOKEN,
            update_fingerprint=(
                FINGERPRINT
            ),
        )
    )


def test_complete_uses_opaque_lease(
    monkeypatch,
):
    captured = {}

    def fake_complete(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return (
            repository
            .TelegramUpdateLifecycleResult(
                update_id=1001,
                status="completed",
                attempt_count=2,
            )
        )

    monkeypatch.setattr(
        service.repository,
        "complete_telegram_update",
        fake_complete,
    )

    outcome = (
        service.complete_authenticated_telegram_update(
            _lease()
        )
    )

    assert outcome.status == "completed"

    assert captured == {
        "update_id": 1001,
        "claim_token": CLAIM_TOKEN,
    }


def test_fail_uses_allowed_sanitized_code(
    monkeypatch,
):
    captured = {}

    def fake_fail(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return (
            repository
            .TelegramUpdateLifecycleResult(
                update_id=1001,
                status="failed",
                attempt_count=2,
            )
        )

    monkeypatch.setattr(
        service.repository,
        "fail_telegram_update",
        fake_fail,
    )

    outcome = (
        service.fail_authenticated_telegram_update(
            _lease(),
            error_code=(
                "telegram.processing_failed"
            ),
        )
    )

    assert outcome.status == "failed"

    assert captured[
        "error_code"
    ] == "telegram.processing_failed"


@pytest.mark.parametrize(
    "error_code",
    [
        "",
        "database password leaked",
        "UPPERCASE",
        "telegram.unknown",
    ],
)
def test_unapproved_failure_code_is_rejected(
    error_code,
):
    with pytest.raises(
        service.TelegramUpdateReceiptValidationError
    ):
        service.fail_authenticated_telegram_update(
            _lease(),
            error_code=error_code,
        )


def test_ownership_error_is_mapped(
    monkeypatch,
):
    monkeypatch.setattr(
        service.repository,
        "complete_telegram_update",
        MagicMock(
            side_effect=(
                repository
                .TelegramUpdateClaimOwnershipError(
                    "old token details"
                )
            )
        ),
    )

    with pytest.raises(
        service.TelegramUpdateReceiptOwnershipError
    ) as captured:
        service.complete_authenticated_telegram_update(
            _lease()
        )

    assert (
        "old token details"
        not in str(
            captured.value
        )
    )


def test_safe_representations_exclude_secrets():
    lease = _lease()

    decision = (
        service.TelegramUpdateClaimDecision(
            update_id=1001,
            status="claimed",
            attempt_count=2,
            lease=lease,
        )
    )

    assert CLAIM_TOKEN not in repr(
        lease
    )

    assert FINGERPRINT not in repr(
        lease
    )

    assert CLAIM_TOKEN not in str(
        decision.to_safe_dict()
    )

    assert FINGERPRINT not in str(
        decision.to_safe_dict()
    )

    assert "claim_token" not in (
        lease.to_safe_dict()
    )

    assert "update_fingerprint" not in (
        lease.to_safe_dict()
    )
