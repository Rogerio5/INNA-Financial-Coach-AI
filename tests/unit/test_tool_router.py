from src.tools.router import (
    extrair_contexto_basico_mensagem,
    identificar_intencao_tool,
    mesclar_contextos_tool,
    montar_argumentos_tool,
    normalizar_texto,
    rotear_tool,
)


def test_normalizar_texto():
    resultado = normalizar_texto(
        "  Quanto POSSO guardar por SEMANA? "
    )

    assert resultado == (
        "quanto posso guardar por semana?"
    )


def test_identificar_capacidade_semanal():
    resultado = identificar_intencao_tool(
        "Quanto posso guardar por semana?"
    )

    assert resultado["ok"] is True
    assert (
        resultado["tool"]
        == "calcular_capacidade_semanal"
    )


def test_identificar_orcamento():
    resultado = identificar_intencao_tool(
        "Com minha renda e gastos, quanto sobra?"
    )

    assert resultado["ok"] is True
    assert resultado["tool"] == "analisar_orcamento"


def test_identificar_divida():
    resultado = identificar_intencao_tool(
        "Tenho uma dívida atrasada e não sei os juros."
    )

    assert resultado["ok"] is True
    assert (
        resultado["tool"]
        == "analisar_divida_educativamente"
    )


def test_identificar_parcelamento():
    resultado = identificar_intencao_tool(
        "Quanto fica o valor da parcela sem juros?"
    )

    assert resultado["ok"] is True
    assert (
        resultado["tool"]
        == "simular_parcelamento_sem_juros"
    )


def test_montar_argumentos_com_aliases():
    resultado = montar_argumentos_tool(
        "analisar_orcamento",
        {
            "renda": 6300,
            "gastos": 3300,
            "parcelas_mensais": 500,
        },
    )

    assert resultado["ok"] is True
    assert resultado["argumentos"] == {
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "dividas_mensais": 500,
    }


def test_router_informa_dado_ausente():
    resultado = rotear_tool(
        "Quanto posso guardar por semana?",
        contexto={},
    )

    assert resultado["ok"] is False
    assert resultado["executada"] is False
    assert (
        "valor_mensal"
        in resultado["preparacao"]["dados_ausentes"]
    )


def test_router_executa_capacidade_semanal():
    resultado = rotear_tool(
        "Quanto posso guardar por semana?",
        contexto={
            "valor_reserva": 1200,
        },
    )

    assert resultado["ok"] is True
    assert resultado["executada"] is True
    assert (
        resultado["execucao"]["resultado"][
            "valor_semanal_estimado"
        ]
        == 300.0
    )


def test_router_executa_orcamento():
    resultado = rotear_tool(
        "Com minha renda e gastos, quanto sobra?",
        contexto={
            "renda_mensal": 6300,
            "gastos_mensais": 3300,
            "dividas_mensais": 500,
        },
    )

    assert resultado["ok"] is True
    assert (
        resultado["execucao"]["resultado"][
            "saldo_mensal"
        ]
        == 2500.0
    )


def test_router_pode_apenas_preparar():
    resultado = rotear_tool(
        "Quanto posso guardar por semana?",
        contexto={
            "valor_reserva": 1200,
        },
        executar=False,
    )

    assert resultado["ok"] is True
    assert resultado["executada"] is False
    assert resultado["execucao"] is None


def test_mensagem_sem_tool():
    resultado = rotear_tool(
        "Olá, bom dia!",
        contexto={},
    )

    assert resultado["ok"] is False
    assert resultado["classificacao"]["tool"] is None

def test_extrair_divida_atrasada_da_mensagem():
    contexto = extrair_contexto_basico_mensagem(
        "Tenho uma dívida atrasada."
    )

    assert contexto["esta_atrasada"] is True


def test_extrair_divida_em_dia():
    contexto = extrair_contexto_basico_mensagem(
        "Minha dívida está em dia."
    )

    assert contexto["esta_atrasada"] is False


def test_extrair_tipo_divida_cartao():
    contexto = extrair_contexto_basico_mensagem(
        "Minha fatura do cartão está atrasada."
    )

    assert contexto["tipo_divida"] == "cartao"
    assert contexto["esta_atrasada"] is True


def test_mesclar_contextos_prioriza_mensagem():
    resultado = mesclar_contextos_tool(
        contexto_memoria={
            "esta_atrasada": False,
            "valor_total": 5000,
        },
        contexto_mensagem={
            "esta_atrasada": True,
        },
    )

    assert resultado["esta_atrasada"] is True
    assert resultado["valor_total"] == 5000


def test_router_divida_atrasada_gera_sinal():
    resultado = rotear_tool(
        "Tenho uma dívida atrasada.",
        contexto={},
    )

    ferramenta = resultado["execucao"]["resultado"]

    assert ferramenta["esta_atrasada"] is True
    assert (
        "divida_atrasada"
        in ferramenta["sinais_de_atencao"]
    )

def test_router_divida_cartao_atrasada_com_termos_intermediarios():
    resultado = rotear_tool(
        "Tenho uma dívida do cartão atrasada.",
        contexto={},
    )

    ferramenta = resultado["execucao"]["resultado"]

    assert ferramenta["tipo_divida"] == "cartao"
    assert ferramenta["esta_atrasada"] is True
    assert (
        "divida_atrasada"
        in ferramenta["sinais_de_atencao"]
    )

