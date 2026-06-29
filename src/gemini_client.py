
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

import os

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL, INNA_MOCK_MODE
from src.prompts import build_plan_prompt

LAST_GEMINI_USAGE_METADATA = {
    "provider": "gemini",
    "modelo_ia": GEMINI_MODEL,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "custo_estimado_usd": 0.0,
    "tokens_disponiveis": False,
}


def _usage_value(usage, *names):
    for name in names:
        if usage is None:
            continue

        if isinstance(usage, dict) and name in usage:
            return usage.get(name)

        value = getattr(usage, name, None)
        if value is not None:
            return value

    return 0


def _estimate_gemini_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Custo estimado opcional.
    Para custo real, configure no Render/.env:
    GEMINI_INPUT_COST_PER_1M
    GEMINI_OUTPUT_COST_PER_1M
    """
    input_cost_per_1m = float(os.getenv("GEMINI_INPUT_COST_PER_1M", "0") or 0)
    output_cost_per_1m = float(os.getenv("GEMINI_OUTPUT_COST_PER_1M", "0") or 0)

    return round(
        (prompt_tokens / 1_000_000) * input_cost_per_1m
        + (completion_tokens / 1_000_000) * output_cost_per_1m,
        6,
    )


def _update_last_gemini_usage(response=None, fallback: bool = False):
    global LAST_GEMINI_USAGE_METADATA

    if fallback or response is None:
        LAST_GEMINI_USAGE_METADATA = {
            "provider": "gemini",
            "modelo_ia": GEMINI_MODEL,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "custo_estimado_usd": 0.0,
            "tokens_disponiveis": False,
            "observabilidade": "fallback_sem_usage_metadata",
        }
        return LAST_GEMINI_USAGE_METADATA

    usage = getattr(response, "usage_metadata", None)

    prompt_tokens = int(
        _usage_value(
            usage,
            "prompt_token_count",
            "prompt_tokens",
            "input_tokens",
        )
        or 0
    )

    completion_tokens = int(
        _usage_value(
            usage,
            "candidates_token_count",
            "completion_tokens",
            "output_tokens",
        )
        or 0
    )

    total_tokens = int(
        _usage_value(
            usage,
            "total_token_count",
            "total_tokens",
        )
        or (prompt_tokens + completion_tokens)
        or 0
    )

    LAST_GEMINI_USAGE_METADATA = {
        "provider": "gemini",
        "modelo_ia": GEMINI_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "custo_estimado_usd": _estimate_gemini_cost_usd(prompt_tokens, completion_tokens),
        "tokens_disponiveis": total_tokens > 0,
    }

    return LAST_GEMINI_USAGE_METADATA


def get_last_gemini_usage_metadata() -> dict:
    return dict(LAST_GEMINI_USAGE_METADATA)


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
- Reserva estimada: sua reserva cobre aproximadamente {dias_reserva:.0f} dias de despesas ({meses_reserva:.2f} mes(es))

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
- Traduza também Resumo da situação, Plano de ação e Próxima orientação.
- Evite textos longos.
- Nao use muitos detalhes.
- O plano completo deve caber bem em 1 pagina de PDF.
- Inclua proximos passos claros e curtos.
""".strip()


