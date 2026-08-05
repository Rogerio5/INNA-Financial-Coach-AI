"""Adiciona Segurança Operacional e Resiliência."""

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
        "operational_security_resilience_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


OPERATIONAL_SECURITY_RESILIENCE_DEFINITION = """
_OPERATIONAL_SECURITY_RESILIENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "operational_security_resilience"
    ]
)


OPERATIONAL_SECURITY_RESILIENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="operational_security_resilience",
        icon="🛡️",
        title="Segurança Operacional e Resiliência",
        description=(
            "Arquitetura tecnológica para identificação de serviços "
            "e ativos críticos, dependências, riscos operacionais, "
            "telemetria, detecção de ameaças, controle de acesso, "
            "configurações seguras, gestão de mudanças, resposta "
            "a incidentes, continuidade, recuperação, terceiros, "
            "infraestrutura conectada, governança, métricas, "
            "auditoria e observabilidade."
        ),
        status=(
            _OPERATIONAL_SECURITY_RESILIENCE_MODULE.status
        ),
        integration_type=(
            _OPERATIONAL_SECURITY_RESILIENCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "operational_security_assets_criticality"
                ),
                title="🗂️ Serviços, ativos e criticidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_critical_service_inventory"
                        ),
                        title="📋 Inventário de serviços críticos",
                        description=(
                            "Cadastro de serviços, sistemas, aplicações, "
                            "infraestruturas, equipamentos, responsáveis, "
                            "localização e requisitos operacionais."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "asset_management_smart_maintenance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_dependency_mapping"
                        ),
                        title="🔗 Dependências operacionais",
                        description=(
                            "Mapeamento de dependências entre serviços, "
                            "dados, aplicações, redes, fornecedores, "
                            "ativos físicos e equipes responsáveis."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "networks_telecommunications_connectivity",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_criticality_impact_analysis"
                        ),
                        title="⚠️ Criticidade e análise de impacto",
                        description=(
                            "Classificação conforme segurança, usuários, "
                            "dados, disponibilidade, custos, ambiente, "
                            "obrigações e consequências de interrupção."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "simulation_optimization_operations_research",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_security_monitoring_detection"
                ),
                title="📡 Monitoramento e detecção",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_security_telemetry_ingestion"
                        ),
                        title="📨 Telemetria de segurança operacional",
                        description=(
                            "Ingestão de logs, métricas, traces, eventos, "
                            "alarmes, estados, acessos, configurações "
                            "e dados provenientes da infraestrutura."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "ai_operations",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_anomaly_threat_detection"
                        ),
                        title="🚨 Anomalias e ameaças operacionais",
                        description=(
                            "Identificação de comportamentos incomuns, "
                            "degradações, acessos suspeitos, alterações "
                            "indevidas e possíveis sinais de comprometimento."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_alert_event_correlation"
                        ),
                        title="🧩 Correlação de alertas e eventos",
                        description=(
                            "Correlação de eventos provenientes de redes, "
                            "aplicações, identidades, dispositivos, cloud "
                            "e ativos para reduzir alertas isolados."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_access_configuration_change"
                ),
                title="🔐 Acesso, configuração e mudanças",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_privileged_access_control"
                        ),
                        title="🔑 Acesso privilegiado operacional",
                        description=(
                            "Controle de operadores, administradores, "
                            "contas técnicas, privilégios, sessões, "
                            "aprovações e atividades administrativas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "digital_identity_verifiable_credentials",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_secure_configuration_baselines"
                        ),
                        title="⚙️ Configurações seguras e baselines",
                        description=(
                            "Definição e verificação de configurações "
                            "aprovadas, versões, parâmetros, permissões, "
                            "serviços ativos e desvios de segurança."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "software_supply_chain_security",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_change_risk_control"
                        ),
                        title="🔄 Controle de mudanças operacionais",
                        description=(
                            "Avaliação, aprovação, teste, implantação gradual, "
                            "monitoramento e rollback de mudanças que possam "
                            "afetar serviços críticos."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_software_engineering",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_incident_response_coordination"
                ),
                title="🚨 Resposta e coordenação de incidentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_incident_response_workflows"
                        ),
                        title="⚡ Workflows de resposta a incidentes",
                        description=(
                            "Classificação, priorização, atribuição, "
                            "contenção, investigação, recuperação, "
                            "comunicação e encerramento de incidentes."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_forensics_evidence_preservation"
                        ),
                        title="🔎 Evidências e investigação",
                        description=(
                            "Preservação de logs, eventos, configurações, "
                            "artefatos, acessos, alterações e demais "
                            "evidências necessárias à investigação."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "cryptography_confidential_computing",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_crisis_communication_coordination"
                        ),
                        title="📣 Comunicação e coordenação de crise",
                        description=(
                            "Coordenação de equipes, responsáveis, "
                            "fornecedores, usuários e lideranças com "
                            "mensagens, atualizações e decisões rastreáveis."
                        ),
                        technology_dependencies=(
                            "ai_collaboration_meetings_productivity",
                            "emergency_disaster_management",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_continuity_recovery_resilience"
                ),
                title="♻️ Continuidade, recuperação e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_redundancy_failover"
                        ),
                        title="🔁 Redundância e failover",
                        description=(
                            "Planejamento e validação de redundância, "
                            "replicação, rotas alternativas, substituição "
                            "de recursos e continuidade dos serviços."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "networks_telecommunications_connectivity",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_backup_restore_recovery"
                        ),
                        title="💾 Backup, restauração e recuperação",
                        description=(
                            "Gestão de cópias, retenção, proteção, testes "
                            "de restauração, recuperação de dados "
                            "e reconstrução dos ambientes."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "cryptography_confidential_computing",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_continuity_exercises"
                        ),
                        title="🧪 Exercícios e testes de continuidade",
                        description=(
                            "Simulação controlada de indisponibilidades, "
                            "falhas, perda de recursos, recuperação, "
                            "comunicação e operação degradada."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "software_testing_quality_reliability",
                            "emergency_disaster_management",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_third_party_ot_infrastructure"
                ),
                title="🏭 Terceiros e infraestrutura conectada",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_third_party_dependency_resilience"
                        ),
                        title="🤝 Resiliência de terceiros",
                        description=(
                            "Avaliação de fornecedores, serviços externos, "
                            "contratos, dependências, continuidade, "
                            "acessos e capacidade de recuperação."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "software_supply_chain_security",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_ot_iot_security"
                        ),
                        title="🏭 Segurança de OT e IoT",
                        description=(
                            "Proteção de sensores, dispositivos, gateways, "
                            "sistemas de controle, comandos, redes "
                            "e integrações da infraestrutura conectada."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "zero_trust_identity_access",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_physical_asset_emergency_integration"
                        ),
                        title="🚧 Ativos físicos e emergências",
                        description=(
                            "Integração de segurança tecnológica com "
                            "ativos físicos, instalações, equipes de campo, "
                            "manutenção e planos de emergência."
                        ),
                        technology_dependencies=(
                            "asset_management_smart_maintenance",
                            "emergency_disaster_management",
                            "gis_location_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "operational_governance_metrics_observability"
                ),
                title="📊 Governança, métricas e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operational_security_policy_compliance"
                        ),
                        title="⚖️ Políticas e conformidade operacional",
                        description=(
                            "Verificação de políticas, controles, requisitos, "
                            "exceções, responsabilidades, testes, evidências "
                            "e planos de correção."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_resilience_metrics_slo"
                        ),
                        title="📈 Métricas de resiliência e SLOs",
                        description=(
                            "Acompanhamento de disponibilidade, tempo "
                            "de detecção, resposta, recuperação, falhas, "
                            "impactos e cumprimento dos objetivos."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "ai_operations",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operational_security_audit_observability"
                        ),
                        title="🧾 Auditoria e observabilidade operacional",
                        description=(
                            "Registro de eventos, acessos, mudanças, "
                            "incidentes, decisões, recuperações, testes, "
                            "custos, versões e evidências."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_operations",
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

    module_id = "operational_security_resilience"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        50: (350, 1050),
        51: (357, 1071),
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

    print("OPERATIONAL_SECURITY_RESILIENCE_PREREQUISITES=OK")


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
    """Adiciona Segurança Operacional e Resiliência."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "OPERATIONAL_SECURITY_RESILIENCE_SOLUTION =" in source:
        print("OPERATIONAL_SECURITY_RESILIENCE_ALREADY_PRESENT=OK")
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
        OPERATIONAL_SECURITY_RESILIENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    OPERATIONAL_SECURITY_RESILIENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("OPERATIONAL_SECURITY_RESILIENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona ou completa os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

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

    solution_name = "OPERATIONAL_SECURITY_RESILIENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 50
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 51
"""

    if old_count in source:
        source = source.replace(
            old_count,
            new_count,
            1,
        )
    elif new_count not in source:
        raise RuntimeError(
            "Contagem esperada das soluções tecnológicas não encontrada."
        )

    test_name = "def test_operational_security_resilience_is_complete"

    if test_name not in source:
        source += """


def test_operational_security_resilience_is_complete():
    assert (
        OPERATIONAL_SECURITY_RESILIENCE_SOLUTION.solution_id
        == "operational_security_resilience"
    )

    assert len(
        OPERATIONAL_SECURITY_RESILIENCE_SOLUTION.areas
    ) == 7

    assert (
        OPERATIONAL_SECURITY_RESILIENCE_SOLUTION
        .capability_count
        == 21
    )


def test_operational_security_resilience_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "operational_security_resilience"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        OPERATIONAL_SECURITY_RESILIENCE_SOLUTION.status
        is module.status
    )

    assert (
        OPERATIONAL_SECURITY_RESILIENCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_operational_security_resilience_lookup():
    assert (
        platform_technology_solution(
            "operational_security_resilience"
        )
        is OPERATIONAL_SECURITY_RESILIENCE_SOLUTION
    )
"""

        print("OPERATIONAL_SECURITY_RESILIENCE_TESTS_CREATED=OK")
    else:
        print("OPERATIONAL_SECURITY_RESILIENCE_TESTS_ALREADY_PRESENT=OK")

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    operational_solution = module.OPERATIONAL_SECURITY_RESILIENCE_SOLUTION

    assert len(solutions) == 51
    assert len(operational_solution.areas) == 7

    assert operational_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 357
    assert total_capabilities == 1071

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=51")
    print("TOTAL_TECHNOLOGY_AREAS=357")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1071")
    print("OPERATIONAL_SECURITY_RESILIENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
