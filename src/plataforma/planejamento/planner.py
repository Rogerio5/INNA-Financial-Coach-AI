"""
Query Planner profissional do Agentic RAG da INNA.

O modo determinístico é o padrão de produção nesta fase.
O modo Gemini é opcional, estruturado e sempre possui
fallback seguro para o planejador determinístico.
"""

from __future__ import annotations

import os
import re
import unicodedata
from time import perf_counter
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.compartilhado.rag.agentic.contracts import (
    ALLOWED_TOOL_BY_SOURCE,
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)
from src.plataforma.planejamento.planner_cache import (
    is_planner_cache_enabled,
    mark_planner_cache_miss,
    read_planner_cache,
    write_planner_cache,
)
from src.compartilhado.observabilidade.phoenix.runtime import traced_operation
from src.plataforma.observabilidade.planner_metrics import (
    PlannerMetricEvent,
    record_planner_metric_event,
)


def _set_planner_route_trace(
    *,
    planner_mode: str,
    query_complexity: str,
    planner_route: str,
    cache_hit: bool,
    plan_source: str,
    plan_valid: bool,
    fallback_used: bool,
) -> None:
    """
    Exporta somente metadados operacionais
    seguros da rota do Planner.
    """
    try:
        with traced_operation(
            "inna.agentic_rag.planner.route",
            attributes={
                "planner.mode": str(
                    planner_mode
                ),
                "planner.query_complexity": str(
                    query_complexity
                ),
                "planner.route": str(
                    planner_route
                ),
                "planner.cache_hit": bool(
                    cache_hit
                ),
                "planner.plan_source": str(
                    plan_source
                ),
                "planner.plan_valid": bool(
                    plan_valid
                ),
                "planner.fallback_used": bool(
                    fallback_used
                ),
                "privacy.content_exported": False,
            },
            instrumentation_name=(
                "inna.agentic_rag.planner"
            ),
        ):
            pass

    except Exception:
        return


class PlannerValidationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    valid: bool
    reason: str


def _normalize_validation_text(
    value: str,
) -> str:
    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def validate_llm_research_plan(
    plan: ResearchPlan,
    *,
    question: str,
    language: str,
    user_id: str | None,
) -> PlannerValidationResult:
    """
    Valida invariantes semânticas e operacionais
    antes de aceitar um plano LLM.

    O schema Pydantic continua responsável pelas
    invariantes estruturais do ResearchPlan.
    """

    if (
        plan.generation_mode
        != PlanGenerationMode.LLM
    ):
        return PlannerValidationResult(
            valid=False,
            reason="generation_mode_not_llm",
        )

    if (
        plan.original_question.strip()
        != str(question).strip()
    ):
        return PlannerValidationResult(
            valid=False,
            reason="question_mismatch",
        )

    if (
        plan.language.strip().lower()
        != str(language).strip().lower()
    ):
        return PlannerValidationResult(
            valid=False,
            reason="language_mismatch",
        )

    normalized_subqueries: set[str] = set()

    for subquery in plan.subqueries:
        normalized_question = (
            _normalize_validation_text(
                subquery.question
            )
        )

        if normalized_question in normalized_subqueries:
            return PlannerValidationResult(
                valid=False,
                reason="duplicate_subquery",
            )

        normalized_subqueries.add(
            normalized_question
        )

        if (
            subquery.source
            == ResearchSource.FINANCIAL_HISTORY
            and not str(user_id or "").strip()
        ):
            return PlannerValidationResult(
                valid=False,
                reason="untrusted_history_step",
            )

    if (
        plan.complexity
        == ResearchComplexity.SIMPLE
        and len(plan.subqueries) > 1
    ):
        return PlannerValidationResult(
            valid=False,
            reason="simple_plan_has_multiple_steps",
        )

    return PlannerValidationResult(
        valid=True,
        reason="valid",
    )


