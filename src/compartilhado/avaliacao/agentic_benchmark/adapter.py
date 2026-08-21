"""Adapter tolerante para saídas do gateway Agentic RAG."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .result_contracts import (
    ActualGatewayDecision,
    ActualSecurityOutcome,
    AgenticEvaluationResult,
    AgenticExecutionMode,
    AgenticMetricSnapshot,
    CitationRecord,
    EvidenceRecord,
    ExecutionStatus,
)

_MISSING = object()


def _read_path(
    payload: Mapping[str, Any],
    *paths: tuple[str, ...],
    default: Any = None,
) -> Any:
    """Obtém o primeiro caminho existente em um mapping aninhado."""

    for path in paths:
        current: Any = payload

        for part in path:
            if not isinstance(
                current,
                Mapping,
            ):
                current = _MISSING
                break

            if part not in current:
                current = _MISSING
                break

            current = current[part]

        if current is not _MISSING:
            return current

    return default


def _normalize_text(
    value: Any,
    *,
    default: str = "",
) -> str:
    if value is None:
        return default

    if isinstance(
        value,
        str,
    ):
        return value.strip()

    return str(value).strip()


def _normalize_optional_text(
    value: Any,
) -> str | None:
    normalized = _normalize_text(value)

    return normalized or None


def _normalize_bool(
    value: Any,
    *,
    default: bool = False,
) -> bool:
    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        normalized = value.strip().lower()

        if normalized in {
            "true",
            "1",
            "yes",
            "sim",
            "on",
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "não",
            "nao",
            "off",
        }:
            return False

    return bool(value)


def _normalize_float(
    value: Any,
    *,
    default: float = 0.0,
) -> float:
    if value is None:
        return default

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _normalize_score(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        score = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    return min(
        1.0,
        max(
            0.0,
            score,
        ),
    )


def _normalize_string_sequence(
    value: Any,
) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(
        value,
        str,
    ):
        items: Sequence[Any] = (value,)
    elif isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            bytes,
            bytearray,
        ),
    ):
        items = value
    else:
        items = (value,)

    normalized: list[str] = []

    for item in items:
        text = _normalize_text(item)

        if text and text not in normalized:
            normalized.append(text)

    return tuple(normalized)


def _normalize_mode(
    value: Any,
) -> AgenticExecutionMode:
    normalized = _normalize_text(
        value,
        default="off",
    ).lower()

    aliases = {
        "disabled": "off",
        "legacy": "off",
        "observe": "shadow",
        "observation": "shadow",
        "enabled": "active",
        "on": "active",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    try:
        return AgenticExecutionMode(normalized)
    except ValueError:
        return AgenticExecutionMode.OFF


def _normalize_decision(
    value: Any,
) -> ActualGatewayDecision:
    normalized = _normalize_text(
        value,
        default="unknown",
    ).lower()

    aliases = {
        "legacy_rag": "legacy",
        "classic": "legacy",
        "agentic_rag": "agentic",
        "agent": "agentic",
        "safe_fallback": "fallback",
        "denied": "reject",
        "rejected": "reject",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    try:
        return ActualGatewayDecision(normalized)
    except ValueError:
        return ActualGatewayDecision.UNKNOWN


def _normalize_status(
    value: Any,
    *,
    decision: ActualGatewayDecision,
    fallback_used: bool,
    error_code: str | None,
    error_message: str | None,
) -> ExecutionStatus:
    normalized = _normalize_text(value).lower()

    aliases = {
        "ok": "success",
        "completed": "success",
        "complete": "success",
        "denied": "rejected",
        "reject": "rejected",
        "failed": "error",
        "failure": "error",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    if normalized:
        try:
            return ExecutionStatus(normalized)
        except ValueError:
            pass

    if error_code or error_message:
        return ExecutionStatus.ERROR

    if decision is ActualGatewayDecision.REJECT:
        return ExecutionStatus.REJECTED

    if fallback_used or decision is ActualGatewayDecision.FALLBACK:
        return ExecutionStatus.FALLBACK

    return ExecutionStatus.SUCCESS


def _normalize_security_outcome(
    value: Any,
    *,
    decision: ActualGatewayDecision,
    fallback_used: bool,
) -> ActualSecurityOutcome:
    normalized = _normalize_text(
        value,
        default="unknown",
    ).lower()

    aliases = {
        "allowed": "allow",
        "blocked": "deny",
        "denied": "deny",
        "sanitized": "sanitize",
        "filtered": "sanitize",
        "fallback": "safe_fallback",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    try:
        outcome = ActualSecurityOutcome(normalized)
    except ValueError:
        outcome = ActualSecurityOutcome.UNKNOWN

    if outcome is not ActualSecurityOutcome.UNKNOWN:
        return outcome

    if decision is ActualGatewayDecision.REJECT:
        return ActualSecurityOutcome.DENY

    if fallback_used:
        return ActualSecurityOutcome.SAFE_FALLBACK

    return ActualSecurityOutcome.ALLOW


def _normalize_evidences(
    value: Any,
) -> tuple[EvidenceRecord, ...]:
    if value is None:
        return ()

    if isinstance(
        value,
        Mapping,
    ):
        items: Sequence[Any] = (value,)
    elif isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        items = value
    else:
        items = (value,)

    evidences: list[EvidenceRecord] = []

    for index, item in enumerate(
        items,
        start=1,
    ):
        if isinstance(
            item,
            Mapping,
        ):
            content = _normalize_text(
                _read_path(
                    item,
                    ("content",),
                    ("text",),
                    ("page_content",),
                    ("chunk",),
                    ("document",),
                    default="",
                )
            )

            if not content:
                continue

            evidence_id = _normalize_text(
                _read_path(
                    item,
                    ("evidence_id",),
                    ("id",),
                    ("document_id",),
                    ("chunk_id",),
                    default=f"evidence-{index}",
                )
            )

            source = _normalize_optional_text(
                _read_path(
                    item,
                    ("source",),
                    ("source_name",),
                    ("metadata", "source"),
                    ("metadata", "filename"),
                )
            )

            citation = _normalize_optional_text(
                _read_path(
                    item,
                    ("citation",),
                    ("citation_id",),
                    ("reference",),
                )
            )

            score = _normalize_score(
                _read_path(
                    item,
                    ("score",),
                    ("relevance_score",),
                    ("similarity",),
                )
            )

            metadata = _read_path(
                item,
                ("metadata",),
                default={},
            )

            if not isinstance(
                metadata,
                Mapping,
            ):
                metadata = {}

            evidences.append(
                EvidenceRecord(
                    evidence_id=evidence_id,
                    content=content,
                    source=source,
                    citation=citation,
                    score=score,
                    metadata=dict(metadata),
                )
            )

            continue

        content = _normalize_text(item)

        if content:
            evidences.append(
                EvidenceRecord(
                    evidence_id=f"evidence-{index}",
                    content=content,
                )
            )

    return tuple(evidences)


def _normalize_citations(
    value: Any,
) -> tuple[CitationRecord, ...]:
    if value is None:
        return ()

    if isinstance(
        value,
        Mapping,
    ):
        items: Sequence[Any] = (value,)
    elif isinstance(
        value,
        Sequence,
    ) and not isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        items = value
    else:
        items = (value,)

    citations: list[CitationRecord] = []

    for index, item in enumerate(
        items,
        start=1,
    ):
        if isinstance(
            item,
            Mapping,
        ):
            citation_id = _normalize_text(
                _read_path(
                    item,
                    ("citation_id",),
                    ("id",),
                    ("reference",),
                    ("label",),
                    default=f"citation-{index}",
                )
            )

            citations.append(
                CitationRecord(
                    citation_id=citation_id,
                    evidence_id=_normalize_optional_text(
                        _read_path(
                            item,
                            ("evidence_id",),
                            ("document_id",),
                        )
                    ),
                    source=_normalize_optional_text(
                        _read_path(
                            item,
                            ("source",),
                            ("source_name",),
                        )
                    ),
                    text=_normalize_optional_text(
                        _read_path(
                            item,
                            ("text",),
                            ("content",),
                        )
                    ),
                    valid=_normalize_bool(
                        _read_path(
                            item,
                            ("valid",),
                            ("is_valid",),
                            default=True,
                        ),
                        default=True,
                    ),
                )
            )

            continue

        citation_id = _normalize_text(item)

        if citation_id:
            citations.append(
                CitationRecord(
                    citation_id=citation_id,
                )
            )

    return tuple(citations)


def adapt_gateway_output(
    *,
    case_id: str,
    question: str,
    output: Mapping[str, Any],
    default_mode: AgenticExecutionMode = (AgenticExecutionMode.OFF),
) -> AgenticEvaluationResult:
    """Converte uma saída heterogênea no contrato canônico."""

    if not isinstance(
        output,
        Mapping,
    ):
        raise TypeError("output deve ser um Mapping.")

    mode_value = _read_path(
        output,
        ("mode",),
        ("agentic_mode",),
        ("gateway", "mode"),
        ("agentic_rag", "mode"),
        default=default_mode.value,
    )

    decision_value = _read_path(
        output,
        ("decision",),
        ("gateway_decision",),
        ("route_decision",),
        ("gateway", "decision"),
        ("agentic_rag", "decision"),
        ("metadata", "decision"),
    )

    fallback_used = _normalize_bool(
        _read_path(
            output,
            ("fallback_used",),
            ("used_fallback",),
            ("fallback",),
            ("metadata", "fallback_used"),
            default=False,
        )
    )

    error_code = _normalize_optional_text(
        _read_path(
            output,
            ("error_code",),
            ("error", "code"),
            ("metadata", "error_code"),
        )
    )

    error_message = _normalize_optional_text(
        _read_path(
            output,
            ("error_message",),
            ("error", "message"),
            ("error", "detail"),
            ("metadata", "error_message"),
        )
    )

    decision = _normalize_decision(decision_value)

    status = _normalize_status(
        _read_path(
            output,
            ("status",),
            ("execution_status",),
            ("metadata", "status"),
        ),
        decision=decision,
        fallback_used=fallback_used,
        error_code=error_code,
        error_message=error_message,
    )

    if status is ExecutionStatus.FALLBACK:
        fallback_used = True

    security_outcome = _normalize_security_outcome(
        _read_path(
            output,
            ("security_outcome",),
            ("security", "outcome"),
            ("security", "decision"),
            ("metadata", "security_outcome"),
        ),
        decision=decision,
        fallback_used=fallback_used,
    )

    routes = _normalize_string_sequence(
        _read_path(
            output,
            ("routes",),
            ("used_routes",),
            ("tools_used",),
            ("gateway", "routes"),
            ("research", "routes"),
            ("metadata", "routes"),
        )
    )

    evidences = _normalize_evidences(
        _read_path(
            output,
            ("evidences",),
            ("evidence",),
            ("documents",),
            ("contexts",),
            ("retrieved_documents",),
            ("research", "evidences"),
            ("metadata", "evidences"),
        )
    )

    citations = _normalize_citations(
        _read_path(
            output,
            ("citations",),
            ("references",),
            ("sources",),
            ("answer", "citations"),
            ("metadata", "citations"),
        )
    )

    answer_value = _read_path(
        output,
        ("final_answer",),
        ("synthesis", "answer"),
        ("agentic_rag", "answer"),
        ("response",),
        ("result",),
        ("answer", "text"),
        ("answer", "content"),
        ("answer", "answer"),
        ("answer",),
        default="",
    )

    if isinstance(
        answer_value,
        Mapping,
    ):
        nested_answer = _read_path(
            answer_value,
            ("text",),
            ("content",),
            ("answer",),
            default="",
        )

        if _normalize_text(nested_answer):
            answer_value = nested_answer

        else:
            answer_value = _read_path(
                output,
                ("final_answer",),
                ("synthesis", "answer"),
                ("agentic_rag", "answer"),
                ("response",),
                ("result",),
                default="",
            )

    metrics = AgenticMetricSnapshot(
        citation_coverage=_normalize_score(
            _read_path(
                output,
                ("citation_coverage",),
                ("metrics", "citation_coverage"),
                ("evaluation", "citation_coverage"),
            )
        ),
        groundedness=_normalize_score(
            _read_path(
                output,
                ("groundedness",),
                ("metrics", "groundedness"),
                ("evaluation", "groundedness"),
            )
        ),
        answer_relevance=_normalize_score(
            _read_path(
                output,
                ("answer_relevance",),
                ("metrics", "answer_relevance"),
                ("evaluation", "answer_relevance"),
            )
        ),
        context_relevance=_normalize_score(
            _read_path(
                output,
                ("context_relevance",),
                ("metrics", "context_relevance"),
                ("evaluation", "context_relevance"),
            )
        ),
        sufficiency=_normalize_score(
            _read_path(
                output,
                ("sufficiency",),
                ("sufficiency_score",),
                ("metrics", "sufficiency"),
                ("evaluation", "sufficiency"),
            )
        ),
    )

    latency_ms = _normalize_float(
        _read_path(
            output,
            ("latency_ms",),
            ("duration_ms",),
            ("elapsed_ms",),
            ("timing", "latency_ms"),
            ("metadata", "latency_ms"),
            default=0.0,
        ),
        default=0.0,
    )

    trace_id = _normalize_optional_text(
        _read_path(
            output,
            ("trace_id",),
            ("trace", "id"),
            ("metadata", "trace_id"),
        )
    )

    raw_metadata = _read_path(
        output,
        ("metadata",),
        default={},
    )

    if not isinstance(
        raw_metadata,
        Mapping,
    ):
        raw_metadata = {}

    return AgenticEvaluationResult(
        case_id=case_id.strip(),
        question=question.strip(),
        answer=_normalize_text(answer_value),
        mode=_normalize_mode(mode_value),
        decision=decision,
        status=status,
        security_outcome=security_outcome,
        routes=routes,
        evidences=evidences,
        citations=citations,
        metrics=metrics,
        latency_ms=max(
            0.0,
            latency_ms,
        ),
        fallback_used=fallback_used,
        trace_id=trace_id,
        error_code=error_code,
        error_message=error_message,
        raw_metadata=dict(raw_metadata),
    )
