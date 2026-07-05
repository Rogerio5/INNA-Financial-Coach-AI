from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(".env", override=True)

from src.rag_engine import get_rag_connection

report_path = Path("reports/rag_observability_report.md")

conn = get_rag_connection()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM inna_rag_logs;")
total_logs = cur.fetchone()[0]

cur.execute("""
SELECT modo, COUNT(*)
FROM inna_rag_logs
GROUP BY modo
ORDER BY COUNT(*) DESC;
""")
por_modo = cur.fetchall()

cur.execute("""
SELECT
    SUM(CASE WHEN usou_gemini THEN 1 ELSE 0 END),
    SUM(CASE WHEN usou_seguranca THEN 1 ELSE 0 END),
    SUM(CASE WHEN usou_fallback THEN 1 ELSE 0 END),
    ROUND(AVG(tempo_resposta_ms), 2),
    MAX(tempo_resposta_ms)
FROM inna_rag_logs;
""")
gemini, seguranca, fallback, tempo_medio, tempo_maximo = cur.fetchone()

cur.execute("""
SELECT pergunta, modo, tempo_resposta_ms, created_at
FROM inna_rag_logs
ORDER BY id DESC
LIMIT 10;
""")
ultimas = cur.fetchall()

cur.close()
conn.close()

linhas = []
linhas.append("# Relatório de Observabilidade — INNA RAG")
linhas.append("")
linhas.append(f"Gerado em: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
linhas.append("")
linhas.append("## Resumo")
linhas.append("")
linhas.append(f"- Total de logs: **{total_logs}**")
linhas.append(f"- Usaram Gemini: **{gemini or 0}**")
linhas.append(f"- Segurança Financeira: **{seguranca or 0}**")
linhas.append(f"- Fallback: **{fallback or 0}**")
linhas.append(f"- Tempo médio: **{tempo_medio or 0} ms**")
linhas.append(f"- Maior tempo: **{tempo_maximo or 0} ms**")
linhas.append("")
linhas.append("## Distribuição por modo")
linhas.append("")

for modo, qtd in por_modo:
    linhas.append(f"- `{modo}`: **{qtd}**")

linhas.append("")
linhas.append("## Últimas perguntas")
linhas.append("")

for pergunta, modo, tempo, created_at in ultimas:
    linhas.append(f"- **{created_at}** | `{modo}` | {tempo} ms")
    linhas.append(f"  - {pergunta}")

report_path.write_text("\n".join(linhas), encoding="utf-8")

print("RELATÓRIO GERADO:")
print(report_path)
print("TOTAL LOGS:", total_logs)
print("GEMINI:", gemini or 0)
print("SEGURANÇA:", seguranca or 0)
print("FALLBACK:", fallback or 0)
print("TEMPO MÉDIO:", tempo_medio or 0)
