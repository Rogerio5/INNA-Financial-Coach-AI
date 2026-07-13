import pandas as pd

from src.dashboard_pages.timeline_viewer_page import (
    calcular_diferenca_traces,
    calcular_resumo_trace,
    formatar_duracao_ms,
    preparar_timeline_exibicao,
    preparar_traces_exibicao,
)


def timeline_teste():
    return pd.DataFrame([
        {
            "ordem": 10,
            "etapa_label": "Pergunta recebida",
            "status": "sucesso",
            "duracao_ms": 0.0,
            "inicio_em": "2026-07-13T19:00:00Z",
            "mensagem": "Pergunta recebida.",
            "erro": None,
            "metadata": {},
            "criado_em": "2026-07-13T19:00:00Z",
        },
        {
            "ordem": 50,
            "etapa_label": "Busca RAG concluída",
            "status": "sucesso",
            "duracao_ms": 1700.0,
            "inicio_em": "2026-07-13T19:00:01Z",
            "mensagem": "RAG concluído.",
            "erro": None,
            "metadata": {},
            "criado_em": "2026-07-13T19:00:01Z",
        },
        {
            "ordem": 70,
            "etapa_label": "Gemini executado",
            "status": "sucesso",
            "duracao_ms": 3300.0,
            "inicio_em": "2026-07-13T19:00:03Z",
            "mensagem": "Gemini concluído.",
            "erro": None,
            "metadata": {},
            "criado_em": "2026-07-13T19:00:03Z",
        },
        {
            "ordem": 90,
            "etapa_label": "Resposta entregue",
            "status": "sucesso",
            "duracao_ms": 0.0,
            "inicio_em": "2026-07-13T19:00:06Z",
            "mensagem": "Resposta entregue.",
            "erro": None,
            "metadata": {},
            "criado_em": "2026-07-13T19:00:06Z",
        },
    ])


def traces_teste():
    return pd.DataFrame([
        {
            "trace_id": "trace-1",
            "inicio_trace": "2026-07-13T19:00:00Z",
            "usuario_id": "demo_user",
            "pergunta": "Quanto posso guardar?",
            "total_etapas": 9,
            "total_falhas": 0,
            "duracao_total_ms": 5500.0,
            "origem": "dashboard_rag",
        }
    ])


def test_formatar_duracao_em_ms():
    assert formatar_duracao_ms(
        500
    ) == "500.000 ms"


def test_formatar_duracao_em_segundos():
    assert formatar_duracao_ms(
        5500
    ) == "5.500 s"


def test_calcular_resumo_trace():
    resumo = calcular_resumo_trace(
        timeline_teste()
    )

    assert resumo["total_etapas"] == 4
    assert resumo["total_falhas"] == 0
    assert resumo["duracao_total_ms"] == 5000.0
    assert (
        resumo["etapa_mais_lenta"]
        == "Gemini executado"
    )
    assert (
        resumo["possivel_cold_start"]
        is False
    )


def test_detectar_cold_start():
    df = timeline_teste()

    df.loc[
        df["etapa_label"]
        == "Busca RAG concluída",
        "duracao_ms",
    ] = 40000.0

    resumo = calcular_resumo_trace(
        df
    )

    assert (
        resumo["possivel_cold_start"]
        is True
    )


def test_preparar_traces_exibicao():
    tabela = preparar_traces_exibicao(
        traces_teste()
    )

    assert "Trace ID" in tabela.columns
    assert "Duração total" in tabela.columns
    assert tabela.iloc[0]["Status"] == "✅ Sucesso"


def test_preparar_timeline_exibicao():
    tabela = preparar_timeline_exibicao(
        timeline_teste()
    )

    assert "Etapa" in tabela.columns
    assert "Status visual" in tabela.columns
    assert "Duração" in tabela.columns


def test_resumo_vazio():
    resumo = calcular_resumo_trace(
        pd.DataFrame()
    )

    assert resumo["total_etapas"] == 0
    assert resumo["duracao_total_ms"] == 0.0

def test_diferenca_trace_b_mais_lento():
    resultado = calcular_diferenca_traces(
        5000,
        10000,
    )

    assert (
        resultado["diferenca_absoluta_ms"]
        == 5000.0
    )

    assert (
        resultado["diferenca_percentual"]
        == 100.0
    )


def test_diferenca_trace_b_mais_rapido():
    resultado = calcular_diferenca_traces(
        10000,
        5000,
    )

    assert (
        resultado["diferenca_absoluta_ms"]
        == -5000.0
    )

    assert (
        resultado["diferenca_percentual"]
        == -50.0
    )


def test_diferenca_com_trace_a_zero():
    resultado = calcular_diferenca_traces(
        0,
        5000,
    )

    assert (
        resultado["diferenca_percentual"]
        == 0.0
    )

