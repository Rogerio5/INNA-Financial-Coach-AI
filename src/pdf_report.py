from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors


def gerar_relatorio_pdf(response: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    titulo = "INNA Financial Coach AI"
    subtitulo = "Relatorio de Diagnostico Financeiro"

    story.append(Paragraph(titulo, styles["Title"]))
    story.append(Paragraph(subtitulo, styles["Heading2"]))
    story.append(Spacer(1, 16))

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

    dados_principais = [
        ["Campo", "Valor"],
        ["Nome", str(response.get("nome", "Usuario"))],
        ["Data de geracao", data_geracao],
        ["Saldo estimado", f"R$ {float(response.get('saldo_estimado', 0)):.2f}"],
        ["Score financeiro", f"{response.get('score_financeiro', 0)}/100"],
        ["Nivel de risco", str(response.get("nivel_risco", "Indefinido"))],
        [
            "Comprometimento da renda",
            f"{float(response.get('comprometimento_renda_percentual', 0)):.2f}%",
        ],
        [
            "Meses estimados de reserva",
            f"{float(response.get('meses_reserva_estimados', 0)):.2f} mes(es) - aprox. {float(response.get('meses_reserva_estimados', 0)) * 30:.0f} dias",
        ],
    ]

    tabela = Table(dados_principais, colWidths=[180, 300])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(tabela)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Diagnostico", styles["Heading2"]))
    story.append(
        Paragraph(
            str(response.get("diagnostico", "Diagnostico nao informado.")),
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 16))

    story.append(Paragraph("Plano de Acao de 30 Dias", styles["Heading2"]))

    plano = str(response.get("plano_30_dias", "Plano nao informado."))
    plano_html = plano.replace("\n", "<br/>")

    story.append(Paragraph(plano_html, styles["BodyText"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Aviso Importante", styles["Heading2"]))
    story.append(
        Paragraph(
            "A INNA atua como educadora financeira digital. "
            "Ela nao recomenda compra ou venda de ativos, nao promete rentabilidade "
            "e nao substitui profissionais certificados.",
            styles["BodyText"],
        )
    )

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
