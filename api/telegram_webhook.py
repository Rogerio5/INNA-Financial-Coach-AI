import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Request

from api.schemas import FinancialInput
from src.financial_engine import build_financial_diagnosis
from src.gemini_client import generate_ai_plan
from src.repository import save_diagnostico_db

load_dotenv()

router = APIRouter(prefix="/telegram", tags=["telegram"])

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USER_SESSIONS = {}
PROCESSED_UPDATES = set()

LANGUAGE_OPTIONS = {
    "🇧🇷 Português": "pt",
    "🇺🇸 English": "en",
    "🇪🇸 Español": "es",
    "🇷🇺 Русский": "ru",
    "🇫🇷 Français": "fr",
    "🇸🇦 العربية": "ar",
}


def send_telegram_message(chat_id: int, text: str, reply_markup: dict | None = None):
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN não configurado.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(url, json=payload, timeout=30)


def keyboard(options: list[list[str]]) -> dict:
    return {
        "keyboard": options,
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def remove_keyboard() -> dict:
    return {"remove_keyboard": True}


def to_float(text: str) -> float:
    text = text.strip()
    text = text.replace("R$", "").replace("r$", "").strip()

    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "")

    return float(text)


def format_money(value) -> str:
    try:
        number = float(value)
        formatted = f"{number:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except Exception:
        return "R$ 0,00"


def format_currency_mentions(text: str) -> str:
    """
    Converte valores como R$ 21700.00 para R$ 21.700,00 dentro do texto.
    """
    def replace_match(match):
        raw_value = match.group(1)
        try:
            number = float(raw_value.replace(".", "").replace(",", ".") if "," in raw_value else raw_value)
            formatted = f"{number:,.2f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {formatted}"
        except Exception:
            return match.group(0)

    return re.sub(r"R\$\s*([0-9]+(?:\.[0-9]{2})?)", replace_match, text)


def resposta_curta(resultado: dict) -> str:
    diagnostico = resultado.get("diagnostico", "")
    diagnostico = format_currency_mentions(diagnostico)

    if len(diagnostico) > 350:
        diagnostico = diagnostico[:350].rstrip() + "..."

    return f"""
💰 Diagnóstico INNA

👤 Nome: {resultado.get("nome")}
💵 Saldo estimado: {format_money(resultado.get("saldo_estimado"))}
📊 Score financeiro: {resultado.get("score_financeiro")}/100
⚠️ Nível de risco: {resultado.get("nivel_risco")}

🧾 Resumo:
{diagnostico}

📅 Plano rápido:
Semana 1 — Mapear gastos e entender para onde o dinheiro está indo.
Semana 2 — Cortar desperdícios e revisar gastos variáveis.
Semana 3 — Separar uma parte possível para reserva.
Semana 4 — Revisar o progresso e manter uma rotina simples.

✅ Diagnóstico salvo na base online da INNA.
📊 Para ver o plano completo, use o app web, dashboard ou relatório PDF.
"""


def gerar_diagnostico_pelo_payload(payload: dict) -> dict:
    financial_input = FinancialInput(**payload)
    payload_dict = financial_input.model_dump()

    diagnosis = build_financial_diagnosis(payload_dict)
    ai_plan = generate_ai_plan(payload_dict, diagnosis)

    response = {
        **diagnosis,
        "nome": payload_dict["nome"],
        "objetivo": payload_dict["objetivo"],
        "plano_30_dias": ai_plan,
    }

    diagnostico_id = save_diagnostico_db(payload_dict, response)
    response["id"] = diagnostico_id

    return response


