"""Conecta as soluções tecnológicas ao catálogo visual da INNA."""

from __future__ import annotations

import importlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OVERVIEW_PATH = ROOT / "src" / "dashboard_pages" / "platform_modules_overview.py"

BUSINESS_DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_business_solution_details.py"
)

TECHNOLOGY_DETAILS_PATH = (
    ROOT / "src" / "dashboard_pages" / "platform_technology_solution_details.py"
)

TECHNOLOGY_TEST_PATH = (
    ROOT / "tests" / "unit" / "test_platform_technology_solution_navigation.py"
)

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("technology_solution_navigation_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


TECHNOLOGY_NAVIGATION_TEST_SOURCE = """from pathlib import Path

from src.dashboard_pages.platform_modules_overview import (
    build_platform_module_cards,
)
from src.dashboard_pages.platform_technology_solution_details import (
    TECHNOLOGY_SOLUTION_STATE_KEY,
    render_platform_technology_solution_details,
)
from src.platform_modules import PlatformModuleCategory
from src.platform_technology_solutions import (
    PLATFORM_TECHNOLOGY_SOLUTIONS,
    platform_technology_solution,
)


OVERVIEW_PATH = Path(
    "src/dashboard_pages/platform_modules_overview.py"
)


def test_technology_detail_renderer_is_available():
    assert TECHNOLOGY_SOLUTION_STATE_KEY
    assert callable(
        render_platform_technology_solution_details
    )


def test_all_technology_solutions_match_technology_cards():
    technology_cards = tuple(
        card
        for card in build_platform_module_cards()
        if (
            card.category
            is PlatformModuleCategory.TECHNOLOGY_CORE
        )
    )

    technology_card_ids = {
        card.module_id
        for card in technology_cards
    }

    registered_solution_ids = {
        solution.solution_id
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    }

    assert len(technology_cards) == 56
    assert technology_card_ids == registered_solution_ids

    for solution_id in registered_solution_ids:
        assert (
            platform_technology_solution(solution_id)
            is not None
        )


def test_overview_contains_technology_navigation_flow():
    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "TECHNOLOGY_SOLUTION_STATE_KEY",
        "render_platform_technology_solution_details",
        "platform_technology_solution",
        "open_technology_solution_",
        "selected_technology_solution_id",
    )

    for token in required_tokens:
        assert token in source


def test_technology_registry_totals_remain_complete():
    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 56

    assert sum(
        len(solution.areas)
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 392

    assert sum(
        solution.capability_count
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 1176
"""


def validate_prerequisites() -> None:
    """Valida arquivos e registros necessários."""

    required_paths = (
        OVERVIEW_PATH,
        BUSINESS_DETAILS_PATH,
    )

    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Arquivo obrigatório ausente: {path}")

    from src.platform_modules import (
        PLATFORM_MODULES,
        PlatformModuleCategory,
    )
    from src.platform_technology_solutions import (
        PLATFORM_TECHNOLOGY_SOLUTIONS,
    )

    technology_modules = tuple(
        module
        for module in PLATFORM_MODULES
        if (module.category is PlatformModuleCategory.TECHNOLOGY_CORE)
    )

    if len(technology_modules) != 56:
        raise RuntimeError("O catálogo principal não possui 56 módulos tecnológicos.")

    if len(PLATFORM_TECHNOLOGY_SOLUTIONS) != 56:
        raise RuntimeError(
            "O registro especializado não possui 56 soluções tecnológicas."
        )

    total_areas = sum(len(solution.areas) for solution in PLATFORM_TECHNOLOGY_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    )

    if total_areas != 392:
        raise RuntimeError(f"Total inesperado de áreas: {total_areas}")

    if total_capabilities != 1176:
        raise RuntimeError(f"Total inesperado de capacidades: {total_capabilities}")

    print("TECHNOLOGY_NAVIGATION_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria cópias dos arquivos antes da alteração."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = (
        OVERVIEW_PATH,
        BUSINESS_DETAILS_PATH,
        TECHNOLOGY_DETAILS_PATH,
        TECHNOLOGY_TEST_PATH,
    )

    copied_files = 0

    for source_path in paths:
        if not source_path.exists():
            continue

        shutil.copy2(
            source_path,
            BACKUP_ROOT / source_path.name,
        )

        copied_files += 1

    print(f"BACKUP_CREATED={BACKUP_ROOT}")
    print(f"BACKUP_FILES={copied_files}")


def create_technology_details_page() -> None:
    """Cria a página tecnológica usando o padrão empresarial."""

    if TECHNOLOGY_DETAILS_PATH.exists():
        existing_source = TECHNOLOGY_DETAILS_PATH.read_text(
            encoding="utf-8",
        )

        required_existing_tokens = (
            "TECHNOLOGY_SOLUTION_STATE_KEY",
            "render_platform_technology_solution_details",
            "platform_technology_solution",
            "TechnologyCapability",
            "PlatformTechnologySolution",
        )

        if all(token in existing_source for token in required_existing_tokens):
            print("TECHNOLOGY_DETAILS_PAGE_ALREADY_PRESENT=OK")
            return

        raise RuntimeError(
            "A página tecnológica já existe, mas não possui a estrutura esperada."
        )

    source = BUSINESS_DETAILS_PATH.read_text(
        encoding="utf-8",
    )

    replacements = (
        ("BUSINESS", "TECHNOLOGY"),
        ("Business", "Technology"),
        ("business", "technology"),
        (
            "soluções empresariais",
            "soluções tecnológicas",
        ),
        (
            "Solução empresarial não encontrada.",
            "Solução tecnológica não encontrada.",
        ),
        (
            "Solución technologyial no encontrada.",
            "Solución tecnológica no encontrada.",
        ),
        (
            "capacidade setorial",
            "capacidade tecnológica",
        ),
        (
            "área setorial",
            "área tecnológica",
        ),
    )

    for old_value, new_value in replacements:
        source = source.replace(
            old_value,
            new_value,
        )

    source = source.replace(
        '"planned": "Planejado",',
        ('"planned": "Planejado",\n        "active": "Ativo",'),
        1,
    )

    source = source.replace(
        '"hybrid": "Híbrida",',
        ('"hybrid": "Híbrida",\n        "internal": "Interna",'),
        1,
    )

    source = source.replace(
        '"planned": "Planned",',
        ('"planned": "Planned",\n        "active": "Active",'),
        1,
    )

    source = source.replace(
        '"hybrid": "Hybrid",',
        ('"hybrid": "Hybrid",\n        "internal": "Internal",'),
        1,
    )

    source = source.replace(
        '"planned": "Planificado",',
        ('"planned": "Planificado",\n        "active": "Activo",'),
        1,
    )

    source = source.replace(
        """        "planned": "Planificado",
        "active": "Activo",
        "hybrid": "Híbrida",
""",
        """        "planned": "Planificado",
        "active": "Activo",
        "hybrid": "Híbrida",
        "internal": "Interna",
""",
        1,
    )

    required_tokens = (
        "from src.platform_technology_solutions import",
        "TechnologyCapability",
        "PlatformTechnologySolution",
        "platform_technology_solution",
        "TECHNOLOGY_SOLUTION_STATE_KEY",
        "selected_platform_technology_solution_id",
        "render_platform_technology_solution_details",
        "clear_selected_technology_solution",
        "technology_solution_back_to_catalog",
    )

    missing_tokens = tuple(token for token in required_tokens if token not in source)

    if missing_tokens:
        raise RuntimeError(
            f"A transformação da página tecnológica ficou incompleta: {missing_tokens}"
        )

    TECHNOLOGY_DETAILS_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TECHNOLOGY_DETAILS_PAGE_CREATED=OK")


def connect_overview_navigation() -> None:
    """Conecta os cartões tecnológicos à página de detalhes."""

    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    if (
        "open_technology_solution_" in source
        and "selected_technology_solution_id" in source
        and "render_platform_technology_solution_details" in source
    ):
        print("TECHNOLOGY_OVERVIEW_NAVIGATION_ALREADY_CONNECTED=OK")
        return

    sector_details_import = """from src.dashboard_pages.platform_sector_solution_details import (
    SECTOR_SOLUTION_STATE_KEY,
    render_platform_sector_solution_details,
)
"""

    technology_details_import = """from src.dashboard_pages.platform_technology_solution_details import (
    TECHNOLOGY_SOLUTION_STATE_KEY,
    render_platform_technology_solution_details,
)
"""

    if sector_details_import not in source:
        raise RuntimeError("Importação de detalhes setoriais não encontrada.")

    source = source.replace(
        sector_details_import,
        (sector_details_import + technology_details_import),
        1,
    )

    sector_registry_import = """from src.platform_sector_solutions import (
    platform_sector_solution,
)
"""

    technology_registry_import = """from src.platform_technology_solutions import (
    platform_technology_solution,
)
"""

    if sector_registry_import not in source:
        raise RuntimeError("Importação do registro setorial não encontrada.")

    source = source.replace(
        sector_registry_import,
        (sector_registry_import + technology_registry_import),
        1,
    )

    sector_state_anchor = """                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                SECTOR_SOLUTION_STATE_KEY
                            ] = card.module_id
"""

    sector_state_replacement = """                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                TECHNOLOGY_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                SECTOR_SOLUTION_STATE_KEY
                            ] = card.module_id
"""

    if sector_state_anchor not in source:
        raise RuntimeError("Fluxo de abertura setorial não encontrado.")

    source = source.replace(
        sector_state_anchor,
        sector_state_replacement,
        1,
    )

    business_state_anchor = """                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                BUSINESS_SOLUTION_STATE_KEY
                            ] = card.module_id
"""

    business_state_replacement = """                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                TECHNOLOGY_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                BUSINESS_SOLUTION_STATE_KEY
                            ] = card.module_id
"""

    if business_state_anchor not in source:
        raise RuntimeError("Fluxo de abertura empresarial não encontrado.")

    source = source.replace(
        business_state_anchor,
        business_state_replacement,
        1,
    )

    business_navigation_block = """                    business_solution = (
                        platform_business_solution(
                            card.module_id
                        )
                    )

                    if business_solution is not None:
                        if st.button(
                            "Ver detalhes",
                            key=(
                                "open_business_solution_"
                                f"{card.module_id}"
                            ),
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                TECHNOLOGY_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                BUSINESS_SOLUTION_STATE_KEY
                            ] = card.module_id

                            st.rerun()
"""

    technology_navigation_block = """
                    technology_solution = (
                        platform_technology_solution(
                            card.module_id
                        )
                    )

                    if technology_solution is not None:
                        if st.button(
                            "Ver detalhes",
                            key=(
                                "open_technology_solution_"
                                f"{card.module_id}"
                            ),
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state.pop(
                                SECTOR_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                TECHNOLOGY_SOLUTION_STATE_KEY
                            ] = card.module_id

                            st.rerun()
"""

    if business_navigation_block not in source:
        raise RuntimeError(
            "Bloco de navegação empresarial não encontrado após a atualização."
        )

    source = source.replace(
        business_navigation_block,
        (business_navigation_block + technology_navigation_block),
        1,
    )

    business_selection_anchor = """    selected_business_solution_id = (
        st.session_state.get(
            BUSINESS_SOLUTION_STATE_KEY
        )
    )
"""

    technology_selection_block = """    selected_technology_solution_id = (
        st.session_state.get(
            TECHNOLOGY_SOLUTION_STATE_KEY
        )
    )

    if selected_technology_solution_id:
        render_platform_technology_solution_details(
            selected_technology_solution_id,
            language,
        )
        return

"""

    if business_selection_anchor not in source:
        raise RuntimeError("Seleção empresarial não encontrada.")

    source = source.replace(
        business_selection_anchor,
        (technology_selection_block + business_selection_anchor),
        1,
    )

    required_tokens = (
        "TECHNOLOGY_SOLUTION_STATE_KEY",
        "render_platform_technology_solution_details",
        "platform_technology_solution",
        "open_technology_solution_",
        "selected_technology_solution_id",
    )

    for token in required_tokens:
        if token not in source:
            raise RuntimeError(f"Token tecnológico ausente no overview: {token}")

    OVERVIEW_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("TECHNOLOGY_OVERVIEW_NAVIGATION_CONNECTED=OK")


def create_navigation_tests() -> None:
    """Cria os testes de navegação tecnológica."""

    if TECHNOLOGY_TEST_PATH.exists():
        current_source = TECHNOLOGY_TEST_PATH.read_text(
            encoding="utf-8",
        )

        if "test_all_technology_solutions_match_technology_cards" in current_source:
            print("TECHNOLOGY_NAVIGATION_TESTS_ALREADY_PRESENT=OK")
            return

        raise RuntimeError(
            "O arquivo de teste tecnológico já existe, "
            "mas não possui o conteúdo esperado."
        )

    TECHNOLOGY_TEST_PATH.write_text(
        TECHNOLOGY_NAVIGATION_TEST_SOURCE,
        encoding="utf-8",
    )

    print("TECHNOLOGY_NAVIGATION_TESTS_CREATED=OK")


def validate_result() -> None:
    """Importa os componentes e valida a integração."""

    importlib.invalidate_caches()

    details_module = importlib.import_module(
        "src.dashboard_pages.platform_technology_solution_details"
    )

    overview_module = importlib.reload(
        importlib.import_module("src.dashboard_pages.platform_modules_overview")
    )

    technology_module = importlib.import_module("src.platform_technology_solutions")

    assert (
        details_module.TECHNOLOGY_SOLUTION_STATE_KEY
        == "selected_platform_technology_solution_id"
    )

    assert callable(details_module.render_platform_technology_solution_details)

    cards = overview_module.build_platform_module_cards()

    from src.platform_modules import PlatformModuleCategory

    technology_cards = tuple(
        card
        for card in cards
        if (card.category is PlatformModuleCategory.TECHNOLOGY_CORE)
    )

    assert len(technology_cards) == 56
    assert len(technology_module.PLATFORM_TECHNOLOGY_SOLUTIONS) == 56

    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    assert source.count("open_technology_solution_") == 1

    print("TECHNOLOGY_DETAIL_RENDERER=OK")
    print("TECHNOLOGY_NAVIGATION_CARDS=56")
    print("TECHNOLOGY_CATALOG_NAVIGATION_VALIDATED=OK")


validate_prerequisites()
create_backup()
create_technology_details_page()
connect_overview_navigation()
create_navigation_tests()
validate_result()
