"""Adiciona Jurídico e Compliance ao registro empresarial."""

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
    / ("legal_compliance_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


LEGAL_COMPLIANCE_DEFINITION = """
LEGAL_COMPLIANCE_SOLUTION = PlatformBusinessSolution(
    solution_id="legal_compliance",
    icon="⚖️",
    title="Jurídico e Compliance",
    description=(
        "Solução empresarial para contratos, documentos jurídicos, "
        "requisitos regulatórios, controles, obrigações, privacidade, "
        "riscos, auditorias, investigações e governança."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="legal_contracts_documents",
            title="📄 Contratos e documentos jurídicos",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_contract_repository",
                    title="📚 Repositório e ciclo de vida de contratos",
                    description=(
                        "Organização de contratos, partes, responsáveis, "
                        "versões, anexos, vigências e situações."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "data_platform_governance",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_clause_risk_analysis",
                    title="🔎 Análise de cláusulas e riscos",
                    description=(
                        "Identificação assistida de cláusulas, obrigações, "
                        "restrições, divergências e riscos contratuais."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_document_generation_review",
                    title="✍️ Geração e revisão de documentos",
                    description=(
                        "Apoio controlado à elaboração, comparação, "
                        "revisão e aprovação de documentos jurídicos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "enterprise_rag",
                        "business_automation",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="legal_requirements_controls",
            title="📋 Requisitos, políticas e controles",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_regulatory_catalog",
                    title="📋 Catálogo de requisitos regulatórios",
                    description=(
                        "Organização de leis, normas, obrigações, temas, "
                        "responsáveis, prazos e aplicabilidade."
                    ),
                    technology_dependencies=(
                        "technology_governance_policy_compliance",
                        "knowledge_graph_semantic_ai",
                        "document_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_controls_evidence_mapping",
                    title="🧩 Mapeamento de controles e evidências",
                    description=(
                        "Relacionamento entre requisitos, riscos, controles, "
                        "processos, documentos e evidências."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "data_traceability_provenance",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_policy_management",
                    title="📑 Gestão de políticas corporativas",
                    description=(
                        "Criação, revisão, aprovação, publicação, aceite "
                        "e controle de versões de políticas."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="legal_cases_deadlines_workflows",
            title="🗂️ Casos, obrigações e workflows",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_case_management",
                    title="🗂️ Gestão de casos e demandas jurídicas",
                    description=(
                        "Cadastro de casos, assuntos, partes, responsáveis, "
                        "documentos, movimentações e situações."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "document_ai",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_deadline_obligation_management",
                    title="⏱️ Prazos e obrigações",
                    description=(
                        "Controle de vencimentos, compromissos, responsáveis, "
                        "alertas, prioridades e escalonamentos."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "business_automation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_approvals_human_review",
                    title="👤 Aprovações e revisão humana",
                    description=(
                        "Encaminhamento de documentos e decisões para "
                        "revisão, aprovação, correção ou rejeição."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "zero_trust_identity_access",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="legal_privacy_ethics_risk",
            title="🔐 Privacidade, ética e riscos",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_lgpd_requests",
                    title="🔐 Solicitações e direitos relacionados à LGPD",
                    description=(
                        "Gestão de solicitações, validações, responsáveis, "
                        "prazos, evidências e respostas relacionadas a dados."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "privacy_enhancing_technologies",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_third_party_due_diligence",
                    title="🔍 Due diligence de terceiros",
                    description=(
                        "Avaliação de fornecedores, parceiros, documentos, "
                        "riscos, restrições e evidências."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "enterprise_decision_intelligence",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_ethics_conflicts_reports",
                    title="⚖️ Ética, conflitos e relatos",
                    description=(
                        "Registro e tratamento controlado de conflitos, "
                        "relatos, manifestações e medidas adotadas."
                    ),
                    technology_dependencies=(
                        "responsible_ai_ethics_risk",
                        "zero_trust_identity_access",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="legal_audit_monitoring_investigations",
            title="🛡️ Monitoramento, auditoria e investigações",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_compliance_monitoring",
                    title="🛡️ Monitoramento de conformidade",
                    description=(
                        "Acompanhamento de eventos, desvios, controles, "
                        "obrigações, riscos e situações relevantes."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_audit_evidence",
                    title="🧾 Auditoria e evidências",
                    description=(
                        "Registro de acessos, alterações, decisões, "
                        "documentos, responsáveis e evidências."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "document_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_investigation_support",
                    title="🔎 Apoio a investigações internas",
                    description=(
                        "Organização de fatos, documentos, eventos, "
                        "relações, evidências e linhas de análise."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "zero_trust_identity_access",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="legal_analytics_governance",
            title="📊 Analytics e governança jurídica",
            capabilities=(
                BusinessCapability(
                    capability_id="legal_compliance_dashboards",
                    title="📊 Indicadores jurídicos e de compliance",
                    description=(
                        "Acompanhamento de contratos, casos, prazos, "
                        "riscos, auditorias, controles e obrigações."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_risk_obligation_forecasting",
                    title="📈 Previsão de riscos e obrigações",
                    description=(
                        "Projeções de demandas, vencimentos, exposições, "
                        "recursos necessários e cenários."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "simulation_optimization_operations_research",
                    ),
                ),
                BusinessCapability(
                    capability_id="legal_governance_reporting",
                    title="📑 Relatórios e prestação de contas",
                    description=(
                        "Consolidação de informações, decisões, riscos, "
                        "controles e evidências para a governança."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "technology_governance_policy_compliance",
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
    """Adiciona Jurídico e Compliance ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "LEGAL_COMPLIANCE_SOLUTION = PlatformBusinessSolution(" in source:
        print("LEGAL_COMPLIANCE_ALREADY_PRESENT=OK")
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
        LEGAL_COMPLIANCE_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
)"""

    new_registry = """    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
    LEGAL_COMPLIANCE_SOLUTION,
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

    print("LEGAL_COMPLIANCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_legal_compliance_solution_is_complete" in source:
        print("LEGAL_COMPLIANCE_TESTS_ALREADY_PRESENT=OK")
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

    if "LEGAL_COMPLIANCE_SOLUTION" not in import_block:
        source = (
            source[:import_end]
            + "    LEGAL_COMPLIANCE_SOLUTION,\n"
            + source[import_end:]
        )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 6"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 7"

    if old_count not in source:
        raise RuntimeError("Contagem atual de seis soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_legal_compliance_solution_is_complete():
    assert (
        LEGAL_COMPLIANCE_SOLUTION.solution_id
        == "legal_compliance"
    )
    assert (
        LEGAL_COMPLIANCE_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        LEGAL_COMPLIANCE_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        LEGAL_COMPLIANCE_SOLUTION.areas
    ) == 6
    assert (
        LEGAL_COMPLIANCE_SOLUTION.capability_count
        == 18
    )


def test_legal_compliance_solution_lookup():
    assert (
        platform_business_solution(
            "legal_compliance"
        )
        is LEGAL_COMPLIANCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("LEGAL_COMPLIANCE_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        LEGAL_COMPLIANCE_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 7

    assert platform_business_solution("legal_compliance") is LEGAL_COMPLIANCE_SOLUTION

    assert len(LEGAL_COMPLIANCE_SOLUTION.areas) == 6

    assert LEGAL_COMPLIANCE_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 42
    assert total_capabilities == 125

    print("SPECIALIZED_BUSINESS_SOLUTIONS=7")
    print("TOTAL_BUSINESS_AREAS=42")
    print("TOTAL_BUSINESS_CAPABILITIES=125")
    print("LEGAL_COMPLIANCE_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
