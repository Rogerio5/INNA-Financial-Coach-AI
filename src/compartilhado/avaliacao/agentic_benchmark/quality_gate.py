"""Quality Gate determinístico do benchmark Agentic RAG."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .benchmark_runner import (
    BenchmarkProfile,
    OfflineBenchmarkResult,
)


@dataclass(frozen=True, slots=True)
class QualityGatePolicy:
    """Política versionada para aprovação do benchmark."""

    policy_version: str = "1.0.0"
    minimum_agentic_pass_rate: float = 1.0
    minimum_agentic_average_score: float = 1.0
    minimum_score_delta: float = 0.0
    maximum_regression_count: int = 0
    maximum_invalid_citation_count: int = 0
    maximum_agentic_error_count: int = 0
    maximum_latency_delta_ms: float = 100.0
    minimum_category_pass_rate: float = 1.0
    require_all_dataset_cases: bool = True
    require_all_categories: bool = True
    require_offline_execution: bool = True

    def __post_init__(self) -> None:
        if not self.policy_version.strip():
            raise ValueError("policy_version é obrigatória.")

        for field_name in (
            "minimum_agentic_pass_rate",
            "minimum_agentic_average_score",
            "minimum_category_pass_rate",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} deve estar entre 0.0 e 1.0.")

        for field_name in (
            "maximum_regression_count",
            "maximum_invalid_citation_count",
            "maximum_agentic_error_count",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value < 0:
                raise ValueError(f"{field_name} não pode ser negativo.")

        if self.maximum_latency_delta_ms < 0:
            raise ValueError("maximum_latency_delta_ms não pode ser negativo.")


@dataclass(frozen=True, slots=True)
class QualityGateCheck:
    """Resultado de uma regra individual."""

    code: str
    description: str
    actual: Any
    expected: Any
    passed: bool
    blocking: bool = True


@dataclass(frozen=True, slots=True)
class QualityGateResult:
    """Resultado consolidado do Quality Gate."""

    policy_version: str
    dataset_version: str
    checks: tuple[QualityGateCheck, ...]
    passed: bool
    failed_blocking_codes: tuple[str, ...]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def total_checks(self) -> int:
        """Quantidade total de verificações."""

        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        """Quantidade de verificações aprovadas."""

        return sum(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> int:
        """Quantidade de verificações reprovadas."""

        return self.total_checks - self.passed_checks

    def check(
        self,
        code: str,
    ) -> QualityGateCheck:
        """Obtém uma verificação pelo código."""

        for item in self.checks:
            if item.code == code:
                return item

        raise KeyError(f"Verificação não encontrada: {code}")


def load_quality_gate_policy(
    path: str | Path,
) -> QualityGatePolicy:
    """Carrega política JSON validada."""

    policy_path = Path(path)

    if not policy_path.exists():
        raise FileNotFoundError(f"Política não encontrada: {policy_path}")

    payload = json.loads(policy_path.read_text(encoding="utf-8-sig"))

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError("A política deve ser um objeto JSON.")

    return QualityGatePolicy(**payload)


def evaluate_benchmark_quality_gate(
    benchmark: OfflineBenchmarkResult,
    *,
    policy: QualityGatePolicy,
    expected_case_count: int | None = None,
    expected_category_count: int | None = None,
) -> QualityGateResult:
    """Avalia o benchmark contra uma política determinística."""

    agentic = benchmark.summary(BenchmarkProfile.AGENTIC)

    comparison = benchmark.comparison

    category_rates = dict(agentic.category_pass_rates)

    minimum_observed_category_rate = (
        min(category_rates.values()) if category_rates else 0.0
    )

    observed_case_count = agentic.total_cases

    observed_category_count = len(category_rates)

    all_cases_present = (
        expected_case_count is None or observed_case_count == expected_case_count
    )

    all_categories_present = (
        expected_category_count is None
        or observed_category_count == expected_category_count
    )

    checks = (
        QualityGateCheck(
            code="agentic_pass_rate",
            description=("Taxa de aprovação mínima do perfil Agentic."),
            actual=agentic.pass_rate,
            expected=(f">={policy.minimum_agentic_pass_rate}"),
            passed=(agentic.pass_rate >= policy.minimum_agentic_pass_rate),
        ),
        QualityGateCheck(
            code="agentic_average_score",
            description=("Score médio mínimo do perfil Agentic."),
            actual=agentic.average_score,
            expected=(f">={policy.minimum_agentic_average_score}"),
            passed=(agentic.average_score >= policy.minimum_agentic_average_score),
        ),
        QualityGateCheck(
            code="score_delta",
            description=("O Agentic não pode regredir no score médio."),
            actual=comparison.average_score_delta,
            expected=(f">={policy.minimum_score_delta}"),
            passed=(comparison.average_score_delta >= policy.minimum_score_delta),
        ),
        QualityGateCheck(
            code="regression_count",
            description=("Quantidade máxima de regressões funcionais."),
            actual=len(comparison.regressions),
            expected=(f"<={policy.maximum_regression_count}"),
            passed=(len(comparison.regressions) <= policy.maximum_regression_count),
        ),
        QualityGateCheck(
            code="invalid_citation_count",
            description=("Quantidade máxima de citações inválidas."),
            actual=agentic.invalid_citation_count,
            expected=(f"<={policy.maximum_invalid_citation_count}"),
            passed=(
                agentic.invalid_citation_count <= policy.maximum_invalid_citation_count
            ),
        ),
        QualityGateCheck(
            code="agentic_error_count",
            description=("Quantidade máxima de erros no perfil Agentic."),
            actual=agentic.error_count,
            expected=(f"<={policy.maximum_agentic_error_count}"),
            passed=(agentic.error_count <= policy.maximum_agentic_error_count),
        ),
        QualityGateCheck(
            code="latency_delta",
            description=("Aumento máximo permitido de latência simulada."),
            actual=comparison.latency_delta_ms,
            expected=(f"<={policy.maximum_latency_delta_ms}"),
            passed=(comparison.latency_delta_ms <= policy.maximum_latency_delta_ms),
        ),
        QualityGateCheck(
            code="category_pass_rate",
            description=("Taxa mínima de aprovação em cada categoria."),
            actual=minimum_observed_category_rate,
            expected=(f">={policy.minimum_category_pass_rate}"),
            passed=(
                minimum_observed_category_rate >= policy.minimum_category_pass_rate
            ),
        ),
        QualityGateCheck(
            code="dataset_case_count",
            description=("Todos os casos esperados devem ser executados."),
            actual=observed_case_count,
            expected=expected_case_count,
            passed=(all_cases_present or not policy.require_all_dataset_cases),
        ),
        QualityGateCheck(
            code="dataset_category_count",
            description=("Todas as categorias esperadas devem ser executadas."),
            actual=observed_category_count,
            expected=expected_category_count,
            passed=(all_categories_present or not policy.require_all_categories),
        ),
        QualityGateCheck(
            code="offline_execution",
            description=("O Quality Gate desta fase deve permanecer offline."),
            actual=True,
            expected=True,
            passed=True,
        ),
    )

    failed_blocking_codes = tuple(
        check.code for check in checks if (check.blocking and not check.passed)
    )

    return QualityGateResult(
        policy_version=policy.policy_version,
        dataset_version=benchmark.dataset_version,
        checks=checks,
        passed=not failed_blocking_codes,
        failed_blocking_codes=failed_blocking_codes,
        metadata={
            "offline": True,
            "live_services_used": False,
            "agentic_total_cases": (agentic.total_cases),
            "agentic_total_categories": (observed_category_count),
        },
    )


def quality_gate_to_dict(
    result: QualityGateResult,
) -> dict[str, Any]:
    """Converte o resultado para relatório JSON."""

    return {
        "policy_version": result.policy_version,
        "dataset_version": result.dataset_version,
        "passed": result.passed,
        "total_checks": result.total_checks,
        "passed_checks": result.passed_checks,
        "failed_checks": result.failed_checks,
        "failed_blocking_codes": list(result.failed_blocking_codes),
        "metadata": dict(result.metadata),
        "checks": [asdict(check) for check in result.checks],
    }


def write_quality_gate_report(
    result: QualityGateResult,
    path: str | Path,
) -> Path:
    """Grava o relatório do Quality Gate."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            quality_gate_to_dict(result),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return output_path
