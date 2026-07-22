"""
Revisor determinístico de risco dos relatórios da INNA.

O revisor:
- não recalcula indicadores;
- não chama LLM;
- não modifica valores financeiros;
- bloqueia linguagem inadequada;
- decide se o relatório pode seguir para PDF.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping, Sequence


RISK_REVIEW_VERSION = "1.0"

BLOCKING_PROMISE_PATTERNS = (
    r"\bretorno garantido\b",
    r"\blucro garantido\b",
    r"\bganho garantido\b",
    r"\bsem risco\b",
    r"\brisco zero\b",
    r"\bresultado garantido\b",
    r"\bvocê vai ganhar\b",
    r"\bvoce vai ganhar\b",
    r"\bficará rico\b",
    r"\bficara rico\b",
)

CONTRADICTORY_PAIRS = (
    (
        "assuma novas dívidas",
        "evite novas dívidas",
    ),
    (
        "aumente os gastos",
        "reduza os gastos",
    ),
    (
        "use toda a reserva",
        "preserve a reserva",
    ),
    (
        "ignore suas dívidas",
        "priorize suas dívidas",
    ),
)


@dataclass(frozen=True)
class RiskReviewFinding:
    """
    Achado individual da revisão.
    """

    code: str
    severity: str
    message: str
    blocking: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RiskReviewDecision:
    """
    Decisão final da revisão determinística.
    """

    approved: bool
    report_version: str
    review_version: str
    financial_values_recalculated: bool
    official_data_present: bool
    findings: tuple[RiskReviewFinding, ...]
    blocking_findings: int
    warning_findings: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "report_version": self.report_version,
            "review_version": self.review_version,
            "financial_values_recalculated": (
                self.financial_values_recalculated
            ),
            "official_data_present": (
                self.official_data_present
            ),
            "findings": [
                item.to_dict()
                for item in self.findings
            ],
            "blocking_findings": (
                self.blocking_findings
            ),
            "warning_findings": (
                self.warning_findings
            ),
            "reason": self.reason,
        }


def _normalized_text(
    value: Any,
) -> str:
    return " ".join(
        str(value or "").strip().lower().split()
    )


def _collect_report_text(
    report: Mapping[str, Any],
) -> str:
    parts: list[str] = []

    for key in (
        "titulo",
        "resumo_executivo",
    ):
        value = report.get(key)

        if value:
            parts.append(str(value))

    for key in (
        "recomendacoes",
        "proximos_passos",
    ):
        values = report.get(key, [])

        if isinstance(
            values,
            Sequence,
        ) and not isinstance(
            values,
            (str, bytes),
        ):
            parts.extend(
                str(item)
                for item in values
                if str(item).strip()
            )

    return _normalized_text(
        " ".join(parts)
    )


def _add_finding(
    findings: list[RiskReviewFinding],
    *,
    code: str,
    severity: str,
    message: str,
    blocking: bool,
) -> None:
    findings.append(
        RiskReviewFinding(
            code=code,
            severity=severity,
            message=message,
            blocking=blocking,
        )
    )


def _validate_official_indicators(
    report: Mapping[str, Any],
    findings: list[RiskReviewFinding],
) -> bool:
    possui_diagnostico = bool(
        report.get(
            "possui_diagnostico",
            False,
        )
    )

    indicators = report.get(
        "indicadores_oficiais"
    )

    if not possui_diagnostico:
        return False

    if not isinstance(indicators, Mapping):
        _add_finding(
            findings,
            code="official_indicators_missing",
            severity="critical",
            message=(
                "O relatório possui diagnóstico, mas "
                "não contém indicadores oficiais."
            ),
            blocking=True,
        )

        return False

    score = indicators.get(
        "score_financeiro"
    )

    if score is not None:
        try:
            normalized_score = int(score)
        except (TypeError, ValueError):
            _add_finding(
                findings,
                code="invalid_financial_score",
                severity="critical",
                message=(
                    "O score financeiro oficial "
                    "possui formato inválido."
                ),
                blocking=True,
            )
        else:
            if not 0 <= normalized_score <= 100:
                _add_finding(
                    findings,
                    code="financial_score_out_of_range",
                    severity="critical",
                    message=(
                        "O score financeiro oficial "
                        "está fora do intervalo permitido."
                    ),
                    blocking=True,
                )

    percentage = indicators.get(
        "comprometimento_renda_percentual"
    )

    if percentage is not None:
        try:
            normalized_percentage = float(
                percentage
            )
        except (TypeError, ValueError):
            _add_finding(
                findings,
                code="invalid_income_commitment",
                severity="critical",
                message=(
                    "O comprometimento de renda "
                    "possui formato inválido."
                ),
                blocking=True,
            )
        else:
            if normalized_percentage < 0:
                _add_finding(
                    findings,
                    code="negative_income_commitment",
                    severity="critical",
                    message=(
                        "O comprometimento de renda "
                        "não pode ser negativo."
                    ),
                    blocking=True,
                )

            elif normalized_percentage > 100:
                _add_finding(
                    findings,
                    code="income_commitment_above_100",
                    severity="warning",
                    message=(
                        "O comprometimento de renda "
                        "está acima de 100%."
                    ),
                    blocking=False,
                )

    reserve_months = indicators.get(
        "meses_reserva_estimados"
    )

    if reserve_months is not None:
        try:
            normalized_reserve = float(
                reserve_months
            )
        except (TypeError, ValueError):
            _add_finding(
                findings,
                code="invalid_reserve_months",
                severity="critical",
                message=(
                    "A estimativa de meses de reserva "
                    "possui formato inválido."
                ),
                blocking=True,
            )
        else:
            if normalized_reserve < 0:
                _add_finding(
                    findings,
                    code="negative_reserve_months",
                    severity="critical",
                    message=(
                        "A estimativa de reserva "
                        "não pode ser negativa."
                    ),
                    blocking=True,
                )

    return True


def _validate_language(
    report: Mapping[str, Any],
    findings: list[RiskReviewFinding],
) -> None:
    report_text = _collect_report_text(
        report
    )

    for pattern in BLOCKING_PROMISE_PATTERNS:
        if re.search(
            pattern,
            report_text,
            flags=re.IGNORECASE,
        ):
            _add_finding(
                findings,
                code="prohibited_financial_promise",
                severity="critical",
                message=(
                    "O relatório contém promessa "
                    "financeira inadequada."
                ),
                blocking=True,
            )

            break

    for first, second in CONTRADICTORY_PAIRS:
        if (
            first in report_text
            and second in report_text
        ):
            _add_finding(
                findings,
                code="contradictory_recommendations",
                severity="critical",
                message=(
                    "O relatório contém recomendações "
                    "financeiras contraditórias."
                ),
                blocking=True,
            )

            break


def review_financial_report(
    report: Mapping[str, Any],
) -> RiskReviewDecision:
    """
    Executa a revisão determinística do relatório.
    """
    if not isinstance(report, Mapping):
        finding = RiskReviewFinding(
            code="invalid_report_payload",
            severity="critical",
            message=(
                "A estrutura do relatório é inválida."
            ),
            blocking=True,
        )

        return RiskReviewDecision(
            approved=False,
            report_version="unknown",
            review_version=RISK_REVIEW_VERSION,
            financial_values_recalculated=True,
            official_data_present=False,
            findings=(finding,),
            blocking_findings=1,
            warning_findings=0,
            reason="risk_review_blocked",
        )

    findings: list[RiskReviewFinding] = []

    report_version = str(
        report.get(
            "report_version",
            "unknown",
        )
    ).strip()

    recalculated = bool(
        report.get(
            "financial_values_recalculated",
            True,
        )
    )

    if recalculated:
        _add_finding(
            findings,
            code="financial_values_recalculated",
            severity="critical",
            message=(
                "O relatório indica recálculo de "
                "valores financeiros."
            ),
            blocking=True,
        )

    official_data_present = (
        _validate_official_indicators(
            report,
            findings,
        )
    )

    possui_diagnostico = bool(
        report.get(
            "possui_diagnostico",
            False,
        )
    )

    if not possui_diagnostico:
        _add_finding(
            findings,
            code="no_financial_diagnosis",
            severity="warning",
            message=(
                "Não existem diagnósticos financeiros "
                "para compor o relatório."
            ),
            blocking=True,
        )

    if not bool(
        report.get(
            "ready_for_risk_review",
            False,
        )
    ):
        _add_finding(
            findings,
            code="report_not_ready_for_review",
            severity="critical",
            message=(
                "O relatório não foi marcado como "
                "pronto para revisão."
            ),
            blocking=True,
        )

    _validate_language(
        report,
        findings,
    )

    blocking_findings = sum(
        1
        for item in findings
        if item.blocking
    )

    warning_findings = sum(
        1
        for item in findings
        if not item.blocking
    )

    approved = (
        blocking_findings == 0
        and not recalculated
        and official_data_present
    )

    reason = (
        "risk_review_approved"
        if approved
        else "risk_review_blocked"
    )

    return RiskReviewDecision(
        approved=approved,
        report_version=report_version,
        review_version=RISK_REVIEW_VERSION,
        financial_values_recalculated=(
            recalculated
        ),
        official_data_present=(
            official_data_present
        ),
        findings=tuple(findings),
        blocking_findings=blocking_findings,
        warning_findings=warning_findings,
        reason=reason,
    )


def apply_risk_review_to_report(
    report: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Aplica a decisão ao relatório sem alterar valores.
    """
    decision = review_financial_report(
        report
    )

    updated_report = dict(report)

    updated_report[
        "risk_review"
    ] = decision.to_dict()

    updated_report[
        "risk_review_approved"
    ] = decision.approved

    updated_report[
        "ready_for_pdf_rendering"
    ] = decision.approved

    return updated_report


__all__ = [
    "RISK_REVIEW_VERSION",
    "BLOCKING_PROMISE_PATTERNS",
    "CONTRADICTORY_PAIRS",
    "RiskReviewFinding",
    "RiskReviewDecision",
    "review_financial_report",
    "apply_risk_review_to_report",
]
