from __future__ import annotations

import json
import re
import unicodedata

from dataclasses import asdict
from dataclasses import is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Mapping

from src.platform_business_solutions import (
    PLATFORM_BUSINESS_SOLUTIONS,
)
from src.platform_modules import (
    PLATFORM_MODULES,
)
from src.platform_sector_solutions import (
    PLATFORM_SECTOR_SOLUTIONS,
)
from src.platform_technology_relationships import (
    PLATFORM_TECHNOLOGY_RELATIONSHIPS,
)
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTIONS,
)


ROOT = Path(__file__).resolve().parents[1]

CATALOG_PATH = (
    ROOT
    / "src"
    / "data"
    / "relationship_graph_catalog.json"
)

SCHEMA_VERSION = "1.0.0"


def _to_plain(value: Any) -> Any:
    """Converte dataclasses, enums e coleções em JSON."""

    if value is None:
        return None

    if isinstance(value, Enum):
        return _to_plain(value.value)

    if is_dataclass(value):
        return _to_plain(
            asdict(value)
        )

    if isinstance(value, Mapping):
        return {
            str(key): _to_plain(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        return [
            _to_plain(item)
            for item in value
        ]

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    return str(value)


def _pick(
    data: Mapping[str, Any],
    *names: str,
    default: Any = None,
) -> Any:
    """Obtém o primeiro campo disponível."""

    for name in names:
        value = data.get(name)

        if value not in (
            None,
            "",
            [],
            (),
            {},
        ):
            return value

    return default


def _text(
    value: Any,
    default: str = "",
) -> str:
    """Normaliza um valor para texto."""

    if value is None:
        return default

    if isinstance(value, Mapping):
        nested = _pick(
            value,
            "module_id",
            "solution_id",
            "capability_id",
            "area_id",
            "id",
            "title",
            "name",
            default=default,
        )

        return _text(
            nested,
            default,
        )

    rendered = str(value).strip()

    return rendered or default


def _normalized_key(
    value: Any,
) -> str:
    """Gera chave estável para correspondência."""

    rendered = _text(value).lower()

    rendered = "".join(
        character
        for character in unicodedata.normalize(
            "NFKD",
            rendered,
        )
        if not unicodedata.combining(character)
    )

    return re.sub(
        r"[^a-z0-9]+",
        "-",
        rendered,
    ).strip("-")


def _string_list(
    value: Any,
) -> list[str]:
    """Converte uma coleção em lista de textos."""

    if value is None:
        return []

    if not isinstance(
        value,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        value = [value]

    result: list[str] = []

    for item in value:
        rendered = _text(item)

        if rendered and rendered not in result:
            result.append(rendered)

    return result


def _normalize_capability(
    capability: Any,
) -> dict[str, Any]:
    raw = _to_plain(capability)

    if not isinstance(raw, Mapping):
        raw = {
            "title": _text(raw),
        }

    capability_id = _text(
        _pick(
            raw,
            "capability_id",
            "submodule_id",
            "id",
            "slug",
        )
    )

    title = _text(
        _pick(
            raw,
            "title",
            "name",
            "label",
        ),
        capability_id,
    )

    if not capability_id:
        capability_id = _normalized_key(
            title
        )

    return {
        "id": capability_id,
        "title": title,
        "description": _text(
            _pick(
                raw,
                "description",
                "summary",
                "purpose",
            )
        ),
        "technologies": _string_list(
            _pick(
                raw,
                "technologies",
                "connected_technologies",
                "technology_ids",
                "tools",
            )
        ),
        "status": _text(
            _pick(
                raw,
                "status",
                "implementation_status",
            )
        ),
    }


def _normalize_area(
    area: Any,
) -> dict[str, Any]:
    raw = _to_plain(area)

    if not isinstance(raw, Mapping):
        raw = {
            "title": _text(raw),
        }

    area_id = _text(
        _pick(
            raw,
            "area_id",
            "id",
            "slug",
        )
    )

    title = _text(
        _pick(
            raw,
            "title",
            "name",
            "label",
        ),
        area_id,
    )

    if not area_id:
        area_id = _normalized_key(
            title
        )

    capabilities_source = _pick(
        raw,
        "capabilities",
        "submodules",
        "features",
        default=[],
    )

    capabilities = [
        _normalize_capability(
            capability
        )
        for capability in capabilities_source
    ]

    return {
        "id": area_id,
        "title": title,
        "description": _text(
            _pick(
                raw,
                "description",
                "summary",
            )
        ),
        "capabilities": capabilities,
        "capability_count": len(
            capabilities
        ),
    }


def _base_module(
    item: Any,
    *,
    source_registry: str,
    category_fallback: str,
) -> dict[str, Any]:
    raw = _to_plain(item)

    if not isinstance(raw, Mapping):
        raw = {
            "title": _text(raw),
        }

    module_id = _text(
        _pick(
            raw,
            "module_id",
            "solution_id",
            "id",
            "slug",
        )
    )

    title = _text(
        _pick(
            raw,
            "title",
            "name",
            "label",
        ),
        module_id,
    )

    if not module_id:
        module_id = _normalized_key(
            title
        )

    areas_source = _pick(
        raw,
        "areas",
        "specialized_areas",
        default=[],
    )

    areas = [
        _normalize_area(area)
        for area in areas_source
    ]

    capability_count = sum(
        area["capability_count"]
        for area in areas
    )

    return {
        "id": module_id,
        "title": title,
        "icon": _text(
            _pick(
                raw,
                "icon",
                "emoji",
            )
        ),
        "description": _text(
            _pick(
                raw,
                "description",
                "summary",
                "purpose",
            )
        ),
        "status": _text(
            _pick(
                raw,
                "status",
                "implementation_status",
            ),
            "unknown",
        ),
        "category": _text(
            _pick(
                raw,
                "category",
                "module_category",
            ),
            category_fallback,
        ),
        "technology_family": _text(
            _pick(
                raw,
                "technology_family",
                "family",
            )
        ),
        "integration_type": _text(
            _pick(
                raw,
                "integration_type",
                "integration",
            )
        ),
        "areas": areas,
        "area_count": len(areas),
        "capability_count": (
            capability_count
        ),
        "source_registries": [
            source_registry
        ],
    }


def _merge_module(
    current: dict[str, Any],
    incoming: dict[str, Any],
) -> dict[str, Any]:
    """Combina metadados e estrutura detalhada."""

    merged = dict(current)

    for key in (
        "title",
        "icon",
        "description",
        "status",
        "category",
        "technology_family",
        "integration_type",
    ):
        incoming_value = incoming.get(key)
        current_value = merged.get(key)

        if (
            incoming_value
            and incoming_value != "unknown"
            and (
                not current_value
                or current_value == "unknown"
            )
        ):
            merged[key] = incoming_value

    incoming_areas = incoming.get(
        "areas",
        [],
    )

    if incoming_areas:
        merged["areas"] = incoming_areas
        merged["area_count"] = incoming[
            "area_count"
        ]
        merged["capability_count"] = incoming[
            "capability_count"
        ]

    registries = list(
        merged.get(
            "source_registries",
            [],
        )
    )

    for registry in incoming.get(
        "source_registries",
        [],
    ):
        if registry not in registries:
            registries.append(registry)

    merged["source_registries"] = registries

    return merged


def _relationship_endpoint(
    value: Any,
) -> str:
    if isinstance(value, Mapping):
        return _text(
            _pick(
                value,
                "module_id",
                "solution_id",
                "id",
                "slug",
                "title",
            )
        )

    return _text(value)


def build_relationship_graph_catalog() -> dict[str, Any]:
    """Monta catálogo real para o grafo da INNA."""

    modules_by_id: dict[
        str,
        dict[str, Any],
    ] = {}

    title_index: dict[
        str,
        str,
    ] = {}

    def register_module(
        item: Any,
        *,
        source_registry: str,
        category_fallback: str,
    ) -> None:
        normalized = _base_module(
            item,
            source_registry=source_registry,
            category_fallback=(
                category_fallback
            ),
        )

        module_id = normalized["id"]

        title_key = _normalized_key(
            normalized["title"]
        )

        matched_id = module_id

        if module_id not in modules_by_id:
            existing_title_id = (
                title_index.get(title_key)
            )

            if existing_title_id:
                matched_id = (
                    existing_title_id
                )

        normalized["id"] = matched_id

        if matched_id in modules_by_id:
            modules_by_id[matched_id] = (
                _merge_module(
                    modules_by_id[
                        matched_id
                    ],
                    normalized,
                )
            )
        else:
            modules_by_id[matched_id] = (
                normalized
            )

        title_index[title_key] = (
            matched_id
        )

    for item in PLATFORM_MODULES:
        register_module(
            item,
            source_registry=(
                "platform_modules"
            ),
            category_fallback=(
                "platform"
            ),
        )

    for item in PLATFORM_TECHNOLOGY_SOLUTIONS:
        register_module(
            item,
            source_registry=(
                "platform_technology_solutions"
            ),
            category_fallback=(
                "technology"
            ),
        )

    for item in PLATFORM_BUSINESS_SOLUTIONS:
        register_module(
            item,
            source_registry=(
                "platform_business_solutions"
            ),
            category_fallback=(
                "business"
            ),
        )

    for item in PLATFORM_SECTOR_SOLUTIONS:
        register_module(
            item,
            source_registry=(
                "platform_sector_solutions"
            ),
            category_fallback=(
                "sector"
            ),
        )

    normalized_id_index = {
        _normalized_key(module_id): module_id
        for module_id in modules_by_id
    }

    normalized_title_index = {
        _normalized_key(
            module["title"]
        ): module_id
        for module_id, module
        in modules_by_id.items()
    }

    def resolve_module_id(
        candidate: Any,
    ) -> str | None:
        rendered = _relationship_endpoint(
            candidate
        )

        if rendered in modules_by_id:
            return rendered

        normalized = _normalized_key(
            rendered
        )

        return (
            normalized_id_index.get(
                normalized
            )
            or normalized_title_index.get(
                normalized
            )
        )

    relationships: list[
        dict[str, Any]
    ] = []

    relationship_keys: set[
        tuple[str, str, str]
    ] = set()

    for module_id in modules_by_id:
        relationships.append(
            {
                "id": (
                    f"inna-platform--{module_id}"
                ),
                "source": "inna-platform",
                "target": module_id,
                "type": "contains",
                "label": "Módulo da plataforma",
                "source_registry": (
                    "platform_modules"
                ),
            }
        )

    skipped_relationships = 0

    for relationship in (
        PLATFORM_TECHNOLOGY_RELATIONSHIPS
    ):
        raw = _to_plain(
            relationship
        )

        if not isinstance(raw, Mapping):
            skipped_relationships += 1
            continue

        source = resolve_module_id(
            _pick(
                raw,
                "source_id",
                "source_module_id",
                "source_solution_id",
                "source",
                "from_id",
            )
        )

        target = resolve_module_id(
            _pick(
                raw,
                "target_id",
                "target_module_id",
                "target_solution_id",
                "target",
                "to_id",
            )
        )

        relationship_type = _text(
            _pick(
                raw,
                "relationship_type",
                "relation_type",
                "kind",
                "type",
                "label",
            ),
            "depends_on",
        )

        if (
            not source
            or not target
            or source == target
        ):
            skipped_relationships += 1
            continue

        key = (
            source,
            target,
            relationship_type,
        )

        if key in relationship_keys:
            continue

        relationship_keys.add(key)

        relationships.append(
            {
                "id": (
                    f"{source}--"
                    f"{relationship_type}--"
                    f"{target}"
                ),
                "source": source,
                "target": target,
                "type": relationship_type,
                "label": relationship_type.replace(
                    "_",
                    " ",
                ),
                "description": _text(
                    _pick(
                        raw,
                        "description",
                        "summary",
                    )
                ),
                "source_registry": (
                    "platform_technology_relationships"
                ),
            }
        )

    modules = sorted(
        modules_by_id.values(),
        key=lambda module: (
            module["category"],
            module["title"].lower(),
        ),
    )

    categories: dict[
        str,
        int,
    ] = {}

    for module in modules:
        category = (
            module["category"]
            or "unknown"
        )

        categories[category] = (
            categories.get(
                category,
                0,
            )
            + 1
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "root": {
            "id": "inna-platform",
            "title": "INNA AI Platform",
            "icon": "🧠",
            "description": (
                "Plataforma modular de inteligência "
                "artificial, dados, automação, "
                "governança e experiências digitais."
            ),
            "kind": "platform",
        },
        "modules": modules,
        "relationships": relationships,
        "statistics": {
            "module_count": len(
                modules
            ),
            "relationship_count": len(
                relationships
            ),
            "explicit_relationship_count": sum(
                1
                for relationship
                in relationships
                if relationship[
                    "source_registry"
                ]
                == (
                    "platform_technology_relationships"
                )
            ),
            "skipped_relationship_count": (
                skipped_relationships
            ),
            "area_count": sum(
                module["area_count"]
                for module in modules
            ),
            "capability_count": sum(
                module[
                    "capability_count"
                ]
                for module in modules
            ),
            "categories": categories,
        },
        "sources": [
            "src.platform_modules",
            (
                "src."
                "platform_technology_solutions"
            ),
            (
                "src."
                "platform_business_solutions"
            ),
            (
                "src."
                "platform_sector_solutions"
            ),
            (
                "src."
                "platform_technology_relationships"
            ),
        ],
    }


def validate_relationship_graph_catalog(
    catalog: Mapping[str, Any],
) -> None:
    """Valida IDs, nós e conexões."""

    modules = catalog.get(
        "modules",
        [],
    )

    if not modules:
        raise RuntimeError(
            "Nenhum módulo foi encontrado."
        )

    module_ids = [
        module["id"]
        for module in modules
    ]

    if len(module_ids) != len(
        set(module_ids)
    ):
        raise RuntimeError(
            "Foram encontrados IDs duplicados."
        )

    valid_ids = {
        "inna-platform",
        *module_ids,
    }

    for module in modules:
        if not module.get("title"):
            raise RuntimeError(
                "Módulo sem título: "
                + module["id"]
            )

    for relationship in catalog.get(
        "relationships",
        [],
    ):
        source = relationship.get(
            "source"
        )

        target = relationship.get(
            "target"
        )

        if source not in valid_ids:
            raise RuntimeError(
                "Origem inexistente: "
                + str(source)
            )

        if target not in valid_ids:
            raise RuntimeError(
                "Destino inexistente: "
                + str(target)
            )


def write_relationship_graph_catalog(
    path: Path = CATALOG_PATH,
) -> dict[str, Any]:
    """Gera e grava o catálogo em JSON."""

    catalog = (
        build_relationship_graph_catalog()
    )

    validate_relationship_graph_catalog(
        catalog
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            catalog,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return catalog


if __name__ == "__main__":
    generated_catalog = (
        write_relationship_graph_catalog()
    )

    statistics = generated_catalog[
        "statistics"
    ]

    print(
        f"CATALOG_PATH={CATALOG_PATH}"
    )

    print(
        "MODULE_COUNT="
        f"{statistics['module_count']}"
    )

    print(
        "AREA_COUNT="
        f"{statistics['area_count']}"
    )

    print(
        "CAPABILITY_COUNT="
        f"{statistics['capability_count']}"
    )

    print(
        "RELATIONSHIP_COUNT="
        f"{statistics['relationship_count']}"
    )

    print(
        "EXPLICIT_RELATIONSHIP_COUNT="
        f"{statistics['explicit_relationship_count']}"
    )

    print(
        "SKIPPED_RELATIONSHIP_COUNT="
        f"{statistics['skipped_relationship_count']}"
    )

    print(
        "CATEGORIES="
        + json.dumps(
            statistics["categories"],
            ensure_ascii=False,
            sort_keys=True,
        )
    )

    print(
        "RELATIONSHIP_GRAPH_REAL_CATALOG=OK"
    )
