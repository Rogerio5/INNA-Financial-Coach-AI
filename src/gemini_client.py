
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
- Calculated balance / Solde calculé / Berechneter Überschuss / Saldo calculado: {simbolo_moeda} {saldo:.2f} ({moeda})
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
    lang = payload.get("idioma", "pt")
    moeda = payload.get("moeda", "BRL")
    symbol = payload.get("simbolo_moeda", "R$")

    saldo = float(diagnosis.get("saldo_estimado", 0))
    score = int(diagnosis.get("score_financeiro", 0))
    risco = diagnosis.get("nivel_risco", "Indefinido")
    comprometimento = float(diagnosis.get("comprometimento_renda_percentual", 0))
    meses_reserva = float(diagnosis.get("meses_reserva_estimados", 0))
    dias_reserva = meses_reserva * 30

    def money(value: float) -> str:
        if moeda in ["USD", "GBP"]:
            return f"{symbol}{value:,.2f}"
        if moeda == "CHF":
            return f"{symbol} {value:,.2f}".replace(",", "'")
        if moeda in ["EUR", "BRL", "RON", "UAH", "RUB"]:
            formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{symbol} {formatted}"
        return f"{symbol} {value:,.2f}"

    risk_map = {
        "Baixo": {
            "pt": "Baixo", "en_us": "Low", "en_gb": "Low", "es": "Bajo", "fr": "Faible",
            "de": "Niedrig", "ch": "Niedrig", "it": "Basso", "ro": "Scăzut",
            "uk": "Низький", "ru": "Низкий", "ar": "منخفض",
        },
        "Medio": {
            "pt": "Médio", "en_us": "Medium", "en_gb": "Medium", "es": "Medio", "fr": "Moyen",
            "de": "Mittel", "ch": "Mittel", "it": "Medio", "ro": "Mediu",
            "uk": "Середній", "ru": "Средний", "ar": "متوسط",
        },
        "Alto": {
            "pt": "Alto", "en_us": "High", "en_gb": "High", "es": "Alto", "fr": "Élevé",
            "de": "Hoch", "ch": "Hoch", "it": "Alto", "ro": "Ridicat",
            "uk": "Високий", "ru": "Высокий", "ar": "مرتفع",
        },
    }

    risco_txt = risk_map.get(risco, {}).get(lang, risco)

    texts = {
        "pt": {
            "intro": f"Olá, {nome}. A INNA preparou um plano de ação seguro com base no seu diagnóstico financeiro.",
            "summary": "Resumo da situação:",
            "balance": "Saldo mensal estimado",
            "score": "Score financeiro",
            "risk": "Nível de risco",
            "commitment": "Comprometimento da renda",
            "reserve": "Reserva atual estimada",
            "plan": "Plano de ação de 30 dias:",
            "w1": "Semana 1 — Entender para onde o dinheiro está indo",
            "w1a": "Anote todos os gastos fixos e variáveis.",
            "w1b": "Separe os gastos em essenciais, importantes e opcionais.",
            "w1c": "Identifique pelo menos 3 gastos que podem ser reduzidos sem prejudicar sua rotina.",
            "w2": "Semana 2 — Reduzir desperdícios",
            "w2a": "Defina um limite semanal para gastos variáveis.",
            "w2b": "Evite novas dívidas durante este período.",
            "w2c": "Direcione qualquer sobra para a reserva financeira.",
            "w3": "Semana 3 — Fortalecer a reserva",
            "w3a": "Como sua reserva ainda cobre poucos dias, priorize aumentar esse valor.",
            "w3b": "Mesmo que o valor guardado seja pequeno, mantenha consistência.",
            "w3c": "O objetivo inicial é chegar a pelo menos 1 mês de gastos cobertos.",
            "w4": "Semana 4 — Revisar e ajustar",
            "w4a": "Compare sua situação atual com o início do plano.",
            "w4b": "Veja se o saldo mensal melhorou.",
            "w4c": "Ajuste metas para o próximo mês.",
            "next": "Próximo passo recomendado:",
            "next_text": "Priorize aumentar sua reserva financeira e reduzir gastos variáveis antes de assumir novos compromissos financeiros.",
            "notice": "Aviso:",
            "notice_text": "A INNA atua como educadora financeira digital. Ela não recomenda compra ou venda de ativos, não promete rentabilidade e não substitui profissionais certificados.",
            "months": "mês(es)",
            "days": "dias",
            "approximately": "aproximadamente",
        },
        "fr": {
            "intro": f"Bonjour, {nome}. INNA a préparé un plan d’action sûr à partir de votre diagnostic financier.",
            "summary": "Résumé de la situation :",
            "balance": "Solde mensuel estimé",
            "score": "Score financier",
            "risk": "Niveau de risque",
            "commitment": "Engagement du revenu",
            "reserve": "Épargne actuelle estimée",
            "plan": "Plan d’action de 30 jours :",
            "w1": "Semaine 1 — Comprendre où va l’argent",
            "w1a": "Notez toutes les dépenses fixes et variables.",
            "w1b": "Séparez les dépenses essentielles, importantes et optionnelles.",
            "w1c": "Identifiez au moins 3 dépenses qui peuvent être réduites sans nuire à votre routine.",
            "w2": "Semaine 2 — Réduire les gaspillages",
            "w2a": "Définissez une limite hebdomadaire pour les dépenses variables.",
            "w2b": "Évitez de nouvelles dettes pendant cette période.",
            "w2c": "Dirigez tout excédent vers votre épargne de sécurité.",
            "w3": "Semaine 3 — Renforcer l’épargne",
            "w3a": "Comme votre épargne couvre encore peu de jours, donnez la priorité à son augmentation.",
            "w3b": "Même si le montant épargné est petit, gardez de la régularité.",
            "w3c": "L’objectif initial est d’atteindre au moins 1 mois de dépenses couvertes.",
            "w4": "Semaine 4 — Réviser et ajuster",
            "w4a": "Comparez votre situation actuelle avec le début du plan.",
            "w4b": "Vérifiez si le solde mensuel s’est amélioré.",
            "w4c": "Ajustez les objectifs pour le mois suivant.",
            "next": "Prochaine étape recommandée :",
            "next_text": "Priorisez l’augmentation de votre épargne et la réduction des dépenses variables avant d’assumer de nouveaux engagements financiers.",
            "notice": "Avis :",
            "notice_text": "INNA agit comme éducatrice financière numérique. Elle ne recommande pas l’achat ou la vente d’actifs, ne promet pas de rentabilité et ne remplace pas des professionnels certifiés.",
            "months": "mois",
            "days": "jours",
            "approximately": "environ",
        },
        "en_us": {
            "intro": f"Hello, {nome}. INNA prepared a safe action plan based on your financial diagnosis.",
            "summary": "Situation summary:",
            "balance": "Estimated monthly balance",
            "score": "Financial score",
            "risk": "Risk level",
            "commitment": "Income commitment",
            "reserve": "Estimated current savings",
            "plan": "30-day action plan:",
            "w1": "Week 1 — Understand where your money is going",
            "w1a": "Write down all fixed and variable expenses.",
            "w1b": "Separate expenses into essential, important, and optional.",
            "w1c": "Identify at least 3 expenses that can be reduced without hurting your routine.",
            "w2": "Week 2 — Reduce waste",
            "w2a": "Set a weekly limit for variable expenses.",
            "w2b": "Avoid new debt during this period.",
            "w2c": "Send any surplus to your emergency savings.",
            "w3": "Week 3 — Strengthen savings",
            "w3a": "Because your savings still cover only a few days, prioritize increasing this amount.",
            "w3b": "Even if the saved amount is small, keep consistency.",
            "w3c": "The first goal is to reach at least 1 month of covered expenses.",
            "w4": "Week 4 — Review and adjust",
            "w4a": "Compare your current situation with the beginning of the plan.",
            "w4b": "Check whether your monthly balance has improved.",
            "w4c": "Adjust your goals for the next month.",
            "next": "Recommended next step:",
            "next_text": "Prioritize increasing your savings and reducing variable expenses before taking on new financial commitments.",
            "notice": "Notice:",
            "notice_text": "INNA acts as a digital financial educator. It does not recommend buying or selling assets, does not promise returns, and does not replace certified professionals.",
            "months": "month(s)",
            "days": "days",
            "approximately": "approximately",
        },
        "en_gb": {
            "intro": f"Hello, {nome}. INNA prepared a safe action plan based on your financial diagnosis.",
            "summary": "Situation summary:",
            "balance": "Estimated monthly balance",
            "score": "Financial score",
            "risk": "Risk level",
            "commitment": "Income commitment",
            "reserve": "Estimated current savings",
            "plan": "30-day action plan:",
            "w1": "Week 1 — Understand where your money is going",
            "w1a": "Write down all fixed and variable expenses.",
            "w1b": "Separate expenses into essential, important, and optional.",
            "w1c": "Identify at least 3 expenses that can be reduced without affecting your routine.",
            "w2": "Week 2 — Reduce waste",
            "w2a": "Set a weekly limit for variable expenses.",
            "w2b": "Avoid new debt during this period.",
            "w2c": "Send any surplus to your emergency savings.",
            "w3": "Week 3 — Strengthen savings",
            "w3a": "Because your savings still cover only a few days, prioritise increasing this amount.",
            "w3b": "Even if the saved amount is small, keep consistency.",
            "w3c": "The first goal is to reach at least 1 month of covered expenses.",
            "w4": "Week 4 — Review and adjust",
            "w4a": "Compare your current situation with the beginning of the plan.",
            "w4b": "Check whether your monthly balance has improved.",
            "w4c": "Adjust your goals for the next month.",
            "next": "Recommended next step:",
            "next_text": "Prioritise increasing your savings and reducing variable expenses before taking on new financial commitments.",
            "notice": "Notice:",
            "notice_text": "INNA acts as a digital financial educator. It does not recommend buying or selling assets, does not promise returns, and does not replace certified professionals.",
            "months": "month(s)",
            "days": "days",
            "approximately": "approximately",
        },
        "es": {
            "intro": f"Hola, {nome}. INNA preparó un plan de acción seguro basado en tu diagnóstico financiero.",
            "summary": "Resumen de la situación:",
            "balance": "Saldo mensual estimado",
            "score": "Puntuación financiera",
            "risk": "Nivel de riesgo",
            "commitment": "Compromiso de ingresos",
            "reserve": "Reserva actual estimada",
            "plan": "Plan de acción de 30 días:",
            "w1": "Semana 1 — Entender a dónde va el dinero",
            "w1a": "Anota todos los gastos fijos y variables.",
            "w1b": "Separa los gastos en esenciales, importantes y opcionales.",
            "w1c": "Identifica al menos 3 gastos que puedan reducirse sin afectar tu rutina.",
            "w2": "Semana 2 — Reducir desperdicios",
            "w2a": "Define un límite semanal para gastos variables.",
            "w2b": "Evita nuevas deudas durante este período.",
            "w2c": "Dirige cualquier sobrante a tu reserva financiera.",
            "w3": "Semana 3 — Fortalecer la reserva",
            "w3a": "Como tu reserva aún cubre pocos días, prioriza aumentarla.",
            "w3b": "Aunque el monto ahorrado sea pequeño, mantén la constancia.",
            "w3c": "El objetivo inicial es llegar al menos a 1 mes de gastos cubiertos.",
            "w4": "Semana 4 — Revisar y ajustar",
            "w4a": "Compara tu situación actual con el inicio del plan.",
            "w4b": "Verifica si el saldo mensual mejoró.",
            "w4c": "Ajusta metas para el próximo mes.",
            "next": "Próximo paso recomendado:",
            "next_text": "Prioriza aumentar tu reserva financiera y reducir gastos variables antes de asumir nuevos compromisos financieros.",
            "notice": "Aviso:",
            "notice_text": "INNA actúa como educadora financiera digital. No recomienda compra o venta de activos, no promete rentabilidad y no sustituye a profesionales certificados.",
            "months": "mes(es)",
            "days": "días",
            "approximately": "aproximadamente",
        },
        "de": {
            "intro": f"Hallo, {nome}. INNA hat auf Grundlage deiner Finanzdiagnose einen sicheren Aktionsplan vorbereitet.",
            "summary": "Zusammenfassung der Situation:",
            "balance": "Geschätzter monatlicher Überschuss",
            "score": "Finanzscore",
            "risk": "Risikostufe",
            "commitment": "Einkommensbindung",
            "reserve": "Geschätzte aktuelle Rücklage",
            "plan": "30-Tage-Aktionsplan:",
            "w1": "Woche 1 — Verstehen, wohin das Geld fließt",
            "w1a": "Notiere alle festen und variablen Ausgaben.",
            "w1b": "Trenne Ausgaben in notwendige, wichtige und optionale Kategorien.",
            "w1c": "Finde mindestens 3 Ausgaben, die ohne große Einschränkung reduziert werden können.",
            "w2": "Woche 2 — Verschwendung reduzieren",
            "w2a": "Lege ein wöchentliches Limit für variable Ausgaben fest.",
            "w2b": "Vermeide in diesem Zeitraum neue Schulden.",
            "w2c": "Leite jeden Überschuss in deine Rücklage.",
            "w3": "Woche 3 — Rücklage stärken",
            "w3a": "Da deine Rücklage noch wenige Tage abdeckt, priorisiere ihren Aufbau.",
            "w3b": "Auch kleine Beträge helfen, wenn du konsequent bleibst.",
            "w3c": "Das erste Ziel ist mindestens 1 Monat gedeckter Ausgaben.",
            "w4": "Woche 4 — Überprüfen und anpassen",
            "w4a": "Vergleiche deine aktuelle Situation mit dem Beginn des Plans.",
            "w4b": "Prüfe, ob sich dein monatlicher Überschuss verbessert hat.",
            "w4c": "Passe deine Ziele für den nächsten Monat an.",
            "next": "Empfohlener nächster Schritt:",
            "next_text": "Priorisiere den Aufbau deiner Rücklage und die Reduzierung variabler Ausgaben, bevor du neue finanzielle Verpflichtungen eingehst.",
            "notice": "Hinweis:",
            "notice_text": "INNA agiert als digitale Finanzbildnerin. Sie empfiehlt keinen Kauf oder Verkauf von Vermögenswerten, verspricht keine Rendite und ersetzt keine zertifizierten Fachleute.",
            "months": "Monat(e)",
            "days": "Tage",
            "approximately": "ungefähr",
        },
    }

    # Reaproveita alemão para Suíça se não houver texto específico
    if lang == "ch":
        lang = "de"

    t = texts.get(lang, texts["en_us"])

    return f"""
{t["intro"]}

{t["summary"]}
- {t["balance"]}: {money(saldo)}
- {t["score"]}: {score}/100
- {t["risk"]}: {risco_txt}
- {t["commitment"]}: {comprometimento:.1f}%
- {t["reserve"]}: {meses_reserva:.2f} {t["months"]}, {t.get("approximately", "approximately")} {dias_reserva:.0f} {t["days"]}

{t["plan"]}

{t["w1"]}
- {t["w1a"]}
- {t["w1b"]}
- {t["w1c"]}

{t["w2"]}
- {t["w2a"]}
- {t["w2b"]}
- {t["w2c"]}

{t["w3"]}
- {t["w3a"]}
- {t["w3b"]}
- {t["w3c"]}

{t["w4"]}
- {t["w4a"]}
- {t["w4b"]}
- {t["w4c"]}

{t["next"]}
{t["next_text"]}

{t["notice"]}
{t["notice_text"]}
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
