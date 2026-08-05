"""Cria o registro tecnológico especializado do Enterprise RAG."""

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
    / ("enterprise_rag_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


REGISTRY_SOURCE = '''"""Registro de soluções tecnológicas especializadas da INNA."""

from __future__ import annotations

from dataclasses import dataclass

from src.platform_modules import (
    PLATFORM_MODULE_BY_ID,
    PlatformModuleCategory,
    PlatformModuleStatus,
)


@dataclass(frozen=True, slots=True)
class TechnologyCapability:
    """Capacidade interna de uma solução tecnológica."""

    capability_id: str
    title: str
    description: str
    technology_dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TechnologyArea:
    """Área especializada de uma solução tecnológica."""

    area_id: str
    title: str
    capabilities: tuple[TechnologyCapability, ...]


@dataclass(frozen=True, slots=True)
class PlatformTechnologySolution:
    """Solução tecnológica composta por áreas e capacidades."""

    solution_id: str
    icon: str
    title: str
    description: str
    status: PlatformModuleStatus
    integration_type: str
    areas: tuple[TechnologyArea, ...]

    @property
    def capability_count(self) -> int:
        """Retorna a quantidade total de capacidades."""

        return sum(
            len(area.capabilities)
            for area in self.areas
        )

    @property
    def technology_dependencies(self) -> tuple[str, ...]:
        """Retorna dependências sem duplicações."""

        return tuple(
            dict.fromkeys(
                dependency
                for area in self.areas
                for capability in area.capabilities
                for dependency in (
                    capability.technology_dependencies
                )
            )
        )


_ENTERPRISE_RAG_MODULE = (
    PLATFORM_MODULE_BY_ID["enterprise_rag"]
)


ENTERPRISE_RAG_SOLUTION = PlatformTechnologySolution(
    solution_id="enterprise_rag",
    icon="🧠",
    title="Enterprise RAG",
    description=(
        "Arquitetura tecnológica para ingestão, indexação, "
        "recuperação híbrida, reranking, geração fundamentada, "
        "avaliação, segurança, observabilidade e evolução "
        "de bases de conhecimento empresariais."
    ),
    status=_ENTERPRISE_RAG_MODULE.status,
    integration_type=(
        _ENTERPRISE_RAG_MODULE.integration_type
    ),
    areas=(
        TechnologyArea(
            area_id="rag_sources_ingestion",
            title="📥 Fontes e ingestão de conhecimento",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_source_connectors",
                    title="🔌 Conectores de fontes",
                    description=(
                        "Integração com documentos, APIs, bancos de dados, "
                        "armazenamentos e sistemas empresariais autorizados."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "document_ai",
                        "data_platform_governance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_document_parsing_chunking",
                    title="📄 Leitura, segmentação e chunking",
                    description=(
                        "Preparação de documentos, extração de conteúdo "
                        "e segmentação em unidades adequadas à recuperação."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "multimodal_ai",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_metadata_enrichment",
                    title="🏷️ Metadados e enriquecimento semântico",
                    description=(
                        "Inclusão de origem, assunto, entidades, permissões, "
                        "datas, versões e outros metadados relevantes."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_indexing_representations",
            title="🗄️ Indexação e representações",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_embedding_generation",
                    title="🧮 Geração de embeddings",
                    description=(
                        "Conversão de conteúdos em representações vetoriais "
                        "para recuperação por similaridade semântica."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "scientific_computing_engineering",
                        "ai_evaluation_benchmarks_red_team",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_vector_index",
                    title="📐 Índice vetorial",
                    description=(
                        "Armazenamento, consulta, filtragem e manutenção "
                        "de vetores e representações semânticas."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "cloud_devops_finops",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_lexical_index",
                    title="🔤 Índice lexical e textual",
                    description=(
                        "Indexação por termos, frequência, campos, filtros "
                        "e critérios de busca textual."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_retrieval_orchestration",
            title="🔎 Recuperação e orquestração",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_hybrid_retrieval",
                    title="🔎 Recuperação híbrida",
                    description=(
                        "Combinação de busca semântica, lexical, filtros "
                        "e outras estratégias de recuperação."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "enterprise_decision_intelligence",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_query_rewriting_routing",
                    title="🧭 Reescrita e roteamento de consultas",
                    description=(
                        "Interpretação, reformulação, decomposição "
                        "e direcionamento da consulta para fontes adequadas."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "knowledge_graph_semantic_ai",
                        "multimodal_ai",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_access_aware_filtering",
                    title="🔐 Filtragem por acesso e contexto",
                    description=(
                        "Aplicação de permissões, escopo, usuário, idioma, "
                        "origem, período e regras de acesso."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "privacy_data_protection_lgpd",
                        "data_platform_governance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_ranking_context",
            title="🎯 Ranking e construção de contexto",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_reranking",
                    title="🎯 Reranking de resultados",
                    description=(
                        "Reordenação dos resultados recuperados conforme "
                        "relevância, contexto, qualidade e critérios definidos."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "ai_evaluation_benchmarks_red_team",
                        "model_explainability_interpretability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_context_compression",
                    title="🗜️ Compressão e deduplicação de contexto",
                    description=(
                        "Redução de redundâncias, remoção de conteúdo "
                        "irrelevante e seleção de trechos essenciais."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "software_testing_quality_reliability",
                        "tools_analytics",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_context_assembly",
                    title="🧩 Montagem do contexto",
                    description=(
                        "Organização de evidências, instruções, histórico, "
                        "metadados e limites antes da geração."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "knowledge_graph_semantic_ai",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_grounded_generation",
            title="💬 Geração fundamentada",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_grounded_answer_generation",
                    title="💬 Geração baseada em evidências",
                    description=(
                        "Produção de respostas sustentadas pelo contexto "
                        "recuperado e pelas regras definidas."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "responsible_ai_ethics_risk",
                        "model_explainability_interpretability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_citations_provenance",
                    title="🔗 Citações e proveniência",
                    description=(
                        "Associação da resposta às fontes, trechos, versões, "
                        "documentos e evidências utilizadas."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "document_ai",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_abstention_fallback",
                    title="🛑 Abstenção e fallback seguro",
                    description=(
                        "Recusa controlada, solicitação de esclarecimento "
                        "ou encaminhamento quando não houver evidência suficiente."
                    ),
                    technology_dependencies=(
                        "responsible_ai_ethics_risk",
                        "agent_process_orchestration",
                        "ai_evaluation_benchmarks_red_team",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_evaluation_security_governance",
            title="🛡️ Avaliação, segurança e governança",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_offline_online_evaluation",
                    title="🧪 Avaliação offline e online",
                    description=(
                        "Medição de recuperação, relevância, fidelidade, "
                        "qualidade, cobertura e utilidade das respostas."
                    ),
                    technology_dependencies=(
                        "ai_evaluation_benchmarks_red_team",
                        "ai_bias_quality_monitoring",
                        "tools_analytics",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_adversarial_security",
                    title="🛡️ Segurança e testes adversariais",
                    description=(
                        "Avaliação de injeção de instruções, vazamento, "
                        "manipulação de contexto e uso indevido."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "ai_evaluation_benchmarks_red_team",
                        "zero_trust_identity_access",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_privacy_governance",
                    title="🔐 Privacidade e governança do conhecimento",
                    description=(
                        "Gestão de acesso, retenção, descarte, dados sensíveis, "
                        "políticas e evidências de conformidade."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="rag_observability_lifecycle",
            title="📊 Observabilidade e ciclo de vida",
            capabilities=(
                TechnologyCapability(
                    capability_id="rag_tracing_metrics",
                    title="📊 Tracing, métricas e monitoramento",
                    description=(
                        "Acompanhamento de consultas, fontes, latência, "
                        "tokens, custos, erros e qualidade operacional."
                    ),
                    technology_dependencies=(
                        "ai_operations",
                        "tools_analytics",
                        "cloud_devops_finops",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_feedback_human_review",
                    title="👤 Feedback e revisão humana",
                    description=(
                        "Coleta de avaliações e encaminhamento de casos "
                        "para aprovação, correção ou investigação."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "quality_process_management",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="rag_index_refresh_versioning",
                    title="🔄 Atualização e versionamento dos índices",
                    description=(
                        "Reindexação, atualização incremental, invalidação, "
                        "versionamento e recuperação de versões anteriores."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "data_traceability_provenance",
                        "cloud_devops_finops",
                    ),
                ),
            ),
        ),
    ),
)


PLATFORM_TECHNOLOGY_SOLUTIONS: tuple[
    PlatformTechnologySolution,
    ...
] = (
    ENTERPRISE_RAG_SOLUTION,
)


PLATFORM_TECHNOLOGY_SOLUTION_BY_ID = {
    solution.solution_id: solution
    for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
}


def platform_technology_solution(
    solution_id: str,
) -> PlatformTechnologySolution | None:
    """Retorna uma solução tecnológica pelo ID."""

    return PLATFORM_TECHNOLOGY_SOLUTION_BY_ID.get(
        solution_id
    )


def validate_platform_technology_solution_registry() -> None:
    """Valida o registro tecnológico especializado."""

    solution_ids = [
        solution.solution_id
        for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    ]

    if len(solution_ids) != len(set(solution_ids)):
        raise ValueError(
            "Existem soluções tecnológicas duplicadas."
        )

    for solution in PLATFORM_TECHNOLOGY_SOLUTIONS:
        module = PLATFORM_MODULE_BY_ID.get(
            solution.solution_id
        )

        if module is None:
            raise ValueError(
                "Módulo tecnológico inexistente: "
                f"{solution.solution_id}"
            )

        if (
            module.category
            is not PlatformModuleCategory.TECHNOLOGY_CORE
        ):
            raise ValueError(
                "Solução fora da categoria tecnológica: "
                f"{solution.solution_id}"
            )

        if solution.status is not module.status:
            raise ValueError(
                "Status tecnológico divergente: "
                f"{solution.solution_id}"
            )

        if (
            solution.integration_type
            != module.integration_type
        ):
            raise ValueError(
                "Integração tecnológica divergente: "
                f"{solution.solution_id}"
            )

        if not solution.areas:
            raise ValueError(
                "Solução tecnológica sem áreas: "
                f"{solution.solution_id}"
            )

        area_ids = [
            area.area_id
            for area in solution.areas
        ]

        if len(area_ids) != len(set(area_ids)):
            raise ValueError(
                "Áreas tecnológicas duplicadas em: "
                f"{solution.solution_id}"
            )

        capability_ids = [
            capability.capability_id
            for area in solution.areas
            for capability in area.capabilities
        ]

        if len(capability_ids) != len(
            set(capability_ids)
        ):
            raise ValueError(
                "Capacidades tecnológicas duplicadas em: "
                f"{solution.solution_id}"
            )

        for area in solution.areas:
            if not area.capabilities:
                raise ValueError(
                    "Área tecnológica sem capacidades: "
                    f"{area.area_id}"
                )

            for capability in area.capabilities:
                if not capability.technology_dependencies:
                    raise ValueError(
                        "Capacidade sem dependências: "
                        f"{capability.capability_id}"
                    )

                missing_dependencies = {
                    dependency
                    for dependency in (
                        capability.technology_dependencies
                    )
                    if dependency
                    not in PLATFORM_MODULE_BY_ID
                }

                if missing_dependencies:
                    raise ValueError(
                        "Dependências tecnológicas inexistentes em "
                        f"{capability.capability_id}: "
                        f"{sorted(missing_dependencies)}"
                    )


validate_platform_technology_solution_registry()
'''


TEST_SOURCE = """from src.platform_modules import (
    PLATFORM_MODULE_BY_ID,
    PlatformModuleCategory,
)
from src.platform_technology_solutions import (
    ENTERPRISE_RAG_SOLUTION,
    PLATFORM_TECHNOLOGY_SOLUTIONS,
    platform_technology_solution,
    validate_platform_technology_solution_registry,
)


def test_technology_solution_registry_is_valid():
    validate_platform_technology_solution_registry()


def test_enterprise_rag_is_registered():
    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 1

    assert (
        platform_technology_solution(
            "enterprise_rag"
        )
        is ENTERPRISE_RAG_SOLUTION
    )


def test_enterprise_rag_solution_is_complete():
    assert (
        ENTERPRISE_RAG_SOLUTION.solution_id
        == "enterprise_rag"
    )

    assert len(
        ENTERPRISE_RAG_SOLUTION.areas
    ) == 7

    assert (
        ENTERPRISE_RAG_SOLUTION.capability_count
        == 21
    )


def test_enterprise_rag_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "enterprise_rag"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ENTERPRISE_RAG_SOLUTION.status
        is module.status
    )

    assert (
        ENTERPRISE_RAG_SOLUTION.integration_type
        == module.integration_type
    )


def test_enterprise_rag_capabilities_have_dependencies():
    for area in ENTERPRISE_RAG_SOLUTION.areas:
        assert area.capabilities

        for capability in area.capabilities:
            assert capability.technology_dependencies


def test_enterprise_rag_dependency_list_has_no_duplicates():
    dependencies = (
        ENTERPRISE_RAG_SOLUTION.technology_dependencies
    )

    assert dependencies
    assert len(dependencies) == len(set(dependencies))


def test_unknown_technology_solution_returns_none():
    assert (
        platform_technology_solution(
            "unknown_technology_solution"
        )
        is None
    )
"""


def create_backup() -> None:
    """Cria backup caso algum arquivo já exista."""

    existing_paths = tuple(
        path
        for path in (
            REGISTRY_PATH,
            TEST_PATH,
        )
        if path.exists()
    )

    if not existing_paths:
        print("BACKUP_NOT_REQUIRED=OK")
        return

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for source_path in existing_paths:
        shutil.copy2(
            source_path,
            BACKUP_ROOT / source_path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")


def create_files() -> None:
    """Cria o registro tecnológico e os testes."""

    if REGISTRY_PATH.exists() or TEST_PATH.exists():
        registry_source = (
            REGISTRY_PATH.read_text(
                encoding="utf-8",
            )
            if REGISTRY_PATH.exists()
            else ""
        )

        test_source = (
            TEST_PATH.read_text(
                encoding="utf-8",
            )
            if TEST_PATH.exists()
            else ""
        )

        if (
            "ENTERPRISE_RAG_SOLUTION" in registry_source
            and "test_enterprise_rag_solution_is_complete" in test_source
        ):
            print("ENTERPRISE_RAG_TECHNOLOGY_ALREADY_PRESENT=OK")
            return

        raise RuntimeError(
            "Registro tecnológico existente ou incompleto. Audite antes de substituir."
        )

    REGISTRY_PATH.write_text(
        REGISTRY_SOURCE,
        encoding="utf-8",
    )

    print("ENTERPRISE_RAG_TECHNOLOGY_REGISTRY_CREATED=OK")

    TEST_PATH.write_text(
        TEST_SOURCE,
        encoding="utf-8",
    )

    print("ENTERPRISE_RAG_TECHNOLOGY_TESTS_CREATED=OK")


def validate_result() -> None:
    """Importa e valida a solução criada."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    enterprise_rag = getattr(
        module,
        "ENTERPRISE_RAG_SOLUTION",
    )

    assert len(solutions) == 1
    assert len(enterprise_rag.areas) == 7
    assert enterprise_rag.capability_count == 21

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=1")
    print("TOTAL_TECHNOLOGY_AREAS=7")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=21")
    print("ENTERPRISE_RAG_TECHNOLOGY_EXPANSION_VALIDATED=OK")


create_backup()
create_files()
validate_result()
