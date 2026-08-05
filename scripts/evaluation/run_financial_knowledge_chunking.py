"""Executa o chunking local da base financeira profissional."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.evaluation.financial_knowledge_chunking import (
    create_chunking_report,
    validate_official_questions,
    write_chunking_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Gera chunks locais da base financeira sem Neon e sem Gemini.")
    )

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
    parser.add_argument(
        "--minimum-words",
        type=int,
        default=45,
    )
    parser.add_argument(
        "--target-words",
        type=int,
        default=110,
    )
    parser.add_argument(
        "--maximum-words",
        type=int,
        default=180,
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    report = create_chunking_report(
        root=args.root.resolve(),
        minimum_words=args.minimum_words,
        target_words=args.target_words,
        maximum_words=args.maximum_words,
    )

    output_paths = write_chunking_outputs(
        report=report,
        output_directory=args.output,
    )

    lexical_validation = validate_official_questions(report.chunks)

    lexical_report_path = args.output / "financial_knowledge_lexical_validation.json"

    lexical_report_path.write_text(
        json.dumps(
            lexical_validation,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"DOCUMENT_COUNT={report.document_count}")
    print(f"CHUNK_COUNT={report.chunk_count}")
    print(f"EDUCATION_DOCUMENT_COUNT={report.education_document_count}")
    print(f"SECURITY_DOCUMENT_COUNT={report.security_document_count}")
    print(f"EDUCATION_CHUNK_COUNT={report.education_chunk_count}")
    print(f"SECURITY_CHUNK_COUNT={report.security_chunk_count}")
    print(f"MINIMUM_CHUNK_WORDS={report.minimum_chunk_words}")
    print(f"MAXIMUM_CHUNK_WORDS={report.maximum_chunk_words}")
    print(f"MEAN_CHUNK_WORDS={report.mean_chunk_words:.3f}")
    print(f"DUPLICATE_CHUNK_COUNT={report.duplicate_chunk_count}")
    print(f"OFFICIAL_QUESTION_COUNT={lexical_validation['case_count']}")
    print(f"OFFICIAL_QUESTION_HIT_COUNT={lexical_validation['hit_count']}")
    print(f"OFFICIAL_QUESTION_HIT_RATE={lexical_validation['hit_rate']:.6f}")
    print(f"LEXICAL_VALIDATION_PASSED={lexical_validation['passed']}")

    for case in lexical_validation["cases"]:
        print("")
        print(
            "CASE="
            f"{case['case_id']}"
            f"|EXPECTED_TOPIC={case['expected_topic']}"
            f"|HIT={case['hit']}"
        )

        for result in case["results"]:
            print(
                "RESULT="
                f"RANK={result['rank']}"
                f"|TOPIC={result['topic']}"
                f"|CHUNK_ID={result['chunk_id']}"
                f"|SCORE={result['score']}"
            )

    print("")
    print(f"CHUNKS_JSON={output_paths['json']}")
    print(f"CHUNKS_JSONL={output_paths['jsonl']}")
    print(f"CHUNKING_REPORT={output_paths['report']}")
    print(f"LEXICAL_REPORT={lexical_report_path}")
    print("NEON_USED=False")
    print("GEMINI_USED=False")
    print("DATABASE_WRITE_EXECUTED=False")

    if report.document_count != 16:
        return 1

    if report.duplicate_chunk_count != 0:
        return 2

    if not lexical_validation["passed"]:
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
