from __future__ import annotations

from src.agents.graph import criar_builder_inna


def _edge_pairs(builder):
    pairs = set()

    for edge in builder.edges:
        if (
            isinstance(edge, tuple)
            and len(edge) >= 2
        ):
            source, target = edge[:2]

        else:
            source = getattr(
                edge,
                "source",
                None,
            )

            target = getattr(
                edge,
                "target",
                None,
            )

        if (
            source is None
            or target is None
        ):
            continue

        pairs.add(
            (
                str(source),
                str(target),
            )
        )

    return pairs


def test_summary_node_is_registered():
    builder = criar_builder_inna()

    assert (
        "conversation_summary"
        in builder.nodes
    )


def test_all_specialized_agents_follow_finalization_pipeline():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    agents = {
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    }

    for agent in agents:
        assert (
            agent,
            "task_completion",
        ) in edges

        assert (
            agent,
            "conversation_summary",
        ) not in edges

    assert (
        "task_completion",
        "human_review_policy",
    ) in edges

    assert (
        "task_completion",
        "handoff_coordinator",
    ) not in edges


def test_specialized_agents_do_not_finish_directly():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    agents = {
        "financial_agent",
        "education_agent",
        "rag_agent",
        "report_agent",
        "fallback_agent",
    }

    for agent in agents:
        assert not any(
            source == agent
            and target == "__end__"
            for source, target in edges
        )


def test_summary_node_is_the_final_node():
    builder = criar_builder_inna()
    edges = _edge_pairs(builder)

    assert (
        "conversation_summary",
        "__end__",
    ) in edges