def process_telegram_update(update: dict):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        return

    text = text.strip()

    if text in ["/start", "/idioma", "/language"]:
        USER_SESSIONS[chat_id] = {"step": "idioma"}
        send_telegram_message(
            chat_id,
            "🌍 Escolha o idioma / Choose your language:",
            keyboard([
                ["🇧🇷 Português", "🇺🇸 English"],
                ["🇪🇸 Español", "🇷🇺 Русский"],
                ["🇫🇷 Français", "🇸🇦 العربية"],
            ]),
        )
        return

    if text in ["/cancelar", "/cancel"]:
        USER_SESSIONS.pop(chat_id, None)
        send_telegram_message(
            chat_id,
            "Atendimento cancelado. Para começar de novo, envie /start.",
            remove_keyboard(),
        )
        return

    session = USER_SESSIONS.get(chat_id)

    if not session:
        send_telegram_message(
            chat_id,
            "Oi! Para começar seu diagnóstico financeiro, envie /start.",
        )
        return

    step = session.get("step")

    try:
        if step == "idioma":
            session["lang"] = LANGUAGE_OPTIONS.get(text, "pt")
            session["step"] = "nome"
            send_telegram_message(
                chat_id,
                "💰 Oi! Eu sou a INNA, sua educadora financeira com IA.\n\n"
                "Vou te ajudar com perguntas simples, uma por vez.\n"
                "Não precisa colocar R$, só o número.\n\n"
                "Primeiro, como posso te chamar?",
                remove_keyboard(),
            )

        elif step == "nome":
            if len(text) < 2:
                send_telegram_message(chat_id, "Me diga um nome simples para eu te chamar.")
                return

            session["nome"] = text
            session["step"] = "renda"
            send_telegram_message(
                chat_id,
                f"Prazer, {text}! 😊\n\nQuanto você ganha por mês?\nExemplo: 3000",
            )

        elif step == "renda":
            renda = to_float(text)
            if renda <= 0:
                raise ValueError

            session["renda_mensal"] = renda
            session["step"] = "gastos_fixos"
            send_telegram_message(
                chat_id,
                "Agora me diga quanto você gasta por mês com contas fixas.\n\n"
                "Exemplos: aluguel, luz, água, internet, telefone.\n"
                "Exemplo: 1400",
            )

        elif step == "gastos_fixos":
            gastos_fixos = to_float(text)
            if gastos_fixos < 0:
                raise ValueError

            session["gastos_fixos"] = gastos_fixos
            session["step"] = "gastos_variaveis"
            send_telegram_message(
                chat_id,
                "Quanto você gasta por mês com gastos variáveis?\n\n"
                "Exemplos: mercado, transporte, comida fora, lazer e compras do dia a dia.\n"
                "Exemplo: 700",
            )

        elif step == "gastos_variaveis":
            gastos_variaveis = to_float(text)
            if gastos_variaveis < 0:
                raise ValueError

            session["gastos_variaveis"] = gastos_variaveis
            session["step"] = "dividas"
            send_telegram_message(
                chat_id,
                "Você paga alguma dívida ou parcela por mês?\n\n"
                "Se não tiver, responda 0.\n"
                "Exemplo: 300",
            )

        elif step == "dividas":
            dividas = to_float(text)
            if dividas < 0:
                raise ValueError

            session["dividas_mensais"] = dividas
            session["step"] = "reserva"
            send_telegram_message(
                chat_id,
                "Você tem algum dinheiro guardado hoje?\n\n"
                "Se não tiver, responda 0.\n"
                "Exemplo: 500",
            )

        elif step == "reserva":
            reserva = to_float(text)
            if reserva < 0:
                raise ValueError

            session["reserva_atual"] = reserva
            session["step"] = "objetivo"
            send_telegram_message(
                chat_id,
                "Qual é seu principal objetivo agora?",
                keyboard([
                    ["Organizar as contas"],
                    ["Sair das dívidas"],
                    ["Guardar dinheiro"],
                    ["Fazer sobrar no fim do mês"],
                ]),
            )

        elif step == "objetivo":
            objetivo_original = text
            objetivo = objetivo_original

            dividas_mensais = float(session.get("dividas_mensais", 0))
            objetivo_fala_sobre_divida = any(
                termo in objetivo_original.lower()
                for termo in ["dívida", "divida", "dívidas", "dividas"]
            )

            if dividas_mensais <= 0 and objetivo_fala_sobre_divida:
                objetivo = (
                    "Organizar as contas, evitar novas dívidas e fortalecer a reserva financeira"
                )
                send_telegram_message(
                    chat_id,
                    "Entendi. Você informou que não tem dívidas mensais agora. ✅\n\n"
                    "Então vou ajustar o foco: em vez de sair das dívidas, vamos trabalhar "
                    "para organizar suas contas, evitar novas dívidas e fortalecer sua reserva.",
                )

            payload = {
                "nome": session["nome"],
                "renda_mensal": session["renda_mensal"],
                "gastos_fixos": session["gastos_fixos"],
                "gastos_variaveis": session["gastos_variaveis"],
                "dividas_mensais": session["dividas_mensais"],
                "reserva_atual": session["reserva_atual"],
                "objetivo": objetivo,
            }

            send_telegram_message(
                chat_id,
                "Pronto. Estou analisando seus dados financeiros... ⏳",
                remove_keyboard(),
            )

            resultado = gerar_diagnostico_pelo_payload(payload)
            send_telegram_message(chat_id, resposta_curta(resultado))

            USER_SESSIONS.pop(chat_id, None)

    except ValueError:
        send_telegram_message(
            chat_id,
            "Não consegui entender esse valor. Envie apenas o número.\nExemplo: 3000",
        )

    except Exception as error:
        print(f"Erro no webhook Telegram: {error}")
        send_telegram_message(
            chat_id,
            "Ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes.",
        )


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    update = await request.json()
    update_id = update.get("update_id")

    if update_id in PROCESSED_UPDATES:
        return {"ok": True, "duplicate": True}

    if update_id is not None:
        PROCESSED_UPDATES.add(update_id)

        if len(PROCESSED_UPDATES) > 1000:
            PROCESSED_UPDATES.clear()

    background_tasks.add_task(process_telegram_update, update)

    return {"ok": True}
