from __future__ import annotations

import pytest

from api import telegram_webhook


def test_private_core_requires_bridge_argument():
    with pytest.raises(
        TypeError,
    ):
        telegram_webhook._process_telegram_update_core(
            {
                "update_id": 801,
            }
        )


def test_private_core_rejects_explicit_none_bridge():
    with pytest.raises(
        telegram_webhook
        .TelegramUpdateIngressConfigurationError,
        match="conversation_bridge é obrigatória",
    ):
        telegram_webhook._process_telegram_update_core(
            {
                "update_id": 802,
            },
            conversation_bridge=None,
        )


def test_legacy_processor_no_longer_exists():
    assert not hasattr(
        telegram_webhook,
        "_process_legacy_telegram_update",
    )