def _set_planner_validation_trace(
    *,
    status: str,
    reason: str,
    fallback_used: bool,
) -> None:
    """
    Exporta somente metadados seguros da
    validação do plano.
    """

    try:
        with traced_operation(
            "inna.agentic_rag.planner.validation",
            attributes={
                "planner.validation.status": str(
                    status
                ),
                "planner.validation.reason": str(
                    reason
                ),
                "planner.fallback.used": bool(
                    fallback_used
                ),
            },
            instrumentation_name=(
                "inna.agentic_rag.planner"
            ),
        ):
            pass

    except Exception:
        return


def _set_planner_trace_attributes(
    *,
    generation_mode: str,
    cache_enabled: bool,
    cache_status: str,
    cache_backend: str = "none",
    cache_stored: bool = False,
) -> None:
    """
    Exporta somente metadados operacionais seguros.

    Nunca exporta pergunta, resposta, user_id,
    prompt ou conteudo do ResearchPlan.
    """
    try:
        with traced_operation(
            "inna.agentic_rag.planner.cache",
            attributes={
                "planner.generation_mode": str(
                    generation_mode
                ),
                "planner.cache.enabled": bool(
                    cache_enabled
                ),
                "planner.cache.status": str(
                    cache_status
                ),
                "planner.cache.backend": str(
                    cache_backend
                ),
                "planner.cache.stored": bool(
                    cache_stored
                ),
            },
            instrumentation_name=(
                "inna.agentic_rag.planner"
            ),
        ):
            pass

    except Exception:
        # Telemetria nunca pode alterar
        # o caminho funcional do Planner.
        return


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        str(value or ""),
    )

    return (
        "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )
        .lower()
        .strip()
    )


