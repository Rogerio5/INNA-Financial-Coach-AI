from pathlib import Path

WORKFLOW = Path(
    ".github/workflows/evaluation-ci.yml"
)


def _workflow_source() -> str:
    return WORKFLOW.read_text(
        encoding="utf-8"
    )


def test_multi_agent_runtime_changes_trigger_evaluation_ci():
    source = _workflow_source()

    required_paths = (
        'src/agents/**',
        'src/agentic_rag/**',
        'src/agent_tools/**',
        'src/a2a_server/**',
        'src/mcp_server/**',
        'src/observability/**',
        'src/context_engineering/**',
        'src/services/rag/**',
        'src/services/llm/**',
        'src/gemini_client.py',
        'api/**',
    )

    for path in required_paths:
        assert (
            source.count(
                f'- "{path}"'
            )
            == 2
        )


def test_quality_gate_remains_deterministic_and_cost_free():
    source = _workflow_source()

    assert (
        'RUN_LIVE_GEMINI_TESTS: "0"'
        in source
    )

    assert (
        "--minimum-pass-rate 1.0"
        in source
    )

    assert (
        "--maximum-failed-cases 0"
        in source
    )

    assert (
        "--maximum-blocked-cases 0"
        in source
    )

    assert (
        "--maximum-error-cases 0"
        in source
    )

    assert (
        "--maximum-total-cost 0"
        in source
    )


def test_quality_gate_and_baseline_regression_are_enforced():
    source = _workflow_source()

    assert (
        "python -m src.evaluation run-official"
        in source
    )

    assert (
        "python -m src.evaluation.ci_pipeline"
        in source
    )

    assert (
        "O Quality Gate bloqueou esta alteração."
        in source
    )

    assert (
        "O gate de regressão bloqueou esta alteração."
        in source
    )


def test_full_regression_remains_part_of_evaluation_ci():
    source = _workflow_source()

    assert (
        "python -m pytest -q"
        in source
    )
