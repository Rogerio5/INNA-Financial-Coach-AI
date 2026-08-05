"""Adiciona Data Platform e Governança ao registro tecnológico."""

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
        "data_platform_governance_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


DATA_PLATFORM_GOVERNANCE_DEFINITION = """
_DATA_PLATFORM_GOVERNANCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "data_platform_governance"
    ]
)


DATA_PLATFORM_GOVERNANCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="data_platform_governance",
        icon="🗄️",
        title="Data Platform e Governança",
        description=(
            "Arquitetura tecnológica para ingestão, armazenamento, "
            "processamento, catálogo, qualidade, linhagem, segurança, "
            "privacidade, interoperabilidade, observabilidade e "
            "disponibilização governada de dados empresariais."
        ),
        status=(
            _DATA_PLATFORM_GOVERNANCE_MODULE.status
        ),
        integration_type=(
            _DATA_PLATFORM_GOVERNANCE_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="data_platform_sources_ingestion",
                title="📥 Fontes e ingestão de dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_source_connectors",
                        title="🔌 Conectores de fontes",
                        description=(
                            "Integração com bancos de dados, APIs, arquivos, "
                            "sistemas empresariais, eventos e serviços externos."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_batch_stream_ingestion",
                        title="⚡ Ingestão em lote e streaming",
                        description=(
                            "Recebimento de dados por lotes, eventos, filas "
                            "e fluxos contínuos com controle operacional."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_schema_contracts",
                        title="📋 Contratos e validação de esquemas",
                        description=(
                            "Definição de formatos, campos, tipos, regras, "
                            "compatibilidade e evolução dos contratos de dados."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_storage_lifecycle",
                title="🏛️ Armazenamento e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_lakehouse_zones",
                        title="🏛️ Lakehouse e zonas de dados",
                        description=(
                            "Organização de dados brutos, tratados, "
                            "curados e disponibilizados em camadas controladas."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_partitioning_optimization",
                        title="📦 Particionamento e otimização",
                        description=(
                            "Estruturação de partições, formatos, índices, "
                            "compactação e estratégias de desempenho."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_retention_archival",
                        title="🗃️ Retenção, arquivamento e descarte",
                        description=(
                            "Controle do período de retenção, arquivamento, "
                            "recuperação e descarte seguro dos dados."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "technology_governance_policy_compliance",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_processing_orchestration",
                title="⚙️ Processamento e orquestração",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_etl_elt_pipelines",
                        title="⚙️ Pipelines ETL e ELT",
                        description=(
                            "Extração, transformação, padronização, "
                            "combinação e carregamento de dados."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "scientific_computing_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_pipeline_orchestration",
                        title="🧩 Orquestração de pipelines",
                        description=(
                            "Coordenação de etapas, dependências, agendas, "
                            "eventos, retries e tratamento de falhas."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_incremental_cdc",
                        title="🔄 Processamento incremental e CDC",
                        description=(
                            "Identificação e processamento de inclusões, "
                            "alterações e exclusões desde a última execução."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_catalog_metadata_lineage",
                title="🏷️ Catálogo, metadados e linhagem",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_data_catalog",
                        title="📚 Catálogo e descoberta de dados",
                        description=(
                            "Organização de fontes, tabelas, campos, produtos, "
                            "responsáveis, descrições e condições de uso."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_business_glossary",
                        title="🏷️ Glossário e metadados semânticos",
                        description=(
                            "Definição de conceitos empresariais, termos, "
                            "sinônimos, métricas e relacionamentos."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_lineage_provenance",
                        title="🔗 Linhagem e proveniência",
                        description=(
                            "Rastreamento da origem, transformações, "
                            "dependências, versões e destinos dos dados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_quality_observability",
                title="✅ Qualidade e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_quality_rules",
                        title="✅ Regras de qualidade de dados",
                        description=(
                            "Validação de completude, consistência, "
                            "unicidade, formato, validade e integridade."
                        ),
                        technology_dependencies=(
                            "quality_process_management",
                            "software_testing_quality_reliability",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_freshness_anomalies",
                        title="⚠️ Atualização, esquemas e anomalias",
                        description=(
                            "Monitoramento de atrasos, mudanças de esquema, "
                            "variações, volumes incomuns e falhas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "ai_bias_quality_monitoring",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_pipeline_observability",
                        title="📊 Observabilidade dos pipelines",
                        description=(
                            "Acompanhamento de execuções, duração, filas, "
                            "falhas, consumo, dependências e resultados."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_security_privacy_governance",
                title="🛡️ Segurança, privacidade e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_identity_access",
                        title="🔐 Identidade e controle de acesso",
                        description=(
                            "Gestão de usuários, serviços, papéis, permissões, "
                            "escopos e acesso baseado em necessidade."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_encryption_masking",
                        title="🕶️ Criptografia, mascaramento e privacidade",
                        description=(
                            "Proteção de dados armazenados ou transmitidos, "
                            "anonimização e redução de exposição."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_policy_audit",
                        title="🧾 Políticas, conformidade e auditoria",
                        description=(
                            "Aplicação de políticas e registro de acessos, "
                            "alterações, decisões, responsáveis e evidências."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "legal_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="data_platform_serving_interoperability",
                title="🚀 Disponibilização e interoperabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="data_platform_data_products",
                        title="📦 Produtos de dados e camada semântica",
                        description=(
                            "Disponibilização de conjuntos de dados, métricas, "
                            "modelos semânticos e contratos reutilizáveis."
                        ),
                        technology_dependencies=(
                            "data_bi_copilot",
                            "knowledge_graph_semantic_ai",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_apis_sharing",
                        title="🔌 APIs, compartilhamento e interoperabilidade",
                        description=(
                            "Distribuição controlada de dados por APIs, "
                            "consultas, arquivos, eventos e integrações."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="data_platform_performance_finops",
                        title="💰 Desempenho, capacidade e FinOps",
                        description=(
                            "Monitoramento e otimização de consultas, "
                            "armazenamento, processamento, recursos e custos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
        ),
    )
)


"""


