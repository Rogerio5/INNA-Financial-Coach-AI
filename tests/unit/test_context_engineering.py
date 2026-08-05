from __future__ import annotations

from src.context_engineering.context_builder import (
    build_agent_context,
    render_context_for_llm,
)
from src.context_engineering.history_selector import (
    select_relevant_history,
)
from src.context_engineering.privacy_filter import (
    sanitize_sensitive_text,
)
from src.context_engineering.token_budget import (
    create_context_budget,
    estimate_tokens,
    truncate_text_to_token_budget,
)
from src.context_engineering.tool_selector import (
    extract_unique_sources,
    select_tool_results,
)


def test_privacy_filter_masks_email_and_cpf():
    sanitized, report = sanitize_sensitive_text(
        ("Meu e-mail é teste@email.com e meu CPF é 123.456.789-00.")
    )

    assert "teste@email.com" not in sanitized
    assert "123.456.789-00" not in sanitized

    assert report.email_addresses_masked == 1
    assert report.cpf_numbers_masked == 1


def test_estimate_tokens_returns_positive_value():
    assert estimate_tokens("Reserva financeira") > 0


def test_context_budget_detects_overflow():
    budget = create_context_budget(
        max_tokens=1000,
        reserved_output_tokens=200,
        estimated_input_tokens=900,
    )

    assert budget.available_input_tokens == 800
    assert budget.within_budget is False


def test_truncate_text_respects_budget():
    text = "a" * 1000

    result = truncate_text_to_token_budget(
        text,
        max_tokens=40,
    )

    assert len(result) < len(text)
    assert "TRUNCADO" in result


def test_history_selector_avoids_current_message():
    history = [
        {
            "role": "user",
            "content": "Mensagem anterior",
        },
        {
            "role": "assistant",
            "content": "Resposta anterior",
        },
        {
            "role": "user",
            "content": "Mensagem atual",
        },
    ]

    selected, _ = select_relevant_history(
        history,
        current_message="Mensagem atual",
    )

    assert len(selected) == 2
    assert selected[-1].content == "Resposta anterior"


def test_history_selector_keeps_recent_messages():
    history = [
        {
            "role": "user",
            "content": f"Mensagem {index}",
        }
        for index in range(20)
    ]

    selected, _ = select_relevant_history(
        history,
        max_messages=5,
    )

    assert len(selected) == 5
    assert selected[0].content == "Mensagem 15"


def test_tool_selector_removes_unknown_fields():
    selected = select_tool_results(
        [
            {
                "tool": "rag",
                "ok": True,
                "sources": ["Fonte A"],
                "internal_secret": "não incluir",
            }
        ]
    )

    assert len(selected) == 1
    assert "internal_secret" not in selected[0]


def test_extract_unique_sources():
    sources = extract_unique_sources(
        [
            {
                "sources": [
                    "Fonte A",
                    "Fonte B",
                ]
            },
            {
                "sources": [
                    "Fonte A",
                    "Fonte C",
                ]
            },
        ]
    )

    assert sources == [
        "Fonte A",
        "Fonte B",
        "Fonte C",
    ]


def test_build_agent_context_complete():
    context = build_agent_context(
        current_message=("Como criar uma reserva?"),
        conversation_history=[
            {
                "role": "user",
                "content": "Tenho renda de 3000",
            },
            {
                "role": "assistant",
                "content": "Entendi.",
            },
            {
                "role": "user",
                "content": ("Como criar uma reserva?"),
            },
        ],
        conversation_summary=("Usuário quer organizar o orçamento."),
        financial_profile={
            "monthly_income": 3000,
            "fixed_expenses": 2000,
            "password": "não incluir",
        },
        tool_results=[
            {
                "tool": "consultar_rag_inna",
                "ok": True,
                "sources": ["Faq Financeiro Inna"],
            }
        ],
        language="pt",
        currency="BRL",
    )

    assert context.current_message == "Como criar uma reserva?"

    assert len(context.selected_history) == 2

    assert context.financial_profile["monthly_income"] == 3000

    assert "password" not in context.financial_profile

    assert context.sources == ["Faq Financeiro Inna"]

    assert context.metrics.budget.estimated_input_tokens > 0


def test_render_context_for_llm():
    context = build_agent_context(
        current_message=("Como criar uma reserva?"),
        conversation_history=[],
    )

    rendered = render_context_for_llm(context)

    assert "## INSTRUÇÕES" in rendered
    assert "## SOLICITAÇÃO ATUAL" in rendered
    assert "Como criar uma reserva?" in rendered
