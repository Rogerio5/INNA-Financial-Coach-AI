"""Repara as seções incorporadas do gerador de relacionamentos."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

GENERATOR_PATH = ROOT / "scripts" / "add_technology_relationship_index.py"

RELATIONSHIP_PATH = ROOT / "src" / "platform_technology_relationships.py"

DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_technology_solution_details.py"
)

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_technology_relationships.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / (
        "repair_technology_relationship_generator_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


def extract_segment(
    source: str,
    start_marker: str,
    end_marker: str,
) -> tuple[int, int, str]:
    """Localiza uma seção incorporada no gerador."""

    marker_position = source.find(start_marker)

    if marker_position == -1:
        raise RuntimeError(f"Marcador inicial não encontrado: {start_marker}")

    content_start = marker_position + len(start_marker)

    content_end = source.find(
        end_marker,
        content_start,
    )

    if content_end == -1:
        raise RuntimeError(f"Marcador final não encontrado: {end_marker}")

    return (
        content_start,
        content_end,
        source[content_start:content_end],
    )


def replace_in_segment(
    segment: str,
    old: str,
    new: str,
    label: str,
) -> str:
    """Aplica uma substituição somente na seção correta."""

    if new in segment:
        print(f"{label}=ALREADY_FIXED")
        return segment

    old_count = segment.count(old)

    if old_count == 1:
        print(f"{label}=FIXED")

        return segment.replace(
            old,
            new,
            1,
        )

    if old_count > 1:
        raise RuntimeError(
            f"{label}: trecho repetido {old_count} vezes na mesma seção."
        )

    raise RuntimeError(f"{label}: trecho esperado não encontrado.")


def replace_segment(
    source: str,
    start_marker: str,
    end_marker: str,
    replacements: tuple[
        tuple[str, str, str],
        ...,
    ],
) -> str:
    """Corrige somente o conteúdo entre dois marcadores."""

    start, end, segment = extract_segment(
        source,
        start_marker,
        end_marker,
    )

    for old, new, label in replacements:
        segment = replace_in_segment(
            segment,
            old,
            new,
            label,
        )

    return source[:start] + segment + source[end:]


def validate_files() -> None:
    """Confirma os arquivos necessários."""

    for path in (
        GENERATOR_PATH,
        RELATIONSHIP_PATH,
        DETAILS_PATH,
        TEST_PATH,
    ):
        if not path.exists():
            raise RuntimeError(f"Arquivo não encontrado: {path}")

    print("RELATIONSHIP_GENERATOR_REPAIR_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup antes da correção."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        GENERATOR_PATH,
        RELATIONSHIP_PATH,
        DETAILS_PATH,
        TEST_PATH,
    ):
        shutil.copy2(
            path,
            BACKUP_ROOT / path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")
    print("BACKUP_FILES=4")


RELATIONSHIP_SOURCE_REPLACEMENTS = (
    (
        """from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTIONS,
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
    PlatformTechnologySolution,
)
""",
        """from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTION_BY_ID,
    PLATFORM_TECHNOLOGY_SOLUTIONS,
)
""",
        "GENERATOR_RELATIONSHIP_PLATFORM_IMPORT",
    ),
    (
        """def technology_dependencies_for(
    solution_id: str,
) -> tuple[PlatformTechnologySolution, ...]:
    \"""Retorna os módulos utilizados pela solução.\"""

    target_ids = {
        relationship.target_solution_id
        for relationship in technology_relationships_from(
            solution_id
        )
    }

    return tuple(
        solution
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        if solution.solution_id in target_ids
    )
""",
        """def technology_dependencies_for(
    solution_id: str,
) -> tuple[str, ...]:
    \"""Retorna os IDs dos módulos utilizados pela solução.\"""

    return tuple(
        dict.fromkeys(
            relationship.target_solution_id
            for relationship in technology_relationships_from(
                solution_id
            )
        )
    )
""",
        "GENERATOR_RELATIONSHIP_DEPENDENCIES",
    ),
    (
        """def technology_dependents_for(
    solution_id: str,
) -> tuple[PlatformTechnologySolution, ...]:
    \"""Retorna os módulos que utilizam a solução.\"""

    source_ids = {
        relationship.source_solution_id
        for relationship in technology_relationships_to(
            solution_id
        )
    }

    return tuple(
        solution
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
        if solution.solution_id in source_ids
    )
""",
        """def technology_dependents_for(
    solution_id: str,
) -> tuple[str, ...]:
    \"""Retorna os IDs dos módulos que utilizam a solução.\"""

    return tuple(
        dict.fromkeys(
            relationship.source_solution_id
            for relationship in technology_relationships_to(
                solution_id
            )
        )
    )
""",
        "GENERATOR_RELATIONSHIP_DEPENDENTS",
    ),
    (
        """    solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )
""",
        """    technology_solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )

    platform_module_ids = set(
        PLATFORM_MODULE_BY_ID
    )
""",
        "GENERATOR_RELATIONSHIP_VALIDATION_SETS",
    ),
    (
        """        if (
            relationship.source_solution_id
            not in solution_ids
        ):
""",
        """        if (
            relationship.source_solution_id
            not in technology_solution_ids
        ):
""",
        "GENERATOR_RELATIONSHIP_SOURCE_VALIDATION",
    ),
    (
        """        if (
            relationship.target_solution_id
            not in solution_ids
        ):
""",
        """        if (
            relationship.target_solution_id
            not in platform_module_ids
        ):
""",
        "GENERATOR_RELATIONSHIP_TARGET_VALIDATION",
    ),
)


