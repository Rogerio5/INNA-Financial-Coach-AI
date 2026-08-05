"""Adiciona Privacidade, Proteção de Dados e LGPD ao registro tecnológico."""

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
        "privacy_data_protection_lgpd_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


PRIVACY_DATA_PROTECTION_LGPD_DEFINITION = """
_PRIVACY_DATA_PROTECTION_LGPD_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "privacy_data_protection_lgpd"
    ]
)


PRIVACY_DATA_PROTECTION_LGPD_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="privacy_data_protection_lgpd",
        icon="🔐",
        title="Privacidade, Proteção de Dados e LGPD",
        description=(
            "Arquitetura tecnológica para inventário, classificação, "
            "bases legais, direitos dos titulares, privacidade desde "
            "a concepção, minimização, retenção, proteção de dados "
            "sensíveis, compartilhamento, riscos, incidentes, "
            "auditoria e conformidade com a LGPD."
        ),
        status=(
            _PRIVACY_DATA_PROTECTION_LGPD_MODULE.status
        ),
        integration_type=(
            _PRIVACY_DATA_PROTECTION_LGPD_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="privacy_governance_inventory",
                title="🗂️ Governança e inventário de dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_data_inventory",
                        title="🗂️ Inventário de dados pessoais",
                        description=(
                            "Mapeamento de dados pessoais, fontes, sistemas, "
                            "finalidades, responsáveis, destinatários "
                            "e locais de armazenamento."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "legal_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_data_classification",
                        title="🏷️ Classificação de dados pessoais",
                        description=(
                            "Classificação de dados pessoais, sensíveis, "
                            "identificadores, documentos e informações "
                            "com diferentes níveis de proteção."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "document_ai",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_legal_basis_purpose",
                        title="⚖️ Bases legais e finalidades",
                        description=(
                            "Registro das bases legais, finalidades, "
                            "necessidade, responsáveis e condições "
                            "do tratamento de dados."
                        ),
                        technology_dependencies=(
                            "legal_compliance",
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_data_subject_rights",
                title="👤 Direitos dos titulares",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_subject_access_portability",
                        title="📄 Acesso e portabilidade",
                        description=(
                            "Localização, consolidação e entrega controlada "
                            "dos dados relacionados ao titular."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "data_platform_governance",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_correction_deletion",
                        title="✏️ Correção, anonimização e eliminação",
                        description=(
                            "Execução controlada de correções, bloqueios, "
                            "anonimizações ou eliminações autorizadas."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "privacy_enhancing_technologies",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_subject_request_workflows",
                        title="🧩 Workflows de solicitações",
                        description=(
                            "Recebimento, validação de identidade, análise, "
                            "aprovação, resposta e auditoria das solicitações."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_by_design_minimization",
                title="🛡️ Privacy by Design e minimização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_data_minimization",
                        title="📉 Minimização de dados",
                        description=(
                            "Redução da coleta, armazenamento, exposição "
                            "e utilização ao mínimo necessário."
                        ),
                        technology_dependencies=(
                            "privacy_enhancing_technologies",
                            "technology_governance_policy_compliance",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_purpose_limitation",
                        title="🎯 Limitação de finalidade",
                        description=(
                            "Verificação de que os dados são usados apenas "
                            "para finalidades autorizadas e documentadas."
                        ),
                        technology_dependencies=(
                            "legal_compliance",
                            "data_traceability_provenance",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_retention_disposal",
                        title="🗃️ Retenção e descarte seguro",
                        description=(
                            "Aplicação de prazos de retenção, arquivamento, "
                            "bloqueio e descarte seguro dos dados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "business_automation",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_sensitive_data_protection",
                title="🔒 Proteção de dados sensíveis",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_sensitive_data_discovery",
                        title="🔎 Descoberta de dados sensíveis",
                        description=(
                            "Identificação de informações pessoais ou "
                            "confidenciais em bancos, documentos, eventos "
                            "e bases de conhecimento."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "enterprise_rag",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_masking_pseudonymization",
                        title="🕶️ Mascaramento e pseudonimização",
                        description=(
                            "Substituição ou ocultação de identificadores "
                            "para reduzir exposição e possibilidade "
                            "de associação direta."
                        ),
                        technology_dependencies=(
                            "privacy_enhancing_technologies",
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_encryption_key_protection",
                        title="🔑 Criptografia e proteção de chaves",
                        description=(
                            "Proteção de dados em trânsito e armazenamento, "
                            "com gestão controlada de chaves e segredos."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_access_sharing_transfers",
                title="🔐 Acesso, compartilhamento e transferências",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_access_controls",
                        title="🪪 Controle de acesso aos dados",
                        description=(
                            "Aplicação de papéis, permissões, escopos, "
                            "segregação e acesso conforme necessidade."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "data_platform_governance",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_data_sharing_controls",
                        title="🤝 Compartilhamento controlado",
                        description=(
                            "Registro e controle de dados compartilhados, "
                            "destinatários, contratos, finalidades "
                            "e condições de utilização."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "legal_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_cross_border_transfers",
                        title="🌐 Transferências internacionais",
                        description=(
                            "Avaliação e registro de transferências entre "
                            "regiões, provedores ou países, conforme regras "
                            "e garantias aplicáveis."
                        ),
                        technology_dependencies=(
                            "legal_compliance",
                            "cloud_devops_finops",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_risk_incident_response",
                title="🚨 Riscos e incidentes de privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_impact_assessment",
                        title="📋 Avaliação de impacto à privacidade",
                        description=(
                            "Identificação de tratamentos, riscos, impactos, "
                            "controles, responsáveis e medidas de redução."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "legal_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_violation_detection",
                        title="🚨 Detecção de violações e exposição",
                        description=(
                            "Monitoramento de acessos, exportações, "
                            "vazamentos, usos inadequados e operações "
                            "fora das políticas."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "real_time_event_intelligence",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_incident_response",
                        title="🧯 Resposta a incidentes de dados",
                        description=(
                            "Contenção, investigação, avaliação de impacto, "
                            "recuperação, registro e comunicação autorizada."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cybersecurity_fraud_prevention",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="privacy_audit_metrics_lifecycle",
                title="📊 Auditoria e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="privacy_audit_evidence",
                        title="🧾 Evidências e trilha de auditoria",
                        description=(
                            "Registro de acessos, consentimentos, alterações, "
                            "solicitações, compartilhamentos e decisões."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "legal_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_metrics_reporting",
                        title="📊 Métricas e relatórios de privacidade",
                        description=(
                            "Acompanhamento de solicitações, incidentes, "
                            "prazos, riscos, acessos e eficácia dos controles."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "ai_operations",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="privacy_continuous_improvement",
                        title="📈 Melhoria contínua e conscientização",
                        description=(
                            "Evolução de políticas, processos, controles, "
                            "treinamentos e práticas de proteção de dados."
                        ),
                        technology_dependencies=(
                            "quality_process_management",
                            "technology_governance_policy_compliance",
                            "responsible_ai_ethics_risk",
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

    module_id = "privacy_data_protection_lgpd"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        14: (98, 294),
        15: (105, 315),
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

    print("PRIVACY_DATA_PROTECTION_LGPD_PREREQUISITES=OK")


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
    """Adiciona a solução ao registro tecnológico."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "PRIVACY_DATA_PROTECTION_LGPD_SOLUTION =" in source:
        print("PRIVACY_DATA_PROTECTION_LGPD_ALREADY_PRESENT=OK")
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
        PRIVACY_DATA_PROTECTION_LGPD_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    REAL_TIME_EVENT_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    PRIVACY_DATA_PROTECTION_LGPD_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("PRIVACY_DATA_PROTECTION_LGPD_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_privacy_data_protection_lgpd_is_complete" in source:
        print("PRIVACY_DATA_PROTECTION_LGPD_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "PRIVACY_DATA_PROTECTION_LGPD_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 14
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 15
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quatorze soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_privacy_data_protection_lgpd_is_complete():
    assert (
        PRIVACY_DATA_PROTECTION_LGPD_SOLUTION.solution_id
        == "privacy_data_protection_lgpd"
    )

    assert len(
        PRIVACY_DATA_PROTECTION_LGPD_SOLUTION.areas
    ) == 7

    assert (
        PRIVACY_DATA_PROTECTION_LGPD_SOLUTION.capability_count
        == 21
    )


def test_privacy_data_protection_lgpd_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "privacy_data_protection_lgpd"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        PRIVACY_DATA_PROTECTION_LGPD_SOLUTION.status
        is module.status
    )

    assert (
        PRIVACY_DATA_PROTECTION_LGPD_SOLUTION.integration_type
        == module.integration_type
    )


def test_privacy_data_protection_lgpd_lookup():
    assert (
        platform_technology_solution(
            "privacy_data_protection_lgpd"
        )
        is PRIVACY_DATA_PROTECTION_LGPD_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("PRIVACY_DATA_PROTECTION_LGPD_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    privacy_solution = getattr(
        module,
        "PRIVACY_DATA_PROTECTION_LGPD_SOLUTION",
    )

    assert len(solutions) == 15
    assert len(privacy_solution.areas) == 7
    assert privacy_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 105
    assert total_capabilities == 315

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=15")
    print("TOTAL_TECHNOLOGY_AREAS=105")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=315")
    print("PRIVACY_DATA_PROTECTION_LGPD_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
