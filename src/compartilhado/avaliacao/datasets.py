from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

from src.compartilhado.avaliacao.contracts import (
    ConversationTurn,
    ExpectedToolCall,
    InnaEvaluationCase,
    PrivacyLevel,
)
from src.evaluation.privacy import (
    assert_safe_for_external_export,
    content_hash,
    prepare_external_payload,
    safe_artifact_name,
)

DATASET_SCHEMA_VERSION = "1.0.0"
DEFAULT_DATASET_NAME = "inna-evaluation"
DEFAULT_DATASET_VERSION = "1.0.0"

_IDENTIFIER_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._-]{1,127}$"
)

_SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(?:0|[1-9]\d*)"
    r"\.(?:0|[1-9]\d*)"
    r"\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)


def utc_now() -> datetime:
    """Retorna o horário atual em UTC."""

    return datetime.now(UTC)


def _freeze_mapping(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Cria uma cópia rasa e imutável de um mapping."""

    return MappingProxyType(
        dict(value or {})
    )


def _normalize_identifier(
    value: str,
    *,
    field_name: str,
) -> str:
    """Normaliza e valida identificadores técnicos."""

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError(
            f"{field_name} não pode estar vazio."
        )

    if not _IDENTIFIER_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} possui formato inválido: "
            f"{value!r}. Use letras minúsculas, números, "
            "ponto, hífen ou sublinhado."
        )

    return normalized


def _normalize_version(
    value: str,
    *,
    field_name: str,
) -> str:
    """Valida uma versão semântica."""

    normalized = value.strip()

    if not _SEMANTIC_VERSION_PATTERN.fullmatch(
        normalized
    ):
        raise ValueError(
            f"{field_name} deve usar versionamento "
            f"semântico. Valor recebido: {value!r}."
        )

    return normalized


def _normalize_optional_text(
    value: str | None,
) -> str | None:
    """Normaliza uma string opcional."""

    if value is None:
        return None

    normalized = value.strip()

    return normalized or None


def _normalize_string_tuple(
    values: Iterable[str] | None,
) -> tuple[str, ...]:
    """Normaliza, remove vazios e elimina duplicidades."""

    if values is None:
        return ()

    normalized_values: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = str(value).strip()

        if not normalized:
            continue

        deduplication_key = normalized.casefold()

        if deduplication_key in seen:
            continue

        seen.add(deduplication_key)
        normalized_values.append(normalized)

    return tuple(normalized_values)



def _canonicalize_fingerprint_value(
    value: Any,
) -> Any:
    """
    Converte valores para uma representação JSON canônica.

    A canonicalização garante que valores semanticamente equivalentes,
    como 5000 e 5000.0, produzam exatamente o mesmo fingerprint.

    Também ordena mappings de forma determinística e preserva booleanos
    separadamente, pois bool é uma subclasse de int em Python.
    """

    if value is None or isinstance(
        value,
        (
            str,
            bool,
        ),
    ):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                "O fingerprint não aceita valores "
                "NaN ou infinitos."
            )

        if value == 0.0:
            return 0

        if value.is_integer():
            return int(value)

        return value

    if isinstance(value, Mapping):
        return {
            str(key): _canonicalize_fingerprint_value(
                nested_value
            )
            for key, nested_value in sorted(
                value.items(),
                key=lambda item: str(item[0]),
            )
        }

    if isinstance(
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
        return [
            _canonicalize_fingerprint_value(item)
            for item in value
        ]

    if isinstance(value, PrivacyLevel):
        return value.value

    return str(value)



def _require_mapping(
    value: Any,
    *,
    field_name: str,
    allow_none: bool = True,
) -> Mapping[str, Any]:
    """
    Valida que um valor seja um mapping.

    JSONs antigos podem omitir mappings opcionais. Nesse caso,
    None é convertido para um mapping vazio quando allow_none=True.
    """

    if value is None and allow_none:
        return {}

    if not isinstance(value, Mapping):
        raise ValueError(
            f"{field_name} deve ser um objeto JSON."
        )

    return value


def _require_sequence(
    value: Any,
    *,
    field_name: str,
    allow_none: bool = True,
) -> Sequence[Any]:
    """
    Valida listas e tuplas sem aceitar strings como sequências.
    """

    if value is None and allow_none:
        return ()

    if not isinstance(value, Sequence) or isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise ValueError(
            f"{field_name} deve ser uma lista JSON."
        )

    return value


def _parse_bool(
    value: Any,
    *,
    field_name: str,
    default: bool,
) -> bool:
    """
    Converte booleanos com validação estrita e compatibilidade
    com representações textuais antigas.
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int) and value in {
        0,
        1,
    }:
        return bool(value)

    if isinstance(value, str):
        normalized = value.strip().casefold()

        if normalized in {
            "true",
            "1",
            "yes",
            "sim",
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "nao",
            "não",
        }:
            return False

    raise ValueError(
        f"{field_name} deve ser booleano."
    )


