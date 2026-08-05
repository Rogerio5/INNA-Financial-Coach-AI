from __future__ import annotations

from uuid import uuid4

from src.agents.graph import (
    executar_nucleo_inna_persistente,
)


def test_summary_is_created_and_persisted_by_thread():
    thread_id = "summary-integration-" + uuid4().hex

    first = executar_nucleo_inna_persistente(
        mensagem=(
            "Minha renda mensal é 5000 reais e meus gastos mensais são 3200 reais."
        ),
        thread_id=thread_id,
    )

    assert first["conversation_summary"]
    assert "R$ 5.000,00" in first["conversation_summary"]
    assert "R$ 3.200,00" in first["conversation_summary"]

    assert first["conversation_summary_updated"] is True

    assert first["conversation_summary_version"] >= 1

    second = executar_nucleo_inna_persistente(
        mensagem=("Minha renda mensal agora é 6500 reais."),
        thread_id=thread_id,
    )

    assert "R$ 6.500,00" in second["conversation_summary"]

    assert "R$ 5.000,00" not in second["conversation_summary"]

    assert "R$ 3.200,00" in second["conversation_summary"]

    assert (
        second["conversation_summary_version"] > first["conversation_summary_version"]
    )

    assert any(
        item.startswith("conversation_summary_node:") for item in second["trace"]
    )


def test_different_threads_do_not_share_summary():
    first_thread = "summary-isolation-a-" + uuid4().hex

    second_thread = "summary-isolation-b-" + uuid4().hex

    first = executar_nucleo_inna_persistente(
        mensagem=("Minha renda mensal é 9000 reais."),
        thread_id=first_thread,
    )

    second = executar_nucleo_inna_persistente(
        mensagem=("Minha renda mensal é 3000 reais."),
        thread_id=second_thread,
    )

    assert "R$ 9.000,00" in first["conversation_summary"]

    assert "R$ 3.000,00" in second["conversation_summary"]

    assert "R$ 9.000,00" not in second["conversation_summary"]
