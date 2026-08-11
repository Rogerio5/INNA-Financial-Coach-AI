from __future__ import annotations

import json
import os
import re
import socket
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SPAN_TYPE_KEY = "ai.observability.span_type"
TEMP_DIR_ENV = "INNA_TRULENS_TEMP_DIR"


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()

    if not raw.strip():
        raise ValueError("empty payload")

    payload = json.loads(raw)

    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")

    return payload


def _extract_span_types(value: Any) -> list[str]:
    found: list[str] = []

    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) == SPAN_TYPE_KEY:
                found.append(str(nested))

            found.extend(_extract_span_types(nested))

        return found

    if isinstance(value, (list, tuple)):
        for nested in value:
            found.extend(_extract_span_types(nested))

        return found

    if isinstance(value, str):
        stripped = value.strip()

        if (
            stripped.startswith("{")
            or stripped.startswith("[")
        ):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None

            if parsed is not None:
                found.extend(
                    _extract_span_types(parsed)
                )

        match = re.search(
            r"ai\.observability\.span_type"
            r"""["']?\s*[:=]\s*["']([^"']+)["']""",
            value,
        )

        if match:
            found.append(match.group(1))

    return found


def _validate_record(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    app_id = str(payload.get("app_id") or "").strip()
    record_id = str(
        payload.get("record_id") or ""
    ).strip()
    main_input = str(
        payload.get("main_input") or ""
    ).strip()
    main_output = str(
        payload.get("main_output") or ""
    ).strip()

    raw_contexts = (
        payload.get("retrieved_contexts")
        or ()
    )

    if isinstance(raw_contexts, str):
        raw_contexts = (raw_contexts,)

    contexts = [
        str(context).strip()
        for context in raw_contexts
        if str(context).strip()
    ]

    meta = payload.get("meta") or {}
    feedback_results = (
        payload.get("feedback_results")
        or {}
    )

    if not app_id:
        raise ValueError("app_id is required")

    if not record_id:
        raise ValueError("record_id is required")

    if not main_input:
        raise ValueError("main_input is required")

    if not main_output:
        raise ValueError("main_output is required")

    if not contexts:
        raise ValueError(
            "retrieved_contexts are required"
        )

    if not isinstance(meta, Mapping):
        raise TypeError("meta must be a JSON object")

    if not isinstance(
        feedback_results,
        Mapping,
    ):
        raise TypeError(
            "feedback_results must be a JSON object"
        )

    return {
        "app_id": app_id,
        "record_id": record_id,
        "main_input": main_input,
        "main_output": main_output,
        "retrieved_contexts": contexts,
        "meta": dict(meta),
        "feedback_results": dict(
            feedback_results
        ),
        "overall_score": payload.get(
            "overall_score"
        ),
        "quality_gate_passed": bool(
            payload.get("quality_gate_passed")
        ),
    }


def _validate_only(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = _validate_record(payload)

    import importlib.metadata as metadata

    return {
        "framework": "trulens",
        "mode": "isolated_validate",
        "ready": True,
        "trulens_version": metadata.version(
            "trulens"
        ),
        "context_count": len(
            normalized["retrieved_contexts"]
        ),
    }


def _resolve_temp_directory() -> Path:
    raw = os.environ.get(TEMP_DIR_ENV, "").strip()

    if not raw:
        raise RuntimeError(
            "isolated TruLens temp directory "
            "was not provided"
        )

    temp_directory = Path(raw).resolve()

    if not temp_directory.is_dir():
        raise RuntimeError(
            "isolated TruLens temp directory "
            "does not exist"
        )

    return temp_directory


def _record_offline(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    from trulens.apps.app import TruApp
    from trulens.core import TruSession
    from trulens.core.database.connector import (
        DefaultDBConnector,
    )
    from trulens.core.otel.instrument import (
        instrument,
    )
    from trulens.otel.semconv.trace import (
        SpanAttributes,
    )

    normalized = _validate_record(payload)
    temp_directory = _resolve_temp_directory()
    db_path = temp_directory / "events.sqlite"

    network_attempts: list[str] = []
    original_connect = socket.socket.connect

    def blocked_connect(
        sock: socket.socket,
        address: object,
    ) -> None:
        del sock
        network_attempts.append(
            type(address).__name__
        )
        raise RuntimeError(
            "TruLens isolated runner blocked "
            "a network connection attempt"
        )

    socket.socket.connect = blocked_connect
    os.environ["TRULENS_OTEL_TRACING"] = "1"

    class AgenticEvaluationRecord:
        def __init__(
            self,
            contexts: list[str],
            output: str,
        ) -> None:
            self.contexts = contexts
            self.output = output

        @instrument(
            span_type=(
                SpanAttributes.SpanType.RETRIEVAL
            ),
            attributes={
                (
                    SpanAttributes.RETRIEVAL
                    .QUERY_TEXT
                ): "query",
                (
                    SpanAttributes.RETRIEVAL
                    .RETRIEVED_CONTEXTS
                ): "return",
            },
        )
        def retrieve(
            self,
            query: str,
        ) -> list[str]:
            del query
            return list(self.contexts)

        @instrument(
            span_type=(
                SpanAttributes.SpanType.GENERATION
            ),
        )
        def generate(
            self,
            query: str,
            contexts: list[str],
        ) -> str:
            del query, contexts
            return self.output

        @instrument(
            attributes={
                (
                    SpanAttributes.RECORD_ROOT
                    .INPUT
                ): "query",
                (
                    SpanAttributes.RECORD_ROOT
                    .OUTPUT
                ): "return",
            },
        )
        def query(self, query: str) -> str:
            contexts = self.retrieve(query)
            return self.generate(
                query,
                contexts,
            )

    session = None

    try:
        connector = DefaultDBConnector(
            database_url=(
                "sqlite:///"
                + db_path.as_posix()
            ),
            database_redact_keys=True,
        )
        session = TruSession(
            connector=connector
        )

        app = AgenticEvaluationRecord(
            contexts=normalized[
                "retrieved_contexts"
            ],
            output=normalized[
                "main_output"
            ],
        )

        tru_app = TruApp(
            app,
            app_name=normalized["app_id"],
            app_version="agentic-evaluation",
            metadata=normalized["meta"],
            session=session,
        )

        with tru_app:
            answer = app.query(
                normalized["main_input"]
            )

        if (
            answer
            != normalized["main_output"]
        ):
            raise RuntimeError(
                "instrumented output mismatch"
            )

        flush_ok = bool(
            session.force_flush(
                timeout_millis=30_000
            )
        )

        events = session.get_events(
            app_name=normalized["app_id"],
            app_version=(
                "agentic-evaluation"
            ),
        )

        rows = events.to_dict(
            orient="records"
        )

        span_types: list[str] = []

        for row in rows:
            span_types.extend(
                _extract_span_types(row)
            )

        normalized_types = sorted(
            {
                item.strip()
                .lower()
                .replace(" ", "_")
                for item in span_types
                if item.strip()
            }
        )

        expected = {
            "record_root",
            "retrieval",
            "generation",
        }

        if not expected.issubset(
            set(normalized_types)
        ):
            raise RuntimeError(
                "expected TruLens span types "
                "were not persisted"
            )

        if network_attempts:
            raise RuntimeError(
                "network attempt detected"
            )

        return {
            "framework": "trulens",
            "mode": "isolated_offline",
            "recorded": True,
            "force_flush": flush_ok,
            "event_count": len(events),
            "span_types": normalized_types,
            "record_id": normalized[
                "record_id"
            ],
            "feedback_metric_count": len(
                normalized[
                    "feedback_results"
                ]
            ),
            "overall_score": normalized[
                "overall_score"
            ],
            "quality_gate_passed": (
                normalized[
                    "quality_gate_passed"
                ]
            ),
            (
                "network_connection_"
                "attempt_count"
            ): len(network_attempts),
        }

    finally:
        socket.socket.connect = (
            original_connect
        )

        if session is not None:
            try:
                session.connector.db.engine.dispose()
            except Exception:
                pass


def _execute(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    execution_mode = str(
        payload.get("execution_mode")
        or "record"
    ).strip()

    clean_payload = dict(payload)
    clean_payload.pop(
        "execution_mode",
        None,
    )

    if execution_mode == "validate":
        return _validate_only(
            clean_payload
        )

    if execution_mode == "record":
        return _record_offline(
            clean_payload
        )

    raise ValueError(
        "unsupported execution_mode: "
        + execution_mode
    )


def main() -> int:
    try:
        payload = _read_payload()
        result = _execute(payload)

        sys.stdout.write(
            json.dumps(
                result,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    except Exception as exc:
        sys.stdout.write(
            json.dumps(
                {
                    "framework": "trulens",
                    "mode": "isolated_error",
                    "error_type": (
                        type(exc).__name__
                    ),
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
