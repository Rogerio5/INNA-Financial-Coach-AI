"""Cria a página de detalhes das soluções empresariais."""

from __future__ import annotations

import importlib
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

SOURCE_PATH = ROOT / "src" / "dashboard_pages" / "platform_sector_solution_details.py"

TARGET_PATH = ROOT / "src" / "dashboard_pages" / "platform_business_solution_details.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("business_solution_details_page_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


REPLACEMENTS = (
    (
        "SECTOR",
        "BUSINESS",
    ),
    (
        "Sector",
        "Business",
    ),
    (
        "sector",
        "business",
    ),
    (
        "platform_sector_solutions",
        "platform_business_solutions",
    ),
    (
        "PlatformSectorSolution",
        "PlatformBusinessSolution",
    ),
    (
        "selected_platform_sector_solution_id",
        "selected_platform_business_solution_id",
    ),
    (
        "render_platform_sector_solution_details",
        "render_platform_business_solution_details",
    ),
    (
        "platform_sector_solution",
        "platform_business_solution",
    ),
    (
        "Soluções setoriais",
        "Soluções empresariais",
    ),
    (
        "soluções setoriais",
        "soluções empresariais",
    ),
    (
        "Solução setorial",
        "Solução empresarial",
    ),
    (
        "solução setorial",
        "solução empresarial",
    ),
)


def validate_prerequisites() -> None:
    """Valida os arquivos e registros necessários."""

    if not SOURCE_PATH.exists():
        raise RuntimeError("A página setorial de referência não foi encontrada.")

    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
    )

    if len(PLATFORM_BUSINESS_SOLUTIONS) != 12:
        raise RuntimeError(
            "Esperadas 12 soluções empresariais, "
            f"encontradas {len(PLATFORM_BUSINESS_SOLUTIONS)}."
        )

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    if total_areas != 72:
        raise RuntimeError(f"Esperadas 72 áreas, encontradas {total_areas}.")

    if total_capabilities != 215:
        raise RuntimeError(
            f"Esperados 215 submódulos, encontrados {total_capabilities}."
        )

    print("BUSINESS_DETAILS_PAGE_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup caso o destino já exista."""

    if not TARGET_PATH.exists():
        print("BUSINESS_DETAILS_PAGE_BACKUP_NOT_REQUIRED=OK")
        return

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET_PATH,
        BACKUP_ROOT / TARGET_PATH.name,
    )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")


def create_business_details_page() -> None:
    """Adapta a página setorial para soluções empresariais."""

    source = SOURCE_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "platform_sector_solutions",
        "PlatformSectorSolution",
        "platform_sector_solution",
    )

    missing_tokens = tuple(token for token in required_tokens if token not in source)

    if missing_tokens:
        raise RuntimeError(
            f"A página setorial não possui os elementos esperados: {missing_tokens}"
        )

    transformed = source

    for old, new in REPLACEMENTS:
        transformed = transformed.replace(
            old,
            new,
        )

    required_business_tokens = (
        "platform_business_solutions",
        "PlatformBusinessSolution",
        "platform_business_solution",
        "render_platform_business_solution_details",
    )

    missing_business_tokens = tuple(
        token for token in required_business_tokens if token not in transformed
    )

    if missing_business_tokens:
        raise RuntimeError(
            "A transformação não produziu os elementos esperados: "
            f"{missing_business_tokens}"
        )

    TARGET_PATH.write_text(
        transformed,
        encoding="utf-8",
    )

    print("BUSINESS_SOLUTION_DETAILS_PAGE_CREATED=OK")


def validate_created_page() -> None:
    """Importa a nova página e valida sua função principal."""

    importlib.invalidate_caches()

    module = importlib.import_module(
        "src.dashboard_pages.platform_business_solution_details"
    )

    renderer = getattr(
        module,
        "render_platform_business_solution_details",
        None,
    )

    if not callable(renderer):
        raise RuntimeError(
            "A função de renderização empresarial não foi criada corretamente."
        )

    source = TARGET_PATH.read_text(
        encoding="utf-8",
    )

    remaining_sector_terms = tuple(
        (
            line_number,
            line.strip(),
        )
        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        )
        if (
            "platform_sector" in line
            or "PlatformSector" in line
            or "selected_platform_sector" in line
        )
    )

    if remaining_sector_terms:
        raise RuntimeError(
            "Ainda existem referências técnicas setoriais "
            f"na página empresarial: {remaining_sector_terms}"
        )

    print("BUSINESS_SOLUTION_DETAILS_RENDERER=OK")


validate_prerequisites()
create_backup()
create_business_details_page()
validate_created_page()
