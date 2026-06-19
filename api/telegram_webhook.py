import os
import re

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
USER_LAST_LANG = {}
PROCESSED_UPDATES = set()

LANGUAGE_OPTIONS = {
    "🇧🇷 Português": "pt",
    "🇺🇸 English US": "en_us",
    "🇬🇧 English UK": "en_gb",
    "🇪🇸 Español": "es",
    "🇷🇺 Русский": "ru",
    "🇫🇷 Français": "fr",
    "🇸🇦 العربية": "ar",
    "🇩🇪 Deutsch": "de",
    "🇷🇴 Română": "ro",
    "🇺🇦 Українська": "uk",
    "🇨🇭 Schweiz": "ch",
    "🇮🇹 Italiano": "it",
}

LANGUAGE_NAMES = {
    "pt": "português brasileiro",
    "en_us": "English from the United States",
    "en_gb": "British English",
    "es": "español",
    "ru": "русский",
    "fr": "français",
    "ar": "العربية",
    "de": "Deutsch",
    "ro": "română",
    "uk": "українська",
    "ch": "Swiss German / German",
    "it": "italiano",
}

CURRENCY_BY_LANG = {
    "pt": {"prefix": "R$ ", "suffix": "", "style": "br"},
    "en_us": {"prefix": "US$ ", "suffix": "", "style": "us"},
    "en_gb": {"prefix": "£", "suffix": "", "style": "uk"},
    "es": {"prefix": "€ ", "suffix": "", "style": "br"},
    "ru": {"prefix": "", "suffix": " ₽", "style": "ru"},
    "fr": {"prefix": "€ ", "suffix": "", "style": "fr"},
    "ar": {"prefix": "SAR ", "suffix": "", "style": "us"},
    "de": {"prefix": "€ ", "suffix": "", "style": "de"},
    "ro": {"prefix": "", "suffix": " RON", "style": "ro"},
    "uk": {"prefix": "", "suffix": " ₴", "style": "uk"},
    "ch": {"prefix": "CHF ", "suffix": "", "style": "ch"},
    "it": {"prefix": "€ ", "suffix": "", "style": "it"},
}

