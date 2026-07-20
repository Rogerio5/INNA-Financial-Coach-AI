from __future__ import annotations

import pytest

from api import telegram_webhook


def test_claimed_processor_requires_bridge_argument():
    lease = object()

    with pytest.raises(
        TypeError,
    ):
        telegram_webhook.process_claimed_telegram_update(
            {
                "update_id": 501,
            },
            lease,
        )


def test_claimed_processor_forwards_bridge_to_public_processor(
    monkeypatch,
):
    calls = []
    bridge = object()
    lease = object()

    def fake_processor(
        update,
        *,
        conversation_bridge,
    ):
        calls.append(
            {
                "update": update,
                "bridge": conversation_bridge,
            }
        )

        return True

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_processor,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        lambda received_lease: None,
    )

    update = {
        "update_id": 502,
    }

    telegram_webhook.process_claimed_telegram_update(
        update,
        lease,
        conversation_bridge=bridge,
    )

    assert calls == [
        {
            "update": update,
            "bridge": bridge,
        }
    ]


def test_claimed_processor_fails_claim_when_processor_returns_false(
    monkeypatch,
):
    bridge = object()
    lease = object()
    failures = []
    completions = []

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        lambda update, *, conversation_bridge: False,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "_fail_claimed_telegram_update_safely",
        lambda received_lease: failures.append(
            received_lease
        ),
    )

    monkeypatch.setattr(
        telegram_webhook,
        "complete_authenticated_telegram_update",
        lambda received_lease: completions.append(
            received_lease
        ),
    )

    telegram_webhook.process_claimed_telegram_update(
        {
            "update_id": 503,
        },
        lease,
        conversation_bridge=bridge,
    )

    assert failures == [lease]
    assert completions == []


def test_claimed_processor_fails_claim_when_processor_raises(
    monkeypatch,
):
    bridge = object()
    lease = object()
    failures = []

    def raise_processing_error(
        update,
        *,
        conversation_bridge,
    ):
        raise RuntimeError(
            "processing failure"
        )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        raise_processing_error,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "_fail_claimed_telegram_update_safely",
        lambda received_lease: failures.append(
            received_lease
        ),
    )

    telegram_webhook.process_claimed_telegram_update(
        {
            "update_id": 504,
        },
        lease,
        conversation_bridge=bridge,
    )

    assert failures == [lease]
