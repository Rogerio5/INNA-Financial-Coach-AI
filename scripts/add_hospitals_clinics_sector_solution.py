"""Adiciona a solução setorial de Hospitais e Clínicas."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_sector_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_sector_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("hospitals_clinics_sector_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


HOSPITALS_CLINICS_DEFINITION = """
HOSPITALS_CLINICS_SOLUTION = PlatformSectorSolution(
    solution_id="hospitals_clinics",
    icon="🏥",
    title="Hospitais e Clínicas",
    description=(
        "Solução para recepção, agenda, fluxo de pacientes, "
        "documentos, prontuários, leitos, recursos, estoque, "
        "faturamento, qualidade e indicadores operacionais."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="healthcare_reception_access",
            title="👤 Atendimento e recepção",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_patient_registration",
                    title="👤 Cadastro administrativo de pacientes",
                    description=(
                        "Cadastro de pacientes, responsáveis, contatos, "
                        "documentos, preferências e dados administrativos."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_digital_reception",
                    title="🖥️ Recepção e direcionamento digital",
                    description=(
                        "Check-in, confirmação de dados, orientação "
                        "administrativa e direcionamento para atendimento."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "digital_experiences_intelligent_interfaces",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_patient_communication",
                    title="💬 Comunicação e suporte ao paciente",
                    description=(
                        "Mensagens, orientações administrativas, "
                        "confirmações, notificações e acompanhamento."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_schedule_patient_flow",
            title="📅 Agenda e fluxo de pacientes",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_intelligent_schedule",
                    title="📅 Agenda integrada de atendimentos",
                    description=(
                        "Agendamento de consultas, exames, procedimentos, "
                        "retornos, profissionais e salas."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "api_integrations_connectors",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_queue_flow_management",
                    title="🚶 Filas e fluxo de pacientes",
                    description=(
                        "Acompanhamento de filas, espera, chamadas, "
                        "movimentações e gargalos operacionais."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_capacity_coordination",
                    title="🏥 Coordenação de capacidade assistencial",
                    description=(
                        "Visão administrativa da capacidade, ocupação, "
                        "recursos disponíveis e demanda por atendimento."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "digital_twins_simulation",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_records_documents",
            title="📄 Documentos e prontuários",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_digital_records",
                    title="🗂️ Prontuários e registros digitais",
                    description=(
                        "Organização segura de registros, documentos, "
                        "históricos, anexos e dados relacionados."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "privacy_data_protection_lgpd",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_document_organization",
                    title="📑 Organização inteligente de documentos",
                    description=(
                        "Classificação, busca e organização assistida "
                        "de laudos, relatórios, exames e formulários."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_forms_consents",
                    title="✍️ Formulários, termos e consentimentos",
                    description=(
                        "Gestão de formulários, termos, assinaturas, "
                        "consentimentos e evidências documentais."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_beds_resources",
            title="🛏️ Leitos, salas e recursos",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_bed_capacity",
                    title="🛏️ Gestão de leitos e capacidade",
                    description=(
                        "Monitoramento de ocupação, disponibilidade, "
                        "reservas, movimentações e capacidade operacional."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "digital_twins_simulation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_rooms_equipment",
                    title="🏥 Salas, equipamentos e recursos",
                    description=(
                        "Gestão de salas, equipamentos, disponibilidade, "
                        "utilização, inspeções e manutenção."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "iot_edge_intelligence",
                        "digital_twins_simulation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_inventory_supplies",
            title="📦 Estoque, farmácia e suprimentos",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_supply_inventory",
                    title="📦 Estoque de materiais e suprimentos",
                    description=(
                        "Controle de materiais, insumos, entradas, "
                        "saídas, consumo, inventários e disponibilidade."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "supply_chain_procurement_logistics",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_medication_traceability",
                    title="💊 Lotes, validade e rastreabilidade",
                    description=(
                        "Monitoramento administrativo de lotes, validade, "
                        "movimentações, disponibilidade e alertas."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                        "erp_business_operations",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_smart_replenishment",
                    title="🔄 Reposição inteligente de suprimentos",
                    description=(
                        "Previsão de consumo, pontos de reposição, "
                        "alertas e apoio ao planejamento de compras."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_billing_insurance",
            title="💰 Faturamento e convênios",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_billing_management",
                    title="💰 Faturamento administrativo",
                    description=(
                        "Organização de cobranças, contas, pagamentos, "
                        "recebimentos, conciliação e pendências."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "erp_business_operations",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_insurance_authorizations",
                    title="📋 Autorizações e convênios",
                    description=(
                        "Controle de solicitações, documentos, "
                        "autorizações, prazos e retornos de convênios."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "document_ai",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_quality_safety",
            title="✅ Qualidade, segurança e conformidade",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_quality_processes",
                    title="✅ Qualidade e processos assistenciais",
                    description=(
                        "Gestão de processos, checklists, auditorias, "
                        "evidências, melhorias e controles de qualidade."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "technology_governance_policy_compliance",
                        "ai_certification_system_evidence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_incidents_risks",
                    title="⚠️ Incidentes, riscos e segurança",
                    description=(
                        "Registro e acompanhamento de ocorrências, "
                        "riscos operacionais, ações e evidências."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "responsible_ai_ethics_risk",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_analytics_operations",
            title="📊 Indicadores operacionais",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_operational_indicators",
                    title="📊 Indicadores hospitalares e clínicos",
                    description=(
                        "Ocupação, espera, agenda, produtividade, "
                        "recursos, estoque e desempenho operacional."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_demand_forecasting",
                    title="📈 Previsão de demanda e capacidade",
                    description=(
                        "Análise de padrões, sazonalidade, demanda "
                        "esperada e necessidades de capacidade."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "digital_twins_simulation",
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
    """Adiciona Hospitais e Clínicas ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "HOSPITALS_CLINICS_SOLUTION = PlatformSectorSolution(" in source:
        print("HOSPITALS_CLINICS_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_SECTOR_SOLUTIONS: tuple[
    PlatformSectorSolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro especializado não encontrada.")

    source = source.replace(
        registry_anchor,
        (HOSPITALS_CLINICS_DEFINITION + registry_anchor),
        1,
    )

    old_registry_tail = """    RETAIL_STORES_SOLUTION,
    DENTISTRY_SOLUTION,
)"""

    new_registry_tail = """    RETAIL_STORES_SOLUTION,
    DENTISTRY_SOLUTION,
    HOSPITALS_CLINICS_SOLUTION,
)"""

    if old_registry_tail not in source:
        raise RuntimeError("Final atual do registro especializado não encontrado.")

    source = source.replace(
        old_registry_tail,
        new_registry_tail,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("HOSPITALS_CLINICS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_hospitals_clinics_solution_is_complete" in source:
        print("HOSPITALS_CLINICS_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    DENTISTRY_SOLUTION,\n"

    import_replacement = "    DENTISTRY_SOLUTION,\n    HOSPITALS_CLINICS_SOLUTION,\n"

    if import_anchor not in source:
        raise RuntimeError("Âncora de importação dos testes não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 6"

    new_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 7"

    if old_count not in source:
        raise RuntimeError("Contagem atual de seis soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    expected_anchor = """        "dentistry",
    }"""

    expected_replacement = """        "dentistry",
        "hospitals_clinics",
    }"""

    if expected_anchor not in source:
        raise RuntimeError("Conjunto esperado das soluções não encontrado.")

    source = source.replace(
        expected_anchor,
        expected_replacement,
        1,
    )

    source += """


def test_hospitals_clinics_solution_is_complete():
    assert (
        HOSPITALS_CLINICS_SOLUTION.solution_id
        == "hospitals_clinics"
    )
    assert (
        HOSPITALS_CLINICS_SOLUTION.status
        is SectorSolutionStatus.PLANNED
    )
    assert (
        HOSPITALS_CLINICS_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        HOSPITALS_CLINICS_SOLUTION.areas
    ) == 8
    assert (
        HOSPITALS_CLINICS_SOLUTION.capability_count
        == 20
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("HOSPITALS_CLINICS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma a expansão final dos setores."""

    from src.platform_sector_solutions import (
        HOSPITALS_CLINICS_SOLUTION,
        PLATFORM_SECTOR_SOLUTIONS,
        platform_sector_solution,
    )

    assert len(PLATFORM_SECTOR_SOLUTIONS) == 7

    assert platform_sector_solution("hospitals_clinics") is HOSPITALS_CLINICS_SOLUTION

    assert len(HOSPITALS_CLINICS_SOLUTION.areas) == 8

    assert HOSPITALS_CLINICS_SOLUTION.capability_count == 20

    total_areas = sum(len(solution.areas) for solution in PLATFORM_SECTOR_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_SECTOR_SOLUTIONS
    )

    assert total_areas == 47
    assert total_capabilities == 121

    print("SPECIALIZED_SECTOR_SOLUTIONS=7")
    print("TOTAL_SECTOR_AREAS=47")
    print("TOTAL_SECTOR_CAPABILITIES=121")
    print("ALL_SECTOR_CARDS_HAVE_DETAILS=OK")
    print("HOSPITALS_CLINICS_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
