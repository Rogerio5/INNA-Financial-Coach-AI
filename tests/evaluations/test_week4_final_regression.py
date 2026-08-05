from __future__ import annotations

from pathlib import Path

from src.evaluation.final_regression import (
    build_offline_environment,
    build_suite_specs,
    discover_agentic_rag_tests,
    discover_mcp_existing_tests,
    load_policy,
    validate_reports,
)

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

POLICY_PATH = (
    PROJECT_ROOT
    / "config"
    / "evaluation"
    / "week4_final_regression.json"
)

EVALUATION_PYTHON = (
    PROJECT_ROOT
    / ".venv-evaluation"
    / "Scripts"
    / "python.exe"
)


def test_policy_is_offline() -> None:
    policy = load_policy(
        POLICY_PATH
    )

    assert policy.phase == "8B.2H"
    assert policy.offline is True
    assert policy.expected_dataset_case_count == 24
    assert policy.expected_dataset_category_count == 12
    assert policy.minimum_mcp_scenario_count == 8


def test_agentic_rag_tests_are_discovered() -> None:
    paths = discover_agentic_rag_tests(
        PROJECT_ROOT
    )

    assert paths
    assert all(
        path.exists()
        for path in paths
    )


def test_mcp_regression_tests_exist() -> None:
    paths = discover_mcp_existing_tests(
        PROJECT_ROOT
    )

    assert len(paths) == 7
    assert all(
        path.exists()
        for path in paths
    )


def test_required_suite_codes_are_built() -> None:
    policy = load_policy(
        POLICY_PATH
    )

    specs = build_suite_specs(
        PROJECT_ROOT,
        evaluation_python=(
            EVALUATION_PYTHON
        ),
    )

    codes = {
        spec.code
        for spec in specs
    }

    assert (
        set(
            policy.required_suite_codes
        )
        <= codes
    )


def test_commands_do_not_contain_live_urls() -> None:
    specs = build_suite_specs(
        PROJECT_ROOT,
        evaluation_python=(
            EVALUATION_PYTHON
        ),
    )

    serialized = " ".join(
        " ".join(
            spec.command
        )
        for spec in specs
    ).casefold()

    assert "https://" not in serialized
    assert "http://" not in serialized
    assert "gemini_api_key" not in serialized
    assert "database_url" not in serialized


def test_offline_environment_uses_local_sqlite() -> None:
    environment = (
        build_offline_environment()
    )

    assert environment[
        "INNA_OFFLINE_EVALUATION"
    ] == "true"

    assert environment[
        "GEMINI_API_KEY"
    ] == ""

    assert environment[
        "GOOGLE_API_KEY"
    ] == ""

    assert environment[
        "DATABASE_URL"
    ] == "sqlite+pysqlite:///:memory:"

    assert environment[
        "NEON_DATABASE_URL"
    ] == "sqlite+pysqlite:///:memory:"

    assert "postgres" not in environment[
        "DATABASE_URL"
    ].casefold()

    assert "neon" not in environment[
        "DATABASE_URL"
    ].casefold()

    assert "@" not in environment[
        "DATABASE_URL"
    ]


def test_current_reports_pass_policy() -> None:
    policy = load_policy(
        POLICY_PATH
    )

    validations, facts = validate_reports(
        PROJECT_ROOT,
        policy,
    )

    assert all(
        validations.values()
    )

    assert facts[
        "dataset_case_count"
    ] == 24

    assert facts[
        "dataset_category_count"
    ] == 12

    assert facts[
        "mcp_scenario_count"
    ] >= 8

    assert facts[
        "quality_gate_passed"
    ] is True


def test_offline_database_url_is_not_empty() -> None:
    environment = build_offline_environment()

    database_url = environment[
        "DATABASE_URL"
    ]

    assert database_url
    assert database_url.startswith(
        "sqlite+"
    )
    assert database_url.endswith(
        ":memory:"
    )
