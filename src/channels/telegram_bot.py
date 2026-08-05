import asyncio
import os

from dotenv import load_dotenv
from src.api_client import (
    gerar_diagnostico_telegram_api,
)
from src.channels.telegram_context import (
    TelegramUpdateContextError,
    construir_contexto_confiavel_telegram,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
API_BASE_URL = os.getenv("API_BASE_URL", "https://inna-api.onrender.com")

IDIOMA, NOME, RENDA, GASTOS_FIXOS, GASTOS_VARIAVEIS, DIVIDAS, RESERVA, OBJETIVO = range(
    8
)

LANGUAGE_OPTIONS = {
    "🇧🇷 Português": "pt",
    "🇺🇸 English": "en",
    "🇪🇸 Español": "es",
    "🇷🇺 Русский": "ru",
    "🇫🇷 Français": "fr",
    "🇸🇦 العربية": "ar",
}

LANGUAGE_NAMES = {
    "pt": "português brasileiro",
    "en": "inglês",
    "es": "espanhol",
    "ru": "russo",
    "fr": "francês",
    "ar": "árabe",
}

TEXTS = {
    "pt": {
        "choose_language": "🌍 Escolha o idioma para começar:",
        "start": "💰 Oi! Eu sou a INNA, sua educadora financeira com IA.\n\nVou te ajudar com perguntas simples, uma por vez.\nNão precisa colocar R$, só o número.\n\nPrimeiro, como posso te chamar?",
        "invalid_name": "Me diga um nome simples para eu te chamar.",
        "ask_income": "Prazer, {nome}! 😊\n\nQuanto você ganha por mês?\nExemplo: 3000",
        "invalid_income": "Não consegui entender. Me envie só o número da sua renda mensal.\nExemplo: 3000",
        "ask_fixed": "Agora me diga quanto você gasta por mês com contas fixas.\n\nExemplos: aluguel, luz, água, internet, telefone.\nSe não souber exato, mande uma média.\n\nExemplo: 1400",
        "invalid_fixed": "Me envie só o número dos gastos fixos.\nExemplo: 1400",
        "ask_variable": "Quanto você gasta por mês com gastos variáveis?\n\nExemplos: mercado, transporte, comida fora, lazer e compras do dia a dia.\nExemplo: 700",
        "invalid_variable": "Me envie só o número dos gastos variáveis.\nExemplo: 700",
        "ask_debts": "Você paga alguma dívida ou parcela por mês?\n\nSe não tiver, responda 0.\nExemplo: 300",
        "invalid_debts": "Me envie só o número das dívidas mensais.\nSe não tiver, responda 0.",
        "ask_savings": "Você tem algum dinheiro guardado hoje?\n\nSe não tiver, responda 0.\nExemplo: 500",
        "invalid_savings": "Me envie só o número da reserva atual.\nSe não tiver, responda 0.",
        "ask_goal": "Qual é seu principal objetivo agora?",
        "goal_options": [
            ["Organizar as contas"],
            ["Sair das dívidas"],
            ["Guardar dinheiro"],
            ["Fazer sobrar no fim do mês"],
        ],
        "adjust_debt": "Entendi. Você informou que não tem dívidas mensais agora. ✅\n\nEntão vou ajustar o foco: em vez de sair das dívidas, vamos trabalhar para organizar suas contas, evitar novas dívidas e fortalecer sua reserva.",
        "analyzing": "Pronto. Estou analisando seus dados financeiros... ⏳",
        "api_error": "A API da INNA não respondeu agora. Tente novamente em alguns instantes.",
        "cancel": "Tudo bem, atendimento cancelado. Para começar de novo, envie /start.",
        "help": "Para começar, envie /start.\n\nA INNA vai perguntar uma coisa por vez.",
        "diagnosis_title": "💰 Diagnóstico INNA",
        "name": "Nome",
        "balance": "Saldo estimado",
        "score": "Score financeiro",
        "risk": "Nível de risco",
        "summary": "Resumo",
        "quick_plan": "Plano rápido",
        "week1": "Semana 1 — Mapear gastos e entender para onde o dinheiro está indo.",
        "week2": "Semana 2 — Cortar desperdícios e revisar gastos variáveis.",
        "week3": "Semana 3 — Separar uma parte possível para reserva.",
        "week4": "Semana 4 — Revisar o progresso e manter uma rotina simples.",
        "saved": "✅ Diagnóstico salvo na base online da INNA.",
        "details": "📊 Para ver o plano completo, use o app web, dashboard ou relatório PDF.",
    },
    "en": {
        "choose_language": "🌍 Choose your language:",
        "start": "💰 Hi! I'm INNA, your AI financial educator.\n\nI'll help you with simple questions, one at a time.\nNo need to type currency symbols, just numbers.\n\nFirst, what should I call you?",
        "invalid_name": "Please send a simple name.",
        "ask_income": "Nice to meet you, {nome}! 😊\n\nHow much do you earn per month?\nExample: 3000",
        "invalid_income": "I couldn't understand. Please send only your monthly income number.\nExample: 3000",
        "ask_fixed": "How much do you spend per month on fixed bills?\n\nExamples: rent, electricity, water, internet, phone.\nIf you don't know exactly, send an estimate.\n\nExample: 1400",
        "invalid_fixed": "Please send only the number for fixed expenses.\nExample: 1400",
        "ask_variable": "How much do you spend per month on variable expenses?\n\nExamples: groceries, transport, food outside, leisure and daily purchases.\nExample: 700",
        "invalid_variable": "Please send only the number for variable expenses.\nExample: 700",
        "ask_debts": "Do you pay any debt or monthly installment?\n\nIf not, reply 0.\nExample: 300",
        "invalid_debts": "Please send only the number for monthly debts.\nIf you don't have any, reply 0.",
        "ask_savings": "Do you have any money saved today?\n\nIf not, reply 0.\nExample: 500",
        "invalid_savings": "Please send only the number for your current savings.\nIf you don't have any, reply 0.",
        "ask_goal": "What is your main goal right now?",
        "goal_options": [
            ["Organize my bills"],
            ["Get out of debt"],
            ["Save money"],
            ["Have money left at the end of the month"],
        ],
        "adjust_debt": "Got it. You said you don't have monthly debts right now. ✅\n\nSo I'll adjust the focus: instead of getting out of debt, we'll work on organizing your bills, avoiding new debt and strengthening your savings.",
        "analyzing": "Done. I'm analyzing your financial data... ⏳",
        "api_error": "INNA's API did not respond right now. Please try again soon.",
        "cancel": "Okay, session canceled. To start again, send /start.",
        "help": "To start, send /start.\n\nINNA will ask one question at a time.",
        "diagnosis_title": "💰 INNA diagnosis",
        "name": "Name",
        "balance": "Estimated balance",
        "score": "Financial score",
        "risk": "Risk level",
        "summary": "Summary",
        "quick_plan": "Quick plan",
        "week1": "Week 1 — Map expenses and understand where the money is going.",
        "week2": "Week 2 — Cut waste and review variable expenses.",
        "week3": "Week 3 — Set aside a possible amount for savings.",
        "week4": "Week 4 — Review progress and keep a simple routine.",
        "saved": "✅ Diagnosis saved in INNA's online database.",
        "details": "📊 For the full plan, use the web app, dashboard or PDF report.",
    },
    "es": {
        "choose_language": "🌍 Elige tu idioma:",
        "start": "💰 ¡Hola! Soy INNA, tu educadora financiera con IA.\n\nTe ayudaré con preguntas simples, una por vez.\nNo necesitas escribir símbolos de moneda, solo números.\n\nPrimero, ¿cómo puedo llamarte?",
        "invalid_name": "Dime un nombre simple para llamarte.",
        "ask_income": "¡Mucho gusto, {nome}! 😊\n\n¿Cuánto ganas por mes?\nEjemplo: 3000",
        "invalid_income": "No pude entender. Envíame solo el número de tus ingresos mensuales.\nEjemplo: 3000",
        "ask_fixed": "¿Cuánto gastas por mes en cuentas fijas?\n\nEjemplos: alquiler, luz, agua, internet, teléfono.\nSi no sabes exacto, envía un promedio.\n\nEjemplo: 1400",
        "invalid_fixed": "Envíame solo el número de los gastos fijos.\nEjemplo: 1400",
        "ask_variable": "¿Cuánto gastas por mes en gastos variables?\n\nEjemplos: mercado, transporte, comida fuera, ocio y compras del día a día.\nEjemplo: 700",
        "invalid_variable": "Envíame solo el número de los gastos variables.\nEjemplo: 700",
        "ask_debts": "¿Pagas alguna deuda o cuota por mes?\n\nSi no tienes, responde 0.\nEjemplo: 300",
        "invalid_debts": "Envíame solo el número de las deudas mensuales.\nSi no tienes, responde 0.",
        "ask_savings": "¿Tienes dinero guardado hoy?\n\nSi no tienes, responde 0.\nEjemplo: 500",
        "invalid_savings": "Envíame solo el número de tu reserva actual.\nSi no tienes, responde 0.",
        "ask_goal": "¿Cuál es tu principal objetivo ahora?",
        "goal_options": [
            ["Organizar las cuentas"],
            ["Salir de deudas"],
            ["Ahorrar dinero"],
            ["Que sobre dinero al fin del mes"],
        ],
        "adjust_debt": "Entiendo. Informaste que no tienes deudas mensuales ahora. ✅\n\nEntonces ajustaré el foco: en vez de salir de deudas, vamos a organizar tus cuentas, evitar nuevas deudas y fortalecer tu reserva.",
        "analyzing": "Listo. Estoy analizando tus datos financieros... ⏳",
        "api_error": "La API de INNA no respondió ahora. Inténtalo nuevamente en unos instantes.",
        "cancel": "Está bien, atención cancelada. Para empezar de nuevo, envía /start.",
        "help": "Para empezar, envía /start.\n\nINNA hará una pregunta por vez.",
        "diagnosis_title": "💰 Diagnóstico INNA",
        "name": "Nombre",
        "balance": "Saldo estimado",
        "score": "Score financiero",
        "risk": "Nivel de riesgo",
        "summary": "Resumen",
        "quick_plan": "Plan rápido",
        "week1": "Semana 1 — Mapear gastos y entender a dónde va el dinero.",
        "week2": "Semana 2 — Reducir desperdicios y revisar gastos variables.",
        "week3": "Semana 3 — Separar una parte posible para la reserva.",
        "week4": "Semana 4 — Revisar el progreso y mantener una rutina simple.",
        "saved": "✅ Diagnóstico guardado en la base online de INNA.",
        "details": "📊 Para ver el plan completo, usa la app web, el dashboard o el PDF.",
    },
}

# Fallback: mantém russo, francês e árabe com perguntas simples em inglês se quiser acelerar.
# Depois podemos traduzir 100% desses três idiomas.
for code in ["ru", "fr", "ar"]:
    TEXTS[code] = TEXTS["en"].copy()


def t(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    lang = context.user_data.get("lang", "pt")
    return TEXTS.get(lang, TEXTS["pt"]).get(key, TEXTS["pt"][key])


def _to_float(text: str) -> float:
    text = text.strip()
    text = text.replace("R$", "").replace("r$", "").strip()

    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "")

    return float(text)


def _format_money(value) -> str:
    try:
        return f"R$ {float(value):.2f}".replace(".", ",")
    except (TypeError, ValueError):
        return "R$ 0,00"


def gerar_diagnostico(
    payload: dict,
    *,
    usuario_id_confiavel: str,
    request_id: str,
) -> dict:
    return gerar_diagnostico_telegram_api(
        payload,
        usuario_id_confiavel=(usuario_id_confiavel),
        request_id=request_id,
    )


def formatar_resposta(resultado: dict, context: ContextTypes.DEFAULT_TYPE) -> str:
    saldo = _format_money(resultado.get("saldo_estimado"))
    score = resultado.get("score_financeiro")
    risco = resultado.get("nivel_risco")
    diagnostico = resultado.get("diagnostico", "")

    resumo_curto = diagnostico
    if len(resumo_curto) > 350:
        resumo_curto = resumo_curto[:350].rstrip() + "..."

    return f"""
{t(context, "diagnosis_title")}

👤 {t(context, "name")}: {resultado.get("nome")}
💵 {t(context, "balance")}: {saldo}
📊 {t(context, "score")}: {score}/100
⚠️ {t(context, "risk")}: {risco}

🧾 {t(context, "summary")}:
{resumo_curto}

📅 {t(context, "quick_plan")}:
{t(context, "week1")}
{t(context, "week2")}
{t(context, "week3")}
{t(context, "week4")}

{t(context, "saved")}
{t(context, "details")}
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    keyboard = [
        ["🇧🇷 Português", "🇺🇸 English"],
        ["🇪🇸 Español", "🇷🇺 Русский"],
        ["🇫🇷 Français", "🇸🇦 العربية"],
    ]

    await update.message.reply_text(
        "🌍 Escolha o idioma / Choose your language:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return IDIOMA


async def receber_idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    escolha = update.message.text.strip()
    lang = LANGUAGE_OPTIONS.get(escolha, "pt")
    context.user_data["lang"] = lang

    await update.message.reply_text(
        t(context, "start"),
        reply_markup=ReplyKeyboardRemove(),
    )
    return NOME


async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text.strip()

    if len(nome) < 2:
        await update.message.reply_text(t(context, "invalid_name"))
        return NOME

    context.user_data["nome"] = nome

    await update.message.reply_text(t(context, "ask_income").format(nome=nome))
    return RENDA


async def receber_renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        renda = _to_float(update.message.text)
        if renda <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(context, "invalid_income"))
        return RENDA

    context.user_data["renda_mensal"] = renda
    await update.message.reply_text(t(context, "ask_fixed"))
    return GASTOS_FIXOS


async def receber_gastos_fixos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        gastos_fixos = _to_float(update.message.text)
        if gastos_fixos < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(context, "invalid_fixed"))
        return GASTOS_FIXOS

    context.user_data["gastos_fixos"] = gastos_fixos
    await update.message.reply_text(t(context, "ask_variable"))
    return GASTOS_VARIAVEIS


async def receber_gastos_variaveis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        gastos_variaveis = _to_float(update.message.text)
        if gastos_variaveis < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(context, "invalid_variable"))
        return GASTOS_VARIAVEIS

    context.user_data["gastos_variaveis"] = gastos_variaveis
    await update.message.reply_text(t(context, "ask_debts"))
    return DIVIDAS


async def receber_dividas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dividas = _to_float(update.message.text)
        if dividas < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(context, "invalid_debts"))
        return DIVIDAS

    context.user_data["dividas_mensais"] = dividas
    await update.message.reply_text(t(context, "ask_savings"))
    return RESERVA


async def receber_reserva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reserva = _to_float(update.message.text)
        if reserva < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(context, "invalid_savings"))
        return RESERVA

    context.user_data["reserva_atual"] = reserva

    await update.message.reply_text(
        t(context, "ask_goal"),
        reply_markup=ReplyKeyboardMarkup(
            TEXTS[context.user_data.get("lang", "pt")]["goal_options"],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return OBJETIVO


async def receber_objetivo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    effective_message = update.effective_message

    effective_chat = update.effective_chat

    if effective_message is None or effective_chat is None:
        context.user_data.clear()

        return ConversationHandler.END

    objetivo_original = (effective_message.text or "").strip()

    objetivo = objetivo_original

    dividas_mensais = float(
        context.user_data.get(
            "dividas_mensais",
            0,
        )
    )

    lang = context.user_data.get(
        "lang",
        "pt",
    )

    objetivo_fala_sobre_divida = any(
        termo in objetivo_original.lower()
        for termo in [
            "dívida",
            "divida",
            "dívidas",
            "dividas",
            "debt",
            "debts",
            "deuda",
            "deudas",
        ]
    )

    if dividas_mensais <= 0 and objetivo_fala_sobre_divida:
        objetivo = (
            "Organizar as contas, evitar novas "
            "dívidas e fortalecer a reserva "
            "financeira"
        )

        await effective_message.reply_text(
            t(
                context,
                "adjust_debt",
            )
        )

    objetivo = (
        f"{objetivo}. Responda em {LANGUAGE_NAMES.get(lang, 'português brasileiro')}."
    )

    payload = {
        "nome": context.user_data["nome"],
        "renda_mensal": (context.user_data["renda_mensal"]),
        "gastos_fixos": (context.user_data["gastos_fixos"]),
        "gastos_variaveis": (context.user_data["gastos_variaveis"]),
        "dividas_mensais": (context.user_data["dividas_mensais"]),
        "reserva_atual": (context.user_data["reserva_atual"]),
        "objetivo": objetivo,
        "idioma": lang,
    }

    await effective_message.reply_text(
        t(
            context,
            "analyzing",
        ),
        reply_markup=ReplyKeyboardRemove(),
    )

    try:
        trusted_update = construir_contexto_confiavel_telegram(
            update_id=update.update_id,
            chat_id=effective_chat.id,
            message_id=(effective_message.message_id),
        )

        resultado = await asyncio.to_thread(
            gerar_diagnostico,
            payload,
            usuario_id_confiavel=(trusted_update.usuario_id),
            request_id=(trusted_update.request_id),
        )

        resposta = formatar_resposta(
            resultado,
            context,
        )

        await effective_message.reply_text(resposta)

    except TelegramUpdateContextError:
        await effective_message.reply_text(
            t(
                context,
                "api_error",
            )
        )

    except Exception:
        await effective_message.reply_text(
            t(
                context,
                "api_error",
            )
        )

    finally:
        context.user_data.clear()

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        t(context, "cancel"), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t(context, "help"))


def main():
    if not TELEGRAM_ENABLED:
        print("Telegram desativado. Configure TELEGRAM_ENABLED=true no .env.")
        return

    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN não encontrado. Configure o token no .env."
        )

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conversa = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            IDIOMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_idioma)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            RENDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_renda)],
            GASTOS_FIXOS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_gastos_fixos)
            ],
            GASTOS_VARIAVEIS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, receber_gastos_variaveis
                )
            ],
            DIVIDAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_dividas)],
            RESERVA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_reserva)],
            OBJETIVO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_objetivo)
            ],
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar),
            CommandHandler("cancel", cancelar),
            CommandHandler("help", ajuda),
        ],
    )

    app.add_handler(conversa)
    app.add_handler(CommandHandler("help", ajuda))

    print("Bot Telegram da INNA iniciado com seleção de idioma.")
    print(f"API configurada: {API_BASE_URL}")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
