from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.evaluation.financial_knowledge_chunking_tuned import (
    create_tuned_chunking_report,
    tuned_lexical_search,
)

OFFICIAL_CASES = (
    (
        "reserva-financeira-001",
        "Como montar uma reserva financeira?",
        "reserva_de_emergencia",
    ),
    (
        "orcamento-mensal-001",
        "Como organizar renda e despesas mensais?",
        "orcamento_pessoal",
    ),
    (
        "cartao-credito-001",
        "Como usar cartao de credito sem me endividar?",
        "cartao_de_credito",
    ),
    (
        "dividas-priorizacao-001",
        "Qual divida devo pagar primeiro?",
        "priorizacao_de_dividas",
    ),
    (
        "gastos-fixos-variaveis-001",
        "Qual a diferenca entre gastos fixos e variaveis?",
        "classificacao_de_gastos",
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    report = create_tuned_chunking_report(
        root=args.root.resolve(),
        minimum_words=70,
        target_words=130,
        maximum_words=190,
    )

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunks_path = args.output / "financial_knowledge_tuned_chunks.json"

    report_path = args.output / "financial_knowledge_tuned_report.json"

    lexical_path = args.output / "financial_knowledge_tuned_lexical.json"

    chunk_payloads = [chunk.as_dict() for chunk in report.chunks]

    chunks_path.write_text(
        json.dumps(
            chunk_payloads,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_payload = report.as_dict()
    report_payload["chunks"] = []

    report_path.write_text(
        json.dumps(
            report_payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lexical_cases = []
    top1_correct = 0

    for case_id, question, expected_topic in OFFICIAL_CASES:
        results = tuned_lexical_search(
            query=question,
            chunks=report.chunks,
            top_k=4,
        )

        top1_topic = results[0][0].topic if results else None

        top1_is_correct = top1_topic == expected_topic

        if top1_is_correct:
            top1_correct += 1

        lexical_cases.append(
            {
                "case_id": case_id,
                "question": question,
                "expected_topic": expected_topic,
                "top1_topic": top1_topic,
                "top1_correct": top1_is_correct,
                "results": [
                    {
                        "rank": rank,
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "topic": chunk.topic,
                        "score": score,
                        "word_count": chunk.word_count,
                    }
                    for rank, (
                        chunk,
                        score,
                    ) in enumerate(
                        results,
                        start=1,
                    )
                ],
            }
        )

    lexical_report = {
        "case_count": len(lexical_cases),
        "top1_correct_count": top1_correct,
        "top1_accuracy": (top1_correct / len(lexical_cases)),
        "passed": (top1_correct == len(lexical_cases)),
        "cases": lexical_cases,
    }

    lexical_path.write_text(
        json.dumps(
            lexical_report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"DOCUMENT_COUNT={report.document_count}")
    print(f"CHUNK_COUNT={report.chunk_count}")
    print(f"EDUCATION_CHUNK_COUNT={report.education_chunk_count}")
    print(f"SECURITY_CHUNK_COUNT={report.security_chunk_count}")
    print(f"MINIMUM_CHUNK_WORDS={report.minimum_chunk_words}")
    print(f"MAXIMUM_CHUNK_WORDS={report.maximum_chunk_words}")
    print(f"MEAN_CHUNK_WORDS={report.mean_chunk_words:.3f}")
    print(f"DUPLICATE_CHUNK_COUNT={report.duplicate_chunk_count}")
    print(f"TOP1_CORRECT_COUNT={lexical_report['top1_correct_count']}")
    print(f"TOP1_ACCURACY={lexical_report['top1_accuracy']:.6f}")
    print(f"LEXICAL_VALIDATION_PASSED={lexical_report['passed']}")

    for case in lexical_cases:
        print(
            "CASE="
            f"{case['case_id']}"
            f"|EXPECTED={case['expected_topic']}"
            f"|TOP1={case['top1_topic']}"
            f"|CORRECT={case['top1_correct']}"
        )

    print(f"CHUNKS_JSON={chunks_path}")
    print(f"REPORT_JSON={report_path}")
    print(f"LEXICAL_JSON={lexical_path}")
    print("NEON_USED=False")
    print("GEMINI_USED=False")
    print("DATABASE_WRITE_EXECUTED=False")

    if report.document_count != 16:
        return 1

    if report.chunk_count >= 80:
        return 2

    if report.minimum_chunk_words < 70:
        return 3

    if report.mean_chunk_words < 90:
        return 4

    if report.duplicate_chunk_count != 0:
        return 5

    if not lexical_report["passed"]:
        return 6

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
