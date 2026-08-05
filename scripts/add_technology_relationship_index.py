"""Cria o índice bidirecional de relacionamentos tecnológicos."""

from __future__ import annotations

import importlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


RELATIONSHIP_PATH = ROOT / "src" / "platform_technology_relationships.py"

DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_technology_solution_details.py"
)

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_technology_relationships.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("technology_relationship_index_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


RELATIONSHIP_SOURCE = '''"""Índice bidirecional dos relacionamentos tecnológicos da INNA."""

from __future__ import annotations

from dataclasses import dataclass

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
    PLATFORM_TECHNOLOGY_SOLUTIONS,
)


@dataclass(frozen=True, slots=True)
class TechnologyRelationship:
    """Linha da tabela ponte entre dois módulos tecnológicos."""

    source_solution_id: str
    source_area_id: str
    source_capability_id: str
    target_solution_id: str


def _build_technology_relationships() -> tuple[
    TechnologyRelationship,
    ...,
]:
    """Cria uma linha para cada dependência de cada capacidade."""

    return tuple(
        TechnologyRelationship(
            source_solution_id=solution.solution_id,
            source_area_id=area.area_id,
            source_capability_id=capability.capability_id,
            target_solution_id=target_solution_id,
        )
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        for area in solution.areas
        for capability in area.capabilities
        for target_solution_id in (
            capability.technology_dependencies
        )
    )


PLATFORM_TECHNOLOGY_RELATIONSHIPS = (
    _build_technology_relationships()
)


def _build_relationship_index(
    *,
    use_source: bool,
) -> dict[str, tuple[TechnologyRelationship, ...]]:
    """Agrupa relacionamentos por origem ou destino."""

    buckets: dict[
        str,
        list[TechnologyRelationship],
    ] = {}

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        relationship_id = (
            relationship.source_solution_id
            if use_source
            else relationship.target_solution_id
        )

        buckets.setdefault(
            relationship_id,
            [],
        ).append(relationship)

    return {
        relationship_id: tuple(relationships)
        for relationship_id, relationships in buckets.items()
    }


TECHNOLOGY_RELATIONSHIPS_BY_SOURCE = (
    _build_relationship_index(
        use_source=True,
    )
)

TECHNOLOGY_RELATIONSHIPS_BY_TARGET = (
    _build_relationship_index(
        use_source=False,
    )
)


def technology_relationships_from(
    solution_id: str,
) -> tuple[TechnologyRelationship, ...]:
    """Retorna as linhas em que o módulo aparece como origem."""

    return TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.get(
        solution_id,
        (),
    )


def technology_relationships_to(
    solution_id: str,
) -> tuple[TechnologyRelationship, ...]:
    """Retorna as linhas em que o módulo aparece como destino."""

    return TECHNOLOGY_RELATIONSHIPS_BY_TARGET.get(
        solution_id,
        (),
    )


def technology_dependencies_for(
    solution_id: str,
) -> tuple[str, ...]:
    """Retorna os IDs dos módulos utilizados pela solução."""

    return tuple(
        dict.fromkeys(
            relationship.target_solution_id
            for relationship in technology_relationships_from(
                solution_id
            )
        )
    )


def technology_dependents_for(
    solution_id: str,
) -> tuple[str, ...]:
    """Retorna os IDs dos módulos que utilizam a solução."""

    return tuple(
        dict.fromkeys(
            relationship.source_solution_id
            for relationship in technology_relationships_to(
                solution_id
            )
        )
    )


def validate_platform_technology_relationship_registry() -> None:
    """Valida a tabela ponte e os índices bidirecionais."""

    technology_solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )

    platform_module_ids = set(
        PLATFORM_MODULE_BY_ID
    )

    capability_dependencies = {
        (
            solution.solution_id,
            area.area_id,
            capability.capability_id,
        ): set(capability.technology_dependencies)
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        for area in solution.areas
        for capability in area.capabilities
    }

    seen_relationships: set[
        tuple[str, str, str, str]
    ] = set()

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        relationship_key = (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
            relationship.target_solution_id,
        )

        if relationship_key in seen_relationships:
            raise ValueError(
                "Relacionamento tecnológico duplicado: "
                f"{relationship_key}"
            )

        seen_relationships.add(
            relationship_key
        )

        if (
            relationship.source_solution_id
            not in technology_solution_ids
        ):
            raise ValueError(
                "Módulo de origem não registrado: "
                f"{relationship.source_solution_id}"
            )

        if (
            relationship.target_solution_id
            not in platform_module_ids
        ):
            raise ValueError(
                "Módulo de destino não registrado: "
                f"{relationship.target_solution_id}"
            )

        capability_key = (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
        )

        expected_dependencies = (
            capability_dependencies.get(
                capability_key
            )
        )

        if expected_dependencies is None:
            raise ValueError(
                "Capacidade de origem não encontrada: "
                f"{capability_key}"
            )

        if (
            relationship.target_solution_id
            not in expected_dependencies
        ):
            raise ValueError(
                "Destino ausente nas dependências "
                f"da capacidade: {relationship_key}"
            )

        if (
            relationship
            not in TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.get(
                relationship.source_solution_id,
                (),
            )
        ):
            raise ValueError(
                "Relacionamento ausente no índice de origem."
            )

        if (
            relationship
            not in TECHNOLOGY_RELATIONSHIPS_BY_TARGET.get(
                relationship.target_solution_id,
                (),
            )
        ):
            raise ValueError(
                "Relacionamento ausente no índice de destino."
            )

    if not PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        raise ValueError(
            "A tabela ponte tecnológica está vazia."
        )


validate_platform_technology_relationship_registry()
'''


RELATIONSHIP_RENDERER_SOURCE = '''
TECHNOLOGY_RELATIONSHIP_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "title": "Relacionamentos tecnológicos",
        "caption": (
            "Conexões geradas automaticamente pelas dependências "
            "dos submódulos."
        ),
        "uses": "Este módulo utiliza",
        "used_by": "Este módulo é utilizado por",
        "no_uses": "Nenhuma dependência tecnológica registrada.",
        "no_used_by": "Nenhum outro módulo utiliza esta tecnologia.",
    },
    "en_us": {
        "title": "Technology relationships",
        "caption": (
            "Connections generated automatically from "
            "submodule dependencies."
        ),
        "uses": "This module uses",
        "used_by": "This module is used by",
        "no_uses": "No technology dependency is registered.",
        "no_used_by": "No other module uses this technology.",
    },
    "es": {
        "title": "Relaciones tecnológicas",
        "caption": (
            "Conexiones generadas automáticamente desde "
            "las dependencias de los submódulos."
        ),
        "uses": "Este módulo utiliza",
        "used_by": "Este módulo es utilizado por",
        "no_uses": "No hay dependencias tecnológicas registradas.",
        "no_used_by": "Ningún otro módulo utiliza esta tecnología.",
    },
}


def technology_relationship_t(
    key: str,
    language: str = "pt",
) -> str:
    """Traduz os textos dos relacionamentos tecnológicos."""

    normalized_language = (
        "en_us"
        if language == "en_gb"
        else language
    )

    language_texts = TECHNOLOGY_RELATIONSHIP_TEXTS.get(
        normalized_language,
        TECHNOLOGY_RELATIONSHIP_TEXTS["pt"],
    )

    return language_texts.get(
        key,
        TECHNOLOGY_RELATIONSHIP_TEXTS["pt"][key],
    )


def _technology_relationship_label(
    module_id: str,
    language: str,
) -> str:
    """Cria o rótulo de um módulo conectado."""

    specialized_solution = (
        platform_technology_solution(
            module_id
        )
    )

    if specialized_solution is not None:
        return (
            f"{specialized_solution.icon} "
            f"**{specialized_solution.title}**"
        )

    return (
        f"**{platform_module_t(module_id, language)}**"
    )


def render_technology_relationship_summary(
    solution_id: str,
    language: str = "pt",
) -> None:
    """Mostra os relacionamentos nos dois sentidos."""

    dependencies = technology_dependencies_for(
        solution_id
    )

    dependents = technology_dependents_for(
        solution_id
    )

    st.divider()

    st.markdown(
        "### "
        + technology_relationship_t(
            "title",
            language,
        )
    )

    st.caption(
        technology_relationship_t(
            "caption",
            language,
        )
    )

    uses_column, used_by_column = st.columns(2)

    uses_column.markdown(
        "#### 🔗 "
        + technology_relationship_t(
            "uses",
            language,
        )
        + f" ({len(dependencies)})"
    )

    if dependencies:
        for dependency_id in dependencies:
            uses_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependency_id,
                    language,
                )
            )
    else:
        uses_column.caption(
            technology_relationship_t(
                "no_uses",
                language,
            )
        )

    used_by_column.markdown(
        "#### 🔄 "
        + technology_relationship_t(
            "used_by",
            language,
        )
        + f" ({len(dependents)})"
    )

    if dependents:
        for dependent_id in dependents:
            used_by_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependent_id,
                    language,
                )
            )
    else:
        used_by_column.caption(
            technology_relationship_t(
                "no_used_by",
                language,
            )
        )

    st.divider()


'''


TEST_SOURCE = """from pathlib import Path

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_relationships import (
    PLATFORM_TECHNOLOGY_RELATIONSHIPS,
    TECHNOLOGY_RELATIONSHIPS_BY_SOURCE,
    TECHNOLOGY_RELATIONSHIPS_BY_TARGET,
    technology_dependencies_for,
    technology_dependents_for,
    validate_platform_technology_relationship_registry,
)
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
)


DETAILS_PATH = Path(
    "src/dashboard_pages/"
    "platform_technology_solution_details.py"
)


def test_technology_relationship_registry_is_valid():
    validate_platform_technology_relationship_registry()

    assert PLATFORM_TECHNOLOGY_RELATIONSHIPS


def test_technology_relationship_rows_are_unique():
    relationship_keys = {
        (
            relationship.source_solution_id,
            relationship.source_area_id,
            relationship.source_capability_id,
            relationship.target_solution_id,
        )
        for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS
    }

    assert len(relationship_keys) == len(
        PLATFORM_TECHNOLOGY_RELATIONSHIPS
    )


def test_relationships_reference_registered_solutions():
    technology_solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )

    platform_module_ids = set(
        PLATFORM_MODULE_BY_ID
    )

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        assert (
            relationship.source_solution_id
            in technology_solution_ids
        )

        assert (
            relationship.target_solution_id
            in platform_module_ids
        )


def test_directional_indexes_cover_every_relationship():
    source_total = sum(
        len(relationships)
        for relationships in (
            TECHNOLOGY_RELATIONSHIPS_BY_SOURCE.values()
        )
    )

    target_total = sum(
        len(relationships)
        for relationships in (
            TECHNOLOGY_RELATIONSHIPS_BY_TARGET.values()
        )
    )

    expected_total = len(
        PLATFORM_TECHNOLOGY_RELATIONSHIPS
    )

    assert source_total == expected_total
    assert target_total == expected_total


def test_bidirectional_lookup_returns_connected_modules():
    relationship = (
        PLATFORM_TECHNOLOGY_RELATIONSHIPS[0]
    )

    dependency_ids = set(
        technology_dependencies_for(
            relationship.source_solution_id
        )
    )

    dependent_ids = set(
        technology_dependents_for(
            relationship.target_solution_id
        )
    )

    assert (
        relationship.target_solution_id
        in dependency_ids
    )

    assert (
        relationship.source_solution_id
        in dependent_ids
    )


def test_cross_category_targets_are_supported():
    technology_solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )

    cross_category_target_ids = {
        relationship.target_solution_id
        for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS
        if (
            relationship.target_solution_id
            not in technology_solution_ids
        )
    }

    assert cross_category_target_ids
    assert "document_ai" in cross_category_target_ids


def test_details_page_contains_relationship_summary():
    source = DETAILS_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "render_technology_relationship_summary",
        "technology_dependencies_for",
        "technology_dependents_for",
        "Este módulo utiliza",
        "Este módulo é utilizado por",
    )

    for token in required_tokens:
        assert token in source
"""


def validate_prerequisites() -> None:
    """Valida os arquivos e o catálogo atual."""

    if not DETAILS_PATH.exists():
        raise RuntimeError("Página de detalhes tecnológicos não encontrada.")

    from src.platform_technology_solutions import (
        PLATFORM_TECHNOLOGY_SOLUTIONS,
    )

    if len(PLATFORM_TECHNOLOGY_SOLUTIONS) != 56:
        raise RuntimeError("O registro tecnológico não possui 56 soluções.")

    total_areas = sum(len(solution.areas) for solution in PLATFORM_TECHNOLOGY_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    )

    if total_areas != 392:
        raise RuntimeError(f"Total inesperado de áreas: {total_areas}")

    if total_capabilities != 1176:
        raise RuntimeError(f"Total inesperado de capacidades: {total_capabilities}")

    print("TECHNOLOGY_RELATIONSHIP_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup dos arquivos que serão alterados."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    copied_files = 0

    for path in (
        DETAILS_PATH,
        RELATIONSHIP_PATH,
        TEST_PATH,
    ):
        if not path.exists():
            continue

        shutil.copy2(
            path,
            BACKUP_ROOT / path.name,
        )

        copied_files += 1

    print(f"BACKUP_CREATED={BACKUP_ROOT}")
    print(f"BACKUP_FILES={copied_files}")


def create_relationship_registry() -> None:
    """Cria a tabela ponte tecnológica."""

    if RELATIONSHIP_PATH.exists():
        source = RELATIONSHIP_PATH.read_text(
            encoding="utf-8",
        )

        required_tokens = (
            "TechnologyRelationship",
            "PLATFORM_TECHNOLOGY_RELATIONSHIPS",
            "TECHNOLOGY_RELATIONSHIPS_BY_SOURCE",
            "TECHNOLOGY_RELATIONSHIPS_BY_TARGET",
            "technology_dependencies_for",
            "technology_dependents_for",
        )

        if all(token in source for token in required_tokens):
            print("TECHNOLOGY_RELATIONSHIP_REGISTRY_ALREADY_PRESENT=OK")
            return

        raise RuntimeError(
            "O arquivo de relacionamentos já existe, "
            "mas possui uma estrutura inesperada."
        )

    RELATIONSHIP_PATH.write_text(
        RELATIONSHIP_SOURCE,
        encoding="utf-8",
    )

    print("TECHNOLOGY_RELATIONSHIP_REGISTRY_CREATED=OK")


def connect_relationships_to_details() -> None:
    """Adiciona os relacionamentos à página tecnológica."""

    source = DETAILS_PATH.read_text(
        encoding="utf-8",
    )

    relationship_import = """from src.platform_technology_relationships import (
    technology_dependencies_for,
    technology_dependents_for,
)
"""

    technology_import_anchor = "from src.platform_technology_solutions import (\n"

    if relationship_import not in source:
        import_position = source.find(technology_import_anchor)

        if import_position == -1:
            raise RuntimeError("Importação das soluções tecnológicas não encontrada.")

        source = (
            source[:import_position] + relationship_import + source[import_position:]
        )

    helper_anchor = "def clear_selected_technology_solution()"

    if "def render_technology_relationship_summary(" not in source:
        helper_position = source.find(helper_anchor)

        if helper_position == -1:
            raise RuntimeError(
                "Função de limpeza da seleção tecnológica não encontrada."
            )

        source = (
            source[:helper_position]
            + RELATIONSHIP_RENDERER_SOURCE
            + source[helper_position:]
        )

    render_anchor = """    st.subheader(detail.title)
    st.write(detail.description)
"""

    render_replacement = """    st.subheader(detail.title)
    st.write(detail.description)

    render_technology_relationship_summary(
        solution.solution_id,
        language,
    )
"""

    if (
        "render_technology_relationship_summary(\n"
        "        solution.solution_id," not in source
    ):
        if render_anchor not in source:
            raise RuntimeError("Ponto de renderização da descrição não encontrado.")

        source = source.replace(
            render_anchor,
            render_replacement,
            1,
        )

    required_tokens = (
        "technology_dependencies_for",
        "technology_dependents_for",
        "TECHNOLOGY_RELATIONSHIP_TEXTS",
        "render_technology_relationship_summary",
        "solution.solution_id",
    )

    missing_tokens = tuple(token for token in required_tokens if token not in source)

    if missing_tokens:
        raise RuntimeError(f"Integração visual incompleta: {missing_tokens}")

    DETAILS_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TECHNOLOGY_RELATIONSHIP_DETAILS_CONNECTED=OK")


def create_tests() -> None:
    """Cria os testes do índice de relacionamentos."""

    if TEST_PATH.exists():
        source = TEST_PATH.read_text(
            encoding="utf-8",
        )

        if "test_bidirectional_lookup_returns_connected_modules" in source:
            print("TECHNOLOGY_RELATIONSHIP_TESTS_ALREADY_PRESENT=OK")
            return

        raise RuntimeError(
            "O arquivo de testes já existe, mas possui uma estrutura inesperada."
        )

    TEST_PATH.write_text(
        TEST_SOURCE,
        encoding="utf-8",
    )

    print("TECHNOLOGY_RELATIONSHIP_TESTS_CREATED=OK")


def validate_result() -> None:
    """Importa e valida o índice criado."""

    importlib.invalidate_caches()

    relationship_module = importlib.import_module(
        "src.platform_technology_relationships"
    )

    relationship_module.validate_platform_technology_relationship_registry()

    relationships = relationship_module.PLATFORM_TECHNOLOGY_RELATIONSHIPS

    unique_module_connections = {
        (
            relationship.source_solution_id,
            relationship.target_solution_id,
        )
        for relationship in relationships
    }

    details_module = importlib.reload(
        importlib.import_module(
            "src.dashboard_pages.platform_technology_solution_details"
        )
    )

    assert relationships

    assert callable(details_module.render_technology_relationship_summary)

    print(f"TECHNOLOGY_RELATIONSHIP_ROWS={len(relationships)}")

    print(f"TECHNOLOGY_UNIQUE_MODULE_CONNECTIONS={len(unique_module_connections)}")

    source_index_count = len(relationship_module.TECHNOLOGY_RELATIONSHIPS_BY_SOURCE)

    print(f"TECHNOLOGY_RELATIONSHIP_SOURCE_INDEX={source_index_count}")

    target_index_count = len(relationship_module.TECHNOLOGY_RELATIONSHIPS_BY_TARGET)

    print(f"TECHNOLOGY_RELATIONSHIP_TARGET_INDEX={target_index_count}")

    print("TECHNOLOGY_BIDIRECTIONAL_RELATIONSHIP_INDEX_VALIDATED=OK")


validate_prerequisites()
create_backup()
create_relationship_registry()
connect_relationships_to_details()
create_tests()
validate_result()
