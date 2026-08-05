from src.dashboard_pages.health_score_page import (
    preparar_componentes_exibicao,
)


def test_preparar_componentes_exibicao():
    componentes = {
        "tools": {
            "score": 98,
            "peso": 0.25,
            "contribuicao": 24.5,
            "classificacao": "Excelente",
            "status": "saudavel",
            "icone": "🟢",
        },
        "rag": {
            "score": 90,
            "peso": 0.20,
            "contribuicao": 18.0,
            "classificacao": "Boa",
            "status": "atencao_leve",
            "icone": "🟡",
        },
    }

    tabela = preparar_componentes_exibicao(componentes)

    assert len(tabela) == 2
    assert "Componente" in tabela.columns
    assert "Score" in tabela.columns
    assert "Peso (%)" in tabela.columns
    assert tabela.iloc[0]["Componente"] == "Ferramentas"
    assert tabela.iloc[0]["Peso (%)"] == 25.0


def test_componentes_vazios():
    tabela = preparar_componentes_exibicao({})

    assert tabela.empty
