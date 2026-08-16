"""Cache Redis fail-open para o Query Planner LLM."""

from __future__ import annotations

import hashlib
import json
import logging
import os

from redis.exceptions import RedisError

from src.agentic_rag.contracts import (
    PlanGenerationMode,
    ResearchPlan,
)
from src.cache import get_redis_client

log = logging.getLogger(__name__)

PLANNER_CACHE_NAMESPACE = "inna:planner:v1"


def _read_bool_environment(
    name: str,
    default: bool = False,
) -> bool:
    raw = str(
        os.getenv(
            name,
            str(default),
        )
        or ""
    ).strip().lower()

    return raw in {
        "1",
        "true",
        "yes",
        "on",
    }


def _read_int_environment(
    name: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(
            str(
                os.getenv(
                    name,
                    default,
                )
            ).strip()
        )
    except (TypeError, ValueError):
        value = default

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def is_planner_cache_enabled() -> bool:
    """Retorna True somente quando o cache foi habilitado."""
    return _read_bool_environment(
        "INNA_PLANNER_CACHE_ENABLED",
        False,
    )


def get_planner_cache_ttl_seconds() -> int:
    """TTL do cache, limitado para evitar retenção longa."""
    return _read_int_environment(
        "INNA_PLANNER_CACHE_TTL_SECONDS",
        3600,
        minimum=60,
        maximum=86400,
    )


def build_planner_cache_key(
    *,
    question: str,
    language: str,
    trusted_user_context_available: bool,
) -> str:
    """
    Gera chave privacy-safer.

    A pergunta não aparece diretamente na chave Redis.
    """
    canonical = json.dumps(
        {
            "version": 1,
            "planner": "gemini_structured_v1",
            "question": str(question).strip(),
            "language": str(language).strip().lower(),
            "trusted_user_context_available": bool(
                trusted_user_context_available
            ),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return (
        f"{PLANNER_CACHE_NAMESPACE}:"
        f"{digest}"
    )


def _with_cache_metadata(
    plan: ResearchPlan,
    *,
    status: str,
    stored: bool | None = None,
) -> ResearchPlan:
    data = plan.model_dump(
        mode="python"
    )

    metadata = {
        **plan.metadata,
        "planner_cache_status": status,
        "planner_cache_backend": "redis",
    }

    if stored is not None:
        metadata[
            "planner_cache_stored"
        ] = stored

    data["metadata"] = metadata

    return ResearchPlan.model_validate(
        data
    )


def read_planner_cache(
    *,
    question: str,
    language: str,
    user_id: str | None,
) -> ResearchPlan | None:
    """
    Consulta o cache.

    Qualquer erro é fail-open e equivale a cache miss.
    """
    if not is_planner_cache_enabled():
        return None

    client = get_redis_client()

    if client is None:
        return None

    key = build_planner_cache_key(
        question=question,
        language=language,
        trusted_user_context_available=bool(
            user_id
        ),
    )

    try:
        cached = client.get(
            key
        )

        if not cached:
            return None

        plan = (
            ResearchPlan.model_validate_json(
                cached
            )
        )

        if (
            plan.generation_mode
            != PlanGenerationMode.LLM
        ):
            return None

        if (
            plan.original_question
            != question
        ):
            return None

        return _with_cache_metadata(
            plan,
            status="hit",
        )

    except (
        RedisError,
        ValueError,
        TypeError,
    ):
        log.warning(
            "Falha ao ler Planner Cache; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return None

    except Exception:
        log.warning(
            "Falha inesperada no Planner Cache; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return None


def write_planner_cache(
    *,
    plan: ResearchPlan,
    question: str,
    language: str,
    user_id: str | None,
) -> bool:
    """
    Persiste somente planos realmente gerados pelo LLM.

    Fallback determinístico nunca é armazenado.
    """
    if not is_planner_cache_enabled():
        return False

    if (
        plan.generation_mode
        != PlanGenerationMode.LLM
    ):
        return False

    client = get_redis_client()

    if client is None:
        return False

    key = build_planner_cache_key(
        question=question,
        language=language,
        trusted_user_context_available=bool(
            user_id
        ),
    )

    try:
        client.setex(
            key,
            get_planner_cache_ttl_seconds(),
            plan.model_dump_json(),
        )
        return True

    except RedisError:
        log.warning(
            "Falha ao gravar Planner Cache; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return False

    except Exception:
        log.warning(
            "Falha inesperada ao gravar Planner Cache; "
            "continuando em modo fail-open.",
            exc_info=True,
        )
        return False


def mark_planner_cache_miss(
    plan: ResearchPlan,
    *,
    stored: bool,
) -> ResearchPlan:
    """Adiciona somente metadados operacionais ao resultado."""
    return _with_cache_metadata(
        plan,
        status="miss",
        stored=stored,
    )


__all__ = [
    "build_planner_cache_key",
    "get_planner_cache_ttl_seconds",
    "is_planner_cache_enabled",
    "mark_planner_cache_miss",
    "read_planner_cache",
    "write_planner_cache",
]