def generate_fallback_plan(payload: dict, diagnosis: dict) -> str:
    nome = payload.get("nome", "Usuário")
    lang = str(payload.get("idioma", "pt") or "pt").lower()
    moeda = payload.get("moeda", "BRL")
    symbol = payload.get("simbolo_moeda", "R$")

    if lang == "ch":
        lang = "de"

    if lang == "en":
        lang = "en_us"

    saldo = float(diagnosis.get("saldo_estimado", 0))
    score = int(diagnosis.get("score_financeiro", 0))
    risco = diagnosis.get("nivel_risco", "Indefinido")
    comprometimento = float(diagnosis.get("comprometimento_renda_percentual", 0))
    meses_reserva = float(diagnosis.get("meses_reserva_estimados", 0))
    dias_reserva = max(0, int(round(meses_reserva * 30)))

    def money(value: float) -> str:
        try:
            value = float(value)
        except Exception:
            value = 0.0

        if moeda in ("USD", "GBP"):
            return f"{symbol}{value:,.2f}"

        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{symbol} {formatted}"

    risk_map = {
        "Baixo": {
            "pt": "Baixo", "en_us": "Low", "en_gb": "Low", "es": "Bajo", "fr": "Faible",
            "de": "Niedrig", "it": "Basso", "ro": "Scăzut",
            "uk": "Низький", "ru": "Низкий", "ar": "منخفض",
        },
        "Medio": {
            "pt": "Médio", "en_us": "Medium", "en_gb": "Medium", "es": "Medio", "fr": "Moyen",
            "de": "Mittel", "it": "Medio", "ro": "Mediu",
            "uk": "Середній", "ru": "Средний", "ar": "متوسط",
        },
        "Médio": {
            "pt": "Médio", "en_us": "Medium", "en_gb": "Medium", "es": "Medio", "fr": "Moyen",
            "de": "Mittel", "it": "Medio", "ro": "Mediu",
            "uk": "Середній", "ru": "Средний", "ar": "متوسط",
        },
        "Alto": {
            "pt": "Alto", "en_us": "High", "en_gb": "High", "es": "Alto", "fr": "Élevé",
            "de": "Hoch", "it": "Alto", "ro": "Ridicat",
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
            "reserve": "Reserva de emergência",
            "plan": "Plano de Ação de 30 Dias",
            "w1": "Semana 1 — Diagnóstico e organização",
            "w1a": "Levante seus gastos fixos, variáveis e dívidas.",
            "w1b": "Separe seus gastos por categoria para entender melhor o orçamento.",
            "w2": "Semana 2 — Redução de gastos e controle",
            "w2a": "Revise assinaturas, compras por impulso e pequenos gastos recorrentes.",
            "w2b": "Acompanhe os gastos durante a semana para evitar surpresas.",
            "w3": "Semana 3 — Reserva financeira",
            "w3a": "Separe uma parte possível do saldo mensal para fortalecer a reserva.",
            "w3b": "Crie o hábito de acompanhar a evolução da reserva.",
            "w4": "Semana 4 — Revisão e próximos passos",
            "w4a": "Revise o que funcionou melhor durante o plano.",
            "w4b": "Compare gastos antes e depois do plano.",
            "next": "Próxima orientação:",
            "next_text": "Após os 30 dias, mantenha o foco no ponto mais sensível do diagnóstico: reserva, dívidas ou controle de gastos, conforme seu saldo estimado e nível de risco.",
            "notice": "Aviso:",
            "notice_text": "A INNA atua como educadora financeira digital. Ela orienta de forma educativa, não indica compra ou venda de ativos, não promete rentabilidade e não substitui profissionais certificados.",
            "months": "mês(es)",
            "days": "dias",
        },
        "en_us": {
            "intro": f"Hello, {nome}. INNA has prepared a safe action plan based on your financial diagnosis.",
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
        },
        "en_gb": {
            "intro": f"Hello, {nome}. INNA has prepared a safe action plan based on your financial diagnosis.",
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
        },
        "es": {
            "intro": f"Hola, {nome}. INNA preparó un plan de acción seguro con base en tu diagnóstico financiero.",
            "summary": "Resumen de la situación:",
            "balance": "Saldo mensual estimado",
            "score": "Puntuación financiera",
            "risk": "Nivel de riesgo",
            "commitment": "Compromiso de los ingresos",
            "reserve": "Reserva actual estimada",
            "plan": "Plan de acción de 30 días:",
            "w1": "Semana 1 — Entender hacia dónde va el dinero",
            "w1a": "Anota todos los gastos fijos y variables.",
            "w1b": "Separa los gastos en esenciales, importantes y opcionales.",
            "w1c": "Identifica al menos 3 gastos que se puedan reducir sin afectar tu rutina.",
            "w2": "Semana 2 — Reducir desperdicios",
            "w2a": "Define un límite semanal para gastos variables.",
            "w2b": "Evita crear nuevas deudas durante este período.",
            "w2c": "Envía cualquier excedente a tu reserva de emergencia.",
            "w3": "Semana 3 — Fortalecer la reserva",
            "w3a": "Como tu reserva aún cubre pocos días, prioriza aumentar ese valor.",
            "w3b": "Aunque el valor ahorrado sea pequeño, mantén la constancia.",
            "w3c": "La primera meta es llegar a por lo menos 1 mes de gastos cubiertos.",
            "w4": "Semana 4 — Revisar y ajustar",
            "w4a": "Compara tu situación actual con el inicio del plan.",
            "w4b": "Verifica si el saldo mensual mejoró.",
            "w4c": "Ajusta tus metas para el próximo mes.",
            "next": "Próxima orientación:",
            "next_text": "Prioriza aumentar tu reserva y reducir gastos variables antes de asumir nuevos compromisos financieros.",
            "notice": "Aviso:",
            "notice_text": "INNA actúa como educadora financiera digital. No recomienda comprar o vender activos, no promete rentabilidad y no sustituye a profesionales certificados.",
            "months": "mes(es)",
            "days": "días",
        },
        "fr": {
            "intro": f"Bonjour, {nome}. INNA a préparé un plan d’action sécurisé à partir de votre diagnostic financier.",
            "summary": "Résumé de la situation :",
            "balance": "Solde mensuel estimé",
            "score": "Score financier",
            "risk": "Niveau de risque",
            "commitment": "Part du revenu engagée",
            "reserve": "Épargne actuelle estimée",
            "plan": "Plan d’action sur 30 jours :",
            "w1": "Semaine 1 — Comprendre où va votre argent",
            "w1a": "Notez toutes les dépenses fixes et variables.",
            "w1b": "Séparez les dépenses en essentielles, importantes et optionnelles.",
            "w1c": "Identifiez au moins 3 dépenses pouvant être réduites sans nuire à votre routine.",
            "w2": "Semaine 2 — Réduire les gaspillages",
            "w2a": "Définissez une limite hebdomadaire pour les dépenses variables.",
            "w2b": "Évitez de créer de nouvelles dettes pendant cette période.",
            "w2c": "Dirigez tout excédent vers votre réserve d’urgence.",
            "w3": "Semaine 3 — Renforcer l’épargne",
            "w3a": "Comme votre réserve couvre encore peu de jours, donnez la priorité à son augmentation.",
            "w3b": "Même si le montant épargné est faible, gardez de la régularité.",
            "w3c": "Le premier objectif est d’atteindre au moins 1 mois de dépenses couvertes.",
            "w4": "Semaine 4 — Réviser et ajuster",
            "w4a": "Comparez votre situation actuelle avec le début du plan.",
            "w4b": "Vérifiez si votre solde mensuel s’est amélioré.",
            "w4c": "Ajustez vos objectifs pour le mois suivant.",
            "next": "Prochaine étape recommandée :",
            "next_text": "Priorisez l’augmentation de votre réserve et la réduction des dépenses variables avant de prendre de nouveaux engagements financiers.",
            "notice": "Avis :",
            "notice_text": "INNA agit comme éducatrice financière numérique. Elle ne recommande pas l’achat ou la vente d’actifs, ne promet pas de rendement et ne remplace pas les professionnels certifiés.",
            "months": "mois",
            "days": "jours",
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
            "w2a": "Lege ein Wochenlimit für variable Ausgaben fest.",
            "w2b": "Vermeide in diesem Zeitraum neue Schulden.",
            "w2c": "Leite jeden Überschuss in deine Rücklage.",
            "w3": "Woche 3 — Rücklage stärken",
            "w3a": "Da deine Rücklage nur wenige Tage abdeckt, priorisiere ihren Aufbau.",
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
        },
        "it": {
            "intro": f"Ciao, {nome}. INNA ha preparato un piano d’azione sicuro sulla base della tua diagnosi finanziaria.",
            "summary": "Riepilogo della situazione:",
            "balance": "Saldo mensile stimato",
            "score": "Punteggio finanziario",
            "risk": "Livello di rischio",
            "commitment": "Impegno del reddito",
            "reserve": "Riserva attuale stimata",
            "plan": "Piano d’azione di 30 giorni:",
            "w1": "Settimana 1 — Capire dove va il denaro",
            "w1a": "Annota tutte le spese fisse e variabili.",
            "w1b": "Separa le spese in essenziali, importanti e opzionali.",
            "w1c": "Individua almeno 3 spese che possono essere ridotte senza danneggiare la tua routine.",
            "w2": "Settimana 2 — Ridurre gli sprechi",
            "w2a": "Stabilisci un limite settimanale per le spese variabili.",
            "w2b": "Evita nuovi debiti durante questo periodo.",
            "w2c": "Destina qualsiasi avanzo alla tua riserva di emergenza.",
            "w3": "Settimana 3 — Rafforzare la riserva",
            "w3a": "Poiché la tua riserva copre ancora pochi giorni, dai priorità al suo aumento.",
            "w3b": "Anche se l’importo risparmiato è piccolo, mantieni costanza.",
            "w3c": "Il primo obiettivo è arrivare ad almeno 1 mese di spese coperte.",
            "w4": "Settimana 4 — Rivedere e adattare",
            "w4a": "Confronta la tua situazione attuale con l’inizio del piano.",
            "w4b": "Verifica se il saldo mensile è migliorato.",
            "w4c": "Adatta i tuoi obiettivi per il mese successivo.",
            "next": "Prossimo passo consigliato:",
            "next_text": "Dai priorità all’aumento della riserva e alla riduzione delle spese variabili prima di assumere nuovi impegni finanziari.",
            "notice": "Avviso:",
            "notice_text": "INNA agisce come educatrice finanziaria digitale. Non raccomanda l’acquisto o la vendita di asset, non promette rendimenti e non sostituisce professionisti certificati.",
            "months": "mese/i",
            "days": "giorni",
        },
        "ro": {
            "intro": f"Bună, {nome}. INNA a pregătit un plan de acțiune sigur pe baza diagnosticului tău financiar.",
            "summary": "Rezumatul situației:",
            "balance": "Sold lunar estimat",
            "score": "Scor financiar",
            "risk": "Nivel de risc",
            "commitment": "Angajarea venitului",
            "reserve": "Rezervă actuală estimată",
            "plan": "Plan de acțiune pe 30 de zile:",
            "w1": "Săptămâna 1 — Înțelege unde se duc banii",
            "w1a": "Notează toate cheltuielile fixe și variabile.",
            "w1b": "Separă cheltuielile în esențiale, importante și opționale.",
            "w1c": "Identifică cel puțin 3 cheltuieli care pot fi reduse fără să îți afecteze rutina.",
            "w2": "Săptămâna 2 — Redu risipa",
            "w2a": "Stabilește o limită săptămânală pentru cheltuielile variabile.",
            "w2b": "Evită datoriile noi în această perioadă.",
            "w2c": "Direcționează orice surplus către rezerva de urgență.",
            "w3": "Săptămâna 3 — Consolidarea rezervei",
            "w3a": "Deoarece rezerva acoperă încă puține zile, prioritizează creșterea acesteia.",
            "w3b": "Chiar dacă suma economisită este mică, păstrează consecvența.",
            "w3c": "Primul obiectiv este să ajungi la cel puțin 1 lună de cheltuieli acoperite.",
            "w4": "Săptămâna 4 — Revizuire și ajustare",
            "w4a": "Compară situația actuală cu începutul planului.",
            "w4b": "Verifică dacă soldul lunar s-a îmbunătățit.",
            "w4c": "Ajustează obiectivele pentru luna următoare.",
            "next": "Următorul pas recomandat:",
            "next_text": "Prioritizează creșterea rezervei și reducerea cheltuielilor variabile înainte de a-ți asuma noi angajamente financiare.",
            "notice": "Notificare:",
            "notice_text": "INNA acționează ca educator financiar digital. Nu recomandă cumpărarea sau vânzarea de active, nu promite randamente și nu înlocuiește profesioniștii certificați.",
            "months": "lună/luni",
            "days": "zile",
        },
        "uk": {
            "intro": f"Вітаю, {nome}. INNA підготувала безпечний план дій на основі вашої фінансової діагностики.",
            "summary": "Короткий підсумок ситуації:",
            "balance": "Орієнтовний щомісячний баланс",
            "score": "Фінансовий бал",
            "risk": "Рівень ризику",
            "commitment": "Навантаження на дохід",
            "reserve": "Орієнтовний поточний резерв",
            "plan": "План дій на 30 днів:",
            "w1": "Тиждень 1 — Зрозуміти, куди йдуть гроші",
            "w1a": "Запишіть усі постійні та змінні витрати.",
            "w1b": "Розділіть витрати на необхідні, важливі та необов’язкові.",
            "w1c": "Визначте щонайменше 3 витрати, які можна зменшити без шкоди для вашої рутини.",
            "w2": "Тиждень 2 — Зменшити зайві витрати",
            "w2a": "Встановіть тижневий ліміт для змінних витрат.",
            "w2b": "Уникайте нових боргів у цей період.",
            "w2c": "Спрямовуйте будь-який залишок до резерву на непередбачені витрати.",
            "w3": "Тиждень 3 — Зміцнити резерв",
            "w3a": "Оскільки ваш резерв покриває лише кілька днів, пріоритетом є його збільшення.",
            "w3b": "Навіть якщо сума невелика, зберігайте регулярність.",
            "w3c": "Перша мета — накопичити резерв щонайменше на 1 місяць витрат.",
            "w4": "Тиждень 4 — Перевірити та скоригувати",
            "w4a": "Порівняйте поточну ситуацію з початком плану.",
            "w4b": "Перевірте, чи покращився щомісячний баланс.",
            "w4c": "Скоригуйте цілі на наступний місяць.",
            "next": "Рекомендований наступний крок:",
            "next_text": "Спочатку збільшуйте резерв і зменшуйте змінні витрати, перш ніж брати нові фінансові зобов’язання.",
            "notice": "Важливо:",
            "notice_text": "INNA є цифровим фінансовим освітнім помічником. Вона не рекомендує купівлю чи продаж активів, не обіцяє прибутковість і не замінює сертифікованих фахівців.",
            "months": "міс.",
            "days": "днів",
        },
        "ru": {
            "intro": f"Здравствуйте, {nome}. INNA подготовила безопасный план действий на основе вашей финансовой диагностики.",
            "summary": "Краткое резюме ситуации:",
            "balance": "Оценочный ежемесячный баланс",
            "score": "Финансовый балл",
            "risk": "Уровень риска",
            "commitment": "Нагрузка на доход",
            "reserve": "Оценочный текущий резерв",
            "plan": "План действий на 30 дней:",
            "w1": "Неделя 1 — Понять, куда уходят деньги",
            "w1a": "Запишите все фиксированные и переменные расходы.",
            "w1b": "Разделите расходы на необходимые, важные и необязательные.",
            "w1c": "Найдите как минимум 3 расхода, которые можно сократить без вреда для вашей рутины.",
            "w2": "Неделя 2 — Сократить лишние расходы",
            "w2a": "Установите недельный лимит для переменных расходов.",
            "w2b": "Избегайте новых долгов в этот период.",
            "w2c": "Направляйте любой остаток денег в резерв на непредвиденные расходы.",
            "w3": "Неделя 3 — Укрепить резерв",
            "w3a": "Поскольку ваш резерв покрывает только несколько дней, приоритет — увеличить эту сумму.",
            "w3b": "Даже если сумма небольшая, сохраняйте регулярность.",
            "w3c": "Первая цель — накопить резерв минимум на 1 месяц расходов.",
            "w4": "Неделя 4 — Проверить и скорректировать",
            "w4a": "Сравните текущую ситуацию с началом плана.",
            "w4b": "Проверьте, улучшился ли ежемесячный баланс.",
            "w4c": "Скорректируйте цели на следующий месяц.",
            "next": "Рекомендуемый следующий шаг:",
            "next_text": "Сначала увеличьте резерв и сократите переменные расходы, прежде чем брать новые финансовые обязательства.",
            "notice": "Важно:",
            "notice_text": "INNA является цифровым финансовым помощником. Она не рекомендует покупку или продажу активов, не обещает доходность и не заменяет сертифицированных специалистов.",
            "months": "мес.",
            "days": "дней",
        },
        "ar": {
            "intro": f"مرحبًا، {nome}. أعدّت INNA خطة عمل آمنة بناءً على تشخيصك المالي.",
            "summary": "ملخص الوضع:",
            "balance": "الرصيد الشهري التقديري",
            "score": "الدرجة المالية",
            "risk": "مستوى المخاطر",
            "commitment": "نسبة الالتزام من الدخل",
            "reserve": "الاحتياطي الحالي التقديري",
            "plan": "خطة عمل لمدة 30 يومًا:",
            "w1": "الأسبوع 1 — فهم أين تذهب الأموال",
            "w1a": "اكتب جميع المصروفات الثابتة والمتغيرة.",
            "w1b": "قسّم المصروفات إلى أساسية ومهمة واختيارية.",
            "w1c": "حدد 3 مصروفات على الأقل يمكن تقليلها دون الإضرار بروتينك.",
            "w2": "الأسبوع 2 — تقليل الهدر",
            "w2a": "حدد حدًا أسبوعيًا للمصروفات المتغيرة.",
            "w2b": "تجنب إنشاء ديون جديدة خلال هذه الفترة.",
            "w2c": "وجّه أي فائض إلى احتياطي الطوارئ.",
            "w3": "الأسبوع 3 — تعزيز الاحتياطي",
            "w3a": "بما أن احتياطيك يغطي بضعة أيام فقط، أعطِ الأولوية لزيادته.",
            "w3b": "حتى لو كان المبلغ صغيرًا، حافظ على الاستمرارية.",
            "w3c": "الهدف الأول هو الوصول إلى احتياطي يغطي شهرًا واحدًا على الأقل من المصروفات.",
            "w4": "الأسبوع 4 — المراجعة والتعديل",
            "w4a": "قارن وضعك الحالي ببداية الخطة.",
            "w4b": "تحقق مما إذا كان الرصيد الشهري قد تحسن.",
            "w4c": "عدّل أهدافك للشهر القادم.",
            "next": "الخطوة التالية الموصى بها:",
            "next_text": "أعطِ الأولوية لزيادة الاحتياطي وتقليل المصروفات المتغيرة قبل الالتزام بالتزامات مالية جديدة.",
            "notice": "تنبيه:",
            "notice_text": "تعمل INNA كمثقفة مالية رقمية. لا توصي بشراء أو بيع الأصول، ولا تعد بعوائد، ولا تحل محل المختصين المعتمدين.",
            "months": "شهر",
            "days": "أيام",
        },
    }

    t = texts.get(lang, texts["pt"])

    return f"""
{t["intro"]}

{t["summary"]}
- {t["balance"]}: {money(saldo)}
- {t["score"]}: {score}/100
- {t["risk"]}: {risco_txt}
- {t["commitment"]}: {comprometimento:.1f}%
- {t["reserve"]}: {dias_reserva} {t["days"]} ({meses_reserva:.2f} {t["months"]})

{t["plan"]}

{t["w1"]}
- {t["w1a"]}
- {t["w1b"]}

{t["w2"]}
- {t["w2a"]}
- {t["w2b"]}

{t["w3"]}
- {t["w3a"]}
- {t["w3b"]}

{t["w4"]}
- {t["w4a"]}
- {t["w4b"]}

{t["next"]} {t["next_text"]}

{t["notice"]} {t["notice_text"]}
""".strip()

def generate_ai_plan(payload: dict, diagnosis: dict) -> str:
    _update_last_gemini_usage(fallback=True)
    if INNA_MOCK_MODE:
        return generate_fallback_plan(payload, diagnosis)

    if not GEMINI_API_KEY:
        return generate_fallback_plan(payload, diagnosis)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = build_plan_prompt(payload, diagnosis)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        _update_last_gemini_usage(response)

        text = getattr(response, "text", None)

        if not text:
            return generate_fallback_plan(payload, diagnosis)

        return text

    except Exception:
        return generate_fallback_plan(payload, diagnosis)
