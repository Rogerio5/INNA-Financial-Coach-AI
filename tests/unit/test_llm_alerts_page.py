from src.dashboard_pages.llm_costs_page import (
    render_alertas_llm_section,
)


def test_componente_visual_alertas_disponivel():
    assert callable(render_alertas_llm_section)
