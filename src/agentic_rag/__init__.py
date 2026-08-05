"""
Núcleo do Agentic RAG da INNA.

Fase 1:
- contratos Pydantic;
- Query Planner.

Fase 2:
- Router Agent determinístico;
- ToolCall formal;
- contexto confiável;
- auditoria sanitizada.

Fase 3:
- Evidence Collector;
- proveniência;
- hashes determinísticos;
- relevância lexical;
- deduplicação;
- filtragem de identidade.
"""

from src.agentic_rag.collector import (
    COLLECTOR_VERSION,
    EvidenceCollectionError,
    EvidenceCollector,
    UnsafeToolOutputError,
    UnsupportedEvidenceSourceError,
    collect_evidence_from_tool_output,
    collect_evidence_from_tool_result,
    collect_history_evidence,
    collect_rag_evidence,
)
from src.agentic_rag.contracts import (
    ALLOWED_TOOL_BY_SOURCE,
    EvidenceCollectionResult,
    EvidenceCollectionStatus,
    EvidenceItem,
    PlanGenerationMode,
    ResearchComplexity,
    ResearchPlan,
    ResearchSource,
    ResearchSubquery,
)
from src.agentic_rag.evidence import (
    canonical_output_sha256,
    content_sha256,
    deduplicate_evidence,
    evidence_terms,
    lexical_relevance,
    normalize_evidence_text,
    token_jaccard_similarity,
)
from src.agentic_rag.planner import (
    QueryComplexityAssessment,
    QueryPlanner,
    assess_query_complexity,
    create_research_plan,
)
from src.agentic_rag.router import (
    MissingTrustedUserContextError,
    ResearchRoute,
    ResearchRoutingError,
    ResearchSourceRouter,
    build_tool_call,
    execute_routed_tool,
    route_research_plan,
    route_to_audit_payload,
)


from src.agentic_rag.contracts import (
    EvidenceGap,
    EvidenceGapType,
    SufficiencyAssessment,
    SufficiencyDecision,
)


from src.agentic_rag.sufficiency import (
    SUFFICIENCY_VERSION,
    SufficiencyEvaluator,
    assess_evidence_sufficiency,
    assessment_to_audit_payload,
    resolve_sufficiency_threshold,
)


from src.agentic_rag.research_agent import (
    RESEARCH_AGENT_VERSION,
    ClockFunction,
    IterativeResearchAgent,
    ResearchAgentResult,
    ResearchAgentStatus,
    ResearchExecutionError,
    ResearchExecutionPolicy,
    ResearchExecutorContractError,
    ResearchRoundSummary,
    ResearchRoutingContractError,
    ResearchStopReason,
    RetryDisposition,
    RouteExecutor,
    SleepFunction,
    TechnicalRetryEvent,
    ToolRuntimeReportedError,
    create_runtime_route_executor,
    research_result_to_audit_payload,
    run_research_agent,
    run_research_agent_with_runtime,
)


from src.agentic_rag.synthesizer import (
    SYNTHESIS_VERSION,
    GroundedCitation,
    GroundedSynthesisError,
    GroundedSynthesisPolicy,
    GroundedSynthesisResult,
    GroundedSynthesizer,
    ModelExecutor,
    PreparedEvidence,
    SynthesisExecutorContractError,
    SynthesisFailureReason,
    SynthesisStatus,
    SynthesisValidation,
    build_grounded_synthesis_prompt,
    create_synthesis_model_executor,
    prepare_grounded_evidence,
    synthesis_result_to_audit_payload,
    synthesize_research_result,
    validate_grounded_answer,
)

__all__ = [
    "ALLOWED_TOOL_BY_SOURCE",
    "COLLECTOR_VERSION",
    "EvidenceCollectionError",
    "EvidenceCollectionResult",
    "EvidenceCollectionStatus",
    "EvidenceCollector",
    "EvidenceItem",
    "MissingTrustedUserContextError",
    "PlanGenerationMode",
    "QueryComplexityAssessment",
    "QueryPlanner",
    "ResearchComplexity",
    "ResearchPlan",
    "ResearchRoute",
    "ResearchRoutingError",
    "ResearchSource",
    "ResearchSourceRouter",
    "ResearchSubquery",
    "UnsafeToolOutputError",
    "UnsupportedEvidenceSourceError",
    "assess_query_complexity",
    "build_tool_call",
    "canonical_output_sha256",
    "collect_evidence_from_tool_output",
    "collect_evidence_from_tool_result",
    "collect_history_evidence",
    "collect_rag_evidence",
    "content_sha256",
    "create_research_plan",
    "deduplicate_evidence",
    "evidence_terms",
    "execute_routed_tool",
    "lexical_relevance",
    "normalize_evidence_text",
    "route_research_plan",
    "route_to_audit_payload",
    "token_jaccard_similarity",
    "EvidenceGap",
    "EvidenceGapType",
    "SUFFICIENCY_VERSION",
    "SufficiencyAssessment",
    "SufficiencyDecision",
    "SufficiencyEvaluator",
    "assess_evidence_sufficiency",
    "assessment_to_audit_payload",
    "resolve_sufficiency_threshold",
    "RESEARCH_AGENT_VERSION",
    "IterativeResearchAgent",
    "ResearchAgentResult",
    "ResearchAgentStatus",
    "ResearchExecutionError",
    "ResearchExecutionPolicy",
    "ResearchExecutorContractError",
    "ResearchRoundSummary",
    "ResearchRoutingContractError",
    "ResearchStopReason",
    "RouteExecutor",
    "create_runtime_route_executor",
    "research_result_to_audit_payload",
    "run_research_agent",
    "run_research_agent_with_runtime",
    "ClockFunction",
    "RetryDisposition",
    "SleepFunction",
    "TechnicalRetryEvent",
    "ToolRuntimeReportedError",
    "SYNTHESIS_VERSION",
    "GroundedCitation",
    "GroundedSynthesisError",
    "GroundedSynthesisPolicy",
    "GroundedSynthesisResult",
    "GroundedSynthesizer",
    "ModelExecutor",
    "PreparedEvidence",
    "SynthesisExecutorContractError",
    "SynthesisFailureReason",
    "SynthesisStatus",
    "SynthesisValidation",
    "build_grounded_synthesis_prompt",
    "create_synthesis_model_executor",
    "prepare_grounded_evidence",
    "synthesis_result_to_audit_payload",
    "synthesize_research_result",
    "validate_grounded_answer",
]
