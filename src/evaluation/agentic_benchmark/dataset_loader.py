"""Carregamento seguro do dataset JSONL do Agentic RAG."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .contracts import (
    AgenticBenchmarkCase,
    BenchmarkCaseCategory,
    BenchmarkDataset,
    BenchmarkExpectations,
    BenchmarkThresholds,
    ExpectedComplexity,
    ExpectedGatewayDecision,
    ExpectedSecurityOutcome,
    normalize_string_sequence,
)

DEFAULT_DATASET_VERSION = "1.0.0"


class DatasetValidationError(ValueError):
    """Erro de validação de um dataset do benchmark."""


def _require_mapping(
    value: Any,
    *,
    field_name: str,
    line_number: int,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DatasetValidationError(
            f"Linha {line_number}: {field_name} deve ser um objeto."
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
    line_number: int,
) -> str:
    if not isinstance(value, str):
        raise DatasetValidationError(
            f"Linha {line_number}: {field_name} deve ser texto."
        )

    normalized = value.strip()

    if not normalized:
        raise DatasetValidationError(
            f"Linha {line_number}: {field_name} é obrigatório."
        )

    return normalized


def _string_sequence(
    value: Any,
    *,
    field_name: str,
    line_number: int,
) -> tuple[str, ...]:
    if value is None:
        return ()

    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise DatasetValidationError(
            f"Linha {line_number}: {field_name} deve ser uma lista de textos."
        )

    try:
        return normalize_string_sequence(value)
    except ValueError as exc:
        raise DatasetValidationError(
            f"Linha {line_number}: {field_name}: {exc}"
        ) from exc


def parse_case(
    payload: Mapping[str, Any],
    *,
    line_number: int,
) -> AgenticBenchmarkCase:
    """Converte um objeto JSON em contrato validado."""

    expectations_payload = _require_mapping(
        payload.get("expectations"),
        field_name="expectations",
        line_number=line_number,
    )

    thresholds_payload = _require_mapping(
        payload.get("thresholds"),
        field_name="thresholds",
        line_number=line_number,
    )

    metadata = payload.get(
        "metadata",
        {},
    )

    if not isinstance(metadata, Mapping):
        raise DatasetValidationError(
            f"Linha {line_number}: metadata deve ser um objeto."
        )

    try:
        expectations = BenchmarkExpectations(
            complexity=ExpectedComplexity(
                _require_string(
                    expectations_payload.get("complexity"),
                    field_name=("expectations.complexity"),
                    line_number=line_number,
                )
            ),
            gateway_decision=(
                ExpectedGatewayDecision(
                    _require_string(
                        expectations_payload.get("gateway_decision"),
                        field_name=("expectations.gateway_decision"),
                        line_number=line_number,
                    )
                )
            ),
            routes=_string_sequence(
                expectations_payload.get(
                    "routes",
                    [],
                ),
                field_name="expectations.routes",
                line_number=line_number,
            ),
            required_terms=_string_sequence(
                expectations_payload.get(
                    "required_terms",
                    [],
                ),
                field_name=("expectations.required_terms"),
                line_number=line_number,
            ),
            forbidden_terms=_string_sequence(
                expectations_payload.get(
                    "forbidden_terms",
                    [],
                ),
                field_name=("expectations.forbidden_terms"),
                line_number=line_number,
            ),
            expected_fallback=bool(
                expectations_payload.get(
                    "expected_fallback",
                    False,
                )
            ),
            security_outcome=(
                ExpectedSecurityOutcome(
                    expectations_payload.get(
                        "security_outcome",
                        "allow",
                    )
                )
            ),
        )

        thresholds = BenchmarkThresholds(
            minimum_evidence_count=int(
                thresholds_payload.get(
                    "minimum_evidence_count",
                    0,
                )
            ),
            minimum_citation_coverage=float(
                thresholds_payload.get(
                    "minimum_citation_coverage",
                    0.0,
                )
            ),
            minimum_groundedness=float(
                thresholds_payload.get(
                    "minimum_groundedness",
                    0.0,
                )
            ),
            minimum_answer_relevance=float(
                thresholds_payload.get(
                    "minimum_answer_relevance",
                    0.0,
                )
            ),
            minimum_context_relevance=float(
                thresholds_payload.get(
                    "minimum_context_relevance",
                    0.0,
                )
            ),
            maximum_latency_ms=int(
                thresholds_payload.get(
                    "maximum_latency_ms",
                    10_000,
                )
            ),
        )

        return AgenticBenchmarkCase(
            case_id=_require_string(
                payload.get("case_id"),
                field_name="case_id",
                line_number=line_number,
            ),
            dataset_version=_require_string(
                payload.get("dataset_version"),
                field_name="dataset_version",
                line_number=line_number,
            ),
            category=BenchmarkCaseCategory(
                _require_string(
                    payload.get("category"),
                    field_name="category",
                    line_number=line_number,
                )
            ),
            question=_require_string(
                payload.get("question"),
                field_name="question",
                line_number=line_number,
            ),
            expectations=expectations,
            thresholds=thresholds,
            synthetic_contexts=(
                _string_sequence(
                    payload.get(
                        "synthetic_contexts",
                        [],
                    ),
                    field_name="synthetic_contexts",
                    line_number=line_number,
                )
            ),
            metadata=dict(metadata),
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        if isinstance(
            exc,
            DatasetValidationError,
        ):
            raise

        raise DatasetValidationError(f"Linha {line_number}: {exc}") from exc


def load_benchmark_dataset(
    path: str | Path,
) -> BenchmarkDataset:
    """Carrega e valida um dataset JSONL."""

    dataset_path = Path(path).resolve()

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {dataset_path}")

    if not dataset_path.is_file():
        raise DatasetValidationError(f"O caminho não é um arquivo: {dataset_path}")

    cases: list[AgenticBenchmarkCase] = []

    with dataset_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(
                    f"Linha {line_number}: JSON inválido: {exc.msg}"
                ) from exc

            mapping = _require_mapping(
                payload,
                field_name="registro",
                line_number=line_number,
            )

            cases.append(
                parse_case(
                    mapping,
                    line_number=line_number,
                )
            )

    if not cases:
        raise DatasetValidationError("O dataset não contém casos.")

    versions = {case.dataset_version for case in cases}

    if len(versions) != 1:
        raise DatasetValidationError(
            "O dataset possui múltiplas versões: " + ", ".join(sorted(versions))
        )

    version = next(iter(versions))

    return BenchmarkDataset(
        version=version,
        cases=tuple(cases),
    )
