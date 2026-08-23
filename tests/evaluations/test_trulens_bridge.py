from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from src.evaluation.agentic_benchmark.framework_payloads import (
    build_trulens_record,
)

import src.evaluation.trulens_bridge as trulens_bridge
from src.evaluation.trulens_bridge import (
    TruLensBridgeError,
    run_trulens_record,
)


def _sample_record() -> dict[str, Any]:
    return {
        "app_id": "inna-agentic-rag-offline",
        "record_id": "offline-case-1",
        "main_input": "O que e reserva de emergencia?",
        "main_output": "Reserva cobre imprevistos.",
        "retrieved_contexts": [
            "Reserva cobre imprevistos."
        ],
        "meta": {
            "case_id": "case-1",
            "offline": True,
        },
        "feedback_results": {},
        "overall_score": 1.0,
        "quality_gate_passed": True,
    }


def test_build_trulens_record_includes_contexts() -> None:
    enum_simple = SimpleNamespace(
        value="simple"
    )

    case = SimpleNamespace(
        case_id="case-1",
        dataset_version="1.0.0",
        category=enum_simple,
        question="Pergunta de teste valida.",
    )

    evidence = SimpleNamespace(
        content="Contexto recuperado."
    )

    result = SimpleNamespace(
        trace_id=None,
        answer="Resposta de teste.",
        mode=enum_simple,
        decision=enum_simple,
        status=enum_simple,
        security_outcome=enum_simple,
        routes=(),
        evidence_count=1,
        citation_count=0,
        fallback_used=False,
        latency_ms=10.0,
        evidences=(evidence,),
    )

    report = SimpleNamespace(
        metrics=(),
        overall_score=1.0,
        passed=True,
    )

    record = build_trulens_record(
        case=case,
        result=result,
        report=report,
    )

    assert record["retrieved_contexts"] == [
        "Contexto recuperado."
    ]


def test_trulens_bridge_validate_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(
        args: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        captured["input"] = kwargs["input"]
        captured["env"] = kwargs["env"]

        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=(
                '{"context_count":1,'
                '"framework":"trulens",'
                '"mode":"isolated_validate",'
                '"ready":true,'
                '"trulens_version":"2.12.0"}'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        trulens_bridge.subprocess,
        "run",
        fake_run,
    )

    result = run_trulens_record(
        _sample_record(),
        trulens_python=Path(
            sys.executable
        ),
        validate_only=True,
    )

    assert result["ready"] is True
    assert result["framework"] == "trulens"

    serialized = json.loads(
        str(captured["input"])
    )

    assert (
        serialized["execution_mode"]
        == "validate"
    )
    assert (
        captured["env"]["PYTHONNOUSERSITE"]
        == "1"
    )


def test_trulens_bridge_record_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(
        args: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        captured["input"] = kwargs["input"]

        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=(
                '{"event_count":3,'
                '"force_flush":true,'
                '"framework":"trulens",'
                '"mode":"isolated_offline",'
                '"network_connection_attempt_count":0,'
                '"recorded":true,'
                '"span_types":["generation",'
                '"record_root","retrieval"]}'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        trulens_bridge.subprocess,
        "run",
        fake_run,
    )

    result = run_trulens_record(
        _sample_record(),
        trulens_python=Path(
            sys.executable
        ),
    )

    assert result["recorded"] is True
    assert result["event_count"] == 3
    assert set(result["span_types"]) == {
        "record_root",
        "retrieval",
        "generation",
    }

    serialized = json.loads(
        str(captured["input"])
    )

    assert (
        serialized["execution_mode"]
        == "record"
    )


def test_trulens_bridge_missing_python() -> None:
    with pytest.raises(
        TruLensBridgeError,
        match=(
            "isolated TruLens Python "
            "executable not found"
        ),
    ):
        run_trulens_record(
            _sample_record(),
            trulens_python=Path(
                "missing-trulens-python.exe"
            ),
        )


def test_trulens_bridge_surfaces_runner_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(
        args: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs

        return subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout=(
                '{"error":"invalid payload",'
                '"error_type":"ValueError",'
                '"framework":"trulens",'
                '"mode":"isolated_error"}'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        trulens_bridge.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        TruLensBridgeError,
        match="invalid payload",
    ):
        run_trulens_record(
            _sample_record(),
            trulens_python=Path(
                sys.executable
            ),
        )


def test_default_trulens_python_supports_posix_venv(
    monkeypatch,
    tmp_path,
) -> None:
    import src.evaluation.trulens_bridge as bridge

    python_path = (
        tmp_path
        / ".venv-trulens"
        / "bin"
        / "python"
    )
    python_path.parent.mkdir(parents=True)
    python_path.touch()

    monkeypatch.setattr(
        bridge,
        "_repo_root",
        lambda: tmp_path,
    )

    assert (
        bridge._default_trulens_python()
        == python_path
    )
