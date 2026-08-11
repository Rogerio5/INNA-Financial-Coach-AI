from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import src.evaluation.ragas_bridge as ragas_bridge
from src.evaluation.ragas_bridge import (
    RagasBridgeError,
    run_ragas_agentic_payload_live,
    run_ragas_llm,
)


def _completed(
    args: list[str],
    *,
    stdout: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=args,
        returncode=0,
        stdout=stdout,
        stderr="",
    )


def test_live_bridge_keeps_secret_out_of_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(
        args: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        captured["input"] = kwargs["input"]
        captured["env"] = kwargs["env"]

        return _completed(
            args,
            stdout=(
                '{"framework":"ragas",'
                '"llm_ready":true,'
                '"metrics":{},'
                '"mode":"isolated_llm_validate"}'
            ),
        )

    monkeypatch.setattr(
        ragas_bridge.subprocess,
        "run",
        fake_run,
    )

    secret = "offline-secret-value"

    result = run_ragas_llm(
        {
            "user_input": "O que e reserva?",
            "response": "Reserva cobre imprevistos.",
            "retrieved_contexts": [
                "Reserva cobre imprevistos."
            ],
            "reference": "Reserva cobre imprevistos.",
        },
        api_key=secret,
        model="gemini-2.0-flash",
        ragas_python=Path(sys.executable),
        validate_only=True,
    )

    assert result["llm_ready"] is True
    assert secret not in str(captured["input"])

    serialized = json.loads(
        str(captured["input"])
    )

    assert serialized["execution_mode"] == (
        "llm_validate"
    )
    assert captured["env"][
        "INNA_RAGAS_API_KEY"
    ] == secret


def test_live_bridge_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    with pytest.raises(
        RagasBridgeError,
        match="Gemini API key is required",
    ):
        run_ragas_llm(
            {
                "user_input": "Pergunta valida",
                "response": "Resposta valida",
                "retrieved_contexts": ["Contexto"],
            },
            api_key="",
            model="gemini-2.0-flash",
        )


def test_live_bridge_requires_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "INNA_DEEPEVAL_GEMINI_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "GEMINI_MODEL",
        raising=False,
    )

    with pytest.raises(
        RagasBridgeError,
        match="Gemini model is required",
    ):
        run_ragas_llm(
            {
                "user_input": "Pergunta valida",
                "response": "Resposta valida",
                "retrieved_contexts": ["Contexto"],
            },
            api_key="offline-key",
            model="",
        )


def test_agentic_live_bridge_preserves_all_contexts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_live(
        payload: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        captured["payload"] = payload
        captured["kwargs"] = kwargs

        return {
            "framework": "ragas",
            "mode": "isolated_llm_validate",
            "metrics": {},
            "llm_ready": True,
        }

    monkeypatch.setattr(
        ragas_bridge,
        "run_ragas_llm",
        fake_live,
    )

    result = run_ragas_agentic_payload_live(
        {
            "user_input": "Compare as fontes.",
            "response": "Resposta.",
            "retrieved_contexts": [
                "Contexto 1",
                "Contexto 2",
            ],
            "reference": "Referencia.",
        },
        api_key="offline-key",
        model="gemini-2.0-flash",
        validate_only=True,
    )

    assert result["llm_ready"] is True
    assert captured["payload"][
        "retrieved_contexts"
    ] == [
        "Contexto 1",
        "Contexto 2",
    ]
    assert captured["payload"][
        "reference"
    ] == "Referencia."
