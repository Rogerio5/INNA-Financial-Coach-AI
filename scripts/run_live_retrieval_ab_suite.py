from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from src.evaluation.deepeval_integration import (
    deepeval_availability,
)
from src.evaluation.live_retrieval_ab_suite import (
    LiveSuiteConfiguration,
    run_live_retrieval_ab_suite,
)


def _load_questions(
    path: Path,
) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

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
        questions = payload.get("questions") or payload.get("perguntas")

        if isinstance(
            questions,
            list,
        ):
            return [str(item) for item in questions]

    raise ValueError("O arquivo deve conter uma lista ou o campo questions/perguntas.")


def _configured(
    *names: str,
) -> bool:
    return any(
        bool(
            str(
                os.getenv(
                    name,
                    "",
                )
                or ""
            ).strip()
        )
        for name in names
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Executa o experimento real entre o RAG "
            "atual e Sentence-Window com RAG Triad."
        )
    )

    parser.add_argument(
        "--questions-file",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--language",
        default="pt",
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.005,
    )

    parser.add_argument(
        "--max-total-cost-per-variant",
        type=float,
        default=0.10,
    )

    parser.add_argument(
        "--max-median-latency-regression-ms",
        type=float,
        default=1000.0,
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
    )

    args = parser.parse_args()

    gemini_ready = _configured(
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GENAI_API_KEY",
    )

    database_ready = _configured(
        "DATABASE_URL",
        "NEON_DATABASE_URL",
    )

    print("GEMINI_CREDENTIALS_READY=" + str(gemini_ready))

    print("DATABASE_READY=" + str(database_ready))

    availability = deepeval_availability()

    print("DEEPEVAL_AVAILABILITY=" + str(availability))

    if not gemini_ready:
        raise RuntimeError("Nenhuma credencial Gemini foi encontrada.")

    if not database_ready:
        raise RuntimeError("Nenhuma conexão PostgreSQL/Neon foi encontrada.")

    questions = _load_questions(args.questions_file)

    maximum_experiment_guardrail = (
        len(questions)
        * 2
        * max(
            0.01,
            args.max_total_cost_per_variant,
        )
    )

    print("QUESTION_COUNT=" + str(len(questions)))

    print("MAX_COST_PER_VARIANT=" + str(args.max_total_cost_per_variant))

    print(
        "MAX_EXPERIMENT_GUARDRAIL="
        + str(
            round(
                maximum_experiment_guardrail,
                4,
            )
        )
    )

    result = run_live_retrieval_ab_suite(
        questions=questions,
        output_directory=(args.output_dir),
        configuration=(
            LiveSuiteConfiguration(
                top_k=args.top_k,
                language=args.language,
                tolerance=(args.tolerance),
                maximum_total_cost_per_variant=(args.max_total_cost_per_variant),
                maximum_median_latency_regression_ms=(
                    args.max_median_latency_regression_ms
                ),
                fail_fast=(args.fail_fast),
            )
        ),
    )

    payload = result["payload"]

    print("")
    print("==========================================")

    print("RESULTADO CONSOLIDADO")

    print("==========================================")

    print("RUN_ID=" + result["run_id"])

    print("QUESTIONS=" + str(payload["question_count"]))

    print("COMPLETED=" + str(payload["completed_count"]))

    print("FAILED=" + str(payload["failed_count"]))

    print("RECOMMENDATION=" + str(payload["recommendation"]))

    for reason in payload["recommendation_reasons"]:
        print("RECOMMENDATION_REASON=" + str(reason))

    print("MEDIAN_LATENCY_DELTA_MS=" + str(payload["median_latency_delta_ms"]))

    print(
        "AVERAGE_CONTEXT_CHARACTER_DELTA="
        + str(payload["average_context_character_delta"])
    )

    print("TOTAL_ESTIMATED_COST=" + str(payload["total_estimated_cost"]))

    for case in payload["cases"]:
        print("")
        print(
            "CASE_ID="
            + str(
                case.get(
                    "case_id",
                    "",
                )
            )
        )

        print(
            "CASE_STATUS="
            + str(
                case.get(
                    "status",
                    "",
                )
            )
        )

        if case.get("status") == "completed":
            print(
                "CASE_RECOMMENDATION="
                + str(
                    case.get(
                        "recommendation",
                        "",
                    )
                )
            )

            print("CASE_QUALITY_GATE_PASSED=" + str(case.get("quality_gate_passed")))

            deltas = case.get(
                "axis_deltas",
                {},
            )

            for axis_name in (
                "answer_relevancy",
                "faithfulness",
                "contextual_relevancy",
            ):
                print(
                    "CASE_AXIS_DELTA_"
                    + axis_name.upper()
                    + "="
                    + str(deltas.get(axis_name))
                )

        else:
            print(
                "CASE_ERROR_TYPE="
                + str(
                    case.get(
                        "error_type",
                        "",
                    )
                )
            )

            print(
                "CASE_ERROR_MESSAGE="
                + str(
                    case.get(
                        "error_message",
                        "",
                    )
                )
            )

    print("")
    print("JSON_REPORT=" + result["json_path"])

    print("MARKDOWN_REPORT=" + result["markdown_path"])

    print("HISTORY=" + result["history_path"])

    print("RAW_OUTPUTS_STORED=False")

    print("RAW_CONTEXTS_STORED=False")

    print("WEEK3_LIVE_RETRIEVAL_AB_SUITE=OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
