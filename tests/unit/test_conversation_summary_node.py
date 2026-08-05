from __future__ import annotations

from src.agents.conversation_summary_node import (
    conversation_summary_node,
)


def test_node_creates_summary_and_version():
    result = conversation_summary_node(
        {
            "conversation_summary": "",
            "conversation_summary_version": 0,
            "conversation_history": [
                {
                    "role": "user",
                    "content": ("Minha renda mensal é 5000 reais."),
                }
            ],
            "trace": [],
        }
    )

    assert result["conversation_summary"]
    assert result["conversation_summary_updated"] is True
    assert result["conversation_summary_version"] == 1
    assert result["conversation_summary_source_messages"] == 1
    assert result["conversation_summary_source"] == "conversation_history"


def test_node_increments_existing_version():
    result = conversation_summary_node(
        {
            "conversation_summary": (
                "Resumo incremental da conversa:\n- Renda mensal: R$ 5.000,00"
            ),
            "conversation_summary_version": 3,
            "conversation_history": [
                {
                    "role": "user",
                    "content": ("Minha renda mensal agora é 6500 reais."),
                }
            ],
            "trace": [],
        }
    )

    assert "R$ 6.500,00" in result["conversation_summary"]

    assert result["conversation_summary_version"] == 4


def test_node_does_not_increment_unchanged_summary():
    summary = "Resumo incremental da conversa:\n- Renda mensal: R$ 5.000,00"

    result = conversation_summary_node(
        {
            "conversation_summary": summary,
            "conversation_summary_version": 2,
            "conversation_history": [
                {
                    "role": "user",
                    "content": ("Minha renda mensal é 5000 reais."),
                }
            ],
            "trace": [],
        }
    )

    assert result["conversation_summary"] == summary

    assert result["conversation_summary_updated"] is False

    assert result["conversation_summary_version"] == 2


def test_node_does_not_create_user_fact_from_assistant():
    result = conversation_summary_node(
        {
            "conversation_summary": "",
            "conversation_summary_version": 0,
            "conversation_history": [
                {
                    "role": "assistant",
                    "content": ("Sua renda mensal é R$ 999.999,00."),
                }
            ],
            "trace": [],
        }
    )

    assert "Renda mensal" not in result["conversation_summary"]


def test_node_records_auditable_trace():
    result = conversation_summary_node(
        {
            "conversation_summary": "",
            "conversation_summary_version": 0,
            "conversation_history": [
                {
                    "role": "user",
                    "content": ("Minha renda mensal é 5000 reais."),
                }
            ],
            "trace": [
                "context_builder:1_messages",
            ],
        }
    )

    assert any(
        item.startswith("conversation_summary_node:") for item in result["trace"]
    )
