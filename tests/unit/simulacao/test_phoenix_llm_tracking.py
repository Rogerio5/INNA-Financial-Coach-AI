from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from src.observability import llm_tracking


class FakeSpan:
    def __init__(self):
        self.attributes = {}

    def set_attribute(self, name, value):
        self.attributes[name] = value


@contextmanager
def fake_traced_operation(
    name,
    *,
    attributes=None,
    instrumentation_name=None,
):
    span = FakeSpan()
    span.attributes.update(attributes or {})
    span.attributes["test.span_name"] = name
    span.attributes["test.instrumentation"] = (
        instrumentation_name or ""
    )

    fake_traced_operation.last_span = span

    yield span


fake_traced_operation.last_span = None


@pytest.fixture
def telemetry_mocks(monkeypatch):
    database_records = []

    monkeypatch.setattr(
        llm_tracking,
        "traced_operation",
        fake_traced_operation,
    )

    monkeypatch.setattr(
        llm_tracking,
        "registrar_consumo_llm",
        lambda **kwargs: database_records.append(kwargs),
    )

    monkeypatch.setattr(
        llm_tracking,
        "extrair_tokens_resposta",
        lambda response: {
            "tokens_entrada": 12,
            "tokens_saida": 8,
            "tokens_totais": 20,
        },
    )

    return database_records


def test_successful_llm_call_creates_sanitized_span(
    telemetry_mocks,
):
    response = SimpleNamespace(text="conteúdo privado")

    result = llm_tracking.executar_llm_observado(
        lambda: response,
        modelo="gemini-test",
        operacao="generate_content",
        provider="google",
        origem="unit-test",
        usuario_id="usuario-real",
        trace_id="trace-real",
        request_id="request-real",
        metadados={
            "prompt": "não exportar",
        },
    )

    assert result is response

    span = fake_traced_operation.last_span

    assert span is not None
    assert span.attributes["llm.model_name"] == "gemini-test"
    assert span.attributes["inna.llm.operation"] == "generate_content"
    assert span.attributes["llm.provider"] == "google"
    assert (
        span.attributes["openinference.span.kind"]
        == "LLM"
    )
    assert span.attributes["inna.llm.origin"] == "unit-test"
    assert span.attributes["llm.token_count.prompt"] == 12
    assert span.attributes["llm.token_count.completion"] == 8
    assert span.attributes["llm.token_count.total"] == 20
    assert span.attributes["llm.success"] is True

    assert (
        span.attributes["enduser.id_hash"]
        != "usuario-real"
    )
    assert (
        span.attributes["inna.trace_id_hash"]
        != "trace-real"
    )
    assert (
        span.attributes["inna.request_id_hash"]
        != "request-real"
    )

    assert "prompt" not in span.attributes
    assert "response" not in span.attributes
    assert "contents" not in span.attributes

    assert len(telemetry_mocks) == 1
    assert telemetry_mocks[0]["sucesso"] is True


def test_failed_llm_call_records_error_type_only(
    telemetry_mocks,
):
    def failing_call():
        raise RuntimeError(
            "mensagem privada que não deve ir ao Phoenix"
        )

    with pytest.raises(RuntimeError):
        llm_tracking.executar_llm_observado(
            failing_call,
            modelo="gemini-test",
            operacao="generate_content",
            origem="unit-test",
        )

    span = fake_traced_operation.last_span

    assert span is not None
    assert span.attributes["llm.success"] is False
    assert span.attributes["llm.error_type"] == "RuntimeError"

    assert not any(
        "mensagem privada" in str(value)
        for value in span.attributes.values()
    )

    assert len(telemetry_mocks) == 1
    assert telemetry_mocks[0]["sucesso"] is False
    assert telemetry_mocks[0]["erro_tipo"] == "RuntimeError"


def test_generate_content_does_not_export_contents(
    telemetry_mocks,
):
    class FakeModels:
        def generate_content(self, **kwargs):
            assert kwargs["contents"] == "pergunta confidencial"
            return SimpleNamespace(text="resposta confidencial")

    client = SimpleNamespace(
        models=FakeModels()
    )

    result = (
        llm_tracking.executar_generate_content_observado(
            client,
            modelo="gemini-test",
            contents="pergunta confidencial",
            origem="unit-test",
        )
    )

    assert result.text == "resposta confidencial"

    span = fake_traced_operation.last_span

    assert span is not None
    assert "contents" not in span.attributes
    assert "prompt" not in span.attributes
    assert "response" not in span.attributes
