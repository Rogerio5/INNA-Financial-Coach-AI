"""Adiciona Atendimento e Suporte Inteligente ao registro empresarial."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_business_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_business_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("intelligent_support_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


INTELLIGENT_SUPPORT_DEFINITION = """
INTELLIGENT_SUPPORT_SOLUTION = PlatformBusinessSolution(
    solution_id="intelligent_support",
    icon="🎧",
    title="Atendimento e Suporte Inteligente",
    description=(
        "Solução empresarial para atendimento omnichannel, "
        "assistentes conversacionais, gestão de chamados, "
        "autoatendimento, qualidade, segurança e analytics."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="support_omnichannel_intake",
            title="💬 Atendimento omnichannel",
            capabilities=(
                BusinessCapability(
                    capability_id="support_channel_integrations",
                    title="🔌 Integração de canais",
                    description=(
                        "Integração de chat, e-mail, aplicativos, "
                        "mensageria, voz, formulários e APIs."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                        "voice_audio_speech_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_unified_inbox",
                    title="📥 Caixa de entrada unificada",
                    description=(
                        "Centralização de mensagens, solicitações, "
                        "interações e eventos recebidos por diversos canais."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "data_platform_governance",
                        "crm_sales_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_customer_context",
                    title="👤 Contexto unificado do cliente",
                    description=(
                        "Consolidação de identidade, histórico, perfil, "
                        "preferências, solicitações e relacionamento."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="support_conversational_ai",
            title="🤖 IA conversacional",
            capabilities=(
                BusinessCapability(
                    capability_id="support_intent_classification",
                    title="🧠 Intenção e classificação da solicitação",
                    description=(
                        "Identificação do assunto, objetivo, prioridade, "
                        "categoria e contexto da mensagem recebida."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "knowledge_graph_semantic_ai",
                        "ai_evaluation_benchmarks_red_team",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_grounded_answers",
                    title="📚 Respostas fundamentadas em conhecimento",
                    description=(
                        "Geração de respostas apoiadas em documentos, "
                        "políticas, manuais e bases empresariais autorizadas."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "document_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_voice_multimodal",
                    title="🎙️ Atendimento por voz e multimodal",
                    description=(
                        "Processamento de voz, texto, imagens, anexos "
                        "e outros formatos usados no atendimento."
                    ),
                    technology_dependencies=(
                        "voice_audio_speech_ai",
                        "multimodal_ai",
                        "document_ai",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="support_cases_workflows",
            title="🎫 Chamados, casos e workflows",
            capabilities=(
                BusinessCapability(
                    capability_id="support_case_creation_routing",
                    title="🎫 Criação e roteamento de chamados",
                    description=(
                        "Abertura automática, categorização e envio "
                        "do chamado para equipe, fila ou responsável."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_priority_sla",
                    title="⏱️ Prioridade, filas e SLA",
                    description=(
                        "Controle de prioridade, tempo de espera, prazo, "
                        "nível de serviço e risco de atraso."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_human_handoff",
                    title="👤 Transferência para atendimento humano",
                    description=(
                        "Encaminhamento do atendimento com contexto, "
                        "histórico, resumo e motivo da transferência."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "crm_sales_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="support_knowledge_self_service",
            title="📚 Conhecimento e autoatendimento",
            capabilities=(
                BusinessCapability(
                    capability_id="support_knowledge_base",
                    title="📚 Base de conhecimento empresarial",
                    description=(
                        "Organização de artigos, respostas, manuais, "
                        "procedimentos, políticas e perguntas frequentes."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "document_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_self_service_portal",
                    title="🌐 Portal de autoatendimento",
                    description=(
                        "Experiência digital para consultas, solicitações, "
                        "acompanhamento e resolução orientada."
                    ),
                    technology_dependencies=(
                        "digital_experiences_intelligent_interfaces",
                        "site_app_generator",
                        "mobile_apps_omnichannel_experiences",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_content_lifecycle",
                    title="🔄 Ciclo de vida do conhecimento",
                    description=(
                        "Criação, revisão, aprovação, publicação, "
                        "versionamento e desativação de conteúdos."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "business_automation",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="support_quality_security",
            title="✅ Qualidade, segurança e conformidade",
            capabilities=(
                BusinessCapability(
                    capability_id="support_quality_review",
                    title="✅ Avaliação de qualidade do atendimento",
                    description=(
                        "Análise de respostas, aderência, clareza, "
                        "resolução, consistência e experiência do cliente."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "ai_evaluation_benchmarks_red_team",
                        "ai_bias_quality_monitoring",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_privacy_access",
                    title="🔐 Privacidade e controle de acesso",
                    description=(
                        "Proteção de dados, permissões, mascaramento, "
                        "identidade e acesso conforme necessidade."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "zero_trust_identity_access",
                        "privacy_enhancing_technologies",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_audit_evidence",
                    title="🧾 Auditoria e evidências",
                    description=(
                        "Registro de mensagens, ações, decisões, "
                        "transferências, alterações e responsáveis."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "operational_security_resilience",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="support_analytics_optimization",
            title="📊 Analytics e otimização",
            capabilities=(
                BusinessCapability(
                    capability_id="support_operational_analytics",
                    title="📊 Indicadores de atendimento",
                    description=(
                        "Volume, tempo de resposta, resolução, SLA, "
                        "filas, canais, assuntos e produtividade."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_feedback_sentiment",
                    title="💭 Feedback e sinais de satisfação",
                    description=(
                        "Análise de avaliações, comentários, sentimento, "
                        "motivos de insatisfação e oportunidades."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "crm_sales_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="support_demand_forecasting",
                    title="📈 Previsão de demanda e capacidade",
                    description=(
                        "Análise de sazonalidade, crescimento, volume "
                        "esperado, necessidade de equipes e canais."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                    ),
                ),
            ),
        ),
    ),
)


"""


def create_backup() -> None:
    """Cria cópias dos arquivos antes da alteração."""

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for source_path in (
        REGISTRY_PATH,
        TEST_PATH,
    ):
        shutil.copy2(
            source_path,
            BACKUP_ROOT / source_path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")


def update_registry() -> None:
    """Adiciona Atendimento Inteligente ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "INTELLIGENT_SUPPORT_SOLUTION = PlatformBusinessSolution(" in source:
        print("INTELLIGENT_SUPPORT_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_BUSINESS_SOLUTIONS: tuple[
    PlatformBusinessSolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro empresarial não encontrada.")

    source = source.replace(
        registry_anchor,
        (INTELLIGENT_SUPPORT_DEFINITION + registry_anchor),
        1,
    )

    old_registry = """    DOCUMENT_AI_SOLUTION,
    BUSINESS_AUTOMATION_SOLUTION,
)"""

    new_registry = """    DOCUMENT_AI_SOLUTION,
    BUSINESS_AUTOMATION_SOLUTION,
    INTELLIGENT_SUPPORT_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Registro atual das soluções empresariais não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("INTELLIGENT_SUPPORT_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_intelligent_support_solution_is_complete" in source:
        print("INTELLIGENT_SUPPORT_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    DOCUMENT_AI_SOLUTION,\n"

    import_replacement = (
        "    DOCUMENT_AI_SOLUTION,\n    INTELLIGENT_SUPPORT_SOLUTION,\n"
    )

    if import_anchor not in source:
        raise RuntimeError("Importação do Document AI não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 2"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 3"

    if old_count not in source:
        raise RuntimeError("Contagem atual de duas soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_intelligent_support_solution_is_complete():
    assert (
        INTELLIGENT_SUPPORT_SOLUTION.solution_id
        == "intelligent_support"
    )
    assert (
        INTELLIGENT_SUPPORT_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        INTELLIGENT_SUPPORT_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        INTELLIGENT_SUPPORT_SOLUTION.areas
    ) == 6
    assert (
        INTELLIGENT_SUPPORT_SOLUTION.capability_count
        == 18
    )


def test_intelligent_support_lookup():
    assert (
        platform_business_solution(
            "intelligent_support"
        )
        is INTELLIGENT_SUPPORT_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("INTELLIGENT_SUPPORT_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        INTELLIGENT_SUPPORT_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 3

    assert (
        platform_business_solution("intelligent_support")
        is INTELLIGENT_SUPPORT_SOLUTION
    )

    assert len(INTELLIGENT_SUPPORT_SOLUTION.areas) == 6

    assert INTELLIGENT_SUPPORT_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 18
    assert total_capabilities == 53

    print("SPECIALIZED_BUSINESS_SOLUTIONS=3")
    print("TOTAL_BUSINESS_AREAS=18")
    print("TOTAL_BUSINESS_CAPABILITIES=53")
    print("INTELLIGENT_SUPPORT_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
