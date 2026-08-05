"""Adiciona Rastreabilidade e Proveniência de Dados."""

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
        "data_traceability_provenance_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


DATA_TRACEABILITY_PROVENANCE_DEFINITION = """
_DATA_TRACEABILITY_PROVENANCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "data_traceability_provenance"
    ]
)


DATA_TRACEABILITY_PROVENANCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="data_traceability_provenance",
        icon="🧬",
        title="Rastreabilidade e Proveniência de Dados",
        description=(
            "Arquitetura tecnológica para identificação de fontes, "
            "linhagem, origem, transformações, versões, decisões, "
            "modelos, agentes, evidências, integridade, cadeia "
            "de custódia, acessos, compartilhamentos, qualidade, "
            "incidentes, retenção, conformidade, auditoria "
            "e observabilidade do ciclo de vida dos dados."
        ),
        status=(
            _DATA_TRACEABILITY_PROVENANCE_MODULE.status
        ),
        integration_type=(
            _DATA_TRACEABILITY_PROVENANCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="data_source_identity_lineage",
                title="🗂️ Fontes, identidade e linhagem",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_source_registry_identity"
                        ),
                        title="🏷️ Registro e identidade das fontes",
                        description=(
                            "Cadastro de sistemas, bancos, arquivos, "
                            "APIs, documentos, sensores, responsáveis, "
                            "localização e contexto de cada fonte."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "api_integrations_connectors",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_lineage_relationship_mapping"
                        ),
                        title="🔗 Mapeamento de linhagem",
                        description=(
                            "Representação das relações entre fontes, "
                            "tabelas, campos, arquivos, aplicações, "
                            "processos, relatórios e produtos de dados."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_provenance_metadata_capture"
                        ),
                        title="📋 Metadados de proveniência",
                        description=(
                            "Captura de origem, responsável, horário, "
                            "sistema, processo, versão, finalidade "
                            "e contexto associado aos dados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "real_time_event_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "data_ingestion_transformation_versioning"
                ),
                title="🔄 Ingestão, transformação e versionamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_ingestion_origin_tracking"
                        ),
                        title="📥 Rastreamento da ingestão",
                        description=(
                            "Registro de origem, horário, lote, evento, "
                            "conector, parâmetros, resultados, falhas "
                            "e responsáveis pela entrada dos dados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "real_time_event_intelligence",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_transformation_lineage"
                        ),
                        title="⚙️ Linhagem das transformações",
                        description=(
                            "Registro das regras, consultas, funções, "
                            "modelos, filtros, agregações e processos "
                            "aplicados aos dados durante sua evolução."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "ai_software_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_version_snapshot_management"
                        ),
                        title="📦 Versões e snapshots dos dados",
                        description=(
                            "Controle de versões, estados, snapshots, "
                            "alterações, restauração e comparação "
                            "entre diferentes momentos dos conjuntos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "data_platform_governance",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "data_decision_model_agent_traceability"
                ),
                title="🤖 Decisões, modelos e agentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_decision_input_output_trace"
                        ),
                        title="🧭 Entradas e saídas de decisões",
                        description=(
                            "Registro dos dados, regras, contexto, "
                            "alternativas, resultados, responsáveis "
                            "e justificativas associados às decisões."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_model_training_inference_lineage"
                        ),
                        title="🧠 Linhagem de modelos de IA",
                        description=(
                            "Rastreamento de datasets, características, "
                            "versões, parâmetros, avaliações, modelos "
                            "e resultados utilizados nas inferências."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "ai_bias_quality_monitoring",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_agent_tool_execution_trace"
                        ),
                        title="🛠️ Execuções de agentes e ferramentas",
                        description=(
                            "Registro de contexto, modelo, prompt, "
                            "ferramentas, chamadas, respostas, aprovações, "
                            "erros e resultados dos fluxos agênticos."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "ai_model_agent_security",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "data_evidence_integrity_chain_custody"
                ),
                title="🔐 Integridade e cadeia de custódia",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_evidence_integrity_hashing"
                        ),
                        title="🔏 Integridade e verificação de evidências",
                        description=(
                            "Utilização de hashes, assinaturas, versões "
                            "e verificações para detectar alterações "
                            "não autorizadas em dados e evidências."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "software_testing_quality_reliability",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_chain_of_custody",
                        title="⛓️ Cadeia de custódia dos dados",
                        description=(
                            "Registro de posse, transferência, acesso, "
                            "processamento, armazenamento e responsabilidade "
                            "durante todo o ciclo de vida da evidência."
                        ),
                        technology_dependencies=(
                            "digital_identity_verifiable_credentials",
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_timestamp_signature_validation"
                        ),
                        title="🕒 Tempo, assinatura e validação",
                        description=(
                            "Validação de horários, assinaturas, emissores, "
                            "certificados, sequência dos eventos "
                            "e consistência temporal dos registros."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "digital_identity_verifiable_credentials",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_access_usage_sharing_audit",
                title="👁️ Acesso, uso e compartilhamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_access_audit_trail",
                        title="🔐 Trilha de acesso aos dados",
                        description=(
                            "Registro de identidade, papel, recurso, "
                            "ação, horário, origem, resultado e motivo "
                            "dos acessos realizados aos dados."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "privacy_data_protection_lgpd",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_usage_purpose_tracking"
                        ),
                        title="🎯 Finalidade e utilização dos dados",
                        description=(
                            "Rastreamento das finalidades, processos, "
                            "aplicações, análises e decisões que utilizaram "
                            "determinado conjunto de informações."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "technology_governance_policy_compliance",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_sharing_transfer_traceability"
                        ),
                        title="🔄 Compartilhamentos e transferências",
                        description=(
                            "Registro de dados compartilhados, destinatários, "
                            "contratos, autorizações, canais, localização, "
                            "horários e confirmações de recebimento."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "privacy_enhancing_technologies",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_quality_incident_change_impact",
                title="🚨 Qualidade, mudanças e incidentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_quality_issue_provenance"
                        ),
                        title="✅ Origem de problemas de qualidade",
                        description=(
                            "Identificação das fontes, transformações, "
                            "processos e mudanças relacionadas a dados "
                            "incompletos, incorretos ou inconsistentes."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_change_impact_analysis"
                        ),
                        title="🔎 Impacto de alterações nos dados",
                        description=(
                            "Avaliação de sistemas, relatórios, modelos, "
                            "APIs, decisões e processos potencialmente "
                            "afetados por mudanças nas fontes ou estruturas."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                            "ai_software_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_incident_root_cause_trace"
                        ),
                        title="🩺 Causa raiz de incidentes de dados",
                        description=(
                            "Correlação de eventos, alterações, acessos, "
                            "transformações, falhas e dependências para "
                            "apoiar a investigação de incidentes."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "enterprise_rag",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "data_provenance_governance_observability"
                ),
                title="🧾 Governança, retenção e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "data_retention_disposition_trace"
                        ),
                        title="🗑️ Retenção e descarte rastreáveis",
                        description=(
                            "Registro de políticas, prazos, bloqueios, "
                            "arquivamentos, anonimizações, eliminações "
                            "e confirmações do descarte dos dados."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "technology_governance_policy_compliance",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_provenance_policy_compliance"
                        ),
                        title="⚖️ Políticas e conformidade da proveniência",
                        description=(
                            "Verificação de requisitos sobre origem, "
                            "linhagem, integridade, acesso, retenção, "
                            "evidências e responsabilidades."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "software_testing_quality_reliability",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "data_traceability_observability_reporting"
                        ),
                        title="📊 Observabilidade e relatórios",
                        description=(
                            "Monitoramento de cobertura da linhagem, "
                            "falhas de captura, atrasos, integrações, "
                            "custos, acessos e evidências disponíveis."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
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

    module_id = "data_traceability_provenance"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        48: (336, 1008),
        49: (343, 1029),
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

    print("DATA_TRACEABILITY_PROVENANCE_PREREQUISITES=OK")


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
    """Adiciona Rastreabilidade e Proveniência de Dados."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "DATA_TRACEABILITY_PROVENANCE_SOLUTION =" in source:
        print("DATA_TRACEABILITY_PROVENANCE_ALREADY_PRESENT=OK")
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
        DATA_TRACEABILITY_PROVENANCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    TECHNOLOGY_GOVERNANCE_POLICY_COMPLIANCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    DATA_TRACEABILITY_PROVENANCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("DATA_TRACEABILITY_PROVENANCE_SOLUTION_CREATED=OK")


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

    solution_name = "DATA_TRACEABILITY_PROVENANCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 48
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 49
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

    test_name = "def test_data_traceability_provenance_is_complete"

    if test_name not in source:
        source += """


def test_data_traceability_provenance_is_complete():
    assert (
        DATA_TRACEABILITY_PROVENANCE_SOLUTION.solution_id
        == "data_traceability_provenance"
    )

    assert len(
        DATA_TRACEABILITY_PROVENANCE_SOLUTION.areas
    ) == 7

    assert (
        DATA_TRACEABILITY_PROVENANCE_SOLUTION
        .capability_count
        == 21
    )


def test_data_traceability_provenance_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "data_traceability_provenance"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        DATA_TRACEABILITY_PROVENANCE_SOLUTION.status
        is module.status
    )

    assert (
        DATA_TRACEABILITY_PROVENANCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_data_traceability_provenance_lookup():
    assert (
        platform_technology_solution(
            "data_traceability_provenance"
        )
        is DATA_TRACEABILITY_PROVENANCE_SOLUTION
    )
"""

        print("DATA_TRACEABILITY_PROVENANCE_TESTS_CREATED=OK")
    else:
        print("DATA_TRACEABILITY_PROVENANCE_TESTS_ALREADY_PRESENT=OK")

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

    traceability_solution = module.DATA_TRACEABILITY_PROVENANCE_SOLUTION

    assert len(solutions) == 49
    assert len(traceability_solution.areas) == 7

    assert traceability_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 343
    assert total_capabilities == 1029

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=49")
    print("TOTAL_TECHNOLOGY_AREAS=343")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1029")
    print("DATA_TRACEABILITY_PROVENANCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
