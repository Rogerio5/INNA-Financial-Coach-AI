from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env",
    override=False,
)

RUN_FLAG = "RUN_LIVE_EVALUATION_TESTS"

CASE_ID = "rag-financial-education-001"

REPORT_DIRECTORY = PROJECT_ROOT / "artifacts" / "live-evaluation-e2e"

REPORT_PATH = REPORT_DIRECTORY / "live-evaluation-e2e-report.txt"

JSON_PATH = REPORT_DIRECTORY / "live-evaluation-result.json"

TIMEOUT_SECONDS = 240


pytestmark = [
    pytest.mark.integration,
    pytest.mark.live,
]


def _live_test_enabled() -> bool:
    return str(
        os.getenv(
            RUN_FLAG,
            "",
        )
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _required_environment() -> tuple[str, ...]:
    missing: list[str] = []

    if not str(
        os.getenv(
            "DATABASE_URL",
            "",
        )
    ).strip():
        missing.append("DATABASE_URL")

    gemini_configured = bool(
        str(
            os.getenv(
                "GEMINI_API_KEY",
                "",
            )
        ).strip()
        or str(
            os.getenv(
                "GOOGLE_API_KEY",
                "",
            )
        ).strip()
    )

    if not gemini_configured:
        missing.append("GEMINI_API_KEY ou GOOGLE_API_KEY")

    return tuple(missing)


def _write_report(
    *,
    return_code: int | None,
    stdout: str,
    stderr: str,
    timeout: bool,
) -> None:
    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = "\n".join(
        [
            "INNA LIVE EVALUATION E2E REPORT",
            "================================",
            f"case_id={CASE_ID}",
            f"timeout={timeout}",
            f"return_code={return_code}",
            "",
            "STDOUT",
            "------",
            stdout,
            "",
            "STDERR",
            "------",
            stderr,
            "",
        ]
    )

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
    )


def _parse_json_output(
    stdout: str,
) -> dict[str, object]:
    normalized = stdout.strip()

    assert normalized, "A CLI live não produziu saída JSON."

    try:
        payload = json.loads(normalized)
    except json.JSONDecodeError as exception:
        pytest.fail(
            f"A CLI live produziu JSON inválido.\nSaída:\n{stdout}\nErro: {exception}",
            pytrace=False,
        )

    assert isinstance(
        payload,
        dict,
    )

    return payload


@pytest.mark.skipif(
    not _live_test_enabled(),
    reason=("Teste live de avaliação desativado. Defina RUN_LIVE_EVALUATION_TESTS=1."),
)
def test_live_evaluation_e2e() -> None:
    missing = _required_environment()

    assert not missing, f"Variáveis obrigatórias ausentes: {list(missing)}"

    environment = os.environ.copy()

    environment.update(
        {
            "RUN_LIVE_EVALUATION_TESTS": "1",
            "RUN_LIVE_GEMINI_TESTS": "0",
            "RUN_HITL_E2E_TESTS": "0",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )

    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.evaluation.cli",
                "run-live",
                "--case-id",
                CASE_ID,
                "--gate-profile",
                "single-case",
                "--no-report",
                "--json-output",
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )

        stdout = completed.stdout
        stderr = completed.stderr

        _write_report(
            return_code=(completed.returncode),
            stdout=stdout,
            stderr=stderr,
            timeout=False,
        )

        assert completed.returncode == 0, (
            "A avaliação live retornou código "
            "diferente de zero.\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )

        payload = _parse_json_output(stdout)

        REPORT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        JSON_PATH.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        assert payload.get("command") == "run-live"

        assert payload.get("case_id") == CASE_ID

        assert payload.get("execution_type") == "live-application-evaluation"

        assert payload.get("production_evaluation") is True

        assert payload.get("batch_status") == "passed"

        assert payload.get("total_cases") == 1

        assert payload.get("passed_cases") == 1

        assert payload.get("failed_cases") == 0

        assert payload.get("blocked_cases") == 0

        assert payload.get("error_cases") == 0

        assert payload.get("pass_rate") == 1.0

        assert payload.get("quality_gate_passed") is True

        assert payload.get("quality_gate_violations") == []

    except subprocess.TimeoutExpired as exception:
        stdout = str(exception.stdout or "")

        stderr = str(exception.stderr or "")

        _write_report(
            return_code=None,
            stdout=stdout,
            stderr=stderr,
            timeout=True,
        )

        pytest.fail(
            f"A avaliação live excedeu {TIMEOUT_SECONDS} segundos.",
            pytrace=False,
        )
