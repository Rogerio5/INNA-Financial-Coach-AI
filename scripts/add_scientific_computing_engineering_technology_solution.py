"""Adiciona Computação Científica e Engenharia ao registro tecnológico."""

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
        "scientific_computing_engineering_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


SCIENTIFIC_COMPUTING_ENGINEERING_DEFINITION = """
_SCIENTIFIC_COMPUTING_ENGINEERING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "scientific_computing_engineering"
    ]
)


SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="scientific_computing_engineering",
        icon="🧮",
        title="Computação Científica e Engenharia",
        description=(
            "Arquitetura tecnológica para modelagem matemática, "
            "métodos numéricos, álgebra linear, equações "
            "diferenciais, otimização, simulação, processamento "
            "paralelo, aceleração computacional, análise de "
            "incerteza, visualização científica, reprodutibilidade, "
            "governança e operação de workloads científicos."
        ),
        status=(
            _SCIENTIFIC_COMPUTING_ENGINEERING_MODULE.status
        ),
        integration_type=(
            _SCIENTIFIC_COMPUTING_ENGINEERING_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="scientific_numerical_modeling",
                title="📐 Modelagem e métodos numéricos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_mathematical_modeling"
                        ),
                        title="📐 Modelagem matemática",
                        description=(
                            "Representação de fenômenos, sistemas, "
                            "processos e restrições por equações, "
                            "variáveis, parâmetros e relações."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_linear_algebra_solvers"
                        ),
                        title="🧮 Álgebra linear e solucionadores",
                        description=(
                            "Operações matriciais, decomposições, "
                            "sistemas lineares, autovalores e métodos "
                            "iterativos para problemas científicos."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_differential_equations"
                        ),
                        title="📈 Equações diferenciais e sistemas dinâmicos",
                        description=(
                            "Solução numérica de modelos contínuos, "
                            "dinâmicos, temporais e espaciais utilizados "
                            "em engenharia e pesquisa."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "research_labs_assisted_discovery",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_data_precision_uncertainty",
                title="🧪 Dados científicos, precisão e incerteza",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_multidimensional_arrays"
                        ),
                        title="🧊 Arrays e dados multidimensionais",
                        description=(
                            "Processamento de vetores, matrizes, tensores, "
                            "grades, séries temporais e dados científicos "
                            "de múltiplas dimensões."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_units_precision_management"
                        ),
                        title="📏 Unidades, precisão e estabilidade",
                        description=(
                            "Gestão de unidades físicas, escalas, "
                            "arredondamento, precisão numérica, tolerâncias "
                            "e estabilidade dos cálculos."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                            "materials_product_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_uncertainty_propagation"
                        ),
                        title="🎲 Propagação de incertezas",
                        description=(
                            "Avaliação de como erros, distribuições "
                            "e incertezas das entradas influenciam "
                            "os resultados dos modelos."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "tools_analytics",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_estimation_optimization",
                title="🎯 Estimação e otimização",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_parameter_estimation"
                        ),
                        title="🎯 Estimação de parâmetros",
                        description=(
                            "Ajuste de parâmetros de modelos utilizando "
                            "medições, experimentos, funções de erro "
                            "e restrições conhecidas."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "research_labs_assisted_discovery",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_inverse_problems"
                        ),
                        title="🔎 Problemas inversos",
                        description=(
                            "Inferência de causas, parâmetros ou condições "
                            "internas a partir de medições e resultados "
                            "observados."
                        ),
                        technology_dependencies=(
                            "research_labs_assisted_discovery",
                            "model_explainability_interpretability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_constrained_optimization"
                        ),
                        title="📈 Otimização com restrições",
                        description=(
                            "Busca de soluções que melhorem objetivos "
                            "respeitando limites físicos, operacionais, "
                            "financeiros e técnicos."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_high_performance_computing",
                title="⚡ Computação de alto desempenho",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_parallel_distributed_computing"
                        ),
                        title="🧩 Processamento paralelo e distribuído",
                        description=(
                            "Divisão de cálculos e simulações entre "
                            "processos, máquinas ou workers para reduzir "
                            "o tempo de execução."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "agent_process_orchestration",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_gpu_acceleration"
                        ),
                        title="⚡ Aceleração por GPU e hardware",
                        description=(
                            "Utilização controlada de aceleradores para "
                            "operações matriciais, simulações, otimização "
                            "e processamento intensivo."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "ai_operations",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_compute_job_orchestration"
                        ),
                        title="⚙️ Orquestração de jobs científicos",
                        description=(
                            "Agendamento, distribuição, priorização, "
                            "retentativas e acompanhamento de workloads "
                            "científicos de longa duração."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "cloud_devops_finops",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_engineering_simulation",
                title="🏗️ Simulação aplicada à engenharia",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_structural_thermal_fluid_models"
                        ),
                        title="🏗️ Modelos estruturais, térmicos e de fluidos",
                        description=(
                            "Modelagem e análise de esforços, deformações, "
                            "temperatura, transferência de calor, escoamentos "
                            "e condições físicas."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "materials_product_engineering",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_signal_system_analysis"
                        ),
                        title="📡 Sinais, sistemas e controle",
                        description=(
                            "Análise de sinais, frequências, filtros, "
                            "respostas dinâmicas e comportamento "
                            "de sistemas controlados."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "robotics_autonomous_systems",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_geospatial_physical_models"
                        ),
                        title="🌍 Modelos físicos e geoespaciais",
                        description=(
                            "Simulação de fenômenos distribuídos no espaço, "
                            "território, superfície, ambiente ou infraestrutura."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_validation_visualization",
                title="📊 Validação e visualização científica",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_verification_validation"
                        ),
                        title="✅ Verificação e validação dos modelos",
                        description=(
                            "Comparação com referências, experimentos, "
                            "soluções conhecidas e critérios de aceitação "
                            "para confirmar o comportamento dos modelos."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "research_labs_assisted_discovery",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_visualization_reporting"
                        ),
                        title="📊 Visualização e relatórios científicos",
                        description=(
                            "Produção de gráficos, mapas, superfícies, "
                            "animações, relatórios e representações "
                            "dos resultados calculados."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "digital_experiences_intelligent_interfaces",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_reproducible_notebooks"
                        ),
                        title="📓 Notebooks e experimentos reproduzíveis",
                        description=(
                            "Organização de código, parâmetros, dados, "
                            "resultados e explicações para repetição "
                            "e revisão dos experimentos."
                        ),
                        technology_dependencies=(
                            "research_labs_assisted_discovery",
                            "data_traceability_provenance",
                            "software_supply_chain_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="scientific_governance_operations",
                title="🛡️ Governança e operações científicas",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "scientific_environment_dependency_management"
                        ),
                        title="📦 Ambientes e dependências científicas",
                        description=(
                            "Controle de bibliotecas, compiladores, "
                            "versões, containers, configurações "
                            "e ambientes utilizados nos cálculos."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_performance_cost_observability"
                        ),
                        title="📈 Desempenho, recursos e custos",
                        description=(
                            "Monitoramento de duração, memória, CPU, GPU, "
                            "armazenamento, filas, falhas e custos "
                            "dos workloads científicos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "scientific_provenance_audit_lifecycle"
                        ),
                        title="🧾 Proveniência, auditoria e ciclo de vida",
                        description=(
                            "Registro de dados, código, parâmetros, "
                            "ambientes, execuções, responsáveis, versões "
                            "e resultados produzidos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "data_platform_governance",
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

    module_id = "scientific_computing_engineering"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        26: (182, 546),
        27: (189, 567),
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

    print("SCIENTIFIC_COMPUTING_ENGINEERING_PREREQUISITES=OK")


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
    """Adiciona Computação Científica e Engenharia."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION =" in source:
        print("SCIENTIFIC_COMPUTING_ENGINEERING_ALREADY_PRESENT=OK")
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
        SCIENTIFIC_COMPUTING_ENGINEERING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_scientific_computing_engineering_is_complete"

    if test_name in source:
        print("SCIENTIFIC_COMPUTING_ENGINEERING_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 26
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 27
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e seis soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_scientific_computing_engineering_is_complete():
    assert (
        SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION.solution_id
        == "scientific_computing_engineering"
    )

    assert len(
        SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION.areas
    ) == 7

    assert (
        SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION.capability_count
        == 21
    )


def test_scientific_computing_engineering_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "scientific_computing_engineering"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION.status
        is module.status
    )

    assert (
        SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION.integration_type
        == module.integration_type
    )


def test_scientific_computing_engineering_lookup():
    assert (
        platform_technology_solution(
            "scientific_computing_engineering"
        )
        is SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SCIENTIFIC_COMPUTING_ENGINEERING_TESTS_CREATED=OK")


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

    scientific_solution = getattr(
        module,
        "SCIENTIFIC_COMPUTING_ENGINEERING_SOLUTION",
    )

    assert len(solutions) == 27
    assert len(scientific_solution.areas) == 7

    assert scientific_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 189
    assert total_capabilities == 567

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=27")
    print("TOTAL_TECHNOLOGY_AREAS=189")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=567")
    print("SCIENTIFIC_COMPUTING_ENGINEERING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
