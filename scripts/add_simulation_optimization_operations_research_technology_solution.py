"""Adiciona Simulação, Otimização e Pesquisa Operacional ao registro."""

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
        "simulation_optimization_operations_research_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_DEFINITION = """
_SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "simulation_optimization_operations_research"
    ]
)


SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION = (
    PlatformTechnologySolution(
        solution_id=(
            "simulation_optimization_operations_research"
        ),
        icon="📈",
        title=(
            "Simulação, Otimização e Pesquisa Operacional"
        ),
        description=(
            "Arquitetura tecnológica para formulação de problemas, "
            "modelagem de objetivos e restrições, otimização "
            "matemática, simulação discreta e estocástica, "
            "planejamento, roteirização, alocação de recursos, "
            "análise de cenários, incerteza, execução de "
            "solucionadores, integração decisória, governança "
            "e observabilidade."
        ),
        status=(
            _SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_MODULE
            .status
        ),
        integration_type=(
            _SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="operations_research_problem_modeling",
                title="📐 Formulação e modelagem de problemas",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_problem_formulation"
                        ),
                        title="🧩 Formulação de problemas decisórios",
                        description=(
                            "Representação estruturada de decisões, "
                            "variáveis, recursos, relações, premissas "
                            "e resultados esperados."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_objectives_constraints"
                        ),
                        title="🎯 Objetivos e restrições",
                        description=(
                            "Definição de funções objetivo, limites, "
                            "capacidades, regras, dependências "
                            "e condições obrigatórias."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "technology_governance_policy_compliance",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_scenario_assumptions"
                        ),
                        title="🧭 Cenários, parâmetros e premissas",
                        description=(
                            "Organização de parâmetros, hipóteses, "
                            "condições iniciais, versões e cenários "
                            "alternativos para análise."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "data_traceability_provenance",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mathematical_optimization_solvers",
                title="🧮 Otimização matemática",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "optimization_linear_mixed_integer"
                        ),
                        title="📏 Otimização linear e inteira mista",
                        description=(
                            "Solução de problemas com relações lineares, "
                            "variáveis contínuas, inteiras ou binárias "
                            "e restrições operacionais."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_nonlinear_convex"
                        ),
                        title="📈 Otimização não linear e convexa",
                        description=(
                            "Tratamento de objetivos e restrições "
                            "não lineares, convexidade, gradientes "
                            "e métodos iterativos."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "materials_product_engineering",
                            "research_labs_assisted_discovery",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_multiobjective_robust"
                        ),
                        title="⚖️ Otimização multiobjetivo e robusta",
                        description=(
                            "Avaliação de compromissos entre múltiplos "
                            "objetivos e busca de soluções resistentes "
                            "a variações e incertezas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="simulation_stochastic_systems",
                title="🎲 Simulação e sistemas estocásticos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "simulation_discrete_event"
                        ),
                        title="⏱️ Simulação de eventos discretos",
                        description=(
                            "Representação de filas, recursos, entidades, "
                            "processos, eventos e mudanças de estado "
                            "ao longo do tempo."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "digital_twins_simulation",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "simulation_monte_carlo_stochastic"
                        ),
                        title="🎲 Monte Carlo e simulação estocástica",
                        description=(
                            "Execução repetida de cenários com variáveis "
                            "aleatórias para estimar distribuições, "
                            "probabilidades e riscos."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "simulation_agent_system_dynamics"
                        ),
                        title="🤖 Agentes e dinâmica de sistemas",
                        description=(
                            "Simulação de agentes, interações, estoques, "
                            "fluxos, retroalimentações e comportamentos "
                            "em sistemas complexos."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "robotics_autonomous_systems",
                            "digital_twins_simulation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="planning_scheduling_routing_allocation",
                title="🗓️ Planejamento e alocação de recursos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "optimization_scheduling_sequencing"
                        ),
                        title="🗓️ Programação e sequenciamento",
                        description=(
                            "Organização de tarefas, ordens, máquinas, "
                            "equipes, prazos, precedências e janelas "
                            "de execução."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "enterprise_decision_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_routing_network_flows"
                        ),
                        title="🛣️ Roteirização e fluxos em redes",
                        description=(
                            "Otimização de caminhos, entregas, transporte, "
                            "fluxos, conexões, capacidade e custos "
                            "em redes físicas ou lógicas."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_resource_allocation"
                        ),
                        title="📦 Alocação de recursos e capacidade",
                        description=(
                            "Distribuição de pessoas, equipamentos, "
                            "materiais, orçamento, capacidade computacional "
                            "e outros recursos limitados."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "cloud_devops_finops",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="experimentation_sensitivity_uncertainty",
                title="🧪 Experimentos, sensibilidade e incerteza",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_experiment_design"
                        ),
                        title="🧪 Planejamento de experimentos",
                        description=(
                            "Definição de fatores, níveis, tratamentos, "
                            "repetições e critérios para comparar "
                            "alternativas e resultados."
                        ),
                        technology_dependencies=(
                            "research_labs_assisted_discovery",
                            "scientific_computing_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_sensitivity_analysis"
                        ),
                        title="📊 Análise de sensibilidade",
                        description=(
                            "Avaliação da influência de parâmetros, "
                            "restrições e premissas sobre as soluções "
                            "e os indicadores produzidos."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "tools_analytics",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "operations_research_uncertainty_risk"
                        ),
                        title="⚠️ Incerteza e análise de risco",
                        description=(
                            "Avaliação de distribuições, cenários extremos, "
                            "probabilidades, impactos e limites "
                            "de confiança das decisões."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="solver_runtime_orchestration",
                title="⚙️ Solucionadores e execução computacional",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "optimization_solver_selection_tuning"
                        ),
                        title="🧠 Seleção e ajuste de solucionadores",
                        description=(
                            "Escolha de algoritmos, estratégias, "
                            "tolerâncias, limites de tempo, critérios "
                            "de parada e parâmetros de execução."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "scientific_computing_engineering",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_parallel_execution"
                        ),
                        title="⚡ Execução paralela e distribuída",
                        description=(
                            "Distribuição de cenários, buscas, simulações "
                            "e solucionadores entre workers e recursos "
                            "computacionais disponíveis."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "agent_process_orchestration",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_checkpoint_recovery"
                        ),
                        title="♻️ Checkpoint, retomada e recuperação",
                        description=(
                            "Persistência de estados intermediários, "
                            "retomada após falhas, cancelamento controlado "
                            "e preservação dos resultados válidos."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_integration_governance",
                title="🧭 Decisão, governança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "optimization_decision_recommendations"
                        ),
                        title="💡 Recomendações e alternativas decisórias",
                        description=(
                            "Apresentação de soluções candidatas, "
                            "compromissos, restrições ativas, impactos "
                            "e justificativas para apoio à decisão."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_workflow_integrations"
                        ),
                        title="🔌 Integração com workflows e sistemas",
                        description=(
                            "Disponibilização de cenários e soluções "
                            "para APIs, agentes, gêmeos digitais, "
                            "automações e sistemas empresariais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "agent_process_orchestration",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "optimization_validation_audit_observability"
                        ),
                        title="🧾 Validação, auditoria e observabilidade",
                        description=(
                            "Registro de modelos, parâmetros, versões, "
                            "execuções, qualidade, recursos, custos, "
                            "responsáveis e resultados."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                            "tools_analytics",
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

    module_id = "simulation_optimization_operations_research"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        27: (189, 567),
        28: (196, 588),
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

    print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_PREREQUISITES=OK")


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
    """Adiciona Simulação, Otimização e Pesquisa Operacional."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION =" in source:
        print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_ALREADY_PRESENT=OK")
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
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_simulation_optimization_operations_research_is_complete"

    if test_name in source:
        print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 27
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 28
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e sete soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_simulation_optimization_operations_research_is_complete():
    assert (
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION.solution_id
        == "simulation_optimization_operations_research"
    )

    assert len(
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION.areas
    ) == 7

    assert (
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION
        .capability_count
        == 21
    )


def test_simulation_optimization_operations_research_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "simulation_optimization_operations_research"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION.status
        is module.status
    )

    assert (
        SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_simulation_optimization_operations_research_lookup():
    assert (
        platform_technology_solution(
            "simulation_optimization_operations_research"
        )
        is SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_TESTS_CREATED=OK")


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

    optimization_solution = getattr(
        module,
        ("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_SOLUTION"),
    )

    assert len(solutions) == 28

    assert len(optimization_solution.areas) == 7

    assert optimization_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 196
    assert total_capabilities == 588

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=28")
    print("TOTAL_TECHNOLOGY_AREAS=196")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=588")
    print("SIMULATION_OPTIMIZATION_OPERATIONS_RESEARCH_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
