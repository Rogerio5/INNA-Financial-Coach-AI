"""Adiciona Governança, Políticas e Conformidade Tecnológica."""

from __future__ import annotations

import importlib
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_technology_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_technology_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / (
        "technology_governance_policy_compliance_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_DEFINITION = """
_TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "technology_governance_policy_compliance"
    ]
)


TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id=(
            "technology_governance_policy_compliance"
        ),
        icon="⚖️",
        title=(
            "Governança, Políticas e Conformidade Tecnológica"
        ),
        description=(
            "Arquitetura tecnológica para modelos de governança, "
            "portfólio e arquitetura corporativa, políticas, "
            "controles, exceções, requisitos regulatórios, riscos, "
            "segurança, privacidade, terceiros, IA, dados, cloud, "
            "mudanças, continuidade, auditoria, evidências, "
            "automação, métricas e observabilidade."
        ),
        status=(
            _TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_MODULE
            .status
        ),
        integration_type=(
            _TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "technology_governance_operating_model"
                ),
                title="🏛️ Modelo de governança e arquitetura",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_governance_roles_committees"
                        ),
                        title="👥 Papéis, fóruns e responsabilidades",
                        description=(
                            "Definição de papéis, comitês, autoridades, "
                            "responsáveis, escalonamentos, segregação "
                            "de funções e prestação de contas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "enterprise_decision_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_portfolio_service_catalog"
                        ),
                        title="📚 Portfólio e catálogo tecnológico",
                        description=(
                            "Organização de produtos, plataformas, serviços, "
                            "sistemas, capacidades, responsáveis, custos, "
                            "criticidade e estágio do ciclo de vida."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_architecture_decision_records"
                        ),
                        title="🏗️ Decisões e padrões de arquitetura",
                        description=(
                            "Registro de decisões, alternativas, critérios, "
                            "dependências, impactos, padrões aprovados "
                            "e justificativas arquiteturais."
                        ),
                        technology_dependencies=(
                            "ai_software_engineering",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_policy_control_management"
                ),
                title="📜 Políticas, padrões e controles",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_policy_lifecycle_management"
                        ),
                        title="📄 Ciclo de vida das políticas",
                        description=(
                            "Criação, revisão, aprovação, publicação, "
                            "comunicação, versionamento, vigência "
                            "e retirada de políticas tecnológicas."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "enterprise_rag",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_control_library_mapping"
                        ),
                        title="🧩 Biblioteca e mapeamento de controles",
                        description=(
                            "Organização de controles, objetivos, riscos, "
                            "responsáveis, sistemas aplicáveis, evidências "
                            "e relações com políticas e requisitos."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_exception_waiver_management"
                        ),
                        title="⚠️ Exceções e dispensas controladas",
                        description=(
                            "Registro, avaliação, aprovação, prazo, "
                            "compensações, responsáveis e acompanhamento "
                            "de exceções às políticas tecnológicas."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "enterprise_decision_intelligence",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_compliance_evidence_assurance"
                ),
                title="🧾 Conformidade, evidências e auditoria",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_obligation_requirement_mapping"
                        ),
                        title="⚖️ Requisitos e obrigações aplicáveis",
                        description=(
                            "Mapeamento de requisitos legais, regulatórios, "
                            "contratuais, normativos e internos aos sistemas, "
                            "processos, dados e controles relacionados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "document_ai",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_compliance_evidence_collection"
                        ),
                        title="📥 Coleta de evidências de conformidade",
                        description=(
                            "Coleta automatizada ou assistida de logs, "
                            "configurações, aprovações, relatórios, testes, "
                            "documentos e registros operacionais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "business_automation",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_audit_readiness_assurance"
                        ),
                        title="🔎 Preparação e suporte à auditoria",
                        description=(
                            "Consolidação de escopo, controles, amostras, "
                            "evidências, responsáveis, deficiências, "
                            "planos de ação e histórico das verificações."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "document_ai",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_risk_security_privacy_governance"
                ),
                title="🛡️ Riscos, segurança e privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_risk_register_assessment"
                        ),
                        title="⚠️ Registro e avaliação de riscos",
                        description=(
                            "Identificação, análise, classificação, "
                            "tratamento, aceitação e monitoramento de riscos "
                            "tecnológicos e suas dependências."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_security_privacy_alignment"
                        ),
                        title="🔐 Alinhamento de segurança e privacidade",
                        description=(
                            "Relacionamento entre controles tecnológicos, "
                            "proteção de dados, identidade, criptografia, "
                            "segurança de aplicações e riscos cibernéticos."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_third_party_risk_governance"
                        ),
                        title="🤝 Riscos tecnológicos de terceiros",
                        description=(
                            "Avaliação de fornecedores, serviços, contratos, "
                            "dependências, acessos, subcontratações, "
                            "continuidade e evidências de terceiros."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "api_integrations_connectors",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_ai_data_cloud_governance"
                ),
                title="🤖 Governança de IA, dados e cloud",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_ai_model_agent_governance"
                        ),
                        title="🤖 Governança de modelos e agentes",
                        description=(
                            "Controle de modelos, agentes, ferramentas, "
                            "dados, avaliações, riscos, aprovações, "
                            "limites operacionais e responsabilidades."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "ai_model_agent_security",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_data_governance_alignment"
                        ),
                        title="🗃️ Governança tecnológica dos dados",
                        description=(
                            "Alinhamento entre classificação, qualidade, "
                            "linhagem, retenção, acesso, compartilhamento "
                            "e uso dos dados pelas soluções tecnológicas."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_cloud_finops_governance"
                        ),
                        title="☁️ Governança cloud e FinOps",
                        description=(
                            "Políticas para contas, recursos, regiões, "
                            "identidades, custos, capacidade, segurança, "
                            "configurações e ciclo de vida em cloud."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "zero_trust_identity_access",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_change_resilience_operations"
                ),
                title="🔄 Mudanças, resiliência e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_change_release_governance"
                        ),
                        title="🚀 Governança de mudanças e releases",
                        description=(
                            "Critérios de avaliação, aprovação, testes, "
                            "implantação gradual, comunicação, rollback "
                            "e evidências das mudanças tecnológicas."
                        ),
                        technology_dependencies=(
                            "ai_software_engineering",
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_resilience_continuity_governance"
                        ),
                        title="♻️ Resiliência e continuidade tecnológica",
                        description=(
                            "Definição de requisitos, estratégias, testes, "
                            "recuperação, redundância, operação degradada "
                            "e continuidade dos serviços críticos."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_incident_problem_governance"
                        ),
                        title="🚨 Incidentes e problemas",
                        description=(
                            "Governança de detecção, classificação, "
                            "escalonamento, resposta, comunicação, "
                            "causa raiz e acompanhamento das correções."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "technology_governance_automation_metrics"
                ),
                title="📊 Automação, métricas e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "technology_policy_as_code_automation"
                        ),
                        title="⚙️ Políticas como código",
                        description=(
                            "Tradução controlada de regras e controles "
                            "em verificações automatizadas, bloqueios, "
                            "alertas e critérios de implantação."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "ai_software_engineering",
                            "software_supply_chain_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_governance_metrics_reporting"
                        ),
                        title="📈 Métricas e relatórios de governança",
                        description=(
                            "Acompanhamento de riscos, controles, exceções, "
                            "auditorias, custos, qualidade, incidentes, "
                            "mudanças e níveis de conformidade."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_platform_governance",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "technology_governance_observability_provenance"
                        ),
                        title="🧾 Observabilidade e proveniência",
                        description=(
                            "Registro de políticas, versões, decisões, "
                            "aprovações, controles, evidências, acessos, "
                            "custos, alterações e resultados."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
        ),
    )
)


