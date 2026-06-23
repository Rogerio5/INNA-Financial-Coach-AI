import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests

from src.api_client import gerar_diagnostico_api, enviar_feedback_api, baixar_relatorio_pdf_api, buscar_historico_usuario_api, verificar_api_online, enviar_relatorio_email


st.set_page_config(
    page_title="INNA Financial Coach AI",
    page_icon="💰",
    layout="centered",
)


APP_LANG_LABELS = {
    "pt": "🇧🇷 Português Brasil",
    "en_us": "🇺🇸 English US",
    "en_gb": "🇬🇧 English UK",
    "es": "🇪🇸 Español",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "it": "🇮🇹 Italiano",
    "ro": "🇷🇴 Română",
    "uk": "🇺🇦 Українська",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "ch": "🇨🇭 Schweiz",
}


BROWSER_LANG_TO_APP_LANG = {
    "pt": "pt",
    "pt-br": "pt",
    "en": "en_us",
    "en-us": "en_us",
    "en-gb": "en_gb",
    "es": "es",
    "es-es": "es",
    "de": "de",
    "de-de": "de",
    "fr": "fr",
    "fr-fr": "fr",
    "it": "it",
    "it-it": "it",
    "ro": "ro",
    "ro-ro": "ro",
    "uk": "uk",
    "uk-ua": "uk",
    "ru": "ru",
    "ru-ru": "ru",
    "ar": "ar",
    "ar-sa": "ar",
    "de-ch": "ch",
    "fr-ch": "ch",
    "it-ch": "ch",
}

def detect_browser_language() -> str:
    browser_lang = streamlit_js_eval(
        js_expressions="navigator.language || navigator.userLanguage",
        key="browser_language",
    )

    if not browser_lang:
        return "pt"

    browser_lang = str(browser_lang).lower()
    short_lang = browser_lang.split("-")[0]

    return BROWSER_LANG_TO_APP_LANG.get(
        browser_lang,
        BROWSER_LANG_TO_APP_LANG.get(short_lang, "pt"),
    )


