from contextlib import contextmanager

from src.observability.langgraph_tracing import (
    add_langgraph_node_result_attributes,
    add_langgraph_result_attributes,
    build_langgraph_attributes,
    build_langgraph_node_attributes,
    traced_langgraph_execution,
    traced_langgraph_node,
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



def test_week5_result_attributes_export_only_safe_operational_metadata():
    span = FakeSpan()

    private_marker = (
        "PRIVATE_WEEK5_CONTENT_DO_NOT_EXPORT"
    )

    result = {
        "a2a_message_count": 3,
        "a2a_history": [
            {
                "allowed": True,
                "payload": private_marker,
            },
            {
                "allowed": False,
                "reason": private_marker,
            },
        ],
        "shared_blackboard_count": 2,
        "shared_blackboard_entries": [
            {
                "payload": {
                    "private": private_marker,
                },
            },
        ],
        "shared_blackboard_audit": [
            {
                "reason": "accepted",
            },
        ],
        "supervisor_mesh_active": True,
        "supervisor_mesh_status": "planned",
        "supervisor_mesh_visited_count": 2,
        "supervisor_mesh_history": [
            {
                "private": private_marker,
            },
        ],
        "supervisor_mesh_visit_history": [
            {},
            {},
        ],
        "adaptive_risk": "critical",
        "adaptive_route_type": "complex",
        "adaptive_multi_domain": True,
        "human_review_status": "requested",
        "human_review_limit_exceeded": False,
        "task_status": "completed",
        "task_completion_score": 0.91,
        "user_message": private_marker,
        "response": private_marker,
        "context": {
            "private": private_marker,
        },
    }

    add_langgraph_result_attributes(
        span,
        result,
    )

    assert (
        span.attributes[
            "agent.a2a_message_count"
        ]
        == 3
    )

    assert (
        span.attributes[
            "agent.a2a_history_count"
        ]
        == 2
    )

    assert (
        span.attributes[
            "agent.blackboard_entry_count"
        ]
        == 2
    )

    assert (
        span.attributes[
            "agent.blackboard_audit_count"
        ]
        == 1
    )

    assert (
        span.attributes[
            "agent.supervisor_mesh_active"
        ]
        is True
    )

    assert (
        span.attributes[
            "agent.supervisor_mesh_visited_count"
        ]
        == 2
    )

    assert (
        span.attributes[
            "agent.supervisor_mesh_history_count"
        ]
        == 1
    )

    assert (
        span.attributes[
            "agent.supervisor_mesh_visit_history_count"
        ]
        == 2
    )

    assert (
        span.attributes[
            "agent.adaptive_risk"
        ]
        == "critical"
    )

    assert (
        span.attributes[
            "agent.adaptive_route_type"
        ]
        == "complex"
    )

    assert (
        span.attributes[
            "agent.adaptive_multi_domain"
        ]
        is True
    )

    assert (
        span.attributes[
            "agent.human_review_status"
        ]
        == "requested"
    )

    assert (
        span.attributes[
            "agent.task_status"
        ]
        == "completed"
    )

    assert (
        span.attributes[
            "agent.task_completion_score"
        ]
        == 0.91
    )

    serialized = str(
        span.attributes
    )

    assert (
        private_marker
        not in serialized
    )

    assert (
        "shared_blackboard_entries"
        not in span.attributes
    )

    assert (
        "a2a_history"
        not in span.attributes
    )

    assert (
        "user_message"
        not in span.attributes
    )

    assert (
        "response"
        not in span.attributes
    )

    assert (
        "context"
        not in span.attributes
    )


def test_week5_observability_handles_missing_optional_state():
    span = FakeSpan()

    add_langgraph_result_attributes(
        span,
        {},
    )

    assert (
        span.attributes[
            "agent.a2a_message_count"
        ]
        == 0
    )

    assert (
        span.attributes[
            "agent.blackboard_entry_count"
        ]
        == 0
    )

    assert (
        span.attributes[
            "agent.supervisor_mesh_visited_count"
        ]
        == 0
    )



def test_build_node_attributes_exports_only_safe_state():
    private_marker = (
        "PRIVATE_NODE_CONTENT_DO_NOT_EXPORT"
    )

    attributes = (
        build_langgraph_node_attributes(
            node_name="adaptive_gateway",
            state={
                "thread_id": "thread-real",
                "user_id": "user-real",
                "current_agent": "financial_agent",
                "current_team": "financial_team",
                "adaptive_risk": "critical",
                "adaptive_route_type": "complex",
                "a2a_message_count": 2,
                "shared_blackboard_count": 3,
                "supervisor_mesh_visited_count": 2,
                "human_review_count": 1,
                "human_review_required": True,
                "user_message": private_marker,
                "response": private_marker,
                "context": {
                    "private": private_marker,
                },
                "shared_blackboard_entries": [
                    {
                        "payload": private_marker,
                    },
                ],
            },
        )
    )

    assert (
        attributes[
            "agent.node.name"
        ]
        == "adaptive_gateway"
    )

    assert (
        attributes[
            "agent.adaptive_risk"
        ]
        == "critical"
    )

    assert (
        attributes[
            "agent.a2a_message_count"
        ]
        == 2
    )

    assert (
        attributes[
            "agent.blackboard_entry_count"
        ]
        == 3
    )

    assert (
        attributes[
            "inna.thread_id_hash"
        ]
        != "thread-real"
    )

    assert (
        attributes[
            "enduser.id_hash"
        ]
        != "user-real"
    )

    assert (
        private_marker
        not in str(
            attributes
        )
    )


def test_node_result_attributes_export_only_safe_metadata():
    span = FakeSpan()

    private_marker = (
        "PRIVATE_NODE_RESULT_DO_NOT_EXPORT"
    )

    add_langgraph_node_result_attributes(
        span,
        {
            "current_agent": "rag_agent",
            "current_team": "knowledge_team",
            "adaptive_risk": "high",
            "a2a_message_count": 4,
            "shared_blackboard_count": 2,
            "handoff_count": 1,
            "human_review_required": True,
            "response": private_marker,
            "errors": [
                private_marker,
            ],
            "shared_blackboard_entries": [
                {
                    "payload": private_marker,
                },
            ],
        },
    )

    assert (
        span.attributes[
            "agent.node.result_available"
        ]
        is True
    )

    assert (
        span.attributes[
            "agent.node.current_agent"
        ]
        == "rag_agent"
    )

    assert (
        span.attributes[
            "agent.node.a2a_message_count"
        ]
        == 4
    )

    assert (
        span.attributes[
            "agent.node.blackboard_entry_count"
        ]
        == 2
    )

    assert (
        private_marker
        not in str(
            span.attributes
        )
    )

    assert (
        "response"
        not in span.attributes
    )

    assert (
        "errors"
        not in span.attributes
    )


def test_traced_langgraph_node_uses_dedicated_child_span(
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
        captured[
            "instrumentation_name"
        ] = instrumentation_name

        yield FakeSpan()

    monkeypatch.setattr(
        (
            "src.observability.langgraph_tracing."
            "traced_operation"
        ),
        fake_traced_operation,
    )

    with traced_langgraph_node(
        node_name="supervisor_mesh",
        state={
            "thread_id": "thread-real",
            "supervisor_mesh_active": True,
            "supervisor_mesh_status": "planned",
        },
    ):
        pass

    assert (
        captured["name"]
        == "inna.langgraph.node.supervisor_mesh"
    )

    assert (
        captured[
            "instrumentation_name"
        ]
        == "inna.agents.langgraph"
    )

    assert (
        captured["attributes"][
            "privacy.content_exported"
        ]
        is False
    )

    assert (
        captured["attributes"][
            "supervisor_mesh_status"
        ]
        if "supervisor_mesh_status"
        in captured["attributes"]
        else captured["attributes"][
            "agent.supervisor_mesh_status"
        ]
    ) == "planned"