def _parse_optional_bool(
    value: Any,
    *,
    field_name: str,
) -> bool | None:
    """Converte um booleano opcional."""

    if value is None:
        return None

    return _parse_bool(
        value,
        field_name=field_name,
        default=False,
    )


def _parse_int(
    value: Any,
    *,
    field_name: str,
    default: int,
) -> int:
    """Converte inteiros sem aceitar booleanos."""

    if value is None:
        return default

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} deve ser inteiro."
        )

    try:
        converted = int(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exception:
        raise ValueError(
            f"{field_name} deve ser inteiro."
        ) from exception

    if isinstance(value, float) and not value.is_integer():
        raise ValueError(
            f"{field_name} não aceita valor fracionário."
        )

    return converted


def _parse_optional_int(
    value: Any,
    *,
    field_name: str,
) -> int | None:
    """Converte um inteiro opcional."""

    if value is None:
        return None

    return _parse_int(
        value,
        field_name=field_name,
        default=0,
    )


def _parse_float(
    value: Any,
    *,
    field_name: str,
    default: float,
) -> float:
    """Converte números de ponto flutuante com validação."""

    if value is None:
        return default

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} deve ser numérico."
        )

    try:
        converted = float(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exception:
        raise ValueError(
            f"{field_name} deve ser numérico."
        ) from exception

    if not math.isfinite(converted):
        raise ValueError(
            f"{field_name} não aceita NaN ou infinito."
        )

    return converted


def _parse_optional_float(
    value: Any,
    *,
    field_name: str,
) -> float | None:
    """Converte um número opcional."""

    if value is None:
        return None

    return _parse_float(
        value,
        field_name=field_name,
        default=0.0,
    )


def _serialize_expected_tool(
    tool: ExpectedToolCall,
) -> dict[str, Any]:
    """Serializa completamente uma expectativa de ferramenta."""

    return {
        "name": tool.name,
        "arguments": dict(tool.arguments),
        "required": tool.required,
        "allow_additional_arguments": (
            tool.allow_additional_arguments
        ),
        "call_order": tool.call_order,
        "minimum_calls": tool.minimum_calls,
        "maximum_calls": tool.maximum_calls,
        "metadata": dict(tool.metadata),
    }


def _deserialize_expected_tool(
    payload: Mapping[str, Any],
) -> ExpectedToolCall:
    """
    Reconstrói uma ferramenta com validação e compatibilidade
    com datasets antigos que não continham metadata.
    """

    arguments = _require_mapping(
        payload.get("arguments"),
        field_name="expected_tool.arguments",
    )

    metadata = _require_mapping(
        payload.get("metadata"),
        field_name="expected_tool.metadata",
    )

    return ExpectedToolCall(
        name=str(
            payload.get(
                "name",
                "",
            )
        ),
        arguments=dict(arguments),
        required=_parse_bool(
            payload.get("required"),
            field_name="expected_tool.required",
            default=True,
        ),
        allow_additional_arguments=_parse_bool(
            payload.get(
                "allow_additional_arguments"
            ),
            field_name=(
                "expected_tool."
                "allow_additional_arguments"
            ),
            default=True,
        ),
        call_order=_parse_optional_int(
            payload.get("call_order"),
            field_name="expected_tool.call_order",
        ),
        minimum_calls=_parse_int(
            payload.get("minimum_calls"),
            field_name="expected_tool.minimum_calls",
            default=1,
        ),
        maximum_calls=_parse_optional_int(
            payload.get("maximum_calls"),
            field_name="expected_tool.maximum_calls",
        ),
        metadata=dict(metadata),
    )


def _serialize_conversation_turn(
    turn: ConversationTurn,
) -> dict[str, Any]:
    """Serializa completamente um turno conversacional."""

    return {
        "role": turn.role,
        "content": turn.content,
        "turn_index": turn.turn_index,
        "expected_output": turn.expected_output,
        "expected_agent": turn.expected_agent,
        "expected_team": turn.expected_team,
        "expected_intent": turn.expected_intent,
        "expected_tools": [
            _serialize_expected_tool(tool)
            for tool in turn.expected_tools
        ],
        "metadata": dict(turn.metadata),
    }


def _deserialize_conversation_turn(
    payload: Mapping[str, Any],
) -> ConversationTurn:
    """Reconstrói um turno conversacional."""

    raw_tools = _require_sequence(
        payload.get("expected_tools"),
        field_name=(
            "conversation.expected_tools"
        ),
    )

    expected_tools: list[
        ExpectedToolCall
    ] = []

    for index, raw_tool in enumerate(raw_tools):
        if not isinstance(raw_tool, Mapping):
            raise ValueError(
                "conversation.expected_tools"
                f"[{index}] deve ser um objeto JSON."
            )

        expected_tools.append(
            _deserialize_expected_tool(
                raw_tool
            )
        )

    metadata = _require_mapping(
        payload.get("metadata"),
        field_name="conversation.metadata",
    )

    return ConversationTurn(
        role=str(
            payload.get(
                "role",
                "",
            )
        ),
        content=str(
            payload.get(
                "content",
                "",
            )
        ),
        turn_index=_parse_int(
            payload.get("turn_index"),
            field_name="conversation.turn_index",
            default=0,
        ),
        expected_output=_normalize_optional_text(
            payload.get("expected_output")
        ),
        expected_agent=_normalize_optional_text(
            payload.get("expected_agent")
        ),
        expected_team=_normalize_optional_text(
            payload.get("expected_team")
        ),
        expected_intent=_normalize_optional_text(
            payload.get("expected_intent")
        ),
        expected_tools=tuple(
            expected_tools
        ),
        metadata=dict(metadata),
    )



def evaluation_case_to_dict(
    case: InnaEvaluationCase,
) -> dict[str, Any]:
    """
    Serializa todos os campos do contrato InnaEvaluationCase.

    A manutenção desta função deve acompanhar qualquer evolução
    futura do contrato.
    """

    return {
        "case_id": case.case_id,
        "input_text": case.input_text,
        "case_version": case.case_version,
        "dataset_name": case.dataset_name,
        "dataset_version": case.dataset_version,
        "description": case.description,
        "category": case.category,
        "tags": list(case.tags),
        "conversation": [
            _serialize_conversation_turn(turn)
            for turn in case.conversation
        ],
        "expected_output": case.expected_output,
        "expected_agent": case.expected_agent,
        "expected_team": case.expected_team,
        "expected_intent": case.expected_intent,
        "expected_task_status": (
            case.expected_task_status
        ),
        "expected_tools": [
            _serialize_expected_tool(tool)
            for tool in case.expected_tools
        ],
        "forbidden_tools": list(
            case.forbidden_tools
        ),
        "expected_terms": list(
            case.expected_terms
        ),
        "forbidden_terms": list(
            case.forbidden_terms
        ),
        "expected_structured_keys": list(
            case.expected_structured_keys
        ),
        "forbidden_structured_keys": list(
            case.forbidden_structured_keys
        ),
        "expected_trace_terms": list(
            case.expected_trace_terms
        ),
        "forbidden_trace_terms": list(
            case.forbidden_trace_terms
        ),
        "expected_retrieval_terms": list(
            case.expected_retrieval_terms
        ),
        "minimum_retrieved_documents": (
            case.minimum_retrieved_documents
        ),
        "minimum_completion_score": (
            case.minimum_completion_score
        ),
        "minimum_answer_score": (
            case.minimum_answer_score
        ),
        "maximum_latency_ms": (
            case.maximum_latency_ms
        ),
        "maximum_estimated_cost": (
            case.maximum_estimated_cost
        ),
        "language": case.language,
        "currency": case.currency,
        "privacy_level": (
            case.privacy_level.value
        ),
        "external_evaluation_allowed": (
            case.external_evaluation_allowed
        ),
        "human_review_expected": (
            case.human_review_expected
        ),
        "metadata": dict(case.metadata),
    }



def evaluation_case_from_dict(
    payload: Mapping[str, Any],
) -> InnaEvaluationCase:
    """
    Reconstrói todos os campos do contrato InnaEvaluationCase.

    Campos ausentes recebem os defaults atuais para manter
    compatibilidade com datasets antigos.
    """

    if not isinstance(payload, Mapping):
        raise ValueError(
            "O caso de avaliação deve ser "
            "um objeto JSON."
        )

    raw_privacy_level = payload.get(
        "privacy_level",
        PrivacyLevel.CONFIDENTIAL.value,
    )

    try:
        privacy_level = (
            raw_privacy_level
            if isinstance(
                raw_privacy_level,
                PrivacyLevel,
            )
            else PrivacyLevel(
                str(raw_privacy_level)
                .strip()
                .casefold()
            )
        )
    except ValueError as exception:
        raise ValueError(
            "privacy_level inválido: "
            f"{raw_privacy_level!r}."
        ) from exception

    raw_expected_tools = _require_sequence(
        payload.get("expected_tools"),
        field_name="expected_tools",
    )

    expected_tools: list[
        ExpectedToolCall
    ] = []

    for index, raw_tool in enumerate(
        raw_expected_tools
    ):
        if not isinstance(raw_tool, Mapping):
            raise ValueError(
                f"expected_tools[{index}] deve "
                "ser um objeto JSON."
            )

        expected_tools.append(
            _deserialize_expected_tool(
                raw_tool
            )
        )

    raw_conversation = _require_sequence(
        payload.get("conversation"),
        field_name="conversation",
    )

    conversation: list[
        ConversationTurn
    ] = []

    for index, raw_turn in enumerate(
        raw_conversation
    ):
        if not isinstance(raw_turn, Mapping):
            raise ValueError(
                f"conversation[{index}] deve "
                "ser um objeto JSON."
            )

        conversation.append(
            _deserialize_conversation_turn(
                raw_turn
            )
        )

    metadata = _require_mapping(
        payload.get("metadata"),
        field_name="metadata",
    )

    return InnaEvaluationCase(
        case_id=str(
            payload.get(
                "case_id",
                "",
            )
        ),
        input_text=str(
            payload.get(
                "input_text",
                "",
            )
        ),
        case_version=str(
            payload.get(
                "case_version",
                "1.0.0",
            )
        ),
        dataset_name=str(
            payload.get(
                "dataset_name",
                DEFAULT_DATASET_NAME,
            )
        ),
        dataset_version=str(
            payload.get(
                "dataset_version",
                DEFAULT_DATASET_VERSION,
            )
        ),
        description=_normalize_optional_text(
            payload.get("description")
        ),
        category=str(
            payload.get(
                "category",
                "general",
            )
        ),
        tags=_normalize_string_tuple(
            payload.get("tags")
        ),
        conversation=tuple(
            conversation
        ),
        expected_output=_normalize_optional_text(
            payload.get("expected_output")
        ),
        expected_agent=_normalize_optional_text(
            payload.get("expected_agent")
        ),
        expected_team=_normalize_optional_text(
            payload.get("expected_team")
        ),
        expected_intent=_normalize_optional_text(
            payload.get("expected_intent")
        ),
        expected_task_status=(
            _normalize_optional_text(
                payload.get(
                    "expected_task_status"
                )
            )
        ),
        expected_tools=tuple(
            expected_tools
        ),
        forbidden_tools=_normalize_string_tuple(
            payload.get("forbidden_tools")
        ),
        expected_terms=_normalize_string_tuple(
            payload.get("expected_terms")
        ),
        forbidden_terms=_normalize_string_tuple(
            payload.get("forbidden_terms")
        ),
        expected_structured_keys=(
            _normalize_string_tuple(
                payload.get(
                    "expected_structured_keys"
                )
            )
        ),
        forbidden_structured_keys=(
            _normalize_string_tuple(
                payload.get(
                    "forbidden_structured_keys"
                )
            )
        ),
        expected_trace_terms=(
            _normalize_string_tuple(
                payload.get(
                    "expected_trace_terms"
                )
            )
        ),
        forbidden_trace_terms=(
            _normalize_string_tuple(
                payload.get(
                    "forbidden_trace_terms"
                )
            )
        ),
        expected_retrieval_terms=(
            _normalize_string_tuple(
                payload.get(
                    "expected_retrieval_terms"
                )
            )
        ),
        minimum_retrieved_documents=_parse_int(
            payload.get(
                "minimum_retrieved_documents"
            ),
            field_name=(
                "minimum_retrieved_documents"
            ),
            default=0,
        ),
        minimum_completion_score=_parse_float(
            payload.get(
                "minimum_completion_score"
            ),
            field_name=(
                "minimum_completion_score"
            ),
            default=0.0,
        ),
        minimum_answer_score=_parse_float(
            payload.get(
                "minimum_answer_score"
            ),
            field_name="minimum_answer_score",
            default=0.0,
        ),
        maximum_latency_ms=(
            _parse_optional_float(
                payload.get(
                    "maximum_latency_ms"
                ),
                field_name=(
                    "maximum_latency_ms"
                ),
            )
        ),
        maximum_estimated_cost=(
            _parse_optional_float(
                payload.get(
                    "maximum_estimated_cost"
                ),
                field_name=(
                    "maximum_estimated_cost"
                ),
            )
        ),
        language=str(
            payload.get(
                "language",
                "pt",
            )
        ),
        currency=str(
            payload.get(
                "currency",
                "BRL",
            )
        ),
        privacy_level=privacy_level,
        external_evaluation_allowed=(
            _parse_bool(
                payload.get(
                    "external_evaluation_allowed"
                ),
                field_name=(
                    "external_evaluation_allowed"
                ),
                default=False,
            )
        ),
        human_review_expected=(
            _parse_optional_bool(
                payload.get(
                    "human_review_expected"
                ),
                field_name=(
                    "human_review_expected"
                ),
            )
        ),
        metadata=dict(metadata),
    )


@dataclass(frozen=True, slots=True)
class EvaluationDataset:
    """
    Dataset versionado de casos de avaliação da INNA.

    O objeto é imutável e valida identificadores, versões e
    duplicidades durante sua construção.
    """

    name: str
    version: str
    cases: tuple[InnaEvaluationCase, ...]

    description: str = ""
    owner: str = ""
    tags: tuple[str, ...] = ()

    schema_version: str = DATASET_SCHEMA_VERSION
    created_at: datetime = field(
        default_factory=utc_now
    )
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        normalized_name = _normalize_identifier(
            self.name,
            field_name="name",
        )

        normalized_version = _normalize_version(
            self.version,
            field_name="version",
        )

        normalized_schema_version = (
            _normalize_version(
                self.schema_version,
                field_name="schema_version",
            )
        )

        normalized_cases = tuple(
            self.cases
        )

        duplicate_case_ids = _find_duplicates(
            case.case_id
            for case in normalized_cases
        )

        if duplicate_case_ids:
            raise ValueError(
                "O dataset contém case_ids duplicados: "
                + ", ".join(
                    sorted(duplicate_case_ids)
                )
            )

        for case in normalized_cases:
            if (
                case.dataset_name
                != normalized_name
            ):
                raise ValueError(
                    f"O caso {case.case_id!r} pertence ao "
                    f"dataset {case.dataset_name!r}, mas o "
                    f"catálogo atual é {normalized_name!r}."
                )

            if (
                case.dataset_version
                != normalized_version
            ):
                raise ValueError(
                    f"O caso {case.case_id!r} usa a versão "
                    f"{case.dataset_version!r}, mas o dataset "
                    f"atual usa {normalized_version!r}."
                )

        if self.created_at.tzinfo is None:
            raise ValueError(
                "created_at deve possuir timezone."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "version",
            normalized_version,
        )
        object.__setattr__(
            self,
            "schema_version",
            normalized_schema_version,
        )
        object.__setattr__(
            self,
            "cases",
            normalized_cases,
        )
        object.__setattr__(
            self,
            "description",
            self.description.strip(),
        )
        object.__setattr__(
            self,
            "owner",
            self.owner.strip(),
        )
        object.__setattr__(
            self,
            "tags",
            _normalize_string_tuple(
                self.tags
            ),
        )
        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata
            ),
        )

    def __len__(self) -> int:
        """Retorna a quantidade de casos."""

        return len(self.cases)

    def __iter__(
        self,
    ):
        """Permite iterar diretamente pelos casos."""

        return iter(self.cases)

    def __contains__(
        self,
        case_id: object,
    ) -> bool:
        """Verifica se um case_id pertence ao dataset."""

        if not isinstance(case_id, str):
            return False

        return any(
            case.case_id == case_id
            for case in self.cases
        )

    @property
    def dataset_id(self) -> str:
        """Identificador único do dataset versionado."""

        return f"{self.name}@{self.version}"

    @property
    def case_ids(self) -> tuple[str, ...]:
        """Lista ordenada de case_ids."""

        return tuple(
            case.case_id
            for case in self.cases
        )

    @property
    def categories(self) -> tuple[str, ...]:
        """Categorias presentes no dataset."""

        return tuple(
            sorted(
                {
                    case.category
                    for case in self.cases
                    if case.category
                }
            )
        )

    @property
    def privacy_levels(
        self,
    ) -> tuple[PrivacyLevel, ...]:
        """Níveis de privacidade presentes."""

        return tuple(
            sorted(
                {
                    case.privacy_level
                    for case in self.cases
                },
                key=lambda level: level.value,
            )
        )

    @property
    def fingerprint(self) -> str:
        """Hash estável do conteúdo funcional do dataset."""

        payload = {
            "name": self.name,
            "version": self.version,
            "schema_version": (
                self.schema_version
            ),
            "cases": [
                evaluation_case_to_dict(case)
                for case in self.cases
            ],
        }

        canonical_payload = (
            _canonicalize_fingerprint_value(
                payload
            )
        )

        serialized = json.dumps(
            canonical_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )

        return content_hash(serialized)

    def get_case(
        self,
        case_id: str,
    ) -> InnaEvaluationCase:
        """Obtém um caso pelo identificador."""

        for case in self.cases:
            if case.case_id == case_id:
                return case

        raise KeyError(
            f"Caso não encontrado: {case_id}"
        )

    def select(
        self,
        *,
        case_ids: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        privacy_levels: (
            Iterable[PrivacyLevel] | None
        ) = None,
        external_only: bool = False,
        human_review_only: bool = False,
    ) -> tuple[InnaEvaluationCase, ...]:
        """
        Filtra casos usando critérios combinados.

        Todos os filtros informados são aplicados com semântica AND.
        """

        selected_case_ids = (
            set(case_ids)
            if case_ids is not None
            else None
        )

        selected_categories = (
            {
                category.strip().casefold()
                for category in categories
                if category.strip()
            }
            if categories is not None
            else None
        )

        selected_privacy_levels = (
            set(privacy_levels)
            if privacy_levels is not None
            else None
        )

        selected: list[
            InnaEvaluationCase
        ] = []

        for case in self.cases:
            if (
                selected_case_ids is not None
                and case.case_id
                not in selected_case_ids
            ):
                continue

            if (
                selected_categories is not None
                and case.category.casefold()
                not in selected_categories
            ):
                continue

            if (
                selected_privacy_levels
                is not None
                and case.privacy_level
                not in selected_privacy_levels
            ):
                continue

            if (
                external_only
                and not (
                    case.external_evaluation_allowed
                )
            ):
                continue

            if (
                human_review_only
                and case.human_review_expected
                is not True
            ):
                continue

            selected.append(case)

        return tuple(selected)

    def public_cases(
        self,
    ) -> tuple[InnaEvaluationCase, ...]:
        """Retorna casos autorizados para avaliação externa."""

        return self.select(
            external_only=True
        )

    def manifest(
        self,
    ) -> dict[str, Any]:
        """Gera um manifesto resumido do dataset."""

        category_counts: dict[str, int] = {}
        privacy_counts: dict[str, int] = {}

        for case in self.cases:
            category = (
                case.category
                or "uncategorized"
            )

            category_counts[category] = (
                category_counts.get(
                    category,
                    0,
                )
                + 1
            )

            privacy_key = (
                case.privacy_level.value
            )

            privacy_counts[privacy_key] = (
                privacy_counts.get(
                    privacy_key,
                    0,
                )
                + 1
            )

        return {
            "schema_version": (
                self.schema_version
            ),
            "dataset_id": self.dataset_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "owner": self.owner,
            "tags": list(self.tags),
            "created_at": (
                self.created_at.isoformat()
            ),
            "case_count": len(self),
            "case_ids": list(
                self.case_ids
            ),
            "categories": category_counts,
            "privacy_levels": (
                privacy_counts
            ),
            "external_case_count": len(
                self.public_cases()
            ),
            "human_review_case_count": len(
                self.select(
                    human_review_only=True
                )
            ),
            "fingerprint": self.fingerprint,
            "metadata": dict(self.metadata),
        }

    def to_dict(
        self,
        *,
        include_cases: bool = True,
    ) -> dict[str, Any]:
        """Serializa o dataset."""

        payload = self.manifest()

        if include_cases:
            payload["cases"] = [
                evaluation_case_to_dict(case)
                for case in self.cases
            ]

        return payload

    def to_json(
        self,
        *,
        indent: int = 2,
        include_cases: bool = True,
    ) -> str:
        """Serializa o dataset para JSON."""

        return json.dumps(
            self.to_dict(
                include_cases=include_cases
            ),
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )

    def export_json(
        self,
        destination: str | Path,
        *,
        external_only: bool = False,
        indent: int = 2,
    ) -> Path:
        """
        Exporta o dataset para um arquivo JSON.

        Quando external_only=True, somente casos explicitamente
        autorizados para avaliação externa são incluídos e o payload
        passa pela camada de sanitização.
        """

        destination_path = Path(
            destination
        )

        if destination_path.suffix.lower() != ".json":
            destination_path = (
                destination_path.with_suffix(
                    ".json"
                )
            )

        destination_path = (
            destination_path.with_name(
                safe_artifact_name(
                    destination_path.name,
                    default=(
                        f"{self.name}-"
                        f"{self.version}.json"
                    ),
                )
            )
        )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if external_only:
            selected_cases = (
                self.public_cases()
            )

            payload = {
                **self.manifest(),
                "case_count": len(
                    selected_cases
                ),
                "case_ids": [
                    case.case_id
                    for case in selected_cases
                ],
                "cases": [
                    evaluation_case_to_dict(
                        case
                    )
                    for case in selected_cases
                ],
                "external_export": True,
            }

            payload = prepare_external_payload(
                payload
            )

            assert_safe_for_external_export(
                payload
            )
        else:
            payload = self.to_dict(
                include_cases=True
            )

        destination_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=indent,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return destination_path

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> EvaluationDataset:
        """Reconstrói um dataset a partir de um mapping."""

        raw_cases = payload.get(
            "cases",
            (),
        )

        cases = tuple(
            evaluation_case_from_dict(
                case_payload
            )
            for case_payload in raw_cases
            if isinstance(
                case_payload,
                Mapping,
            )
        )

        created_at_raw = payload.get(
            "created_at"
        )

        if created_at_raw:
            created_at = datetime.fromisoformat(
                str(created_at_raw)
            )
        else:
            created_at = utc_now()

        return cls(
            name=str(
                payload.get(
                    "name",
                    DEFAULT_DATASET_NAME,
                )
            ),
            version=str(
                payload.get(
                    "version",
                    DEFAULT_DATASET_VERSION,
                )
            ),
            cases=cases,
            description=str(
                payload.get(
                    "description",
                    "",
                )
            ),
            owner=str(
                payload.get(
                    "owner",
                    "",
                )
            ),
            tags=_normalize_string_tuple(
                payload.get("tags")
            ),
            schema_version=str(
                payload.get(
                    "schema_version",
                    DATASET_SCHEMA_VERSION,
                )
            ),
            created_at=created_at,
            metadata=dict(
                payload.get(
                    "metadata",
                    {},
                )
            ),
        )

    @classmethod
    def from_json(
        cls,
        source: str | bytes,
    ) -> EvaluationDataset:
        """Reconstrói um dataset a partir de JSON."""

        if isinstance(source, bytes):
            source = source.decode(
                "utf-8"
            )

        payload = json.loads(source)

        if not isinstance(payload, Mapping):
            raise ValueError(
                "O JSON do dataset deve conter "
                "um objeto na raiz."
            )

        return cls.from_dict(payload)

    @classmethod
    def load_json(
        cls,
        source: str | Path,
    ) -> EvaluationDataset:
        """Carrega um dataset de um arquivo JSON."""

        source_path = Path(source)

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Dataset não encontrado: "
                f"{source_path}"
            )

        return cls.from_json(
            source_path.read_text(
                encoding="utf-8"
            )
        )


