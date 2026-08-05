"""Adiciona Inteligência Ambiental e de Recursos Naturais."""

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
        "environmental_natural_resources_intelligence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_DEFINITION = """
_ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "environmental_natural_resources_intelligence"
    ]
)


ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id=(
            "environmental_natural_resources_intelligence"
        ),
        icon="🌿",
        title=(
            "Inteligência Ambiental e de Recursos Naturais"
        ),
        description=(
            "Arquitetura tecnológica para integração de sensores, "
            "observação da Terra, inventários ambientais, recursos "
            "hídricos, solos, biodiversidade, qualidade ambiental, "
            "poluição, riscos, uso sustentável dos recursos, "
            "avaliação de impactos, conformidade, alertas, "
            "governança, rastreabilidade e operação ambiental."
        ),
        status=(
            _ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_MODULE
            .status
        ),
        integration_type=(
            _ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="environmental_data_observation",
                title="📡 Dados e observação ambiental",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "environmental_sensor_networks"
                        ),
                        title="🌡️ Redes de sensores ambientais",
                        description=(
                            "Ingestão de medições de ar, água, solo, "
                            "ruído, radiação, umidade, temperatura "
                            "e outras variáveis ambientais."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_earth_observation"
                        ),
                        title="🛰️ Observação da Terra",
                        description=(
                            "Integração de imagens de satélite, drones, "
                            "sensoriamento remoto e produtos derivados "
                            "para análise ambiental e territorial."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "drones_aerial_intelligence",
                            "computer_vision_video_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_external_data_connectors"
                        ),
                        title="🔌 Fontes ambientais externas",
                        description=(
                            "Conectores para bases públicas, serviços, "
                            "inventários, estações, mapas, relatórios "
                            "e fornecedores de dados autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="natural_resources_inventory",
                title="🗺️ Inventários de recursos naturais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "land_cover_ecosystem_inventory"
                        ),
                        title="🌳 Cobertura do solo e ecossistemas",
                        description=(
                            "Mapeamento de vegetação, uso da terra, "
                            "ecossistemas, áreas degradadas, mudanças "
                            "territoriais e unidades ambientais."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                            "computer_vision_video_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "water_soil_resource_inventory"
                        ),
                        title="💧 Recursos hídricos e solos",
                        description=(
                            "Registro e análise de bacias, corpos d'água, "
                            "reservas, aquíferos, solos, propriedades "
                            "e condições dos recursos naturais."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "scientific_computing_engineering",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "biodiversity_habitat_inventory"
                        ),
                        title="🦋 Biodiversidade e habitats",
                        description=(
                            "Organização de espécies, ocorrências, "
                            "habitats, corredores, áreas sensíveis, "
                            "ameaças e evidências de conservação."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "geoai_earth_observation",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="environmental_quality_pollution",
                title="✅ Qualidade ambiental e poluição",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "air_water_soil_quality"
                        ),
                        title="🌍 Qualidade do ar, água e solo",
                        description=(
                            "Monitoramento de indicadores, parâmetros, "
                            "limites, tendências e condições de qualidade "
                            "dos diferentes meios ambientais."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "tools_analytics",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_pollution_detection"
                        ),
                        title="🚨 Detecção de poluição e anomalias",
                        description=(
                            "Identificação de concentrações incomuns, "
                            "descargas, vazamentos, contaminações, "
                            "mudanças abruptas e eventos suspeitos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "ai_bias_quality_monitoring",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_source_dispersion_analysis"
                        ),
                        title="🧭 Fontes e dispersão ambiental",
                        description=(
                            "Análise de possíveis origens, transporte, "
                            "dispersão, alcance territorial e evolução "
                            "de contaminantes ou impactos."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "climate_meteorological_intelligence",
                            "gis_location_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="natural_resources_planning",
                title="📈 Planejamento e uso de recursos naturais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "water_resource_allocation"
                        ),
                        title="💧 Planejamento de recursos hídricos",
                        description=(
                            "Análise de disponibilidade, demanda, "
                            "prioridades, restrições, cenários de escassez "
                            "e alternativas de distribuição da água."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "climate_meteorological_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "land_resource_planning"
                        ),
                        title="🗺️ Planejamento territorial e do solo",
                        description=(
                            "Avaliação de aptidão, conflitos de uso, "
                            "restrições ambientais, capacidade territorial "
                            "e alternativas de ocupação."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "geoai_earth_observation",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ecosystem_services_decision_support"
                        ),
                        title="🌱 Serviços ecossistêmicos",
                        description=(
                            "Análise de benefícios ambientais, proteção, "
                            "regulação, provisão de recursos, impactos "
                            "e compromissos entre alternativas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="environmental_impact_compliance",
                title="⚖️ Impactos e conformidade ambiental",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "environmental_impact_assessment"
                        ),
                        title="📋 Avaliação de impactos ambientais",
                        description=(
                            "Identificação de aspectos, impactos, áreas "
                            "afetadas, severidade, duração, reversibilidade "
                            "e medidas de prevenção ou mitigação."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "scientific_computing_engineering",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_policy_compliance"
                        ),
                        title="⚖️ Políticas e requisitos ambientais",
                        description=(
                            "Organização e verificação de políticas, "
                            "limites, condicionantes, obrigações, prazos "
                            "e critérios de conformidade."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_evidence_reporting"
                        ),
                        title="📄 Evidências e relatórios ambientais",
                        description=(
                            "Produção de indicadores, mapas, relatórios, "
                            "evidências, históricos e registros necessários "
                            "para acompanhamento e auditoria."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "document_ai",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="environmental_alerts_response",
                title="🚨 Alertas e resposta ambiental",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "environmental_threshold_alerting"
                        ),
                        title="🔔 Alertas ambientais",
                        description=(
                            "Geração de alertas por limites, tendências, "
                            "anomalias, localização, persistência "
                            "e níveis de severidade definidos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "business_automation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_incident_workflows"
                        ),
                        title="⚡ Workflows de incidentes ambientais",
                        description=(
                            "Acionamento de equipes, análises, inspeções, "
                            "coletas, notificações e ações controladas "
                            "após a identificação de eventos."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_response_scenarios"
                        ),
                        title="🧪 Cenários de resposta e recuperação",
                        description=(
                            "Simulação de contenção, mitigação, recuperação, "
                            "priorização territorial e utilização "
                            "de recursos em diferentes cenários."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="environmental_governance_operations",
                title="🛡️ Governança e operações ambientais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "environmental_data_quality_provenance"
                        ),
                        title="✅ Qualidade e proveniência dos dados",
                        description=(
                            "Validação de fontes, cobertura, atualidade, "
                            "unidades, consistência, transformações, "
                            "versões e responsáveis pelos dados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_model_validation"
                        ),
                        title="🧠 Validação e explicabilidade dos modelos",
                        description=(
                            "Avaliação de desempenho, incerteza, limitações, "
                            "vieses, diferenças territoriais e justificativas "
                            "dos modelos ambientais."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "environmental_observability_security"
                        ),
                        title="📊 Observabilidade e segurança operacional",
                        description=(
                            "Monitoramento de ingestões, jobs, integrações, "
                            "alertas, erros, recursos, custos, acessos "
                            "e disponibilidade dos serviços ambientais."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "zero_trust_identity_access",
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

    module_id = "environmental_natural_resources_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        32: (224, 672),
        33: (231, 693),
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

    print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_PREREQUISITES=OK")


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
    """Adiciona a solução ambiental ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION =" in source:
        print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_environmental_natural_resources_intelligence_is_complete"

    if test_name in source:
        print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 32
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 33
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e duas soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_environmental_natural_resources_intelligence_is_complete():
    assert (
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION.solution_id
        == "environmental_natural_resources_intelligence"
    )

    assert len(
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION
        .capability_count
        == 21
    )


def test_environmental_natural_resources_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "environmental_natural_resources_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_environmental_natural_resources_intelligence_lookup():
    assert (
        platform_technology_solution(
            "environmental_natural_resources_intelligence"
        )
        is ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_TESTS_CREATED=OK")


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

    environmental_solution = getattr(
        module,
        ("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION"),
    )

    assert len(solutions) == 33

    assert len(environmental_solution.areas) == 7

    assert environmental_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 231
    assert total_capabilities == 693

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=33")
    print("TOTAL_TECHNOLOGY_AREAS=231")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=693")
    print("ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
