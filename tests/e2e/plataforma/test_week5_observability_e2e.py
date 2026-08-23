from contextlib import contextmanager

from src.agents.graph import _observed_control_node
from src.observability import langgraph_tracing


class FakeSpan:
    def __init__(self):
        self.attributes = {}

    def set_attribute(
        self,
        name,
        value,
    ):
        self.attributes[name] = value


def test_root_and_control_node_spans_form_safe_observability_flow(
    monkeypatch,
):
    spans = []

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        span = FakeSpan()

        span.attributes.update(
            attributes or {}
        )

        spans.append(
            {
                "name": name,
                "instrumentation_name": (
                    instrumentation_name
                ),
                "span": span,
            }
        )

        yield span

    monkeypatch.setattr(
        langgraph_tracing,
        "traced_operation",
        fake_traced_operation,
    )

    private_marker = (
        "PRIVATE_MULTI_AGENT_CONTENT_DO_NOT_EXPORT"
    )

    def fake_supervisor_mesh(
        state,
    ):
        assert (
            state["user_message"]
            == private_marker
        )

        return {
            "supervisor_mesh_active": True,
            "supervisor_mesh_status": "planned",
            "supervisor_mesh_visited_count": 2,
            "shared_blackboard_count": 1,
            "a2a_message_count": 1,
            "user_message": private_marker,
            "response": private_marker,
            "shared_blackboard_entries": [
                {
                    "payload": private_marker,
                },
            ],
        }

    observed_node = _observed_control_node(
        "supervisor_mesh",
        fake_supervisor_mesh,
    )

    state = {
        "thread_id": "thread-private",
        "user_message": private_marker,
        "supervisor_mesh_active": True,
        "supervisor_mesh_status": "planned",
        "shared_blackboard_entries": [
            {
                "payload": private_marker,
            },
        ],
    }

    with (
        langgraph_tracing
        .traced_langgraph_execution(
            execution_mode="non_persistent",
            thread_id="thread-private",
            user_id="user-private",
            language="pt",
            currency="BRL",
            human_review_enabled=True,
        )
    ) as root_span:
        result = observed_node(
            state
        )

        (
            langgraph_tracing
            .add_langgraph_result_attributes(
                root_span,
                result,
            )
        )

    assert (
        [item["name"] for item in spans]
        == [
            "inna.langgraph.execution",
            "inna.langgraph.node.supervisor_mesh",
        ]
    )

    assert all(
        item["instrumentation_name"]
        == "inna.agents.langgraph"
        for item in spans
    )

    serialized = str(
        [
            item["span"].attributes
            for item in spans
        ]
    )

    assert (
        private_marker
        not in serialized
    )

    assert (
        "thread-private"
        not in serialized
    )

    assert (
        "user-private"
        not in serialized
    )

    child = spans[1]["span"].attributes

    assert (
        child[
            "agent.node.name"
        ]
        == "supervisor_mesh"
    )

    assert (
        child[
            "agent.node.supervisor_mesh_status"
        ]
        == "planned"
    )

    assert (
        child[
            "agent.node.supervisor_mesh_visited_count"
        ]
        == 2
    )

    assert (
        child[
            "agent.node.a2a_message_count"
        ]
        == 1
    )

    assert (
        child[
            "agent.node.blackboard_entry_count"
        ]
        == 1
    )


def test_control_plane_components_use_observed_wrapper(
    monkeypatch,
):
    spans = []

    @contextmanager
    def fake_traced_operation(
        name,
        *,
        attributes,
        instrumentation_name,
    ):
        del instrumentation_name

        span = FakeSpan()
        span.attributes.update(
            attributes or {}
        )

        spans.append(
            (
                name,
                span,
            )
        )

        yield span

    monkeypatch.setattr(
        langgraph_tracing,
        "traced_operation",
        fake_traced_operation,
    )

    components = (
        "adaptive_gateway",
        "supervisor_mesh",
        "team_router",
        "financial_team_supervisor",
        "knowledge_team_supervisor",
        "support_team_supervisor",
        "execution_governance",
        "task_completion",
        "human_review_policy",
        "human_review_interrupt",
        "handoff_coordinator",
    )

    for component in components:
        observed = _observed_control_node(
            component,
            lambda state: {
                "execution_steps": (
                    state.get(
                        "execution_steps",
                        0,
                    )
                    + 1
                ),
            },
        )

        result = observed(
            {
                "execution_steps": 0,
            }
        )

        assert (
            result[
                "execution_steps"
            ]
            == 1
        )

    assert (
        [name for name, _ in spans]
        == [
            (
                "inna.langgraph.node."
                f"{component}"
            )
            for component in components
        ]
    )
