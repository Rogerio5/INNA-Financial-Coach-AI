"""
=========================================================
INNA Financial Coach AI
Prompt Builder Inteligente

Responsável por montar o contexto completo enviado ao Gemini.
=========================================================
"""

from datetime import datetime



def formatar_moeda(valor, moeda="BRL"):
    if valor is None:
        return "Não informado"

    try:
        valor_float = float(valor)
    except Exception:
        return str(valor)

    if moeda == "BRL":
        texto = f"R$ {valor_float:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return texto

    if moeda == "USD":
        return f"US$ {valor_float:,.2f}"

    if moeda == "EUR":
        texto = f"€ {valor_float:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return texto

    return f"{moeda} {valor_float:,.2f}"


def _secao(titulo: str, conteudo: str) -> str:
    return f"""
==================================================
{titulo.upper()}
==================================================

{conteudo.strip()}
"""


def _identidade() -> str:
    return """
Você é a INNA Financial Coach AI.

Você ajuda pessoas com educação financeira de forma simples,
acolhedora, responsável e educativa.

Você pode orientar sobre:
- organização financeira;
- cartão de crédito;
- reserva financeira;
- dívidas;
- Pix;
- segurança digital;
- metas financeiras.

Nunca peça senha, token, código bancário, chave Pix sensível,
número completo de cartão ou dados íntimos.
"""


def _memoria(memoria) -> str:
    if not memoria:
        return "Nenhuma memória ativa disponível para este usuário."

    moeda = memoria.get("moeda") or "BRL"

    renda_formatada = formatar_moeda(memoria.get("renda_mensal"), moeda)
    gastos_formatados = formatar_moeda(memoria.get("gastos_mensais"), moeda)
    reserva_formatada = formatar_moeda(memoria.get("valor_reserva"), moeda)

    reserva_semanal = "Não informado"

    try:
        if memoria.get("valor_reserva") is not None:
            reserva_semanal = formatar_moeda(float(memoria.get("valor_reserva")) / 4, moeda)
    except Exception:
        reserva_semanal = "Não informado"

    saldo_mensal = "Não informado"

    try:
        if memoria.get("renda_mensal") is not None and memoria.get("gastos_mensais") is not None:
            saldo_mensal = formatar_moeda(
                float(memoria.get("renda_mensal")) - float(memoria.get("gastos_mensais")),
                moeda
            )
    except Exception:
        saldo_mensal = "Não informado"

    return f"""
Usuário ID: {memoria.get("usuario_id")}
Nome: {memoria.get("nome")}
Idioma: {memoria.get("idioma")}
Moeda: {moeda}

Renda mensal: {renda_formatada}
Gastos mensais: {gastos_formatados}
Saldo estimado mensal: {saldo_mensal}
Valor que consegue guardar por mês: {reserva_formatada}
Valor aproximado por semana: {reserva_semanal}

Possui dívidas: {memoria.get("possui_dividas")}
Usa cartão de crédito: {memoria.get("uso_cartao_credito")}

Perfil financeiro: {memoria.get("perfil_financeiro")}
Objetivo principal: {memoria.get("objetivo_principal")}
Última meta: {memoria.get("ultima_meta")}
Último score: {memoria.get("ultimo_score")}
Último risco: {memoria.get("ultimo_risco")}

Resumo:
{memoria.get("resumo_contexto")}

Memória JSON:
{memoria.get("memoria_json")}
"""


def _historico(historico) -> str:
    if not historico:
        return "Sem histórico recente disponível."

    texto = ""

    for item in historico:
        texto += f"""
Pergunta:
{item.get("pergunta")}

Resposta:
{item.get("resposta")}

--------------------------
"""

    return texto


def _rag(chunks) -> str:
    if not chunks:
        return "Nenhum contexto RAG encontrado."

    texto = ""

    for i, chunk in enumerate(chunks, start=1):
        texto += f"""
Fonte {i}

Documento:
{chunk.get("documento_origem") or chunk.get("documento")}

Categoria:
{chunk.get("categoria", "geral")}

Similaridade:
{chunk.get("similaridade_aproximada") or chunk.get("score_rag")}

Conteúdo:
{chunk.get("texto")}

--------------------------
"""

    return texto


def _regras() -> str:
    return """
REGRAS OBRIGATÓRIAS

1. Use primeiro a memória do usuário quando ela existir.

2. Use o RAG como complemento.

3. Nunca invente números financeiros.

4. Se existir renda e gastos na memória, calcule quanto sobra.

5. Se existir valor_reserva, calcule quanto isso representa por semana.

6. Cite explicitamente os valores conhecidos quando eles forem úteis.

7. Se o usuário perguntar quanto pode guardar, use valor_reserva como base.

8. Se houver meta financeira, use a meta na orientação.

9. Responda no idioma salvo na memória, quando disponível.

10. Use a moeda salva na memória, quando disponível.

11. Nunca peça senha, token, código de segurança, CVV ou dados bancários sensíveis.

12. Para Pix suspeito, oriente verificar no aplicativo oficial do banco.

13. Não oriente devolver Pix por fora.

14. Seja simples, claro, acolhedor e educativo.

15. Finalize com um próximo passo prático.

16. Formate valores monetários sempre assim:
R$ 200,00
R$ 3.500,00
R$ 50,00 por semana

17. Nunca escreva valores grudados, como R200, R$200por mês ou R$50por semana.

18. Separe frases em parágrafos curtos.

19. Quando fizer cálculo, mostre a conta de forma simples.

Exemplo:
"Você informou que consegue guardar R$ 200,00 por mês.
Dividindo por 4 semanas, isso dá aproximadamente R$ 50,00 por semana."

20. Evite excesso de negrito, símbolos ou markdown quebrado.

21. Use este formato preferencial:

Olá, [nome].

Resumo:
[resumo curto usando memória]

Cálculo:
[conta simples]

Orientação:
[orientação prática]

Próximo passo:
[ação simples]
"""


def montar_prompt_inna(
    pergunta: str,
    memoria=None,
    historico=None,
    chunks=None,
) -> str:
    prompt = ""

    prompt += _secao("Identidade", _identidade())
    prompt += _secao("Memória do Usuário", _memoria(memoria))
    prompt += _secao("Histórico Recente", _historico(historico))
    prompt += _secao("Documentos RAG", _rag(chunks))
    prompt += _secao("Regras", _regras())
    prompt += _secao("Data Atual", str(datetime.now()))
    prompt += _secao("Pergunta do Usuário", pergunta)

    return prompt
