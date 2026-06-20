
LANGUAGE_NAME_BY_CODE = {
    "pt": "Português Brasil",
    "en_us": "English US",
    "en_gb": "English UK",
    "es": "Español",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "ro": "Română",
    "uk": "Українська",
    "ru": "Русский",
    "ar": "العربية",
    "ch": "Deutsch Schweiz",
}

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL, INNA_MOCK_MODE


def build_financial_prompt(payload: dict, diagnosis: dict) -> str:
    nome = payload.get("nome", "Usuario")
    objetivo = payload.get("objetivo", "Organizar minha vida financeira")

    renda = float(payload.get("renda_mensal", 0))
    gastos_fixos = float(payload.get("gastos_fixos", 0))
    gastos_variaveis = float(payload.get("gastos_variaveis", 0))
    dividas = float(payload.get("dividas_mensais", 0))
    reserva = float(payload.get("reserva_atual", 0))

    saldo = float(diagnosis.get("saldo_estimado", 0))
    score = int(diagnosis.get("score_financeiro", 0))
    risco = diagnosis.get("nivel_risco", "Indefinido")
    comprometimento = float(diagnosis.get("comprometimento_renda_percentual", 0))
    meses_reserva = float(diagnosis.get("meses_reserva_estimados", 0))
    dias_reserva = meses_reserva * 30

    return f"""
Voce e a INNA, uma educadora financeira digital. A resposta final deve estar 100% no idioma informado pelo campo 'Idioma obrigatório da resposta'.

Crie um plano de acao de 30 dias no idioma informado, curto, direto, seguro e educativo para a pessoa abaixo.

User data / Données utilisateur / Benutzerdaten / Dados do usuário:
- Nome: {nome}
- Financial goal / Objectif financier / Finanzielles Ziel / Objetivo financeiro: {objetivo}
- Idioma obrigatório da resposta: {idioma_nome}
- Moeda obrigatória: {moeda} ({simbolo_moeda})
- Monthly income / Revenu mensuel / Monatliches Einkommen / Renda mensal: {simbolo_moeda} {renda:.2f} ({moeda})
- Fixed expenses / Dépenses fixes / Fixkosten / Gastos fixos: {simbolo_moeda} {gastos_fixos:.2f} ({moeda})
- Variable expenses / Dépenses variables / Variable Ausgaben / Gastos variáveis: {simbolo_moeda} {gastos_variaveis:.2f} ({moeda})
- Monthly debts / Dettes mensuelles / Monatliche Schulden / Dívidas mensais: {simbolo_moeda} {dividas:.2f} ({moeda})
- Current savings / Épargne actuelle / Aktuelle Rücklage / Reserva atual: {simbolo_moeda} {reserva:.2f} ({moeda})

Diagnostico calculado:
- Saldo estimado: R$ {saldo:.2f}
- Score financeiro: {score}/100
- Nivel de risco: {risco}
- Comprometimento da renda: {comprometimento:.1f}%
- Reserva estimada: {meses_reserva:.2f} mes(es), aproximadamente {dias_reserva:.0f} dias

Regras importantes:
- Nao recomende compra ou venda de ativos.
- Nao prometa rentabilidade.
- Nao substitua um profissional certificado.
- Use linguagem simples e acolhedora.
- Responda obrigatoriamente no idioma informado.
- Use a moeda informada nos valores financeiros.
- Não misture português com outro idioma.
- Se o idioma for Deutsch, escreva tudo em alemão.
- Se o idioma for English US ou English UK, escreva tudo em inglês.
- Se o idioma for Español, escreva tudo em espanhol.
- Se o idioma for Français, escreva tudo em francês.
- Se o idioma for Italiano, escreva tudo em italiano.
- Se o idioma for Română, escreva tudo em romeno.
- Se o idioma for Українська, escreva tudo em ucraniano.
- Se o idioma for Русский, escreva tudo em russo.
- Se o idioma for العربية, escreva tudo em árabe.
- Explique prioridades de forma pratica.
- Organize em 4 semanas, com apenas 1 objetivo e 2 acoes curtas por semana.
- Traduza os títulos Semana 1, Semana 2, Semana 3 e Semana 4 para o idioma informado.
- Traduza também Resumo da situação, Plano de ação e Próximo passo recomendado.
- Evite textos longos.
- Nao use muitos detalhes.
- O plano completo deve caber bem em 1 pagina de PDF.
- Inclua proximos passos claros e curtos.
""".strip()


def generate_fallback_plan(payload: dict, diagnosis: dict) -> str:
    nome = payload.get("nome", "Usuario")
    saldo = float(diagnosis.get("saldo_estimado", 0))
    score = int(diagnosis.get("score_financeiro", 0))
    risco = diagnosis.get("nivel_risco", "Indefinido")
    comprometimento = float(diagnosis.get("comprometimento_renda_percentual", 0))
    meses_reserva = float(diagnosis.get("meses_reserva_estimados", 0))
    dias_reserva = meses_reserva * 30

    return f"""
Olá, {nome}. A INNA preparou um plano de ação seguro com base no seu diagnóstico financeiro.

Resumo da situação:
- Saldo mensal estimado: R$ {saldo:.2f}
- Score financeiro: {score}/100
- Nível de risco: {risco}
- Comprometimento da renda: {comprometimento:.1f}%
- Reserva atual estimada: {meses_reserva:.2f} mês(es), aproximadamente {dias_reserva:.0f} dias

Plano de ação de 30 dias:

Semana 1 — Entender para onde o dinheiro está indo
- Anote todos os gastos fixos e variáveis.
- Separe os gastos em essenciais, importantes e opcionais.
- Identifique pelo menos 3 gastos que podem ser reduzidos sem prejudicar sua rotina.

Semana 2 — Reduzir desperdícios
- Defina um limite semanal para gastos variáveis.
- Evite novas dívidas durante este período.
- Direcione qualquer sobra para a reserva financeira.

Semana 3 — Fortalecer a reserva
- Como sua reserva ainda cobre poucos dias, priorize aumentar esse valor.
- Mesmo que o valor guardado seja pequeno, mantenha consistência.
- O objetivo inicial é chegar a pelo menos 1 mês de gastos cobertos.

Semana 4 — Revisar e ajustar
- Compare sua situação atual com o início do plano.
- Veja se o saldo mensal melhorou.
- Ajuste metas para o próximo mês.

Próximo passo recomendado:
Priorize aumentar sua reserva financeira e reduzir gastos variáveis antes de assumir novos compromissos financeiros.

Aviso:
A INNA atua como educadora financeira digital. Ela não recomenda compra ou venda de ativos, não promete rentabilidade e não substitui profissionais certificados.
""".strip()


def generate_ai_plan(payload: dict, diagnosis: dict) -> str:
    if INNA_MOCK_MODE:
        return generate_fallback_plan(payload, diagnosis)

    if not GEMINI_API_KEY:
        return generate_fallback_plan(payload, diagnosis)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = build_financial_prompt(payload, diagnosis)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            return generate_fallback_plan(payload, diagnosis)

        return text

    except Exception:
        return generate_fallback_plan(payload, diagnosis)