APP_TRANSLATIONS = {
    "pt": {
        "currency_notice": "Os valores devem ser informados em {currency}. A INNA não faz conversão cambial automática.",
        "estimated_balance": "Saldo estimado",
        "financial_score": "Score financeiro",
        "risk": "Risco",
        "income_commitment": "Comprometimento da renda",
        "reserve_months": "Meses de reserva",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnóstico financeiro com IA e plano de ação de 30 dias",
        "notice": "A INNA é uma educadora financeira. Ela não recomenda investimentos nem substitui um profissional certificado.",
        "api_offline": "A API da INNA está offline. Confirme se a API online está ativa.",
        "name": "Seu nome",
        "monthly_income": "Renda mensal",
        "fixed_expenses": "Gastos fixos mensais",
        "variable_expenses": "Gastos variáveis mensais",
        "debts": "Dívidas mensais",
        "savings": "Reserva atual",
        "goal": "Qual seu objetivo financeiro?",
        "default_goal": "Organizar minha vida financeira",
        "generate": "Gerar diagnóstico com a INNA",
        "loading": "Chamando a API da INNA e gerando diagnóstico com IA...",
        "saved": "Diagnóstico gerado e salvo via FastAPI com sucesso!",
        "success": "Diagnóstico gerado com sucesso!",
        "diagnosis": "### Diagnóstico",
        "plan": "### Plano de ação de 30 dias",
        "download_pdf": "📄 Baixar relatório em PDF",
        "email_title": "### 📧 Receber relatório por e-mail",
        "email_input": "Digite seu e-mail para receber o relatório PDF:",
        "email_button": "📧 Enviar relatório por e-mail",
        "email_invalid": "Digite um e-mail válido.",
        "email_success": "Relatório enviado por e-mail com sucesso!",
        "email_error": "Erro ao enviar relatório por e-mail",
        "pdf_error": "Não foi possível baixar o relatório pela API",
        "pdf_unavailable": "Relatório PDF indisponível: diagnóstico ainda não possui ID retornado pela API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Comentário opcional",
        "feedback_placeholder": "Exemplo: o plano ficou claro, faltou mais detalhe, gostei da explicação...",
        "feedback_button": "Enviar feedback",
        "feedback_success": "Feedback registrado via FastAPI com sucesso. Obrigado por ajudar a evoluir a INNA!",
        "history_title": "Histórico individual",
        "history_name": "Nome para buscar histórico",
        "history_limit": "Quantidade máxima de registros",
        "history_button": "Buscar histórico",
        "history_empty": "Nenhum diagnóstico encontrado para esse nome.",
        "browser_translate_warning": "Para testar os idiomas corretamente, desative o tradutor automático do navegador.",
        "feedback_help": "Sua avaliação ajuda a melhorar a INNA e validar o projeto.",
        "feedback_question": "Essa resposta foi útil?",
        "yes": "Sim",
        "no": "Não",
        "history_help": "Consulte diagnósticos anteriores pelo nome do usuário. Essa área usa a FastAPI para buscar dados salvos no PostgreSQL.",
    },
    "en_us": {
        "currency_notice": "Enter values in {currency}. INNA does not automatically convert exchange rates.",
        "estimated_balance": "Estimated balance",
        "financial_score": "Financial score",
        "risk": "Risk",
        "income_commitment": "Income commitment",
        "reserve_months": "Savings months",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "AI financial diagnosis and 30-day action plan",
        "notice": "INNA is a financial educator. It does not recommend investments and does not replace a certified professional.",
        "api_offline": "The INNA API is offline. Please check if the online API is active.",
        "name": "Your name",
        "monthly_income": "Monthly income",
        "fixed_expenses": "Monthly fixed expenses",
        "variable_expenses": "Monthly variable expenses",
        "debts": "Monthly debt payments",
        "savings": "Current savings",
        "goal": "What is your financial goal?",
        "default_goal": "Organize my financial life",
        "generate": "Generate diagnosis with INNA",
        "loading": "Calling INNA API and generating AI diagnosis...",
        "saved": "Diagnosis generated and saved through FastAPI successfully!",
        "success": "Diagnosis generated successfully!",
        "diagnosis": "### Diagnosis",
        "plan": "### 30-day action plan",
        "download_pdf": "📄 Download PDF report",
        "email_title": "### 📧 Receive report by email",
        "email_input": "Enter your email to receive the PDF report:",
        "email_button": "📧 Send report by email",
        "email_invalid": "Enter a valid email.",
        "email_success": "Report sent by email successfully!",
        "email_error": "Error sending report by email",
        "pdf_error": "Could not download the report from the API",
        "pdf_unavailable": "PDF report unavailable: the diagnosis does not have an API ID yet.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optional comment",
        "feedback_placeholder": "Example: the plan was clear, I wanted more detail, I liked the explanation...",
        "feedback_button": "Send feedback",
        "feedback_success": "Feedback registered successfully through FastAPI. Thank you for helping INNA improve!",
        "history_title": "Individual history",
        "history_name": "Name to search history",
        "history_limit": "Maximum number of records",
        "history_button": "Search history",
        "history_empty": "No diagnosis found for this name.",
        "browser_translate_warning": "To test languages correctly, disable the browser automatic translator.",
        "feedback_help": "Your feedback helps improve INNA and validate the project.",
        "feedback_question": "Was this answer useful?",
        "yes": "Yes",
        "no": "No",
        "history_help": "Search previous diagnoses by user name. This area uses FastAPI to retrieve data saved in PostgreSQL.",
    },
    "en_gb": {
        "currency_notice": "Enter values in {currency}. INNA does not automatically convert exchange rates.",
        "estimated_balance": "Estimated balance",
        "financial_score": "Financial score",
        "risk": "Risk",
        "income_commitment": "Income commitment",
        "reserve_months": "Savings months",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "AI financial diagnosis and 30-day action plan",
        "notice": "INNA is a financial educator. It does not recommend investments and does not replace a certified professional.",
        "api_offline": "The INNA API is offline. Please check if the online API is active.",
        "name": "Your name",
        "monthly_income": "Monthly income",
        "fixed_expenses": "Monthly fixed expenses",
        "variable_expenses": "Monthly variable expenses",
        "debts": "Monthly debt payments",
        "savings": "Current savings",
        "goal": "What is your financial goal?",
        "default_goal": "Organise my financial life",
        "generate": "Generate diagnosis with INNA",
        "loading": "Calling INNA API and generating AI diagnosis...",
        "saved": "Diagnosis generated and saved through FastAPI successfully!",
        "success": "Diagnosis generated successfully!",
        "diagnosis": "### Diagnosis",
        "plan": "### 30-day action plan",
        "download_pdf": "📄 Download PDF report",
        "email_title": "### 📧 Receive report by email",
        "email_input": "Enter your email to receive the PDF report:",
        "email_button": "📧 Send report by email",
        "email_invalid": "Enter a valid email.",
        "email_success": "Report sent by email successfully!",
        "email_error": "Error sending report by email",
        "pdf_error": "Could not download the report from the API",
        "pdf_unavailable": "PDF report unavailable: the diagnosis does not have an API ID yet.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optional comment",
        "feedback_placeholder": "Example: the plan was clear, I wanted more detail, I liked the explanation...",
        "feedback_button": "Send feedback",
        "feedback_success": "Feedback registered successfully through FastAPI. Thank you for helping INNA improve!",
        "history_title": "Individual history",
        "history_name": "Name to search history",
        "history_limit": "Maximum number of records",
        "history_button": "Search history",
        "history_empty": "No diagnosis found for this name.",
        "browser_translate_warning": "To test languages correctly, disable the browser automatic translator.",
        "feedback_help": "Your feedback helps improve INNA and validate the project.",
        "feedback_question": "Was this answer useful?",
        "yes": "Yes",
        "no": "No",
        "history_help": "Search previous diagnoses by user name. This area uses FastAPI to retrieve data saved in PostgreSQL.",
    },
    "es": {
        "currency_notice": "Ingresa los valores en {currency}. INNA no convierte tipos de cambio automáticamente.",
        "estimated_balance": "Saldo estimado",
        "financial_score": "Puntuación financiera",
        "risk": "Riesgo",
        "income_commitment": "Compromiso de ingresos",
        "reserve_months": "Meses de reserva",
        "history_score": "Puntuación",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnóstico financiero con IA y plan de acción de 30 días",
        "notice": "INNA es una educadora financiera. No recomienda inversiones ni sustituye a un profesional certificado.",
        "api_offline": "La API de INNA está fuera de línea. Verifica si la API online está activa.",
        "name": "Tu nombre",
        "monthly_income": "Ingresos mensuales",
        "fixed_expenses": "Gastos fijos mensuales",
        "variable_expenses": "Gastos variables mensuales",
        "debts": "Deudas mensuales",
        "savings": "Ahorros actuales",
        "goal": "¿Cuál es tu objetivo financiero?",
        "default_goal": "Organizar mi vida financiera",
        "generate": "Generar diagnóstico con INNA",
        "loading": "Llamando a la API de INNA y generando diagnóstico con IA...",
        "saved": "Diagnóstico generado y guardado con éxito vía FastAPI.",
        "success": "Diagnóstico generado con éxito.",
        "diagnosis": "### Diagnóstico",
        "plan": "### Plan de acción de 30 días",
        "download_pdf": "📄 Descargar informe PDF",
        "email_title": "### 📧 Recibir informe por e-mail",
        "email_input": "Introduce tu e-mail para recibir el informe PDF:",
        "email_button": "📧 Enviar informe por e-mail",
        "email_invalid": "Introduce un e-mail válido.",
        "email_success": "Informe enviado por e-mail con éxito.",
        "email_error": "Error al enviar el informe por e-mail",
        "pdf_error": "No fue posible descargar el informe desde la API",
        "pdf_unavailable": "Informe PDF no disponible: el diagnóstico aún no tiene ID de API.",
        "feedback_title": "Comentarios",
        "feedback_comment": "Comentario opcional",
        "feedback_placeholder": "Ejemplo: el plan fue claro, faltó más detalle, me gustó la explicación...",
        "feedback_button": "Enviar comentario",
        "feedback_success": "Comentario registrado con éxito vía FastAPI. ¡Gracias por ayudar a mejorar INNA!",
        "history_title": "Historial individual",
        "history_name": "Nombre para buscar historial",
        "history_limit": "Número máximo de registros",
        "history_button": "Buscar historial",
        "history_empty": "No se encontró ningún diagnóstico para ese nombre.",
        "feedback_help": "Tu evaluación ayuda a mejorar INNA y validar el proyecto.",
        "feedback_question": "¿Esta respuesta fue útil?",
        "yes": "Sí",
        "no": "No",
        "history_help": "Consulta diagnósticos anteriores por nombre de usuario. Esta área usa FastAPI para buscar datos guardados en PostgreSQL.",
    },
    "de": {
        "currency_notice": "Gib die Werte in {currency} ein. INNA führt keine automatische Währungsumrechnung durch.",
        "estimated_balance": "Geschätzter Überschuss",
        "financial_score": "Finanzscore",
        "risk": "Risiko",
        "income_commitment": "Einkommensbindung",
        "reserve_months": "Rücklagenmonate",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Finanzdiagnose mit KI und 30-Tage-Aktionsplan",
        "notice": "INNA ist eine Finanzpädagogin. Sie empfiehlt keine Investitionen und ersetzt keine zertifizierte Fachperson.",
        "api_offline": "Die INNA-API ist offline. Prüfe, ob die Online-API aktiv ist.",
        "name": "Dein Name",
        "monthly_income": "Monatliches Einkommen",
        "fixed_expenses": "Monatliche Fixkosten",
        "variable_expenses": "Monatliche variable Ausgaben",
        "debts": "Monatliche Schulden/Raten",
        "savings": "Aktuelle Rücklage",
        "goal": "Was ist dein finanzielles Ziel?",
        "default_goal": "Mein Finanzleben organisieren",
        "generate": "Diagnose mit INNA erstellen",
        "loading": "INNA-API wird aufgerufen und KI-Diagnose wird erstellt...",
        "saved": "Diagnose erfolgreich über FastAPI erstellt und gespeichert.",
        "success": "Diagnose erfolgreich erstellt.",
        "diagnosis": "### Diagnose",
        "plan": "### 30-Tage-Aktionsplan",
        "download_pdf": "📄 PDF-Bericht herunterladen",
        "email_title": "### 📧 Bericht per E-Mail erhalten",
        "email_input": "Gib deine E-Mail ein, um den PDF-Bericht zu erhalten:",
        "email_button": "📧 Bericht per E-Mail senden",
        "email_invalid": "Gib eine gültige E-Mail ein.",
        "email_success": "Bericht erfolgreich per E-Mail gesendet.",
        "email_error": "Fehler beim Senden des Berichts per E-Mail",
        "pdf_error": "Bericht konnte nicht von der API heruntergeladen werden",
        "pdf_unavailable": "PDF-Bericht nicht verfügbar: Die Diagnose hat noch keine API-ID.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optionaler Kommentar",
        "feedback_placeholder": "Beispiel: Der Plan war klar, ich wollte mehr Details, mir gefiel die Erklärung...",
        "feedback_button": "Feedback senden",
        "feedback_success": "Feedback erfolgreich über FastAPI registriert. Danke, dass du INNA verbesserst!",
        "history_title": "Individueller Verlauf",
        "history_name": "Name für Verlaufssuche",
        "history_limit": "Maximale Anzahl von Einträgen",
        "history_button": "Verlauf suchen",
        "history_empty": "Keine Diagnose für diesen Namen gefunden.",
        "browser_translate_warning": "Um die Sprachen korrekt zu testen, deaktiviere den automatischen Browser-Übersetzer.",
        "feedback_help": "Deine Bewertung hilft, INNA zu verbessern und das Projekt zu validieren.",
        "feedback_question": "War diese Antwort hilfreich?",
        "yes": "Ja",
        "no": "Nein",
        "history_help": "Suche frühere Diagnosen nach Benutzername. Dieser Bereich nutzt FastAPI, um gespeicherte Daten aus PostgreSQL abzurufen.",
    },
    "fr": {
        "currency_notice": "Saisissez les valeurs en {currency}. INNA ne convertit pas automatiquement les devises.",
        "estimated_balance": "Solde estimé",
        "financial_score": "Score financier",
        "risk": "Risque",
        "income_commitment": "Engagement du revenu",
        "reserve_months": "Mois d’épargne",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnostic financier avec IA et plan d’action de 30 jours",
        "notice": "INNA est une éducatrice financière. Elle ne recommande pas d’investissements et ne remplace pas un professionnel certifié.",
        "api_offline": "L’API INNA est hors ligne. Vérifiez si l’API en ligne est active.",
        "name": "Votre nom",
        "monthly_income": "Revenu mensuel",
        "fixed_expenses": "Dépenses fixes mensuelles",
        "variable_expenses": "Dépenses variables mensuelles",
        "debts": "Dettes mensuelles",
        "savings": "Épargne actuelle",
        "goal": "Quel est votre objectif financier ?",
        "default_goal": "Organiser ma vie financière",
        "generate": "Générer le diagnostic avec INNA",
        "loading": "Appel de l’API INNA et génération du diagnostic IA...",
        "saved": "Diagnostic généré et enregistré avec succès via FastAPI.",
        "success": "Diagnostic généré avec succès.",
        "diagnosis": "### Diagnostic",
        "plan": "### Plan d’action de 30 jours",
        "download_pdf": "📄 Télécharger le rapport PDF",
        "email_title": "### 📧 Recevoir le rapport par e-mail",
        "email_input": "Entrez votre e-mail pour recevoir le rapport PDF :",
        "email_button": "📧 Envoyer le rapport par e-mail",
        "email_invalid": "Entrez un e-mail valide.",
        "email_success": "Rapport envoyé par e-mail avec succès.",
        "email_error": "Erreur lors de l’envoi du rapport par e-mail",
        "pdf_error": "Impossible de télécharger le rapport depuis l’API",
        "pdf_unavailable": "Rapport PDF indisponible : le diagnostic n’a pas encore d’ID API.",
        "feedback_title": "Retour",
        "feedback_comment": "Commentaire optionnel",
        "feedback_placeholder": "Exemple : le plan était clair, je voulais plus de détails, j’ai aimé l’explication...",
        "feedback_button": "Envoyer le retour",
        "feedback_success": "Retour enregistré avec succès via FastAPI. Merci d’aider INNA à s’améliorer !",
        "history_title": "Historique individuel",
        "history_name": "Nom pour rechercher l’historique",
        "history_limit": "Nombre maximum d’enregistrements",
        "history_button": "Rechercher l’historique",
        "history_empty": "Aucun diagnostic trouvé pour ce nom.",
        "feedback_help": "Votre avis aide à améliorer INNA et à valider le projet.",
        "feedback_question": "Cette réponse était-elle utile ?",
        "yes": "Oui",
        "no": "Non",
        "history_help": "Consultez les diagnostics précédents par nom d’utilisateur. Cette zone utilise FastAPI pour récupérer les données enregistrées dans PostgreSQL.",
    },
    "it": {
        "currency_notice": "Inserisci i valori in {currency}. INNA non converte automaticamente i tassi di cambio.",
        "estimated_balance": "Saldo stimato",
        "financial_score": "Punteggio finanziario",
        "risk": "Rischio",
        "income_commitment": "Impegno del reddito",
        "reserve_months": "Mesi di riserva",
        "history_score": "Punteggio",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnosi finanziaria con IA e piano d’azione di 30 giorni",
        "notice": "INNA è un’educatrice finanziaria. Non raccomanda investimenti e non sostituisce un professionista certificato.",
        "api_offline": "L’API INNA è offline. Controlla se l’API online è attiva.",
        "name": "Il tuo nome",
        "monthly_income": "Reddito mensile",
        "fixed_expenses": "Spese fisse mensili",
        "variable_expenses": "Spese variabili mensili",
        "debts": "Debiti mensili",
        "savings": "Risparmi attuali",
        "goal": "Qual è il tuo obiettivo finanziario?",
        "default_goal": "Organizzare la mia vita finanziaria",
        "generate": "Genera diagnosi con INNA",
        "loading": "Chiamata all’API INNA e generazione della diagnosi IA...",
        "saved": "Diagnosi generata e salvata con successo tramite FastAPI.",
        "success": "Diagnosi generata con successo.",
        "diagnosis": "### Diagnosi",
        "plan": "### Piano d’azione di 30 giorni",
        "download_pdf": "📄 Scarica rapporto PDF",
        "email_title": "### 📧 Ricevi il rapporto via e-mail",
        "email_input": "Inserisci la tua e-mail per ricevere il rapporto PDF:",
        "email_button": "📧 Invia rapporto via e-mail",
        "email_invalid": "Inserisci una e-mail valida.",
        "email_success": "Rapporto inviato via e-mail con successo.",
        "email_error": "Errore durante l’invio del rapporto via e-mail",
        "pdf_error": "Impossibile scaricare il rapporto dall’API",
        "pdf_unavailable": "Rapporto PDF non disponibile: la diagnosi non ha ancora un ID API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Commento opzionale",
        "feedback_placeholder": "Esempio: il piano era chiaro, volevo più dettagli, mi è piaciuta la spiegazione...",
        "feedback_button": "Invia feedback",
        "feedback_success": "Feedback registrato con successo tramite FastAPI. Grazie per aiutare INNA a migliorare!",
        "history_title": "Cronologia individuale",
        "history_name": "Nome per cercare la cronologia",
        "history_limit": "Numero massimo di record",
        "history_button": "Cerca cronologia",
        "history_empty": "Nessuna diagnosi trovata per questo nome.",
        "feedback_help": "La tua valutazione aiuta a migliorare INNA e a validare il progetto.",
        "feedback_question": "Questa risposta è stata utile?",
        "yes": "Sì",
        "no": "No",
        "history_help": "Consulta le diagnosi precedenti per nome utente. Quest’area usa FastAPI per cercare dati salvati in PostgreSQL.",
    },
    "ro": {
        "currency_notice": "Introduceți valorile în {currency}. INNA nu face conversie valutară automată.",
        "estimated_balance": "Sold estimat",
        "financial_score": "Scor financiar",
        "risk": "Risc",
        "income_commitment": "Grad de angajare a venitului",
        "reserve_months": "Luni de rezervă",
        "history_score": "Scor",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Diagnostic financiar cu IA și plan de acțiune pe 30 de zile",
        "notice": "INNA este o educatoare financiară. Nu recomandă investiții și nu înlocuiește un profesionist certificat.",
        "api_offline": "API-ul INNA este offline. Verifică dacă API-ul online este activ.",
        "name": "Numele tău",
        "monthly_income": "Venit lunar",
        "fixed_expenses": "Cheltuieli fixe lunare",
        "variable_expenses": "Cheltuieli variabile lunare",
        "debts": "Datorii lunare",
        "savings": "Economii actuale",
        "goal": "Care este obiectivul tău financiar?",
        "default_goal": "Să îmi organizez viața financiară",
        "generate": "Generează diagnosticul cu INNA",
        "loading": "Se apelează API-ul INNA și se generează diagnosticul cu IA...",
        "saved": "Diagnostic generat și salvat cu succes prin FastAPI.",
        "success": "Diagnostic generat cu succes.",
        "diagnosis": "### Diagnostic",
        "plan": "### Plan de acțiune pe 30 de zile",
        "download_pdf": "📄 Descarcă raportul PDF",
        "email_title": "### 📧 Primește raportul prin e-mail",
        "email_input": "Introdu e-mailul pentru a primi raportul PDF:",
        "email_button": "📧 Trimite raportul prin e-mail",
        "email_invalid": "Introdu un e-mail valid.",
        "email_success": "Raport trimis cu succes prin e-mail.",
        "email_error": "Eroare la trimiterea raportului prin e-mail",
        "pdf_error": "Nu s-a putut descărca raportul din API",
        "pdf_unavailable": "Raport PDF indisponibil: diagnosticul nu are încă ID API.",
        "feedback_title": "Feedback",
        "feedback_comment": "Comentariu opțional",
        "feedback_placeholder": "Exemplu: planul a fost clar, am vrut mai multe detalii, mi-a plăcut explicația...",
        "feedback_button": "Trimite feedback",
        "feedback_success": "Feedback înregistrat cu succes prin FastAPI. Mulțumim că ajuți INNA să evolueze!",
        "history_title": "Istoric individual",
        "history_name": "Nume pentru căutarea istoricului",
        "history_limit": "Număr maxim de înregistrări",
        "history_button": "Caută istoricul",
        "history_empty": "Nu a fost găsit niciun diagnostic pentru acest nume.",
        "feedback_help": "Evaluarea ta ajută la îmbunătățirea INNA și la validarea proiectului.",
        "feedback_question": "A fost util acest răspuns?",
        "yes": "Da",
        "no": "Nu",
        "history_help": "Consultă diagnosticele anterioare după numele utilizatorului. Această zonă folosește FastAPI pentru datele salvate în PostgreSQL.",
    },
    "uk": {
        "currency_notice": "Вводьте значення у валюті {currency}. INNA не виконує автоматичну конвертацію валют.",
        "estimated_balance": "Орієнтовний баланс",
        "financial_score": "Фінансовий бал",
        "risk": "Ризик",
        "income_commitment": "Навантаження на дохід",
        "reserve_months": "Місяці резерву",
        "history_score": "Бал",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Фінансова діагностика з ШІ та план дій на 30 днів",
        "notice": "INNA — фінансова освітня помічниця. Вона не рекомендує інвестиції та не замінює сертифікованого фахівця.",
        "api_offline": "API INNA не в мережі. Перевірте, чи активний онлайн API.",
        "name": "Ваше ім’я",
        "monthly_income": "Місячний дохід",
        "fixed_expenses": "Щомісячні фіксовані витрати",
        "variable_expenses": "Щомісячні змінні витрати",
        "debts": "Щомісячні борги",
        "savings": "Поточні заощадження",
        "goal": "Яка ваша фінансова мета?",
        "default_goal": "Організувати моє фінансове життя",
        "generate": "Створити діагностику з INNA",
        "loading": "Виклик API INNA та створення діагностики з ШІ...",
        "saved": "Діагностику успішно створено та збережено через FastAPI.",
        "success": "Діагностику успішно створено.",
        "diagnosis": "### Діагностика",
        "plan": "### План дій на 30 днів",
        "download_pdf": "📄 Завантажити PDF-звіт",
        "email_title": "### 📧 Отримати звіт електронною поштою",
        "email_input": "Введіть e-mail, щоб отримати PDF-звіт:",
        "email_button": "📧 Надіслати звіт e-mail",
        "email_invalid": "Введіть дійсний e-mail.",
        "email_success": "Звіт успішно надіслано електронною поштою.",
        "email_error": "Помилка надсилання звіту електронною поштою",
        "pdf_error": "Не вдалося завантажити звіт з API",
        "pdf_unavailable": "PDF-звіт недоступний: діагностика ще не має API ID.",
        "feedback_title": "Відгук",
        "feedback_comment": "Необов’язковий коментар",
        "feedback_placeholder": "Приклад: план був зрозумілим, хотілося більше деталей, сподобалося пояснення...",
        "feedback_button": "Надіслати відгук",
        "feedback_success": "Відгук успішно збережено через FastAPI. Дякуємо, що допомагаєте INNA розвиватися!",
        "history_title": "Індивідуальна історія",
        "history_name": "Ім’я для пошуку історії",
        "history_limit": "Максимальна кількість записів",
        "history_button": "Шукати історію",
        "history_empty": "Діагностику для цього імені не знайдено.",
        "feedback_help": "Ваш відгук допомагає покращити INNA та перевірити проєкт.",
        "feedback_question": "Ця відповідь була корисною?",
        "yes": "Так",
        "no": "Ні",
        "history_help": "Перегляньте попередні діагностики за ім’ям користувача. Цей розділ використовує FastAPI для пошуку даних у PostgreSQL.",
    },
    "ru": {
        "currency_notice": "Введите значения в валюте {currency}. INNA не выполняет автоматическую конвертацию валют.",
        "estimated_balance": "Оценочный баланс",
        "financial_score": "Финансовый балл",
        "risk": "Риск",
        "income_commitment": "Нагрузка на доход",
        "reserve_months": "Месяцы резерва",
        "history_score": "Балл",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Финансовая диагностика с ИИ и план действий на 30 дней",
        "notice": "INNA — финансовый образовательный помощник. Она не рекомендует инвестиции и не заменяет сертифицированного специалиста.",
        "api_offline": "API INNA не в сети. Проверьте, активен ли онлайн API.",
        "name": "Ваше имя",
        "monthly_income": "Ежемесячный доход",
        "fixed_expenses": "Ежемесячные фиксированные расходы",
        "variable_expenses": "Ежемесячные переменные расходы",
        "debts": "Ежемесячные долги",
        "savings": "Текущие сбережения",
        "goal": "Какая у вас финансовая цель?",
        "default_goal": "Организовать мою финансовую жизнь",
        "generate": "Создать диагностику с INNA",
        "loading": "Вызов API INNA и создание диагностики с ИИ...",
        "saved": "Диагностика успешно создана и сохранена через FastAPI.",
        "success": "Диагностика успешно создана.",
        "diagnosis": "### Диагностика",
        "plan": "### План действий на 30 дней",
        "download_pdf": "📄 Скачать PDF-отчёт",
        "email_title": "### 📧 Получить отчёт по e-mail",
        "email_input": "Введите e-mail, чтобы получить PDF-отчёт:",
        "email_button": "📧 Отправить отчёт по e-mail",
        "email_invalid": "Введите корректный e-mail.",
        "email_success": "Отчёт успешно отправлен по e-mail.",
        "email_error": "Ошибка отправки отчёта по e-mail",
        "pdf_error": "Не удалось скачать отчёт из API",
        "pdf_unavailable": "PDF-отчёт недоступен: у диагностики ещё нет API ID.",
        "feedback_title": "Обратная связь",
        "feedback_comment": "Необязательный комментарий",
        "feedback_placeholder": "Пример: план был понятным, хотелось больше деталей, понравилось объяснение...",
        "feedback_button": "Отправить отзыв",
        "feedback_success": "Отзыв успешно сохранён через FastAPI. Спасибо, что помогаете INNA развиваться!",
        "history_title": "Индивидуальная история",
        "history_name": "Имя для поиска истории",
        "history_limit": "Максимальное количество записей",
        "history_button": "Искать историю",
        "history_empty": "Диагностика для этого имени не найдена.",
        "feedback_help": "Ваш отзыв помогает улучшить INNA и подтвердить проект.",
        "feedback_question": "Был ли этот ответ полезен?",
        "yes": "Да",
        "no": "Нет",
        "history_help": "Просмотрите предыдущие диагностики по имени пользователя. Этот раздел использует FastAPI для поиска данных в PostgreSQL.",
    },
    "ar": {
        "currency_notice": "أدخل القيم بعملة {currency}. لا تقوم INNA بتحويل العملات تلقائيًا.",
        "estimated_balance": "الرصيد التقديري",
        "financial_score": "الدرجة المالية",
        "risk": "المخاطر",
        "income_commitment": "نسبة الالتزام من الدخل",
        "reserve_months": "أشهر الاحتياطي",
        "history_score": "الدرجة",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "تشخيص مالي بالذكاء الاصطناعي وخطة عمل لمدة 30 يومًا",
        "notice": "INNA هي أداة تعليم مالي. لا تقدم توصيات استثمارية ولا تستبدل المتخصص المالي المعتمد.",
        "api_offline": "واجهة API الخاصة بـ INNA غير متصلة. تحقق من أن الواجهة تعمل عبر الإنترنت.",
        "name": "اسمك",
        "monthly_income": "الدخل الشهري",
        "fixed_expenses": "المصاريف الثابتة الشهرية",
        "variable_expenses": "المصاريف المتغيرة الشهرية",
        "debts": "الديون الشهرية",
        "savings": "المدخرات الحالية",
        "goal": "ما هو هدفك المالي؟",
        "default_goal": "تنظيم حياتي المالية",
        "generate": "إنشاء التشخيص باستخدام INNA",
        "loading": "يتم الاتصال بواجهة INNA وإنشاء التشخيص بالذكاء الاصطناعي...",
        "saved": "تم إنشاء التشخيص وحفظه بنجاح عبر FastAPI.",
        "success": "تم إنشاء التشخيص بنجاح.",
        "diagnosis": "### التشخيص",
        "plan": "### خطة عمل لمدة 30 يومًا",
        "download_pdf": "📄 تنزيل تقرير PDF",
        "email_title": "### 📧 استلام التقرير عبر البريد الإلكتروني",
        "email_input": "أدخل بريدك الإلكتروني لاستلام تقرير PDF:",
        "email_button": "📧 إرسال التقرير عبر البريد الإلكتروني",
        "email_invalid": "أدخل بريدًا إلكترونيًا صالحًا.",
        "email_success": "تم إرسال التقرير عبر البريد الإلكتروني بنجاح.",
        "email_error": "خطأ في إرسال التقرير عبر البريد الإلكتروني",
        "pdf_error": "تعذر تنزيل التقرير من API",
        "pdf_unavailable": "تقرير PDF غير متاح: التشخيص لا يحتوي على معرف API بعد.",
        "feedback_title": "ملاحظات",
        "feedback_comment": "تعليق اختياري",
        "feedback_placeholder": "مثال: كانت الخطة واضحة، أريد تفاصيل أكثر، أعجبتني الشرح...",
        "feedback_button": "إرسال الملاحظات",
        "feedback_success": "تم تسجيل الملاحظات بنجاح عبر FastAPI. شكرًا لمساعدتك في تطوير INNA!",
        "history_title": "السجل الفردي",
        "history_name": "الاسم للبحث في السجل",
        "history_limit": "الحد الأقصى لعدد السجلات",
        "history_button": "البحث في السجل",
        "history_empty": "لم يتم العثور على تشخيص لهذا الاسم.",
        "feedback_help": "تساعد ملاحظاتك في تحسين INNA والتحقق من المشروع.",
        "feedback_question": "هل كانت هذه الإجابة مفيدة؟",
        "yes": "نعم",
        "no": "لا",
        "history_help": "ابحث عن التشخيصات السابقة حسب اسم المستخدم. يستخدم هذا القسم FastAPI لجلب البيانات المحفوظة في PostgreSQL.",
    },
    "ch": {
        "currency_notice": "Gib die Werte in {currency} ein. INNA führt keine automatische Währungsumrechnung durch.",
        "estimated_balance": "Geschätzter Überschuss",
        "financial_score": "Finanzscore",
        "risk": "Risiko",
        "income_commitment": "Einkommensbindung",
        "reserve_months": "Rücklagenmonate",
        "history_score": "Score",
        "title": "💰 INNA Financial Coach AI",
        "subtitle": "Finanzdiagnose mit KI und 30-Tage-Aktionsplan",
        "notice": "INNA ist eine Finanzpädagogin. Sie empfiehlt keine Investitionen und ersetzt keine zertifizierte Fachperson.",
        "api_offline": "Die INNA-API ist offline. Prüfe, ob die Online-API aktiv ist.",
        "name": "Dein Name",
        "monthly_income": "Monatliches Einkommen",
        "fixed_expenses": "Monatliche Fixkosten",
        "variable_expenses": "Monatliche variable Ausgaben",
        "debts": "Monatliche Schulden/Raten",
        "savings": "Aktuelle Rücklage",
        "goal": "Was ist dein finanzielles Ziel?",
        "default_goal": "Mein Finanzleben organisieren",
        "generate": "Diagnose mit INNA erstellen",
        "loading": "INNA-API wird aufgerufen und KI-Diagnose wird erstellt...",
        "saved": "Diagnose erfolgreich über FastAPI erstellt und gespeichert.",
        "success": "Diagnose erfolgreich erstellt.",
        "diagnosis": "### Diagnose",
        "plan": "### 30-Tage-Aktionsplan",
        "download_pdf": "📄 PDF-Bericht herunterladen",
        "email_title": "### 📧 Bericht per E-Mail erhalten",
        "email_input": "Gib deine E-Mail ein, um den PDF-Bericht zu erhalten:",
        "email_button": "📧 Bericht per E-Mail senden",
        "email_invalid": "Gib eine gültige E-Mail ein.",
        "email_success": "Bericht erfolgreich per E-Mail gesendet.",
        "email_error": "Fehler beim Senden des Berichts per E-Mail",
        "pdf_error": "Bericht konnte nicht von der API heruntergeladen werden",
        "pdf_unavailable": "PDF-Bericht nicht verfügbar: Die Diagnose hat noch keine API-ID.",
        "feedback_title": "Feedback",
        "feedback_comment": "Optionaler Kommentar",
        "feedback_placeholder": "Beispiel: Der Plan war klar, ich wollte mehr Details, mir gefiel die Erklärung...",
        "feedback_button": "Feedback senden",
        "feedback_success": "Feedback erfolgreich über FastAPI registriert. Danke, dass du INNA verbesserst!",
        "history_title": "Individueller Verlauf",
        "history_name": "Name für Verlaufssuche",
        "history_limit": "Maximale Anzahl von Einträgen",
        "history_button": "Verlauf suchen",
        "history_empty": "Keine Diagnose für diesen Namen gefunden.",
        "browser_translate_warning": "Um die Sprachen korrekt zu testen, deaktiviere den automatischen Browser-Übersetzer.",
        "feedback_help": "Deine Bewertung hilft, INNA zu verbessern und das Projekt zu validieren.",
        "feedback_question": "War diese Antwort hilfreich?",
        "yes": "Ja",
        "no": "Nein",
        "history_help": "Suche frühere Diagnosen nach Benutzername. Dieser Bereich nutzt FastAPI, um gespeicherte Daten aus PostgreSQL abzurufen.",
    },
}

