from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MetadataAvailability(StrEnum):
    """Disponibilidade de um metadado no histórico."""

    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ExperimentMetadataField:
    """Definição estável de um campo experimental RAG."""

    key: str
    category: str
    label: str
    description: str
    value_type: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "category": self.category,
            "label": self.label,
            "description": self.description,
            "value_type": self.value_type,
        }


@dataclass(frozen=True, slots=True)
class ExperimentMetadataValue:
    """Valor normalizado de um campo em uma execução."""

    key: str
    label: str
    category: str
    value: Any
    available: bool
    display_value: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "category": self.category,
            "value": self.value,
            "available": self.available,
            "display_value": self.display_value,
        }


@dataclass(frozen=True, slots=True)
class ExperimentMetadataReadiness:
    """Cobertura de um campo em todo o histórico analisado."""

    key: str
    label: str
    category: str
    availability: MetadataAvailability
    available_runs: int
    total_runs: int
    coverage_rate: float
    distinct_values: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "category": self.category,
            "availability": self.availability.value,
            "available_runs": self.available_runs,
            "total_runs": self.total_runs,
            "coverage_rate": self.coverage_rate,
            "distinct_values": list(
                self.distinct_values
            ),
        }


EXPERIMENT_METADATA_FIELDS: tuple[
    ExperimentMetadataField,
    ...,
] = (
    ExperimentMetadataField(
        key="retrieval_strategy",
        category="retrieval",
        label="Estratégia de busca",
        description=(
            "Estratégia usada para recuperar os chunks, "
            "como híbrida, vetorial ou lexical."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="reranker_enabled",
        category="retrieval",
        label="Reranker",
        description=(
            "Indica se a etapa de reranking estava habilitada."
        ),
        value_type="boolean",
    ),
    ExperimentMetadataField(
        key="top_k",
        category="retrieval",
        label="Top K",
        description=(
            "Quantidade máxima de chunks recuperados."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="model_name",
        category="generation",
        label="Modelo",
        description=(
            "Modelo generativo utilizado na execução."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="prompt_version",
        category="generation",
        label="Versão do prompt",
        description=(
            "Versão do prompt RAG aplicada na execução."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="temperature",
        category="generation",
        label="Temperatura",
        description=(
            "Temperatura configurada para o modelo."
        ),
        value_type="number",
    ),
    ExperimentMetadataField(
        key="max_output_tokens",
        category="generation",
        label="Limite de tokens",
        description=(
            "Limite máximo de tokens de saída."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="embedding_model",
        category="knowledge",
        label="Modelo de embedding",
        description=(
            "Modelo usado para gerar os embeddings."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="knowledge_base_version",
        category="knowledge",
        label="Versão da base",
        description=(
            "Versão da base de conhecimento avaliada."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="chunk_size",
        category="knowledge",
        label="Tamanho do chunk",
        description=(
            "Tamanho configurado para os chunks."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="chunk_overlap",
        category="knowledge",
        label="Sobreposição dos chunks",
        description=(
            "Quantidade de sobreposição entre chunks."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="dataset_name",
        category="evaluation",
        label="Dataset",
        description=(
            "Dataset utilizado durante a avaliação."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="language",
        category="evaluation",
        label="Idioma",
        description=(
            "Idioma principal da execução avaliada."
        ),
        value_type="text",
    ),
    ExperimentMetadataField(
        key="latency_ms",
        category="performance",
        label="Latência",
        description=(
            "Latência total ou média registrada em milissegundos."
        ),
        value_type="milliseconds",
    ),
    ExperimentMetadataField(
        key="input_tokens",
        category="performance",
        label="Tokens de entrada",
        description=(
            "Quantidade de tokens de entrada consumidos."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="output_tokens",
        category="performance",
        label="Tokens de saída",
        description=(
            "Quantidade de tokens de saída consumidos."
        ),
        value_type="integer",
    ),
    ExperimentMetadataField(
        key="estimated_cost_usd",
        category="performance",
        label="Custo estimado",
        description=(
            "Custo estimado da execução em dólares."
        ),
        value_type="currency_usd",
    ),
)


_FIELD_BY_KEY = {
    field.key: field
    for field in EXPERIMENT_METADATA_FIELDS
}


_METADATA_CONTAINER_NAMES = (
    "experiment_metadata",
    "rag_metadata",
    "metadata",
)


_NESTED_METADATA_NAMES = (
    "experiment",
    "rag",
    "evaluation",
    "configuration",
    "config",
)


def _is_available(
    value: Any,
) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    return True


def _mapping_from(
    value: Any,
) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value

    return {}


def _collect_metadata_mappings(
    entry: Any,
) -> tuple[Mapping[str, Any], ...]:
    mappings: list[Mapping[str, Any]] = []

    for container_name in (
        _METADATA_CONTAINER_NAMES
    ):
        container = _mapping_from(
            getattr(
                entry,
                container_name,
                None,
            )
        )

        if not container:
            continue

        mappings.append(container)

        for nested_name in (
            _NESTED_METADATA_NAMES
        ):
            nested = _mapping_from(
                container.get(nested_name)
            )

            if nested:
                mappings.append(nested)

    return tuple(mappings)


def extract_experiment_metadata(
    entry: Any,
) -> dict[str, Any]:
    """
    Extrai metadados opcionais sem exigir migração imediata.

    A prioridade é:
    1. atributo direto da execução;
    2. experiment_metadata;
    3. rag_metadata;
    4. metadata;
    5. estruturas internas como rag, experiment ou config.
    """

    mappings = _collect_metadata_mappings(
        entry
    )

    extracted: dict[str, Any] = {}

    for field in EXPERIMENT_METADATA_FIELDS:
        direct_value = getattr(
            entry,
            field.key,
            None,
        )

        if _is_available(direct_value):
            extracted[field.key] = direct_value
            continue

        for metadata in mappings:
            value = metadata.get(field.key)

            if _is_available(value):
                extracted[field.key] = value
                break

    return extracted


def format_experiment_metadata_value(
    field: ExperimentMetadataField,
    value: Any,
    *,
    unavailable_label: str = (
        "Não registrado nesta execução"
    ),
    enabled_label: str = "Habilitado",
    disabled_label: str = "Desabilitado",
) -> str:
    if not _is_available(value):
        return unavailable_label

    if field.value_type == "boolean":
        return (
            enabled_label
            if bool(value)
            else disabled_label
        )

    if field.value_type == "milliseconds":
        try:
            return f"{float(value):,.2f} ms"
        except (TypeError, ValueError):
            return str(value)

    if field.value_type == "currency_usd":
        try:
            return f"US$ {float(value):,.6f}"
        except (TypeError, ValueError):
            return str(value)

    if field.value_type == "number":
        try:
            return f"{float(value):.4f}"
        except (TypeError, ValueError):
            return str(value)

    return str(value)


def build_experiment_metadata_snapshot(
    entry: Any,
    *,
    unavailable_label: str = (
        "Não registrado nesta execução"
    ),
    enabled_label: str = "Habilitado",
    disabled_label: str = "Desabilitado",
) -> tuple[ExperimentMetadataValue, ...]:
    metadata = extract_experiment_metadata(
        entry
    )

    return tuple(
        ExperimentMetadataValue(
            key=field.key,
            label=field.label,
            category=field.category,
            value=metadata.get(field.key),
            available=_is_available(
                metadata.get(field.key)
            ),
            display_value=(
                format_experiment_metadata_value(
                    field,
                    metadata.get(field.key),
                    unavailable_label=(
                        unavailable_label
                    ),
                    enabled_label=enabled_label,
                    disabled_label=(
                        disabled_label
                    ),
                )
            ),
        )
        for field in EXPERIMENT_METADATA_FIELDS
    )


def _normalise_distinct_value(
    field: ExperimentMetadataField,
    value: Any,
) -> str:
    return format_experiment_metadata_value(
        field,
        value,
        unavailable_label="",
    )


def build_experiment_metadata_readiness(
    history: Any,
) -> tuple[
    ExperimentMetadataReadiness,
    ...,
]:
    entries = tuple(
        getattr(
            history,
            "entries",
            (),
        )
    )

    total_runs = len(entries)
    readiness: list[
        ExperimentMetadataReadiness
    ] = []

    for field in EXPERIMENT_METADATA_FIELDS:
        available_values: list[Any] = []

        for entry in entries:
            metadata = extract_experiment_metadata(
                entry
            )

            value = metadata.get(field.key)

            if _is_available(value):
                available_values.append(value)

        available_runs = len(
            available_values
        )

        if (
            total_runs > 0
            and available_runs == total_runs
        ):
            availability = (
                MetadataAvailability.AVAILABLE
            )
        elif available_runs > 0:
            availability = (
                MetadataAvailability.PARTIAL
            )
        else:
            availability = (
                MetadataAvailability.UNAVAILABLE
            )

        coverage_rate = (
            available_runs / total_runs
            if total_runs
            else 0.0
        )

        distinct_values = tuple(
            sorted(
                {
                    _normalise_distinct_value(
                        field,
                        value,
                    )
                    for value in available_values
                }
            )
        )

        readiness.append(
            ExperimentMetadataReadiness(
                key=field.key,
                label=field.label,
                category=field.category,
                availability=availability,
                available_runs=available_runs,
                total_runs=total_runs,
                coverage_rate=coverage_rate,
                distinct_values=(
                    distinct_values
                ),
            )
        )

    return tuple(readiness)


def get_available_metadata_filter_values(
    history: Any,
    field_key: str,
) -> tuple[str, ...]:
    field = _FIELD_BY_KEY.get(
        field_key
    )

    if field is None:
        raise KeyError(
            f"Campo experimental desconhecido: "
            f"{field_key}"
        )

    values = set()

    for entry in getattr(
        history,
        "entries",
        (),
    ):
        metadata = extract_experiment_metadata(
            entry
        )

        value = metadata.get(field_key)

        if _is_available(value):
            values.add(
                _normalise_distinct_value(
                    field,
                    value,
                )
            )

    return tuple(
        sorted(values)
    )
