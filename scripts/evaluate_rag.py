from pathlib import Path
from datetime import datetime
import sys
import csv

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(".env", override=True)

from src.rag_engine import answer_with_rag


PERGUNTAS_TESTE = [
    {
        "categoria": "Reserva financeira",
        "pergunta": "como posso começar uma reserva financeira?",
        "esperado": "reserva"
    },
    {
        "categoria": "Cálculo controlado",
        "pergunta": "ganho 3000 gasto 2500 e guardo 100",
        "esperado": "calculo"
    },
    {
        "categoria": "Cartão de crédito",
        "pergunta": "cartão de crédito está me apertando",
        "esperado": "cartao"
    },
    {
        "categoria": "Organização de gastos",
        "pergunta": "como organizar gastos fixos e variáveis?",
        "esperado": "orcamento"
    },
    {
        "categoria": "Dívidas",
        "pergunta": "como sair das dívidas?",
        "esperado": "divida"
    },
    {
        "categoria": "Reserva emergencial",
        "pergunta": "o que é reserva de emergência?",
        "esperado": "reserva"
    },
    {
        "categoria": "Gastos pequenos",
        "pergunta": "gasto muito com pequenas compras, como posso organizar?",
        "esperado": "orcamento"
    },
    {
        "categoria": "Parcelas",
        "pergunta": "tenho muitas parcelas no cartão, por onde começo?",
        "esperado": "cartao"
    },
    {
        "categoria": "Segurança Financeira",
        "pergunta": "apareceu uma compra no meu cartão que eu não reconheço",
        "esperado": "seguranca"
    },
    {
        "categoria": "Segurança Financeira",
        "pergunta": "recebi um link dizendo que minha conta do banco será bloqueada",
        "esperado": "seguranca"
    },
    {
        "categoria": "Segurança Financeira",
        "pergunta": "fiz um pix errado, o que devo fazer?",
        "esperado": "seguranca"
    },
    {
        "categoria": "Segurança Financeira",
        "pergunta": "alguém pediu meu código do banco pelo whatsapp",
        "esperado": "seguranca"
    },
    {
        "categoria": "Segurança Financeira",
        "pergunta": "como me proteger de golpes financeiros?",
        "esperado": "seguranca"
    },
]


def avaliar_resposta(pergunta: str, esperado: str, resultado: dict) -> dict:
    resposta = (resultado.get("resposta") or "").lower()
    modo = resultado.get("modo") or ""
    fontes = resultado.get("fontes") or []

    pontos = 0
    criterios = []

    if "rag_hibrido" in modo:
        pontos += 2
        criterios.append("usa_rag_hibrido")

    if "rerank" in modo:
        pontos += 2
        criterios.append("usa_rerank")

    if esperado == "calculo":
        if "_gemini_answer" not in modo:
            pontos += 2
            criterios.append("calculo_controlado_sem_gemini")
        if "r$" in resposta and "meta" in resposta:
            pontos += 2
            criterios.append("calculo_com_meta")
    else:
        if "_gemini_answer" in modo:
            pontos += 2
            criterios.append("gemini_final")
        else:
            if "rag_hibrido" in modo and "rerank" in modo:
                pontos += 1
                criterios.append("fallback_rag_controlado")

        if len(fontes) > 0:
            pontos += 1
            criterios.append("tem_fontes")

    palavras_por_tema = {
        "reserva": ["reserva", "guardar", "imprevisto", "emergência", "emergencia"],
        "cartao": ["cartão", "cartao", "crédito", "credito", "parcelas"],
        "orcamento": ["gastos", "fixos", "variáveis", "variaveis", "organizar"],
        "divida": ["dívida", "divida", "dívidas", "dividas", "juros", "parcelas"],
        "calculo": ["r$", "meta", "semana", "guardar"],
        "seguranca": ["senha", "token", "código", "codigo", "cvv", "banco", "oficiais", "golpe", "pix", "cartão", "cartao"],
    }

    termos = palavras_por_tema.get(esperado, [])

    if any(termo in resposta for termo in termos):
        pontos += 2
        criterios.append("tema_correto")

    if "não substitui" in resposta or "orientação profissional" in resposta or "educativa" in resposta:
        pontos += 1
        criterios.append("seguranca_educativa")

    if len(resposta) >= 200:
        pontos += 1
        criterios.append("resposta_completa")

    if esperado in ["cartao", "orcamento", "divida", "reserva"] and "quer que eu monte uma meta" in resposta:
        pontos += 1
        criterios.append("pergunta_de_acao")

    if esperado == "cartao":
        termos_cartao_forte = ["parcelas", "fatura", "juros", "cartão", "cartao", "crédito", "credito"]
        encontrados_cartao = sum(1 for termo in termos_cartao_forte if termo in resposta)
        if encontrados_cartao >= 2:
            pontos += 1
            criterios.append("cartao_contexto_forte")

        termos_parcelas_pratico = ["parcelas", "fatura", "evitar", "organizar", "reduzir", "renda", "comprometido"]
        encontrados_parcelas = sum(1 for termo in termos_parcelas_pratico if termo in resposta)
        if "parcelas" in pergunta.lower() and encontrados_parcelas >= 3:
            pontos += 1
            criterios.append("parcelas_plano_pratico")

    nota = min(10, pontos)

    if nota >= 8:
        status = "APROVADO"
    elif nota >= 6:
        status = "ATENÇÃO"
    else:
        status = "REVISAR"

    return {
        "nota": nota,
        "status": status,
        "criterios": criterios,
    }


