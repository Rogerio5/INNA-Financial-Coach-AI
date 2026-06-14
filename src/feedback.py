from pathlib import Path
from datetime import datetime
import csv

FEEDBACK_PATH = Path("data/feedbacks.csv")


def save_feedback(nome: str, util: str, comentario: str, score_financeiro: int, nivel_risco: str) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_exists = FEEDBACK_PATH.exists()

    with FEEDBACK_PATH.open("a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "data_hora",
            "nome",
            "util",
            "comentario",
            "score_financeiro",
            "nivel_risco",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "data_hora": datetime.now().isoformat(timespec="seconds"),
            "nome": nome,
            "util": util,
            "comentario": comentario,
            "score_financeiro": score_financeiro,
            "nivel_risco": nivel_risco,
        })
