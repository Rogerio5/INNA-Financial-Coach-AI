import pandas as pd

from src.dashboard_pages.health_score_page import (
    preparar_historico_exibicao,
    render_health_history_section,
)


def test_preparar_historico_ordenado():
    df = pd.DataFrame([
        {
            "id": 2,
            "criado_em": "2026-07-14T12:00:00Z",
            "score_global": "98.0",
            "score_tools": "99.0",
        },
        {
            "id": 1,
            "criado_em": "2026-07-14T10:00:00Z",
            "score_global": "97.8",
            "score_tools": "97.0",
        },
    ])

    resultado = preparar_historico_exibicao(
        df
    )

    assert len(resultado) == 2

    assert (
        resultado.iloc[0]["id"]
        == 1
    )

    assert (
        resultado.iloc[1]["id"]
        == 2
    )

    assert (
        resultado["score_global"].dtype.kind
        in {"f", "i"}
    )


def test_preparar_historico_vazio():
    resultado = preparar_historico_exibicao(
        pd.DataFrame()
    )

    assert resultado.empty


def test_componente_visual_disponivel():
    assert callable(
        render_health_history_section
    )
