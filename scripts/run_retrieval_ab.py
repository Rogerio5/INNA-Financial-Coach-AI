from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.evaluation.retrieval_ab import (
    run_retrieval_ab_suite,
)


def _load_questions(
    path: Path,
) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        payload: Any = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        if isinstance(
            payload,
            list,
        ):
            return [str(item) for item in payload]

        if isinstance(
            payload,
            dict,
        ):
            questions = payload.get(
                "questions",
                payload.get(
                    "perguntas",
                    [],
                ),
            )

            if isinstance(
                questions,
                list,
            ):
                return [str(item) for item in questions]

        raise ValueError("JSON deve ser uma lista ou conter questions/perguntas.")

    if suffix == ".jsonl":
        questions: list[str] = []

        for line in path.read_text(
            encoding="utf-8",
        ).splitlines():
            rendered = line.strip()

            if not rendered:
                continue

            item = json.loads(rendered)

            if isinstance(
                item,
                str,
            ):
                questions.append(item)

            elif isinstance(
                item,
                dict,
            ):
                question = item.get("question") or item.get("pergunta")

                if question:
                    questions.append(str(question))

        return questions

    return [
        line.strip()
        for line in path.read_text(
            encoding="utf-8",
        ).splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compara o RAG híbrido atual da INNA com o Sentence-Window Retrieval."
        )
    )

    parser.add_argument(
        "--question",
        action="append",
        default=[],
        help=("Pergunta de avaliação. Pode ser usada mais de uma vez."),
    )

    parser.add_argument(
        "--questions-file",
        type=Path,
        help=("Arquivo JSON, JSONL ou TXT com perguntas."),
    )

    parser.add_argument(
        "--language",
        default="pt",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/evaluation/retrieval_ab"),
    )

    parser.add_argument(
        "--label",
        default="week3-sentence-window",
    )

    parser.add_argument(
        "--include-text-preview",
        action="store_true",
    )

    args = parser.parse_args()

    questions = list(args.question)

    if args.questions_file:
        questions.extend(_load_questions(args.questions_file))

    if not questions:
        parser.error("Informe --question ou --questions-file.")

    result = run_retrieval_ab_suite(
        queries=questions,
        language=args.language,
        top_k=args.top_k,
        output_directory=(args.output_dir),
        run_label=args.label,
        include_text_preview=(args.include_text_preview),
    )

    payload = result["payload"]

    print("RUN_ID=" + result["run_id"])

    print("QUESTIONS=" + str(payload["question_count"]))

    print("COMPLETED=" + str(payload["completed_count"]))

    print("FAILED=" + str(payload["failed_count"]))

    print("JSON_REPORT=" + result["json_path"])

    print("MARKDOWN_REPORT=" + result["markdown_path"])

    print("HISTORY=" + result["history_path"])

    print("QUALITY_DECISION=pending_rag_triad")

    print("WEEK3_RETRIEVAL_AB_RUN=OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
