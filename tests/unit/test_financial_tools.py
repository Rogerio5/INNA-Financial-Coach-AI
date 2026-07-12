import pytest

from src.tools.budget_tool import analisar_orcamento
from src.tools.debt_tool import (
    analisar_divida_educativamente,
)
from src.tools.registry import (
    executar_tool,
    listar_tools,
)
from src.tools.reserve_tool import (
    calcular_capacidade_semanal,
    simular_formacao_reserva,
)
from src.tools.simulation_tool import (
    simular_meta_por_aporte,
    simular_parcelamento_sem_juros,
)


def test_analisar_orcamento():
    resultado = analisar_orcamento(
        renda_mensal=6300,
        gastos_mensais=3300,
        dividas_mensais=500,
    )

    assert resultado["despesas_totais"] == 3800.0
    assert resultado["saldo_mensal"] == 2500.0
    assert resultado[
        "renda_comprometida_percentual"
    ] == 60.32
    assert resultado["situacao"] == "saldo_positivo"


def test_analisar_orcamento_deficit():
    resultado = analisar_orcamento(
        renda_mensal=3000,
        gastos_mensais=3500,
    )

    assert resultado["saldo_mensal"] == -500.0
    assert resultado["situacao"] == "deficit"


def test_capacidade_semanal():
    resultado = calcular_capacidade_semanal(
        1200
    )

    assert (
        resultado["valor_semanal_estimado"]
        == 300.0
    )


def test_simular_formacao_reserva():
    resultado = simular_formacao_reserva(
        valor_mensal=500,
        meta_total=6000,
    )

    assert resultado["meses_estimados"] == 12
    assert resultado["considera_rendimento"] is False


def test_meta_ja_atingida():
    resultado = simular_formacao_reserva(
        valor_mensal=500,
        meta_total=6000,
        valor_inicial=6000,
    )

    assert resultado["meses_estimados"] == 0
    assert resultado["status"] == "meta_atingida"


def test_divida_identifica_dados_ausentes():
    resultado = analisar_divida_educativamente(
        valor_total=5000,
        esta_atrasada=True,
    )

    assert "parcela_mensal" in resultado[
        "dados_ausentes"
    ]
    assert "divida_atrasada" in resultado[
        "sinais_de_atencao"
    ]
    assert resultado[
        "tem_dados_suficientes"
    ] is False


def test_divida_completa():
    resultado = analisar_divida_educativamente(
        valor_total=5000,
        parcela_mensal=500,
        taxa_juros_mensal=2.0,
        esta_atrasada=False,
        quantidade_parcelas=10,
        tipo_divida="cartao",
    )

    assert resultado[
        "tem_dados_suficientes"
    ] is True
    assert resultado["tipo_divida"] == "cartao"


def test_parcelamento_sem_juros():
    resultado = simular_parcelamento_sem_juros(
        valor_total=1200,
        quantidade_parcelas=6,
    )

    assert resultado["valor_parcela"] == 200.0


def test_simular_meta_por_aporte():
    resultado = simular_meta_por_aporte(
        meta_total=10000,
        aporte_mensal=1000,
        saldo_inicial=2000,
    )

    assert resultado["meses_estimados"] == 8


def test_registry_lista_tools():
    tools = listar_tools()

    nomes = {
        item["nome"]
        for item in tools
    }

    assert "analisar_orcamento" in nomes
    assert "simular_formacao_reserva" in nomes


def test_registry_executa_tool():
    resultado = executar_tool(
        "calcular_capacidade_semanal",
        {
            "valor_mensal": 1200,
        },
    )

    assert resultado["ok"] is True
    assert resultado["resultado"][
        "valor_semanal_estimado"
    ] == 300.0


def test_registry_tool_inexistente():
    resultado = executar_tool(
        "tool_que_nao_existe",
        {},
    )

    assert resultado["ok"] is False


def test_rejeitar_valor_negativo():
    with pytest.raises(ValueError):
        analisar_orcamento(
            renda_mensal=-1,
            gastos_mensais=0,
        )
