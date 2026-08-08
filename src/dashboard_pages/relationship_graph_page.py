from __future__ import annotations

from copy import deepcopy
import json

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any
from typing import cast

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "relationship_graph_catalog.json"
)


@st.cache_data(
    show_spinner=False,
)
def _read_catalog(
    catalog_path: str,
    modified_time_ns: int,
) -> dict[str, Any]:
    """Lê o catálogo considerando sua última alteração."""

    del modified_time_ns

    path = Path(catalog_path)

    return cast(
        dict[str, Any],
        json.loads(
            path.read_text(
                encoding="utf-8",
            )
        ),
    )


def _ensure_catalog() -> Path:
    """Garante que o catálogo real exista."""

    if CATALOG_PATH.exists():
        return CATALOG_PATH

    from src.relationship_graph_registry import (
        write_relationship_graph_catalog,
    )

    write_relationship_graph_catalog(
        CATALOG_PATH
    )

    return CATALOG_PATH


def _load_catalog() -> dict[str, Any]:
    """Carrega o catálogo atual da plataforma."""

    path = _ensure_catalog()
    file_stat = path.stat()

    return _read_catalog(
        str(path),
        file_stat.st_mtime_ns,
    )


def _clean_module_title_icon(
    title: str,
    icon: str,
) -> str:
    """Remove ícones repetidos do início do título."""

    clean_title = str(
        title or ""
    ).strip()

    clean_icon = str(
        icon or ""
    ).strip()

    if not clean_icon:
        return clean_title

    # Remove todas as repetições do mesmo ícone.
    #
    # Exemplo:
    # 🤖 🤖 Automação Empresarial
    # -> Automação Empresarial
    #
    # O frontend continuará mostrando apenas:
    # 🤖 Automação Empresarial
    while clean_title.startswith(
        clean_icon
    ):
        clean_title = (
            clean_title[
                len(clean_icon):
            ]
            .lstrip()
        )

    return clean_title


