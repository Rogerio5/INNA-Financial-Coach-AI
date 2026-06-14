SYSTEM_PROMPT = '''
Você é a INNA, uma educadora financeira com IA.
Seu papel é explicar a situação financeira do usuário de forma simples, segura e educativa.

Regras:
- Não recomende compra ou venda de investimentos.
- Não prometa rentabilidade.
- Não substitua consultor financeiro certificado.
- Use linguagem clara, humana e motivadora.
- Gere passos práticos para organização financeira.
- Foque em educação, planejamento e hábitos.
'''


def build_plan_prompt(user_data: dict, diagnosis: dict) -> str:
    return f'''
Dados do usuário:
Nome: {user_data.get("nome")}
Renda mensal: R$ {user_data.get("renda_mensal")}
Gastos fixos: R$ {user_data.get("gastos_fixos")}
Gastos variáveis: R$ {user_data.get("gastos_variaveis")}
Dívidas mensais: R$ {user_data.get("dividas_mensais")}
Reserva atual: R$ {user_data.get("reserva_atual")}
Objetivo: {user_data.get("objetivo")}

Diagnóstico calculado:
Saldo estimado: R$ {diagnosis.get("saldo_estimado")}
Comprometimento de renda: {diagnosis.get("comprometimento_renda_percentual")}%
Meses de reserva: {diagnosis.get("meses_reserva_estimados")}
Score financeiro: {diagnosis.get("score_financeiro")}
Nível de risco: {diagnosis.get("nivel_risco")}

Crie um plano de ação de 30 dias, dividido em:
1. Primeira semana
2. Segunda semana
3. Terceira semana
4. Quarta semana
5. Próximo passo após 30 dias

A resposta deve ser simples, educativa e prática.
'''
