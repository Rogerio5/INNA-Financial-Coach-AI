
from __future__ import annotations

import inspect
from contextlib import contextmanager
from types import SimpleNamespace

import src.rag_engine as rag_engine
import src.services.llm.gemini as gemini_service


def test_rag_delegates_to_resilient_gemini_service(
    monkeypatch,
):
    captured = {}
    usage = {}

    def fake_generate(
        prompt,
        *,
        modelo=None,
        role=None,
        temperatura=0.3,
        max_tokens=2048,
        usage_out=None,
    ):
        captured["prompt"] = prompt
        captured["modelo"] = modelo
        captured["role"] = role
        captured["temperatura"] = temperatura
        captured["max_tokens"] = max_tokens

        usage_out.update(
            {
                "tokens_entrada": 11,
                "tokens_saida": 7,
                "tokens_totais": 18,
            }
        )

        return "Resposta resiliente"

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        fake_generate,
    )

    monkeypatch.setattr(
        rag_engine,
        "get_model_for_role",
        lambda role: "gemini-rag-test",
    )

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como criar reserva?",
            "Contexto financeiro seguro.",
            usage_out=usage,
        )
    )

    assert result == "Resposta resiliente"

    assert (
        captured["modelo"]
        == "gemini-rag-test"
    )

    assert "Como criar reserva?" in (
        captured["prompt"]
    )

    assert "Contexto financeiro seguro." in (
        captured["prompt"]
    )

    assert usage == {
        "tokens_entrada": 11,
        "tokens_saida": 7,
        "tokens_totais": 18,
    }


def test_rag_preserves_fallback_on_service_failure(
    monkeypatch,
):
    usage = {
        "tokens_entrada": 999,
    }

    def broken_generate(
        *args,
        **kwargs,
    ):
        raise RuntimeError(
            "simulated provider failure"
        )

    monkeypatch.setattr(
        gemini_service,
        "gerar_texto_gemini",
        broken_generate,
    )

    result = (
        rag_engine.generate_gemini_rag_answer(
            "Como criar reserva?",
            "Contexto.",
            usage_out=usage,
        )
    )

    assert result is None
    assert usage == {}


def test_rag_no_longer_calls_google_client_directly():
    source = inspect.getsource(
        rag_engine.generate_gemini_rag_answer
    )

    assert "gerar_texto_gemini" in source

    assert "genai.Client" not in source

    assert (
        "executar_generate_content_observado"
        not in source
    )

    assert (
        "client.models.generate_content"
        not in source
    )


def test_gemini_text_service_propagates_usage(
    monkeypatch,
):
    response = SimpleNamespace(
        text="Resposta do Gemini",
        usage_metadata=SimpleNamespace(
            prompt_token_count=13,
            candidates_token_count=5,
            total_token_count=18,
        ),
    )

    class FakeRuntime:
        def execute(
            self,
            *,
            policy,
            operation,
            deadline_budget,
            minimum_retry_attempt_seconds,
        ):
            return operation()

    monkeypatch.setattr(
        gemini_service,
        "get_shared_resilience_runtime",
        lambda: FakeRuntime(),
    )

    monkeypatch.setattr(
        gemini_service,
        "criar_cliente_gemini",
        lambda *,
        timeout_ms: object(),
    )

    monkeypatch.setattr(
        gemini_service,
        "executar_generate_content_observado",
        lambda *args, **kwargs: response,
    )

    @contextmanager
    def fake_trace(
        policy,
    ):
        yield object()

    monkeypatch.setattr(
        gemini_service,
        "traced_resilience_operation",
        fake_trace,
    )

    usage = {}

    result = (
        gemini_service.gerar_texto_gemini(
            "Teste",
            modelo="gemini-test",
            usage_out=usage,
        )
    )

    assert result == "Resposta do Gemini"

    assert usage == {
        "tokens_entrada": 13,
        "tokens_saida": 5,
        "tokens_totais": 18,
    }


def test_resilient_service_uses_tracked_policy():
    policy = (
        gemini_service
        .GEMINI_TEXT_GENERATION_POLICY
    )

    assert (
        policy.name
        == "gemini.generate.text_service"
    )

    assert policy.max_attempts == 2
