from __future__ import annotations

from src.services.memory.conversation_summary import (
    build_conversation_summary,
    update_conversation_summary_state,
)


def test_builds_summary_from_user_financial_facts():
    summary = build_conversation_summary(
        conversation_history=[
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é 5000 reais "
                    "e meus gastos mensais são "
                    "3200 reais."
                ),
            }
        ]
    )

    assert "Renda mensal" in summary
    assert "R$ 5.000,00" in summary
    assert "Gastos mensais" in summary
    assert "R$ 3.200,00" in summary


def test_newer_user_fact_overwrites_old_summary():
    summary = build_conversation_summary(
        previous_summary=(
            "Resumo incremental da conversa:\n"
            "- Renda mensal: R$ 5.000,00"
        ),
        conversation_history=[
            {
                "role": "user",
                "content": (
                    "Minha renda mensal agora "
                    "é 7000 reais."
                ),
            }
        ],
    )

    assert "R$ 7.000,00" in summary
    assert "R$ 5.000,00" not in summary


def test_assistant_message_does_not_create_user_income():
    summary = build_conversation_summary(
        conversation_history=[
            {
                "role": "assistant",
                "content": (
                    "Sua renda é de R$ 999.999,00."
                ),
            }
        ]
    )

    assert "Renda mensal" not in summary


def test_preserves_old_fact_not_mentioned_again():
    summary = build_conversation_summary(
        previous_summary=(
            "Resumo incremental da conversa:\n"
            "- Renda mensal: R$ 5.000,00\n"
            "- Meta financeira: criar reserva"
        ),
        conversation_history=[
            {
                "role": "user",
                "content": (
                    "Minha renda mensal agora "
                    "é 6500 reais."
                ),
            }
        ],
    )

    assert "R$ 6.500,00" in summary
    assert "Meta financeira: criar reserva" in summary


def test_masks_sensitive_information():
    summary = build_conversation_summary(
        conversation_history=[
            {
                "role": "user",
                "content": (
                    "Meu objetivo é organizar "
                    "minhas finanças. Meu CPF "
                    "é 123.456.789-00."
                ),
            }
        ]
    )

    assert "123.456.789-00" not in summary


def test_summary_respects_token_limit():
    summary = build_conversation_summary(
        conversation_history=[
            {
                "role": "assistant",
                "content": (
                    "Diagnóstico financeiro "
                    + "detalhado " * 1000
                ),
            }
        ],
        max_summary_tokens=80,
    )

    assert len(summary) < 1000


def test_state_update_returns_langgraph_partial_state():
    result = update_conversation_summary_state({
        "conversation_summary": "",
        "conversation_history": [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é "
                    "5000 reais."
                ),
            }
        ],
        "trace": [],
    })

    assert result["conversation_summary"]
    assert (
        "conversation_summary:updated"
        in result["trace"]
    )


def test_state_update_is_idempotent():
    state = {
        "conversation_summary": "",
        "conversation_history": [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é "
                    "5000 reais."
                ),
            }
        ],
        "trace": [],
    }

    first = update_conversation_summary_state(
        state
    )

    second = (
        update_conversation_summary_state({
            **state,
            "conversation_summary": (
                first["conversation_summary"]
            ),
        })
    )

    assert (
        second["conversation_summary"]
        == first["conversation_summary"]
    )


def test_latest_assistant_action_is_not_duplicated():
    previous = (
        "Resumo incremental da conversa:\n"
        "- Renda mensal: R$ 5.000,00\n"
        "- Última ação da INNA: "
        "Diagnóstico financeiro solicitado."
    )

    summary = build_conversation_summary(
        previous_summary=previous,
        conversation_history=[
            {
                "role": "assistant",
                "content": (
                    "Seu saldo estimado foi "
                    "calculado com segurança."
                ),
            }
        ],
    )

    assert (
        summary.count(
            "- Última ação da INNA:"
        )
        == 1
    )

    assert (
        "saldo estimado"
        in summary.lower()
    )