def _find_duplicates(
    values: Iterable[str],
) -> set[str]:
    """Retorna valores duplicados."""

    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return duplicates


class DatasetRegistry:
    """
    Registro em memória de datasets versionados.

    O registro não sobrescreve versões existentes sem autorização
    explícita.
    """

    def __init__(
        self,
        datasets: Iterable[
            EvaluationDataset
        ] = (),
    ) -> None:
        self._datasets: dict[
            str,
            EvaluationDataset,
        ] = {}

        for dataset in datasets:
            self.register(dataset)

    def __len__(self) -> int:
        return len(self._datasets)

    def register(
        self,
        dataset: EvaluationDataset,
        *,
        replace_existing: bool = False,
    ) -> None:
        """Registra um dataset."""

        dataset_id = dataset.dataset_id

        if (
            dataset_id in self._datasets
            and not replace_existing
        ):
            raise ValueError(
                f"Dataset já registrado: "
                f"{dataset_id}"
            )

        self._datasets[dataset_id] = dataset

    def unregister(
        self,
        name: str,
        version: str,
    ) -> EvaluationDataset:
        """Remove e retorna um dataset."""

        dataset_id = (
            f"{name.strip().lower()}@"
            f"{version.strip()}"
        )

        try:
            return self._datasets.pop(
                dataset_id
            )
        except KeyError as exception:
            raise KeyError(
                f"Dataset não registrado: "
                f"{dataset_id}"
            ) from exception

    def get(
        self,
        name: str,
        version: str,
    ) -> EvaluationDataset:
        """Obtém um dataset específico."""

        dataset_id = (
            f"{name.strip().lower()}@"
            f"{version.strip()}"
        )

        try:
            return self._datasets[
                dataset_id
            ]
        except KeyError as exception:
            raise KeyError(
                f"Dataset não registrado: "
                f"{dataset_id}"
            ) from exception

    def versions(
        self,
        name: str,
    ) -> tuple[str, ...]:
        """Lista versões registradas de um dataset."""

        normalized_name = (
            name.strip().lower()
        )

        versions = [
            dataset.version
            for dataset in (
                self._datasets.values()
            )
            if dataset.name
            == normalized_name
        ]

        return tuple(
            sorted(
                versions,
                key=_semantic_version_key,
            )
        )

    def latest(
        self,
        name: str,
    ) -> EvaluationDataset:
        """Obtém a versão mais recente."""

        versions = self.versions(name)

        if not versions:
            raise KeyError(
                f"Nenhuma versão registrada para: "
                f"{name}"
            )

        return self.get(
            name,
            versions[-1],
        )

    def all(
        self,
    ) -> tuple[EvaluationDataset, ...]:
        """Retorna todos os datasets registrados."""

        return tuple(
            sorted(
                self._datasets.values(),
                key=lambda dataset: (
                    dataset.name,
                    _semantic_version_key(
                        dataset.version
                    ),
                ),
            )
        )