def _localize_catalog(
    catalog: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    """Localiza rótulos visuais sem alterar IDs técnicos."""

    from src.platform_modules import (
        PlatformModuleCategory,
    )
    from src.platform_modules_i18n import (
        platform_module_category_t,
        platform_module_t,
    )

    localized = deepcopy(catalog)

    normalized_language = (
        str(language or "pt")
        .strip()
        .lower()
    )

    statistics = localized.get(
        "statistics",
        {},
    )

    categories = statistics.get(
        "categories",
        {},
    )

    category_labels: dict[str, str] = {}

    for category_id in categories:
        try:
            category_enum = (
                PlatformModuleCategory(
                    category_id
                )
            )

            category_labels[
                category_id
            ] = platform_module_category_t(
                category_enum,
                normalized_language,
            )
        except Exception:
            category_labels[
                category_id
            ] = category_id

    localized[
        "category_labels"
    ] = category_labels

    for module in localized.get(
        "modules",
        [],
    ):
        module_id = str(
            module.get("id", "")
        ).strip()

        if not module_id:
            continue

        try:
            translated_title = (
                platform_module_t(
                    module_id,
                    normalized_language,
                )
            )

            if translated_title:
                module[
                    "title"
                ] = _clean_module_title_icon(
                    translated_title,
                    module.get(
                        "icon",
                        "",
                    ),
                )

        except Exception:
            continue

    return localized


def _refresh_catalog() -> dict[str, Any]:
    """Regenera o catálogo a partir dos registros atuais."""

    from src.relationship_graph_registry import (
        write_relationship_graph_catalog,
    )

    write_relationship_graph_catalog(
        CATALOG_PATH
    )

    _read_catalog.clear()

    return _load_catalog()


def _load_relationship_graph() -> Callable[..., Any]:
    """Carrega o componente durante o runtime do Streamlit."""

    component_module = import_module(
        "inna_relationship_graph"
    )

    component = getattr(
        component_module,
        "relationship_graph",
        None,
    )

    if not callable(component):
        raise RuntimeError(
            "O componente relationship_graph "
            "não está disponível."
        )

    return cast(
        Callable[..., Any],
        component,
    )


def _format_number(
    value: Any,
) -> str:
    """Formata números no padrão brasileiro."""

    try:
        numeric_value = int(value)
    except (
        TypeError,
        ValueError,
    ):
        return str(value)

    return f"{numeric_value:,}".replace(
        ",",
        ".",
    )


def _metrics_html(
    catalog: dict[str, Any],
) -> str:
    """Cria somente os quatro indicadores compactos."""

    statistics = catalog.get(
        "statistics",
        {},
    )

    modules = _format_number(
        statistics.get(
            "module_count",
            0,
        )
    )

    areas = _format_number(
        statistics.get(
            "area_count",
            0,
        )
    )

    capabilities = _format_number(
        statistics.get(
            "capability_count",
            0,
        )
    )

    relationships = _format_number(
        statistics.get(
            "explicit_relationship_count",
            0,
        )
    )

    return f"""
<style>
.inna-graph-metrics-grid {{
    width: 100%;
    display: grid;
    grid-template-columns:
        repeat(
            4,
            minmax(90px, 1fr)
        );
    gap: 9px;
    margin: 2px 0 12px;
}}

.inna-graph-metric {{
    min-width: 0;
    min-height: 82px;
    padding: 11px 12px;
    display: flex;
    align-items: center;
    gap: 11px;
    border:
        1px solid
        rgba(96, 165, 250, 0.25);
    border-radius: 13px;
    background:
        linear-gradient(
            145deg,
            rgba(14, 37, 62, 0.98),
            rgba(6, 17, 32, 0.98)
        );
    box-shadow:
        0 9px 22px
        rgba(0, 0, 0, 0.18);
}}

.inna-graph-metric-icon {{
    flex: 0 0 auto;
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background:
        rgba(37, 99, 235, 0.17);
    font-size: 15px;
}}

.inna-graph-metric-content {{
    min-width: 0;
}}

.inna-graph-metric-value {{
    color: #ffffff;
    font-size: 25px;
    line-height: 1;
    font-weight: 850;
    letter-spacing: -0.7px;
}}

.inna-graph-metric-label {{
    margin-top: 5px;
    color: #93c5fd;
    font-size: 9px;
    line-height: 1.2;
    font-weight: 750;
    letter-spacing: 0.62px;
    text-transform: uppercase;
}}

@media (max-width: 850px) {{
    .inna-graph-metrics-grid {{
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }}
}}
</style>

<section class="inna-graph-metrics-grid">
    <article class="inna-graph-metric">
        <div class="inna-graph-metric-icon">
            🧩
        </div>

        <div class="inna-graph-metric-content">
            <div class="inna-graph-metric-value">
                {modules}
            </div>

            <div class="inna-graph-metric-label">
                Módulos
            </div>
        </div>
    </article>

    <article class="inna-graph-metric">
        <div class="inna-graph-metric-icon">
            ◉
        </div>

        <div class="inna-graph-metric-content">
            <div class="inna-graph-metric-value">
                {areas}
            </div>

            <div class="inna-graph-metric-label">
                Áreas
            </div>
        </div>
    </article>

    <article class="inna-graph-metric">
        <div class="inna-graph-metric-icon">
            ◆
        </div>

        <div class="inna-graph-metric-content">
            <div class="inna-graph-metric-value">
                {capabilities}
            </div>

            <div class="inna-graph-metric-label">
                Capacidades
            </div>
        </div>
    </article>

    <article class="inna-graph-metric">
        <div class="inna-graph-metric-icon">
            🔗
        </div>

        <div class="inna-graph-metric-content">
            <div class="inna-graph-metric-value">
                {relationships}
            </div>

            <div class="inna-graph-metric-label">
                Relações reais
            </div>
        </div>
    </article>
</section>
"""


def _render_certification_popover() -> None:
    """Mostra a certificação apenas quando o usuário clicar."""

    with st.popover(
        "🏅 Certificação e evidências"
    ):
        st.markdown(
            "### 🏅 Certificação de IA e "
            "Evidências do Sistema"
        )

        st.write(
            "É um módulo para comprovar que a IA "
            "funciona corretamente e segue padrões "
            "de qualidade."
        )

        st.markdown("**Exemplos**")

        st.markdown(
            """
- 📋 Gerar evidências de testes.
- ✅ Registrar validações e auditorias.
- 📊 Comprovar desempenho da IA.
- 🔒 Demonstrar conformidade.
- 📄 Emitir relatórios para clientes e auditorias.
            """
        )


# RELATIONSHIP_GRAPH_PAGE_I18N

GRAPH_PAGE_TEXTS: dict[
    str,
    dict[str, str],
] = {
    "pt": {
        "title": "🕸️ Grafo de Relacionamentos",
        "caption": (
            "Mapa executivo-técnico da arquitetura real "
            "da INNA IA PLATAFORMA."
        ),
        "refresh": "↻ Atualizar",
        "modules": "Módulos",
        "areas": "Áreas",
        "capabilities": "Capacidades",
        "real_relationships": "Relações reais",
        "load_error": "Não foi possível carregar o catálogo do grafo",
        "updated": "Catálogo atualizado.",
    },

    "en_us": {
        "title": "🕸️ Relationship Graph",
        "caption": (
            "Executive-technical map of the real "
            "INNA AI PLATFORM architecture."
        ),
        "refresh": "↻ Refresh",
        "modules": "Modules",
        "areas": "Areas",
        "capabilities": "Capabilities",
        "real_relationships": "Real relationships",
        "load_error": "Unable to load the graph catalog",
        "updated": "Catalog updated.",
    },

    "en_gb": {
        "title": "🕸️ Relationship Graph",
        "caption": (
            "Executive-technical map of the real "
            "INNA AI PLATFORM architecture."
        ),
        "refresh": "↻ Refresh",
        "modules": "Modules",
        "areas": "Areas",
        "capabilities": "Capabilities",
        "real_relationships": "Real relationships",
        "load_error": "Unable to load the graph catalogue",
        "updated": "Catalogue updated.",
    },

    "es": {
        "title": "🕸️ Grafo de Relaciones",
        "caption": (
            "Mapa ejecutivo-técnico de la arquitectura real "
            "de INNA IA PLATAFORMA."
        ),
        "refresh": "↻ Actualizar",
        "modules": "Módulos",
        "areas": "Áreas",
        "capabilities": "Capacidades",
        "real_relationships": "Relaciones reales",
        "load_error": "No fue posible cargar el catálogo del grafo",
        "updated": "Catálogo actualizado.",
    },

    "fr": {
        "title": "🕸️ Graphe des Relations",
        "caption": (
            "Carte exécutive et technique de l'architecture réelle "
            "de la PLATEFORME IA INNA."
        ),
        "refresh": "↻ Actualiser",
        "modules": "Modules",
        "areas": "Domaines",
        "capabilities": "Capacités",
        "real_relationships": "Relations réelles",
        "load_error": "Impossible de charger le catalogue du graphe",
        "updated": "Catalogue actualisé.",
    },

    "de": {
        "title": "🕸️ Beziehungsgraph",
        "caption": (
            "Technisch-exekutive Karte der realen Architektur "
            "der INNA KI-PLATTFORM."
        ),
        "refresh": "↻ Aktualisieren",
        "modules": "Module",
        "areas": "Bereiche",
        "capabilities": "Fähigkeiten",
        "real_relationships": "Reale Beziehungen",
        "load_error": "Der Graphkatalog konnte nicht geladen werden",
        "updated": "Katalog aktualisiert.",
    },

    "it": {
        "title": "🕸️ Grafo delle Relazioni",
        "caption": (
            "Mappa esecutivo-tecnica dell'architettura reale "
            "della PIATTAFORMA IA INNA."
        ),
        "refresh": "↻ Aggiorna",
        "modules": "Moduli",
        "areas": "Aree",
        "capabilities": "Capacità",
        "real_relationships": "Relazioni reali",
        "load_error": "Impossibile caricare il catalogo del grafo",
        "updated": "Catalogo aggiornato.",
    },

    "ro": {
        "title": "🕸️ Grafic de Relații",
        "caption": (
            "Hartă executiv-tehnică a arhitecturii reale "
            "a PLATFORMEI IA INNA."
        ),
        "refresh": "↻ Actualizează",
        "modules": "Module",
        "areas": "Arii",
        "capabilities": "Capacități",
        "real_relationships": "Relații reale",
        "load_error": "Catalogul grafului nu a putut fi încărcat",
        "updated": "Catalog actualizat.",
    },

    "ua": {
        "title": "🕸️ Граф Зв'язків",
        "caption": (
            "Виконавчо-технічна карта реальної архітектури "
            "ПЛАТФОРМИ ШІ INNA."
        ),
        "refresh": "↻ Оновити",
        "modules": "Модулі",
        "areas": "Області",
        "capabilities": "Можливості",
        "real_relationships": "Реальні зв'язки",
        "load_error": "Не вдалося завантажити каталог графа",
        "updated": "Каталог оновлено.",
    },

    "ru": {
        "title": "🕸️ Граф Связей",
        "caption": (
            "Исполнительно-техническая карта реальной архитектуры "
            "ПЛАТФОРМЫ ИИ INNA."
        ),
        "refresh": "↻ Обновить",
        "modules": "Модули",
        "areas": "Области",
        "capabilities": "Возможности",
        "real_relationships": "Реальные связи",
        "load_error": "Не удалось загрузить каталог графа",
        "updated": "Каталог обновлён.",
    },

    "sa": {
        "title": "🕸️ مخطط العلاقات",
        "caption": (
            "خريطة تنفيذية وتقنية للبنية الحقيقية "
            "لمنصة INNA للذكاء الاصطناعي."
        ),
        "refresh": "↻ تحديث",
        "modules": "الوحدات",
        "areas": "المجالات",
        "capabilities": "القدرات",
        "real_relationships": "العلاقات الفعلية",
        "load_error": "تعذر تحميل دليل المخطط",
        "updated": "تم تحديث الدليل.",
    },
}


GRAPH_PAGE_TEXTS["ch"] = dict(
    GRAPH_PAGE_TEXTS["de"]
)


def _graph_page_texts(
    language: str,
) -> dict[str, str]:
    normalized = str(
        language or "pt"
    ).strip().lower()

    return GRAPH_PAGE_TEXTS.get(
        normalized,
        GRAPH_PAGE_TEXTS["pt"],
    )


def render_relationship_graph_page(
    interface_language: str = "pt",
) -> None:
    """Renderiza o mapa profissional da arquitetura da INNA."""

    texts = _graph_page_texts(
        interface_language
    )

    relationship_graph = (
        _load_relationship_graph()
    )

    title_column, action_column = st.columns(
        [
            5,
            1,
        ],
        vertical_alignment="center",
    )

    with title_column:
        st.title(
            texts["title"]
        )

        st.caption(
            texts["caption"]
        )

    with action_column:
        refresh_requested = st.button(
            texts["refresh"],
            key=(
                "relationship_graph_refresh_catalog"
            ),
            use_container_width=True,
        )

    try:
        catalog = (
            _refresh_catalog()
            if refresh_requested
            else _load_catalog()
        )
    except Exception as exc:
        st.error(
            f'{texts["load_error"]}: {exc}'
        )
        return

    catalog = _localize_catalog(
        catalog,
        interface_language,
    )

    if refresh_requested:
        st.toast(
            texts["updated"],
            icon="✅",
        )

    metrics_html = _metrics_html(
        catalog
    )

    metrics_html = (
        metrics_html
        .replace(
            "Módulos",
            texts["modules"],
        )
        .replace(
            "Áreas",
            texts["areas"],
        )
        .replace(
            "Capacidades",
            texts["capabilities"],
        )
        .replace(
            "Relações reais",
            texts["real_relationships"],
        )
    )

    st.html(
        metrics_html
    )

    relationship_graph(
        catalog=catalog,
        locale=interface_language,
        key=(
            "dashboard_relationship_graph_"
            + str(interface_language)
        ),
        height=840,
    )


__all__ = [
    "render_relationship_graph_page",
]
