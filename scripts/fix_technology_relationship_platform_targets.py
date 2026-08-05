"""Corrige relacionamentos tecnológicos com módulos de outras categorias."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

RELATIONSHIP_PATH = ROOT / "src" / "platform_technology_relationships.py"

DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_technology_solution_details.py"
)

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_technology_relationships.py"

GENERATOR_PATH = ROOT / "scripts" / "add_technology_relationship_index.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / (
        "fix_technology_relationship_platform_targets_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


def replace_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    """Substitui uma estrutura ou reconhece correção existente."""

    if new in source:
        print(f"{label}=ALREADY_FIXED")
        return source

    old_count = source.count(old)

    if old_count == 1:
        print(f"{label}=FIXED")

        return source.replace(
            old,
            new,
            1,
        )

    if old_count > 1:
        raise RuntimeError(f"{label}: estrutura repetida {old_count} vezes.")

    raise RuntimeError(f"{label}: estrutura esperada não encontrada.")


def validate_files() -> None:
    """Confirma os arquivos necessários."""

    for path in (
        RELATIONSHIP_PATH,
        DETAILS_PATH,
        TEST_PATH,
        GENERATOR_PATH,
    ):
        if not path.exists():
            raise RuntimeError(f"Arquivo não encontrado: {path}")

    print("TECHNOLOGY_RELATIONSHIP_FIX_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria cópias antes da correção."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in (
        RELATIONSHIP_PATH,
        DETAILS_PATH,
        TEST_PATH,
        GENERATOR_PATH,
    ):
        shutil.copy2(
            path,
            BACKUP_ROOT / path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")
    print("BACKUP_FILES=4")


RELATIONSHIP_REPLACEMENTS = (
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
        "RELATIONSHIP_PLATFORM_MODULE_IMPORT",
    ),
    (
        '''def technology_dependencies_for(
    solution_id: str,
) -> tuple[PlatformTechnologySolution, ...]:
    """Retorna os módulos utilizados pela solução."""

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
''',
        '''def technology_dependencies_for(
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
''',
        "RELATIONSHIP_DEPENDENCIES_LOOKUP",
    ),
    (
        '''def technology_dependents_for(
    solution_id: str,
) -> tuple[PlatformTechnologySolution, ...]:
    """Retorna os módulos que utilizam a solução."""

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
''',
        '''def technology_dependents_for(
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
''',
        "RELATIONSHIP_DEPENDENTS_LOOKUP",
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
        "RELATIONSHIP_VALIDATION_ID_SETS",
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
        "RELATIONSHIP_SOURCE_VALIDATION",
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
        "RELATIONSHIP_TARGET_VALIDATION",
    ),
)


DETAILS_REPLACEMENTS = (
    (
        """def render_technology_relationship_summary(
""",
        '''def _technology_relationship_label(
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
''',
        "TECHNOLOGY_RELATIONSHIP_LABEL_HELPER",
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
        "TECHNOLOGY_DEPENDENCIES_RENDERER",
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
        "TECHNOLOGY_DEPENDENTS_RENDERER",
    ),
)


TEST_REPLACEMENTS = (
    (
        """from pathlib import Path

from src.platform_technology_relationships import (
""",
        """from pathlib import Path

from src.platform_modules import PLATFORM_MODULE_BY_ID
from src.platform_technology_relationships import (
""",
        "RELATIONSHIP_TEST_PLATFORM_IMPORT",
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
        "RELATIONSHIP_TEST_REGISTERED_TARGETS",
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
        "RELATIONSHIP_TEST_DIRECTIONAL_LOOKUP",
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
        "RELATIONSHIP_TEST_CROSS_CATEGORY_TARGETS",
    ),
)


def apply_replacements(
    path: Path,
    replacements: tuple[
        tuple[str, str, str],
        ...,
    ],
) -> None:
    """Aplica alterações controladas em um arquivo."""

    source = path.read_text(
        encoding="utf-8",
    )

    for old, new, label in replacements:
        source = replace_once(
            source,
            old,
            new,
            label,
        )

    path.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )


def fix_relationship_registry() -> None:
    """Permite destinos de todo o catálogo principal."""

    apply_replacements(
        RELATIONSHIP_PATH,
        RELATIONSHIP_REPLACEMENTS,
    )

    print("TECHNOLOGY_RELATIONSHIP_REGISTRY_FIXED=OK")


def fix_details_renderer() -> None:
    """Renderiza módulos especializados ou gerais."""

    apply_replacements(
        DETAILS_PATH,
        DETAILS_REPLACEMENTS,
    )

    print("TECHNOLOGY_RELATIONSHIP_DETAILS_FIXED=OK")


def fix_tests() -> None:
    """Atualiza os testes para relações entre categorias."""

    apply_replacements(
        TEST_PATH,
        TEST_REPLACEMENTS,
    )

    print("TECHNOLOGY_RELATIONSHIP_TESTS_FIXED=OK")


def fix_generator() -> None:
    """Corrige também o script gerador original."""

    source = GENERATOR_PATH.read_text(
        encoding="utf-8",
    )

    replacements = RELATIONSHIP_REPLACEMENTS + DETAILS_REPLACEMENTS + TEST_REPLACEMENTS

    for old, new, label in replacements:
        source = replace_once(
            source,
            old,
            new,
            f"GENERATOR_{label}",
        )

    GENERATOR_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TECHNOLOGY_RELATIONSHIP_GENERATOR_FIXED=OK")


validate_files()
create_backup()
fix_relationship_registry()
fix_details_renderer()
fix_tests()
fix_generator()

print("TECHNOLOGY_RELATIONSHIP_PLATFORM_TARGET_FIX=OK")
