"""Adiciona Cidades Inteligentes e Infraestrutura Urbana ao registro."""

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
        "smart_cities_urban_infrastructure_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


SMART_CITIES_URBAN_INFRASTRUCTURE_DEFINITION = """
_SMART_CITIES_URBAN_INFRASTRUCTURE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "smart_cities_urban_infrastructure"
    ]
)


SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="smart_cities_urban_infrastructure",
        icon="🏙️",
        title="Cidades Inteligentes e Infraestrutura Urbana",
        description=(
            "Arquitetura tecnológica para cadastro territorial, "
            "ativos urbanos, sensores conectados, mobilidade, "
            "energia, iluminação, água, resíduos, infraestrutura "
            "digital, serviços públicos, participação cidadã, "
            "planejamento urbano, emergências, sustentabilidade, "
            "governança, segurança e observabilidade municipal."
        ),
        status=(
            _SMART_CITIES_URBAN_INFRASTRUCTURE_MODULE.status
        ),
        integration_type=(
            _SMART_CITIES_URBAN_INFRASTRUCTURE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="urban_assets_digital_registry",
                title="🗺️ Território e ativos urbanos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_geospatial_asset_registry"
                        ),
                        title="📍 Cadastro territorial e de ativos",
                        description=(
                            "Registro de vias, bairros, imóveis, postes, "
                            "redes, equipamentos, áreas públicas, "
                            "serviços, localização e responsáveis."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "data_platform_governance",
                            "construction_bim_digital_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_infrastructure_relationship_model"
                        ),
                        title="🔗 Relações da infraestrutura urbana",
                        description=(
                            "Representação das conexões, dependências, "
                            "hierarquias, áreas atendidas e impactos "
                            "entre os diferentes ativos e serviços."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "digital_twins_simulation",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_digital_twin_models"
                        ),
                        title="🏙️ Gêmeos digitais urbanos",
                        description=(
                            "Representação integrada de territórios, "
                            "edificações, redes, equipamentos, serviços "
                            "e estados operacionais da cidade."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "construction_bim_digital_engineering",
                            "spatial_computing_augmented_reality",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_iot_connectivity_operations",
                title="📡 IoT, conectividade e operação urbana",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_sensor_network_ingestion"
                        ),
                        title="📨 Sensores e dispositivos urbanos",
                        description=(
                            "Ingestão de dados de iluminação, tráfego, "
                            "ambiente, água, energia, segurança, "
                            "equipamentos e infraestrutura pública."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_edge_event_processing"
                        ),
                        title="⚡ Processamento de eventos em edge",
                        description=(
                            "Filtragem, agregação, detecção de condições "
                            "e execução controlada de ações próximas "
                            "aos equipamentos urbanos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_connected_infrastructure_monitoring"
                        ),
                        title="🌐 Monitoramento da infraestrutura conectada",
                        description=(
                            "Acompanhamento de conectividade, disponibilidade, "
                            "latência, falhas, energia, versões e saúde "
                            "dos dispositivos e gateways."
                        ),
                        technology_dependencies=(
                            "networks_telecommunications_connectivity",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_mobility_public_space",
                title="🚦 Mobilidade e espaços públicos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_integrated_mobility_operations"
                        ),
                        title="🚦 Operação integrada da mobilidade",
                        description=(
                            "Integração de tráfego, transporte público, "
                            "frotas, rotas, semáforos, ocorrências "
                            "e indicadores de mobilidade."
                        ),
                        technology_dependencies=(
                            "mobility_traffic_transport",
                            "navigation_positioning_geolocation",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_public_space_monitoring"
                        ),
                        title="🏞️ Monitoramento de espaços públicos",
                        description=(
                            "Acompanhamento de ocupação, conservação, "
                            "acessibilidade, iluminação, equipamentos "
                            "e condições dos espaços urbanos."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "gis_location_intelligence",
                            "iot_edge_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_accessibility_route_planning"
                        ),
                        title="♿ Acessibilidade e rotas inclusivas",
                        description=(
                            "Análise de calçadas, travessias, transporte, "
                            "barreiras, equipamentos e alternativas "
                            "de deslocamento acessível."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "mobility_traffic_transport",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_utilities_environment_services",
                title="⚡ Serviços urbanos e meio ambiente",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_energy_lighting_management"
                        ),
                        title="💡 Energia e iluminação pública",
                        description=(
                            "Monitoramento e otimização de consumo, "
                            "iluminação, falhas, horários, intensidade "
                            "e eficiência dos ativos energéticos."
                        ),
                        technology_dependencies=(
                            "energy_smart_grids",
                            "iot_edge_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_water_waste_operations"
                        ),
                        title="💧 Água, drenagem e resíduos",
                        description=(
                            "Acompanhamento de abastecimento, drenagem, "
                            "vazamentos, coleta, contêineres, rotas, "
                            "volume e condições dos serviços."
                        ),
                        technology_dependencies=(
                            "environmental_natural_resources_intelligence",
                            "iot_edge_intelligence",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_environmental_quality_monitoring"
                        ),
                        title="🌿 Qualidade ambiental urbana",
                        description=(
                            "Monitoramento de ar, ruído, temperatura, "
                            "ilhas de calor, áreas verdes, água, "
                            "solo e condições ambientais."
                        ),
                        technology_dependencies=(
                            "environmental_natural_resources_intelligence",
                            "climate_meteorological_intelligence",
                            "geoai_earth_observation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_public_services_citizen_experience",
                title="👥 Serviços públicos e experiência cidadã",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_service_request_management"
                        ),
                        title="📋 Solicitações e serviços municipais",
                        description=(
                            "Recebimento, classificação, encaminhamento, "
                            "priorização e acompanhamento de solicitações "
                            "relacionadas aos serviços urbanos."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_multichannel_citizen_assistance"
                        ),
                        title="💬 Atendimento cidadão multicanal",
                        description=(
                            "Disponibilização de informações, orientações, "
                            "protocolos e atualizações por interfaces "
                            "digitais e canais autorizados."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "multimodal_ai",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_participation_feedback_analysis"
                        ),
                        title="🗣️ Participação e análise de feedback",
                        description=(
                            "Organização de consultas, sugestões, avaliações, "
                            "percepções e indicadores de satisfação "
                            "sobre políticas e serviços urbanos."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "responsible_ai_ethics_risk",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_planning_resilience_emergency",
                title="🧭 Planejamento, resiliência e emergências",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_growth_scenario_simulation"
                        ),
                        title="🏗️ Simulação do desenvolvimento urbano",
                        description=(
                            "Avaliação de expansão, densidade, infraestrutura, "
                            "uso do solo, mobilidade, demanda de serviços "
                            "e cenários de planejamento."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "construction_bim_digital_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_climate_resilience_analysis"
                        ),
                        title="🌦️ Resiliência climática urbana",
                        description=(
                            "Análise de enchentes, calor, tempestades, "
                            "secas, exposição de ativos, vulnerabilidades "
                            "e medidas de adaptação."
                        ),
                        technology_dependencies=(
                            "climate_meteorological_intelligence",
                            "environmental_natural_resources_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_emergency_coordination"
                        ),
                        title="🚨 Coordenação de emergências urbanas",
                        description=(
                            "Integração de alertas, mapas, equipes, "
                            "infraestrutura, rotas, abrigos, recursos "
                            "e comunicação durante incidentes."
                        ),
                        technology_dependencies=(
                            "emergency_disaster_management",
                            "mobility_traffic_transport",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="urban_governance_security_observability",
                title="🛡️ Governança, segurança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "urban_data_governance_interoperability"
                        ),
                        title="🗂️ Governança e interoperabilidade",
                        description=(
                            "Padronização de dados, catálogos, contratos, "
                            "APIs, responsabilidades, qualidade, retenção "
                            "e integração entre áreas municipais."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "api_integrations_connectors",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_privacy_cybersecurity_access"
                        ),
                        title="🔐 Privacidade e segurança urbana",
                        description=(
                            "Proteção de dados pessoais, dispositivos, "
                            "comandos, sistemas, integrações, operadores "
                            "e serviços críticos da cidade."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "urban_operations_observability_audit"
                        ),
                        title="📊 Observabilidade e auditoria urbana",
                        description=(
                            "Monitoramento de ativos, sensores, integrações, "
                            "serviços, eventos, qualidade, custos, acessos, "
                            "alterações e disponibilidade operacional."
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

    module_id = "smart_cities_urban_infrastructure"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        37: (259, 777),
        38: (266, 798),
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

    print("SMART_CITIES_URBAN_INFRASTRUCTURE_PREREQUISITES=OK")


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
    """Adiciona Cidades Inteligentes e Infraestrutura Urbana."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION =" in source:
        print("SMART_CITIES_URBAN_INFRASTRUCTURE_ALREADY_PRESENT=OK")
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
        SMART_CITIES_URBAN_INFRASTRUCTURE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    MOBILITY_TRAFFIC_TRANSPORT_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_smart_cities_urban_infrastructure_is_complete"

    if test_name in source:
        print("SMART_CITIES_URBAN_INFRASTRUCTURE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 37
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 38
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e sete soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_smart_cities_urban_infrastructure_is_complete():
    assert (
        SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION.solution_id
        == "smart_cities_urban_infrastructure"
    )

    assert len(
        SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION.areas
    ) == 7

    assert (
        SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION
        .capability_count
        == 21
    )


def test_smart_cities_urban_infrastructure_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "smart_cities_urban_infrastructure"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION.status
        is module.status
    )

    assert (
        SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_smart_cities_urban_infrastructure_lookup():
    assert (
        platform_technology_solution(
            "smart_cities_urban_infrastructure"
        )
        is SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SMART_CITIES_URBAN_INFRASTRUCTURE_TESTS_CREATED=OK")


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

    smart_city_solution = getattr(
        module,
        "SMART_CITIES_URBAN_INFRASTRUCTURE_SOLUTION",
    )

    assert len(solutions) == 38
    assert len(smart_city_solution.areas) == 7

    assert smart_city_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 266
    assert total_capabilities == 798

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=38")
    print("TOTAL_TECHNOLOGY_AREAS=266")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=798")
    print("SMART_CITIES_URBAN_INFRASTRUCTURE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
