from __future__ import annotations

import inspect

import pytest

from src.channels import telegram_update_worker


def test_worker_composes_single_bridge_and_reuses_it(
    monkeypatch,
):
    from api import telegram_webhook
    from src.services import telegram_conversation_state

    created_bridges = []
    processor_calls = []

    fake_bridge = object()

    def fake_bridge_factory():
        created_bridges.append(fake_bridge)
        return fake_bridge

    def fake_process(
        update,
        *,
        conversation_bridge=None,
    ):
        processor_calls.append(
            (
                update,
                conversation_bridge,
            )
        )
        return "processed"

    monkeypatch.setattr(
        telegram_conversation_state,
        "create_postgres_telegram_webhook_conversation_bridge",
        fake_bridge_factory,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_process,
    )

    processor = (
        telegram_update_worker
        .load_telegram_processor()
    )

    assert callable(processor)
    assert created_bridges == [fake_bridge]

    first_update = {
        "update_id": 101,
    }

    second_update = {
        "update_id": 102,
    }

    assert processor(first_update) == "processed"
    assert processor(second_update) == "processed"

    assert created_bridges == [fake_bridge]

    assert processor_calls == [
        (
            first_update,
            fake_bridge,
        ),
        (
            second_update,
            fake_bridge,
        ),
    ]


def test_worker_does_not_create_bridge_per_update(
    monkeypatch,
):
    from api import telegram_webhook
    from src.services import telegram_conversation_state

    factory_calls = []

    def fake_bridge_factory():
        factory_calls.append(object())
        return object()

    def fake_process(
        update,
        *,
        conversation_bridge=None,
    ):
        assert conversation_bridge is not None
        return None

    monkeypatch.setattr(
        telegram_conversation_state,
        "create_postgres_telegram_webhook_conversation_bridge",
        fake_bridge_factory,
    )

    monkeypatch.setattr(
        telegram_webhook,
        "process_telegram_update",
        fake_process,
    )

    processor = (
        telegram_update_worker
        .load_telegram_processor()
    )

    processor({"update_id": 1})
    processor({"update_id": 2})
    processor({"update_id": 3})

    assert len(factory_calls) == 1


def test_worker_rejects_invalid_bridge_factory(
    monkeypatch,
):
    from src.services import telegram_conversation_state

    monkeypatch.setattr(
        telegram_conversation_state,
        "create_postgres_telegram_webhook_conversation_bridge",
        None,
    )

    with pytest.raises(
        telegram_update_worker
        .TelegramUpdateRunnerConfigurationError
    ):
        telegram_update_worker.load_telegram_processor()


def test_worker_wraps_bridge_composition_failure(
    monkeypatch,
):
    from src.services import telegram_conversation_state

    def failing_factory():
        raise RuntimeError(
            "database details must not escape"
        )

    monkeypatch.setattr(
        telegram_conversation_state,
        "create_postgres_telegram_webhook_conversation_bridge",
        failing_factory,
    )

    with pytest.raises(
        telegram_update_worker
        .TelegramUpdateRunnerConfigurationError,
        match=(
            "Não foi possível compor "
            "o estado conversacional durável"
        ),
    ) as captured:
        telegram_update_worker.load_telegram_processor()

    assert captured.value.__cause__ is None
    assert (
        "database details"
        not in str(captured.value)
    )


def test_worker_rejects_none_bridge(
    monkeypatch,
):
    from src.services import telegram_conversation_state

    monkeypatch.setattr(
        telegram_conversation_state,
        "create_postgres_telegram_webhook_conversation_bridge",
        lambda: None,
    )

    with pytest.raises(
        telegram_update_worker
        .TelegramUpdateRunnerConfigurationError,
        match="conversation bridge criada é inválida",
    ):
        telegram_update_worker.load_telegram_processor()


def test_worker_composition_source_has_no_direct_runtime_creation():
    source = inspect.getsource(
        telegram_update_worker
        .load_telegram_processor
    )

    assert (
        "create_postgres_telegram_webhook_conversation_bridge"
        in source
    )

    assert (
        "create_postgres_telegram_conversation_state_runtime("
        not in source
    )

    assert (
        "conversation_bridge=conversation_bridge"
        in source
    )
