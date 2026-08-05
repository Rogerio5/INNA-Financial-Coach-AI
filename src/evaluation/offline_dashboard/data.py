"""Leitura e normalização dos relatórios offline da avaliação."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class OfflineDashboardDataError(RuntimeError):
    """Erro ao carregar os relatórios do dashboard."""


@dataclass(frozen=True, slots=True)
class OfflineDashboardPaths:
    """Caminhos dos relatórios exibidos pelo dashboard."""

    benchmark: Path
    quality_gate: Path
    quality_summary: Path
    mcp_e2e: Path


@dataclass(frozen=True, slots=True)
class OfflineDashboardSnapshot:
    """Snapshot imutável dos relatórios offline."""

    loaded_at: str
    paths: OfflineDashboardPaths
    benchmark: dict[str, Any]
    quality_gate: dict[str, Any]
    quality_summary: dict[str, Any]
    mcp_e2e: dict[str, Any]
    errors: tuple[str, ...]


def default_dashboard_paths(
    project_root: Path,
) -> OfflineDashboardPaths:
    """Retorna os caminhos oficiais dos relatórios latest."""

    return OfflineDashboardPaths(
        benchmark=(
            project_root
            / "artifacts"
            / "evaluations"
            / "agentic_benchmark"
            / "offline_benchmark_latest.json"
        ),
        quality_gate=(
            project_root
            / "artifacts"
            / "evaluations"
            / "agentic_benchmark"
            / "offline_quality_gate_latest.json"
        ),
        quality_summary=(
            project_root
            / "artifacts"
            / "evaluations"
            / "agentic_benchmark"
            / "offline_quality_summary_latest.json"
        ),
        mcp_e2e=(
            project_root
            / "artifacts"
            / "evaluations"
            / "mcp_simulated_e2e"
            / "mcp_simulated_e2e_latest.json"
        ),
    )


def _load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise OfflineDashboardDataError(
            f"Relatório não encontrado: {path}"
        )

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )
    except json.JSONDecodeError as exc:
        raise OfflineDashboardDataError(
            f"JSON inválido em {path}: {exc}"
        ) from exc

    if not isinstance(
        payload,
        dict,
    ):
        raise OfflineDashboardDataError(
            f"O relatório precisa ser um objeto JSON: {path}"
        )

    return payload


def load_offline_dashboard_snapshot(
    project_root: Path,
    *,
    strict: bool = True,
    paths: OfflineDashboardPaths | None = None,
) -> OfflineDashboardSnapshot:
    """Carrega os quatro relatórios utilizados pelo dashboard."""

    resolved_paths = (
        paths
        or default_dashboard_paths(
            project_root
        )
    )

    loaded: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    sources = {
        "benchmark": resolved_paths.benchmark,
        "quality_gate": resolved_paths.quality_gate,
        "quality_summary": resolved_paths.quality_summary,
        "mcp_e2e": resolved_paths.mcp_e2e,
    }

    for name, path in sources.items():
        try:
            loaded[name] = _load_json(
                path
            )
        except OfflineDashboardDataError as exc:
            if strict:
                raise

            loaded[name] = {}
            errors.append(
                str(exc)
            )

    return OfflineDashboardSnapshot(
        loaded_at=datetime.now(
            UTC
        ).isoformat(),
        paths=resolved_paths,
        benchmark=loaded["benchmark"],
        quality_gate=loaded["quality_gate"],
        quality_summary=loaded[
            "quality_summary"
        ],
        mcp_e2e=loaded["mcp_e2e"],
        errors=tuple(errors),
    )


def _value_at(
    payload: Mapping[str, Any],
    path: str,
) -> Any:
    current: Any = payload

    for part in path.split("."):
        if not isinstance(
            current,
            Mapping,
        ):
            return None

        if part not in current:
            return None

        current = current[part]

    return current


def _first_value(
    payloads: Sequence[Mapping[str, Any]],
    paths: Sequence[str],
    *,
    default: Any = None,
) -> Any:
    for payload in payloads:
        for path in paths:
            value = _value_at(
                payload,
                path,
            )

            if value is not None:
                return value

    return default


def _as_float(
    value: Any,
    *,
    default: float = 0.0,
) -> float:
    if isinstance(
        value,
        bool,
    ):
        return float(value)

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _as_int(
    value: Any,
    *,
    default: int = 0,
) -> int:
    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _count_value(
    value: Any,
) -> int:
    if isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            str,
            bytes,
        ),
    ):
        return len(value)

    return _as_int(value)


def _quality_check_actual(
    payloads: Sequence[Mapping[str, Any]],
    check_name: str,
    *,
    default: Any = None,
) -> Any:
    """Localiza o valor atual de um critério em schemas variados."""

    target = check_name.casefold()

    name_keys = (
        "name",
        "check",
        "check_name",
        "metric",
        "metric_name",
        "criterion",
        "criterion_name",
        "id",
        "key",
    )

    value_keys = (
        "actual",
        "value",
        "observed",
        "measured",
        "current",
        "result",
        "count",
    )

    def extract_candidate(
        candidate: Any,
    ) -> Any:
        if not isinstance(
            candidate,
            Mapping,
        ):
            return candidate

        for nested_key in (
            "value",
            "actual",
            "count",
            "result",
        ):
            if (
                nested_key in candidate
                and candidate[nested_key]
                is not None
            ):
                return candidate[nested_key]

        return candidate

    def walk(
        value: Any,
    ) -> tuple[bool, Any]:
        if isinstance(
            value,
            Mapping,
        ):
            declared_names = {
                str(value[key]).casefold()
                for key in name_keys
                if (
                    key in value
                    and value[key] is not None
                )
            }

            string_values = {
                str(item).casefold()
                for item in value.values()
                if isinstance(
                    item,
                    str,
                )
            }

            matches_target = (
                target in declared_names
                or target in string_values
                or target
                in {
                    str(key).casefold()
                    for key in value
                }
            )

            if matches_target:
                for key in value_keys:
                    if (
                        key in value
                        and value[key] is not None
                    ):
                        return (
                            True,
                            extract_candidate(
                                value[key]
                            ),
                        )

                if check_name in value:
                    return (
                        True,
                        extract_candidate(
                            value[check_name]
                        ),
                    )

            for nested in value.values():
                found, actual = walk(
                    nested
                )

                if found:
                    return found, actual

        elif isinstance(
            value,
            Sequence,
        ) and not isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):
            for nested in value:
                found, actual = walk(
                    nested
                )

                if found:
                    return found, actual

        return False, default

    for payload in payloads:
        found, actual = walk(
            payload
        )

        if found:
            return actual

    return default


def _profile_mapping(
    report: Mapping[str, Any],
    profile: str,
) -> Mapping[str, Any]:
    candidates = (
        f"{profile}_summary",
        f"summaries.{profile}",
        f"profiles.{profile}",
        f"results.{profile}.summary",
        f"benchmark.{profile}",
    )

    for path in candidates:
        value = _value_at(
            report,
            path,
        )

        if isinstance(
            value,
            Mapping,
        ):
            return value

    return {}


def build_overview(
    snapshot: OfflineDashboardSnapshot,
) -> dict[str, Any]:
    """Constrói os principais indicadores do dashboard."""

    benchmark = snapshot.benchmark
    quality_gate = snapshot.quality_gate
    quality_summary = snapshot.quality_summary
    mcp_e2e = snapshot.mcp_e2e

    legacy = _profile_mapping(
        benchmark,
        "legacy",
    )

    agentic = _profile_mapping(
        benchmark,
        "agentic",
    )

    comparison = _first_value(
        (benchmark,),
        (
            "comparison",
            "summary.comparison",
            "benchmark_comparison",
        ),
        default={},
    )

    if not isinstance(
        comparison,
        Mapping,
    ):
        comparison = {}

    quality_gate_passed = _first_value(
        (
            quality_gate,
            quality_summary,
        ),
        (
            "passed",
            "quality_gate_passed",
            "result.passed",
            "gate.passed",
        ),
        default=False,
    )

    gate_checks = _first_value(
        (
            quality_gate,
            quality_summary,
        ),
        (
            "checks",
            "quality_checks",
            "gate.checks",
        ),
        default=[],
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

    category_count_value = _first_value(
        (
            benchmark,
            quality_summary,
        ),
        (
            "category_count",
            "dataset_category_count",
            "dataset.category_count",
        ),
        default=None,
    )

    if category_count_value is None:
        category_count_value = (
            _quality_check_actual(
                (
                    quality_gate,
                    quality_summary,
                ),
                "dataset_category_count",
                default=None,
            )
        )

    if category_count_value is None:
        category_groups = _first_value(
            (benchmark,),
            (
                "category_summaries",
                "categories",
                "per_category",
                "comparison.categories",
            ),
            default=(),
        )

        category_count_value = _count_value(
            category_groups
        )

    return {
        "dataset_version": _first_value(
            (
                benchmark,
                quality_summary,
            ),
            (
                "dataset_version",
                "dataset.version",
                "benchmark.dataset_version",
            ),
            default="unknown",
        ),
        "case_count": _as_int(
            _first_value(
                (
                    benchmark,
                    quality_summary,
                ),
                (
                    "case_count",
                    "dataset_case_count",
                    "total_cases",
                    "dataset.case_count",
                ),
                default=0,
            )
        ),
        "category_count": _as_int(
            category_count_value
        ),
        "legacy_pass_rate": _as_float(
            _first_value(
                (legacy,),
                (
                    "pass_rate",
                    "passed_rate",
                ),
                default=0,
            )
        ),
        "agentic_pass_rate": _as_float(
            _first_value(
                (agentic,),
                (
                    "pass_rate",
                    "passed_rate",
                ),
                default=0,
            )
        ),
        "legacy_average_score": _as_float(
            _first_value(
                (legacy,),
                (
                    "average_score",
                    "avg_score",
                    "score",
                ),
                default=0,
            )
        ),
        "agentic_average_score": _as_float(
            _first_value(
                (agentic,),
                (
                    "average_score",
                    "avg_score",
                    "score",
                ),
                default=0,
            )
        ),
        "score_delta": _as_float(
            _first_value(
                (
                    comparison,
                    benchmark,
                    quality_summary,
                ),
                (
                    "average_score_delta",
                    "score_delta",
                    "comparison.score_delta",
                ),
                default=0,
            )
        ),
        "latency_delta_ms": _as_float(
            _first_value(
                (
                    comparison,
                    benchmark,
                    quality_summary,
                ),
                (
                    "latency_delta_ms",
                    "average_latency_delta_ms",
                    "latency_delta",
                    "comparison.latency_delta_ms",
                ),
                default=0,
            )
        ),
        "improvement_count": _count_value(
            _first_value(
                (
                    comparison,
                    benchmark,
                ),
                (
                    "improvements",
                    "improvement_count",
                    "comparison.improvements",
                ),
                default=0,
            )
        ),
        "regression_count": _count_value(
            _first_value(
                (
                    comparison,
                    benchmark,
                    quality_summary,
                ),
                (
                    "regressions",
                    "regression_count",
                    "comparison.regressions",
                ),
                default=0,
            )
        ),
        "quality_gate_passed": bool(
            quality_gate_passed
        ),
        "quality_check_count": _count_value(
            gate_checks
        ),
        "mcp_scenario_count": _as_int(
            mcp_e2e.get(
                "scenario_count",
                len(scenarios),
            )
        ),
        "offline": bool(
            mcp_e2e.get(
                "offline",
                False,
            )
        ),
    }


def benchmark_profile_rows(
    snapshot: OfflineDashboardSnapshot,
) -> list[dict[str, Any]]:
    """Retorna uma linha por perfil do benchmark."""

    rows: list[dict[str, Any]] = []

    for profile in (
        "legacy",
        "agentic",
    ):
        payload = _profile_mapping(
            snapshot.benchmark,
            profile,
        )

        rows.append(
            {
                "Perfil": profile.title(),
                "Casos": _as_int(
                    _first_value(
                        (payload,),
                        (
                            "total_cases",
                            "case_count",
                            "cases",
                        ),
                        default=0,
                    )
                ),
                "Aprovados": _as_int(
                    _first_value(
                        (payload,),
                        (
                            "passed_cases",
                            "pass_count",
                            "passed",
                        ),
                        default=0,
                    )
                ),
                "Taxa de aprovação": _as_float(
                    _first_value(
                        (payload,),
                        (
                            "pass_rate",
                            "passed_rate",
                        ),
                        default=0,
                    )
                ),
                "Pontuação média": _as_float(
                    _first_value(
                        (payload,),
                        (
                            "average_score",
                            "avg_score",
                            "score",
                        ),
                        default=0,
                    )
                ),
                "Latência média (ms)": _as_float(
                    _first_value(
                        (payload,),
                        (
                            "average_latency_ms",
                            "avg_latency_ms",
                            "latency_ms",
                        ),
                        default=0,
                    )
                ),
            }
        )

    return rows


def quality_gate_rows(
    snapshot: OfflineDashboardSnapshot,
) -> list[dict[str, Any]]:
    """Normaliza os critérios do Quality Gate."""

    checks = _first_value(
        (
            snapshot.quality_gate,
            snapshot.quality_summary,
        ),
        (
            "checks",
            "quality_checks",
            "gate.checks",
        ),
        default=[],
    )

    rows: list[dict[str, Any]] = []

    if isinstance(
        checks,
        Mapping,
    ):
        iterable = []

        for name, value in checks.items():
            if isinstance(
                value,
                Mapping,
            ):
                item = dict(value)
                item.setdefault(
                    "name",
                    name,
                )
            else:
                item = {
                    "name": name,
                    "actual": value,
                }

            iterable.append(item)

    elif isinstance(
        checks,
        Sequence,
    ) and not isinstance(
        checks,
        (
            str,
            bytes,
        ),
    ):
        iterable = list(checks)

    else:
        iterable = []

    for index, item in enumerate(
        iterable,
        start=1,
    ):
        if not isinstance(
            item,
            Mapping,
        ):
            continue

        rows.append(
            {
                "Critério": item.get(
                    "name",
                    item.get(
                        "check",
                        f"check_{index}",
                    ),
                ),
                "Atual": item.get(
                    "actual",
                    item.get(
                        "value",
                        "",
                    ),
                ),
                "Esperado": item.get(
                    "expected",
                    item.get(
                        "threshold",
                        "",
                    ),
                ),
                "Aprovado": bool(
                    item.get(
                        "passed",
                        False,
                    )
                ),
                "Bloqueante": bool(
                    item.get(
                        "blocking",
                        True,
                    )
                ),
            }
        )

    return rows


def mcp_scenario_rows(
    snapshot: OfflineDashboardSnapshot,
) -> list[dict[str, Any]]:
    """Normaliza os oito cenários do relatório MCP."""

    scenarios = snapshot.mcp_e2e.get(
        "scenarios",
        {},
    )

    if not isinstance(
        scenarios,
        Mapping,
    ):
        return []

    rows: list[dict[str, Any]] = []

    for name, payload in scenarios.items():
        if not isinstance(
            payload,
            Mapping,
        ):
            continue

        output = payload.get(
            "output",
            {},
        )

        if not isinstance(
            output,
            Mapping,
        ):
            output = {}

        rows.append(
            {
                "Cenário": str(name),
                "Status": payload.get(
                    "status",
                    "unknown",
                ),
                "Código de erro": payload.get(
                    "error_code",
                    "",
                ),
                "user_id": output.get(
                    "user_id",
                    "",
                ),
                "session_id": output.get(
                    "session_id",
                    "",
                ),
                "trace_id": output.get(
                    "trace_id",
                    "",
                ),
            }
        )

    return rows


def report_status_rows(
    snapshot: OfflineDashboardSnapshot,
) -> list[dict[str, Any]]:
    """Retorna a situação dos arquivos utilizados."""

    sources = (
        (
            "Benchmark",
            snapshot.paths.benchmark,
            snapshot.benchmark,
        ),
        (
            "Quality Gate",
            snapshot.paths.quality_gate,
            snapshot.quality_gate,
        ),
        (
            "Resumo",
            snapshot.paths.quality_summary,
            snapshot.quality_summary,
        ),
        (
            "MCP E2E",
            snapshot.paths.mcp_e2e,
            snapshot.mcp_e2e,
        ),
    )

    return [
        {
            "Relatório": name,
            "Existe": path.exists(),
            "Carregado": bool(payload),
            "Caminho": str(path),
        }
        for name, path, payload in sources
    ]


def security_rows(
    snapshot: OfflineDashboardSnapshot,
) -> list[dict[str, Any]]:
    """Retorna as garantias offline registradas no MCP."""

    payload = snapshot.mcp_e2e

    checks = (
        (
            "Execução offline",
            payload.get(
                "offline",
                False,
            )
            is True,
        ),
        (
            "Servidor de rede não iniciado",
            payload.get(
                "network_server_started",
                True,
            )
            is False,
        ),
        (
            "Nenhuma requisição HTTP",
            payload.get(
                "http_requests_executed",
                True,
            )
            is False,
        ),
        (
            "Nenhuma conexão de banco",
            payload.get(
                "database_connections_executed",
                True,
            )
            is False,
        ),
        (
            "Gemini não chamado",
            payload.get(
                "gemini_api_called",
                True,
            )
            is False,
        ),
        (
            "RAG real não chamado",
            payload.get(
                "live_rag_called",
                True,
            )
            is False,
        ),
        (
            "MCP de rede não chamado",
            payload.get(
                "live_mcp_called",
                True,
            )
            is False,
        ),
    )

    return [
        {
            "Controle": name,
            "Aprovado": passed,
        }
        for name, passed in checks
    ]
