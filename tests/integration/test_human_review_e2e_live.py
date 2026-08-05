from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env",
    override=False,
)

E2E_SCRIPT = PROJECT_ROOT / "scripts" / "test_human_review_e2e_resume.py"

REPORT_DIRECTORY = PROJECT_ROOT / "artifacts" / "hitl-e2e"

REPORT_PATH = REPORT_DIRECTORY / "hitl-e2e-report.txt"

RUN_FLAG = "RUN_HITL_E2E_TESTS"

REQUIRED_ENVIRONMENT = {
    "DATABASE_URL",
    "INNA_INTERNAL_API_SIGNING_SECRET",
}

SUCCESS_MARKERS = (
    "REAL_LANGGRAPH_INTERRUPT_CREATED",
    "DATABASE_REVIEW_REGISTERED: pending",
    "SIGNED_RESOLVE_API_APPROVED",
    "CHECKPOINT_APPROVED_STATE_VALIDATED",
    "DATABASE_APPROVED_STATE_VALIDATED",
    "HUMAN_REVIEW_FULL_E2E_RESUME_VALIDATED",
    "CHECKPOINT_THREAD_DELETED",
    "REVIEW_CLEANUP_ROWS: 1",
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.live,
]


def _live_test_enabled() -> bool:
    return (
        str(
            os.getenv(
                RUN_FLAG,
                "",
            )
        ).strip()
        == "1"
    )


def _run_suffix() -> str:
    seed = "|".join(
        [
            str(
                os.getenv(
                    "GITHUB_RUN_ID",
                    "",
                )
            ),
            str(
                os.getenv(
                    "GITHUB_RUN_ATTEMPT",
                    "",
                )
            ),
            uuid4().hex,
        ]
    )

    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


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
            "INNA HITL E2E REPORT",
            "====================",
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


def _cleanup_test_data(
    *,
    suffix: str,
) -> None:
    """
    Limpeza defensiva executada pelo processo pai.

    O script E2E também limpa seus dados, mas esta
    rotina cobre falhas abruptas e timeout.
    """
    review_id = f"hitl-e2e-review-{suffix}"

    thread_id = f"hitl-e2e-thread-{suffix}"

    try:
        from src.database.connection import (
            cursor_postgres,
        )

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=True,
        ) as cursor:
            cursor.execute(
                """
                DELETE FROM public.human_reviews
                WHERE review_id = %s;
                """,
                (review_id,),
            )

    except Exception:
        pass

    try:
        from src.agents.persistence import (
            abrir_checkpointer_postgres,
        )

        with abrir_checkpointer_postgres() as checkpointer:
            delete_thread = getattr(
                checkpointer,
                "delete_thread",
                None,
            )

            if callable(delete_thread):
                delete_thread(thread_id)

    except Exception:
        pass


@pytest.mark.skipif(
    not _live_test_enabled(),
    reason=("Teste HITL E2E real desativado. Defina RUN_HITL_E2E_TESTS=1."),
)
def test_human_review_e2e_live() -> None:
    missing = sorted(
        name
        for name in REQUIRED_ENVIRONMENT
        if not str(
            os.getenv(
                name,
                "",
            )
        ).strip()
    )

    assert not missing, f"Variáveis obrigatórias ausentes: {missing}"

    secret = str(os.environ["INNA_INTERNAL_API_SIGNING_SECRET"]).encode("utf-8")

    assert len(secret) >= 32, (
        "INNA_INTERNAL_API_SIGNING_SECRET deve possuir pelo menos 32 bytes."
    )

    assert E2E_SCRIPT.is_file()

    suffix = _run_suffix()

    environment = os.environ.copy()

    environment.update(
        {
            "HITL_E2E_RUN_ID": suffix,
            "PYTHONUNBUFFERED": "1",
        }
    )

    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(E2E_SCRIPT),
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
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
            f"O subprocesso HITL E2E falhou.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

        missing_markers = [marker for marker in SUCCESS_MARKERS if marker not in stdout]

        assert not missing_markers, (
            f"Marcadores E2E ausentes: {missing_markers}\nSTDOUT:\n{stdout}"
        )

    except subprocess.TimeoutExpired as exc:
        stdout = str(exc.stdout or "")

        stderr = str(exc.stderr or "")

        _write_report(
            return_code=None,
            stdout=stdout,
            stderr=stderr,
            timeout=True,
        )

        pytest.fail(
            "O teste HITL E2E excedeu 180 segundos.",
            pytrace=False,
        )

    finally:
        _cleanup_test_data(suffix=suffix)
