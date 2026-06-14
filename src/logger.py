from pathlib import Path
from datetime import datetime
import csv

DATA_PATH = Path("data/interacoes.csv")


def save_interaction(user_data: dict, response: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_exists = DATA_PATH.exists()

    with DATA_PATH.open("a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "data_hora",
            "nome",
            "renda_mensal",
            "saldo_estimado",
            "score_financeiro",
            "nivel_risco",
            "objetivo",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "data_hora": datetime.now().isoformat(timespec="seconds"),
            "nome": user_data.get("nome"),
            "renda_mensal": user_data.get("renda_mensal"),
            "saldo_estimado": response.get("saldo_estimado"),
            "score_financeiro": response.get("score_financeiro"),
            "nivel_risco": response.get("nivel_risco"),
            "objetivo": user_data.get("objetivo"),
        })