def _semantic_version_key(
    version: str,
) -> tuple[int, int, int, str]:
    """Cria uma chave simples para ordenar SemVer."""

    core_and_suffix = version.split(
        "+",
        maxsplit=1,
    )[0]

    core, separator, prerelease = (
        core_and_suffix.partition("-")
    )

    major, minor, patch = (
        int(part)
        for part in core.split(".")
    )

    release_marker = (
        "\uffff"
        if not separator
        else prerelease
    )

    return (
        major,
        minor,
        patch,
        release_marker,
    )


def build_dataset(
    *,
    name: str,
    version: str,
    cases: Sequence[InnaEvaluationCase],
    description: str = "",
    owner: str = "",
    tags: Iterable[str] = (),
    metadata: Mapping[str, Any] | None = None,
) -> EvaluationDataset:
    """Constrói um dataset versionado."""

    return EvaluationDataset(
        name=name,
        version=version,
        cases=tuple(cases),
        description=description,
        owner=owner,
        tags=tuple(tags),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "DATASET_SCHEMA_VERSION",
    "DEFAULT_DATASET_NAME",
    "DEFAULT_DATASET_VERSION",
    "DatasetRegistry",
    "EvaluationDataset",
    "build_dataset",
    "evaluation_case_from_dict",
    "evaluation_case_to_dict",
    "utc_now",
]
