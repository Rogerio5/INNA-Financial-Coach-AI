"""Adiciona Pesquisa, Laboratórios e Descoberta Assistida ao registro."""

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
        "research_labs_assisted_discovery_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


RESEARCH_LABS_ASSISTED_DISCOVERY_DEFINITION = """
_RESEARCH_LABS_ASSISTED_DISCOVERY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "research_labs_assisted_discovery"
    ]
)


RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="research_labs_assisted_discovery",
        icon="🔬",
        title="Pesquisa, Laboratórios e Descoberta Assistida",
        description=(
            "Arquitetura tecnológica para perguntas de pesquisa, "
            "hipóteses, revisão de conhecimento, planejamento "
            "experimental, integração com laboratórios, coleta "
            "de resultados, análise científica, descoberta assistida "
            "por IA, colaboração, reprodutibilidade, segurança, "
            "governança e operação do ciclo de pesquisa."
        ),
        status=(
            _RESEARCH_LABS_ASSISTED_DISCOVERY_MODULE.status
        ),
        integration_type=(
            _RESEARCH_LABS_ASSISTED_DISCOVERY_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="research_questions_hypotheses",
                title="🧭 Perguntas, hipóteses e planejamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_question_formulation",
                        title="❓ Formulação de perguntas de pesquisa",
                        description=(
                            "Estruturação de objetivos, problemas, "
                            "variáveis, escopo, critérios e resultados "
                            "esperados para cada iniciativa científica."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_hypothesis_generation",
                        title="💡 Geração assistida de hipóteses",
                        description=(
                            "Proposição de hipóteses fundamentadas em "
                            "evidências, lacunas, relações conhecidas "
                            "e resultados anteriores."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_study_planning",
                        title="📋 Planejamento de estudos",
                        description=(
                            "Definição de etapas, recursos, dependências, "
                            "cronogramas, riscos, critérios de aceitação "
                            "e responsabilidades da pesquisa."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_literature_knowledge_evidence",
                title="📚 Literatura, conhecimento e evidências",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_literature_search",
                        title="🔎 Pesquisa de literatura e documentos",
                        description=(
                            "Recuperação de artigos, relatórios, protocolos, "
                            "documentos técnicos e outras fontes relevantes "
                            "para a investigação."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "document_ai",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_evidence_synthesis",
                        title="🧠 Síntese e comparação de evidências",
                        description=(
                            "Organização de resultados, métodos, limitações, "
                            "convergências, divergências e níveis "
                            "de confiança das fontes."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "model_explainability_interpretability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_knowledge_graph",
                        title="🔗 Grafo de conhecimento científico",
                        description=(
                            "Representação de autores, estudos, materiais, "
                            "métodos, variáveis, resultados, hipóteses "
                            "e relações científicas."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_traceability_provenance",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_experiment_design_protocols",
                title="🧪 Experimentos e protocolos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_experiment_design",
                        title="🧪 Planejamento experimental",
                        description=(
                            "Definição de fatores, níveis, tratamentos, "
                            "controles, repetições, amostragem "
                            "e critérios de comparação."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "scientific_computing_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_protocol_management",
                        title="📋 Protocolos e procedimentos",
                        description=(
                            "Criação, versionamento, aprovação e execução "
                            "controlada de protocolos, métodos "
                            "e procedimentos laboratoriais."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "business_automation",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_simulation_prevalidation",
                        title="🖥️ Simulação e pré-validação",
                        description=(
                            "Avaliação virtual de configurações, parâmetros, "
                            "cenários, riscos e resultados esperados "
                            "antes do experimento real."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "scientific_computing_engineering",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_lab_data_instrumentation",
                title="🔬 Laboratórios, instrumentos e dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_instrument_integrations",
                        title="🔌 Integração com instrumentos",
                        description=(
                            "Integração controlada de equipamentos, sensores, "
                            "sistemas laboratoriais, arquivos, APIs "
                            "e serviços de aquisição."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_sample_asset_tracking",
                        title="🏷️ Amostras, materiais e ativos",
                        description=(
                            "Registro de amostras, materiais, lotes, "
                            "instrumentos, responsáveis, localização, "
                            "condições e histórico de utilização."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "materials_product_engineering",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_measurement_quality",
                        title="✅ Qualidade das medições",
                        description=(
                            "Validação de calibração, precisão, repetibilidade, "
                            "valores ausentes, anomalias e consistência "
                            "dos resultados coletados."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "software_testing_quality_reliability",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_analysis_discovery_ai",
                title="🧠 Análise científica e descoberta assistida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_statistical_analysis",
                        title="📊 Análise estatística científica",
                        description=(
                            "Aplicação de estatísticas, testes, intervalos, "
                            "comparações, correlações e avaliação "
                            "da significância dos resultados."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_pattern_discovery",
                        title="🔎 Descoberta de padrões e relações",
                        description=(
                            "Identificação de agrupamentos, associações, "
                            "tendências, anomalias e relações relevantes "
                            "nos dados experimentais."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_assisted_interpretation",
                        title="💡 Interpretação assistida de resultados",
                        description=(
                            "Geração de explicações, hipóteses alternativas, "
                            "limitações e próximos passos com evidências "
                            "e níveis de confiança."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "enterprise_rag",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_collaboration_reproducibility",
                title="👥 Colaboração e reprodutibilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_collaborative_workspace",
                        title="👥 Espaço colaborativo de pesquisa",
                        description=(
                            "Compartilhamento controlado de projetos, "
                            "anotações, dados, métodos, resultados, "
                            "tarefas e discussões."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "api_integrations_connectors",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_reproducible_experiments",
                        title="♻️ Experimentos reproduzíveis",
                        description=(
                            "Preservação de código, dados, parâmetros, "
                            "ambientes, versões, sementes e instruções "
                            "necessárias para repetição."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "data_traceability_provenance",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_results_publication",
                        title="📄 Relatórios e publicação de resultados",
                        description=(
                            "Produção de relatórios, tabelas, gráficos, "
                            "artefatos, evidências e pacotes de resultados "
                            "para revisão e comunicação."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="research_governance_safety_operations",
                title="🛡️ Governança, segurança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="research_ethics_compliance",
                        title="⚖️ Ética, políticas e conformidade",
                        description=(
                            "Aplicação de políticas, aprovações, limites, "
                            "responsabilidades, consentimentos "
                            "e critérios éticos da pesquisa."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_access_data_protection",
                        title="🔐 Acesso e proteção dos dados",
                        description=(
                            "Controle de acesso a estudos, amostras, "
                            "resultados, informações confidenciais "
                            "e propriedade intelectual."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "privacy_data_protection_lgpd",
                            "cryptography_confidential_computing",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="research_observability_audit",
                        title="📊 Observabilidade e auditoria",
                        description=(
                            "Monitoramento de pipelines, jobs, instrumentos, "
                            "erros, recursos, custos, versões, acessos, "
                            "alterações e resultados."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
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

    module_id = "research_labs_assisted_discovery"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        28: (196, 588),
        29: (203, 609),
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

    print("RESEARCH_LABS_ASSISTED_DISCOVERY_PREREQUISITES=OK")


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
    """Adiciona Pesquisa, Laboratórios e Descoberta Assistida."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION =" in source:
        print("RESEARCH_LABS_ASSISTED_DISCOVERY_ALREADY_PRESENT=OK")
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
        RESEARCH_LABS_ASSISTED_DISCOVERY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_research_labs_assisted_discovery_is_complete"

    if test_name in source:
        print("RESEARCH_LABS_ASSISTED_DISCOVERY_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 28
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 29
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e oito soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_research_labs_assisted_discovery_is_complete():
    assert (
        RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION.solution_id
        == "research_labs_assisted_discovery"
    )

    assert len(
        RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION.areas
    ) == 7

    assert (
        RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION.capability_count
        == 21
    )


def test_research_labs_assisted_discovery_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "research_labs_assisted_discovery"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION.status
        is module.status
    )

    assert (
        RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION.integration_type
        == module.integration_type
    )


def test_research_labs_assisted_discovery_lookup():
    assert (
        platform_technology_solution(
            "research_labs_assisted_discovery"
        )
        is RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("RESEARCH_LABS_ASSISTED_DISCOVERY_TESTS_CREATED=OK")


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

    research_solution = getattr(
        module,
        "RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION",
    )

    assert len(solutions) == 29
    assert len(research_solution.areas) == 7

    assert research_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 203
    assert total_capabilities == 609

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=29")
    print("TOTAL_TECHNOLOGY_AREAS=203")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=609")
    print("RESEARCH_LABS_ASSISTED_DISCOVERY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
