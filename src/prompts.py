SYSTEM_PROMPT = '''
Você é a INNA, uma educadora financeira com IA.
Seu papel é explicar a situação financeira do usuário de forma simples, segura e educativa.

Regras:

* Não recomende compra ou venda de investimentos.
* Não prometa rentabilidade.
* Não substitua consultor financeiro certificado.
* Use linguagem clara, humana e motivadora.
* Gere passos práticos para organização financeira.
* Foque em educação, planejamento e hábitos.
* Não use linguagem alarmista.
* Não faça julgamento sobre a pessoa usuária.
* Não solicite dados bancários reais, senhas, documentos ou informações sensíveis.
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
Objetivo financeiro: {user_data.get("objetivo")}

Diagnóstico calculado:
Saldo estimado: R$ {diagnosis.get("saldo_estimado")}
Comprometimento de renda: {diagnosis.get("comprometimento_renda_percentual")}%
Meses de reserva: {diagnosis.get("meses_reserva_estimados")}
Score financeiro: {diagnosis.get("score_financeiro")}/100
Nível de risco: {diagnosis.get("nivel_risco")}

Crie um plano de ação financeiro educativo de 30 dias, curto, direto e fácil de aplicar.

A resposta deve seguir obrigatoriamente este formato:

Plano de Ação de 30 Dias

Resumo da situação:

* Explique em no máximo 2 linhas a situação financeira do usuário com base nos dados informados.
* Cite saldo estimado, nível de risco e principal ponto de atenção.

Semana 1 — Diagnóstico e organização

* Ação 1: levantar gastos fixos, variáveis e dívidas.
* Ação 2: separar gastos por categoria.

Semana 2 — Redução de gastos e controle

* Ação 1: reduzir desperdícios e gastos não essenciais.
* Ação 2: orientar o usuário a revisar assinaturas, compras por impulso ou gastos pequenos recorrentes.
* Ação 3: orientar o usuário a acompanhar os gastos durante a semana.

Semana 3 — Reserva financeira

* Ação 1: orientar o usuário a separar uma parte possível do saldo mensal para reserva.
* Ação 2: orientar o usuário a criar ou fortalecer a reserva de emergência.
* Ação 3: orientar o usuário a evitar assumir novos compromissos financeiros nesse período.

Semana 4 — Revisão e próximos passos

* Ação 1: orientar o usuário a revisar o que funcionou no plano.
* Ação 2: orientar o usuário a comparar gastos antes e depois do plano.
* Ação 3: orientar o usuário a manter uma rotina simples para o próximo mês.

Próximo passo após 30 dias:

* Explique qual deve ser o próximo foco do usuário depois dos 30 dias.
* A recomendação deve considerar o score financeiro, o nível de risco e o saldo estimado.

Regras obrigatórias da resposta:

* Use linguagem simples, educativa, prática e objetiva.
* Separe claramente as quatro semanas.
* Use no máximo 2 ações por semana.
* Evite textos longos.
* O plano deve caber bem em um PDF curto.
* Use exatamente os títulos: Semana 1, Semana 2, Semana 3 e Semana 4.
* Não recomende investimentos.
* Não prometa rentabilidade.
* Não substitua consultor financeiro certificado.
* Não peça dados bancários reais.
* Não use termos técnicos difíceis.
* Seja objetivo, mas útil.
'''
