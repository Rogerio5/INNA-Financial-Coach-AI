"""Conecta as soluções empresariais ao catálogo visual da INNA."""

from __future__ import annotations

import importlib
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

OVERVIEW_PATH = ROOT / "src" / "dashboard_pages" / "platform_modules_overview.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_business_solution_navigation.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("business_catalog_navigation_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


BUSINESS_DETAILS_IMPORT = """from src.dashboard_pages.platform_business_solution_details import (
    BUSINESS_SOLUTION_STATE_KEY,
    render_platform_business_solution_details,
)
"""


BUSINESS_REGISTRY_IMPORT = """from src.platform_business_solutions import (
    platform_business_solution,
)
"""


BUSINESS_CARD_BLOCK = """
                    business_solution = (
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

                            st.session_state[
                                BUSINESS_SOLUTION_STATE_KEY
                            ] = card.module_id

                            st.rerun()
"""


TEST_SOURCE = """from pathlib import Path

from src.dashboard_pages.platform_business_solution_details import (
    BUSINESS_SOLUTION_STATE_KEY,
    render_platform_business_solution_details,
)
from src.dashboard_pages.platform_modules_overview import (
    build_platform_module_cards,
)
from src.platform_business_solutions import (
    PLATFORM_BUSINESS_SOLUTIONS,
    platform_business_solution,
)
from src.platform_modules import PlatformModuleCategory


OVERVIEW_PATH = Path(
    "src/dashboard_pages/platform_modules_overview.py"
)


def test_business_detail_renderer_is_available():
    assert BUSINESS_SOLUTION_STATE_KEY
    assert callable(
        render_platform_business_solution_details
    )


def test_all_business_solutions_match_business_cards():
    business_cards = tuple(
        card
        for card in build_platform_module_cards()
        if (
            card.category
            is PlatformModuleCategory.BUSINESS_SOLUTIONS
        )
    )

    business_card_ids = {
        card.module_id
        for card in business_cards
    }

    registered_solution_ids = {
        solution.solution_id
        for solution in PLATFORM_BUSINESS_SOLUTIONS
    }

    assert len(business_cards) == 12
    assert business_card_ids == registered_solution_ids

    for solution_id in registered_solution_ids:
        assert (
            platform_business_solution(solution_id)
            is not None
        )


def test_overview_contains_business_navigation_flow():
    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "BUSINESS_SOLUTION_STATE_KEY",
        "render_platform_business_solution_details",
        "platform_business_solution",
        "open_business_solution_",
        "selected_business_solution_id",
    )

    for token in required_tokens:
        assert token in source


def test_business_registry_totals_remain_complete():
    assert len(
        PLATFORM_BUSINESS_SOLUTIONS
    ) == 12

    assert sum(
        len(solution.areas)
        for solution in PLATFORM_BUSINESS_SOLUTIONS
    ) == 72

    assert sum(
        solution.capability_count
        for solution in PLATFORM_BUSINESS_SOLUTIONS
    ) == 215
"""


