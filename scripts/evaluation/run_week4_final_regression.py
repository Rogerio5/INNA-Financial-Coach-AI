"""Executa a regressão final offline da Semana 4."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.final_regression import (
    run_final_regression,
)


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser da linha de comando."""

    parser = argparse.ArgumentParser(
        description=(
            "Executa a regressão final offline "
            "da Semana 4."
        )
    )

    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(
            "config/evaluation/"
            "week4_final_regression.json"
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "artifacts/evaluations/"
            "week4_final_regression"
        ),
    )

    parser.add_argument(
        "--evaluation-python",
        type=Path,
        default=Path(
            ".venv-evaluation/Scripts/python.exe"
        ),
    )

    return parser


def main() -> int:
    """Executa o runner."""

    args = build_parser().parse_args()

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    report = run_final_regression(
        project_root,
        policy_path=(
            project_root
            / args.policy
        ),
        output_dir=(
            project_root
            / args.output_dir
        ),
        evaluation_python=(
            project_root
            / args.evaluation_python
        ),
    )

    print(
        "WEEK4_FINAL_REGRESSION="
        + (
            "OK"
            if report.overall_passed
            else "FAILED"
        )
    )

    return (
        0
        if report.overall_passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