def _read_int_environment(
    name: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(str(os.getenv(name, default)).strip())
    except (TypeError, ValueError):
        value = default

    return max(
        minimum,
        min(maximum, value),
    )


def _history_is_relevant(
    question: str,
) -> bool:
    normalized = _normalize_text(question)

    terms = (
        "meu historico",
        "meus diagnosticos",
        "minha evolucao",
        "comparar com antes",
        "compare com antes",
        "ultimos meses",
        "diagnostico anterior",
        "historico financeiro",
        "como eu estava",
        "minhas financas anteriores",
    )

    return any(term in normalized for term in terms)


class QueryComplexityAssessment(BaseModel):
    """
    Avaliação estruturada e observável da complexidade.

    A classificação utiliza somente sinais de alto nível.
    Ela não armazena cadeia de pensamento nem conteúdo
    confidencial do usuário.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    complexity: ResearchComplexity
    score: int = Field(
        ge=0,
        le=30,
    )
    threshold: int = Field(
        default=2,
        ge=1,
        le=10,
    )
    word_count: int = Field(
        ge=0,
    )
    question_count: int = Field(
        ge=0,
    )
    objective_count: int = Field(
        ge=0,
    )
    connector_count: int = Field(
        ge=0,
    )
    signals: list[str] = Field(
        default_factory=list,
        max_length=20,
    )


_STRONG_COMPLEXITY_GROUPS = {
    "comparison": (
        "compare",
        "comparar",
        "comparacao",
        "diferenca entre",
        "relacao entre",
    ),
    "complete_analysis": (
        "plano completo",
        "analise completa",
        "passo a passo",
        "estrategia completa",
    ),
    "tradeoffs": (
        "vantagens e desvantagens",
        "pros e contras",
        "beneficios e riscos",
    ),
    "multi_source": (
        "multiplas fontes",
        "fontes diferentes",
        "varias fontes",
        "multidocumento",
    ),
}


_MEDIUM_COMPLEXITY_GROUPS = {
    "risk_analysis": (
        "riscos",
        "impacto",
        "causas",
        "consequencias",
        "limitacoes",
    ),
    "temporal_analysis": (
        "evolucao",
        "historico",
        "ultimos meses",
        "comparar com antes",
    ),
}


_OBJECTIVE_TERMS = (
    "compare",
    "comparar",
    "explique",
    "explicar",
    "analise",
    "analisar",
    "avalie",
    "avaliar",
    "crie",
    "criar",
    "apresente",
    "apresentar",
    "calcule",
    "calcular",
    "recomende",
    "recomendar",
    "identifique",
    "identificar",
)


def assess_query_complexity(
    question: str,
) -> QueryComplexityAssessment:
    """
    Classifica a consulta com sinais determinísticos.

    Pontuação:
    - sinais fortes: dois pontos cada;
    - sinais médios: um ponto cada;
    - múltiplos objetivos: dois pontos;
    - pergunta longa: um ponto;
    - múltiplas perguntas: um ponto;
    - múltiplos conectores: um ponto;
    - histórico pessoal: três pontos.

    Uma pontuação igual ou superior a dois representa
    uma pesquisa complexa.
    """

    normalized = _normalize_text(question)
    words = re.findall(
        r"[a-z0-9]+",
        normalized,
    )

    score = 0
    signals: list[str] = []

    for signal_name, terms in _STRONG_COMPLEXITY_GROUPS.items():
        if any(term in normalized for term in terms):
            score += 2
            signals.append(f"strong:{signal_name}")

    for signal_name, terms in _MEDIUM_COMPLEXITY_GROUPS.items():
        if any(term in normalized for term in terms):
            score += 1
            signals.append(f"medium:{signal_name}")

    objective_count = sum(
        1
        for term in _OBJECTIVE_TERMS
        if re.search(
            rf"\b{re.escape(term)}\b",
            normalized,
        )
    )

    if objective_count >= 3:
        score += 2
        signals.append("multiple_objectives")
    elif objective_count == 2:
        score += 1
        signals.append("two_objectives")

    connector_count = len(
        re.findall(
            r"\b(?:e|alem disso|tambem|depois|enquanto)\b",
            normalized,
        )
    )

    if connector_count >= 2:
        score += 1
        signals.append("multiple_connectors")

    question_count = max(
        1,
        str(question or "").count("?"),
    )

    if str(question or "").count("?") >= 2:
        score += 1
        signals.append("multiple_questions")

    if len(words) >= 18:
        score += 1
        signals.append("long_query")

    if _history_is_relevant(question):
        score += 3
        signals.append("trusted_history_required")

    threshold = 2

    complexity = (
        ResearchComplexity.COMPLEX if score >= threshold else ResearchComplexity.SIMPLE
    )

    return QueryComplexityAssessment(
        complexity=complexity,
        score=min(30, score),
        threshold=threshold,
        word_count=len(words),
        question_count=question_count,
        objective_count=objective_count,
        connector_count=connector_count,
        signals=list(dict.fromkeys(signals))[:20],
    )


def _classify_complexity(
    question: str,
) -> ResearchComplexity:
    """
    Fachada mantida para compatibilidade interna.
    """

    return assess_query_complexity(question).complexity


def _build_step(
    *,
    index: int,
    question: str,
    source: ResearchSource,
    priority: int,
    required: bool,
    top_k: int = 4,
    max_results: int = 5,
    suffix: str = "",
) -> ResearchSubquery:
    source_token = "knowledge" if source == ResearchSource.KNOWLEDGE_BASE else "history"

    suffix_token = ""

    if suffix:
        normalized_suffix = re.sub(
            r"[^a-z0-9_]+",
            "_",
            _normalize_text(suffix),
        ).strip("_")

        if normalized_suffix:
            suffix_token = f"_{normalized_suffix}"

    return ResearchSubquery(
        step_id=(f"step_{index:02d}_{source_token}{suffix_token}"),
        question=question,
        source=source,
        tool_name=(ALLOWED_TOOL_BY_SOURCE[source]),
        priority=priority,
        required=required,
        top_k=top_k,
        max_results=max_results,
    )


def _build_deterministic_plan(
    *,
    question: str,
    language: str,
    user_id: str | None,
) -> ResearchPlan:
    complexity_assessment = assess_query_complexity(question)
    complexity = complexity_assessment.complexity
    history_relevant = _history_is_relevant(question)

    steps: list[ResearchSubquery] = []

    if complexity == ResearchComplexity.SIMPLE:
        steps.append(
            _build_step(
                index=1,
                question=question,
                source=(ResearchSource.KNOWLEDGE_BASE),
                priority=100,
                required=True,
                top_k=4,
            )
        )

        rationale = (
            "Consulta direta: uma recuperação "
            "fundamentada na base de conhecimento "
            "é suficiente para iniciar a resposta."
        )
        max_rounds = 1

    else:
        steps.extend(
            [
                _build_step(
                    index=1,
                    question=(
                        question + " Foque nos conceitos, critérios "
                        "e evidências aplicáveis."
                    ),
                    source=(ResearchSource.KNOWLEDGE_BASE),
                    priority=100,
                    required=True,
                    top_k=5,
                    suffix="concepts",
                ),
                _build_step(
                    index=2,
                    question=(
                        question + " Foque nos riscos, limites e "
                        "ações práticas seguras."
                    ),
                    source=(ResearchSource.KNOWLEDGE_BASE),
                    priority=90,
                    required=True,
                    top_k=5,
                    suffix="actions",
                ),
            ]
        )

        if history_relevant and user_id:
            steps.append(
                _build_step(
                    index=3,
                    question=question,
                    source=(ResearchSource.FINANCIAL_HISTORY),
                    priority=95,
                    required=True,
                    max_results=8,
                    suffix="personal",
                )
            )

        rationale = (
            "Consulta complexa: decomposição em "
            "subconsultas complementares, fontes "
            "controladas e pesquisa iterativa."
        )

        max_rounds = _read_int_environment(
            "INNA_AGENTIC_RAG_MAX_ROUNDS",
            2,
            minimum=1,
            maximum=3,
        )

    metadata: dict[str, Any] = {
        "planner": "deterministic_v2",
        "complexity_score": (complexity_assessment.score),
        "complexity_threshold": (complexity_assessment.threshold),
        "complexity_signals": list(complexity_assessment.signals),
        "complexity_word_count": (complexity_assessment.word_count),
        "complexity_objective_count": (complexity_assessment.objective_count),
        "complexity_connector_count": (complexity_assessment.connector_count),
        "history_relevant": history_relevant,
        "trusted_user_context_available": bool(user_id),
        "tool_selection_policy": ("deny_by_default"),
    }

    if history_relevant and not user_id:
        metadata["history_omitted_reason"] = "missing_trusted_user_context"

    return ResearchPlan(
        original_question=question,
        language=language,
        complexity=complexity,
        rationale=rationale,
        subqueries=sorted(
            steps,
            key=lambda item: -item.priority,
        ),
        generation_mode=(PlanGenerationMode.DETERMINISTIC),
        requires_iteration=(complexity == ResearchComplexity.COMPLEX),
        max_rounds=max_rounds,
        metadata=metadata,
    )


class _LLMPlanStep(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    question: str = Field(
        min_length=3,
        max_length=1200,
    )
    source: ResearchSource
    priority: int = Field(
        default=50,
        ge=1,
        le=100,
    )
    required: bool = True
    top_k: int = Field(
        default=4,
        ge=1,
        le=10,
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class _LLMPlanResponse(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    complexity: ResearchComplexity
    rationale: str = Field(
        min_length=3,
        max_length=300,
    )
    steps: list[_LLMPlanStep] = Field(
        min_length=1,
        max_length=6,
    )
    requires_iteration: bool = False



def _planner_governor_enforcement_enabled() -> bool:
    """
    Enforcement exige os dois gates:

    - kill-switch global;
    - gate específico do Query Planner.
    """
    from src.config import get_bool_env

    return (
        get_bool_env(
            (
                "INNA_RELIABILITY_GOVERNOR_"
                "ENFORCEMENT_ENABLED"
            ),
            False,
        )
        and get_bool_env(
            (
                "INNA_RELIABILITY_GOVERNOR_"
                "PLANNER_ENFORCEMENT_ENABLED"
            ),
            False,
        )
    )


def _resolve_planner_resilience_policy(
    base_policy,
):
    """
    Resolve a policy efetiva do Planner.

    Fail-open:
    qualquer falha da governança mantém
    a policy original e nunca derruba
    o caminho funcional do Planner.

    Decisões e fail-open são observados
    de forma privacy-safe via OTEL/Phoenix.
    """
    if not _planner_governor_enforcement_enabled():
        return base_policy

    try:
        from src.compartilhado.resilience.tracing import (
            observe_reliability_governor_decision,
        )
        from src.reliability.governor import (
            derive_effective_resilience_policy,
            get_reliability_governor_decision,
        )

        decision = (
            get_reliability_governor_decision(
                base_policy.name
            )
        )

        # Telemetria nunca pode modificar
        # a decisão funcional do Governor.
        try:
            observe_reliability_governor_decision(
                decision
            )
        except Exception:
            pass

        return (
            derive_effective_resilience_policy(
                policy=base_policy,
                decision=decision,
            )
        )

    except Exception as exc:
        # O fail-open continua funcional mesmo
        # se a própria telemetria falhar.
        try:
            from src.compartilhado.resilience.tracing import (
                observe_reliability_governor_fail_open,
            )

            observe_reliability_governor_fail_open(
                operation=base_policy.name,
                current_max_attempts=(
                    base_policy.max_attempts
                ),
                error_type=(
                    type(exc).__name__
                ),
            )
        except Exception:
            pass

        return base_policy

def _build_llm_plan(
    *,
    question: str,
    language: str,
    user_id: str | None,
    trace_id: str | None,
) -> ResearchPlan:
    from google import genai
    from google.genai import types

    from src.plataforma.supervisao.supervisor_config import (
        get_gemini_api_key,
        get_supervisor_runtime_config,
    )
    from src.compartilhado.observabilidade.llm.tracking import (
        executar_generate_content_observado,
    )
    from src.compartilhado.resilience.tracing import (
        get_shared_resilience_runtime,
        traced_resilience_operation,
    )
    from src.compartilhado.resilience.deadline import (
        DeadlineBudget,
    )
    from src.compartilhado.resilience.policies import (
        AGENTIC_RAG_PLANNER_POLICY,
    )

    planner_resilience_policy = (
        _resolve_planner_resilience_policy(
            AGENTIC_RAG_PLANNER_POLICY
        )
    )

    runtime_config = get_supervisor_runtime_config()
    model = str(
        os.getenv(
            "INNA_AGENTIC_RAG_MODEL",
            "",
        )
        or runtime_config.model
    ).strip()

    planner_timeout_ms = _read_int_environment(
        "INNA_AGENTIC_RAG_PLANNER_TIMEOUT_MS",
        12000,
        minimum=1000,
        maximum=120000,
    )

    planner_total_deadline_ms = (
        _read_int_environment(
            "INNA_AGENTIC_RAG_PLANNER_TOTAL_DEADLINE_MS",
            20000,
            minimum=1000,
            maximum=180000,
        )
    )

    deadline_budget = DeadlineBudget(
        planner_total_deadline_ms / 1000.0,
        reserve_seconds=0.25,
    )

    resilience_runtime = (
        get_shared_resilience_runtime()
    )

    prompt = f"""
Você é o Query Planner da INNA.

Crie um plano curto e executável para pesquisar a
pergunta apresentada. Não exponha cadeia de pensamento.
Retorne somente a estrutura solicitada.

Fontes permitidas:
- knowledge_base: conhecimento financeiro da INNA;
- financial_history: histórico do usuário autenticado.

Regras:
1. Use financial_history somente para histórico,
   comparação ou evolução pessoal.
2. Crie no máximo seis etapas.
3. Não invente ferramentas ou fontes.
4. Divida perguntas complexas em consultas menores.
5. A justificativa deve ser objetiva.

Idioma: {language}
Contexto autenticado disponível: {bool(user_id)}

Pergunta:
{question}
""".strip()

    def generate_plan_attempt():
        attempt_timeout_seconds = (
            deadline_budget.clamp_timeout(
                planner_timeout_ms
                / 1000.0
            )
        )

        attempt_timeout_ms = max(
            1,
            int(
                attempt_timeout_seconds
                * 1000
            ),
        )

        http_options = types.HttpOptions(
            timeout=attempt_timeout_ms,
            retry_options=None,
        )

        client = genai.Client(
            api_key=get_gemini_api_key(),
            http_options=http_options,
        )

        return (
            executar_generate_content_observado(
                client,
                modelo=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=700,
                    response_mime_type=(
                        "application/json"
                    ),
                    response_schema=(
                        _LLMPlanResponse
                    ),
                ),
                operacao=(
                    "agentic_rag_query_planner"
                ),
                origem=(
                    "agentic_rag.planner"
                ),
                trace_id=trace_id,
                metadados={
                    "structured_output": True,
                    "question_content_logged": (
                        False
                    ),
                },
            )
        )

    with traced_resilience_operation(
        planner_resilience_policy
    ):
        response = (
            resilience_runtime.execute(
                policy=(
                    planner_resilience_policy
                ),
                operation=(
                    generate_plan_attempt
                ),
                deadline_budget=(
                    deadline_budget
                ),
                minimum_retry_attempt_seconds=(
                    0.50
                ),
            )
        )

    parsed = getattr(
        response,
        "parsed",
        None,
    )

    if isinstance(
        parsed,
        _LLMPlanResponse,
    ):
        llm_plan = parsed

    elif parsed is not None:
        llm_plan = _LLMPlanResponse.model_validate(parsed)

    else:
        response_text = str(
            getattr(
                response,
                "text",
                "",
            )
            or ""
        ).strip()

        llm_plan = _LLMPlanResponse.model_validate_json(response_text)

    normalized_steps: list[ResearchSubquery] = []

    for index, item in enumerate(
        llm_plan.steps,
        start=1,
    ):
        if item.source == ResearchSource.FINANCIAL_HISTORY and not user_id:
            continue

        normalized_steps.append(
            _build_step(
                index=index,
                question=item.question,
                source=item.source,
                priority=item.priority,
                required=item.required,
                top_k=item.top_k,
                max_results=item.max_results,
                suffix="llm",
            )
        )

    if not normalized_steps:
        raise ValueError("O planner LLM não produziu etapas executáveis.")

    return ResearchPlan(
        original_question=question,
        language=language,
        complexity=llm_plan.complexity,
        rationale=llm_plan.rationale,
        subqueries=sorted(
            normalized_steps,
            key=lambda item: -item.priority,
        ),
        generation_mode=(PlanGenerationMode.LLM),
        requires_iteration=(llm_plan.requires_iteration or len(normalized_steps) > 1),
        max_rounds=_read_int_environment(
            "INNA_AGENTIC_RAG_MAX_ROUNDS",
            2,
            minimum=1,
            maximum=3,
        ),
        metadata={
            "planner": "gemini_structured_v1",
            "model": model,
            "trusted_user_context_available": bool(user_id),
            "tool_selection_policy": ("deny_by_default"),
        },
    )


def _record_adaptive_planner_metric(
    *,
    started_at: float,
    planner_mode: str,
    query_complexity: str,
    planner_route: str,
    cache_hit: bool,
    plan_source: str,
    plan_valid: bool,
    fallback_used: bool,
    planner_outcome: str,
) -> bool:
    """
    Registra exatamente o resultado final do
    Adaptive Planner sem conteúdo do usuário.

    A falha desta observabilidade nunca altera
    o resultado do planejamento.
    """

    if planner_mode != "adaptive":
        return False

    try:
        duration_ms = max(
            (
                perf_counter()
                - started_at
            )
            * 1000.0,
            0.0,
        )

        event = PlannerMetricEvent(
            planner_mode=planner_mode,
            query_complexity=(
                query_complexity
            ),
            planner_route=planner_route,
            cache_hit=cache_hit,
            plan_source=plan_source,
            plan_valid=plan_valid,
            fallback_used=fallback_used,
            duration_ms=duration_ms,
            planner_outcome=planner_outcome,
        )

        return bool(
            record_planner_metric_event(
                event
            )
        )

    except Exception:
        return False


def create_research_plan(
    question: str,
    *,
    language: str = "pt",
    user_id: str | None = None,
    intent: str = "unknown",
    planner_mode: str | None = None,
    trace_id: str | None = None,
) -> ResearchPlan:
    planning_started_at = perf_counter()

    normalized_question = str(question or "").strip()
    normalized_language = str(language or "pt").strip().lower()

    if len(normalized_question) < 3:
        raise ValueError("A pergunta precisa possuir pelo menos três caracteres.")

    mode = (
        str(
            planner_mode
            or os.getenv(
                "INNA_AGENTIC_RAG_PLANNER_MODE",
                "deterministic",
            )
            or "deterministic"
        )
        .strip()
        .lower()
    )

    effective_mode = mode

    if mode == "adaptive":
        adaptive_assessment = (
            assess_query_complexity(
                normalized_question
            )
        )

        effective_mode = (
            "llm"
            if (
                adaptive_assessment.complexity
                == ResearchComplexity.COMPLEX
            )
            else "deterministic"
        )

    if effective_mode != "llm":
        deterministic_plan = (
            _build_deterministic_plan(
                question=normalized_question,
                language=normalized_language,
                user_id=user_id,
            )
        )

        _set_planner_trace_attributes(
            generation_mode="deterministic",
            cache_enabled=False,
            cache_status="not_applicable",
        )

        if mode == "adaptive":
            _set_planner_route_trace(
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="deterministic",
                cache_hit=False,
                plan_source="deterministic",
                plan_valid=True,
                fallback_used=False,
            )

        if mode == "adaptive":
            _record_adaptive_planner_metric(
                started_at=planning_started_at,
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="deterministic",
                cache_hit=False,
                plan_source="deterministic",
                plan_valid=True,
                fallback_used=False,
                planner_outcome="success",
            )

        return deterministic_plan

    try:
        cache_enabled = (
            is_planner_cache_enabled()
        )

        if cache_enabled:
            cached_plan = (
                read_planner_cache(
                    question=(
                        normalized_question
                    ),
                    language=(
                        normalized_language
                    ),
                    user_id=user_id,
                    intent=intent,
                )
            )

            if cached_plan is not None:
                cached_validation = (
                    validate_llm_research_plan(
                        cached_plan,
                        question=normalized_question,
                        language=normalized_language,
                        user_id=user_id,
                    )
                )

                if cached_validation.valid:
                    _set_planner_validation_trace(
                        status="valid_cached",
                        reason="valid",
                        fallback_used=False,
                    )

                    _set_planner_trace_attributes(
                        generation_mode="llm",
                        cache_enabled=True,
                        cache_status="hit",
                        cache_backend="redis",
                        cache_stored=True,
                    )

                    if mode == "adaptive":
                        _set_planner_route_trace(
                            planner_mode=mode,
                            query_complexity=(
                                adaptive_assessment.complexity.value
                            ),
                            planner_route="redis_hit",
                            cache_hit=True,
                            plan_source="cache",
                            plan_valid=True,
                            fallback_used=False,
                        )

                    if mode == "adaptive":
                        _record_adaptive_planner_metric(
                            started_at=planning_started_at,
                            planner_mode=mode,
                            query_complexity=(
                                adaptive_assessment.complexity.value
                            ),
                            planner_route="redis_hit",
                            cache_hit=True,
                            plan_source="cache",
                            plan_valid=True,
                            fallback_used=False,
                            planner_outcome="success",
                        )

                    return cached_plan

                _set_planner_validation_trace(
                    status="rejected_cached",
                    reason=cached_validation.reason,
                    fallback_used=False,
                )

                _set_planner_trace_attributes(
                    generation_mode="llm",
                    cache_enabled=True,
                    cache_status="invalid_hit",
                    cache_backend="redis",
                    cache_stored=True,
                )

        llm_plan = _build_llm_plan(
            question=normalized_question,
            language=normalized_language,
            user_id=user_id,
            trace_id=trace_id,
        )

        validation = validate_llm_research_plan(
            llm_plan,
            question=normalized_question,
            language=normalized_language,
            user_id=user_id,
        )

        if not validation.valid:
            _set_planner_validation_trace(
                status="rejected",
                reason=validation.reason,
                fallback_used=True,
            )

            raise ValueError(
                "invalid_llm_plan:"
                + validation.reason
            )

        _set_planner_validation_trace(
            status="valid",
            reason="valid",
            fallback_used=False,
        )

        if not cache_enabled:
            _set_planner_trace_attributes(
                generation_mode="llm",
                cache_enabled=False,
                cache_status="disabled",
            )

            if mode == "adaptive":
                _set_planner_route_trace(
                    planner_mode=mode,
                    query_complexity=(
                        adaptive_assessment.complexity.value
                    ),
                    planner_route="gemini",
                    cache_hit=False,
                    plan_source="gemini",
                    plan_valid=True,
                    fallback_used=False,
                )

            if mode == "adaptive":
                _record_adaptive_planner_metric(
                    started_at=planning_started_at,
                    planner_mode=mode,
                    query_complexity=(
                        adaptive_assessment.complexity.value
                    ),
                    planner_route="gemini",
                    cache_hit=False,
                    plan_source="gemini",
                    plan_valid=True,
                    fallback_used=False,
                    planner_outcome="success",
                )

            return llm_plan

        stored = write_planner_cache(
            plan=llm_plan,
            question=normalized_question,
            language=normalized_language,
            user_id=user_id,
            intent=intent,
        )

        miss_plan = mark_planner_cache_miss(
            llm_plan,
            stored=stored,
        )

        _set_planner_trace_attributes(
            generation_mode="llm",
            cache_enabled=True,
            cache_status="miss",
            cache_backend="redis",
            cache_stored=stored,
        )

        if mode == "adaptive":
            _set_planner_route_trace(
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="gemini",
                cache_hit=False,
                plan_source="gemini",
                plan_valid=True,
                fallback_used=False,
            )

        if mode == "adaptive":
            _record_adaptive_planner_metric(
                started_at=planning_started_at,
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="gemini",
                cache_hit=False,
                plan_source="gemini",
                plan_valid=True,
                fallback_used=False,
                planner_outcome="success",
            )

        return miss_plan

    except Exception as exc:
        fallback = _build_deterministic_plan(
            question=normalized_question,
            language=normalized_language,
            user_id=user_id,
        )

        fallback_data = fallback.model_dump(mode="python")
        fallback_data["generation_mode"] = PlanGenerationMode.FALLBACK
        fallback_data["metadata"] = {
            **fallback.metadata,
            "planner": ("deterministic_after_llm_failure"),
            "llm_error_type": (type(exc).__name__),
        }

        fallback_plan = ResearchPlan.model_validate(
            fallback_data
        )

        if mode == "adaptive":
            _set_planner_route_trace(
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="fallback",
                cache_hit=False,
                plan_source="deterministic",
                plan_valid=True,
                fallback_used=True,
            )

        if mode == "adaptive":
            _record_adaptive_planner_metric(
                started_at=planning_started_at,
                planner_mode=mode,
                query_complexity=(
                    adaptive_assessment.complexity.value
                ),
                planner_route="fallback",
                cache_hit=False,
                plan_source="deterministic",
                plan_valid=True,
                fallback_used=True,
                planner_outcome="fallback",
            )

        return fallback_plan


class QueryPlanner:
    """
    Fachada testável do planejador de consultas.
    """

    def plan(
        self,
        question: str,
        *,
        language: str = "pt",
        user_id: str | None = None,
        intent: str = "unknown",
        planner_mode: str | None = None,
        trace_id: str | None = None,
    ) -> ResearchPlan:
        planning_started_at = perf_counter()

        effective_mode = (
            str(
                planner_mode
                or os.getenv(
                    "INNA_AGENTIC_RAG_PLANNER_MODE",
                    "deterministic",
                )
                or "deterministic"
            )
            .strip()
            .lower()
        )

        try:
            return create_research_plan(
                question,
                language=language,
                user_id=user_id,
                intent=intent,
                planner_mode=planner_mode,
                trace_id=trace_id,
            )

        except Exception:
            _record_adaptive_planner_metric(
                started_at=planning_started_at,
                planner_mode=effective_mode,
                query_complexity="unknown",
                planner_route="error",
                cache_hit=False,
                plan_source="none",
                plan_valid=False,
                fallback_used=False,
                planner_outcome="error",
            )

            raise


__all__ = [
    "QueryComplexityAssessment",
    "QueryPlanner",
    "assess_query_complexity",
    "create_research_plan",
]