RENDERER_SOURCE_REPLACEMENTS = (
    (
        """def render_technology_relationship_summary(
""",
        """def _technology_relationship_label(
    module_id: str,
    language: str,
) -> str:
    \"""Cria o rótulo de um módulo conectado.\"""

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
""",
        "GENERATOR_RELATIONSHIP_LABEL_HELPER",
    ),
    (
        """    if dependencies:
        for dependency in dependencies:
            uses_column.markdown(
                f"- {dependency.icon} "
                f"**{dependency.title}**"
            )
""",
        """    if dependencies:
        for dependency_id in dependencies:
            uses_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependency_id,
                    language,
                )
            )
""",
        "GENERATOR_DEPENDENCIES_RENDERER",
    ),
    (
        """    if dependents:
        for dependent in dependents:
            used_by_column.markdown(
                f"- {dependent.icon} "
                f"**{dependent.title}**"
            )
""",
        """    if dependents:
        for dependent_id in dependents:
            used_by_column.markdown(
                "- "
                + _technology_relationship_label(
                    dependent_id,
                    language,
                )
            )
""",
        "GENERATOR_DEPENDENTS_RENDERER",
    ),
)


TEST_SOURCE_REPLACEMENTS = (
    (
        """from pathlib import Path

from src.platform_technology_relationships import (
""",
        """from pathlib import Path

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_relationships import (
""",
        "GENERATOR_TEST_PLATFORM_IMPORT",
    ),
    (
        """def test_relationships_reference_registered_solutions():
    solution_ids = set(
        PLATFORM_TECHNOLOGY_SOLUTION_BY_ID
    )

    for relationship in PLATFORM_TECHNOLOGY_RELATIONSHIPS:
        assert (
            relationship.source_solution_id
            in solution_ids
        )

        assert (
            relationship.target_solution_id
            in solution_ids
        )
""",
        """def test_relationships_reference_registered_solutions():
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
""",
        "GENERATOR_TEST_REGISTERED_TARGETS",
    ),
    (
        """    dependency_ids = {
        solution.solution_id
        for solution in technology_dependencies_for(
            relationship.source_solution_id
        )
    }

    dependent_ids = {
        solution.solution_id
        for solution in technology_dependents_for(
            relationship.target_solution_id
        )
    }
""",
        """    dependency_ids = set(
        technology_dependencies_for(
            relationship.source_solution_id
        )
    )

    dependent_ids = set(
        technology_dependents_for(
            relationship.target_solution_id
        )
    )
""",
        "GENERATOR_TEST_DIRECTIONAL_LOOKUP",
    ),
    (
        """def test_details_page_contains_relationship_summary():
""",
        """def test_cross_category_targets_are_supported():
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
""",
        "GENERATOR_TEST_CROSS_CATEGORY_TARGETS",
    ),
)


def repair_generator() -> None:
    """Corrige cada fonte incorporada separadamente."""

    source = GENERATOR_PATH.read_text(
        encoding="utf-8",
    )

    source = replace_segment(
        source,
        "RELATIONSHIP_SOURCE = '''",
        "\n'''\n\n\nRELATIONSHIP_RENDERER_SOURCE = '''",
        RELATIONSHIP_SOURCE_REPLACEMENTS,
    )

    source = replace_segment(
        source,
        "RELATIONSHIP_RENDERER_SOURCE = '''",
        "\n'''\n\n\nTEST_SOURCE = '''",
        RENDERER_SOURCE_REPLACEMENTS,
    )

    source = replace_segment(
        source,
        "TEST_SOURCE = '''",
        "\n'''\n\n\ndef validate_prerequisites()",
        TEST_SOURCE_REPLACEMENTS,
    )

    GENERATOR_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TECHNOLOGY_RELATIONSHIP_GENERATOR_REPAIRED=OK")


def validate_generator_content() -> None:
    """Confirma os recursos corrigidos no gerador."""

    source = GENERATOR_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "from src.platform_modules import PLATFORM_MODULE_BY_ID",
        "technology_solution_ids = set(",
        "platform_module_ids = set(",
        "not in platform_module_ids",
        "def _technology_relationship_label(",
        "for dependency_id in dependencies:",
        "for dependent_id in dependents:",
        "def test_cross_category_targets_are_supported():",
        'assert "document_ai" in cross_category_target_ids',
    )

    missing_tokens = tuple(token for token in required_tokens if token not in source)

    if missing_tokens:
        raise RuntimeError(f"Gerador ainda incompleto: {missing_tokens}")

    print("TECHNOLOGY_RELATIONSHIP_GENERATOR_CONTENT=OK")


validate_files()
create_backup()
repair_generator()
validate_generator_content()

print("TECHNOLOGY_RELATIONSHIP_GENERATOR_REPAIR=OK")