def validate_prerequisites() -> None:
    """Valida os arquivos e registros necessários."""

    if not OVERVIEW_PATH.exists():
        raise RuntimeError("Página do catálogo não encontrada.")

    from src.dashboard_pages.platform_business_solution_details import (
        BUSINESS_SOLUTION_STATE_KEY,
        render_platform_business_solution_details,
    )
    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
    )

    if not BUSINESS_SOLUTION_STATE_KEY:
        raise RuntimeError("Chave de estado empresarial inválida.")

    if not callable(render_platform_business_solution_details):
        raise RuntimeError("Renderizador empresarial inválido.")

    if len(PLATFORM_BUSINESS_SOLUTIONS) != 12:
        raise RuntimeError("Esperadas 12 soluções empresariais.")

    if sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS) != 72:
        raise RuntimeError("Esperadas 72 áreas empresariais.")

    if (
        sum(solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS)
        != 215
    ):
        raise RuntimeError("Esperados 215 submódulos empresariais.")

    print("BUSINESS_CATALOG_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup antes das alterações."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for source_path in (
        OVERVIEW_PATH,
        TEST_PATH,
    ):
        if source_path.exists():
            shutil.copy2(
                source_path,
                BACKUP_ROOT / source_path.name,
            )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")


def add_imports(source: str) -> str:
    """Adiciona os imports empresariais."""

    if "platform_business_solution_details" not in source:
        sector_import = """from src.dashboard_pages.platform_sector_solution_details import (
    SECTOR_SOLUTION_STATE_KEY,
    render_platform_sector_solution_details,
)
"""

        if sector_import not in source:
            raise RuntimeError("Import da página setorial não encontrado.")

        source = source.replace(
            sector_import,
            BUSINESS_DETAILS_IMPORT + sector_import,
            1,
        )

        print("BUSINESS_DETAILS_IMPORT_CREATED=OK")
    else:
        print("BUSINESS_DETAILS_IMPORT_ALREADY_PRESENT=OK")

    if "from src.platform_business_solutions import" not in source:
        modules_import_anchor = "from src.platform_modules import (\n"

        if modules_import_anchor not in source:
            raise RuntimeError("Import do registro principal não encontrado.")

        source = source.replace(
            modules_import_anchor,
            (BUSINESS_REGISTRY_IMPORT + modules_import_anchor),
            1,
        )

        print("BUSINESS_REGISTRY_IMPORT_CREATED=OK")
    else:
        print("BUSINESS_REGISTRY_IMPORT_ALREADY_PRESENT=OK")

    return source


def add_sector_state_cleanup(source: str) -> str:
    """Evita manter detalhes empresariais e setoriais simultaneamente."""

    cleanup_marker = """                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
"""

    if cleanup_marker in source:
        print("SECTOR_BUSINESS_STATE_CLEANUP_ALREADY_PRESENT=OK")
        return source

    old_assignment = """                            st.session_state[
                                SECTOR_SOLUTION_STATE_KEY
                            ] = card.module_id

                            st.rerun()
"""

    new_assignment = """                            st.session_state.pop(
                                BUSINESS_SOLUTION_STATE_KEY,
                                None,
                            )

                            st.session_state[
                                SECTOR_SOLUTION_STATE_KEY
                            ] = card.module_id

                            st.rerun()
"""

    if old_assignment not in source:
        raise RuntimeError("Atribuição do estado setorial não encontrada.")

    source = source.replace(
        old_assignment,
        new_assignment,
        1,
    )

    print("SECTOR_BUSINESS_STATE_CLEANUP_CREATED=OK")

    return source


def add_business_card_action(source: str) -> str:
    """Adiciona o botão empresarial aos cards."""

    if "open_business_solution_" in source:
        print("BUSINESS_CARD_ACTION_ALREADY_PRESENT=OK")
        return source

    function_anchor = "\n\ndef render_platform_modules_overview(\n"

    if function_anchor not in source:
        raise RuntimeError("Função principal do catálogo não encontrada.")

    source = source.replace(
        function_anchor,
        BUSINESS_CARD_BLOCK + function_anchor,
        1,
    )

    print("BUSINESS_CARD_ACTION_CREATED=OK")

    return source


def add_business_render_flow(source: str) -> str:
    """Adiciona a navegação para detalhes empresariais."""

    if "selected_business_solution_id" in source:
        print("BUSINESS_RENDER_FLOW_ALREADY_PRESENT=OK")
        return source

    old_flow = """    selected_solution_id = st.session_state.get(
        SECTOR_SOLUTION_STATE_KEY
    )

    if selected_solution_id:
        render_platform_sector_solution_details(
            selected_solution_id,
            language,
        )
        return

    st.subheader(
"""

    new_flow = """    selected_business_solution_id = (
        st.session_state.get(
            BUSINESS_SOLUTION_STATE_KEY
        )
    )

    if selected_business_solution_id:
        render_platform_business_solution_details(
            selected_business_solution_id,
            language,
        )
        return

    selected_sector_solution_id = (
        st.session_state.get(
            SECTOR_SOLUTION_STATE_KEY
        )
    )

    if selected_sector_solution_id:
        render_platform_sector_solution_details(
            selected_sector_solution_id,
            language,
        )
        return

    st.subheader(
"""

    if old_flow not in source:
        raise RuntimeError("Fluxo atual de navegação setorial não foi encontrado.")

    source = source.replace(
        old_flow,
        new_flow,
        1,
    )

    source = source.replace(
        '"""Renderiza o catálogo ou os detalhes setoriais."""',
        ('"""Renderiza o catálogo ou os detalhes especializados."""'),
        1,
    )

    print("BUSINESS_RENDER_FLOW_CREATED=OK")

    return source


def update_overview() -> None:
    """Atualiza a página principal do catálogo."""

    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    source = add_imports(source)
    source = add_sector_state_cleanup(source)
    source = add_business_card_action(source)
    source = add_business_render_flow(source)

    OVERVIEW_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("BUSINESS_CATALOG_OVERVIEW_UPDATED=OK")


def create_tests() -> None:
    """Cria testes da navegação empresarial."""

    TEST_PATH.write_text(
        TEST_SOURCE,
        encoding="utf-8",
    )

    print("BUSINESS_CATALOG_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida a integração criada."""

    importlib.invalidate_caches()

    overview_module = importlib.import_module(
        "src.dashboard_pages.platform_modules_overview"
    )

    from src.dashboard_pages.platform_business_solution_details import (
        BUSINESS_SOLUTION_STATE_KEY,
    )
    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
    )

    renderer = getattr(
        overview_module,
        "render_platform_modules_overview",
        None,
    )

    if not callable(renderer):
        raise RuntimeError("Renderizador do catálogo não encontrado.")

    source = OVERVIEW_PATH.read_text(
        encoding="utf-8",
    )

    required_tokens = (
        "BUSINESS_SOLUTION_STATE_KEY",
        "render_platform_business_solution_details",
        "platform_business_solution",
        "open_business_solution_",
        "selected_business_solution_id",
    )

    missing_tokens = tuple(token for token in required_tokens if token not in source)

    if missing_tokens:
        raise RuntimeError(f"Elementos empresariais ausentes: {missing_tokens}")

    if len(PLATFORM_BUSINESS_SOLUTIONS) != 12:
        raise RuntimeError("Quantidade empresarial inválida.")

    if not BUSINESS_SOLUTION_STATE_KEY:
        raise RuntimeError("Estado empresarial inválido.")

    print("BUSINESS_CATALOG_INTEGRATION_VALIDATED=OK")
    print("SPECIALIZED_BUSINESS_SOLUTIONS=12")
    print("TOTAL_BUSINESS_AREAS=72")
    print("TOTAL_BUSINESS_CAPABILITIES=215")


validate_prerequisites()
create_backup()
update_overview()
create_tests()
validate_result()