detected_lang = detect_browser_language()

if "app_lang" not in st.session_state:
    st.session_state.app_lang = detected_lang

app_lang = st.sidebar.selectbox(
    "🌍 Idioma / Language",
    options=list(APP_LANG_LABELS.keys()),
    index=list(APP_LANG_LABELS.keys()).index(st.session_state.app_lang),
    format_func=lambda key: APP_LANG_LABELS[key],
    key="app_lang",
)



CURRENCY_BY_LANG = {
    "pt": {"moeda": "BRL", "simbolo": "R$"},
    "en_us": {"moeda": "USD", "simbolo": "US$"},
    "en_gb": {"moeda": "GBP", "simbolo": "£"},
    "es": {"moeda": "EUR", "simbolo": "€"},
    "de": {"moeda": "EUR", "simbolo": "€"},
    "fr": {"moeda": "EUR", "simbolo": "€"},
    "it": {"moeda": "EUR", "simbolo": "€"},
    "ro": {"moeda": "RON", "simbolo": "RON"},
    "uk": {"moeda": "UAH", "simbolo": "₴"},
    "ru": {"moeda": "RUB", "simbolo": "₽"},
    "ar": {"moeda": "SAR", "simbolo": "SAR"},
    "ch": {"moeda": "CHF", "simbolo": "CHF"},
}






