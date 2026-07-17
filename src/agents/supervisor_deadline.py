"""
Hard deadline do Supervisor Gemini.

A chamada externa é executada em outro processo para que
possa ser encerrada quando ultrapassar o orçamento total.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from src.agents.schemas import (
    SupervisorDecision,
)
from src.agents.supervisor_config import (
    get_supervisor_runtime_config,
)
from src.agents.supervisor_llm import (
    _obter_mensagem_protegida,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


class SupervisorDeadlineExceeded(
    TimeoutError
):
    """
    O Gemini ultrapassou o prazo total do Supervisor.
    """


def _minimal_context(
    context: dict[str, Any] | None,
    protected_message: str,
) -> dict[str, str]:
    if not isinstance(context, dict):
        context = {}

    return {
        "current_message": protected_message,
        "rendered_prompt": str(
            context.get(
                "rendered_prompt",
                "",
            )
        ),
    }


def _parse_worker_output(
    stdout: str,
) -> dict[str, Any]:
    lines = [
        line.strip()
        for line in str(stdout or "").splitlines()
        if line.strip()
    ]

    if not lines:
        raise RuntimeError(
            "O processo Gemini terminou sem resposta."
        )

    try:
        result = json.loads(
            lines[-1]
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "O processo Gemini retornou uma "
            "resposta inválida."
        ) from exc

    if not isinstance(result, dict):
        raise RuntimeError(
            "Formato de resposta do processo inválido."
        )

    return result


def classificar_com_gemini_com_deadline(
    *,
    mensagem: str,
    context: dict[str, Any] | None = None,
) -> SupervisorDecision:
    runtime = get_supervisor_runtime_config()

    protected_message = (
        _obter_mensagem_protegida(
            mensagem,
            context,
        )
    )

    payload = json.dumps(
        {
            "message": protected_message,
            "context": _minimal_context(
                context,
                protected_message,
            ),
        },
        ensure_ascii=False,
    )

    creation_flags = (
        subprocess.CREATE_NO_WINDOW
        if os.name == "nt"
        else 0
    )

    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.agents.supervisor_worker",
            ],
            input=payload,
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=str(PROJECT_ROOT),
            env=os.environ.copy(),
            timeout=(
                runtime.total_deadline_ms
                / 1000
            ),
            check=False,
            creationflags=creation_flags,
        )

    except subprocess.TimeoutExpired as exc:
        raise SupervisorDeadlineExceeded(
            "Gemini ultrapassou o prazo total de "
            f"{runtime.total_deadline_ms} ms."
        ) from exc

    result = _parse_worker_output(
        completed.stdout
    )

    if not result.get("ok"):
        error_type = str(
            result.get(
                "error_type",
                "GeminiError",
            )
        )

        error_message = str(
            result.get(
                "error",
                "Falha não identificada.",
            )
        )[:300]

        raise RuntimeError(
            f"{error_type}: {error_message}"
        )

    return SupervisorDecision.model_validate(
        result["decision"]
    )


__all__ = [
    "SupervisorDeadlineExceeded",
    "classificar_com_gemini_com_deadline",
]
