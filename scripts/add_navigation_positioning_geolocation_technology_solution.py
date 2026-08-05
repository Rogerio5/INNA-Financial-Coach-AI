"""Adiciona Navegação, Posicionamento e Geolocalização ao registro."""

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
        "navigation_positioning_geolocation_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


NAVIGATION_POSITIONING_GEOLOCATION_DEFINITION = """
_NAVIGATION_POSITIONING_GEOLOCATION_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "navigation_positioning_geolocation"
    ]
)


NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="navigation_positioning_geolocation",
        icon="🧭",
        title="Navegação, Posicionamento e Geolocalização",
        description=(
            "Arquitetura tecnológica para fontes de posicionamento, "
            "GNSS, redes, sensores, fusão de sinais, localização "
            "interna e externa, mapas, rotas, rastreamento em tempo "
            "real, geofencing, serviços de localização, APIs, "
            "privacidade, segurança, qualidade, governança "
            "e observabilidade operacional."
        ),
        status=(
            _NAVIGATION_POSITIONING_GEOLOCATION_MODULE.status
        ),
        integration_type=(
            _NAVIGATION_POSITIONING_GEOLOCATION_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="navigation_positioning_sources",
                title="📡 Fontes e sinais de posicionamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_gnss_positioning",
                        title="🛰️ Posicionamento por GNSS",
                        description=(
                            "Integração de coordenadas, altitude, precisão, "
                            "tempo, velocidade e qualidade fornecidos "
                            "por sistemas globais de navegação."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_network_positioning",
                        title="📶 Posicionamento por redes",
                        description=(
                            "Estimativa de localização utilizando redes "
                            "móveis, Wi-Fi, beacons, gateways e outras "
                            "fontes de conectividade disponíveis."
                        ),
                        technology_dependencies=(
                            "networks_telecommunications_connectivity",
                            "iot_edge_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_inertial_sensor_inputs",
                        title="📱 Sensores inerciais e movimento",
                        description=(
                            "Utilização de aceleração, orientação, rotação, "
                            "passos, velocidade e movimento para apoiar "
                            "a continuidade do posicionamento."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "scientific_computing_engineering",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_location_fusion_accuracy",
                title="🎯 Fusão, precisão e qualidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_multisource_fusion",
                        title="🧩 Fusão de múltiplas fontes",
                        description=(
                            "Combinação de GNSS, redes, sensores, mapas "
                            "e referências espaciais para produzir "
                            "estimativas de localização mais consistentes."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_accuracy_confidence",
                        title="📏 Precisão e nível de confiança",
                        description=(
                            "Cálculo e exposição de erro estimado, "
                            "incerteza, cobertura, qualidade do sinal "
                            "e confiança da posição calculada."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "model_explainability_interpretability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_outlier_spoof_detection",
                        title="🚨 Anomalias e falsificação de localização",
                        description=(
                            "Identificação de saltos, velocidades impossíveis, "
                            "sinais inconsistentes, interferências "
                            "e possíveis tentativas de falsificação."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "real_time_event_intelligence",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_maps_routes_guidance",
                title="🗺️ Mapas, rotas e orientação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_map_matching",
                        title="📍 Correspondência com mapas",
                        description=(
                            "Associação da posição observada a vias, "
                            "corredores, áreas, trilhas, edifícios "
                            "e demais elementos geográficos conhecidos."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "knowledge_graph_semantic_ai",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_route_calculation",
                        title="🛣️ Cálculo de rotas",
                        description=(
                            "Geração de trajetos considerando distância, "
                            "tempo, trânsito, restrições, acessibilidade, "
                            "prioridades e condições da rede."
                        ),
                        technology_dependencies=(
                            "mobility_traffic_transport",
                            "simulation_optimization_operations_research",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_turn_guidance",
                        title="🧭 Orientação contextual de percurso",
                        description=(
                            "Produção de instruções de deslocamento conforme "
                            "posição, direção, velocidade, rota, ambiente "
                            "e alterações identificadas durante a jornada."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "voice_audio_speech_ai",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_tracking_geofencing_events",
                title="📍 Rastreamento, geofencing e eventos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_realtime_tracking",
                        title="📡 Rastreamento em tempo real",
                        description=(
                            "Acompanhamento autorizado de pessoas, veículos, "
                            "equipamentos, robôs, drones ou ativos conforme "
                            "frequência e precisão configuradas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "iot_edge_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_geofence_management",
                        title="🚧 Gestão de áreas geográficas",
                        description=(
                            "Definição de áreas permitidas, restritas, "
                            "prioritárias, temporárias ou condicionais "
                            "para regras e operações baseadas em localização."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "technology_governance_policy_compliance",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_location_event_workflows",
                        title="⚡ Workflows orientados por localização",
                        description=(
                            "Acionamento de alertas, tarefas, integrações "
                            "e processos após entrada, saída, permanência, "
                            "aproximação ou mudança de rota."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_indoor_spatial_positioning",
                title="🏢 Posicionamento interno e espacial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_indoor_positioning",
                        title="🏢 Localização em ambientes internos",
                        description=(
                            "Estimativa de posição em edifícios, fábricas, "
                            "estações, armazéns e áreas onde o sinal "
                            "externo seja limitado ou indisponível."
                        ),
                        technology_dependencies=(
                            "spatial_computing_augmented_reality",
                            "iot_edge_intelligence",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_floor_zone_detection",
                        title="📐 Andares, zonas e ambientes",
                        description=(
                            "Identificação de andar, sala, corredor, setor, "
                            "zona operacional e proximidade com objetos "
                            "ou pontos de referência."
                        ),
                        technology_dependencies=(
                            "construction_bim_digital_engineering",
                            "spatial_computing_augmented_reality",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_robot_drone_localization",
                        title="🤖 Localização de robôs e drones",
                        description=(
                            "Suporte ao posicionamento e à navegação "
                            "de sistemas autônomos em ambientes internos, "
                            "externos ou com conectividade limitada."
                        ),
                        technology_dependencies=(
                            "robotics_autonomous_systems",
                            "drones_aerial_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_location_services_apis",
                title="🔌 Serviços e APIs de localização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_geocoding_services",
                        title="🏷️ Geocodificação e endereçamento",
                        description=(
                            "Conversão entre endereços, referências, "
                            "identificadores territoriais e coordenadas, "
                            "com qualidade e origem documentadas."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "api_integrations_connectors",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_distance_eta_services",
                        title="⏱️ Distâncias e estimativas de chegada",
                        description=(
                            "Cálculo de distância, duração, progresso, "
                            "tempo estimado de chegada e alternativas "
                            "conforme rede, tráfego e localização."
                        ),
                        technology_dependencies=(
                            "mobility_traffic_transport",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_location_api_delivery",
                        title="🔌 APIs e eventos de localização",
                        description=(
                            "Disponibilização controlada de coordenadas, "
                            "rotas, áreas, eventos, resultados e serviços "
                            "para aplicações e sistemas autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="navigation_privacy_security_operations",
                title="🛡️ Privacidade, segurança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="navigation_location_privacy",
                        title="🕶️ Privacidade dos dados de localização",
                        description=(
                            "Minimização, consentimento, finalidade, "
                            "retenção, anonimização e controle de acesso "
                            "aos dados de localização e trajetos."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_service_resilience",
                        title="♻️ Resiliência dos serviços de localização",
                        description=(
                            "Continuidade com múltiplas fontes, cache, "
                            "operação degradada, recuperação, retentativas "
                            "e tratamento de indisponibilidades."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="navigation_observability_audit",
                        title="📊 Observabilidade e auditoria",
                        description=(
                            "Monitoramento de precisão, latência, falhas, "
                            "fontes, APIs, eventos, custos, acessos, "
                            "versões e utilização dos serviços."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
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

    module_id = "navigation_positioning_geolocation"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        39: (273, 819),
        40: (280, 840),
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

    print("NAVIGATION_POSITIONING_GEOLOCATION_PREREQUISITES=OK")


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
    """Adiciona Navegação, Posicionamento e Geolocalização."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION =" in source:
        print("NAVIGATION_POSITIONING_GEOLOCATION_ALREADY_PRESENT=OK")
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
        NAVIGATION_POSITIONING_GEOLOCATION_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    NETWORKS_TELECOMMUNICATIONS_CONNECTIVITY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_navigation_positioning_geolocation_is_complete"

    if test_name in source:
        print("NAVIGATION_POSITIONING_GEOLOCATION_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 39
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 40
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e nove soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_navigation_positioning_geolocation_is_complete():
    assert (
        NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION.solution_id
        == "navigation_positioning_geolocation"
    )

    assert len(
        NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION.areas
    ) == 7

    assert (
        NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION.capability_count
        == 21
    )


def test_navigation_positioning_geolocation_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "navigation_positioning_geolocation"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION.status
        is module.status
    )

    assert (
        NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION.integration_type
        == module.integration_type
    )


def test_navigation_positioning_geolocation_lookup():
    assert (
        platform_technology_solution(
            "navigation_positioning_geolocation"
        )
        is NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("NAVIGATION_POSITIONING_GEOLOCATION_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    navigation_solution = module.NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION

    assert len(solutions) == 40
    assert len(navigation_solution.areas) == 7

    assert navigation_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 280
    assert total_capabilities == 840

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=40")
    print("TOTAL_TECHNOLOGY_AREAS=280")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=840")
    print("NAVIGATION_POSITIONING_GEOLOCATION_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