TEXTS = {
    "pt": {
        "choose_language": "🌍 Escolha o idioma / Choose your language:",
        "auto_start": "💰 Oi! Eu sou a INNA, sua educadora financeira com IA.\n\nVou te ajudar a organizar seu dinheiro com perguntas simples.\n\n🌍 Primeiro, escolha o idioma:",
        "start": "💰 Oi! Eu sou a INNA, sua educadora financeira com IA.\n\nVou te ajudar com perguntas simples, uma por vez.\nNão precisa colocar R$, só o número.\n\nPrimeiro, como posso te chamar?",
        "invalid_name": "Me diga um nome simples para eu te chamar.",
        "ask_income": "Prazer, {nome}! 😊\n\nQuanto você ganha por mês?",
        "ask_fixed": "Agora me diga quanto você gasta por mês com contas fixas.\n\nExemplos: aluguel, luz, água, internet, telefone.",
        "ask_variable": "Quanto você gasta por mês com gastos variáveis?\n\nExemplos: mercado, transporte, comida fora, lazer e compras do dia a dia.",
        "ask_debts": "Você paga alguma dívida ou parcela por mês?\n\nSe não tiver, responda 0.",
        "ask_savings": "Você tem algum dinheiro guardado hoje?\n\nSe não tiver, responda 0.",
        "ask_goal": "Qual é seu principal objetivo agora?",
        "invalid_number": "Não consegui entender esse valor. Envie apenas o número.",
        "adjust_debt": "Entendi. Você informou que não tem dívidas mensais agora. ✅\n\nEntão vou ajustar o foco: em vez de sair das dívidas, vamos trabalhar para organizar suas contas, evitar novas dívidas e fortalecer sua reserva.",
        "analyzing": "Pronto. Estou analisando seus dados financeiros... ⏳",
        "api_error": "Ocorreu um erro ao processar sua mensagem. Tente novamente em alguns instantes.",
        "cancel": "Atendimento cancelado. Para começar de novo, envie /start.",
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
        "goal_options": [["Organizar as contas"], ["Sair das dívidas"], ["Guardar dinheiro"], ["Fazer sobrar no fim do mês"]],
        "risk_map": {"Baixo": "Baixo", "Medio": "Médio", "Alto": "Alto"},
    },
    "en_us": {
        "choose_language": "🌍 Choose your language:",
        "auto_start": "💰 Hi! I'm INNA, your AI financial educator.\n\nI'll help you organize your money with simple questions.\n\n🌍 First, choose your language:",
        "start": "💰 Hi! I'm INNA, your AI financial educator.\n\nI'll help you with simple questions, one at a time.\nNo need to type currency symbols, just numbers.\n\nFirst, what should I call you?",
        "invalid_name": "Please send a simple name.",
        "ask_income": "Nice to meet you, {nome}! 😊\n\nHow much do you earn per month?",
        "ask_fixed": "How much do you spend per month on fixed bills?\n\nExamples: rent, electricity, water, internet, phone.",
        "ask_variable": "How much do you spend per month on variable expenses?\n\nExamples: groceries, transport, food outside, leisure and daily purchases.",
        "ask_debts": "Do you pay any debt or monthly installment?\n\nIf not, reply 0.",
        "ask_savings": "Do you have any money saved today?\n\nIf not, reply 0.",
        "ask_goal": "What is your main goal right now?",
        "invalid_number": "I couldn't understand that value. Please send only the number.",
        "adjust_debt": "Got it. You said you don't have monthly debts right now. ✅\n\nSo I'll adjust the focus: instead of getting out of debt, we'll work on organizing your bills, avoiding new debt and strengthening your savings.",
        "analyzing": "Done. I'm analyzing your financial data... ⏳",
        "api_error": "An error occurred while processing your message. Please try again shortly.",
        "cancel": "Session canceled. To start again, send /start.",
        "diagnosis_title": "💰 INNA diagnosis",
        "name": "Name",
        "balance": "Estimated balance",
        "score": "Financial score",
        "risk": "Risk level",
        "summary": "Summary",
        "quick_plan": "Quick plan",
        "week1": "Week 1 — Map expenses and understand where your money is going.",
        "week2": "Week 2 — Cut waste and review variable expenses.",
        "week3": "Week 3 — Set aside a possible amount for savings.",
        "week4": "Week 4 — Review progress and keep a simple routine.",
        "saved": "✅ Diagnosis saved in INNA's online database.",
        "details": "📊 For the full plan, use the web app, dashboard or PDF report.",
        "goal_options": [["Organize my bills"], ["Get out of debt"], ["Save money"], ["Have money left at the end of the month"]],
        "risk_map": {"Baixo": "Low", "Medio": "Medium", "Alto": "High"},
    },
    "en_gb": {
        "choose_language": "🌍 Choose your language:",
        "auto_start": "💰 Hi! I'm INNA, your AI financial educator.\n\nI'll help you organise your money with simple questions.\n\n🌍 First, choose your language:",
        "start": "💰 Hi! I'm INNA, your AI financial educator.\n\nI'll help you with simple questions, one at a time.\nNo need to type currency symbols, just numbers.\n\nFirst, what should I call you?",
        "invalid_name": "Please send a simple name.",
        "ask_income": "Nice to meet you, {nome}! 😊\n\nHow much do you earn per month?",
        "ask_fixed": "How much do you spend per month on fixed bills?\n\nExamples: rent, electricity, water, internet, phone.",
        "ask_variable": "How much do you spend per month on variable expenses?\n\nExamples: groceries, transport, food outside, leisure and daily purchases.",
        "ask_debts": "Do you pay any debt or monthly instalment?\n\nIf not, reply 0.",
        "ask_savings": "Do you have any money saved today?\n\nIf not, reply 0.",
        "ask_goal": "What is your main goal right now?",
        "invalid_number": "I couldn't understand that value. Please send only the number.",
        "adjust_debt": "Got it. You said you don't have monthly debts right now. ✅\n\nSo I'll adjust the focus: instead of getting out of debt, we'll work on organising your bills, avoiding new debt and strengthening your savings.",
        "analyzing": "Done. I'm analysing your financial data... ⏳",
        "api_error": "An error occurred while processing your message. Please try again shortly.",
        "cancel": "Session cancelled. To start again, send /start.",
        "diagnosis_title": "💰 INNA diagnosis",
        "name": "Name",
        "balance": "Estimated balance",
        "score": "Financial score",
        "risk": "Risk level",
        "summary": "Summary",
        "quick_plan": "Quick plan",
        "week1": "Week 1 — Map expenses and understand where your money is going.",
        "week2": "Week 2 — Cut waste and review variable expenses.",
        "week3": "Week 3 — Set aside a possible amount for savings.",
        "week4": "Week 4 — Review progress and keep a simple routine.",
        "saved": "✅ Diagnosis saved in INNA's online database.",
        "details": "📊 For the full plan, use the web app, dashboard or PDF report.",
        "goal_options": [["Organise my bills"], ["Get out of debt"], ["Save money"], ["Have money left at the end of the month"]],
        "risk_map": {"Baixo": "Low", "Medio": "Medium", "Alto": "High"},
    },
    "es": {
        "choose_language": "🌍 Elige tu idioma:",
        "auto_start": "💰 ¡Hola! Soy INNA, tu educadora financiera con IA.\n\nTe ayudaré a organizar tu dinero con preguntas simples.\n\n🌍 Primero, elige tu idioma:",
        "start": "💰 ¡Hola! Soy INNA, tu educadora financiera con IA.\n\nTe ayudaré con preguntas simples, una por vez.\nNo necesitas escribir símbolos de moneda, solo números.\n\nPrimero, ¿cómo puedo llamarte?",
        "invalid_name": "Dime un nombre simple para llamarte.",
        "ask_income": "¡Mucho gusto, {nome}! 😊\n\n¿Cuánto ganas por mes?",
        "ask_fixed": "¿Cuánto gastas por mes en cuentas fijas?\n\nEjemplos: alquiler, luz, agua, internet, teléfono.",
        "ask_variable": "¿Cuánto gastas por mes en gastos variables?\n\nEjemplos: mercado, transporte, comida fuera, ocio y compras diarias.",
        "ask_debts": "¿Pagas alguna deuda o cuota por mes?\n\nSi no tienes, responde 0.",
        "ask_savings": "¿Tienes dinero guardado hoy?\n\nSi no tienes, responde 0.",
        "ask_goal": "¿Cuál es tu principal objetivo ahora?",
        "invalid_number": "No pude entender ese valor. Envía solo el número.",
        "adjust_debt": "Entiendo. Informaste que no tienes deudas mensuales ahora. ✅\n\nEntonces ajustaré el foco: en vez de salir de deudas, vamos a organizar tus cuentas, evitar nuevas deudas y fortalecer tu reserva.",
        "analyzing": "Listo. Estoy analizando tus datos financieros... ⏳",
        "api_error": "Ocurrió un error al procesar tu mensaje. Inténtalo nuevamente en unos instantes.",
        "cancel": "Atención cancelada. Para empezar de nuevo, envía /start.",
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
        "goal_options": [["Organizar las cuentas"], ["Salir de deudas"], ["Ahorrar dinero"], ["Que sobre dinero al fin del mes"]],
        "risk_map": {"Baixo": "Bajo", "Medio": "Medio", "Alto": "Alto"},
    },
    "ru": {
        "choose_language": "🌍 Выберите язык:",
        "auto_start": "💰 Привет! Я INNA, финансовый помощник с ИИ.\n\nЯ помогу вам организовать деньги простыми вопросами.\n\n🌍 Сначала выберите язык:",
        "start": "💰 Привет! Я INNA, ваш финансовый помощник с ИИ.\n\nЯ задам простые вопросы, шаг за шагом.\nНе нужно писать символ валюты, только число.\n\nКак мне к вам обращаться?",
        "invalid_name": "Пожалуйста, напишите простое имя.",
        "ask_income": "Приятно познакомиться, {nome}! 😊\n\nСколько вы зарабатываете в месяц?",
        "ask_fixed": "Сколько вы тратите в месяц на постоянные счета?\n\nНапример: аренда, электричество, вода, интернет, телефон.",
        "ask_variable": "Сколько вы тратите в месяц на переменные расходы?\n\nНапример: продукты, транспорт, еда вне дома, досуг и покупки.",
        "ask_debts": "Есть ли у вас ежемесячные долги или платежи?\n\nЕсли нет, ответьте 0.",
        "ask_savings": "Есть ли у вас сейчас сбережения?\n\nЕсли нет, ответьте 0.",
        "ask_goal": "Какая ваша главная цель сейчас?",
        "invalid_number": "Я не понял это значение. Отправьте только число.",
        "adjust_debt": "Понял. Вы сообщили, что сейчас у вас нет ежемесячных долгов. ✅\n\nТогда я изменю фокус: вместо выхода из долгов мы будем организовывать счета, избегать новых долгов и укреплять резерв.",
        "analyzing": "Готово. Анализирую ваши финансовые данные... ⏳",
        "api_error": "Произошла ошибка при обработке сообщения. Попробуйте еще раз чуть позже.",
        "cancel": "Диалог отменен. Чтобы начать заново, отправьте /start.",
        "diagnosis_title": "💰 Диагностика INNA",
        "name": "Имя",
        "balance": "Ориентировочный остаток",
        "score": "Финансовый балл",
        "risk": "Уровень риска",
        "summary": "Резюме",
        "quick_plan": "Краткий план",
        "week1": "Неделя 1 — Разобрать расходы и понять, куда уходят деньги.",
        "week2": "Неделя 2 — Сократить лишние траты и пересмотреть переменные расходы.",
        "week3": "Неделя 3 — Отложить возможную сумму в резерв.",
        "week4": "Неделя 4 — Проверить прогресс и сохранить простую привычку.",
        "saved": "✅ Диагностика сохранена в онлайн-базе INNA.",
        "details": "📊 Полный план доступен в веб-приложении, дашборде или PDF-отчете.",
        "goal_options": [["Организовать счета"], ["Выйти из долгов"], ["Накопить деньги"], ["Оставлять деньги в конце месяца"]],
        "risk_map": {"Baixo": "Низкий", "Medio": "Средний", "Alto": "Высокий"},
    },
    "fr": {
        "choose_language": "🌍 Choisissez votre langue :",
        "auto_start": "💰 Bonjour ! Je suis INNA, votre éducatrice financière avec IA.\n\nJe vais vous aider à organiser votre argent avec des questions simples.\n\n🌍 D’abord, choisissez votre langue :",
        "start": "💰 Bonjour ! Je suis INNA, votre éducatrice financière avec IA.\n\nJe vais vous aider avec des questions simples, une par une.\nPas besoin d’écrire le symbole de monnaie, seulement le nombre.\n\nD’abord, comment puis-je vous appeler ?",
        "invalid_name": "Envoyez-moi un prénom simple.",
        "ask_income": "Enchanté, {nome} ! 😊\n\nCombien gagnez-vous par mois ?",
        "ask_fixed": "Combien dépensez-vous par mois en charges fixes ?\n\nExemples : loyer, électricité, eau, internet, téléphone.",
        "ask_variable": "Combien dépensez-vous par mois en dépenses variables ?\n\nExemples : courses, transport, repas dehors, loisirs et achats du quotidien.",
        "ask_debts": "Payez-vous une dette ou une mensualité chaque mois ?\n\nSi non, répondez 0.",
        "ask_savings": "Avez-vous de l’argent épargné aujourd’hui ?\n\nSi non, répondez 0.",
        "ask_goal": "Quel est votre objectif principal maintenant ?",
        "invalid_number": "Je n’ai pas compris cette valeur. Envoyez seulement le nombre.",
        "adjust_debt": "Compris. Vous avez indiqué ne pas avoir de dettes mensuelles actuellement. ✅\n\nJe vais donc ajuster l’objectif : organiser vos comptes, éviter de nouvelles dettes et renforcer votre épargne.",
        "analyzing": "Très bien. J’analyse vos données financières... ⏳",
        "api_error": "Une erreur s’est produite lors du traitement de votre message. Réessayez dans quelques instants.",
        "cancel": "Conversation annulée. Pour recommencer, envoyez /start.",
        "diagnosis_title": "💰 Diagnostic INNA",
        "name": "Nom",
        "balance": "Solde estimé",
        "score": "Score financier",
        "risk": "Niveau de risque",
        "summary": "Résumé",
        "quick_plan": "Plan rapide",
        "week1": "Semaine 1 — Cartographier les dépenses et comprendre où va l’argent.",
        "week2": "Semaine 2 — Réduire les gaspillages et revoir les dépenses variables.",
        "week3": "Semaine 3 — Mettre de côté un montant possible pour l’épargne.",
        "week4": "Semaine 4 — Revoir les progrès et garder une routine simple.",
        "saved": "✅ Diagnostic enregistré dans la base en ligne d’INNA.",
        "details": "📊 Pour voir le plan complet, utilisez l’app web, le dashboard ou le rapport PDF.",
        "goal_options": [["Organiser mes comptes"], ["Sortir des dettes"], ["Épargner"], ["Avoir de l’argent à la fin du mois"]],
        "risk_map": {"Baixo": "Faible", "Medio": "Moyen", "Alto": "Élevé"},
    },
    "ar": {
        "choose_language": "🌍 اختر اللغة:",
        "auto_start": "💰 مرحبًا! أنا INNA، مساعدتك المالية بالذكاء الاصطناعي.\n\nسأساعدك على تنظيم أموالك بأسئلة بسيطة.\n\n🌍 أولًا، اختر اللغة:",
        "start": "💰 مرحبًا! أنا INNA، مساعدتك المالية بالذكاء الاصطناعي.\n\nسأساعدك بأسئلة بسيطة، خطوة بخطوة.\nلا تحتاج إلى كتابة رمز العملة، فقط الرقم.\n\nأولًا، كيف يمكنني مناداتك؟",
        "invalid_name": "من فضلك أرسل اسمًا بسيطًا.",
        "ask_income": "تشرفت بمعرفتك، {nome}! 😊\n\nكم تكسب شهريًا؟",
        "ask_fixed": "كم تنفق شهريًا على المصاريف الثابتة؟\n\nمثل: الإيجار، الكهرباء، الماء، الإنترنت، الهاتف.",
        "ask_variable": "كم تنفق شهريًا على المصاريف المتغيرة؟\n\nمثل: الطعام، النقل، الترفيه، والمشتريات اليومية.",
        "ask_debts": "هل تدفع أي دين أو قسط شهري؟\n\nإذا لم يكن لديك، أرسل 0.",
        "ask_savings": "هل لديك أي مبلغ مدخر الآن؟\n\nإذا لم يكن لديك، أرسل 0.",
        "ask_goal": "ما هو هدفك الرئيسي الآن؟",
        "invalid_number": "لم أفهم هذا الرقم. أرسل الرقم فقط.",
        "adjust_debt": "فهمت. لقد أخبرتني أنه لا توجد لديك ديون شهرية الآن. ✅\n\nلذلك سأعدل التركيز: سنعمل على تنظيم حساباتك، تجنب ديون جديدة، وتقوية الاحتياطي.",
        "analyzing": "تم. أقوم الآن بتحليل بياناتك المالية... ⏳",
        "api_error": "حدث خطأ أثناء معالجة رسالتك. حاول مرة أخرى بعد قليل.",
        "cancel": "تم إلغاء المحادثة. للبدء من جديد، أرسل /start.",
        "diagnosis_title": "💰 تشخيص INNA",
        "name": "الاسم",
        "balance": "الرصيد التقديري",
        "score": "النقاط المالية",
        "risk": "مستوى المخاطر",
        "summary": "الملخص",
        "quick_plan": "خطة سريعة",
        "week1": "الأسبوع 1 — تتبع المصاريف وفهم أين يذهب المال.",
        "week2": "الأسبوع 2 — تقليل الهدر ومراجعة المصاريف المتغيرة.",
        "week3": "الأسبوع 3 — ادخار مبلغ ممكن للاحتياطي.",
        "week4": "الأسبوع 4 — مراجعة التقدم والحفاظ على روتين بسيط.",
        "saved": "✅ تم حفظ التشخيص في قاعدة INNA الإلكترونية.",
        "details": "📊 لرؤية الخطة الكاملة، استخدم تطبيق الويب أو لوحة البيانات أو تقرير PDF.",
        "goal_options": [["تنظيم الحسابات"], ["الخروج من الديون"], ["ادخار المال"], ["بقاء مال في نهاية الشهر"]],
        "risk_map": {"Baixo": "منخفض", "Medio": "متوسط", "Alto": "مرتفع"},
    },
    "de": {
        "choose_language": "🌍 Sprache auswählen:",
        "auto_start": "💰 Hallo! Ich bin INNA, deine Finanzpädagogin mit KI.\n\nIch helfe dir, dein Geld mit einfachen Fragen zu organisieren.\n\n🌍 Wähle zuerst deine Sprache:",
        "start": "💰 Hallo! Ich bin INNA, deine Finanzpädagogin mit KI.\n\nIch stelle dir einfache Fragen, Schritt für Schritt.\nDu musst kein Währungssymbol schreiben, nur die Zahl.\n\nWie darf ich dich nennen?",
        "invalid_name": "Bitte sende einen einfachen Namen.",
        "ask_income": "Schön dich kennenzulernen, {nome}! 😊\n\nWie viel verdienst du pro Monat?",
        "ask_fixed": "Wie viel gibst du monatlich für feste Kosten aus?\n\nBeispiele: Miete, Strom, Wasser, Internet, Telefon.",
        "ask_variable": "Wie viel gibst du monatlich für variable Ausgaben aus?\n\nBeispiele: Lebensmittel, Transport, Essen außer Haus, Freizeit und tägliche Einkäufe.",
        "ask_debts": "Zahlst du monatlich Schulden oder Raten?\n\nWenn nicht, antworte 0.",
        "ask_savings": "Hast du aktuell Geld gespart?\n\nWenn nicht, antworte 0.",
        "ask_goal": "Was ist dein wichtigstes Ziel im Moment?",
        "invalid_number": "Ich konnte diesen Wert nicht verstehen. Sende bitte nur die Zahl.",
        "adjust_debt": "Verstanden. Du hast angegeben, dass du aktuell keine monatlichen Schulden hast. ✅\n\nDann passe ich den Fokus an: Wir organisieren deine Finanzen, vermeiden neue Schulden und stärken deine Rücklage.",
        "analyzing": "Fertig. Ich analysiere deine Finanzdaten... ⏳",
        "api_error": "Beim Verarbeiten deiner Nachricht ist ein Fehler aufgetreten. Bitte versuche es gleich noch einmal.",
        "cancel": "Gespräch abgebrochen. Sende /start, um neu zu beginnen.",
        "diagnosis_title": "💰 INNA-Diagnose",
        "name": "Name",
        "balance": "Geschätzter Überschuss",
        "score": "Finanzscore",
        "risk": "Risikostufe",
        "summary": "Zusammenfassung",
        "quick_plan": "Kurzplan",
        "week1": "Woche 1 — Ausgaben erfassen und verstehen, wohin das Geld geht.",
        "week2": "Woche 2 — Verschwendung reduzieren und variable Ausgaben prüfen.",
        "week3": "Woche 3 — Einen möglichen Betrag für die Rücklage zurücklegen.",
        "week4": "Woche 4 — Fortschritt prüfen und eine einfache Routine halten.",
        "saved": "✅ Diagnose in der Online-Datenbank von INNA gespeichert.",
        "details": "📊 Den vollständigen Plan findest du in der Web-App, im Dashboard oder im PDF-Bericht.",
        "goal_options": [["Finanzen organisieren"], ["Schulden abbauen"], ["Geld sparen"], ["Am Monatsende Geld übrig haben"]],
        "risk_map": {"Baixo": "Niedrig", "Medio": "Mittel", "Alto": "Hoch"},
    },
    "ro": {
        "choose_language": "🌍 Alege limba:",
        "auto_start": "💰 Bună! Sunt INNA, educatoarea ta financiară cu IA.\n\nTe ajut să îți organizezi banii prin întrebări simple.\n\n🌍 Mai întâi, alege limba:",
        "start": "💰 Bună! Sunt INNA, educatoarea ta financiară cu IA.\n\nTe voi ajuta cu întrebări simple, pas cu pas.\nNu trebuie să scrii simbolul monedei, doar numărul.\n\nCum să îți spun?",
        "invalid_name": "Trimite-mi un nume simplu.",
        "ask_income": "Îmi pare bine, {nome}! 😊\n\nCât câștigi pe lună?",
        "ask_fixed": "Cât cheltuiești lunar pe costuri fixe?\n\nExemple: chirie, electricitate, apă, internet, telefon.",
        "ask_variable": "Cât cheltuiești lunar pe cheltuieli variabile?\n\nExemple: alimente, transport, mâncare în oraș, timp liber și cumpărături zilnice.",
        "ask_debts": "Plătești vreo datorie sau rată lunară?\n\nDacă nu, răspunde 0.",
        "ask_savings": "Ai bani puși deoparte acum?\n\nDacă nu, răspunde 0.",
        "ask_goal": "Care este obiectivul tău principal acum?",
        "invalid_number": "Nu am înțeles această valoare. Trimite doar numărul.",
        "adjust_debt": "Am înțeles. Ai spus că nu ai datorii lunare acum. ✅\n\nVoi ajusta obiectivul: vom organiza conturile, vom evita datorii noi și vom întări rezerva financiară.",
        "analyzing": "Gata. Îți analizez datele financiare... ⏳",
        "api_error": "A apărut o eroare la procesarea mesajului. Încearcă din nou în câteva momente.",
        "cancel": "Conversație anulată. Pentru a începe din nou, trimite /start.",
        "diagnosis_title": "💰 Diagnostic INNA",
        "name": "Nume",
        "balance": "Sold estimat",
        "score": "Scor financiar",
        "risk": "Nivel de risc",
        "summary": "Rezumat",
        "quick_plan": "Plan rapid",
        "week1": "Săptămâna 1 — Notează cheltuielile și înțelege unde se duc banii.",
        "week2": "Săptămâna 2 — Redu risipa și verifică cheltuielile variabile.",
        "week3": "Săptămâna 3 — Pune deoparte o sumă posibilă pentru rezervă.",
        "week4": "Săptămâna 4 — Verifică progresul și păstrează o rutină simplă.",
        "saved": "✅ Diagnosticul a fost salvat în baza online INNA.",
        "details": "📊 Pentru planul complet, folosește aplicația web, dashboardul sau raportul PDF.",
        "goal_options": [["Organizarea conturilor"], ["Ieșirea din datorii"], ["Economisirea banilor"], ["Să rămână bani la final de lună"]],
        "risk_map": {"Baixo": "Scăzut", "Medio": "Mediu", "Alto": "Ridicat"},
    },
    "uk": {
        "choose_language": "🌍 Оберіть мову:",
        "auto_start": "💰 Привіт! Я INNA, ваш фінансовий помічник з ШІ.\n\nЯ допоможу вам організувати гроші простими запитаннями.\n\n🌍 Спочатку оберіть мову:",
        "start": "💰 Привіт! Я INNA, ваш фінансовий помічник з ШІ.\n\nЯ ставитиму прості запитання, крок за кроком.\nНе потрібно писати символ валюти, лише число.\n\nЯк мені до вас звертатися?",
        "invalid_name": "Будь ласка, напишіть просте ім’я.",
        "ask_income": "Приємно познайомитися, {nome}! 😊\n\nСкільки ви заробляєте на місяць?",
        "ask_fixed": "Скільки ви витрачаєте щомісяця на постійні рахунки?\n\nНаприклад: оренда, електрика, вода, інтернет, телефон.",
        "ask_variable": "Скільки ви витрачаєте щомісяця на змінні витрати?\n\nНаприклад: продукти, транспорт, їжа поза домом, дозвілля та покупки.",
        "ask_debts": "Чи маєте ви щомісячні борги або платежі?\n\nЯкщо ні, відповідайте 0.",
        "ask_savings": "Чи маєте ви зараз заощадження?\n\nЯкщо ні, відповідайте 0.",
        "ask_goal": "Яка ваша головна мета зараз?",
        "invalid_number": "Я не зрозуміла це значення. Надішліть лише число.",
        "adjust_debt": "Зрозуміло. Ви повідомили, що зараз не маєте щомісячних боргів. ✅\n\nТоді я зміню фокус: організувати рахунки, уникати нових боргів і зміцнити резерв.",
        "analyzing": "Готово. Аналізую ваші фінансові дані... ⏳",
        "api_error": "Сталася помилка під час обробки повідомлення. Спробуйте ще раз трохи пізніше.",
        "cancel": "Діалог скасовано. Щоб почати знову, надішліть /start.",
        "diagnosis_title": "💰 Діагностика INNA",
        "name": "Ім’я",
        "balance": "Орієнтовний залишок",
        "score": "Фінансовий бал",
        "risk": "Рівень ризику",
        "summary": "Резюме",
        "quick_plan": "Короткий план",
        "week1": "Тиждень 1 — Відстежити витрати та зрозуміти, куди йдуть гроші.",
        "week2": "Тиждень 2 — Зменшити зайві витрати та переглянути змінні витрати.",
        "week3": "Тиждень 3 — Відкласти можливу суму в резерв.",
        "week4": "Тиждень 4 — Перевірити прогрес і зберегти просту рутину.",
        "saved": "✅ Діагностику збережено в онлайн-базі INNA.",
        "details": "📊 Повний план доступний у веб-додатку, дашборді або PDF-звіті.",
        "goal_options": [["Організувати рахунки"], ["Вийти з боргів"], ["Заощадити гроші"], ["Мати гроші наприкінці місяця"]],
        "risk_map": {"Baixo": "Низький", "Medio": "Середній", "Alto": "Високий"},
    },
    "ch": {
        "choose_language": "🌍 Sprache auswählen:",
        "auto_start": "💰 Grüezi! Ich bin INNA, deine Finanzpädagogin mit KI.\n\nIch helfe dir, dein Geld mit einfachen Fragen zu organisieren.\n\n🌍 Wähle zuerst deine Sprache:",
        "start": "💰 Grüezi! Ich bin INNA, deine Finanzpädagogin mit KI.\n\nIch stelle dir einfache Fragen, Schritt für Schritt.\nDu musst kein Währungssymbol schreiben, nur die Zahl.\n\nWie darf ich dich nennen?",
        "invalid_name": "Bitte sende einen einfachen Namen.",
        "ask_income": "Schön dich kennenzulernen, {nome}! 😊\n\nWie viel verdienst du pro Monat?",
        "ask_fixed": "Wie viel gibst du monatlich für feste Kosten aus?\n\nBeispiele: Miete, Strom, Wasser, Internet, Telefon.",
        "ask_variable": "Wie viel gibst du monatlich für variable Ausgaben aus?\n\nBeispiele: Lebensmittel, Transport, Essen außer Haus, Freizeit und tägliche Einkäufe.",
        "ask_debts": "Zahlst du monatlich Schulden oder Raten?\n\nWenn nicht, antworte 0.",
        "ask_savings": "Hast du aktuell Geld gespart?\n\nWenn nicht, antworte 0.",
        "ask_goal": "Was ist dein wichtigstes Ziel im Moment?",
        "invalid_number": "Ich konnte diesen Wert nicht verstehen. Sende bitte nur die Zahl.",
        "adjust_debt": "Verstanden. Du hast angegeben, dass du aktuell keine monatlichen Schulden hast. ✅\n\nDann passe ich den Fokus an: Wir organisieren deine Finanzen, vermeiden neue Schulden und stärken deine Rücklage.",
        "analyzing": "Fertig. Ich analysiere deine Finanzdaten... ⏳",
        "api_error": "Beim Verarbeiten deiner Nachricht ist ein Fehler aufgetreten. Bitte versuche es gleich noch einmal.",
        "cancel": "Gespräch abgebrochen. Sende /start, um neu zu beginnen.",
        "diagnosis_title": "💰 INNA-Diagnose",
        "name": "Name",
        "balance": "Geschätzter Überschuss",
        "score": "Finanzscore",
        "risk": "Risikostufe",
        "summary": "Zusammenfassung",
        "quick_plan": "Kurzplan",
        "week1": "Woche 1 — Ausgaben erfassen und verstehen, wohin das Geld geht.",
        "week2": "Woche 2 — Verschwendung reduzieren und variable Ausgaben prüfen.",
        "week3": "Woche 3 — Einen möglichen Betrag für die Rücklage zurücklegen.",
        "week4": "Woche 4 — Fortschritt prüfen und eine einfache Routine halten.",
        "saved": "✅ Diagnose in der Online-Datenbank von INNA gespeichert.",
        "details": "📊 Den vollständigen Plan findest du in der Web-App, im Dashboard oder im PDF-Bericht.",
        "goal_options": [["Finanzen organisieren"], ["Schulden abbauen"], ["Geld sparen"], ["Am Monatsende Geld übrig haben"]],
        "risk_map": {"Baixo": "Niedrig", "Medio": "Mittel", "Alto": "Hoch"},
    },
    "it": {
        "choose_language": "🌍 Scegli la lingua:",
        "auto_start": "💰 Ciao! Sono INNA, la tua educatrice finanziaria con IA.\n\nTi aiuterò a organizzare il tuo denaro con domande semplici.\n\n🌍 Prima scegli la lingua:",
        "start": "💰 Ciao! Sono INNA, la tua educatrice finanziaria con IA.\n\nTi aiuterò con domande semplici, una alla volta.\nNon serve scrivere il simbolo della valuta, solo il numero.\n\nCome posso chiamarti?",
        "invalid_name": "Mandami un nome semplice.",
        "ask_income": "Piacere, {nome}! 😊\n\nQuanto guadagni al mese?",
        "ask_fixed": "Quanto spendi al mese per spese fisse?\n\nEsempi: affitto, luce, acqua, internet, telefono.",
        "ask_variable": "Quanto spendi al mese per spese variabili?\n\nEsempi: spesa, trasporto, pasti fuori, tempo libero e acquisti quotidiani.",
        "ask_debts": "Paghi qualche debito o rata mensile?\n\nSe non ne hai, rispondi 0.",
        "ask_savings": "Hai dei soldi risparmiati oggi?\n\nSe non ne hai, rispondi 0.",
        "ask_goal": "Qual è il tuo obiettivo principale adesso?",
        "invalid_number": "Non ho capito questo valore. Invia solo il numero.",
        "adjust_debt": "Ho capito. Hai indicato che ora non hai debiti mensili. ✅\n\nQuindi adatterò il focus: organizzeremo i conti, eviteremo nuovi debiti e rafforzeremo il risparmio.",
        "analyzing": "Perfetto. Sto analizzando i tuoi dati finanziari... ⏳",
        "api_error": "Si è verificato un errore durante l’elaborazione del messaggio. Riprova tra poco.",
        "cancel": "Conversazione annullata. Per ricominciare, invia /start.",
        "diagnosis_title": "💰 Diagnosi INNA",
        "name": "Nome",
        "balance": "Saldo stimato",
        "score": "Punteggio finanziario",
        "risk": "Livello di rischio",
        "summary": "Riepilogo",
        "quick_plan": "Piano rapido",
        "week1": "Settimana 1 — Mappare le spese e capire dove va il denaro.",
        "week2": "Settimana 2 — Ridurre gli sprechi e rivedere le spese variabili.",
        "week3": "Settimana 3 — Mettere da parte una somma possibile per il risparmio.",
        "week4": "Settimana 4 — Rivedere i progressi e mantenere una routine semplice.",
        "saved": "✅ Diagnosi salvata nella base online di INNA.",
        "details": "📊 Per vedere il piano completo, usa l’app web, il dashboard o il report PDF.",
        "goal_options": [["Organizzare i conti"], ["Uscire dai debiti"], ["Risparmiare denaro"], ["Avere soldi a fine mese"]],
        "risk_map": {"Baixo": "Basso", "Medio": "Medio", "Alto": "Alto"},
    },
}


