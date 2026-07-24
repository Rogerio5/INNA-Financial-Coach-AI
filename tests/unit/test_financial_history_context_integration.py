from __future__ import annotations

from src.context_engineering.context_builder import (
    build_agent_context,
)


def test_previous_financial_message_enters_selected_history():
    context = build_agent_context(
        current_message=(
            "Com base no que informei antes, "
            "qual era meu saldo mensal?"
        ),
        conversation_history=[
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é 5000 reais "
                    "e meus gastos são 3200 reais."
                ),
            },
            {
                "role": "assistant",
                "content": (
                    "Posso ajudar com seu "
                    "diagnóstico financeiro."
                ),
            },
        ],
    )

    contents = [
        message.content
        for message in context.selected_history
    ]

    assert any(
        "5000" in content
        and "3200" in content
        for content in contents
    )
