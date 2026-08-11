from __future__ import annotations

from types import SimpleNamespace

from fastapi import BackgroundTasks

import api.main as api_main


def _payload(*, idioma: str = "pt", top_k: int = 3) -> api_main.RagAskRequest:
    return api_main.RagAskRequest(
        pergunta="O que e reserva de emergencia?",
        idioma=idioma,
        top_k=top_k,
    )


def test_flag_off_preserves_legacy_answer_with_rag(monkeypatch) -> None:
    calls = []
    runtime = SimpleNamespace(
        llamaindex_agentic_rag_enabled=lambda: False,
    )

    def fake_legacy(**kwargs):
        calls.append(kwargs)
        return {"resposta": "legacy", "fontes": ["fonte"]}

    monkeypatch.setattr(
        api_main,
        "_load_llamaindex_agentic_rag_runtime",
        lambda: runtime,
    )
    monkeypatch.setattr(api_main, "answer_with_rag", fake_legacy)

    result = api_main._execute_rag_ask_runtime(_payload())

    assert result == {"resposta": "legacy", "fontes": ["fonte"]}
    assert calls == [{
        "pergunta": "O que e reserva de emergencia?",
        "idioma": "pt",
        "top_k": 3,
    }]


def test_flag_on_portuguese_uses_llamaindex_payload(monkeypatch) -> None:
    calls = []

    async def fake_workflow(
        pergunta: str,
        *,
        idioma: str = "pt",
        top_k: int = 2,
    ):
        calls.append({"pergunta": pergunta, "idioma": idioma, "top_k": top_k})
        return {
            "resposta": "llamaindex",
            "fontes": [{"documento": "doc"}],
            "modo": "rag_hibrido",
            "trace_id": "trace-1",
            "retrieval_trace": {"total_time_ms": 10},
            "llamaindex_agentic_rag": {
                "enabled": True,
                "executed": True,
                "fallback_used": False,
            },
        }

    runtime = SimpleNamespace(
        llamaindex_agentic_rag_enabled=lambda: True,
        executar_llamaindex_agent_workflow_payload=fake_workflow,
    )

    monkeypatch.setattr(
        api_main,
        "_load_llamaindex_agentic_rag_runtime",
        lambda: runtime,
    )
    monkeypatch.setattr(
        api_main,
        "answer_with_rag",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy path should not run")
        ),
    )

    result = api_main._execute_rag_ask_runtime(_payload())

    assert result["resposta"] == "llamaindex"
    assert result["fontes"] == [{"documento": "doc"}]
    assert result["trace_id"] == "trace-1"
    assert calls == [{"pergunta": "O que e reserva de emergencia?", "idioma": "pt", "top_k": 3}]


def test_non_portuguese_stays_legacy_during_canary(monkeypatch) -> None:
    workflow_calls = []

    async def fake_workflow(
        pergunta: str,
        *,
        idioma: str = "pt",
        top_k: int = 2,
    ):
        workflow_calls.append({"pergunta": pergunta, "idioma": idioma, "top_k": top_k})
        return {"resposta": "unexpected"}

    runtime = SimpleNamespace(
        llamaindex_agentic_rag_enabled=lambda: True,
        executar_llamaindex_agent_workflow_payload=fake_workflow,
    )

    monkeypatch.setattr(
        api_main,
        "_load_llamaindex_agentic_rag_runtime",
        lambda: runtime,
    )
    monkeypatch.setattr(
        api_main,
        "answer_with_rag",
        lambda **kwargs: {"resposta": "legacy-en", "fontes": []},
    )

    result = api_main._execute_rag_ask_runtime(_payload(idioma="en-US"))

    assert result["resposta"] == "legacy-en"
    assert workflow_calls == []


def test_llamaindex_failure_falls_back_without_error_detail(monkeypatch) -> None:
    async def failing_workflow(
        pergunta: str,
        *,
        idioma: str = "pt",
        top_k: int = 2,
    ):
        raise RuntimeError("internal-sensitive-message")

    runtime = SimpleNamespace(
        llamaindex_agentic_rag_enabled=lambda: True,
        executar_llamaindex_agent_workflow_payload=failing_workflow,
    )

    monkeypatch.setattr(
        api_main,
        "_load_llamaindex_agentic_rag_runtime",
        lambda: runtime,
    )
    monkeypatch.setattr(
        api_main,
        "answer_with_rag",
        lambda **kwargs: {"resposta": "fallback", "fontes": ["fonte"]},
    )

    result = api_main._execute_rag_ask_runtime(_payload())

    assert result["resposta"] == "fallback"
    assert result["llamaindex_agentic_rag"] == {
        "enabled": True,
        "executed": False,
        "fallback_used": True,
        "runtime": "agent_workflow",
        "error_type": "RuntimeError",
    }
    assert "internal-sensitive-message" not in str(result)


def test_rag_ask_routes_through_runtime_gateway(monkeypatch) -> None:
    calls = []

    def fake_gateway(payload):
        calls.append(payload.pergunta)
        return {
            "resposta": "gateway",
            "fontes": [],
            "modo": "test",
            "trace_id": "trace-test",
            "retrieval_trace": {},
        }

    monkeypatch.setattr(api_main, "_execute_rag_ask_runtime", fake_gateway)

    result = api_main.rag_ask(_payload(), BackgroundTasks())

    assert result["resposta"] == "gateway"
    assert calls == ["O que e reserva de emergencia?"]
    assert "api_latency" in result
