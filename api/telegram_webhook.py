import os
import requests
from fastapi import APIRouter, Request
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(prefix="/telegram", tags=["telegram"])

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


USER_SESSIONS = {}


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
        return f"R$ {float(value):.2f}".replace(".", ",")
    except Exception:
        return "R$ 0,00"


def resposta_curta(resultado: dict) -> str:
    diagnostico = resultado.get("diagnostico", "")
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
    """
    Chama o endpoint /diagnostico da própria API da INNA.

    Isso reaproveita o fluxo já validado:
    motor financeiro + Gemini + Neon + retorno padronizado.
    """
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    response = requests.post(
        f"{base_url}/diagnostico",
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        return {"ok": True}

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
        return {"ok": True}

    if text in ["/cancelar", "/cancel"]:
        USER_SESSIONS.pop(chat_id, None)
        send_telegram_message(
            chat_id,
            "Atendimento cancelado. Para começar de novo, envie /start.",
            remove_keyboard(),
        )
        return {"ok": True}

    session = USER_SESSIONS.get(chat_id)

    if not session:
        send_telegram_message(
            chat_id,
            "Oi! Para começar seu diagnóstico financeiro, envie /start.",
        )
        return {"ok": True}

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
            session["nome"] = text
            session["step"] = "renda"
            send_telegram_message(
                chat_id,
                f"Prazer, {text}! 😊\n\nQuanto você ganha por mês?\nExemplo: 3000",
            )

        elif step == "renda":
            session["renda_mensal"] = to_float(text)
            session["step"] = "gastos_fixos"
            send_telegram_message(
                chat_id,
                "Agora me diga quanto você gasta por mês com contas fixas.\n\n"
                "Exemplos: aluguel, luz, água, internet, telefone.\n"
                "Exemplo: 1400",
            )

        elif step == "gastos_fixos":
            session["gastos_fixos"] = to_float(text)
            session["step"] = "gastos_variaveis"
            send_telegram_message(
                chat_id,
                "Quanto você gasta por mês com gastos variáveis?\n\n"
                "Exemplos: mercado, transporte, comida fora, lazer e compras do dia a dia.\n"
                "Exemplo: 700",
            )

        elif step == "gastos_variaveis":
            session["gastos_variaveis"] = to_float(text)
            session["step"] = "dividas"
            send_telegram_message(
                chat_id,
                "Você paga alguma dívida ou parcela por mês?\n\n"
                "Se não tiver, responda 0.\n"
                "Exemplo: 300",
            )

        elif step == "dividas":
            session["dividas_mensais"] = to_float(text)
            session["step"] = "reserva"
            send_telegram_message(
                chat_id,
                "Você tem algum dinheiro guardado hoje?\n\n"
                "Se não tiver, responda 0.\n"
                "Exemplo: 500",
            )

        elif step == "reserva":
            session["reserva_atual"] = to_float(text)
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

    return {"ok": True}

