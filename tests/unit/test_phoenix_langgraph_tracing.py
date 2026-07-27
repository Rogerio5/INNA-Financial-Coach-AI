from contextlib import contextmanager

from src.observability.langgraph_tracing import (
    add_langgraph_result_attributes,
    build_langgraph_attributes,
    traced_langgraph_execution,
)


class FakeSpan:
    def __init__(self):
        self.attributes = {}

    def set_attribute(self, name, value):
        self.attributes[name] = value


def test_build_attributes_hashes_identifiers():
    attributes = build_langgraph_attributes(
        execution_mode="persistent",
        thread_id="thread-real",
        user_id="usuario-real",
        language="pt",
        currency="BRL",
        human_review_enabled=True,
    )

    assert attributes["agent.framework"] == "langgraph"
    assert attributes["agent.execution_mode"] == "persistent"
    assert attributes["inna.language"] == "pt"
    assert attributes["inna.currency"] == "BRL"

    assert (
        attributes["inna.thread_id_hash"]
        != "thread-real"
    )
    assert (
        attributes["enduser.id_hash"]
        != "usuario-real"
    )

    assert "message" not in attributes
    assert "prompt" not in attributes
    assert "response" not in attributes


def test_add_result_attributes_exports_only_metrics():
    span = FakeSpan()

    result = {
        "execution_steps": 7,
        "handoff_count": 2,
        "human_review_count": 1,
        "current_team": "financial",
        "team_route": "financial_agent",
        "loop_detected": False,
        "errors": ["conteúdo privado"],
        "route_history": ["supervisor", "financial_agent"],
        "tool_results": [
            {
                "private": "conteúdo privado",
            }
        ],
        "user_message": "não exportar",
        "final_answer": "não exportar",
    }

    add_langgraph_result_attributes(
        span,
        result,
    )

    assert span.attributes["agent.execution_steps"] == 7
    assert span.attributes["agent.handoff_count"] == 2
    assert span.attributes["agent.error_count"] == 1
    assert span.attributes["agent.route_count"] == 2
    assert span.attributes["agent.tool_result_count"] == 1

    assert "user_message" not in span.attributes
    assert "final_answer" not in span.attributes
    assert "errors" not in span.attributes
    assert "tool_results" not in span.attributes


def test_traced_execution_uses_safe_attributes(
    monkeypatch,
):
    captured = {}

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        captured["name"] = name
        captured["attributes"] = attributes
        captured["instrumentation_name"] = (
            instrumentation_name
        )

        yield FakeSpan()

    monkeypatch.setattr(
        (
            "src.observability.langgraph_tracing."
            "traced_operation"
        ),
        fake_traced_operation,
    )

    with traced_langgraph_execution(
        execution_mode="non_persistent",
        thread_id="thread-real",
        user_id="usuario-real",
    ):
        pass

    assert captured["name"] == "inna.langgraph.execution"
    assert (
        captured["instrumentation_name"]
        == "inna.agents.langgraph"
    )

    attributes = captured["attributes"]

    assert attributes["privacy.content_exported"] is False
    assert "thread-real" not in attributes.values()
    assert "usuario-real" not in attributes.values()