def translate_risk_app(risk: str) -> str:
    risk = str(risk or "").strip()

    risk_map = {
        "Baixo": {
            "pt": "Baixo",
            "en_us": "Low",
            "en_gb": "Low",
            "es": "Bajo",
            "fr": "Faible",
            "de": "Niedrig",
            "ch": "Niedrig",
            "it": "Basso",
            "ro": "Scăzut",
            "uk": "Низький",
            "ru": "Низкий",
            "ar": "منخفض",
        },
        "Medio": {
            "pt": "Médio",
            "en_us": "Medium",
            "en_gb": "Medium",
            "es": "Medio",
            "fr": "Moyen",
            "de": "Mittel",
            "ch": "Mittel",
            "it": "Medio",
            "ro": "Mediu",
            "uk": "Середній",
            "ru": "Средний",
            "ar": "متوسط",
        },
        "Médio": {
            "pt": "Médio",
            "en_us": "Medium",
            "en_gb": "Medium",
            "es": "Medio",
            "fr": "Moyen",
            "de": "Mittel",
            "ch": "Mittel",
            "it": "Medio",
            "ro": "Mediu",
            "uk": "Середній",
            "ru": "Средний",
            "ar": "متوسط",
        },
        "Alto": {
            "pt": "Alto",
            "en_us": "High",
            "en_gb": "High",
            "es": "Alto",
            "fr": "Élevé",
            "de": "Hoch",
            "ch": "Hoch",
            "it": "Alto",
            "ro": "Ridicat",
            "uk": "Високий",
            "ru": "Высокий",
            "ar": "مرتفع",
        },
    }

    return risk_map.get(risk, {}).get(app_lang, risk)


