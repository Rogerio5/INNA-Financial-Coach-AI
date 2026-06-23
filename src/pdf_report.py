from io import BytesIO
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


PDF_TEXTS = {
    "pt": {
        "report_title": "Relatório de Diagnóstico Financeiro",
        "field": "Campo",
        "value": "Valor",
        "name": "Nome",
        "date": "Data de geração",
        "balance": "Saldo estimado",
        "score": "Score financeiro",
        "risk": "Nível de risco",
        "income_commitment": "Comprometimento da renda",
        "reserve_months": "Meses estimados de reserva",
        "diagnosis": "Diagnóstico",
        "action_plan": "Plano de Ação de 30 Dias",
        "important_notice": "Aviso Importante",
        "notice_text": "A INNA atua como educadora financeira digital. Ela não recomenda compra ou venda de ativos, não promete rentabilidade e não substitui profissionais certificados.",
        "approx": "aprox.",
        "days": "dias",
        "months": "mês(es)",
    },
    "fr": {
        "report_title": "Rapport de diagnostic financier",
        "field": "Champ",
        "value": "Valeur",
        "name": "Nom",
        "date": "Date de génération",
        "balance": "Solde estimé",
        "score": "Score financier",
        "risk": "Niveau de risque",
        "income_commitment": "Engagement du revenu",
        "reserve_months": "Mois estimés d’épargne",
        "diagnosis": "Diagnostic",
        "action_plan": "Plan d’action de 30 jours",
        "important_notice": "Avis important",
        "notice_text": "INNA agit comme éducatrice financière numérique. Elle ne recommande pas l’achat ou la vente d’actifs, ne promet pas de rentabilité et ne remplace pas des professionnels certifiés.",
        "approx": "env.",
        "days": "jours",
        "months": "mois",
    },
    "en_us": {
        "report_title": "Financial Diagnosis Report",
        "field": "Field",
        "value": "Value",
        "name": "Name",
        "date": "Generation date",
        "balance": "Estimated balance",
        "score": "Financial score",
        "risk": "Risk level",
        "income_commitment": "Income commitment",
        "reserve_months": "Estimated savings months",
        "diagnosis": "Diagnosis",
        "action_plan": "30-Day Action Plan",
        "important_notice": "Important Notice",
        "notice_text": "INNA acts as a digital financial educator. It does not recommend buying or selling assets, does not promise returns, and does not replace certified professionals.",
        "approx": "approx.",
        "days": "days",
        "months": "month(s)",
    },
    "en_gb": {
        "report_title": "Financial Diagnosis Report",
        "field": "Field",
        "value": "Value",
        "name": "Name",
        "date": "Generation date",
        "balance": "Estimated balance",
        "score": "Financial score",
        "risk": "Risk level",
        "income_commitment": "Income commitment",
        "reserve_months": "Estimated savings months",
        "diagnosis": "Diagnosis",
        "action_plan": "30-Day Action Plan",
        "important_notice": "Important Notice",
        "notice_text": "INNA acts as a digital financial educator. It does not recommend buying or selling assets, does not promise returns, and does not replace certified professionals.",
        "approx": "approx.",
        "days": "days",
        "months": "month(s)",
    },
    "de": {
        "report_title": "Finanzdiagnosebericht",
        "field": "Feld",
        "value": "Wert",
        "name": "Name",
        "date": "Erstellungsdatum",
        "balance": "Geschätzter Überschuss",
        "score": "Finanzscore",
        "risk": "Risikostufe",
        "income_commitment": "Einkommensbindung",
        "reserve_months": "Geschätzte Rücklagenmonate",
        "diagnosis": "Diagnose",
        "action_plan": "30-Tage-Aktionsplan",
        "important_notice": "Wichtiger Hinweis",
        "notice_text": "INNA agiert als digitale Finanzbildnerin. Sie empfiehlt keinen Kauf oder Verkauf von Vermögenswerten, verspricht keine Rendite und ersetzt keine zertifizierten Fachleute.",
        "approx": "ca.",
        "days": "Tage",
        "months": "Monat(e)",
    },
    "es": {
        "report_title": "Relatório de Diagnóstico Financeiro",
        "field": "Campo",
        "value": "Valor",
        "name": "Nome",
        "date": "Data de geração",
        "balance": "Saldo estimado",
        "score": "Score financeiro",
        "risk": "Nível de risco",
        "income_commitment": "Comprometimento da renda",
        "reserve_months": "Meses estimados de reserva",
        "diagnosis": "Diagnóstico",
        "action_plan": "Plano de Ação de 30 Dias",
        "important_notice": "Aviso Importante",
        "notice_text": "A INNA atua como educadora financeira digital. Ela não recomenda compra ou venda de ativos, não promete rentabilidade e não substitui profissionais certificados.",
        "approx": "aprox.",
        "days": "días",
        "months": "mes(es)",
    },
    "it": {
        "report_title": "Rapporto di diagnosi finanziaria",
        "field": "Campo",
        "value": "Valore",
        "name": "Nome",
        "date": "Data di generazione",
        "balance": "Saldo stimato",
        "score": "Punteggio finanziario",
        "risk": "Livello di rischio",
        "income_commitment": "Impegno del reddito",
        "reserve_months": "Mesi stimati di riserva",
        "diagnosis": "Diagnosi",
        "action_plan": "Piano d’azione di 30 giorni",
        "important_notice": "Avviso importante",
        "notice_text": "INNA agisce come educatrice finanziaria digitale. Non raccomanda l’acquisto o la vendita di asset, non promette rendimenti e non sostituisce professionisti certificati.",
        "approx": "circa",
        "days": "giorni",
        "months": "mese/i",
    },
    "ro": {
        "report_title": "Raport de diagnostic financiar",
        "field": "Câmp",
        "value": "Valoare",
        "name": "Nume",
        "date": "Data generării",
        "balance": "Sold estimat",
        "score": "Scor financiar",
        "risk": "Nivel de risc",
        "income_commitment": "Grad de angajare a venitului",
        "reserve_months": "Luni estimate de rezervă",
        "diagnosis": "Diagnostic",
        "action_plan": "Plan de acțiune pe 30 de zile",
        "important_notice": "Avertisment important",
        "notice_text": "INNA acționează ca educator financiar digital. Nu recomandă cumpărarea sau vânzarea de active, nu promite randamente și nu înlocuiește profesioniștii certificați.",
        "approx": "aprox.",
        "days": "zile",
        "months": "lună/luni",
    },

    "ru": {
        "report_title": "Отчёт финансовой диагностики",
        "field": "Поле",
        "value": "Значение",
        "name": "Имя",
        "date": "Дата создания",
        "balance": "Оценочный баланс",
        "score": "Финансовый балл",
        "risk": "Уровень риска",
        "income_commitment": "Нагрузка на доход",
        "reserve_months": "Оценка резерва",
        "diagnosis": "Диагностика",
        "action_plan": "План действий на 30 дней",
        "important_notice": "Важное уведомление",
        "notice_text": "INNA является цифровым финансовым помощником. Она не рекомендует покупку или продажу активов, не обещает доходность и не заменяет сертифицированных специалистов.",
        "approx": "примерно",
        "days": "дней",
        "months": "мес.",
    },
    "uk": {
        "report_title": "Звіт фінансової діагностики",
        "field": "Поле",
        "value": "Значення",
        "name": "Ім’я",
        "date": "Дата створення",
        "balance": "Орієнтовний баланс",
        "score": "Фінансовий бал",
        "risk": "Рівень ризику",
        "income_commitment": "Навантаження на дохід",
        "reserve_months": "Оцінка резерву",
        "diagnosis": "Діагностика",
        "action_plan": "План дій на 30 днів",
        "important_notice": "Важливе повідомлення",
        "notice_text": "INNA є цифровим фінансовим освітнім помічником. Вона не рекомендує купівлю чи продаж активів, не обіцяє прибутковість і не замінює сертифікованих фахівців.",
        "approx": "приблизно",
        "days": "днів",
        "months": "міс.",
    },
    "ar": {
        "report_title": "تقرير التشخيص المالي",
        "field": "الحقل",
        "value": "القيمة",
        "name": "الاسم",
        "date": "تاريخ الإنشاء",
        "balance": "الرصيد التقديري",
        "score": "الدرجة المالية",
        "risk": "مستوى المخاطر",
        "income_commitment": "نسبة الالتزام من الدخل",
        "reserve_months": "تقدير الاحتياطي",
        "diagnosis": "التشخيص",
        "action_plan": "خطة عمل لمدة 30 يومًا",
        "important_notice": "تنبيه مهم",
        "notice_text": "تعمل INNA كمثقفة مالية رقمية. لا توصي بشراء أو بيع الأصول، ولا تعد بعوائد، ولا تحل محل المختصين المعتمدين.",
        "approx": "تقريبًا",
        "days": "أيام",
        "months": "شهر",
    },

}



