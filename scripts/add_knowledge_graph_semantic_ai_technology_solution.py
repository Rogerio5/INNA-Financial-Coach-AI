"""Adiciona Knowledge Graph e IA Semântica ao registro tecnológico."""

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
        "knowledge_graph_semantic_ai_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


KNOWLEDGE_GRAPH_DEFINITION = """
_KNOWLEDGE_GRAPH_SEMANTIC_AI_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "knowledge_graph_semantic_ai"
    ]
)


KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="knowledge_graph_semantic_ai",
        icon="🕸️",
        title="Knowledge Graph e IA Semântica",
        description=(
            "Arquitetura tecnológica para ontologias, entidades, "
            "relacionamentos, construção de grafos, pesquisa semântica, "
            "Graph RAG, inferência, governança, segurança, qualidade "
            "e observabilidade do conhecimento empresarial."
        ),
        status=(
            _KNOWLEDGE_GRAPH_SEMANTIC_AI_MODULE.status
        ),
        integration_type=(
            _KNOWLEDGE_GRAPH_SEMANTIC_AI_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="semantic_modeling_ontologies",
                title="🧩 Modelagem semântica e ontologias",
                capabilities=(
                    TechnologyCapability(
                        capability_id="semantic_domain_ontology",
                        title="🧩 Ontologias de domínio",
                        description=(
                            "Definição de conceitos, classes, propriedades, "
                            "relações e regras semânticas de cada domínio."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "data_platform_governance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="semantic_taxonomies_vocabularies",
                        title="🏷️ Taxonomias e vocabulários",
                        description=(
                            "Organização de categorias, termos, sinônimos, "
                            "hierarquias e vocabulários empresariais."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "data_platform_governance",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="semantic_schema_mapping",
                        title="🔄 Mapeamento de esquemas e conceitos",
                        description=(
                            "Correspondência entre campos, tabelas, documentos, "
                            "conceitos e modelos de diferentes sistemas."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="semantic_entity_understanding",
                title="🧠 Entidades e compreensão semântica",
                capabilities=(
                    TechnologyCapability(
                        capability_id="semantic_entity_extraction",
                        title="🔎 Extração de entidades",
                        description=(
                            "Identificação de pessoas, empresas, produtos, "
                            "locais, eventos, valores e conceitos em conteúdos."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "document_ai",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="semantic_entity_resolution",
                        title="🪪 Resolução e unificação de entidades",
                        description=(
                            "Identificação de registros equivalentes, "
                            "duplicidades, aliases e relações entre identidades."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "privacy_enhancing_technologies",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="semantic_relation_extraction",
                        title="🔗 Extração de relacionamentos",
                        description=(
                            "Detecção de relações, dependências, eventos "
                            "e conexões entre entidades e conceitos."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "enterprise_rag",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="knowledge_graph_construction",
                title="🏗️ Construção e integração do grafo",
                capabilities=(
                    TechnologyCapability(
                        capability_id="knowledge_graph_ingestion",
                        title="📥 Ingestão de dados e conhecimento",
                        description=(
                            "Recebimento de dados estruturados, documentos, "
                            "eventos e informações de sistemas autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "document_ai",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_generation",
                        title="🏗️ Geração de nós e relacionamentos",
                        description=(
                            "Construção controlada de entidades, propriedades, "
                            "arestas, evidências e relações semânticas."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "agent_process_orchestration",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_incremental_updates",
                        title="🔄 Atualização incremental do grafo",
                        description=(
                            "Inclusão, alteração, invalidação e remoção "
                            "controlada de conhecimento conforme novas fontes."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "business_automation",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="knowledge_graph_query_reasoning",
                title="🔍 Consultas e raciocínio semântico",
                capabilities=(
                    TechnologyCapability(
                        capability_id="knowledge_graph_query_engine",
                        title="🔍 Consultas sobre o grafo",
                        description=(
                            "Pesquisa de entidades, relações, caminhos, "
                            "propriedades e padrões no conhecimento."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "enterprise_decision_intelligence",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_path_discovery",
                        title="🧭 Descoberta de caminhos e conexões",
                        description=(
                            "Identificação de relações indiretas, dependências, "
                            "cadeias de eventos e conexões relevantes."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_rule_inference",
                        title="⚖️ Regras e inferência semântica",
                        description=(
                            "Aplicação de regras explícitas para derivar "
                            "relações, classificações e conclusões controladas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="knowledge_graph_rag_context",
                title="📚 Graph RAG e contexto",
                capabilities=(
                    TechnologyCapability(
                        capability_id="knowledge_graph_rag_retrieval",
                        title="📚 Recuperação Graph RAG",
                        description=(
                            "Combinação de recuperação documental, vetorial "
                            "e baseada em entidades e relacionamentos."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "agent_process_orchestration",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_context_expansion",
                        title="🧩 Expansão semântica de contexto",
                        description=(
                            "Ampliação do contexto com entidades relacionadas, "
                            "vizinhanças, hierarquias e evidências conectadas."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "multimodal_ai",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_citations_provenance",
                        title="🔗 Evidências, citações e proveniência",
                        description=(
                            "Ligação entre respostas, entidades, relações, "
                            "documentos, trechos e fontes utilizadas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "document_ai",
                            "enterprise_rag",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="knowledge_graph_quality_governance_security",
                title="🛡️ Qualidade, governança e segurança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="knowledge_graph_quality_validation",
                        title="✅ Validação da qualidade do grafo",
                        description=(
                            "Verificação de duplicidades, relações inválidas, "
                            "inconsistências, lacunas e dados desatualizados."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_bias_quality_monitoring",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_access_privacy",
                        title="🔐 Acesso e privacidade semântica",
                        description=(
                            "Aplicação de permissões sobre entidades, "
                            "relações, propriedades, fontes e consultas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_governance_audit",
                        title="🧾 Governança e auditoria",
                        description=(
                            "Registro de alterações, responsáveis, versões, "
                            "fontes, decisões e políticas do conhecimento."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="knowledge_graph_observability_lifecycle",
                title="📊 Observabilidade e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="knowledge_graph_metrics_monitoring",
                        title="📊 Métricas e monitoramento",
                        description=(
                            "Acompanhamento de volume, crescimento, consultas, "
                            "latência, qualidade, cobertura e erros."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_versioning",
                        title="🗃️ Versionamento e histórico",
                        description=(
                            "Controle de versões de ontologias, entidades, "
                            "relações, regras e transformações."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="knowledge_graph_feedback_review",
                        title="👤 Feedback e revisão humana",
                        description=(
                            "Encaminhamento de entidades, relações e inferências "
                            "duvidosas para validação e correção humana."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "quality_process_management",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
        ),
    )
)


"""


