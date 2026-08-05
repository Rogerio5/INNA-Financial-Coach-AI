from __future__ import annotations

from typing import Any

import pytest

from src.evaluation.case_catalog import (
    build_core_dataset,
)
from src.evaluation.live_payload_provider import (
    EmptyLiveResponseError,
    InvalidLiveStateError,
    LiveInnaPayloadProvider,
)


def _rag_case():
    return build_core_dataset().get_case("rag-financial-education-001")


def _successful_state() -> dict[str, Any]:
    return {
        "response": (
            "Gastos fixos são recorrentes, "
            "gastos variáveis mudam conforme "
            "o consumo e a reserva ajuda na "
            "proteção financeira."
        ),
        "current_agent": "education_agent",
        "current_team": "knowledge_team",
        "intent": "educacao_financeira",
        "task_status": "completed",
        "task_completion_score": 1.0,
        "tool_results": [
            {
                "tool": ("buscar_conhecimento_rag"),
                "status": "success",
                "ok": True,
                "duration_ms": 12.5,
            }
        ],
        "structured_response": {
            "rag_execution": {
                "tool": ("buscar_conhecimento_rag"),
                "status": "success",
                "retrieved_documents": 2,
                "duration_ms": 18.5,
                "retrieval_context": [
                    ("Gastos fixos, gastos variáveis e reserva financeira.")
                ],
            }
        },
        "human_review_requested": False,
    }


def test_live_provider_builds_real_payload():
    calls: list[dict[str, Any]] = []

    def executor(**kwargs):
        calls.append(kwargs)
        return _successful_state()

    provider = LiveInnaPayloadProvider(
        graph_executor=executor,
    )

    case = _rag_case()
    payload = provider(case)

    assert calls == [
        {
            "mensagem": case.input_text,
            "usuario_id": ("inna-live-evaluation:rag-financial-education-001"),
            "idioma": case.language,
            "moeda": case.currency,
        }
    ]

    assert payload.case_id == case.case_id
    assert "gastos fixos" in payload.actual_output.lower()

    assert payload.retrieval_context == (
        ("Gastos fixos, gastos variáveis e reserva financeira."),
    )

    assert payload.metadata["actual_agent"] == "education_agent"
    assert payload.metadata["actual_team"] == "knowledge_team"
    assert payload.metadata["actual_intent"] == "educacao_financeira"
    assert payload.metadata["actual_task_status"] == "completed"
    assert payload.metadata["retrieved_documents"] == 2
    assert payload.metadata["latency_ms"] == pytest.approx(18.5)
    assert payload.metadata["production_execution"] is True
    assert payload.metadata["synthetic_provider"] is False

    called_tools = payload.metadata["called_tools"]

    assert len(called_tools) == 1
    assert called_tools[0]["name"] == "buscar_conhecimento_rag"
    assert called_tools[0]["status"] == "success"
    assert called_tools[0]["call_index"] == 0


def test_live_provider_accepts_custom_metadata():
    provider = LiveInnaPayloadProvider(
        graph_executor=(lambda **kwargs: _successful_state()),
        metadata={
            "environment": "test",
            "release": "candidate",
        },
    )

    payload = provider(_rag_case())

    assert payload.metadata["environment"] == "test"
    assert payload.metadata["release"] == "candidate"


def test_live_provider_rejects_empty_response():
    state = _successful_state()
    state["response"] = ""

    provider = LiveInnaPayloadProvider(
        graph_executor=(lambda **kwargs: state),
    )

    with pytest.raises(
        EmptyLiveResponseError,
        match="sem resposta avaliável",
    ):
        provider(_rag_case())


def test_live_provider_rejects_invalid_state():
    provider = LiveInnaPayloadProvider(
        graph_executor=(lambda **kwargs: "invalid"),
    )

    with pytest.raises(
        InvalidLiveStateError,
        match="Mapping",
    ):
        provider(_rag_case())


def test_live_provider_normalizes_invalid_rag_numbers():
    state = _successful_state()

    rag = state["structured_response"]["rag_execution"]

    rag["retrieved_documents"] = "invalid"

    rag["duration_ms"] = "invalid"

    provider = LiveInnaPayloadProvider(
        graph_executor=(lambda **kwargs: state),
    )

    payload = provider(_rag_case())

    assert payload.metadata["retrieved_documents"] == 0
    assert payload.metadata["latency_ms"] == 0.0


def test_live_provider_validates_configuration():
    with pytest.raises(
        ValueError,
        match="user_id_prefix",
    ):
        LiveInnaPayloadProvider(
            user_id_prefix=" ",
        )

    with pytest.raises(
        ValueError,
        match="estimated_cost",
    ):
        LiveInnaPayloadProvider(
            estimated_cost=-0.01,
        )
