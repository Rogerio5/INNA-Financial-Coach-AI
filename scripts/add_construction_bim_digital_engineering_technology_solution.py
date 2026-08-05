"""Adiciona Construção, BIM e Engenharia Digital ao registro."""

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
        "construction_bim_digital_engineering_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


CONSTRUCTION_BIM_DIGITAL_ENGINEERING_DEFINITION = """
_CONSTRUCTION_BIM_DIGITAL_ENGINEERING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "construction_bim_digital_engineering"
    ]
)


CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="construction_bim_digital_engineering",
        icon="🏗️",
        title="Construção, BIM e Engenharia Digital",
        description=(
            "Arquitetura tecnológica para modelos BIM, dados "
            "de engenharia, coordenação multidisciplinar, detecção "
            "de interferências, planejamento 4D, estimativas 5D, "
            "monitoramento de obras, gêmeos digitais, realidade "
            "aumentada, segurança, sustentabilidade, conformidade, "
            "rastreabilidade e operação do ciclo de vida dos ativos."
        ),
        status=(
            _CONSTRUCTION_BIM_DIGITAL_ENGINEERING_MODULE.status
        ),
        integration_type=(
            _CONSTRUCTION_BIM_DIGITAL_ENGINEERING_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="bim_models_information_structures",
                title="🏗️ Modelos BIM e estruturas de informação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="bim_model_asset_registry",
                        title="🗂️ Modelos, ativos e componentes",
                        description=(
                            "Registro de edifícios, estruturas, sistemas, "
                            "ambientes, componentes, equipamentos, "
                            "materiais, versões e responsáveis."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "data_platform_governance",
                            "materials_product_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_semantic_object_model",
                        title="🔗 Objetos e relações semânticas",
                        description=(
                            "Representação das relações entre espaços, "
                            "componentes, disciplinas, propriedades, "
                            "dependências e sistemas construtivos."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_geospatial_alignment",
                        title="📍 Georreferenciamento e contexto territorial",
                        description=(
                            "Alinhamento dos modelos com coordenadas, "
                            "terreno, entorno, infraestrutura, mapas "
                            "e demais referências geoespaciais."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "geoai_earth_observation",
                            "spatial_computing_augmented_reality",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="bim_common_data_environment",
                title="📂 Ambiente comum de dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="bim_document_model_management",
                        title="📄 Documentos e modelos de engenharia",
                        description=(
                            "Gestão de plantas, modelos, memoriais, "
                            "especificações, relatórios, contratos, "
                            "imagens e demais documentos técnicos."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "data_platform_governance",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_version_change_control",
                        title="🔄 Versionamento e controle de mudanças",
                        description=(
                            "Registro de revisões, comparações, aprovações, "
                            "autores, motivos, impactos e histórico "
                            "das alterações realizadas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "software_supply_chain_security",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_collaborative_data_exchange",
                        title="🤝 Colaboração e intercâmbio de dados",
                        description=(
                            "Compartilhamento controlado de modelos, "
                            "documentos, comentários, pendências "
                            "e informações entre equipes e sistemas."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="bim_coordination_engineering_analysis",
                title="🧩 Coordenação e análise de engenharia",
                capabilities=(
                    TechnologyCapability(
                        capability_id="bim_multidisciplinary_coordination",
                        title="🤝 Coordenação multidisciplinar",
                        description=(
                            "Integração de arquitetura, estrutura, "
                            "instalações, infraestrutura, equipamentos "
                            "e demais disciplinas do empreendimento."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "agent_process_orchestration",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_clash_rule_detection",
                        title="🚧 Interferências e validação de regras",
                        description=(
                            "Detecção de conflitos geométricos, espaços "
                            "insuficientes, incompatibilidades, violações "
                            "de regras e problemas de construtibilidade."
                        ),
                        technology_dependencies=(
                            "spatial_computing_augmented_reality",
                            "software_testing_quality_reliability",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_engineering_simulation",
                        title="🧮 Simulação e desempenho de engenharia",
                        description=(
                            "Avaliação estrutural, térmica, energética, "
                            "ambiental, operacional e de desempenho "
                            "dos sistemas representados."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "digital_twins_simulation",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="bim_planning_cost_resources",
                title="📅 Planejamento 4D, custos 5D e recursos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="bim_4d_schedule_simulation",
                        title="📅 Planejamento e simulação 4D",
                        description=(
                            "Associação dos elementos do modelo às etapas, "
                            "sequências, prazos, dependências e cenários "
                            "de execução da construção."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_5d_cost_estimation",
                        title="💰 Quantitativos e estimativas 5D",
                        description=(
                            "Extração de quantidades, composição de custos, "
                            "comparação de alternativas e acompanhamento "
                            "de estimativas e orçamento."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                            "materials_product_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_resources_logistics_optimization",
                        title="🚚 Recursos e logística da obra",
                        description=(
                            "Planejamento de equipes, equipamentos, "
                            "materiais, áreas de armazenamento, acessos, "
                            "movimentações e utilização de recursos."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "gis_location_intelligence",
                            "robotics_autonomous_systems",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="construction_site_intelligence",
                title="📡 Obra conectada e inteligência de campo",
                capabilities=(
                    TechnologyCapability(
                        capability_id="construction_progress_capture",
                        title="📷 Captura e acompanhamento do progresso",
                        description=(
                            "Uso de imagens, vídeos, drones, sensores "
                            "e registros de campo para acompanhar "
                            "o avanço físico do empreendimento."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "drones_aerial_intelligence",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="construction_model_reality_comparison",
                        title="🔎 Comparação entre modelo e realidade",
                        description=(
                            "Comparação de elementos planejados e executados "
                            "para identificar desvios, pendências, atrasos "
                            "e diferenças geométricas."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "spatial_computing_augmented_reality",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="construction_iot_event_monitoring",
                        title="📡 Sensores e eventos da construção",
                        description=(
                            "Monitoramento de equipamentos, ambiente, "
                            "estruturas, energia, acesso, localização "
                            "e eventos operacionais da obra."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="bim_safety_sustainability_compliance",
                title="🛡️ Segurança, sustentabilidade e conformidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="construction_safety_risk_analysis",
                        title="⚠️ Segurança e análise de riscos",
                        description=(
                            "Identificação de zonas perigosas, conflitos "
                            "operacionais, riscos de execução, acessos "
                            "e condições que exigem controles adicionais."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "real_time_event_intelligence",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_environmental_energy_analysis",
                        title="🌱 Desempenho ambiental e energético",
                        description=(
                            "Avaliação de energia, materiais, resíduos, "
                            "água, emissões, conforto e demais indicadores "
                            "ambientais do empreendimento."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "materials_product_engineering",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_codes_policy_compliance",
                        title="⚖️ Normas e conformidade técnica",
                        description=(
                            "Verificação de requisitos, normas, políticas, "
                            "documentos obrigatórios, aprovações "
                            "e evidências associadas ao projeto."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "document_ai",
                            "enterprise_rag",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="bim_asset_lifecycle_operations",
                title="🏢 Ciclo de vida e operação dos ativos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="bim_handover_asset_information",
                        title="📦 Entrega digital e informações dos ativos",
                        description=(
                            "Organização de modelos finais, documentos, "
                            "manuais, garantias, especificações, históricos "
                            "e dados necessários à operação."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "document_ai",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_facility_digital_twin",
                        title="🏭 Gêmeo digital para operação e manutenção",
                        description=(
                            "Conexão dos modelos aos ativos, sensores, "
                            "ordens, inspeções, falhas, intervenções "
                            "e condições operacionais reais."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "iot_edge_intelligence",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="bim_observability_governance",
                        title="📊 Observabilidade, auditoria e governança",
                        description=(
                            "Monitoramento de modelos, integrações, eventos, "
                            "qualidade, alterações, acessos, recursos, "
                            "custos e ciclo de vida da solução."
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

    module_id = "construction_bim_digital_engineering"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        30: (210, 630),
        31: (217, 651),
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

    print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_PREREQUISITES=OK")


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
    """Adiciona Construção, BIM e Engenharia Digital."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION =" in source:
        print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_ALREADY_PRESENT=OK")
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
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    MATERIALS_PRODUCT_ENGINEERING_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_construction_bim_digital_engineering_is_complete"

    if test_name in source:
        print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 30
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 31
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_construction_bim_digital_engineering_is_complete():
    assert (
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION.solution_id
        == "construction_bim_digital_engineering"
    )

    assert len(
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION.areas
    ) == 7

    assert (
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION
        .capability_count
        == 21
    )


def test_construction_bim_digital_engineering_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "construction_bim_digital_engineering"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION.status
        is module.status
    )

    assert (
        CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_construction_bim_digital_engineering_lookup():
    assert (
        platform_technology_solution(
            "construction_bim_digital_engineering"
        )
        is CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_TESTS_CREATED=OK")


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

    construction_solution = getattr(
        module,
        "CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION",
    )

    assert len(solutions) == 31

    assert len(construction_solution.areas) == 7

    assert construction_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 217
    assert total_capabilities == 651

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=31")
    print("TOTAL_TECHNOLOGY_AREAS=217")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=651")
    print("CONSTRUCTION_BIM_DIGITAL_ENGINEERING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