def label_with_currency(key: str) -> str:
    currency = current_currency_info.get("moeda", "")
    symbol = current_currency_info.get("simbolo", "")

    if symbol and symbol != currency:
        return f"{tr(key)} ({currency} / {symbol})"

    return f"{tr(key)} ({currency})"


def format_currency_app(value, symbol: str, currency: str) -> str:
    try:
        value = float(value)
    except Exception:
        value = 0.0

    if currency in ("USD", "GBP"):
        return f"{symbol}{value:,.2f}"

    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{symbol} {formatted}"


def tr(key: str) -> str:
    return APP_TRANSLATIONS.get(app_lang, APP_TRANSLATIONS["pt"]).get(
        key,
        APP_TRANSLATIONS["pt"].get(key, key),
    )

current_currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

st.sidebar.caption(tr("browser_translate_warning"))


st.title(tr("title"))

if not verificar_api_online():
    st.error(tr("api_offline"))
    st.stop()

st.subheader(tr("subtitle"))

st.info(tr("notice"))

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None


with st.form("financial_form"):
    nome = st.text_input(tr("name"), value="Ronaldo")

    st.caption(
        tr("currency_notice").format(
            currency=f"{current_currency_info['moeda']} / {current_currency_info['simbolo']}"
            if current_currency_info["simbolo"] != current_currency_info["moeda"]
            else current_currency_info["moeda"]
        )
    )

    renda_mensal = st.number_input(
        label_with_currency("monthly_income"),
        min_value=0.0,
        value=3000.0,
        step=100.0,
    )

    gastos_fixos = st.number_input(
        label_with_currency("fixed_expenses"),
        min_value=0.0,
        value=1400.0,
        step=100.0,
    )

    gastos_variaveis = st.number_input(
        label_with_currency("variable_expenses"),
        min_value=0.0,
        value=700.0,
        step=100.0,
    )

    dividas_mensais = st.number_input(
        label_with_currency("debts"),
        min_value=0.0,
        value=300.0,
        step=100.0,
    )

    reserva_atual = st.number_input(
        label_with_currency("savings"),
        min_value=0.0,
        value=500.0,
        step=100.0,
    )

    objetivo = st.text_area(
        tr("goal"),
        value=tr("default_goal"),
    )

    submitted = st.form_submit_button(tr("generate"))


