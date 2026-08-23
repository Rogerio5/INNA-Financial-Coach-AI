from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from hashlib import blake2s
from pathlib import Path
from types import MappingProxyType
from typing import Any

from src.compartilhado.avaliacao.batch_runner import (
    BatchRunResult,
)
from src.compartilhado.avaliacao.datasets import (
    safe_artifact_name,
)
from src.compartilhado.avaliacao.privacy import (
    assert_safe_for_external_export,
)

REPORT_SCHEMA_VERSION = "1.0.0"


class EvaluationReportingError(RuntimeError):
    """Erro base da geração de relatórios."""


class EvaluationReportSerializationError(
    EvaluationReportingError,
    TypeError,
):
    """Objeto incompatível com a serialização do relatório."""


class EvaluationReportWriteError(
    EvaluationReportingError,
    OSError,
):
    """Falha ao gravar o artefato de avaliação."""


def to_json_compatible(
    value: Any,
    *,
    max_depth: int = 20,
    _depth: int = 0,
) -> Any:
    """
    Converte contratos da avaliação para estruturas compatíveis
    com JSON sem utilizar dataclasses.asdict().

    Suporta:
    - dataclasses;
    - MappingProxyType e mappings;
    - Enum;
    - datetime e date;
    - Path;
    - tuplas, listas, sets e frozensets;
    - valores escalares.
    """

    if _depth > max_depth:
        raise EvaluationReportSerializationError(
            "Profundidade máxima de serialização excedida."
        )

    if value is None or isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(value, Enum):
        return to_json_compatible(
            value.value,
            max_depth=max_depth,
            _depth=_depth + 1,
        )

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value) and not isinstance(
        value,
        type,
    ):
        return {
            item.name: to_json_compatible(
                getattr(value, item.name),
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            for item in fields(value)
        }

    if isinstance(
        value,
        (
            Mapping,
            MappingProxyType,
        ),
    ):
        return {
            str(key): to_json_compatible(
                item,
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            set,
            frozenset,
        ),
    ):
        ordered = sorted(
            value,
            key=lambda item: str(item),
        )

        return [
            to_json_compatible(
                item,
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            for item in ordered
        ]

    if isinstance(value, Sequence) and not isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        return [
            to_json_compatible(
                item,
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            for item in value
        ]

    raise EvaluationReportSerializationError(
        "Tipo não suportado na serialização: "
        f"{type(value).__name__}."
    )


def build_external_run_reference(
    batch_id: str,
) -> str:
    """
    Gera uma referência externa curta e não reversível.

    O identificador interno completo permanece disponível somente
    no relatório interno.
    """

    normalized = batch_id.strip()

    if not normalized:
        raise ValueError(
            "batch_id não pode ser vazio."
        )

    digest = blake2s(
        normalized.encode("utf-8"),
        digest_size=4,
    ).hexdigest()

    return f"run-{digest}"


def build_external_generated_date(
    value: datetime,
) -> str:
    """
    Retorna somente a data civil da execução.

    Horário, microssegundos e timezone completo permanecem apenas
    no relatório interno.
    """

    if value.tzinfo is None:
        raise ValueError(
            "A data de execução precisa possuir timezone."
        )

    return value.date().isoformat()


def _safe_external_batch_metadata(
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Retorna somente metadados externos explicitamente autorizados.

    Strings arbitrárias não são exportadas porque podem transportar
    dados pessoais, segredos ou informações confidenciais.
    """

    safe: dict[str, Any] = {}

    production_evaluation = metadata.get(
        "production_evaluation"
    )

    if isinstance(production_evaluation, bool):
        safe["production_evaluation"] = (
            production_evaluation
        )

    production_execution = metadata.get(
        "production_execution"
    )

    if isinstance(production_execution, bool):
        safe["production_execution"] = (
            production_execution
        )

    official_case_count = metadata.get(
        "official_case_count"
    )

    if (
        isinstance(official_case_count, int)
        and not isinstance(
            official_case_count,
            bool,
        )
        and official_case_count >= 0
    ):
        safe["official_case_count"] = (
            official_case_count
        )

    return safe


def _safe_external_quality_gate(
    quality_gate: Any,
) -> dict[str, Any]:
    """
    Cria uma projeção externa mínima do Quality Gate.

    Os campos actual, expected e metadata das violações não são
    exportados, pois podem transportar conteúdo sensível.
    """

    violations = getattr(
        quality_gate,
        "violations",
        (),
    )

    return {
        "passed": bool(
            getattr(
                quality_gate,
                "passed",
                False,
            )
        ),
        "evaluated_rules": int(
            getattr(
                quality_gate,
                "evaluated_rules",
                0,
            )
        ),
        "batch_id": None,
        "violations": [
            {
                "rule": (
                    violation.rule.value
                    if isinstance(
                        violation.rule,
                        Enum,
                    )
                    else str(violation.rule)
                ),
                "severity": (
                    violation.severity.value
                    if isinstance(
                        violation.severity,
                        Enum,
                    )
                    else str(violation.severity)
                ),
                "message": violation.message,
            }
            for violation in violations
        ],
    }


def _validate_external_report_projection(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Valida a projeção externa previamente allowlisted.

    A análise de segredos permanece ativa. A detecção genérica de
    dados pessoais não é reaplicada, pois esta estrutura não contém
    entrada de usuário, respostas, contexto RAG ou metadata livre.
    Identificadores técnicos são permitidos somente nos campos
    construídos explicitamente pelo reporting.
    """

    required_top_level_keys = {
        "schema_version",
        "report_type",
        "generated_at",
        "batch",
        "summary",
        "datasets",
        "categories",
        "metrics",
        "cases",
    }

    missing_keys = (
        required_top_level_keys
        - set(payload)
    )

    if missing_keys:
        raise EvaluationReportSerializationError(
            "A projeção externa não contém todos os "
            "campos obrigatórios: "
            + ", ".join(sorted(missing_keys))
        )

    batch_payload = payload.get("batch")
    summary_payload = payload.get("summary")
    cases_payload = payload.get("cases")

    if not isinstance(batch_payload, Mapping):
        raise EvaluationReportSerializationError(
            "O campo batch da projeção externa é inválido."
        )

    if not isinstance(summary_payload, Mapping):
        raise EvaluationReportSerializationError(
            "O campo summary da projeção externa é inválido."
        )

    if not isinstance(cases_payload, list):
        raise EvaluationReportSerializationError(
            "O campo cases da projeção externa é inválido."
        )

    forbidden_serialized_keys = {
        "input_text",
        "actual_output",
        "expected_output",
        "retrieval_context",
        "context",
        "conversation",
        "trace",
        "called_tools",
        "structured_output",
    }

    forbidden_secret_keys = {
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "private_key",
        "authorization",
        "credential",
        "credentials",
    }

    def inspect_value(
        value: Any,
        *,
        path: str = "$",
    ) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                normalized_key = str(key)

                normalized_key_folded = (
                    normalized_key.strip().casefold()
                )

                if (
                    normalized_key_folded
                    in forbidden_serialized_keys
                ):
                    raise EvaluationReportSerializationError(
                        "Campo proibido na projeção externa: "
                        f"{path}.{normalized_key}"
                    )

                if (
                    normalized_key_folded
                    in forbidden_secret_keys
                ):
                    raise EvaluationReportSerializationError(
                        "Possível campo de segredo na "
                        "projeção externa: "
                        f"{path}.{normalized_key}"
                    )

                inspect_value(
                    item,
                    path=f"{path}.{normalized_key}",
                )

            return

        if isinstance(value, list):
            for index, item in enumerate(value):
                inspect_value(
                    item,
                    path=f"{path}[{index}]",
                )

    inspect_value(payload)

    assert_safe_for_external_export(
        payload,
        block_personal_data=False,
    )

    compatible = to_json_compatible(payload)

    if not isinstance(compatible, dict):
        raise EvaluationReportSerializationError(
            "A projeção externa não pôde ser normalizada."
        )

    return compatible


def _safe_external_rag_triad(
    evaluation: Any,
) -> dict[str, Any] | None:
    """
    Cria uma projeção externa segura da RAG Triad.

    Não exporta motivos, metadados livres, conteúdo recuperado,
    respostas ou qualquer dado conversacional.
    """

    if evaluation is None:
        return None

    triad = evaluation.rag_triad

    if triad is None:
        return None

    return {
        "status": triad.status.value,
        "aggregate_score": triad.aggregate_score,
        "passed": triad.passed,
        "is_complete": triad.is_complete,
        "missing_metric_ids": list(
            triad.missing_metric_ids
        ),
        "failing_metric_ids": list(
            triad.failing_metric_ids
        ),
        "axes": [
            {
                "metric_id": axis.metric_id,
                "status": axis.status.value,
                "score": axis.score,
                "threshold": axis.threshold,
                "passed": axis.passed,
            }
            for axis in triad.axes
        ],
    }


def _safe_external_case_report(
    case_result: Any,
) -> dict[str, Any]:
    """
    Serializa um caso para exportação externa.

    A estrutura base permanece compatível com o relatório
    anterior. O campo rag_triad somente é incluído quando
    uma tríade real estiver disponível.
    """

    payload = {
        "dataset_id": case_result.dataset_id,
        "case_id": case_result.case_id,
        "category": case_result.category,
        "status": case_result.status.value,
        "has_evaluation": (
            case_result.evaluation is not None
        ),
        "error_type": case_result.error_type,
    }

    triad_payload = _safe_external_rag_triad(
        case_result.evaluation
    )

    if triad_payload is not None:
        payload["rag_triad"] = triad_payload

    return payload


def _internal_case_report(
    case_result: Any,
) -> dict[str, Any]:
    """
    Serializa um caso para o relatório interno completo.

    O payload padrão produzido por to_json_compatible é
    preservado. A RAG Triad é acrescentada somente quando
    existir, sem alterar casos não RAG.
    """

    payload = to_json_compatible(
        case_result
    )

    if not isinstance(payload, dict):
        raise EvaluationReportSerializationError(
            "O resultado do caso não pôde ser "
            "serializado como objeto."
        )

    evaluation = case_result.evaluation

    if evaluation is None:
        return payload

    triad_payload = (
        evaluation.rag_triad_payload
    )

    if triad_payload is None:
        return payload

    evaluation_payload = payload.get(
        "evaluation"
    )

    if not isinstance(
        evaluation_payload,
        dict,
    ):
        raise EvaluationReportSerializationError(
            "A avaliação interna do caso possui "
            "estrutura inválida."
        )

    evaluation_payload["rag_triad"] = (
        to_json_compatible(
            triad_payload
        )
    )

    return payload


def build_batch_report(
    batch: BatchRunResult,
    *,
    quality_gate: Any | None = None,
    sanitize: bool = True,
    include_case_details: bool = True,
) -> dict[str, Any]:
    """
    Constrói o relatório oficial versionado da avaliação.

    sanitize=True gera uma projeção externa mínima e aplica
    a proteção defensiva de privacidade antes da exportação.

    sanitize=False gera o relatório interno completo.
    """

    cases: list[dict[str, Any]] = []

    if include_case_details:
        if sanitize:
            cases = [
                _safe_external_case_report(
                    case_result
                )
                for case_result
                in batch.case_results
            ]
        else:
            cases = [
                _internal_case_report(
                    case_result
                )
                for case_result
                in batch.case_results
            ]

    payload: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_type": "inna-evaluation-batch",
        "generated_at": (
            None
            if sanitize
            else datetime.now(
                batch.started_at.tzinfo
            ).isoformat()
        ),
        "batch": {
            "batch_id": (
                None
                if sanitize
                else batch.batch_id
            ),
            "status": batch.status.value,
            "started_at": (
                None
                if sanitize
                else batch.started_at.isoformat()
            ),
            "finished_at": (
                None
                if sanitize
                else batch.finished_at.isoformat()
            ),
            "duration_ms": batch.duration_ms,
            "total_estimated_cost": (
                batch.total_estimated_cost
            ),
            "metadata": (
                _safe_external_batch_metadata(
                    batch.metadata
                )
                if sanitize
                else to_json_compatible(
                    batch.metadata
                )
            ),
        },
        "summary": {
            "total_cases": batch.total_cases,
            "passed_cases": batch.passed_cases,
            "failed_cases": batch.failed_cases,
            "blocked_cases": batch.blocked_cases,
            "error_cases": batch.error_cases,
            "pass_rate": batch.pass_rate,
        },
        "datasets": to_json_compatible(
            batch.dataset_summaries
        ),
        "categories": to_json_compatible(
            batch.category_summaries
        ),
        "metrics": to_json_compatible(
            batch.metric_summaries
        ),
        "cases": cases,
    }

    if quality_gate is not None:
        payload["quality_gate"] = (
            _safe_external_quality_gate(
                quality_gate
            )
            if sanitize
            else to_json_compatible(
                quality_gate
            )
        )

    if sanitize:
        sanitized = (
            _validate_external_report_projection(
                payload
            )
        )

        run_reference = (
            build_external_run_reference(
                batch.batch_id
            )
        )

        generated_date = (
            build_external_generated_date(
                batch.started_at
            )
        )

        sanitized["run_reference"] = (
            run_reference
        )
        sanitized["generated_date"] = (
            generated_date
        )

        sanitized_batch = sanitized.get(
            "batch"
        )

        if isinstance(
            sanitized_batch,
            dict,
        ):
            sanitized_batch[
                "run_reference"
            ] = run_reference

        sanitized_gate = sanitized.get(
            "quality_gate"
        )

        if isinstance(
            sanitized_gate,
            dict,
        ):
            sanitized_gate[
                "run_reference"
            ] = run_reference

        return sanitized

    return payload


def batch_report_to_json(
    batch: BatchRunResult,
    *,
    quality_gate: Any | None = None,
    sanitize: bool = True,
    include_case_details: bool = True,
    indent: int | None = 2,
) -> str:
    payload = build_batch_report(
        batch,
        quality_gate=quality_gate,
        sanitize=sanitize,
        include_case_details=include_case_details,
    )

    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
            allow_nan=False,
        )
    except (
        TypeError,
        ValueError,
    ) as exception:
        raise EvaluationReportSerializationError(
            "Não foi possível serializar o relatório."
        ) from exception


def build_report_filename(
    batch: BatchRunResult,
    *,
    prefix: str = "inna-evaluation",
) -> str:
    safe_prefix = safe_artifact_name(
        prefix,
        default="inna-evaluation",
    )

    timestamp = batch.started_at.strftime(
        "%Y%m%dT%H%M%SZ"
    )

    batch_fragment = batch.batch_id[:12]

    return (
        f"{safe_prefix}-{timestamp}-"
        f"{batch_fragment}.json"
    )


def write_batch_report(
    batch: BatchRunResult,
    *,
    output_directory: str | Path = (
        "artifacts/evaluations"
    ),
    quality_gate: Any | None = None,
    sanitize: bool = True,
    include_case_details: bool = True,
    indent: int | None = 2,
    filename: str | None = None,
) -> Path:
    directory = Path(output_directory)

    try:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exception:
        raise EvaluationReportWriteError(
            "Não foi possível criar o diretório "
            "dos relatórios."
        ) from exception

    resolved_filename = (
        safe_artifact_name(
            filename,
            default=build_report_filename(batch),
            max_length=180,
        )
        if filename is not None
        else build_report_filename(batch)
    )

    if not resolved_filename.endswith(".json"):
        resolved_filename = (
            f"{resolved_filename}.json"
        )

    destination = (
        directory / resolved_filename
    )

    content = batch_report_to_json(
        batch,
        quality_gate=quality_gate,
        sanitize=sanitize,
        include_case_details=include_case_details,
        indent=indent,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    try:
        temporary.write_text(
            content,
            encoding="utf-8",
        )

        temporary.replace(destination)
    except OSError as exception:
        try:
            temporary.unlink(
                missing_ok=True
            )
        except OSError:
            pass

        raise EvaluationReportWriteError(
            "Não foi possível gravar o relatório "
            "de avaliação."
        ) from exception

    return destination


__all__ = [
    "EvaluationReportSerializationError",
    "EvaluationReportWriteError",
    "EvaluationReportingError",
    "REPORT_SCHEMA_VERSION",
    "batch_report_to_json",
    "build_batch_report",
    "build_external_generated_date",
    "build_external_run_reference",
    "build_report_filename",
    "to_json_compatible",
    "write_batch_report",
]
