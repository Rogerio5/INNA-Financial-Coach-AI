from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.offline_dashboard import (
    OfflineDashboardDataError,
    OfflineDashboardPaths,
    benchmark_profile_rows,
    build_overview,
    load_offline_dashboard_snapshot,
    mcp_scenario_rows,
    quality_gate_rows,
    report_status_rows,
    security_rows,
)


def write_json(
    path: Path,
    payload: dict,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def dashboard_paths(
    tmp_path: Path,
) -> OfflineDashboardPaths:
    benchmark = tmp_path / "offline_benchmark_latest.json"

    quality_gate = tmp_path / "offline_quality_gate_latest.json"

    quality_summary = tmp_path / "offline_quality_summary_latest.json"

    mcp_e2e = tmp_path / "mcp_simulated_e2e_latest.json"

    write_json(
        benchmark,
        {
            "dataset_version": "1.0.0",
            "case_count": 24,
            "category_count": 12,
            "legacy_summary": {
                "total_cases": 24,
                "passed_cases": 0,
                "pass_rate": 0.0,
                "average_score": 0.389444,
                "average_latency_ms": 55,
            },
            "agentic_summary": {
                "total_cases": 24,
                "passed_cases": 24,
                "pass_rate": 1.0,
                "average_score": 1.0,
                "average_latency_ms": 120,
            },
            "comparison": {
                "score_delta": 0.610556,
                "latency_delta_ms": 65,
                "improvements": [
                    "case-1",
                    "case-2",
                ],
                "regressions": [],
            },
        },
    )

    write_json(
        quality_gate,
        {
            "passed": True,
            "checks": [
                {
                    "name": "agentic_pass_rate",
                    "actual": 1.0,
                    "expected": ">=1.0",
                    "passed": True,
                    "blocking": True,
                },
                {
                    "name": "regression_count",
                    "actual": 0,
                    "expected": "<=0",
                    "passed": True,
                    "blocking": True,
                },
            ],
        },
    )

    write_json(
        quality_summary,
        {
            "quality_gate_passed": True,
            "dataset_case_count": 24,
            "dataset_category_count": 12,
        },
    )

    write_json(
        mcp_e2e,
        {
            "offline": True,
            "scenario_count": 8,
            "network_server_started": False,
            "http_requests_executed": False,
            "database_connections_executed": False,
            "gemini_api_called": False,
            "live_rag_called": False,
            "live_mcp_called": False,
            "user_id": "user-test",
            "session_id": "session-test",
            "scenarios": {
                "health": {
                    "status": "success",
                    "error_code": "",
                    "output": {
                        "trace_id": "trace-health",
                    },
                },
                "rag": {
                    "status": "success",
                    "error_code": "",
                    "output": {
                        "user_id": "user-test",
                        "session_id": "session-test",
                        "trace_id": "trace-rag",
                    },
                },
                "financial": {
                    "status": "success",
                    "error_code": "",
                    "output": {
                        "user_id": "user-test",
                        "session_id": "session-test",
                        "trace_id": "trace-financial",
                    },
                },
                "invalid_arguments": {
                    "status": "validation_error",
                    "error_code": ("tool_input_validation_error"),
                },
                "permission_denied": {
                    "status": "denied",
                    "error_code": ("tool_permission_denied"),
                },
                "unknown_tool": {
                    "status": "not_found",
                    "error_code": "tool_not_found",
                },
                "controlled_error": {
                    "status": "error",
                    "error_code": ("tool_execution_error"),
                },
                "timeout": {
                    "status": "timeout",
                    "error_code": "tool_timeout",
                },
            },
        },
    )

    return OfflineDashboardPaths(
        benchmark=benchmark,
        quality_gate=quality_gate,
        quality_summary=quality_summary,
        mcp_e2e=mcp_e2e,
    )


def load_snapshot(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
):
    return load_offline_dashboard_snapshot(
        tmp_path,
        paths=dashboard_paths,
    )


def test_loads_all_dashboard_reports(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    snapshot = load_snapshot(
        tmp_path,
        dashboard_paths,
    )

    assert snapshot.benchmark
    assert snapshot.quality_gate
    assert snapshot.quality_summary
    assert snapshot.mcp_e2e
    assert snapshot.errors == ()


def test_builds_normalized_overview(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    overview = build_overview(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert overview["case_count"] == 24
    assert overview["category_count"] == 12
    assert overview["legacy_pass_rate"] == 0
    assert overview["agentic_pass_rate"] == 1
    assert overview["score_delta"] == pytest.approx(0.610556)
    assert overview["latency_delta_ms"] == 65
    assert overview["quality_gate_passed"] is True
    assert overview["mcp_scenario_count"] == 8


def test_builds_benchmark_profile_rows(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = benchmark_profile_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert len(rows) == 2
    assert rows[0]["Perfil"] == "Legacy"
    assert rows[1]["Perfil"] == "Agentic"
    assert rows[1]["Aprovados"] == 24


def test_builds_quality_gate_rows(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = quality_gate_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert len(rows) == 2
    assert all(row["Aprovado"] for row in rows)


def test_builds_eight_mcp_scenario_rows(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = mcp_scenario_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert len(rows) == 8

    statuses = {row["Cenário"]: row["Status"] for row in rows}

    assert statuses["health"] == "success"
    assert statuses["timeout"] == "timeout"


def test_preserves_context_identifiers(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = mcp_scenario_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    rag = next(row for row in rows if row["Cenário"] == "rag")

    assert rag["user_id"] == "user-test"
    assert rag["session_id"] == "session-test"
    assert rag["trace_id"] == "trace-rag"


def test_all_offline_security_controls_pass(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = security_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert len(rows) == 7
    assert all(row["Aprovado"] for row in rows)


def test_report_status_contains_four_sources(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    rows = report_status_rows(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert len(rows) == 4
    assert all(row["Existe"] for row in rows)
    assert all(row["Carregado"] for row in rows)


def test_missing_report_raises_in_strict_mode(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    dashboard_paths.mcp_e2e.unlink()

    with pytest.raises(
        OfflineDashboardDataError,
        match="Relatório não encontrado",
    ):
        load_offline_dashboard_snapshot(
            tmp_path,
            paths=dashboard_paths,
            strict=True,
        )


def test_missing_report_is_recorded_in_safe_mode(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    dashboard_paths.mcp_e2e.unlink()

    snapshot = load_offline_dashboard_snapshot(
        tmp_path,
        paths=dashboard_paths,
        strict=False,
    )

    assert snapshot.mcp_e2e == {}
    assert len(snapshot.errors) == 1


def test_invalid_json_is_rejected(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    dashboard_paths.benchmark.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        OfflineDashboardDataError,
        match="JSON inválido",
    ):
        load_offline_dashboard_snapshot(
            tmp_path,
            paths=dashboard_paths,
        )


def test_category_count_falls_back_to_quality_gate_check(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    benchmark = json.loads(dashboard_paths.benchmark.read_text(encoding="utf-8"))

    benchmark.pop(
        "category_count",
        None,
    )

    write_json(
        dashboard_paths.benchmark,
        benchmark,
    )

    gate = json.loads(dashboard_paths.quality_gate.read_text(encoding="utf-8"))

    gate["checks"].append(
        {
            "check_name": "dataset_category_count",
            "actual": 12,
            "expected": "12",
            "passed": True,
            "blocking": True,
        }
    )

    write_json(
        dashboard_paths.quality_gate,
        gate,
    )

    overview = build_overview(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert overview["category_count"] == 12


def test_category_count_supports_nested_real_gate_schema(
    tmp_path: Path,
    dashboard_paths: OfflineDashboardPaths,
) -> None:
    benchmark = json.loads(dashboard_paths.benchmark.read_text(encoding="utf-8"))

    benchmark.pop(
        "category_count",
        None,
    )

    write_json(
        dashboard_paths.benchmark,
        benchmark,
    )

    quality_summary = json.loads(
        dashboard_paths.quality_summary.read_text(encoding="utf-8")
    )

    quality_summary.pop(
        "dataset_category_count",
        None,
    )

    write_json(
        dashboard_paths.quality_summary,
        quality_summary,
    )

    write_json(
        dashboard_paths.quality_gate,
        {
            "result": {
                "quality_checks": [
                    {
                        "check_name": ("dataset_category_count"),
                        "actual": {
                            "value": 12,
                        },
                        "expected": 12,
                        "passed": True,
                    }
                ]
            }
        },
    )

    overview = build_overview(
        load_snapshot(
            tmp_path,
            dashboard_paths,
        )
    )

    assert overview["category_count"] == 12
