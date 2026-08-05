from src.services.prompts.builder import (
    montar_prompt_inna,
)


def memoria_teste():
    return {
        "usuario_id": "demo_user",
        "nome": "Usuário Demo",
        "idioma": "pt",
        "moeda": "BRL",
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
        "possui_dividas": True,
        "uso_cartao_credito": True,
        "perfil_financeiro": "organizando",
        "objetivo_principal": "Organizar as finanças",
        "ultima_meta": "Guardar R$ 50 por semana",
        "preferencia_linguagem": "simples",
    }


def test_prompt_contem_dados_financeiros():
    prompt = montar_prompt_inna(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
    )

    assert "R$ 6.300,00" in prompt
    assert "R$ 3.300,00" in prompt
    assert "R$ 3.000,00" in prompt
    assert "R$ 1.200,00" in prompt
    assert "R$ 300,00" in prompt


def test_prompt_contem_regras_de_educacao_financeira():
    prompt = montar_prompt_inna(
        pergunta="O que faço com minhas dívidas?",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
    )

    prompt_lower = prompt.lower()

    assert "nunca recomendações" in prompt_lower
    assert "não diga ao usuário o que ele deve fazer" in prompt_lower
    assert "vale avaliar" in prompt_lower


def test_prompt_diferencia_meta_de_evolucao():
    prompt = montar_prompt_inna(
        pergunta="Quanto posso guardar?",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
    )

    assert "A última meta representa um objetivo registrado" in prompt

    assert 'Só use a seção "Evolução:"' in prompt


def test_prompt_inclui_chunk_rag():
    chunks = [
        {
            "documento_origem": "guia.md",
            "categoria": "reserva_financeira",
            "score_rag": 0.91,
            "texto": (
                "A reserva pode começar com um valor compatível com o orçamento."
            ),
        }
    ]

    prompt = montar_prompt_inna(
        pergunta="Como criar uma reserva?",
        memoria=memoria_teste(),
        historico=None,
        chunks=chunks,
    )

    assert "guia.md" in prompt
    assert "reserva_financeira" in prompt
    assert "0.91" in prompt


def test_prompt_inclui_contexto_tools():
    contexto_tools = """
[TOOL FINANCEIRA EXECUTADA]
Ferramenta: calcular_capacidade_semanal

Resultado determinístico:
{
  "valor_semanal_estimado": 300.0
}
"""

    prompt = montar_prompt_inna(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
        contexto_tools=contexto_tools,
    )

    assert "TOOLS FINANCEIRAS" in prompt
    assert "calcular_capacidade_semanal" in prompt
    assert "valor_semanal_estimado" in prompt
    assert "300.0" in prompt


def test_prompt_funciona_sem_contexto_tools():
    prompt = montar_prompt_inna(
        pergunta="Olá",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
    )

    assert "TOOLS FINANCEIRAS" in prompt
    assert "Nenhuma ferramenta financeira determinística foi acionada" in prompt


def test_prompt_inclui_regras_de_apresentacao_profissional():
    prompt = montar_prompt_inna(
        pergunta="Quanto sobra?",
        memoria=memoria_teste(),
        historico=None,
        chunks=None,
    )

    assert "APRESENTAÇÃO PROFISSIONAL" in prompt
    assert "Não repita o mesmo saldo" in prompt
    assert "Próximo passo sugerido" in prompt
    assert "Saldo mensal estimado" in prompt
