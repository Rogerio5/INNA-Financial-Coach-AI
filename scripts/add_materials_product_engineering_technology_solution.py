"""Adiciona Materiais e Engenharia de Produtos ao registro tecnológico."""

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
        "materials_product_engineering_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


MATERIALS_PRODUCT_ENGINEERING_DEFINITION = """
_MATERIALS_PRODUCT_ENGINEERING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "materials_product_engineering"
    ]
)


MATERIALS_PRODUCT_ENGINEERING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="materials_product_engineering",
        icon="🧱",
        title="Materiais e Engenharia de Produtos",
        description=(
            "Arquitetura tecnológica para especificações, dados "
            "de materiais, propriedades, composições, simulação "
            "multiescala, projeto de produtos, otimização, "
            "experimentos, validação, manufatura, qualidade, "
            "rastreabilidade, conformidade, sustentabilidade "
            "e gestão do ciclo de vida de materiais e produtos."
        ),
        status=(
            _MATERIALS_PRODUCT_ENGINEERING_MODULE.status
        ),
        integration_type=(
            _MATERIALS_PRODUCT_ENGINEERING_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="materials_requirements_specifications",
                title="📋 Requisitos e especificações",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_requirements_definition"
                        ),
                        title="🎯 Requisitos de materiais",
                        description=(
                            "Definição de propriedades mecânicas, "
                            "térmicas, químicas, elétricas, ópticas "
                            "e ambientais necessárias ao produto."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                            "quality_process_management",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "product_performance_targets"
                        ),
                        title="📈 Metas de desempenho do produto",
                        description=(
                            "Registro de metas para resistência, peso, "
                            "durabilidade, custo, eficiência, segurança "
                            "e condições de utilização."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_standards_constraints"
                        ),
                        title="⚖️ Normas, limites e restrições",
                        description=(
                            "Organização de normas técnicas, limites "
                            "de composição, requisitos de segurança, "
                            "qualidade e conformidade aplicáveis."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "research_labs_assisted_discovery",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="materials_data_knowledge",
                title="🗂️ Dados e conhecimento de materiais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_properties_catalog"
                        ),
                        title="🧱 Catálogo de propriedades",
                        description=(
                            "Registro de materiais, propriedades, "
                            "composições, fornecedores, condições "
                            "de ensaio, versões e evidências."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_composition_process_relations"
                        ),
                        title="🔗 Composição, processo e propriedades",
                        description=(
                            "Representação das relações entre composição, "
                            "microestrutura, processamento, condições "
                            "e desempenho final dos materiais."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "scientific_computing_engineering",
                            "research_labs_assisted_discovery",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_evidence_retrieval"
                        ),
                        title="🔎 Pesquisa de evidências técnicas",
                        description=(
                            "Recuperação de artigos, relatórios, ensaios, "
                            "especificações, documentos técnicos "
                            "e resultados laboratoriais."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "document_ai",
                            "research_labs_assisted_discovery",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="materials_computational_modeling",
                title="🧮 Modelagem computacional de materiais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_behavior_models"
                        ),
                        title="📐 Modelos de comportamento dos materiais",
                        description=(
                            "Modelagem de deformação, tensão, fadiga, "
                            "fratura, temperatura, corrosão, transporte "
                            "e outras respostas físicas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "digital_twins_simulation",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_microstructure_simulation"
                        ),
                        title="🔬 Microestrutura e propriedades",
                        description=(
                            "Simulação das relações entre fases, grãos, "
                            "poros, defeitos, tratamentos e propriedades "
                            "resultantes do material."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "research_labs_assisted_discovery",
                            "computer_vision_video_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_multiscale_simulation"
                        ),
                        title="🧩 Simulação multiescala",
                        description=(
                            "Integração de modelos em diferentes escalas, "
                            "do comportamento microscópico ao desempenho "
                            "do componente ou produto completo."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "digital_twins_simulation",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="product_design_optimization",
                title="🧭 Projeto e otimização de produtos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "product_design_space_exploration"
                        ),
                        title="🔎 Exploração do espaço de projeto",
                        description=(
                            "Avaliação de combinações de materiais, "
                            "geometrias, dimensões, processos, parâmetros "
                            "e configurações de produto."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "product_multiobjective_optimization"
                        ),
                        title="⚖️ Otimização multiobjetivo",
                        description=(
                            "Busca de alternativas equilibrando desempenho, "
                            "peso, custo, qualidade, durabilidade, risco "
                            "e capacidade produtiva."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "product_generative_design_candidates"
                        ),
                        title="💡 Geração assistida de alternativas",
                        description=(
                            "Produção de candidatos de materiais, "
                            "componentes ou configurações com base "
                            "em objetivos e restrições documentados."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "research_labs_assisted_discovery",
                            "ai_model_agent_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="materials_experiments_validation",
                title="🧪 Experimentos, testes e validação",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_experiment_planning"
                        ),
                        title="📋 Planejamento experimental",
                        description=(
                            "Definição de amostras, fatores, tratamentos, "
                            "repetições, medições, critérios de aceitação "
                            "e condições de ensaio."
                        ),
                        technology_dependencies=(
                            "research_labs_assisted_discovery",
                            "simulation_optimization_operations_research",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_lab_measurement_integration"
                        ),
                        title="🔌 Integração com ensaios e laboratórios",
                        description=(
                            "Integração de instrumentos, sensores, "
                            "arquivos, APIs e sistemas laboratoriais "
                            "para aquisição de resultados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_validation_failure_analysis"
                        ),
                        title="🔎 Validação e análise de falhas",
                        description=(
                            "Comparação de modelos e ensaios, identificação "
                            "de divergências, causas, defeitos, limitações "
                            "e modos de falha."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "model_explainability_interpretability",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="materials_manufacturing_quality",
                title="🏭 Manufatura, processo e qualidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_process_parameter_optimization"
                        ),
                        title="⚙️ Parâmetros de processamento",
                        description=(
                            "Otimização de temperatura, pressão, velocidade, "
                            "tempo, composição, tratamento e demais "
                            "parâmetros do processo produtivo."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "simulation_optimization_operations_research",
                            "iot_edge_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_quality_defect_analysis"
                        ),
                        title="✅ Qualidade e análise de defeitos",
                        description=(
                            "Detecção e classificação de defeitos, "
                            "variações, não conformidades e tendências "
                            "de qualidade em materiais e produtos."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "ai_bias_quality_monitoring",
                            "quality_process_management",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_traceability_change_control"
                        ),
                        title="🧾 Rastreabilidade e controle de mudanças",
                        description=(
                            "Registro de lotes, fornecedores, composições, "
                            "processos, ensaios, alterações, aprovações "
                            "e versões dos produtos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "software_supply_chain_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="materials_lifecycle_governance_operations",
                title="🛡️ Ciclo de vida, governança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "materials_risk_compliance_management"
                        ),
                        title="⚠️ Riscos e conformidade dos materiais",
                        description=(
                            "Avaliação de riscos técnicos, operacionais, "
                            "regulatórios, ambientais, de fornecedores "
                            "e de segurança dos produtos."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_lifecycle_resource_impact"
                        ),
                        title="♻️ Ciclo de vida e uso de recursos",
                        description=(
                            "Avaliação de consumo, durabilidade, manutenção, "
                            "reutilização, descarte, eficiência de materiais "
                            "e impactos ao longo do ciclo de vida."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "tools_analytics",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "materials_observability_governance"
                        ),
                        title="📊 Observabilidade e governança",
                        description=(
                            "Monitoramento de dados, modelos, experimentos, "
                            "jobs, recursos, custos, versões, qualidade, "
                            "acessos e resultados da engenharia."
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

    module_id = "materials_product_engineering"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        29: (203, 609),
        30: (210, 630),
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

    print("MATERIALS_PRODUCT_ENGINEERING_PREREQUISITES=OK")


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
    """Adiciona Materiais e Engenharia de Produtos."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "MATERIALS_PRODUCT_ENGINEERING_SOLUTION =" in source:
        print("MATERIALS_PRODUCT_ENGINEERING_ALREADY_PRESENT=OK")
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
        MATERIALS_PRODUCT_ENGINEERING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    RESEARCH_LABS_ASSISTED_DISCOVERY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    MATERIALS_PRODUCT_ENGINEERING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("MATERIALS_PRODUCT_ENGINEERING_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_materials_product_engineering_is_complete"

    if test_name in source:
        print("MATERIALS_PRODUCT_ENGINEERING_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "MATERIALS_PRODUCT_ENGINEERING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 29
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 30
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e nove soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_materials_product_engineering_is_complete():
    assert (
        MATERIALS_PRODUCT_ENGINEERING_SOLUTION.solution_id
        == "materials_product_engineering"
    )

    assert len(
        MATERIALS_PRODUCT_ENGINEERING_SOLUTION.areas
    ) == 7

    assert (
        MATERIALS_PRODUCT_ENGINEERING_SOLUTION.capability_count
        == 21
    )


def test_materials_product_engineering_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "materials_product_engineering"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        MATERIALS_PRODUCT_ENGINEERING_SOLUTION.status
        is module.status
    )

    assert (
        MATERIALS_PRODUCT_ENGINEERING_SOLUTION.integration_type
        == module.integration_type
    )


def test_materials_product_engineering_lookup():
    assert (
        platform_technology_solution(
            "materials_product_engineering"
        )
        is MATERIALS_PRODUCT_ENGINEERING_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("MATERIALS_PRODUCT_ENGINEERING_TESTS_CREATED=OK")


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

    materials_solution = getattr(
        module,
        "MATERIALS_PRODUCT_ENGINEERING_SOLUTION",
    )

    assert len(solutions) == 30
    assert len(materials_solution.areas) == 7

    assert materials_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 210
    assert total_capabilities == 630

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=30")
    print("TOTAL_TECHNOLOGY_AREAS=210")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=630")
    print("MATERIALS_PRODUCT_ENGINEERING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