if submitted:
    currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])

    payload = {
        "nome": nome,
        "renda_mensal": renda_mensal,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "dividas_mensais": dividas_mensais,
        "reserva_atual": reserva_atual,
        "objetivo": objetivo,
        "idioma": app_lang,
        "moeda": currency_info["moeda"],
        "simbolo_moeda": currency_info["simbolo"],
    }

    try:
        with st.spinner(tr("loading")):
            response = gerar_diagnostico_api(payload)

        st.session_state.last_payload = payload
        st.session_state.last_response = response

        st.success(tr("saved"))

    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar na FastAPI. "
            "Confirme se a API está rodando em http://127.0.0.1:8000."
        )

    except requests.exceptions.Timeout:
        st.error("A API demorou muito para responder. Tente novamente.")

    except requests.exceptions.HTTPError as error:
        st.error(f"Erro HTTP ao chamar a API: {error}")

    except Exception as error:
        st.error(f"Erro inesperado ao gerar diagnóstico: {error}")


if st.session_state.last_response:
    response = st.session_state.last_response

    st.success(tr("success"))

    col1, col2, col3 = st.columns(3)

    col1.metric(
        tr("estimated_balance"),
        format_currency_app(
            response["saldo_estimado"],
            response.get("simbolo_moeda", current_currency_info["simbolo"]),
            response.get("moeda", current_currency_info["moeda"]),
        ),
    )

    col2.metric(
        tr("financial_score"),
        f"{response['score_financeiro']}/100",
    )

    col3.metric(
        tr("risk"),
        translate_risk_app(response["nivel_risco"]),
    )

    st.write(tr("diagnosis"))
    diagnostico_formatado = response["diagnostico"].replace("$", "\\$")
    st.markdown(diagnostico_formatado)

    st.write(tr("plan"))
    plano_formatado = response["plano_30_dias"].replace("$", "\\$")
    st.markdown(plano_formatado)

    st.divider()

    diagnostico_id = response.get("id")

    if diagnostico_id:
        try:
            pdf_bytes = baixar_relatorio_pdf_api(diagnostico_id)

            st.download_button(
                label=tr("download_pdf"),
                data=pdf_bytes,
                file_name=f"relatorio_inna_{response['nome'].replace(' ', '_').lower()}_{diagnostico_id}.pdf",
                mime="application/pdf",
            )

        except Exception as error:
            st.warning(f"{tr('pdf_error')}: {error}")

        st.markdown(tr("email_title"))

        email_destino = st.text_input(
            tr("email_input"),
            placeholder="seuemail@gmail.com",
            key=f"email_destino_{diagnostico_id}",
        )

        if st.button(tr("email_button"), key=f"btn_email_{diagnostico_id}"):
            if not email_destino or "@" not in email_destino or "." not in email_destino:
                st.warning(tr("email_invalid"))
            else:
                try:
                    currency_info = CURRENCY_BY_LANG.get(app_lang, CURRENCY_BY_LANG["pt"])
                    enviar_relatorio_email(
                        diagnostico_id,
                        email_destino,
                        idioma=app_lang,
                        moeda=currency_info["moeda"],
                        simbolo_moeda=currency_info["simbolo"],
                    )
                    st.success(tr("email_success"))
                except Exception as error:
                    st.error(f"{tr('email_error')}: {error}")

    else:
        st.warning(tr("pdf_unavailable"))


    st.divider()

    st.write(tr("feedback_title"))
    st.caption(tr("feedback_help"))

    with st.form("feedback_form"):
        util = st.radio(
            tr("feedback_question"),
            [tr("yes"), tr("no")],
            horizontal=True,
        )

        comentario = st.text_area(
            tr("feedback_comment"),
            placeholder=tr("feedback_placeholder"),
        )

        feedback_submitted = st.form_submit_button(tr("feedback_button"))

    if feedback_submitted:
        feedback_payload = {
            "nome": response["nome"],
            "util": util,
            "comentario": comentario,
            "score_financeiro": response["score_financeiro"],
            "nivel_risco": translate_risk_app(response["nivel_risco"]),
        }

        try:
            enviar_feedback_api(feedback_payload)
            st.success(tr("feedback_success"))

        except requests.exceptions.ConnectionError:
            st.error(
                "Não foi possível conectar na FastAPI para enviar o feedback. "
                "Confirme se a API está rodando."
            )

        except Exception as error:
            st.error(f"Erro ao enviar feedback pela API: {error}")


