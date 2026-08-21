"""Runner offline da regressão final da Semana 4."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

OFFLINE_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@dataclass(frozen=True, slots=True)
class FinalRegressionPolicy:
    """Política da regressão final."""

    policy_version: str
    phase: str
    offline: bool
    expected_dataset_version: str
    expected_dataset_case_count: int
    expected_dataset_category_count: int
    minimum_mcp_scenario_count: int
    require_quality_gate_passed: bool
    require_all_offline_controls: bool
    require_main_environment_pip_check: bool
    require_evaluation_environment_pip_check: bool
    require_git_diff_check: bool
    required_suite_codes: tuple[str, ...]
    required_reports: tuple[str, ...]
    forbidden_environment_usage: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegressionSuiteSpec:
    """Comando pertencente à regressão."""

    code: str
    description: str
    command: tuple[str, ...]
    timeout_seconds: float = 300.0


@dataclass(frozen=True, slots=True)
class RegressionSuiteResult:
    """Resultado de uma suíte executada."""

    code: str
    description: str
    command: tuple[str, ...]
    return_code: int
    passed: bool
    duration_seconds: float
    pytest_passed_count: int | None
    stdout_tail: str
    stderr_tail: str


@dataclass(frozen=True, slots=True)
class FinalRegressionReport:
    """Relatório consolidado da regressão."""

    phase: str
    policy_version: str
    generated_at: str
    offline: bool
    overall_passed: bool
    suite_count: int
    passed_suite_count: int
    failed_suite_codes: tuple[str, ...]
    suites: tuple[RegressionSuiteResult, ...]
    validations: Mapping[str, bool]
    facts: Mapping[str, Any]
    notes: tuple[str, ...]


def load_policy(
    path: Path,
) -> FinalRegressionPolicy:
    """Carrega a política JSON."""

    payload = json.loads(path.read_text(encoding="utf-8-sig"))

    if not isinstance(
        payload,
        Mapping,
    ):
        raise TypeError("A política precisa ser um objeto JSON.")

    return FinalRegressionPolicy(
        policy_version=str(payload["policy_version"]),
        phase=str(payload["phase"]),
        offline=bool(payload["offline"]),
        expected_dataset_version=str(payload["expected_dataset_version"]),
        expected_dataset_case_count=int(payload["expected_dataset_case_count"]),
        expected_dataset_category_count=int(payload["expected_dataset_category_count"]),
        minimum_mcp_scenario_count=int(payload["minimum_mcp_scenario_count"]),
        require_quality_gate_passed=bool(payload["require_quality_gate_passed"]),
        require_all_offline_controls=bool(payload["require_all_offline_controls"]),
        require_main_environment_pip_check=bool(
            payload["require_main_environment_pip_check"]
        ),
        require_evaluation_environment_pip_check=bool(
            payload["require_evaluation_environment_pip_check"]
        ),
        require_git_diff_check=bool(payload["require_git_diff_check"]),
        required_suite_codes=tuple(
            str(item) for item in payload["required_suite_codes"]
        ),
        required_reports=tuple(str(item) for item in payload["required_reports"]),
        forbidden_environment_usage=tuple(
            str(item) for item in payload["forbidden_environment_usage"]
        ),
    )


def discover_agentic_rag_tests(
    project_root: Path,
) -> tuple[Path, ...]:
    """Localiza os testes unitários Agentic RAG."""

    unit_root = project_root / "tests" / "unit"

    return tuple(sorted(unit_root.glob("test_agentic_rag_*.py")))


def discover_mcp_existing_tests(
    project_root: Path,
) -> tuple[Path, ...]:
    """Retorna os testes MCP existentes da regressão."""

    relative_paths = (
        "tests/unit/test_mcp_server.py",
        "tests/unit/test_mcp_advanced_security.py",
        "tests/unit/test_mcp_communication_tools.py",
        "tests/unit/test_tool_calling_core.py",
        "tests/unit/test_formal_rag_tool.py",
        "tests/unit/test_formal_financial_tool.py",
        "tests/unit/test_formal_report_preparation_tool.py",
    )

    paths = tuple(project_root / relative_path for relative_path in relative_paths)

    missing = [str(path) for path in paths if not path.exists()]

    if missing:
        raise FileNotFoundError("Testes MCP ausentes: " + ", ".join(missing))

    return paths


def discover_week4_ruff_paths(
    project_root: Path,
) -> tuple[Path, ...]:
    """Localiza arquivos Python da Semana 4."""

    paths: list[Path] = [
        project_root / "src" / "evaluation" / "agentic_benchmark",
        project_root / "src" / "evaluation" / "mcp_simulated",
        project_root / "src" / "evaluation" / "offline_dashboard",
        project_root / "src" / "evaluation" / "final_regression",
        project_root / "scripts" / "evaluation" / "run_agentic_rag_offline_gate.py",
        project_root / "scripts" / "evaluation" / "validate_offline_dashboard.py",
        project_root / "scripts" / "evaluation" / "run_week4_final_regression.py",
        project_root / "tests" / "evaluations",
        project_root / "tests" / "unit" / "test_mcp_server.py",
    ]

    return tuple(path for path in paths if path.exists())


def build_suite_specs(
    project_root: Path,
    *,
    evaluation_python: Path,
) -> tuple[RegressionSuiteSpec, ...]:
    """Cria os comandos da regressão."""

    python = Path(sys.executable)

    agentic_tests = discover_agentic_rag_tests(project_root)

    if not agentic_tests:
        raise FileNotFoundError("Nenhum teste Agentic RAG encontrado.")

    mcp_tests = discover_mcp_existing_tests(project_root)

    ruff_paths = discover_week4_ruff_paths(project_root)

    compile_targets = (
        project_root / "src" / "evaluation" / "agentic_benchmark",
        project_root / "src" / "evaluation" / "mcp_simulated",
        project_root / "src" / "evaluation" / "offline_dashboard",
        project_root / "src" / "evaluation" / "final_regression",
        project_root / "scripts" / "evaluation" / "run_agentic_rag_offline_gate.py",
        project_root / "scripts" / "evaluation" / "validate_offline_dashboard.py",
        project_root / "scripts" / "evaluation" / "run_week4_final_regression.py",
    )

    return (
        RegressionSuiteSpec(
            code="python_compile",
            description=("Compilação dos módulos Python da Semana 4"),
            command=(
                str(python),
                "-m",
                "compileall",
                "-q",
                *(str(path) for path in compile_targets),
            ),
        ),
        RegressionSuiteSpec(
            code="ruff_week4",
            description=("Ruff nos módulos e testes da Semana 4"),
            command=(
                str(python),
                "-m",
                "ruff",
                "check",
                *(str(path) for path in ruff_paths),
            ),
        ),
        RegressionSuiteSpec(
            code="evaluation_tests",
            description=("Suíte de testes de avaliação"),
            command=(
                str(python),
                "-m",
                "pytest",
                "-q",
                str(project_root / "tests" / "evaluations"),
            ),
        ),
        RegressionSuiteSpec(
            code="agentic_rag_regression",
            description=("Regressão unitária do Agentic RAG"),
            command=(
                str(python),
                "-m",
                "pytest",
                "-q",
                *(str(path) for path in agentic_tests),
            ),
        ),
        RegressionSuiteSpec(
            code="mcp_existing_regression",
            description=("Regressão MCP existente"),
            command=(
                str(python),
                "-m",
                "pytest",
                "-q",
                *(str(path) for path in mcp_tests),
            ),
        ),
        RegressionSuiteSpec(
            code="quality_gate",
            description=("Quality Gate Agentic RAG offline"),
            command=(
                str(python),
                str(
                    project_root
                    / "scripts"
                    / "evaluation"
                    / "run_agentic_rag_offline_gate.py"
                ),
                "--dataset",
                str(
                    project_root
                    / "tests"
                    / "evaluations"
                    / "datasets"
                    / "agentic_rag_v1.jsonl"
                ),
                "--policy",
                str(
                    project_root
                    / "config"
                    / "evaluation"
                    / "agentic_rag_quality_gate.json"
                ),
                "--output-dir",
                str(project_root / "artifacts" / "evaluations" / "agentic_benchmark"),
                "--expected-case-count",
                "24",
                "--expected-category-count",
                "12",
            ),
        ),
        RegressionSuiteSpec(
            code="dashboard_validator",
            description=("Validação dos relatórios do dashboard offline"),
            command=(
                str(python),
                str(
                    project_root
                    / "scripts"
                    / "evaluation"
                    / "validate_offline_dashboard.py"
                ),
            ),
        ),
        RegressionSuiteSpec(
            code="main_pip_check",
            description=("Integridade do ambiente principal"),
            command=(
                str(python),
                "-m",
                "pip",
                "check",
            ),
        ),
        RegressionSuiteSpec(
            code="evaluation_pip_check",
            description=("Integridade do ambiente de avaliação isolado"),
            command=(
                str(evaluation_python),
                "-m",
                "pip",
                "check",
            ),
        ),
        RegressionSuiteSpec(
            code="git_diff_check",
            description=("Validação de whitespace do Git"),
            command=(
                "git",
                "diff",
                "--check",
            ),
        ),
    )


def build_offline_environment() -> dict[str, str]:
    """Cria ambiente sem credenciais de serviços externos."""

    environment = dict(os.environ)

    environment.update(
        {
            "PYTHONUTF8": "1",
            "INNA_OFFLINE_EVALUATION": "true",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "VERTEX_PROJECT_ID": "",
            "DATABASE_URL": OFFLINE_DATABASE_URL,
            "NEON_DATABASE_URL": OFFLINE_DATABASE_URL,
        }
    )

    return environment


def _tail(
    value: str,
    *,
    maximum_lines: int = 80,
) -> str:
    lines = value.splitlines()

    return "\n".join(lines[-maximum_lines:])


def _pytest_passed_count(
    output: str,
) -> int | None:
    matches = re.findall(
        r"(\d+)\s+passed",
        output,
    )

    if not matches:
        return None

    return int(matches[-1])


def execute_suite(
    spec: RegressionSuiteSpec,
    *,
    project_root: Path,
    environment: Mapping[str, str],
) -> RegressionSuiteResult:
    """Executa uma suíte e registra seu resultado."""

    command_text = subprocess.list2cmdline(list(spec.command))

    print("")
    print("=" * 72)
    print(f"SUITE={spec.code}")
    print(f"DESCRIPTION={spec.description}")
    print(f"COMMAND={command_text}")
    print("=" * 72)

    started = time.perf_counter()

    try:
        completed = subprocess.run(
            list(spec.command),
            cwd=project_root,
            env=dict(environment),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=spec.timeout_seconds,
            check=False,
        )

        return_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr

    except subprocess.TimeoutExpired as exc:
        return_code = 124

        stdout = (
            exc.stdout
            if isinstance(
                exc.stdout,
                str,
            )
            else ""
        )

        stderr = (
            exc.stderr
            if isinstance(
                exc.stderr,
                str,
            )
            else ""
        )

        stderr = stderr + "\nSUITE_TIMEOUT=True"

    duration = time.perf_counter() - started

    if stdout:
        print(stdout.rstrip())

    if stderr:
        print(stderr.rstrip())

    combined_output = stdout + "\n" + stderr

    result = RegressionSuiteResult(
        code=spec.code,
        description=spec.description,
        command=spec.command,
        return_code=return_code,
        passed=return_code == 0,
        duration_seconds=round(
            duration,
            3,
        ),
        pytest_passed_count=(_pytest_passed_count(combined_output)),
        stdout_tail=_tail(stdout),
        stderr_tail=_tail(stderr),
    )

    print(
        f"SUITE_RESULT={spec.code} "
        f"PASSED={result.passed} "
        f"RETURN_CODE={result.return_code} "
        f"DURATION_SECONDS={result.duration_seconds} "
        "PYTEST_PASSED_COUNT="
        f"{result.pytest_passed_count}"
    )

    return result


def _load_json(
    path: Path,
) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))

    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError(f"Relatório inválido: {path}")

    return payload


def _quality_check_actual(
    quality_gate: Mapping[str, Any],
    code: str,
) -> Any:
    checks = quality_gate.get(
        "checks",
        (),
    )

    if not isinstance(
        checks,
        Sequence,
    ) or isinstance(
        checks,
        (
            str,
            bytes,
        ),
    ):
        return None

    for check in checks:
        if not isinstance(
            check,
            Mapping,
        ):
            continue

        check_code = check.get("code") or check.get("name") or check.get("check")

        if str(check_code) == code:
            return check.get("actual")

    return None


def validate_reports(
    project_root: Path,
    policy: FinalRegressionPolicy,
) -> tuple[
    dict[str, bool],
    dict[str, Any],
]:
    """Valida os relatórios produzidos pela Semana 4."""

    configured_report_paths = tuple(
        project_root / relative_path
        for relative_path in policy.required_reports
    )

    reports_by_name = {
        path.name: path
        for path in configured_report_paths
    }

    expected_report_names = {
        "benchmark": "offline_benchmark_latest.json",
        "quality_gate": "offline_quality_gate_latest.json",
        "quality_summary": "offline_quality_summary_latest.json",
        "mcp_e2e": "mcp_simulated_e2e_latest.json",
    }

    missing_contract_reports = tuple(
        report_name
        for report_name in expected_report_names.values()
        if report_name not in reports_by_name
    )

    if missing_contract_reports:
        raise ValueError(
            "Pol??tica de regress??o sem relat??rios obrigat??rios: "
            + ", ".join(missing_contract_reports)
        )

    report_paths = {
        report_key: reports_by_name[report_name]
        for report_key, report_name in expected_report_names.items()
    }

    reports_exist = all(
        report_path.exists()
        for report_path in report_paths.values()
    )

    if not reports_exist:
        missing_reports = tuple(
            str(report_path)
            for report_path in report_paths.values()
            if not report_path.exists()
        )

        raise FileNotFoundError(
            "Relat??rios obrigat??rios da regress??o ausentes: "
            + ", ".join(missing_reports)
        )

    benchmark = _load_json(report_paths["benchmark"])

    quality_gate = _load_json(report_paths["quality_gate"])

    quality_summary = _load_json(report_paths["quality_summary"])

    mcp_e2e = _load_json(report_paths["mcp_e2e"])

    dataset_version = str(
        quality_gate.get(
            "dataset_version",
            benchmark.get(
                "dataset_version",
                "",
            ),
        )
    )

    dataset_case_count = _quality_check_actual(
        quality_gate,
        "dataset_case_count",
    )

    dataset_category_count = _quality_check_actual(
        quality_gate,
        "dataset_category_count",
    )

    quality_gate_passed = bool(
        quality_gate.get(
            "passed",
            quality_summary.get(
                "quality_gate_passed",
                False,
            ),
        )
    )

    scenarios = mcp_e2e.get(
        "scenarios",
        {},
    )

    if not isinstance(
        scenarios,
        Mapping,
    ):
        scenarios = {}

    mcp_scenario_count = int(
        mcp_e2e.get(
            "scenario_count",
            len(scenarios),
        )
    )

    offline_control_values = {
        "offline": (
            mcp_e2e.get(
                "offline",
                False,
            )
            is True
        ),
        "network_server_not_started": (
            mcp_e2e.get(
                "network_server_started",
                True,
            )
            is False
        ),
        "http_not_executed": (
            mcp_e2e.get(
                "http_requests_executed",
                True,
            )
            is False
        ),
        "database_not_connected": (
            mcp_e2e.get(
                "database_connections_executed",
                True,
            )
            is False
        ),
        "gemini_not_called": (
            mcp_e2e.get(
                "gemini_api_called",
                True,
            )
            is False
        ),
        "live_rag_not_called": (
            mcp_e2e.get(
                "live_rag_called",
                True,
            )
            is False
        ),
        "live_mcp_not_called": (
            mcp_e2e.get(
                "live_mcp_called",
                True,
            )
            is False
        ),
    }

    all_offline_controls = all(offline_control_values.values())

    from src.interfaces.avaliacao.offline_dashboard import (
        OfflineDashboardPaths,
        build_overview,
        load_offline_dashboard_snapshot,
        security_rows,
    )

    snapshot = load_offline_dashboard_snapshot(
        project_root,
        strict=True,
        paths=OfflineDashboardPaths(
            benchmark=report_paths["benchmark"],
            quality_gate=report_paths["quality_gate"],
            quality_summary=report_paths["quality_summary"],
            mcp_e2e=report_paths["mcp_e2e"],
        ),
    )

    overview = build_overview(snapshot)

    dashboard_security = security_rows(snapshot)

    dashboard_security_passed = all(row["Aprovado"] for row in dashboard_security)

    validations = {
        "required_reports_exist": reports_exist,
        "dataset_version_matches": (dataset_version == policy.expected_dataset_version),
        "dataset_case_count_matches": (
            int(dataset_case_count) == policy.expected_dataset_case_count
        ),
        "dataset_category_count_matches": (
            int(dataset_category_count) == policy.expected_dataset_category_count
        ),
        "quality_gate_passed": (
            quality_gate_passed if policy.require_quality_gate_passed else True
        ),
        "mcp_scenario_count_valid": (
            mcp_scenario_count >= policy.minimum_mcp_scenario_count
        ),
        "offline_controls_passed": (
            all_offline_controls if policy.require_all_offline_controls else True
        ),
        "dashboard_case_count_matches": (
            int(overview["case_count"]) == policy.expected_dataset_case_count
        ),
        "dashboard_category_count_matches": (
            int(overview["category_count"]) == policy.expected_dataset_category_count
        ),
        "dashboard_quality_gate_passed": bool(overview["quality_gate_passed"]),
        "dashboard_security_passed": (dashboard_security_passed),
    }

    facts = {
        "dataset_version": dataset_version,
        "dataset_case_count": int(dataset_case_count),
        "dataset_category_count": int(dataset_category_count),
        "quality_gate_passed": (quality_gate_passed),
        "quality_gate_check_count": int(
            quality_gate.get(
                "total_checks",
                len(
                    quality_gate.get(
                        "checks",
                        (),
                    )
                ),
            )
        ),
        "mcp_scenario_count": (mcp_scenario_count),
        "mcp_statuses": {
            str(name): (
                payload.get(
                    "status",
                    "unknown",
                )
                if isinstance(
                    payload,
                    Mapping,
                )
                else "unknown"
            )
            for name, payload in scenarios.items()
        },
        "offline_controls": (offline_control_values),
        "dashboard_case_count": int(overview["case_count"]),
        "dashboard_category_count": int(overview["category_count"]),
    }

    return validations, facts


def write_report(
    report: FinalRegressionReport,
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    """Grava JSON e texto, com versões latest e timestamped."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    json_timestamped = output_dir / f"week4_final_regression_{stamp}.json"

    json_latest = output_dir / "week4_final_regression_latest.json"

    text_timestamped = output_dir / f"week4_final_regression_{stamp}.txt"

    text_latest = output_dir / "week4_final_regression_latest.txt"

    payload = asdict(report)

    serialized_json = (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    text_lines = [
        "WEEK 4 FINAL REGRESSION",
        "=" * 72,
        f"PHASE={report.phase}",
        (f"POLICY_VERSION={report.policy_version}"),
        (f"GENERATED_AT={report.generated_at}"),
        f"OFFLINE={report.offline}",
        (f"OVERALL_PASSED={report.overall_passed}"),
        (f"SUITE_COUNT={report.suite_count}"),
        (f"PASSED_SUITE_COUNT={report.passed_suite_count}"),
        ("FAILED_SUITE_CODES=" + ",".join(report.failed_suite_codes)),
        "",
        "SUITES",
        "-" * 72,
    ]

    for suite in report.suites:
        text_lines.append(
            f"{suite.code}: "
            f"PASSED={suite.passed} "
            f"RETURN_CODE={suite.return_code} "
            "PYTEST_PASSED_COUNT="
            f"{suite.pytest_passed_count} "
            "DURATION_SECONDS="
            f"{suite.duration_seconds}"
        )

    text_lines.extend(
        [
            "",
            "VALIDATIONS",
            "-" * 72,
        ]
    )

    for name, passed in sorted(report.validations.items()):
        text_lines.append(f"{name}={passed}")

    text_lines.extend(
        [
            "",
            "NOTES",
            "-" * 72,
            *report.notes,
            "",
            ("WEEK4_FINAL_REGRESSION=" + ("OK" if report.overall_passed else "FAILED")),
        ]
    )

    serialized_text = "\n".join(text_lines) + "\n"

    for path in (
        json_timestamped,
        json_latest,
    ):
        path.write_text(
            serialized_json,
            encoding="utf-8",
            newline="\n",
        )

    for path in (
        text_timestamped,
        text_latest,
    ):
        path.write_text(
            serialized_text,
            encoding="utf-8",
            newline="\n",
        )

    return (
        json_timestamped,
        json_latest,
        text_timestamped,
        text_latest,
    )


def run_final_regression(
    project_root: Path,
    *,
    policy_path: Path,
    output_dir: Path,
    evaluation_python: Path,
) -> FinalRegressionReport:
    """Executa toda a regressão final."""

    policy = load_policy(policy_path)

    if not policy.offline:
        raise RuntimeError("A política precisa ser offline.")

    specs = build_suite_specs(
        project_root,
        evaluation_python=evaluation_python,
    )

    suite_codes = {spec.code for spec in specs}

    missing_suite_codes = set(policy.required_suite_codes) - suite_codes

    if missing_suite_codes:
        raise RuntimeError(
            "Suítes obrigatórias ausentes: " + ", ".join(sorted(missing_suite_codes))
        )

    environment = build_offline_environment()

    results = tuple(
        execute_suite(
            spec,
            project_root=project_root,
            environment=environment,
        )
        for spec in specs
    )

    validations, facts = validate_reports(
        project_root,
        policy,
    )

    suite_map = {result.code: result for result in results}

    policy_specific_validations = {
        "main_pip_check_required": (
            suite_map["main_pip_check"].passed
            if policy.require_main_environment_pip_check
            else True
        ),
        "evaluation_pip_check_required": (
            suite_map["evaluation_pip_check"].passed
            if policy.require_evaluation_environment_pip_check
            else True
        ),
        "git_diff_check_required": (
            suite_map["git_diff_check"].passed
            if policy.require_git_diff_check
            else True
        ),
    }

    validations.update(policy_specific_validations)

    failed_suite_codes = tuple(result.code for result in results if not result.passed)

    all_validations_passed = all(validations.values())

    overall_passed = not failed_suite_codes and all_validations_passed

    report = FinalRegressionReport(
        phase=policy.phase,
        policy_version=(policy.policy_version),
        generated_at=datetime.now(UTC).isoformat(),
        offline=True,
        overall_passed=overall_passed,
        suite_count=len(results),
        passed_suite_count=sum(result.passed for result in results),
        failed_suite_codes=(failed_suite_codes),
        suites=results,
        validations=validations,
        facts=facts,
        notes=(
            ("As contagens de pytest pertencem a suítes independentes."),
            (
                "As contagens não são somadas porque "
                "alguns testes podem aparecer em mais "
                "de uma regressão."
            ),
            ("Nenhuma credencial externa foi disponibilizada aos subprocessos."),
        ),
    )

    paths = write_report(
        report,
        output_dir=output_dir,
    )

    print("")
    print("=" * 72)
    print("FINAL REGRESSION REPORT")
    print("=" * 72)

    print(f"FINAL_SUITE_COUNT={report.suite_count}")

    print(f"FINAL_PASSED_SUITE_COUNT={report.passed_suite_count}")

    print("FINAL_FAILED_SUITE_CODES=" + ",".join(report.failed_suite_codes))

    for name, passed in sorted(report.validations.items()):
        print(f"FINAL_VALIDATION={name} PASSED={passed}")

    print(f"FINAL_DATASET_CASE_COUNT={report.facts['dataset_case_count']}")

    print(f"FINAL_DATASET_CATEGORY_COUNT={report.facts['dataset_category_count']}")

    print(f"FINAL_MCP_SCENARIO_COUNT={report.facts['mcp_scenario_count']}")

    print(f"FINAL_QUALITY_GATE_PASSED={report.facts['quality_gate_passed']}")

    print(f"FINAL_OVERALL_PASSED={report.overall_passed}")

    print(f"FINAL_JSON_REPORT={paths[0]}")

    print(f"FINAL_LATEST_JSON_REPORT={paths[1]}")

    print(f"FINAL_TEXT_REPORT={paths[2]}")

    print(f"FINAL_LATEST_TEXT_REPORT={paths[3]}")

    print("LIVE_SERVICES_USED=False")
    print("SECRETS_USED=False")

    return report
