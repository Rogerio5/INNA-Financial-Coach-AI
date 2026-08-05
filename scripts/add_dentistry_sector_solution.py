"""Adiciona a solução setorial especializada de Odontologia."""

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
    / ("dentistry_sector_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


DENTISTRY_DEFINITION = """
DENTISTRY_SOLUTION = PlatformSectorSolution(
    solution_id="dentistry",
    icon="🦷",
    title="Odontologia",
    description=(
        "Solução para pacientes, prontuários, agenda, "
        "tratamentos, imagens, documentos, orçamentos, "
        "pagamentos, materiais e gestão odontológica."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="dentistry_patients_records",
            title="👤 Pacientes e prontuários",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_patient_registration",
                    title="👤 Cadastro completo de pacientes",
                    description=(
                        "Cadastro de pacientes, contatos, responsáveis, "
                        "preferências e informações administrativas."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_health_history",
                    title="📋 Histórico de saúde e atendimento",
                    description=(
                        "Organização de antecedentes informados, "
                        "atendimentos, observações e ocorrências."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "data_traceability_provenance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_digital_record",
                    title="🗂️ Prontuário odontológico digital",
                    description=(
                        "Registro estruturado da evolução, procedimentos, "
                        "documentos e histórico odontológico."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "knowledge_graph_semantic_ai",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_schedule_returns",
            title="📅 Agenda e retornos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_intelligent_schedule",
                    title="📅 Agenda odontológica inteligente",
                    description=(
                        "Agendamento de consultas, procedimentos, "
                        "avaliações, retornos e encaixes."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_recall_reminders",
                    title="🔔 Retornos, confirmações e lembretes",
                    description=(
                        "Confirmações automáticas, lembretes, reagendamento "
                        "e acompanhamento de retornos pendentes."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "business_automation",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_treatment_planning",
            title="🦷 Planos de tratamento",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_treatment_plan",
                    title="🦷 Planejamento de tratamentos",
                    description=(
                        "Organização de etapas, procedimentos, prioridades, "
                        "prazos e acompanhamento do plano de tratamento."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "knowledge_graph_semantic_ai",
                        "enterprise_rag",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_clinical_evolution",
                    title="📈 Evolução e acompanhamento",
                    description=(
                        "Linha do tempo dos procedimentos realizados, "
                        "etapas concluídas e acompanhamento do paciente."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "tools_analytics",
                        "document_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_assisted_information",
                    title="🧠 Informação odontológica assistida",
                    description=(
                        "Consulta controlada a protocolos, documentos "
                        "internos e materiais de referência profissional."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "responsible_ai_ethics_risk",
                        "ai_certification_system_evidence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_images_documents",
            title="🩻 Imagens e documentos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_images_management",
                    title="🩻 Gestão de imagens odontológicas",
                    description=(
                        "Organização de fotografias, radiografias, "
                        "documentos visuais e histórico de imagens."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "document_ai",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_document_generation",
                    title="📄 Documentos e formulários",
                    description=(
                        "Geração assistida de formulários, termos, "
                        "declarações, orientações e documentos administrativos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_budgets_payments",
            title="💰 Orçamentos e pagamentos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_treatment_budgets",
                    title="💰 Orçamentos de tratamentos",
                    description=(
                        "Composição de procedimentos, valores, condições, "
                        "etapas e aprovação de orçamentos."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "erp_business_operations",
                        "business_automation",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_billing_payments",
                    title="💳 Cobranças e pagamentos",
                    description=(
                        "Cobranças, recebimentos, parcelamentos, "
                        "inadimplência e conciliação financeira."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "api_integrations_connectors",
                        "erp_business_operations",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_management_compliance",
            title="🏥 Gestão clínica e conformidade",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_material_inventory",
                    title="📦 Materiais e estoque odontológico",
                    description=(
                        "Controle de materiais, produtos, lotes, "
                        "validade, consumo e necessidade de reposição."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "supply_chain_procurement_logistics",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_quality_compliance",
                    title="✅ Qualidade, segurança e conformidade",
                    description=(
                        "Processos, evidências, checklists, documentos, "
                        "rastreabilidade e controles administrativos."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "technology_governance_policy_compliance",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_management_indicators",
                    title="📊 Indicadores de gestão odontológica",
                    description=(
                        "Agenda, faltas, ocupação, tratamentos, receita, "
                        "custos, retorno e desempenho operacional."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
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
    """Adiciona Odontologia ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "DENTISTRY_SOLUTION = PlatformSectorSolution(" in source:
        print("DENTISTRY_SOLUTION_ALREADY_PRESENT=OK")
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
        DENTISTRY_DEFINITION + registry_anchor,
        1,
    )

    old_registry_tail = """    SUPERMARKETS_WHOLESALE_SOLUTION,
    RETAIL_STORES_SOLUTION,
)"""

    new_registry_tail = """    SUPERMARKETS_WHOLESALE_SOLUTION,
    RETAIL_STORES_SOLUTION,
    DENTISTRY_SOLUTION,
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

    print("DENTISTRY_SECTOR_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes do registro."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_dentistry_solution_is_complete" in source:
        print("DENTISTRY_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    AGRIBUSINESS_SOLUTION,\n"

    import_replacement = "    AGRIBUSINESS_SOLUTION,\n    DENTISTRY_SOLUTION,\n"

    if import_anchor not in source:
        raise RuntimeError("Âncora de importação dos testes não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 5"

    new_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 6"

    if old_count not in source:
        raise RuntimeError("Contagem atual de cinco soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    expected_anchor = """        "retail_stores",
    }"""

    expected_replacement = """        "retail_stores",
        "dentistry",
    }"""

    if expected_anchor not in source:
        raise RuntimeError("Conjunto esperado das soluções não encontrado.")

    source = source.replace(
        expected_anchor,
        expected_replacement,
        1,
    )

    source += """


def test_dentistry_solution_is_complete():
    assert DENTISTRY_SOLUTION.solution_id == "dentistry"
    assert (
        DENTISTRY_SOLUTION.status
        is SectorSolutionStatus.PLANNED
    )
    assert (
        DENTISTRY_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(DENTISTRY_SOLUTION.areas) == 6
    assert (
        DENTISTRY_SOLUTION.capability_count
        == 15
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("DENTISTRY_SECTOR_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma a expansão de Odontologia."""

    from src.platform_sector_solutions import (
        DENTISTRY_SOLUTION,
        PLATFORM_SECTOR_SOLUTIONS,
        platform_sector_solution,
    )

    assert len(PLATFORM_SECTOR_SOLUTIONS) == 6

    assert platform_sector_solution("dentistry") is DENTISTRY_SOLUTION

    assert len(DENTISTRY_SOLUTION.areas) == 6

    assert DENTISTRY_SOLUTION.capability_count == 15

    total_areas = sum(len(solution.areas) for solution in PLATFORM_SECTOR_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_SECTOR_SOLUTIONS
    )

    assert total_areas == 39
    assert total_capabilities == 101

    print("SPECIALIZED_SECTOR_SOLUTIONS=6")
    print("TOTAL_SECTOR_AREAS=39")
    print("TOTAL_SECTOR_CAPABILITIES=101")
    print("DENTISTRY_SECTOR_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
