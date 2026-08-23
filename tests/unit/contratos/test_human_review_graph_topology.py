from __future__ import annotations

from src.agents.graph import (
    criar_builder_inna,
)


def _builder():
    return criar_builder_inna()


def test_graph_registers_human_review_nodes():
    builder = _builder()

    assert (
        "human_review_policy"
        in builder.nodes
    )

    assert (
        "human_review_interrupt"
        in builder.nodes
    )


def test_task_completion_routes_to_policy():
    builder = _builder()

    assert (
        "task_completion",
        "human_review_policy",
    ) in builder.edges


def test_old_direct_edge_was_removed():
    builder = _builder()

    assert (
        "task_completion",
        "handoff_coordinator",
    ) not in builder.edges


def test_policy_has_conditional_branch():
    builder = _builder()

    assert (
        "human_review_policy"
        in builder.branches
    )


def test_interrupt_has_conditional_branch():
    builder = _builder()

    assert (
        "human_review_interrupt"
        in builder.branches
    )


def test_existing_handoff_branch_is_preserved():
    builder = _builder()

    assert (
        "handoff_coordinator"
        in builder.branches
    )


def test_conversation_summary_still_reaches_end():
    builder = _builder()

    assert any(
        source == "conversation_summary"
        for source, _ in builder.edges
    )