def validate_prerequisites() -> None:
    """Valida o registro tecnológico e o módulo principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )

    module_id = "knowledge_graph_semantic_ai"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("KNOWLEDGE_GRAPH_SEMANTIC_AI_PREREQUISITES=OK")


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
    """Adiciona Knowledge Graph ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION =" in source:
        print("KNOWLEDGE_GRAPH_SEMANTIC_AI_ALREADY_PRESENT=OK")
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
        KNOWLEDGE_GRAPH_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    ENTERPRISE_RAG_SOLUTION,
    AGENT_PROCESS_ORCHESTRATION_SOLUTION,
)"""

    new_registry = """    ENTERPRISE_RAG_SOLUTION,
    AGENT_PROCESS_ORCHESTRATION_SOLUTION,
    KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError(
            "Registro atual das duas soluções tecnológicas não encontrado."
        )

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_knowledge_graph_semantic_ai_is_complete" in source:
        print("KNOWLEDGE_GRAPH_SEMANTIC_AI_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 2
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 3
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de duas soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_knowledge_graph_semantic_ai_is_complete():
    assert (
        KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION.solution_id
        == "knowledge_graph_semantic_ai"
    )

    assert len(
        KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION.areas
    ) == 7

    assert (
        KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION.capability_count
        == 21
    )


def test_knowledge_graph_semantic_ai_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "knowledge_graph_semantic_ai"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION.status
        is module.status
    )

    assert (
        KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION.integration_type
        == module.integration_type
    )


def test_knowledge_graph_semantic_ai_lookup():
    assert (
        platform_technology_solution(
            "knowledge_graph_semantic_ai"
        )
        is KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("KNOWLEDGE_GRAPH_SEMANTIC_AI_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    knowledge_graph_solution = getattr(
        module,
        "KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION",
    )

    assert len(solutions) == 3

    assert len(knowledge_graph_solution.areas) == 7

    assert knowledge_graph_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 21
    assert total_capabilities == 63

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=3")
    print("TOTAL_TECHNOLOGY_AREAS=21")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=63")
    print("KNOWLEDGE_GRAPH_SEMANTIC_AI_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
