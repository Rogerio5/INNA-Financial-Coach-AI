from __future__ import annotations

import asyncio
import json
import math
import os
import sys
from typing import Any

from ragas.metrics.collections import ExactMatch, StringPresence


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()

    if not raw.strip():
        raise ValueError("empty payload")

    payload = json.loads(raw)

    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")

    return payload


def _score_value(result: object) -> float:
    value = getattr(result, "value", None)

    if value is None:
        value = getattr(result, "score", None)

    if value is None:
        value = float(result)

    score = float(value)

    if not math.isfinite(score):
        raise ValueError("metric score must be finite")

    if not 0.0 <= score <= 1.0:
        raise ValueError("metric score must be between 0 and 1")

    return score


async def _evaluate_non_llm(
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = str(payload.get("response") or "")
    reference = str(payload.get("reference") or "")
    required_phrase = str(
        payload.get("required_phrase")
        or reference
        or ""
    )

    metrics: dict[str, float] = {}

    if reference:
        exact = ExactMatch()
        exact_result = await exact.ascore(
            reference=reference,
            response=response,
        )
        metrics["exact_match"] = _score_value(
            exact_result
        )

    if required_phrase:
        presence = StringPresence()
        presence_result = await presence.ascore(
            reference=required_phrase,
            response=response,
        )
        metrics["string_presence"] = _score_value(
            presence_result
        )

    return {
        "framework": "ragas",
        "mode": "isolated_non_llm",
        "metrics": metrics,
    }


def _build_live_llm() -> object:
    import instructor
    import litellm
    from ragas.llms import llm_factory

    api_key = os.environ.get("INNA_RAGAS_API_KEY", "").strip()
    configured_model = os.environ.get(
        "INNA_RAGAS_MODEL",
        "",
    ).strip()

    if not api_key:
        raise ValueError(
            "INNA_RAGAS_API_KEY is required for LLM metrics"
        )

    if not configured_model:
        raise ValueError(
            "INNA_RAGAS_MODEL is required for LLM metrics"
        )

    model = (
        configured_model
        if configured_model.startswith("gemini/")
        else f"gemini/{configured_model}"
    )

    async_client = instructor.from_litellm(
        litellm.acompletion,
        async_client=True,
    )

    llm = llm_factory(
        model,
        provider="gemini",
        client=async_client,
        adapter="litellm",
        api_key=api_key,
    )

    if not getattr(llm, "is_async", False):
        raise TypeError(
            "isolated RAGAS LLM must be async-capable"
        )

    return llm


async def _evaluate_llm(
    payload: dict[str, Any],
    *,
    validate_only: bool,
) -> dict[str, Any]:
    user_input = str(payload.get("user_input") or "").strip()
    response = str(payload.get("response") or "").strip()
    reference = str(payload.get("reference") or "").strip()
    raw_contexts = payload.get("retrieved_contexts") or ()

    if isinstance(raw_contexts, str):
        raw_contexts = (raw_contexts,)

    retrieved_contexts = [
        str(context).strip()
        for context in raw_contexts
        if str(context).strip()
    ]

    if not user_input:
        raise ValueError(
            "user_input is required for RAGAS LLM metrics"
        )

    if not response:
        raise ValueError(
            "response is required for RAGAS LLM metrics"
        )

    if not retrieved_contexts:
        raise ValueError(
            "retrieved_contexts are required for RAGAS LLM metrics"
        )

    llm = _build_live_llm()

    if validate_only:
        return {
            "framework": "ragas",
            "mode": "isolated_llm_validate",
            "metrics": {},
            "llm_ready": True,
        }

    from ragas.metrics.collections import (
        ContextPrecisionWithReference,
        ContextRecall,
        Faithfulness,
    )

    metrics: dict[str, float] = {}

    faithfulness = Faithfulness(llm=llm)
    faithfulness_result = await faithfulness.ascore(
        user_input=user_input,
        response=response,
        retrieved_contexts=retrieved_contexts,
    )
    metrics["faithfulness"] = _score_value(
        faithfulness_result
    )

    if reference:
        precision = ContextPrecisionWithReference(
            llm=llm
        )
        precision_result = await precision.ascore(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=retrieved_contexts,
        )
        metrics["context_precision_with_reference"] = (
            _score_value(precision_result)
        )

        recall = ContextRecall(llm=llm)
        recall_result = await recall.ascore(
            user_input=user_input,
            retrieved_contexts=retrieved_contexts,
            reference=reference,
        )
        metrics["context_recall"] = _score_value(
            recall_result
        )

    return {
        "framework": "ragas",
        "mode": "isolated_llm",
        "metrics": metrics,
        "reference_metrics_executed": bool(reference),
    }


async def _evaluate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    execution_mode = str(
        payload.get("execution_mode") or "non_llm"
    ).strip()

    if execution_mode == "non_llm":
        return await _evaluate_non_llm(payload)

    if execution_mode == "llm_validate":
        return await _evaluate_llm(
            payload,
            validate_only=True,
        )

    if execution_mode == "llm":
        return await _evaluate_llm(
            payload,
            validate_only=False,
        )

    raise ValueError(
        f"unsupported execution_mode: {execution_mode}"
    )


def main() -> int:
    try:
        payload = _read_payload()
        result = asyncio.run(_evaluate(payload))
        sys.stdout.write(
            json.dumps(
                result,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        error = {
            "framework": "ragas",
            "mode": "isolated_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        sys.stdout.write(
            json.dumps(
                error,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