def validate_prerequisites() -> None:
    """Valida o registro e o módulo principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )

    module_id = "data_platform_governance"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("DATA_PLATFORM_GOVERNANCE_PREREQUISITES=OK")


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
    """Adiciona Data Platform e Governança."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "DATA_PLATFORM_GOVERNANCE_SOLUTION =" in source:
        print("DATA_PLATFORM_GOVERNANCE_ALREADY_PRESENT=OK")
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
        DATA_PLATFORM_GOVERNANCE_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    VOICE_AUDIO_SPEECH_AI_SOLUTION,
    AI_OPERATIONS_SOLUTION,
)"""

    new_registry = """    VOICE_AUDIO_SPEECH_AI_SOLUTION,
    AI_OPERATIONS_SOLUTION,
    DATA_PLATFORM_GOVERNANCE_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro tecnológico não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("DATA_PLATFORM_GOVERNANCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_data_platform_governance_is_complete" in source:
        print("DATA_PLATFORM_GOVERNANCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "DATA_PLATFORM_GOVERNANCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 7
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 8
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de sete soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_data_platform_governance_is_complete():
    assert (
        DATA_PLATFORM_GOVERNANCE_SOLUTION.solution_id
        == "data_platform_governance"
    )

    assert len(
        DATA_PLATFORM_GOVERNANCE_SOLUTION.areas
    ) == 7

    assert (
        DATA_PLATFORM_GOVERNANCE_SOLUTION.capability_count
        == 21
    )


def test_data_platform_governance_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "data_platform_governance"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        DATA_PLATFORM_GOVERNANCE_SOLUTION.status
        is module.status
    )

    assert (
        DATA_PLATFORM_GOVERNANCE_SOLUTION.integration_type
        == module.integration_type
    )


def test_data_platform_governance_lookup():
    assert (
        platform_technology_solution(
            "data_platform_governance"
        )
        is DATA_PLATFORM_GOVERNANCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("DATA_PLATFORM_GOVERNANCE_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    data_platform_solution = getattr(
        module,
        "DATA_PLATFORM_GOVERNANCE_SOLUTION",
    )

    assert len(solutions) == 8

    assert len(data_platform_solution.areas) == 7

    assert data_platform_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 56
    assert total_capabilities == 168

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=8")
    print("TOTAL_TECHNOLOGY_AREAS=56")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=168")
    print("DATA_PLATFORM_GOVERNANCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