"""


def validate_prerequisites() -> None:
    """Valida o registro atual e o módulo principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )
    from src.platform_technology_solutions import (
        PLATFORM_TECHNOLOGY_SOLUTIONS,
    )

    module_id = "technology_governance_policy_compliance"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        47: (329, 987),
        48: (336, 1008),
    }

    if current_count not in expected_totals:
        raise RuntimeError(f"Quantidade tecnológica inesperada: {current_count}")

    total_areas = sum(len(solution.areas) for solution in PLATFORM_TECHNOLOGY_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    )

    expected_areas, expected_capabilities = expected_totals[current_count]

    if total_areas != expected_areas:
        raise RuntimeError(f"Total atual de áreas inesperado: {total_areas}")

    if total_capabilities != expected_capabilities:
        raise RuntimeError(
            f"Total atual de capacidades inesperado: {total_capabilities}"
        )

    print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria backup antes das alterações."""

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
    """Adiciona Governança, Políticas e Conformidade."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION =" in source:
        print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_TECHNOLOGY_SOLUTIONS: tuple[
    PlatformTechnologySolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro tecnológico não encontrada.")

    source = source.replace(
        registry_anchor,
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    DIGITAL_IDENTITY_VERIFIABLE_CREDENTIALS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_technology_governance_policy_compliance_is_complete"

    if test_name in source:
        print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_technology_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Importação tecnológica não encontrada.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final da importação tecnológica não encontrado.")

    import_block = source[import_start:import_end]

    solution_name = "TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 47
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 48
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quarenta e sete soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_technology_governance_policy_compliance_is_complete():
    assert (
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION.solution_id
        == "technology_governance_policy_compliance"
    )

    assert len(
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION.areas
    ) == 7

    assert (
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION
        .capability_count
        == 21
    )


def test_technology_governance_policy_compliance_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "technology_governance_policy_compliance"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION.status
        is module.status
    )

    assert (
        TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_technology_governance_policy_compliance_lookup():
    assert (
        platform_technology_solution(
            "technology_governance_policy_compliance"
        )
        is TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    governance_solution = module.TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION

    assert len(solutions) == 48
    assert len(governance_solution.areas) == 7

    assert governance_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 336
    assert total_capabilities == 1008

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=48")
    print("TOTAL_TECHNOLOGY_AREAS=336")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1008")
    print("TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
