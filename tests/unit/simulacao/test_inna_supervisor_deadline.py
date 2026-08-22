from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from src.agents.supervisor_config import (
    reset_supervisor_config_cache,
)
from src.agents.supervisor_deadline import (
    SupervisorDeadlineExceeded,
    classificar_com_gemini_com_deadline,
)


@patch(
    "src.agents.supervisor_deadline."
    "subprocess.run"
)
def test_deadline_retorna_decisao_estruturada(
    mock_run,
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_SUPERVISOR_TOTAL_DEADLINE_MS",
        "8000",
    )

    reset_supervisor_config_cache()

    mock_run.return_value = (
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "decision": {
                        "intent": (
                            "educacao_financeira"
                        ),
                        "next_node": (
                            "education_agent"
                        ),
                        "confidence": 0.91,
                        "use_rag": True,
                        "use_database": False,
                        "generate_report": False,
                        "reason": (
                            "Orientação financeira."
                        ),
                        "classification_source": (
                            "gemini"
                        ),
                        "classification_duration_ms": 500,
                        "gemini_called": True,
                        "fallback_used": False,
                        "classification_error": None,
                    },
                },
                ensure_ascii=False,
            ),
            stderr="",
        )
    )

    decision = (
        classificar_com_gemini_com_deadline(
            mensagem=(
                "Meu e-mail é pessoa@email.com "
                "e preciso de orientação."
            ),
            context={},
        )
    )

    assert (
        decision.intent
        == "educacao_financeira"
    )

    assert (
        decision.classification_source
        == "gemini"
    )

    call = mock_run.call_args

    assert (
        0
        < call.kwargs["timeout"]
        < 8.0
    )

    assert (
        "pessoa@email.com"
        not in call.kwargs["input"]
    )


@patch(
    "src.agents.supervisor_deadline."
    "subprocess.run"
)
def test_deadline_interrompe_chamada_lenta(
    mock_run,
    monkeypatch,
):
    monkeypatch.setenv(
        "INNA_SUPERVISOR_TOTAL_DEADLINE_MS",
        "8000",
    )

    reset_supervisor_config_cache()

    mock_run.side_effect = (
        subprocess.TimeoutExpired(
            cmd=["python"],
            timeout=8,
        )
    )

    with pytest.raises(
        SupervisorDeadlineExceeded
    ):
        classificar_com_gemini_com_deadline(
            mensagem="Mensagem ambígua.",
            context={},
        )


@patch(
    "src.agents.supervisor_deadline."
    "subprocess.run"
)
def test_deadline_propaga_erro_controlado(
    mock_run,
):
    reset_supervisor_config_cache()

    mock_run.return_value = (
        subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout=json.dumps(
                {
                    "ok": False,
                    "error_type": "APIError",
                    "error": "Serviço indisponível.",
                }
            ),
            stderr="",
        )
    )

    with pytest.raises(
        RuntimeError,
        match="APIError",
    ):
        classificar_com_gemini_com_deadline(
            mensagem="Mensagem ambígua.",
            context={},
        )