def get_text(lang: str, key: str) -> str:
    return TEXTS.get(lang, TEXTS["pt"]).get(key, TEXTS["pt"][key])


def get_lang_from_session(session: dict | None) -> str:
    if not session:
        return "pt"
    return session.get("lang", "pt")


def get_chat_lang(chat_id: int, session: dict | None = None) -> str:
    if session and session.get("lang"):
        return session.get("lang", "pt")
    return USER_LAST_LANG.get(chat_id, "pt")


def get_help_message(lang: str) -> str:
    messages = {
        "pt": "💰 INNA ajuda você a organizar sua vida financeira.\n\nComandos:\n/start - Começar atendimento\n/idioma - Trocar idioma\n/cancelar - Cancelar atendimento",
        "en_us": "💰 INNA helps you organize your financial life.\n\nCommands:\n/start - Start service\n/idioma - Change language\n/cancelar - Cancel service",
        "en_gb": "💰 INNA helps you organise your financial life.\n\nCommands:\n/start - Start service\n/idioma - Change language\n/cancelar - Cancel service",
        "es": "💰 INNA te ayuda a organizar tu vida financiera.\n\nComandos:\n/start - Empezar atención\n/idioma - Cambiar idioma\n/cancelar - Cancelar atención",
        "ru": "💰 INNA помогает организовать финансовую жизнь.\n\nКоманды:\n/start - Начать\n/idioma - Сменить язык\n/cancelar - Отменить",
        "fr": "💰 INNA vous aide à organiser votre vie financière.\n\nCommandes :\n/start - Commencer\n/idioma - Changer de langue\n/cancelar - Annuler",
        "ar": "💰 تساعدك INNA على تنظيم حياتك المالية.\n\nالأوامر:\n/start - بدء الخدمة\n/idioma - تغيير اللغة\n/cancelar - إلغاء الخدمة",
        "de": "💰 INNA hilft dir, dein finanzielles Leben zu organisieren.\n\nBefehle:\n/start - Starten\n/idioma - Sprache ändern\n/cancelar - Abbrechen",
        "ro": "💰 INNA te ajută să îți organizezi viața financiară.\n\nComenzi:\n/start - Începe\n/idioma - Schimbă limba\n/cancelar - Anulează",
        "uk": "💰 INNA допомагає організувати фінансове життя.\n\nКоманди:\n/start - Почати\n/idioma - Змінити мову\n/cancelar - Скасувати",
        "ch": "💰 INNA hilft dir, dein finanzielles Leben zu organisieren.\n\nBefehle:\n/start - Starten\n/idioma - Sprache ändern\n/cancelar - Abbrechen",
        "it": "💰 INNA ti aiuta a organizzare la tua vita finanziaria.\n\nComandi:\n/start - Iniziare\n/idioma - Cambiare lingua\n/cancelar - Annullare",
    }
    return messages.get(lang, messages["pt"])


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


