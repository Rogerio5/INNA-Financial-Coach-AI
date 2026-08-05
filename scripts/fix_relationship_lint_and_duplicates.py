"""Corrige compatibilidade Python 3.11 e duplicações dos relacionamentos."""

from __future__ import annotations

import ast
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATOR_PATH = ROOT / "scripts" / "add_technology_relationship_index.py"

FIX_SCRIPT_PATH = ROOT / "scripts" / "fix_technology_relationship_platform_targets.py"

PREVIOUS_REPAIR_PATH = ROOT / "scripts" / "repair_technology_relationship_generator.py"

DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_technology_solution_details.py"
)

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_technology_relationships.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("fix_relationship_lint_duplicates_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


SOURCE_INDEX_OLD = """    print(
        "TECHNOLOGY_RELATIONSHIP_SOURCE_INDEX="
        f"{len(
            relationship_module
            .TECHNOLOGY_RELATIONSHIPS_BY_SOURCE
        )}"
    )
"""

SOURCE_INDEX_NEW = """    source_index_count = len(
        relationship_module
        .TECHNOLOGY_RELATIONSHIPS_BY_SOURCE
    )

    print(
        "TECHNOLOGY_RELATIONSHIP_SOURCE_INDEX="
        f"{source_index_count}"
    )
"""

TARGET_INDEX_OLD = """    print(
        "TECHNOLOGY_RELATIONSHIP_TARGET_INDEX="
        f"{len(
            relationship_module
            .TECHNOLOGY_RELATIONSHIPS_BY_TARGET
        )}"
    )
"""

TARGET_INDEX_NEW = """    target_index_count = len(
        relationship_module
        .TECHNOLOGY_RELATIONSHIPS_BY_TARGET
    )

    print(
        "TECHNOLOGY_RELATIONSHIP_TARGET_INDEX="
        f"{target_index_count}"
    )
"""


IDEMPOTENT_REPLACE_ONCE = '''def replace_once(
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
        raise RuntimeError(
            f"{label}: estrutura repetida {old_count} vezes."
        )

    raise RuntimeError(
        f"{label}: estrutura esperada não encontrada."
    )
'''


IDEMPOTENT_REPLACE_IN_SEGMENT = '''def replace_in_segment(
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
            f"{label}: trecho repetido "
            f"{old_count} vezes na mesma seção."
        )

    raise RuntimeError(
        f"{label}: trecho esperado não encontrado."
    )
'''


def validate_files() -> None:
    """Confirma todos os arquivos utilizados."""

    required_paths = (
        GENERATOR_PATH,
        FIX_SCRIPT_PATH,
        PREVIOUS_REPAIR_PATH,
        DETAILS_PATH,
        TEST_PATH,
    )

    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Arquivo não encontrado: {path}")

    print("RELATIONSHIP_LINT_FIX_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup antes das alterações."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = (
        GENERATOR_PATH,
        FIX_SCRIPT_PATH,
        PREVIOUS_REPAIR_PATH,
        DETAILS_PATH,
        TEST_PATH,
    )

    for path in paths:
        shutil.copy2(
            path,
            BACKUP_ROOT / path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")
    print(f"BACKUP_FILES={len(paths)}")


def replace_block(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    """Substitui um bloco exato de maneira segura."""

    if new in source:
        print(f"{label}=ALREADY_FIXED")
        return source

    count = source.count(old)

    if count != 1:
        raise RuntimeError(f"{label}: bloco esperado apareceu {count} vezes.")

    print(f"{label}=FIXED")

    return source.replace(
        old,
        new,
        1,
    )


def replace_top_level_function(
    source: str,
    function_name: str,
    replacement: str,
    label: str,
) -> str:
    """Substitui uma função de nível superior usando AST."""

    tree = ast.parse(source)

    nodes = [
        node
        for node in tree.body
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == function_name
        )
    ]

    if len(nodes) != 1:
        raise RuntimeError(
            f"{label}: quantidade inesperada da função {function_name}: {len(nodes)}"
        )

    node = nodes[0]

    lines = source.splitlines(
        keepends=True,
    )

    start = node.lineno - 1
    end = node.end_lineno

    while end < len(lines) and not lines[end].strip():
        end += 1

    replacement_lines = replacement.rstrip() + "\n\n"

    updated_lines = lines[:start] + [replacement_lines] + lines[end:]

    print(f"{label}=FIXED")

    return "".join(updated_lines)


def deduplicate_top_level_functions(
    source: str,
    function_names: tuple[str, ...],
    label: str,
) -> str:
    """Remove definições repetidas e idênticas."""

    tree = ast.parse(source)

    nodes_by_name: dict[
        str,
        list[ast.FunctionDef | ast.AsyncFunctionDef],
    ] = {}

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name not in function_names:
            continue

        nodes_by_name.setdefault(
            node.name,
            [],
        ).append(node)

    lines = source.splitlines(
        keepends=True,
    )

    removal_ranges: list[tuple[int, int]] = []

    removed_count = 0

    for function_name in function_names:
        nodes = nodes_by_name.get(
            function_name,
            [],
        )

        if len(nodes) <= 1:
            continue

        first_dump = ast.dump(
            nodes[0],
            include_attributes=False,
        )

        for duplicate_node in nodes[1:]:
            duplicate_dump = ast.dump(
                duplicate_node,
                include_attributes=False,
            )

            if duplicate_dump != first_dump:
                raise RuntimeError(
                    f"Definições diferentes encontradas para {function_name}."
                )

            start = duplicate_node.lineno - 1
            end = duplicate_node.end_lineno

            while end < len(lines) and not lines[end].strip():
                end += 1

            removal_ranges.append((start, end))

            removed_count += 1

    for start, end in sorted(
        removal_ranges,
        reverse=True,
    ):
        del lines[start:end]

    print(f"{label}_REMOVED={removed_count}")

    return "".join(lines)


def extract_embedded_source(
    source: str,
    start_marker: str,
    end_marker: str,
) -> tuple[int, int, str]:
    """Extrai uma fonte Python armazenada em string."""

    marker_position = source.find(start_marker)

    if marker_position == -1:
        raise RuntimeError(f"Marcador inicial ausente: {start_marker}")

    content_start = marker_position + len(start_marker)

    content_end = source.find(
        end_marker,
        content_start,
    )

    if content_end == -1:
        raise RuntimeError(f"Marcador final ausente: {end_marker}")

    return (
        content_start,
        content_end,
        source[content_start:content_end],
    )


def replace_embedded_source(
    source: str,
    start_marker: str,
    end_marker: str,
    function_names: tuple[str, ...],
    label: str,
) -> str:
    """Remove duplicações de uma fonte incorporada."""

    start, end, embedded_source = extract_embedded_source(
        source,
        start_marker,
        end_marker,
    )

    fixed_embedded_source = deduplicate_top_level_functions(
        embedded_source,
        function_names,
        label,
    )

    return source[:start] + fixed_embedded_source + source[end:]


def fix_generator_python_compatibility() -> None:
    """Remove f-strings exclusivas do Python 3.12."""

    source = GENERATOR_PATH.read_text(
        encoding="utf-8",
    )

    source = replace_block(
        source,
        SOURCE_INDEX_OLD,
        SOURCE_INDEX_NEW,
        "GENERATOR_SOURCE_INDEX_PY311",
    )

    source = replace_block(
        source,
        TARGET_INDEX_OLD,
        TARGET_INDEX_NEW,
        "GENERATOR_TARGET_INDEX_PY311",
    )

    source = replace_embedded_source(
        source,
        "RELATIONSHIP_RENDERER_SOURCE = '''",
        "\n'''\n\n\nTEST_SOURCE = '''",
        ("_technology_relationship_label",),
        "GENERATOR_RENDERER_DUPLICATES",
    )

    source = replace_embedded_source(
        source,
        "TEST_SOURCE = '''",
        "\n'''\n\n\ndef validate_prerequisites()",
        ("test_cross_category_targets_are_supported",),
        "GENERATOR_TEST_DUPLICATES",
    )

    GENERATOR_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("RELATIONSHIP_GENERATOR_PY311_FIXED=OK")


def fix_generated_files() -> None:
    """Remove funções repetidas nos arquivos reais."""

    details_source = DETAILS_PATH.read_text(
        encoding="utf-8",
    )

    details_source = deduplicate_top_level_functions(
        details_source,
        ("_technology_relationship_label",),
        "DETAILS_FUNCTION_DUPLICATES",
    )

    DETAILS_PATH.write_text(
        details_source.rstrip() + "\n",
        encoding="utf-8",
    )

    test_source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_source = deduplicate_top_level_functions(
        test_source,
        ("test_cross_category_targets_are_supported",),
        "RELATIONSHIP_TEST_DUPLICATES",
    )

    TEST_PATH.write_text(
        test_source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("RELATIONSHIP_GENERATED_FILES_DEDUPLICATED=OK")


def fix_migration_script_idempotency() -> None:
    """Evita novas duplicações em reexecuções."""

    source = FIX_SCRIPT_PATH.read_text(
        encoding="utf-8",
    )

    source = replace_top_level_function(
        source,
        "replace_once",
        IDEMPOTENT_REPLACE_ONCE,
        "PLATFORM_TARGET_FIX_IDEMPOTENCY",
    )

    FIX_SCRIPT_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    source = PREVIOUS_REPAIR_PATH.read_text(
        encoding="utf-8",
    )

    source = replace_top_level_function(
        source,
        "replace_in_segment",
        IDEMPOTENT_REPLACE_IN_SEGMENT,
        "GENERATOR_REPAIR_IDEMPOTENCY",
    )

    PREVIOUS_REPAIR_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("RELATIONSHIP_REPAIR_SCRIPTS_IDEMPOTENT=OK")


def duplicate_function_names(
    source: str,
) -> tuple[str, ...]:
    """Retorna funções de nível superior duplicadas."""

    tree = ast.parse(source)

    function_names = [
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    return tuple(
        sorted({name for name in function_names if function_names.count(name) > 1})
    )


def validate_result() -> None:
    """Valida que os problemas foram removidos."""

    details_duplicates = duplicate_function_names(
        DETAILS_PATH.read_text(
            encoding="utf-8",
        )
    )

    test_duplicates = duplicate_function_names(
        TEST_PATH.read_text(
            encoding="utf-8",
        )
    )

    if details_duplicates:
        raise RuntimeError(f"Funções duplicadas na página: {details_duplicates}")

    if test_duplicates:
        raise RuntimeError(f"Funções duplicadas nos testes: {test_duplicates}")

    generator_source = GENERATOR_PATH.read_text(
        encoding="utf-8",
    )

    if SOURCE_INDEX_OLD in generator_source:
        raise RuntimeError("F-string incompatível de origem permanece.")

    if TARGET_INDEX_OLD in generator_source:
        raise RuntimeError("F-string incompatível de destino permanece.")

    print("RELATIONSHIP_DUPLICATE_FUNCTIONS=[]")

    print("RELATIONSHIP_PY311_COMPATIBILITY=OK")

    print("RELATIONSHIP_LINT_AND_DUPLICATE_FIX=OK")


validate_files()
create_backup()
fix_generator_python_compatibility()
fix_generated_files()
fix_migration_script_idempotency()
validate_result()
