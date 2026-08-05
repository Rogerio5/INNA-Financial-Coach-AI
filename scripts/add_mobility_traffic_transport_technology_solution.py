"""Adiciona Mobilidade, Tráfego e Transporte ao registro tecnológico."""

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
        "mobility_traffic_transport_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


MOBILITY_TRAFFIC_TRANSPORT_DEFINITION = """
_MOBILITY_TRAFFIC_TRANSPORT_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "mobility_traffic_transport"
    ]
)


MOBILITY_TRAFFIC_TRANSPORT_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="mobility_traffic_transport",
        icon="🚦",
        title="Mobilidade, Tráfego e Transporte",
        description=(
            "Arquitetura tecnológica para redes viárias, ativos "
            "de transporte, sensores, tráfego em tempo real, "
            "previsão de demanda, roteirização, transporte público, "
            "frotas, mobilidade multimodal, segurança viária, "
            "resposta a incidentes, sustentabilidade, governança, "
            "integrações e observabilidade operacional."
        ),
        status=(
            _MOBILITY_TRAFFIC_TRANSPORT_MODULE.status
        ),
        integration_type=(
            _MOBILITY_TRAFFIC_TRANSPORT_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="mobility_network_assets_data",
                title="🗺️ Redes, ativos e dados de mobilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="mobility_network_asset_registry",
                        title="🗂️ Registro de redes e ativos",
                        description=(
                            "Cadastro de vias, corredores, terminais, "
                            "estações, pontos, semáforos, veículos, "
                            "equipamentos e responsáveis operacionais."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "data_platform_governance",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_network_topology",
                        title="🔗 Topologia e conectividade da rede",
                        description=(
                            "Representação de trechos, cruzamentos, "
                            "sentidos, conexões, restrições, capacidades "
                            "e relações entre diferentes modais."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "gis_location_intelligence",
                            "navigation_positioning_geolocation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_data_harmonization",
                        title="✅ Harmonização dos dados de transporte",
                        description=(
                            "Padronização de coordenadas, horários, rotas, "
                            "identificadores, unidades, formatos "
                            "e informações provenientes de várias fontes."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "api_integrations_connectors",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="traffic_sensing_realtime_control",
                title="📡 Sensoriamento e tráfego em tempo real",
                capabilities=(
                    TechnologyCapability(
                        capability_id="traffic_sensor_event_ingestion",
                        title="📨 Sensores e eventos de tráfego",
                        description=(
                            "Ingestão de contagens, velocidades, ocupação, "
                            "filas, posições, estados semafóricos "
                            "e ocorrências operacionais."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="traffic_visual_analytics",
                        title="📷 Análise visual do tráfego",
                        description=(
                            "Detecção e acompanhamento de veículos, "
                            "pedestres, bicicletas, congestionamentos, "
                            "bloqueios e situações incomuns."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="traffic_signal_coordination",
                        title="🚦 Coordenação semafórica",
                        description=(
                            "Ajuste e coordenação de planos semafóricos "
                            "conforme fluxos, filas, prioridades, eventos "
                            "e limites operacionais autorizados."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                            "iot_edge_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobility_demand_flow_forecasting",
                title="📈 Demanda, fluxos e previsão",
                capabilities=(
                    TechnologyCapability(
                        capability_id="mobility_demand_forecasting",
                        title="🔮 Previsão de demanda de mobilidade",
                        description=(
                            "Estimativa de viagens, passageiros, veículos "
                            "e utilização por horário, região, modal, "
                            "evento e condição externa."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "climate_meteorological_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="traffic_flow_prediction",
                        title="📊 Previsão de fluxo e congestionamento",
                        description=(
                            "Estimativa da evolução de velocidade, volume, "
                            "filas, tempos de viagem e congestionamentos "
                            "na rede de transporte."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_scenario_simulation",
                        title="🧪 Simulação de cenários de mobilidade",
                        description=(
                            "Avaliação de mudanças viárias, novas rotas, "
                            "eventos, restrições, políticas e alterações "
                            "na oferta ou demanda."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "smart_cities_urban_infrastructure",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobility_routing_multimodal_optimization",
                title="🧭 Rotas e otimização multimodal",
                capabilities=(
                    TechnologyCapability(
                        capability_id="mobility_dynamic_routing",
                        title="🛣️ Roteirização dinâmica",
                        description=(
                            "Cálculo de rotas considerando trânsito, "
                            "bloqueios, restrições, prioridades, custos, "
                            "tempo e condições da rede."
                        ),
                        technology_dependencies=(
                            "navigation_positioning_geolocation",
                            "gis_location_intelligence",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_multimodal_journey",
                        title="🚆 Planejamento de jornadas multimodais",
                        description=(
                            "Combinação de caminhada, bicicleta, transporte "
                            "público, veículos e outros modais conforme "
                            "tempo, custo e acessibilidade."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "enterprise_decision_intelligence",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_capacity_optimization",
                        title="📈 Otimização de capacidade e oferta",
                        description=(
                            "Ajuste de frequências, veículos, faixas, "
                            "horários, equipes e recursos conforme demanda, "
                            "restrições e nível de serviço."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="public_transport_fleet_operations",
                title="🚌 Transporte público e gestão de frotas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="public_transport_operations",
                        title="🚌 Operação do transporte público",
                        description=(
                            "Acompanhamento de linhas, viagens, partidas, "
                            "chegadas, intervalos, ocupação, atrasos "
                            "e regularidade dos serviços."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "navigation_positioning_geolocation",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_fleet_management",
                        title="🚘 Gestão inteligente de frotas",
                        description=(
                            "Monitoramento de localização, utilização, "
                            "energia, combustível, manutenção, disponibilidade "
                            "e desempenho dos veículos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "digital_twins_simulation",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_service_workflows",
                        title="⚙️ Workflows operacionais de mobilidade",
                        description=(
                            "Automação de despacho, alterações de serviço, "
                            "manutenção, comunicação, escalonamento "
                            "e integração entre equipes e sistemas."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobility_safety_incidents_resilience",
                title="🛡️ Segurança, incidentes e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="mobility_incident_detection",
                        title="🚨 Detecção de incidentes viários",
                        description=(
                            "Identificação de acidentes, veículos parados, "
                            "bloqueios, objetos, condições perigosas "
                            "e interrupções dos serviços."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "real_time_event_intelligence",
                            "emergency_disaster_management",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_incident_response",
                        title="🚑 Resposta e coordenação de incidentes",
                        description=(
                            "Acionamento de equipes, desvios, sinalização, "
                            "notificações, bloqueios, rotas alternativas "
                            "e procedimentos de resposta."
                        ),
                        technology_dependencies=(
                            "emergency_disaster_management",
                            "agent_process_orchestration",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_resilience_continuity",
                        title="♻️ Resiliência e continuidade do transporte",
                        description=(
                            "Planejamento de contingências, rotas alternativas, "
                            "redundância, recuperação e continuidade "
                            "dos serviços essenciais de mobilidade."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "simulation_optimization_operations_research",
                            "smart_cities_urban_infrastructure",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobility_governance_sustainability_operations",
                title="📊 Governança, sustentabilidade e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="mobility_sustainability_emissions",
                        title="🌱 Sustentabilidade e emissões",
                        description=(
                            "Acompanhamento de consumo, emissões, eficiência, "
                            "uso dos modais, eletrificação, impactos ambientais "
                            "e alternativas de mobilidade sustentável."
                        ),
                        technology_dependencies=(
                            "esg_sustainability",
                            "energy_smart_grids",
                            "environmental_natural_resources_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_privacy_security",
                        title="🔐 Privacidade e segurança dos dados",
                        description=(
                            "Proteção de localização, trajetos, usuários, "
                            "veículos, comandos, integrações e informações "
                            "operacionais sensíveis."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="mobility_observability_audit",
                        title="🧾 Observabilidade e auditoria",
                        description=(
                            "Monitoramento de sensores, integrações, modelos, "
                            "rotas, eventos, qualidade, custos, acessos, "
                            "decisões e disponibilidade dos serviços."
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

    module_id = "mobility_traffic_transport"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        36: (252, 756),
        37: (259, 777),
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

    print("MOBILITY_TRAFFIC_TRANSPORT_PREREQUISITES=OK")


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
    """Adiciona Mobilidade, Tráfego e Transporte."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "MOBILITY_TRAFFIC_TRANSPORT_SOLUTION =" in source:
        print("MOBILITY_TRAFFIC_TRANSPORT_ALREADY_PRESENT=OK")
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
        MOBILITY_TRAFFIC_TRANSPORT_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    EMERGENCY_DISASTER_MANAGEMENT_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    MOBILITY_TRAFFIC_TRANSPORT_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("MOBILITY_TRAFFIC_TRANSPORT_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_mobility_traffic_transport_is_complete" in source:
        print("MOBILITY_TRAFFIC_TRANSPORT_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "MOBILITY_TRAFFIC_TRANSPORT_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 36
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 37
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e seis soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_mobility_traffic_transport_is_complete():
    assert (
        MOBILITY_TRAFFIC_TRANSPORT_SOLUTION.solution_id
        == "mobility_traffic_transport"
    )

    assert len(
        MOBILITY_TRAFFIC_TRANSPORT_SOLUTION.areas
    ) == 7

    assert (
        MOBILITY_TRAFFIC_TRANSPORT_SOLUTION.capability_count
        == 21
    )


def test_mobility_traffic_transport_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "mobility_traffic_transport"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        MOBILITY_TRAFFIC_TRANSPORT_SOLUTION.status
        is module.status
    )

    assert (
        MOBILITY_TRAFFIC_TRANSPORT_SOLUTION.integration_type
        == module.integration_type
    )


def test_mobility_traffic_transport_lookup():
    assert (
        platform_technology_solution(
            "mobility_traffic_transport"
        )
        is MOBILITY_TRAFFIC_TRANSPORT_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("MOBILITY_TRAFFIC_TRANSPORT_TESTS_CREATED=OK")


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

    mobility_solution = getattr(
        module,
        "MOBILITY_TRAFFIC_TRANSPORT_SOLUTION",
    )

    assert len(solutions) == 37
    assert len(mobility_solution.areas) == 7

    assert mobility_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 259
    assert total_capabilities == 777

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=37")
    print("TOTAL_TECHNOLOGY_AREAS=259")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=777")
    print("MOBILITY_TRAFFIC_TRANSPORT_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