st.divider()

st.write("## 📚 " + tr("history_title").replace("### ", ""))

st.caption(tr("history_help"))

with st.form("historico_form"):
    nome_historico = st.text_input(
        tr("history_name"),
        value="Ronaldo",
    )

    limite_historico = st.number_input(
        tr("history_limit"),
        min_value=1,
        max_value=20,
        value=10,
        step=1,
    )

    buscar_historico = st.form_submit_button(tr("history_button"))

if buscar_historico:
    try:
        historico = buscar_historico_usuario_api(
            nome=nome_historico,
            limit=int(limite_historico),
        )

        if not historico:
            st.warning(tr("history_empty"))
        else:
            st.success(f"{len(historico)} diagnóstico(s) encontrado(s).")

            historico_ordenado = sorted(
                historico,
                key=lambda item: item["id"],
            )

            score_data = {
                item["id"]: item["score_financeiro"]
                for item in historico_ordenado
            }

            st.write("### Evolução do score")
            st.line_chart(score_data)

            st.write("### Diagnósticos encontrados")

            for item in historico:
                with st.expander(
                    f"ID {item['id']} — {item['nome']} — {tr('history_score')} {item['score_financeiro']}/100 — {tr('risk')} {translate_risk_app(item['nivel_risco'])}"
                ):
                    st.write(
                        f"**{tr('estimated_balance')}:** "
                        f"{format_currency_app(item['saldo_estimado'], item.get('simbolo_moeda', current_currency_info['simbolo']), item.get('moeda', current_currency_info['moeda']))}"
                    )
                    st.write(f"**{tr('income_commitment')}:** {item['comprometimento_renda_percentual']:.2f}%")
                    st.write(f"**{tr('reserve_months')}:** {item['meses_reserva_estimados']:.2f}")
                    st.write(f"**{tr('goal')}:** {item.get('objetivo', '')}")

                    st.write(f"**{tr('diagnosis')}:**")
                    st.write(item["diagnostico"])

                    try:
                        pdf_antigo = baixar_relatorio_pdf_api(item["id"])

                        st.download_button(
                            label=f"📄 Baixar PDF do diagnóstico {item['id']}",
                            data=pdf_antigo,
                            file_name=f"relatorio_inna_{item['nome'].replace(' ', '_').lower()}_{item['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_historico_{item['id']}",
                        )
                    except Exception as error:
                        st.warning(f"Não foi possível gerar PDF do histórico: {error}")

    except Exception as error:
        st.error(f"Erro ao buscar histórico pela API: {error}")
