"""Adiciona CRM e Experiência do Cliente ao registro empresarial."""

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
    / ("crm_customer_experience_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


CRM_CUSTOMER_EXPERIENCE_DEFINITION = """
CRM_CUSTOMER_EXPERIENCE_SOLUTION = PlatformBusinessSolution(
    solution_id="crm_sales_intelligence",
    icon="🤝",
    title="CRM e Experiência do Cliente",
    description=(
        "Solução empresarial para cadastro unificado, "
        "relacionamento, vendas, atendimento, campanhas, "
        "fidelização, experiência e inteligência de clientes."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="crm_customer_data_profile",
            title="👤 Cadastro e visão unificada do cliente",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_customer_registration",
                    title="👤 Cadastro centralizado de clientes",
                    description=(
                        "Organização de clientes, contatos, empresas, "
                        "responsáveis, preferências e informações comerciais."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_customer_360_view",
                    title="🔎 Visão 360 graus do cliente",
                    description=(
                        "Consolidação de interações, compras, chamados, "
                        "oportunidades, documentos e histórico."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_customer_identity_resolution",
                    title="🪪 Identidade e unificação de registros",
                    description=(
                        "Identificação de registros duplicados, relações "
                        "entre contatos e consolidação de perfis."
                    ),
                    technology_dependencies=(
                        "digital_identity_verifiable_credentials",
                        "data_platform_governance",
                        "privacy_enhancing_technologies",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="crm_sales_pipeline",
            title="💼 Vendas e oportunidades",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_lead_management",
                    title="🎯 Gestão de leads",
                    description=(
                        "Captura, cadastro, classificação, origem, "
                        "priorização e acompanhamento de potenciais clientes."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "business_automation",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_sales_pipeline_management",
                    title="📈 Funil e pipeline de vendas",
                    description=(
                        "Acompanhamento de etapas, responsáveis, valores, "
                        "prazos, probabilidades e movimentações."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "real_time_event_intelligence",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_sales_forecasting",
                    title="🔮 Previsão de vendas e oportunidades",
                    description=(
                        "Projeções de receita, conversão, fechamento, "
                        "capacidade comercial e cenários."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "simulation_optimization_operations_research",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="crm_relationship_service",
            title="💬 Relacionamento e atendimento",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_interaction_history",
                    title="💬 Histórico de interações",
                    description=(
                        "Registro de mensagens, reuniões, ligações, "
                        "atendimentos, negociações e compromissos."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "voice_audio_speech_ai",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_omnichannel_relationship",
                    title="📱 Relacionamento omnichannel",
                    description=(
                        "Integração de chat, e-mail, aplicativos, "
                        "mensageria, formulários e outros canais."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_customer_requests",
                    title="🎫 Solicitações, casos e pendências",
                    description=(
                        "Gestão de solicitações, responsáveis, prioridades, "
                        "prazos, encaminhamentos e resolução."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "intelligent_support",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="crm_marketing_campaigns",
            title="📣 Segmentação e campanhas",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_customer_segmentation",
                    title="👥 Segmentação inteligente de clientes",
                    description=(
                        "Agrupamento por perfil, comportamento, valor, "
                        "interesses, frequência e relacionamento."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "multimodal_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_campaign_management",
                    title="📣 Gestão de campanhas",
                    description=(
                        "Planejamento, públicos, canais, conteúdos, "
                        "execução, resultados e acompanhamento."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_personalized_offers",
                    title="🎁 Ofertas e comunicações personalizadas",
                    description=(
                        "Personalização assistida de mensagens, ofertas, "
                        "recomendações e próximos passos."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "multimodal_ai",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="crm_experience_loyalty",
            title="⭐ Experiência e fidelização",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_customer_feedback",
                    title="⭐ Feedback e satisfação do cliente",
                    description=(
                        "Coleta e análise de avaliações, comentários, "
                        "pesquisas e motivos de satisfação ou insatisfação."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "intelligent_support",
                        "tools_analytics",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_loyalty_programs",
                    title="🎁 Programas de fidelidade",
                    description=(
                        "Gestão de pontos, níveis, benefícios, recompensas, "
                        "campanhas e engajamento."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "api_integrations_connectors",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_churn_retention",
                    title="⚠️ Retenção e risco de cancelamento",
                    description=(
                        "Identificação de sinais de abandono, redução "
                        "de relacionamento e oportunidades de retenção."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="crm_analytics_governance",
            title="📊 Analytics, segurança e governança",
            capabilities=(
                BusinessCapability(
                    capability_id="crm_sales_customer_analytics",
                    title="📊 Analytics comercial e de clientes",
                    description=(
                        "Indicadores de leads, oportunidades, conversão, "
                        "receita, retenção, campanhas e atendimento."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_privacy_permissions",
                    title="🔐 Privacidade e permissões",
                    description=(
                        "Controle de acesso, consentimentos, preferências "
                        "de comunicação e proteção dos dados pessoais."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "zero_trust_identity_access",
                        "technology_governance_policy_compliance",
                    ),
                ),
                BusinessCapability(
                    capability_id="crm_audit_data_quality",
                    title="🧾 Auditoria e qualidade cadastral",
                    description=(
                        "Monitoramento de duplicidades, dados incompletos, "
                        "alterações, responsáveis e rastreabilidade."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "quality_process_management",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
    ),
)


"""


def create_backup() -> None:
    """Cria cópias antes da alteração."""

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
    """Adiciona CRM e Experiência do Cliente."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "CRM_CUSTOMER_EXPERIENCE_SOLUTION = PlatformBusinessSolution(" in source:
        print("CRM_CUSTOMER_EXPERIENCE_ALREADY_PRESENT=OK")
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
        (CRM_CUSTOMER_EXPERIENCE_DEFINITION + registry_anchor),
        1,
    )

    old_registry = """    DATA_BI_COPILOT_SOLUTION,
    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
)"""

    new_registry = """    DATA_BI_COPILOT_SOLUTION,
    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro empresarial não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CRM_CUSTOMER_EXPERIENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_crm_customer_experience_solution_is_complete" in source:
        print("CRM_CUSTOMER_EXPERIENCE_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_business_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Bloco de importações empresariais não encontrado.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final do bloco de importações não encontrado.")

    import_block = source[import_start:import_end]

    if "CRM_CUSTOMER_EXPERIENCE_SOLUTION" not in import_block:
        source = (
            source[:import_end]
            + ("    CRM_CUSTOMER_EXPERIENCE_SOLUTION,\n")
            + source[import_end:]
        )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 5"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 6"

    if old_count not in source:
        raise RuntimeError("Contagem atual de cinco soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_crm_customer_experience_solution_is_complete():
    assert (
        CRM_CUSTOMER_EXPERIENCE_SOLUTION.solution_id
        == "crm_sales_intelligence"
    )
    assert (
        CRM_CUSTOMER_EXPERIENCE_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        CRM_CUSTOMER_EXPERIENCE_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        CRM_CUSTOMER_EXPERIENCE_SOLUTION.areas
    ) == 6
    assert (
        CRM_CUSTOMER_EXPERIENCE_SOLUTION.capability_count
        == 18
    )


def test_crm_customer_experience_lookup():
    assert (
        platform_business_solution(
            "crm_sales_intelligence"
        )
        is CRM_CUSTOMER_EXPERIENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CRM_CUSTOMER_EXPERIENCE_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        CRM_CUSTOMER_EXPERIENCE_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 6

    assert (
        platform_business_solution("crm_sales_intelligence")
        is CRM_CUSTOMER_EXPERIENCE_SOLUTION
    )

    assert len(CRM_CUSTOMER_EXPERIENCE_SOLUTION.areas) == 6

    assert CRM_CUSTOMER_EXPERIENCE_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 36
    assert total_capabilities == 107

    print("SPECIALIZED_BUSINESS_SOLUTIONS=6")
    print("TOTAL_BUSINESS_AREAS=36")
    print("TOTAL_BUSINESS_CAPABILITIES=107")
    print("CRM_CUSTOMER_EXPERIENCE_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