def language_keyboard() -> dict:
    return keyboard([
        ["🇧🇷 Português", "🇺🇸 English US"],
        ["🇬🇧 English UK", "🇪🇸 Español"],
        ["🇷🇺 Русский", "🇫🇷 Français"],
        ["🇸🇦 العربية", "🇩🇪 Deutsch"],
        ["🇷🇴 Română", "🇺🇦 Українська"],
        ["🇨🇭 Schweiz", "🇮🇹 Italiano"],
    ])


def keyboard(options: list[list[str]]) -> dict:
    return {
        "keyboard": options,
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


def remove_keyboard() -> dict:
    return {"remove_keyboard": True}


def parse_user_number(text: str) -> float:
    text = text.strip()

    text = re.sub(
        r"(R\\$|US\\$|\\$|€|£|₽|₴|SAR|RON|CHF|BRL|USD|EUR|GBP|RUB|UAH)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace(" ", "").replace("\\u00a0", "")
    text = re.sub(r"[^0-9,\\.\\-]", "", text)

    if not text:
        raise ValueError("Valor vazio")

    has_comma = "," in text
    has_dot = "." in text

    if has_comma and has_dot:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif has_comma:
        parts = text.split(",")
        if len(parts) > 2:
            text = text.replace(",", "")
        elif len(parts[-1]) == 3 and len(parts[0]) <= 3:
            text = text.replace(",", "")
        else:
            text = text.replace(",", ".")
    elif has_dot:
        parts = text.split(".")
        if len(parts) > 2:
            text = text.replace(".", "")
        elif len(parts[-1]) == 3 and len(parts[0]) <= 3:
            text = text.replace(".", "")

    return float(text)


def to_float(text: str) -> float:
    return parse_user_number(text)


def format_money(value, lang: str = "pt") -> str:
    try:
        number = float(value)
        currency = CURRENCY_BY_LANG.get(lang, CURRENCY_BY_LANG["pt"])
        style = currency["style"]

        if style in ["us", "uk"]:
            formatted = f"{number:,.2f}"
        elif style in ["ru", "fr", "ro", "uk", "ch"]:
            formatted = f"{number:,.2f}"
            formatted = formatted.replace(",", " ").replace(".", ",")
        elif style in ["de", "it"]:
            formatted = f"{number:,.2f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            formatted = f"{number:,.2f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

        return f"{currency['prefix']}{formatted}{currency['suffix']}"
    except Exception:
        currency = CURRENCY_BY_LANG.get(lang, CURRENCY_BY_LANG["pt"])
        return f"{currency['prefix']}0,00{currency['suffix']}"


def translate_risk(risk: str, lang: str) -> str:
    risk_map = TEXTS.get(lang, TEXTS["pt"]).get("risk_map", {})
    return risk_map.get(risk, risk)


def build_summary(resultado: dict, lang: str) -> str:
    saldo = format_money(resultado.get("saldo_estimado"), lang)
    comprometimento = resultado.get("comprometimento_renda_percentual")
    meses = resultado.get("meses_reserva_estimados")
    risco = translate_risk(str(resultado.get("nivel_risco")), lang)

    if lang in ["en_us", "en_gb"]:
        return (
            f"Your estimated monthly balance is {saldo}. "
            f"Your income commitment is {comprometimento}%. "
            f"Your savings cover about {meses} months of current expenses. "
            f"The financial risk level was classified as {risco}."
        )

    if lang == "es":
        return (
            f"Tu saldo mensual estimado es {saldo}. "
            f"El compromiso de tus ingresos es de {comprometimento}%. "
            f"Tu reserva cubre aproximadamente {meses} meses de gastos actuales. "
            f"El nivel de riesgo financiero fue clasificado como {risco}."
        )

    if lang == "ru":
        return (
            f"Ваш ориентировочный ежемесячный остаток составляет {saldo}. "
            f"Нагрузка на доход составляет {comprometimento}%. "
            f"Ваш резерв покрывает примерно {meses} месяцев текущих расходов. "
            f"Уровень финансового риска: {risco}."
        )

    if lang == "fr":
        return (
            f"Votre solde mensuel estimé est de {saldo}. "
            f"Votre engagement de revenu est de {comprometimento}%. "
            f"Votre épargne couvre environ {meses} mois de dépenses actuelles. "
            f"Le niveau de risque financier est classé comme {risco}."
        )

    if lang == "ar":
        return (
            f"رصيدك الشهري التقديري هو {saldo}. "
            f"نسبة الالتزام من الدخل هي {comprometimento}%. "
            f"يغطي احتياطيك حوالي {meses} أشهر من المصاريف الحالية. "
            f"تم تصنيف مستوى المخاطر المالية على أنه {risco}."
        )

    if lang in ["de", "ch"]:
        return (
            f"Dein geschätzter monatlicher Überschuss beträgt {saldo}. "
            f"Die Einkommensbindung liegt bei {comprometimento}%. "
            f"Deine Rücklage deckt ungefähr {meses} Monate der aktuellen Ausgaben. "
            f"Die finanzielle Risikostufe wurde als {risco} eingestuft."
        )

    if lang == "ro":
        return (
            f"Soldul tău lunar estimat este {saldo}. "
            f"Gradul de angajare a venitului este {comprometimento}%. "
            f"Rezerva ta acoperă aproximativ {meses} luni de cheltuieli curente. "
            f"Nivelul de risc financiar a fost clasificat ca {risco}."
        )

    if lang == "uk":
        return (
            f"Ваш орієнтовний щомісячний залишок становить {saldo}. "
            f"Навантаження на дохід становить {comprometimento}%. "
            f"Ваш резерв покриває приблизно {meses} місяців поточних витрат. "
            f"Рівень фінансового ризику: {risco}."
        )

    if lang == "it":
        return (
            f"Il tuo saldo mensile stimato è {saldo}. "
            f"L’impegno del reddito è pari al {comprometimento}%. "
            f"I tuoi risparmi coprono circa {meses} mesi di spese attuali. "
            f"Il livello di rischio finanziario è stato classificato come {risco}."
        )

    return (
        f"Seu saldo estimado mensal é de {saldo}. "
        f"O comprometimento da renda está em {comprometimento}%. "
        f"Sua reserva cobre aproximadamente {meses} meses dos gastos atuais. "
        f"O nível de risco financeiro foi classificado como {risco}."
    )


def resposta_curta(resultado: dict, lang: str = "pt") -> str:
    risk = translate_risk(str(resultado.get("nivel_risco")), lang)

    return f"""
{get_text(lang, "diagnosis_title")}

👤 {get_text(lang, "name")}: {resultado.get("nome")}
💵 {get_text(lang, "balance")}: {format_money(resultado.get("saldo_estimado"), lang)}
📊 {get_text(lang, "score")}: {resultado.get("score_financeiro")}/100
⚠️ {get_text(lang, "risk")}: {risk}

🧾 {get_text(lang, "summary")}:
{build_summary(resultado, lang)}

📅 {get_text(lang, "quick_plan")}:
{get_text(lang, "week1")}
{get_text(lang, "week2")}
{get_text(lang, "week3")}
{get_text(lang, "week4")}

{get_text(lang, "saved")}
{get_text(lang, "details")}
"""


def gerar_diagnostico_pelo_payload(payload: dict, lang: str = "pt") -> dict:
    financial_input = FinancialInput(**payload)
    payload_dict = financial_input.model_dump()

    diagnosis = build_financial_diagnosis(payload_dict)

    objective_with_language = (
        f"{payload_dict['objetivo']}. "
        f"Responda em {LANGUAGE_NAMES.get(lang, 'português brasileiro')}."
    )
    ai_payload = {**payload_dict, "objetivo": objective_with_language}

    ai_plan = generate_ai_plan(ai_payload, diagnosis)

    response = {
        **diagnosis,
        "nome": payload_dict["nome"],
        "objetivo": payload_dict["objetivo"],
        "plano_30_dias": ai_plan,
    }

    diagnostico_id = save_diagnostico_db(payload_dict, response)
    response["id"] = diagnostico_id

    return response


def is_debt_goal(text: str) -> bool:
    terms = [
        "dívida", "divida", "dívidas", "dividas",
        "debt", "debts",
        "deuda", "deudas",
        "dette", "dettes",
        "schuld", "schulden",
        "datorie", "datorii",
        "борг", "борги", "боргів",
        "долг", "долги", "долгов",
        "debito", "debiti",
        "دين", "ديون",
    ]
    lower = text.lower()
    return any(term in lower for term in terms)


def start_language_flow(chat_id: int, lang: str = "pt", auto: bool = False):
    send_telegram_message(
        chat_id,
        get_text(lang, "auto_start") if auto else get_text(lang, "choose_language"),
        language_keyboard(),
    )


def process_telegram_update(update: dict):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        return

    text = text.strip()

    if text in ["/start", "/idioma", "/language"]:
        lang = get_chat_lang(chat_id, USER_SESSIONS.get(chat_id))
        USER_SESSIONS[chat_id] = {"step": "idioma", "lang": lang}
        start_language_flow(chat_id, lang)
        return

    if text in ["/help", "/ajuda"]:
        session = USER_SESSIONS.get(chat_id)
        lang = get_chat_lang(chat_id, session)
        send_telegram_message(chat_id, get_help_message(lang))
        return

    if text in ["/help", "/ajuda"]:
        session = USER_SESSIONS.get(chat_id)
        lang = get_chat_lang(chat_id, session)
        send_telegram_message(chat_id, get_help_message(lang))
        return

    if text in ["/cancelar", "/cancel"]:
        session = USER_SESSIONS.get(chat_id)
        lang = get_chat_lang(chat_id, session)
        USER_LAST_LANG[chat_id] = lang
        USER_SESSIONS.pop(chat_id, None)
        send_telegram_message(chat_id, get_text(lang, "cancel"), remove_keyboard())
        return

    session = USER_SESSIONS.get(chat_id)

    if not session:
        lang = get_chat_lang(chat_id)
        USER_SESSIONS[chat_id] = {"step": "idioma", "lang": lang}
        start_language_flow(chat_id, lang, auto=True)
        return

    step = session.get("step")
    lang = get_lang_from_session(session)

    try:
        if step == "idioma":
            if text not in LANGUAGE_OPTIONS:
                start_language_flow(chat_id)
                return

            session["lang"] = LANGUAGE_OPTIONS.get(text, "pt")
            lang = session["lang"]
            USER_LAST_LANG[chat_id] = lang
            session["step"] = "nome"

            send_telegram_message(
                chat_id,
                get_text(lang, "start"),
                remove_keyboard(),
            )

        elif step == "nome":
            if len(text) < 2:
                send_telegram_message(chat_id, get_text(lang, "invalid_name"))
                return

            session["nome"] = text
            session["step"] = "renda"

            send_telegram_message(
                chat_id,
                get_text(lang, "ask_income").format(nome=text),
            )

        elif step == "renda":
            renda = to_float(text)
            if renda <= 0:
                raise ValueError

            session["renda_mensal"] = renda
            session["step"] = "gastos_fixos"
            send_telegram_message(chat_id, get_text(lang, "ask_fixed"))

        elif step == "gastos_fixos":
            gastos_fixos = to_float(text)
            if gastos_fixos < 0:
                raise ValueError

            session["gastos_fixos"] = gastos_fixos
            session["step"] = "gastos_variaveis"
            send_telegram_message(chat_id, get_text(lang, "ask_variable"))

        elif step == "gastos_variaveis":
            gastos_variaveis = to_float(text)
            if gastos_variaveis < 0:
                raise ValueError

            session["gastos_variaveis"] = gastos_variaveis
            session["step"] = "dividas"
            send_telegram_message(chat_id, get_text(lang, "ask_debts"))

        elif step == "dividas":
            dividas = to_float(text)
            if dividas < 0:
                raise ValueError

            session["dividas_mensais"] = dividas
            session["step"] = "reserva"
            send_telegram_message(chat_id, get_text(lang, "ask_savings"))

        elif step == "reserva":
            reserva = to_float(text)
            if reserva < 0:
                raise ValueError

            session["reserva_atual"] = reserva
            session["step"] = "objetivo"

            send_telegram_message(
                chat_id,
                get_text(lang, "ask_goal"),
                keyboard(TEXTS[lang]["goal_options"]),
            )

        elif step == "objetivo":
            objetivo_original = text
            objetivo = objetivo_original

            dividas_mensais = float(session.get("dividas_mensais", 0))

            if dividas_mensais <= 0 and is_debt_goal(objetivo_original):
                objetivo = (
                    "Organizar as contas, evitar novas dívidas e fortalecer a reserva financeira"
                )
                send_telegram_message(chat_id, get_text(lang, "adjust_debt"))

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
                get_text(lang, "analyzing"),
                remove_keyboard(),
            )

            resultado = gerar_diagnostico_pelo_payload(payload, lang)
            send_telegram_message(chat_id, resposta_curta(resultado, lang))

            USER_LAST_LANG[chat_id] = lang
            USER_SESSIONS.pop(chat_id, None)

    except ValueError:
        send_telegram_message(chat_id, get_text(lang, "invalid_number"))

    except Exception as error:
        print(f"Erro no webhook Telegram: {error}")
        send_telegram_message(chat_id, get_text(lang, "api_error"))


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
