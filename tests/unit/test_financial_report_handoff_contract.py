from __future__ import annotations

import inspect

from src.agents.nodes import (
    financial_agent_node,
)


def _financial_source() -> str:
    return inspect.getsource(financial_agent_node)


def test_financial_agent_has_report_handoff_guard():
    source = _financial_source()

    assert "should_request_report_handoff" in source

    assert "generate_report" in source

    assert "diagnostico_financeiro" in source

    assert "handoff_limit_exceeded" in source


def test_financial_agent_requests_report_agent():
    source = _financial_source()

    assert '"handoff_target": (' in source

    assert '"report_agent"' in source

    assert '"handoff_required": (' in source


def test_financial_handoff_requires_success_path():
    source = _financial_source()

    ready_guard_position = source.index("if not resolution.ready:")

    decision_position = source.index("should_request_report_handoff")

    assert decision_position > ready_guard_position


def test_financial_handoff_prevents_duplicate_active_transfer():
    source = _financial_source()

    assert "active_handoff_statuses" in source

    assert '"requested"' in source
    assert '"accepted"' in source

    assert "not handoff_already_active" in source


def test_incomplete_financial_input_clears_handoff():
    source = _financial_source()

    incomplete_start = source.index("if not resolution.ready:")

    tool_context_start = source.index("Construção segura do contexto")

    incomplete_block = source[incomplete_start:tool_context_start]

    assert '"handoff_required": False' in incomplete_block

    assert '"handoff_target": ""' in incomplete_block


def test_financial_tool_failure_clears_handoff():
    source = _financial_source()

    failure_start = source.index("tool_result.status")

    success_section = source.index("Resultado financeiro aprovado")

    failure_block = source[failure_start:success_section]

    assert '"handoff_required": False' in failure_block

    assert '"handoff_target": ""' in failure_block


def test_handoff_request_is_auditable():
    source = _financial_source()

    assert '"handoff_request"' in source

    assert '"diagnosis_completed_with_report_request"' in source

    assert "handoff:intent:" in source
