from src.tools.orchestrator import (
    executar_tools_para_pergunta,
    montar_bloco_tools_prompt,
    preparar_contexto_memoria_tools,
    processar_pergunta_com_tools,
)


def memoria_teste():
    return {
        "usuario_id": "demo_user",
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
        "dividas_mensais": 500,
        "possui_dividas": True,
        "memoria_json": {
            "renda": 6000,
            "gastos": 3500,
            "pode_guardar": 1000,
        },
    }


def test_contexto_prioriza_campos_principais():
    contexto = preparar_contexto_memoria_tools(memoria_teste())

    assert contexto["renda_mensal"] == 6300
    assert contexto["gastos_mensais"] == 3300
    assert contexto["valor_reserva"] == 1200


def test_contexto_usa_alias_quando_campo_principal_ausente():
    contexto = preparar_contexto_memoria_tools(
        {
            "memoria_json": {
                "renda": 5000,
                "gastos": 3000,
                "pode_guardar": 700,
            }
        }
    )

    assert contexto["renda_mensal"] == 5000
    assert contexto["gastos_mensais"] == 3000
    assert contexto["valor_reserva"] == 700


def test_executar_tool_com_memoria():
    resultado = executar_tools_para_pergunta(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
    )

    assert resultado["ok"] is True
    assert resultado["tool_identificada"] == "calcular_capacidade_semanal"
    assert resultado["resultado"]["valor_semanal_estimado"] == 300.0


def test_bloco_prompt_resultado_deterministico():
    resultado = executar_tools_para_pergunta(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
    )

    bloco = montar_bloco_tools_prompt(resultado)

    assert "TOOL FINANCEIRA EXECUTADA" in bloco
    assert "calcular_capacidade_semanal" in bloco
    assert "300.0" in bloco
    assert "não altere" in bloco
    assert "não transforme" in bloco


def test_bloco_prompt_dados_ausentes():
    resultado = executar_tools_para_pergunta(
        pergunta="Quanto posso guardar por semana?",
        memoria={},
    )

    bloco = montar_bloco_tools_prompt(resultado)

    assert "dados insuficientes" in bloco
    assert "valor_mensal" in bloco
    assert "não invente valores" in bloco


def test_pergunta_sem_tool():
    resultado = processar_pergunta_com_tools(
        pergunta="Olá, bom dia!",
        memoria=memoria_teste(),
    )

    assert resultado["tool_identificada"] is None
    assert "Nenhuma ferramenta determinística" in resultado["bloco_prompt"]


def test_orcamento_deterministico():
    resultado = processar_pergunta_com_tools(
        pergunta=("Com minha renda e gastos, quanto sobra?"),
        memoria=memoria_teste(),
    )

    assert resultado["ok"] is True
    assert resultado["resultado"]["saldo_mensal"] == 3000.0


def test_divida_atrasada_da_mensagem():
    resultado = processar_pergunta_com_tools(
        pergunta=("Tenho uma dívida do cartão atrasada."),
        memoria={},
    )

    dados = resultado["resultado"]

    assert dados["tipo_divida"] == "cartao"
    assert dados["esta_atrasada"] is True
    assert "divida_atrasada" in dados["sinais_de_atencao"]


def test_bloco_nao_recomenda_decisao():
    resultado = processar_pergunta_com_tools(
        pergunta=("Com minha renda e gastos, quanto sobra?"),
        memoria=memoria_teste(),
    )

    bloco = resultado["bloco_prompt"]

    assert "não transforme o resultado em recomendação obrigatória" in bloco
    assert "não afirme que uma estratégia é a melhor" in bloco


def test_orquestrador_retorna_label_amigavel():
    resultado = processar_pergunta_com_tools(
        pergunta="Com minha renda e gastos, quanto sobra?",
        memoria=memoria_teste(),
    )

    assert resultado["tool_label"] == "Análise do orçamento mensal"


def test_orquestrador_retorna_motivo_tool():
    resultado = processar_pergunta_com_tools(
        pergunta="Com minha renda e gastos, quanto sobra?",
        memoria=memoria_teste(),
    )

    assert resultado["motivo_tool"]
    assert "renda" in resultado["motivo_tool"].lower()
    assert "gastos" in resultado["motivo_tool"].lower()