def main():
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linhas_md = []
    linhas_md.append("# Relatório de Avaliação do RAG — INNA")
    linhas_md.append("")
    linhas_md.append(f"Data da avaliação: **{agora}**")
    linhas_md.append("")
    linhas_md.append("## Objetivo")
    linhas_md.append("")
    linhas_md.append(
        "Avaliar a qualidade do RAG da INNA considerando busca híbrida, pgvector, busca textual, reranking, uso do Gemini quando adequado e fallback controlado para cálculos financeiros."
    )
    linhas_md.append("")
    linhas_md.append("## Resultados")
    linhas_md.append("")

    total = 0
    aprovados = 0
    atencao = 0
    revisar = 0
    resultados_csv = []

    for item in PERGUNTAS_TESTE:
        pergunta = item["pergunta"]
        categoria = item["categoria"]
        esperado = item["esperado"]

        print("\n==============================")
        print("PERGUNTA:", pergunta)

        resultado = answer_with_rag(pergunta, idioma="pt", top_k=3)
        avaliacao = avaliar_resposta(pergunta, esperado, resultado)

        total += 1

        if avaliacao["status"] == "APROVADO":
            aprovados += 1
        elif avaliacao["status"] == "ATENÇÃO":
            atencao += 1
        else:
            revisar += 1

        modo = resultado.get("modo")
        resposta = resultado.get("resposta") or ""
        fontes = resultado.get("fontes") or []

        print("MODO:", modo)
        print("NOTA:", avaliacao["nota"])
        print("STATUS:", avaliacao["status"])

        resultados_csv.append({
            "categoria": categoria,
            "pergunta": pergunta,
            "esperado": esperado,
            "modo": modo,
            "nota": avaliacao["nota"],
            "status": avaliacao["status"],
            "criterios": "; ".join(avaliacao["criterios"]),
            "fontes_total": len(fontes),
        })

        linhas_md.append(f"### {total}. {categoria}")
        linhas_md.append("")
        linhas_md.append(f"**Pergunta:** {pergunta}")
        linhas_md.append("")
        linhas_md.append(f"**Modo:** `{modo}`")
        linhas_md.append("")
        linhas_md.append(f"**Nota:** {avaliacao['nota']}/10")
        linhas_md.append("")
        linhas_md.append(f"**Status:** {avaliacao['status']}")
        linhas_md.append("")
        linhas_md.append(f"**Critérios atendidos:** {', '.join(avaliacao['criterios'])}")
        linhas_md.append("")
        linhas_md.append("**Fontes recuperadas:**")
        linhas_md.append("")

        if fontes:
            for fonte in fontes:
                linhas_md.append(
                    f"- {fonte.get('titulo')} | score: {fonte.get('score')} | fonte: `{fonte.get('fonte')}`"
                )
        else:
            linhas_md.append("- Nenhuma fonte retornada.")

        linhas_md.append("")
        linhas_md.append("**Resposta gerada:**")
        linhas_md.append("")
        linhas_md.append("> " + resposta.replace("\n", "\n> "))
        linhas_md.append("")
        linhas_md.append("---")
        linhas_md.append("")

    media = round((aprovados / total) * 100, 2) if total else 0

    resumo = [
        "# Resumo Executivo — Avaliação do RAG INNA",
        "",
        f"Total de perguntas avaliadas: **{total}**",
        f"Aprovadas: **{aprovados}**",
        f"Atenção: **{atencao}**",
        f"Revisar: **{revisar}**",
        f"Taxa de aprovação: **{media}%**",
        "",
        "## Interpretação",
        "",
        "A avaliação verifica se a INNA usa RAG híbrido, reranking, fontes recuperadas, resposta com Gemini quando adequado e fallback controlado em perguntas com cálculo.",
        "",
    ]

    linhas_md = resumo + ["---", ""] + linhas_md

    output_path = Path("reports/rag_evaluation_report.md")
    output_path.write_text("\n".join(linhas_md), encoding="utf-8")

    csv_path = Path("reports/rag_evaluation_results.csv")

    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "categoria",
            "pergunta",
            "esperado",
            "modo",
            "nota",
            "status",
            "criterios",
            "fontes_total",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados_csv)

    print("\n==============================")
    print("RELATÓRIO GERADO:")
    print(output_path)
    print("CSV GERADO:")
    print(csv_path)
    print(f"APROVADAS: {aprovados}/{total}")
    print(f"TAXA DE APROVAÇÃO: {media}%")


if __name__ == "__main__":
    main()
