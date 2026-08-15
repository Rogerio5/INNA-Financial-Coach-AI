"""
Processo isolado para classificação real com Gemini.

Recebe JSON pela entrada padrão e devolve JSON pela saída.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from src.agents.supervisor_llm import (
    classificar_com_gemini,
)
from src.resilience import classify_failure


def _write_result(
    payload: dict[str, Any],
) -> None:
    sys.stdout.write(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
        + "\n"
    )

    sys.stdout.flush()


def main() -> int:
    try:
        raw_payload = sys.stdin.read()

        payload = json.loads(
            raw_payload
        )

        message = str(
            payload.get(
                "message",
                "",
            )
        ).strip()

        context = payload.get(
            "context",
            {},
        )

        if not isinstance(context, dict):
            context = {}

        decision = classificar_com_gemini(
            mensagem=message,
            context=context,
        )

        _write_result(
            {
                "ok": True,
                "decision": decision.model_dump(
                    mode="json"
                ),
            }
        )

        return 0

    except Exception as exc:
        failure_kind = classify_failure(
            exc
        )

        _write_result(
            {
                "ok": False,
                "error_type": (
                    type(exc).__name__
                ),
                "failure_kind": (
                    failure_kind.value
                ),
            }
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
