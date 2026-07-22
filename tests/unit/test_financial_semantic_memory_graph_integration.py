from src.agents.graph import (
    executar_nucleo_inna_persistente,
)


def test_same_thread_preserves_conversation_history():
    thread_id = (
        "week5-unit-memory-continuity"
    )

    first = executar_nucleo_inna_persistente(
        mensagem=(
            "Minha renda mensal é 5000 reais "
            "e meus gastos são 3200 reais."
        ),
        thread_id=thread_id,
    )

    second = executar_nucleo_inna_persistente(
        mensagem=(
            "Com base no que informei antes, "
            "qual era meu saldo mensal?"
        ),
        thread_id=thread_id,
    )

    assert first["thread_id"] == thread_id
    assert second["thread_id"] == thread_id

    assert len(
        second.get(
            "conversation_history",
            [],
        )
    ) > len(
        first.get(
            "conversation_history",
            [],
        )
    )


def test_follow_up_uses_previous_financial_information():
    thread_id = (
        "week5-semantic-memory-continuity"
    )

    executar_nucleo_inna_persistente(
        mensagem=(
            "Minha renda mensal é 5000 reais "
            "e meus gastos são 3200 reais."
        ),
        thread_id=thread_id,
    )

    result = executar_nucleo_inna_persistente(
        mensagem=(
            "Com base no que informei antes, "
            "qual era meu saldo mensal?"
        ),
        thread_id=thread_id,
    )

    response = str(
        result.get(
            "response",
            "",
        )
    ).lower()

    assert (
        "1800"
        in response
        or "1.800"
        in response
    )

    assert (
        result.get("current_agent")
        == "financial_agent"
    )