RISK_TRANSLATIONS = {
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

def get_pdf_font_name() -> str:
    possible_paths = [
        "fonts/DejaVuSans.ttf",
        "assets/DejaVuSans.ttf",
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]

    for font_path in possible_paths:
        try:
            candidate = Path(font_path)
            if candidate.exists():
                pdfmetrics.registerFont(TTFont("INNAUnicode", str(candidate)))
                return "INNAUnicode"
        except Exception:
            continue

    return "Helvetica"






def force_pdf_language(diagnostico: dict) -> str:
    idioma = str(diagnostico.get("idioma") or "").lower().strip()

    conteudo = (
        str(diagnostico.get("diagnostico", "")) + " " +
        str(diagnostico.get("plano_30_dias", ""))
    ).lower()

    # Idiomas com alfabetos específicos
    if any("\u0600" <= ch <= "\u06ff" for ch in conteudo):
        return "ar"

    if any(ch in conteudo for ch in "іїєґ"):
        return "uk"

    if any(ch in conteudo for ch in "абвгдежзийклмнопрстуфхцчшщыэюя"):
        return "ru"

    # Detecta alemão mesmo se o campo idioma vier errado como pt
    german_markers = [
        "finanzdiagnose", "finanzscore", "risikostufe", "rücklage",
        "einkommensbindung", "monatlicher überschuss", "woche",
        "wichtiger hinweis", "auf grundlage", "schulden"
    ]
    if any(marker in conteudo for marker in german_markers):
        return "de"

    french_markers = ["diagnostic financier", "semaine", "épargne", "revenu", "avis important"]
    if any(marker in conteudo for marker in french_markers):
        return "fr"

    spanish_markers = ["diagnóstico financiero", "semana", "ingresos", "aviso importante"]
    if any(marker in conteudo for marker in spanish_markers):
        return "es"

    italian_markers = ["diagnosi finanziaria", "settimana", "reddito", "avviso importante"]
    if any(marker in conteudo for marker in italian_markers):
        return "it"

    romanian_markers = ["diagnostic financiar", "săptămâna", "venit", "avertisment important"]
    if any(marker in conteudo for marker in romanian_markers):
        return "ro"

    if idioma == "ch":
        return "de"

    return idioma or "pt"


def get_currency_by_language_pdf(idioma: str) -> dict:
    currencies = {
        "pt": {"moeda": "BRL", "simbolo": "R$"},
        "en_us": {"moeda": "USD", "simbolo": "US$"},
        "en_gb": {"moeda": "GBP", "simbolo": "£"},
        "es": {"moeda": "EUR", "simbolo": "€"},
        "de": {"moeda": "EUR", "simbolo": "€"},
        "ch": {"moeda": "CHF", "simbolo": "CHF"},
        "fr": {"moeda": "EUR", "simbolo": "€"},
        "it": {"moeda": "EUR", "simbolo": "€"},
        "ro": {"moeda": "RON", "simbolo": "RON"},
        "uk": {"moeda": "UAH", "simbolo": "₴"},
        "ru": {"moeda": "RUB", "simbolo": "₽"},
        "ar": {"moeda": "SAR", "simbolo": "SAR"},
    }

    return currencies.get(idioma, currencies["pt"])


def format_money(value, symbol="R$", currency="BRL") -> str:
    try:
        number = float(value)
    except Exception:
        number = 0.0

    if currency in ["USD", "GBP"]:
        return f"{symbol}{number:,.2f}"

    if currency == "CHF":
        return f"{symbol} {number:,.2f}".replace(",", "'")

    if currency in ["EUR", "BRL", "RON", "UAH", "RUB"]:
        formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{symbol} {formatted}"

    return f"{symbol} {number:,.2f}"


def normalizar_texto_pdf(texto: str) -> str:
    if not texto:
        return ""
    return str(texto).replace("\n", "<br/>")



def translate_risk_pdf(risk: str, idioma: str) -> str:
    risk_raw = str(risk or "").strip().lower()
    idioma = str(idioma or "pt").lower().strip()

    # Normaliza entradas em vários idiomas para um código técnico
    low_values = {"baixo", "bajo", "low", "faible", "niedrig", "basso", "scăzut", "низкий", "низький", "منخفض"}
    medium_values = {"medio", "médio", "medium", "moyen", "mittel", "mediu", "средний", "середній", "متوسط"}
    high_values = {"alto", "high", "élevé", "eleve", "hoch", "ridicat", "высокий", "високий", "مرتفع"}

    if risk_raw in low_values:
        code = "low"
    elif risk_raw in medium_values:
        code = "medium"
    elif risk_raw in high_values:
        code = "high"
    else:
        return risk or ""

    translations = {
        "low": {
            "pt": "Baixo", "en_us": "Low", "en_gb": "Low", "es": "Bajo",
            "fr": "Faible", "de": "Niedrig", "ch": "Niedrig", "it": "Basso",
            "ro": "Scăzut", "uk": "Низький", "ru": "Низкий", "ar": "منخفض",
        },
        "medium": {
            "pt": "Médio", "en_us": "Medium", "en_gb": "Medium", "es": "Medio",
            "fr": "Moyen", "de": "Mittel", "ch": "Mittel", "it": "Medio",
            "ro": "Mediu", "uk": "Середній", "ru": "Средний", "ar": "متوسط",
        },
        "high": {
            "pt": "Alto", "en_us": "High", "en_gb": "High", "es": "Alto",
            "fr": "Élevé", "de": "Hoch", "ch": "Hoch", "it": "Alto",
            "ro": "Ridicat", "uk": "Високий", "ru": "Высокий", "ar": "مرتفع",
        },
    }

    return translations[code].get(idioma, translations[code]["pt"])



def force_currency_for_pdf_language(diagnostico: dict, idioma: str, moeda: str, simbolo: str) -> tuple[str, str]:
    diagnostico_texto = str(diagnostico.get("diagnostico", "")).lower()
    plano_texto = str(diagnostico.get("plano_30_dias", "")).lower()

    is_pt_report = (
        idioma == "pt"
        or "seu saldo estimado" in diagnostico_texto
        or "plano de ação" in plano_texto
        or "diagnóstico" in diagnostico_texto
    )

    if is_pt_report:
        return "BRL", "R$"

    return moeda, simbolo



def gerar_relatorio_pdf(diagnostico: dict) -> bytes:
    buffer = BytesIO()

    idioma = force_pdf_language(diagnostico)
    if idioma == "ch":
        idioma = "de"

    if idioma == "ch":
        idioma = "de"

    textos = PDF_TEXTS.get(idioma, PDF_TEXTS["pt"])

    currency_default = get_currency_by_language_pdf(idioma)
    moeda = diagnostico.get("moeda") or currency_default["moeda"]
    simbolo = diagnostico.get("simbolo_moeda") or currency_default["simbolo"]

    moeda, simbolo = force_currency_for_pdf_language(diagnostico, idioma, moeda, simbolo)

    # Regra principal:
    # pt = Brasil = BRL/R$
    # Se o relatório estiver em português, nunca usar moeda estrangeira na tabela.
    if idioma == "pt":
        moeda = "BRL"
        simbolo = "R$"

    # Para relatórios internacionais antigos salvos sem moeda correta,
    # troca BRL pelo padrão do idioma selecionado.
    elif moeda == "BRL" and simbolo == "R$":
        moeda = currency_default["moeda"]
        simbolo = currency_default["simbolo"]

    nome = diagnostico.get("nome", "Usuário")
    saldo = diagnostico.get("saldo_estimado", 0)
    score = diagnostico.get("score_financeiro", 0)
    risco_original = diagnostico.get("nivel_risco", "-")
    risco = translate_risk_pdf(risco_original, idioma)

    comprometimento = diagnostico.get("comprometimento_renda_percentual", 0)
    meses_reserva = diagnostico.get("meses_reserva_estimados", 0)
    dias_reserva = float(meses_reserva or 0) * 30

    diagnostico_texto = diagnostico.get("diagnostico", "")
    plano_30_dias = diagnostico.get("plano_30_dias", "")

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    base_font = get_pdf_font_name()

    title_style = ParagraphStyle(
        "INNATitle",
        parent=styles["Title"],
        fontName=base_font,
        fontSize=16,
        leading=20,
        alignment=1,
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "INNAHeading",
        parent=styles["Heading2"],
        fontName=base_font,
        fontSize=12,
        leading=15,
        spaceBefore=12,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "INNANormal",
        parent=styles["BodyText"],
        fontName=base_font,
        fontSize=8.5,
        leading=11,
        spaceAfter=6,
    )

    elements = []

    elements.append(Paragraph("INNA Financial Coach AI", title_style))
    elements.append(Paragraph(textos["report_title"], heading_style))

    data_geracao = diagnostico.get("data_geracao") or diagnostico.get("created_at") or diagnostico.get("data_hora") or diagnostico.get("data_hora")
    if not data_geracao:
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

    table_data = [
        [textos["field"], textos["value"]],
        [textos["name"], str(nome)],
        [textos["date"], str(data_geracao)],
        [textos["balance"], format_money(saldo, simbolo, moeda)],
        [textos["score"], f"{score}/100"],
        [textos["risk"], str(risco)],
        [textos["income_commitment"], f"{float(comprometimento):.2f}%"],
        [
            textos["reserve_months"],
            f"{float(meses_reserva):.2f} {textos['months']} - {textos['approx']} {dias_reserva:.0f} {textos['days']}",
        ],
    ]

    table = Table(table_data, colWidths=[6.5 * cm, 10.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), base_font),
                ("FONTNAME", (0, 1), (-1, -1), base_font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )

    elements.append(Spacer(1, 8))
    elements.append(table)

    elements.append(Paragraph(textos["diagnosis"], heading_style))
    elements.append(Paragraph(normalizar_texto_pdf(diagnostico_texto), normal_style))

    elements.append(Paragraph(textos["action_plan"], heading_style))
    elements.append(Paragraph(normalizar_texto_pdf(plano_30_dias), normal_style))

    elements.append(Paragraph(textos["important_notice"], heading_style))
    elements.append(Paragraph(textos["notice_text"], normal_style))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
