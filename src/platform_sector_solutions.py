"""Registro das soluções setoriais especializadas da INNA."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.platform_modules import PLATFORM_MODULE_BY_ID


class SectorSolutionStatus(StrEnum):
    """Situação de uma solução setorial."""

    ACTIVE = "active"
    INTEGRATING = "integrating"
    PLANNED = "planned"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class SectorCapability:
    """Capacidade especializada dentro de uma área setorial."""

    capability_id: str
    title: str
    description: str
    technology_dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SectorArea:
    """Área interna de uma solução setorial."""

    area_id: str
    title: str
    capabilities: tuple[SectorCapability, ...]


@dataclass(frozen=True, slots=True)
class PlatformSectorSolution:
    """Solução setorial composta por áreas e capacidades."""

    solution_id: str
    icon: str
    title: str
    description: str
    status: SectorSolutionStatus
    integration_type: str
    areas: tuple[SectorArea, ...]

    @property
    def capability_count(self) -> int:
        """Quantidade total de capacidades da solução."""

        return sum(len(area.capabilities) for area in self.areas)

    @property
    def technology_dependencies(self) -> tuple[str, ...]:
        """Dependências tecnológicas sem repetições."""

        return tuple(
            dict.fromkeys(
                dependency
                for area in self.areas
                for capability in area.capabilities
                for dependency in (capability.technology_dependencies)
            )
        )


TRANSPORT_MOBILITY_SOLUTION = PlatformSectorSolution(
    solution_id="mobility_transport_connected_vehicles",
    icon="🚚",
    title=("Mobilidade, Transporte e Veículos Conectados"),
    description=(
        "Solução para veículos, frotas, transporte rodoviário, "
        "ferroviário, aéreo, marítimo, mobilidade urbana e "
        "máquinas especiais."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="road_transport",
            title="🚗 Transporte rodoviário",
            capabilities=(
                SectorCapability(
                    capability_id="connected_vehicle_telemetry",
                    title="🚘 Veículos conectados e telemetria",
                    description=(
                        "Coleta e análise de velocidade, localização, "
                        "consumo, quilometragem e eventos do veículo."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "real_time_event_intelligence",
                        "cloud_devops_finops",
                    ),
                ),
                SectorCapability(
                    capability_id="intelligent_fleet_management",
                    title="🚛 Gestão inteligente de frotas",
                    description=(
                        "Controle de veículos, motoristas, viagens, "
                        "disponibilidade, custos e produtividade."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="automotive_predictive_maintenance",
                    title="🔧 Manutenção preditiva automotiva",
                    description=(
                        "Detecção de falhas, desgaste, anomalias e "
                        "previsão de manutenção de veículos."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "digital_twins_simulation",
                        "ai_bias_quality_monitoring",
                    ),
                ),
                SectorCapability(
                    capability_id="fuel_emissions_efficiency",
                    title="⛽ Combustível, emissões e eficiência",
                    description=(
                        "Análise de consumo, autonomia, emissões, "
                        "custos e eficiência operacional."
                    ),
                    technology_dependencies=(
                        "energy_smart_grids",
                        "esg_sustainability",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="electric_vehicles_charging",
                    title="🔋 Veículos elétricos, baterias e recarga",
                    description=(
                        "Gestão de bateria, autonomia, pontos de "
                        "recarga, demanda e custos energéticos."
                    ),
                    technology_dependencies=(
                        "energy_smart_grids",
                        "iot_edge_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="motorcycle_mobility_safety",
                    title="🏍️ Mobilidade e segurança para motocicletas",
                    description=(
                        "Telemetria, rotas, risco, manutenção e "
                        "segurança operacional de motocicletas."
                    ),
                    technology_dependencies=(
                        "navigation_positioning_geolocation",
                        "operational_security_resilience",
                        "computer_vision_video_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="rail_transport",
            title="🚆 Transporte ferroviário",
            capabilities=(
                SectorCapability(
                    capability_id="rail_operations_monitoring",
                    title="🚆 Operações ferroviárias inteligentes",
                    description=(
                        "Monitoramento de composições, horários, "
                        "rotas, capacidade e ocorrências."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "iot_edge_intelligence",
                        "gis_location_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="rail_predictive_maintenance",
                    title="🛤️ Manutenção ferroviária preditiva",
                    description=(
                        "Análise de trilhos, rodas, motores, sinais "
                        "e infraestrutura ferroviária."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "computer_vision_video_analytics",
                        "digital_twins_simulation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="aviation",
            title="✈️ Aviação e operações aeroportuárias",
            capabilities=(
                SectorCapability(
                    capability_id="aircraft_operations_maintenance",
                    title="✈️ Operações e manutenção aeronáutica",
                    description=(
                        "Gestão de aeronaves, componentes, inspeções, "
                        "manutenção e disponibilidade operacional."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "digital_twins_simulation",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="flight_airport_route_management",
                    title="🛫 Voos, aeroportos e rotas",
                    description=(
                        "Planejamento de voos, rotas, capacidade, "
                        "pátio e operações aeroportuárias."
                    ),
                    technology_dependencies=(
                        "navigation_positioning_geolocation",
                        "gis_location_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="aviation_weather_risk",
                    title="🌦️ Clima e riscos meteorológicos",
                    description=(
                        "Alertas de tempestades, ventos, visibilidade "
                        "e riscos para operações aéreas."
                    ),
                    technology_dependencies=(
                        "climate_meteorological_intelligence",
                        "real_time_event_intelligence",
                        "geoai_earth_observation",
                    ),
                ),
                SectorCapability(
                    capability_id="airport_baggage_cargo",
                    title="🧳 Bagagens, cargas e logística aeroportuária",
                    description=(
                        "Rastreamento de bagagens, cargas, contêineres "
                        "e eventos logísticos."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "iot_edge_intelligence",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="maritime_transport",
            title="🚢 Transporte marítimo e portos",
            capabilities=(
                SectorCapability(
                    capability_id="vessel_fleet_management",
                    title="🚢 Gestão de embarcações e frotas marítimas",
                    description=(
                        "Monitoramento de embarcações, viagens, "
                        "consumo, tripulação e disponibilidade."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "navigation_positioning_geolocation",
                        "asset_management_smart_maintenance",
                    ),
                ),
                SectorCapability(
                    capability_id="port_operations",
                    title="⚓ Operações portuárias",
                    description=(
                        "Gestão de berços, pátios, cargas, filas, "
                        "equipamentos e movimentações."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "enterprise_decision_intelligence",
                        "digital_twins_simulation",
                    ),
                ),
                SectorCapability(
                    capability_id="maritime_route_weather",
                    title="🌊 Rotas e condições marítimas",
                    description=(
                        "Rotas, ondas, ventos, tempestades e riscos "
                        "para navegação marítima."
                    ),
                    technology_dependencies=(
                        "climate_meteorological_intelligence",
                        "gis_location_intelligence",
                        "geoai_earth_observation",
                    ),
                ),
                SectorCapability(
                    capability_id="container_cargo_traceability",
                    title="📦 Cargas e contêineres rastreáveis",
                    description=(
                        "Rastreamento de cargas, contêineres, origem, "
                        "destino e eventos da cadeia logística."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "iot_edge_intelligence",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="urban_mobility",
            title="🚌 Mobilidade urbana",
            capabilities=(
                SectorCapability(
                    capability_id="public_transport_intelligence",
                    title="🚌 Transporte público inteligente",
                    description=(
                        "Linhas, horários, lotação, demanda, atrasos "
                        "e qualidade do serviço."
                    ),
                    technology_dependencies=(
                        "mobility_traffic_transport",
                        "real_time_event_intelligence",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="traffic_route_intelligence",
                    title="🚦 Tráfego, rotas e congestionamentos",
                    description=(
                        "Análise de tráfego, rotas alternativas, "
                        "incidentes e tempos de deslocamento."
                    ),
                    technology_dependencies=(
                        "gis_location_intelligence",
                        "navigation_positioning_geolocation",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="special_vehicles_machinery",
            title="🚜 Máquinas e veículos especiais",
            capabilities=(
                SectorCapability(
                    capability_id="heavy_machinery_telemetry",
                    title="🚜 Telemetria de máquinas pesadas",
                    description=(
                        "Monitoramento de máquinas agrícolas, "
                        "industriais, mineração e construção."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "asset_management_smart_maintenance",
                        "digital_twins_simulation",
                    ),
                ),
                SectorCapability(
                    capability_id="special_vehicle_safety",
                    title="🛡️ Segurança de veículos especiais",
                    description=(
                        "Riscos operacionais, zonas seguras, alertas "
                        "e prevenção de acidentes."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "computer_vision_video_analytics",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
    ),
)


AGRIBUSINESS_SOLUTION = PlatformSectorSolution(
    solution_id="agribusiness_smart_agriculture_bioeconomy",
    icon="🌾",
    title=("Agronegócio, Agricultura Inteligente e Bioeconomia"),
    description=(
        "Solução para produção vegetal, pecuária, máquinas, "
        "clima, solo, água, armazenagem, logística, riscos, "
        "sustentabilidade e rastreabilidade agroalimentar."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="crop_production",
            title="🌱 Produção vegetal",
            capabilities=(
                SectorCapability(
                    capability_id="precision_agriculture",
                    title="🌱 Agricultura de precisão e manejo por talhão",
                    description=(
                        "Zonas de manejo, mapas de produtividade, "
                        "aplicação localizada e análise por talhão."
                    ),
                    technology_dependencies=(
                        "gis_location_intelligence",
                        "geoai_earth_observation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="crop_monitoring_satellite",
                    title="🛰️ Monitoramento de lavouras por satélite",
                    description=(
                        "Acompanhamento do vigor, desenvolvimento, "
                        "estresse e mudanças da lavoura."
                    ),
                    technology_dependencies=(
                        "geoai_earth_observation",
                        "gis_location_intelligence",
                        "multimodal_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="crop_disease_pest_detection",
                    title="👁️ Pragas, doenças e plantas daninhas",
                    description=(
                        "Detecção visual de pragas, doenças, falhas "
                        "de plantio e plantas daninhas."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "multimodal_ai",
                        "ai_evaluation_benchmarks_red_team",
                    ),
                ),
                SectorCapability(
                    capability_id="harvest_yield_forecasting",
                    title="🌾 Safra e previsão de produtividade",
                    description=(
                        "Planejamento de safra, estimativa de produção "
                        "e análise de riscos agrícolas."
                    ),
                    technology_dependencies=(
                        "climate_meteorological_intelligence",
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="soil_water_climate",
            title="💧 Clima, solo e água",
            capabilities=(
                SectorCapability(
                    capability_id="agrometeorology_alerts",
                    title="🌦️ Clima, agrometeorologia e alertas",
                    description=(
                        "Previsões, chuva, seca, geada, calor e alertas "
                        "voltados à produção agropecuária."
                    ),
                    technology_dependencies=(
                        "climate_meteorological_intelligence",
                        "real_time_event_intelligence",
                        "geoai_earth_observation",
                    ),
                ),
                SectorCapability(
                    capability_id="smart_irrigation",
                    title="💧 Irrigação inteligente e gestão da água",
                    description=(
                        "Controle de irrigação, umidade, consumo, "
                        "disponibilidade e eficiência hídrica."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "environmental_natural_resources_intelligence",
                        "energy_smart_grids",
                    ),
                ),
                SectorCapability(
                    capability_id="soil_fertility_nutrition",
                    title="🧪 Solo, fertilidade e nutrição de plantas",
                    description=(
                        "Análise de solo, fertilidade, nutrientes, "
                        "correções e recomendações por área."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "gis_location_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="agricultural_machinery_automation",
            title="🚜 Máquinas e automação",
            capabilities=(
                SectorCapability(
                    capability_id="agricultural_robotics",
                    title="🤖 Máquinas agrícolas, robótica e automação",
                    description=(
                        "Integração de tratores, implementos, robôs, "
                        "pulverização e operações automatizadas."
                    ),
                    technology_dependencies=(
                        "robotics_autonomous_systems",
                        "iot_edge_intelligence",
                        "computer_vision_video_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="farm_machine_telemetry",
                    title="🚜 Telemetria e manutenção de máquinas",
                    description=(
                        "Monitoramento de uso, consumo, falhas, peças "
                        "e manutenção de máquinas agrícolas."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "digital_twins_simulation",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="agricultural_drones",
                    title="🛸 Drones, mapeamento e inspeção agrícola",
                    description=(
                        "Mapeamento, inspeção, imagens aéreas, contagem "
                        "e análise de áreas produtivas."
                    ),
                    technology_dependencies=(
                        "drones_aerial_intelligence",
                        "geoai_earth_observation",
                        "computer_vision_video_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="precision_livestock",
            title="🐄 Pecuária de precisão",
            capabilities=(
                SectorCapability(
                    capability_id="animal_health_monitoring",
                    title="🐄 Pecuária de precisão e saúde animal",
                    description=(
                        "Monitoramento de saúde, comportamento, "
                        "alimentação, reprodução e produtividade."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "computer_vision_video_analytics",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="pasture_management",
                    title="🌿 Pastagem e manejo inteligente",
                    description=(
                        "Avaliação de pastagens, lotação, rotação, "
                        "disponibilidade e qualidade da alimentação."
                    ),
                    technology_dependencies=(
                        "geoai_earth_observation",
                        "gis_location_intelligence",
                        "environmental_natural_resources_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="storage_post_harvest",
            title="🏭 Armazenagem e pós-colheita",
            capabilities=(
                SectorCapability(
                    capability_id="smart_silos_storage",
                    title="🏭 Silos e armazenagem inteligente",
                    description=(
                        "Temperatura, umidade, ventilação, estoque, "
                        "qualidade e perdas em armazenagem."
                    ),
                    technology_dependencies=(
                        "iot_edge_intelligence",
                        "real_time_event_intelligence",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="grain_quality_inspection",
                    title="👁️ Qualidade de grãos e produtos",
                    description=(
                        "Inspeção, classificação, defeitos, maturação "
                        "e qualidade de produtos agropecuários."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "multimodal_ai",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="agricultural_logistics_traceability",
            title="📦 Logística e rastreabilidade",
            capabilities=(
                SectorCapability(
                    capability_id="agricultural_supply_chain",
                    title="🚚 Logística e escoamento da produção",
                    description=(
                        "Rotas, cargas, transporte, armazenagem, "
                        "entregas e custos logísticos."
                    ),
                    technology_dependencies=(
                        "mobility_traffic_transport",
                        "gis_location_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="food_chain_traceability",
                    title="📦 Rastreabilidade agroalimentar",
                    description=(
                        "Origem, lotes, produção, transformação, "
                        "transporte e destino dos produtos."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "api_integrations_connectors",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="agricultural_finance_risk",
            title="💰 Gestão financeira e riscos",
            capabilities=(
                SectorCapability(
                    capability_id="rural_financial_management",
                    title="💰 Gestão financeira rural",
                    description=(
                        "Custos, orçamento, fluxo de caixa, margem, "
                        "investimentos e planejamento financeiro."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="rural_risk_insurance",
                    title="🛡️ Riscos e seguro rural",
                    description=(
                        "Riscos climáticos, produtivos, operacionais "
                        "e apoio à análise de seguro rural."
                    ),
                    technology_dependencies=(
                        "climate_meteorological_intelligence",
                        "responsible_ai_ethics_risk",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="sustainability_bioeconomy",
            title="🌱 Sustentabilidade e bioeconomia",
            capabilities=(
                SectorCapability(
                    capability_id="rural_esg_carbon",
                    title="🌱 ESG, carbono e sustentabilidade rural",
                    description=(
                        "Emissões, carbono, recursos naturais, metas "
                        "ambientais e evidências de sustentabilidade."
                    ),
                    technology_dependencies=(
                        "esg_sustainability",
                        "environmental_natural_resources_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="smart_forestry",
                    title="🌳 Silvicultura e manejo florestal inteligente",
                    description=(
                        "Monitoramento florestal, inventário, riscos, "
                        "crescimento e manejo sustentável."
                    ),
                    technology_dependencies=(
                        "geoai_earth_observation",
                        "drones_aerial_intelligence",
                        "environmental_natural_resources_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="agricultural_biotechnology",
                    title="🧬 Biotecnologia e melhoramento por dados",
                    description=(
                        "Organização de experimentos, características, "
                        "resultados e descoberta assistida."
                    ),
                    technology_dependencies=(
                        "research_labs_assisted_discovery",
                        "knowledge_graph_semantic_ai",
                        "scientific_computing_engineering",
                    ),
                ),
            ),
        ),
    ),
)


PET_SHOPS_VETERINARY_SOLUTION = PlatformSectorSolution(
    solution_id="pet_shops_veterinary_services",
    icon="🐾",
    title="Pet Shops e Serviços Veterinários",
    description="Solução para atendimento, agenda, serviços, saúde veterinária, estoque, pagamentos e relacionamento com tutores.",
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="pet_customer_registration",
            title="👤 Atendimento, tutores e animais",
            capabilities=(
                SectorCapability(
                    capability_id="pet_tutor_registration",
                    title="👤 Cadastro de tutores e animais",
                    description="Cadastro centralizado de tutores, animais, contatos, preferências e histórico.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_digital_profile",
                    title="🐕 Perfil digital do animal",
                    description="Organização de espécie, raça, idade, peso, características, alertas e informações gerais.",
                    technology_dependencies=(
                        "document_ai",
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_service_history",
                    title="📋 Histórico de atendimentos",
                    description="Linha do tempo de consultas, serviços, compras, observações e ocorrências.",
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "crm_sales_intelligence",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="pet_schedule_services",
            title="📅 Agenda e serviços",
            capabilities=(
                SectorCapability(
                    capability_id="pet_intelligent_schedule",
                    title="📅 Agenda inteligente",
                    description="Agendamento de consultas, banho, tosa, vacinas, retornos e serviços recorrentes.",
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_bath_grooming",
                    title="🛁 Banho, tosa e estética animal",
                    description="Gestão de serviços, profissionais, duração, preferências e acompanhamento da execução.",
                    technology_dependencies=(
                        "erp_business_operations",
                        "business_automation",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_reminders_notifications",
                    title="🔔 Lembretes e notificações",
                    description="Avisos de agendamentos, retornos, vacinas, medicações e serviços pendentes.",
                    technology_dependencies=(
                        "intelligent_support",
                        "real_time_event_intelligence",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="veterinary_health",
            title="🩺 Saúde veterinária",
            capabilities=(
                SectorCapability(
                    capability_id="veterinary_medical_records",
                    title="🩺 Prontuário veterinário",
                    description="Registro de consultas, avaliações, exames, diagnósticos e orientações profissionais.",
                    technology_dependencies=(
                        "document_ai",
                        "privacy_data_protection_lgpd",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="veterinary_vaccination_control",
                    title="💉 Vacinação e prevenção",
                    description="Controle de vacinas, antiparasitários, protocolos preventivos e datas futuras.",
                    technology_dependencies=(
                        "business_automation",
                        "real_time_event_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="veterinary_exams_documents",
                    title="📄 Exames e documentos veterinários",
                    description="Organização e análise assistida de exames, laudos, receitas e documentos.",
                    technology_dependencies=(
                        "document_ai",
                        "multimodal_ai",
                        "enterprise_rag",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="pet_inventory_pharmacy",
            title="📦 Estoque e farmácia",
            capabilities=(
                SectorCapability(
                    capability_id="pet_inventory_management",
                    title="📦 Estoque de produtos e medicamentos",
                    description="Controle de rações, acessórios, medicamentos, lotes, validade e disponibilidade.",
                    technology_dependencies=(
                        "erp_business_operations",
                        "supply_chain_procurement_logistics",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_stock_replenishment",
                    title="🔄 Reposição inteligente",
                    description="Previsão de demanda, ponto de reposição, alertas e sugestões de compra.",
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                        "supply_chain_procurement_logistics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="pet_finance_payments",
            title="💰 Financeiro e pagamentos",
            capabilities=(
                SectorCapability(
                    capability_id="pet_billing_payments",
                    title="💳 Cobranças e pagamentos",
                    description="Orçamentos, cobranças, recebimentos, parcelamentos e conciliação.",
                    technology_dependencies=(
                        "financial_solutions",
                        "erp_business_operations",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_financial_indicators",
                    title="📊 Indicadores financeiros",
                    description="Receita, custos, margem, ticket médio, inadimplência e rentabilidade.",
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="pet_relationship_loyalty",
            title="🤝 Relacionamento e fidelização",
            capabilities=(
                SectorCapability(
                    capability_id="pet_customer_relationship",
                    title="🤝 Relacionamento com tutores",
                    description="Comunicação, histórico, preferências, feedbacks e atendimento personalizado.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "intelligent_support",
                        "multimodal_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="pet_loyalty_campaigns",
                    title="🎁 Fidelidade e campanhas",
                    description="Programas de pontos, campanhas, ofertas e segmentação de clientes.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "enterprise_decision_intelligence",
                        "business_automation",
                    ),
                ),
            ),
        ),
    ),
)

SUPERMARKETS_WHOLESALE_SOLUTION = PlatformSectorSolution(
    solution_id="supermarkets_wholesale",
    icon="🛒",
    title="Supermercados e Atacado",
    description="Solução para compras, fornecedores, estoque, validade, preços, vendas, reposição, clientes, perdas e rentabilidade.",
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="supermarket_procurement_suppliers",
            title="🤝 Compras e fornecedores",
            capabilities=(
                SectorCapability(
                    capability_id="supplier_management",
                    title="🤝 Gestão de fornecedores",
                    description="Cadastro, desempenho, prazos, condições, qualidade e histórico de fornecedores.",
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "erp_business_operations",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="intelligent_procurement",
                    title="🧠 Compras inteligentes",
                    description="Sugestões de compra baseadas em demanda, estoque, sazonalidade e prazo.",
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_inventory_expiration",
            title="📦 Estoque e validade",
            capabilities=(
                SectorCapability(
                    capability_id="supermarket_inventory_control",
                    title="📦 Controle de estoque",
                    description="Entradas, saídas, transferências, inventário, disponibilidade e divergências.",
                    technology_dependencies=(
                        "erp_business_operations",
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="product_expiration_control",
                    title="⏳ Controle de validade e lotes",
                    description="Monitoramento de validade, lotes, alertas, rastreabilidade e prevenção de perdas.",
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                        "business_automation",
                    ),
                ),
                SectorCapability(
                    capability_id="smart_shelf_monitoring",
                    title="👁️ Monitoramento inteligente de gôndolas",
                    description="Identificação de ruptura, organização, disponibilidade e exposição de produtos.",
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "iot_edge_intelligence",
                        "multimodal_ai",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_pricing_promotions",
            title="🏷️ Preços e promoções",
            capabilities=(
                SectorCapability(
                    capability_id="intelligent_pricing",
                    title="🏷️ Precificação inteligente",
                    description="Análise de custos, margem, concorrência, estoque e demanda para apoiar preços.",
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "scientific_computing_engineering",
                    ),
                ),
                SectorCapability(
                    capability_id="promotion_management",
                    title="📣 Promoções e campanhas",
                    description="Planejamento, segmentação, execução e avaliação de campanhas promocionais.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "business_automation",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_sales_checkout",
            title="💳 Vendas e frente de caixa",
            capabilities=(
                SectorCapability(
                    capability_id="checkout_sales_operations",
                    title="💳 Operações de venda e caixa",
                    description="Vendas, pagamentos, cancelamentos, descontos, operadores e fechamento de caixa.",
                    technology_dependencies=(
                        "erp_business_operations",
                        "api_integrations_connectors",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="checkout_fraud_anomalies",
                    title="🛡️ Fraudes e anomalias no caixa",
                    description="Detecção de comportamentos incomuns, perdas, cancelamentos e operações suspeitas.",
                    technology_dependencies=(
                        "cybersecurity_fraud_prevention",
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_replenishment_logistics",
            title="🚚 Logística e reposição",
            capabilities=(
                SectorCapability(
                    capability_id="automatic_replenishment",
                    title="🔄 Reposição automática",
                    description="Sugestões e alertas de reposição conforme vendas, estoque, demanda e prazos.",
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="distribution_logistics",
                    title="🚚 Distribuição e logística",
                    description="Centros de distribuição, entregas, rotas, transferências e acompanhamento logístico.",
                    technology_dependencies=(
                        "mobility_traffic_transport",
                        "gis_location_intelligence",
                        "supply_chain_procurement_logistics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_customers_loyalty",
            title="👥 Clientes e fidelidade",
            capabilities=(
                SectorCapability(
                    capability_id="supermarket_customer_intelligence",
                    title="👥 Inteligência de clientes",
                    description="Segmentação, perfil de compra, frequência, preferências e comportamento.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="supermarket_loyalty_program",
                    title="🎁 Programa de fidelidade",
                    description="Pontos, benefícios, ofertas personalizadas e acompanhamento de engajamento.",
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "business_automation",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="supermarket_losses_profitability",
            title="📊 Dados, perdas e rentabilidade",
            capabilities=(
                SectorCapability(
                    capability_id="retail_loss_prevention",
                    title="⚠️ Prevenção de perdas",
                    description="Análise de quebras, vencimentos, furtos, divergências e causas de perdas.",
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "cybersecurity_fraud_prevention",
                        "quality_process_management",
                    ),
                ),
                SectorCapability(
                    capability_id="supermarket_profitability",
                    title="📈 Margem e rentabilidade",
                    description="Margem por produto, categoria, loja, período e perfil de cliente.",
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
    ),
)


RETAIL_STORES_SOLUTION = PlatformSectorSolution(
    solution_id="retail_stores",
    icon="🏪",
    title="Lojas e Varejo",
    description=(
        "Solução para catálogo, produtos, vendas, pedidos, "
        "estoque, abastecimento, relacionamento com clientes, "
        "operações omnichannel, entregas e rentabilidade."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="retail_catalog_products",
            title="🏷️ Catálogo e produtos",
            capabilities=(
                SectorCapability(
                    capability_id="retail_product_catalog",
                    title="🏷️ Catálogo inteligente de produtos",
                    description=(
                        "Cadastro centralizado de produtos, categorias, "
                        "marcas, variações, atributos, imagens e preços."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "data_platform_governance",
                        "multimodal_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_product_content",
                    title="📝 Conteúdo e descrição de produtos",
                    description=(
                        "Geração e padronização assistida de descrições, "
                        "características, títulos e conteúdo comercial."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "enterprise_rag",
                        "business_automation",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_pricing_promotions",
                    title="🏷️ Preços, descontos e promoções",
                    description=(
                        "Gestão de preços, descontos, campanhas, regras "
                        "promocionais, margem e períodos de validade."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "business_automation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_sales_orders",
            title="🛍️ Vendas e pedidos",
            capabilities=(
                SectorCapability(
                    capability_id="retail_sales_checkout",
                    title="💳 Vendas e frente de caixa",
                    description=(
                        "Operações de venda, pagamento, desconto, troca, "
                        "devolução, cancelamento e fechamento de caixa."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "api_integrations_connectors",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_order_management",
                    title="📋 Gestão inteligente de pedidos",
                    description=(
                        "Recebimento, separação, aprovação, faturamento, "
                        "expedição, entrega e acompanhamento de pedidos."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_sales_fraud",
                    title="🛡️ Fraudes e anomalias em vendas",
                    description=(
                        "Detecção de transações incomuns, abuso de "
                        "descontos, devoluções suspeitas e divergências."
                    ),
                    technology_dependencies=(
                        "cybersecurity_fraud_prevention",
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_inventory_supply",
            title="📦 Estoque e abastecimento",
            capabilities=(
                SectorCapability(
                    capability_id="retail_inventory_control",
                    title="📦 Controle integrado de estoque",
                    description=(
                        "Entradas, saídas, reservas, transferências, "
                        "inventários e disponibilidade por unidade."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_smart_replenishment",
                    title="🔄 Reposição e abastecimento inteligente",
                    description=(
                        "Previsão de demanda, ponto de reposição, "
                        "sugestões de compra e transferências de estoque."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_loss_prevention",
                    title="⚠️ Prevenção de perdas no varejo",
                    description=(
                        "Análise de furtos, avarias, divergências, "
                        "rupturas, devoluções e causas de perdas."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "cybersecurity_fraud_prevention",
                        "quality_process_management",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_customer_experience",
            title="🤝 CRM e experiência do cliente",
            capabilities=(
                SectorCapability(
                    capability_id="retail_customer_profile",
                    title="👤 Perfil e inteligência do cliente",
                    description=(
                        "Histórico de compras, preferências, frequência, "
                        "segmentação, comportamento e valor do cliente."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_loyalty_service",
                    title="🎁 Fidelização e atendimento inteligente",
                    description=(
                        "Programas de fidelidade, benefícios, campanhas, "
                        "feedbacks e suporte personalizado."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "intelligent_support",
                        "business_automation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_omnichannel_delivery",
            title="📱 Omnichannel e entregas",
            capabilities=(
                SectorCapability(
                    capability_id="retail_omnichannel_operations",
                    title="📱 Experiência omnichannel",
                    description=(
                        "Integração entre loja física, aplicativo, site, "
                        "marketplace, atendimento e canais de venda."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "digital_experiences_intelligent_interfaces",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_delivery_fulfillment",
                    title="🚚 Entregas e atendimento de pedidos",
                    description=(
                        "Separação, retirada em loja, entrega local, "
                        "rastreamento, rotas e confirmação de recebimento."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "mobility_traffic_transport",
                        "gis_location_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_analytics_profitability",
            title="📊 Indicadores e rentabilidade",
            capabilities=(
                SectorCapability(
                    capability_id="retail_business_analytics",
                    title="📊 Analytics e indicadores do varejo",
                    description=(
                        "Vendas, conversão, ticket médio, estoque, "
                        "clientes, desempenho e metas operacionais."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_profitability_forecasting",
                    title="📈 Rentabilidade e previsão de demanda",
                    description=(
                        "Margem, custos, rentabilidade por produto, "
                        "unidade, canal e previsão de demanda."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "data_bi_copilot",
                    ),
                ),
            ),
        ),
    ),
)


DENTISTRY_SOLUTION = PlatformSectorSolution(
    solution_id="dentistry",
    icon="🦷",
    title="Odontologia",
    description=(
        "Solução para pacientes, prontuários, agenda, "
        "tratamentos, imagens, documentos, orçamentos, "
        "pagamentos, materiais e gestão odontológica."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="dentistry_patients_records",
            title="👤 Pacientes e prontuários",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_patient_registration",
                    title="👤 Cadastro completo de pacientes",
                    description=(
                        "Cadastro de pacientes, contatos, responsáveis, "
                        "preferências e informações administrativas."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_health_history",
                    title="📋 Histórico de saúde e atendimento",
                    description=(
                        "Organização de antecedentes informados, "
                        "atendimentos, observações e ocorrências."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "data_traceability_provenance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_digital_record",
                    title="🗂️ Prontuário odontológico digital",
                    description=(
                        "Registro estruturado da evolução, procedimentos, "
                        "documentos e histórico odontológico."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "knowledge_graph_semantic_ai",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_schedule_returns",
            title="📅 Agenda e retornos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_intelligent_schedule",
                    title="📅 Agenda odontológica inteligente",
                    description=(
                        "Agendamento de consultas, procedimentos, "
                        "avaliações, retornos e encaixes."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_recall_reminders",
                    title="🔔 Retornos, confirmações e lembretes",
                    description=(
                        "Confirmações automáticas, lembretes, reagendamento "
                        "e acompanhamento de retornos pendentes."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "business_automation",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_treatment_planning",
            title="🦷 Planos de tratamento",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_treatment_plan",
                    title="🦷 Planejamento de tratamentos",
                    description=(
                        "Organização de etapas, procedimentos, prioridades, "
                        "prazos e acompanhamento do plano de tratamento."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "knowledge_graph_semantic_ai",
                        "enterprise_rag",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_clinical_evolution",
                    title="📈 Evolução e acompanhamento",
                    description=(
                        "Linha do tempo dos procedimentos realizados, "
                        "etapas concluídas e acompanhamento do paciente."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "tools_analytics",
                        "document_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_assisted_information",
                    title="🧠 Informação odontológica assistida",
                    description=(
                        "Consulta controlada a protocolos, documentos "
                        "internos e materiais de referência profissional."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "responsible_ai_ethics_risk",
                        "ai_certification_system_evidence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_images_documents",
            title="🩻 Imagens e documentos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_images_management",
                    title="🩻 Gestão de imagens odontológicas",
                    description=(
                        "Organização de fotografias, radiografias, "
                        "documentos visuais e histórico de imagens."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "document_ai",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_document_generation",
                    title="📄 Documentos e formulários",
                    description=(
                        "Geração assistida de formulários, termos, "
                        "declarações, orientações e documentos administrativos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_budgets_payments",
            title="💰 Orçamentos e pagamentos",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_treatment_budgets",
                    title="💰 Orçamentos de tratamentos",
                    description=(
                        "Composição de procedimentos, valores, condições, "
                        "etapas e aprovação de orçamentos."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "erp_business_operations",
                        "business_automation",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_billing_payments",
                    title="💳 Cobranças e pagamentos",
                    description=(
                        "Cobranças, recebimentos, parcelamentos, "
                        "inadimplência e conciliação financeira."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "api_integrations_connectors",
                        "erp_business_operations",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="dentistry_management_compliance",
            title="🏥 Gestão clínica e conformidade",
            capabilities=(
                SectorCapability(
                    capability_id="dentistry_material_inventory",
                    title="📦 Materiais e estoque odontológico",
                    description=(
                        "Controle de materiais, produtos, lotes, "
                        "validade, consumo e necessidade de reposição."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "supply_chain_procurement_logistics",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_quality_compliance",
                    title="✅ Qualidade, segurança e conformidade",
                    description=(
                        "Processos, evidências, checklists, documentos, "
                        "rastreabilidade e controles administrativos."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "technology_governance_policy_compliance",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="dentistry_management_indicators",
                    title="📊 Indicadores de gestão odontológica",
                    description=(
                        "Agenda, faltas, ocupação, tratamentos, receita, "
                        "custos, retorno e desempenho operacional."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
    ),
)


HOSPITALS_CLINICS_SOLUTION = PlatformSectorSolution(
    solution_id="hospitals_clinics",
    icon="🏥",
    title="Hospitais e Clínicas",
    description=(
        "Solução para recepção, agenda, fluxo de pacientes, "
        "documentos, prontuários, leitos, recursos, estoque, "
        "faturamento, qualidade e indicadores operacionais."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="healthcare_reception_access",
            title="👤 Atendimento e recepção",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_patient_registration",
                    title="👤 Cadastro administrativo de pacientes",
                    description=(
                        "Cadastro de pacientes, responsáveis, contatos, "
                        "documentos, preferências e dados administrativos."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_digital_reception",
                    title="🖥️ Recepção e direcionamento digital",
                    description=(
                        "Check-in, confirmação de dados, orientação "
                        "administrativa e direcionamento para atendimento."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "digital_experiences_intelligent_interfaces",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_patient_communication",
                    title="💬 Comunicação e suporte ao paciente",
                    description=(
                        "Mensagens, orientações administrativas, "
                        "confirmações, notificações e acompanhamento."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_schedule_patient_flow",
            title="📅 Agenda e fluxo de pacientes",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_intelligent_schedule",
                    title="📅 Agenda integrada de atendimentos",
                    description=(
                        "Agendamento de consultas, exames, procedimentos, "
                        "retornos, profissionais e salas."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "api_integrations_connectors",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_queue_flow_management",
                    title="🚶 Filas e fluxo de pacientes",
                    description=(
                        "Acompanhamento de filas, espera, chamadas, "
                        "movimentações e gargalos operacionais."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_capacity_coordination",
                    title="🏥 Coordenação de capacidade assistencial",
                    description=(
                        "Visão administrativa da capacidade, ocupação, "
                        "recursos disponíveis e demanda por atendimento."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "digital_twins_simulation",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_records_documents",
            title="📄 Documentos e prontuários",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_digital_records",
                    title="🗂️ Prontuários e registros digitais",
                    description=(
                        "Organização segura de registros, documentos, "
                        "históricos, anexos e dados relacionados."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "privacy_data_protection_lgpd",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_document_organization",
                    title="📑 Organização inteligente de documentos",
                    description=(
                        "Classificação, busca e organização assistida "
                        "de laudos, relatórios, exames e formulários."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_forms_consents",
                    title="✍️ Formulários, termos e consentimentos",
                    description=(
                        "Gestão de formulários, termos, assinaturas, "
                        "consentimentos e evidências documentais."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_beds_resources",
            title="🛏️ Leitos, salas e recursos",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_bed_capacity",
                    title="🛏️ Gestão de leitos e capacidade",
                    description=(
                        "Monitoramento de ocupação, disponibilidade, "
                        "reservas, movimentações e capacidade operacional."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "digital_twins_simulation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_rooms_equipment",
                    title="🏥 Salas, equipamentos e recursos",
                    description=(
                        "Gestão de salas, equipamentos, disponibilidade, "
                        "utilização, inspeções e manutenção."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "iot_edge_intelligence",
                        "digital_twins_simulation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_inventory_supplies",
            title="📦 Estoque, farmácia e suprimentos",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_supply_inventory",
                    title="📦 Estoque de materiais e suprimentos",
                    description=(
                        "Controle de materiais, insumos, entradas, "
                        "saídas, consumo, inventários e disponibilidade."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "supply_chain_procurement_logistics",
                        "data_traceability_provenance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_medication_traceability",
                    title="💊 Lotes, validade e rastreabilidade",
                    description=(
                        "Monitoramento administrativo de lotes, validade, "
                        "movimentações, disponibilidade e alertas."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                        "erp_business_operations",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_smart_replenishment",
                    title="🔄 Reposição inteligente de suprimentos",
                    description=(
                        "Previsão de consumo, pontos de reposição, "
                        "alertas e apoio ao planejamento de compras."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_billing_insurance",
            title="💰 Faturamento e convênios",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_billing_management",
                    title="💰 Faturamento administrativo",
                    description=(
                        "Organização de cobranças, contas, pagamentos, "
                        "recebimentos, conciliação e pendências."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "erp_business_operations",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_insurance_authorizations",
                    title="📋 Autorizações e convênios",
                    description=(
                        "Controle de solicitações, documentos, "
                        "autorizações, prazos e retornos de convênios."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "document_ai",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_quality_safety",
            title="✅ Qualidade, segurança e conformidade",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_quality_processes",
                    title="✅ Qualidade e processos assistenciais",
                    description=(
                        "Gestão de processos, checklists, auditorias, "
                        "evidências, melhorias e controles de qualidade."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "technology_governance_policy_compliance",
                        "ai_certification_system_evidence",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_incidents_risks",
                    title="⚠️ Incidentes, riscos e segurança",
                    description=(
                        "Registro e acompanhamento de ocorrências, "
                        "riscos operacionais, ações e evidências."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "responsible_ai_ethics_risk",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="healthcare_analytics_operations",
            title="📊 Indicadores operacionais",
            capabilities=(
                SectorCapability(
                    capability_id="healthcare_operational_indicators",
                    title="📊 Indicadores hospitalares e clínicos",
                    description=(
                        "Ocupação, espera, agenda, produtividade, "
                        "recursos, estoque e desempenho operacional."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="healthcare_demand_forecasting",
                    title="📈 Previsão de demanda e capacidade",
                    description=(
                        "Análise de padrões, sazonalidade, demanda "
                        "esperada e necessidades de capacidade."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "digital_twins_simulation",
                    ),
                ),
            ),
        ),
    ),
)


PLATFORM_SECTOR_SOLUTIONS: tuple[PlatformSectorSolution, ...] = (
    TRANSPORT_MOBILITY_SOLUTION,
    AGRIBUSINESS_SOLUTION,
    PET_SHOPS_VETERINARY_SOLUTION,
    SUPERMARKETS_WHOLESALE_SOLUTION,
    RETAIL_STORES_SOLUTION,
    DENTISTRY_SOLUTION,
    HOSPITALS_CLINICS_SOLUTION,
)


PLATFORM_SECTOR_SOLUTION_BY_ID = {
    solution.solution_id: solution for solution in PLATFORM_SECTOR_SOLUTIONS
}


def platform_sector_solution(
    solution_id: str,
) -> PlatformSectorSolution | None:
    """Retorna uma solução setorial pelo ID."""

    return PLATFORM_SECTOR_SOLUTION_BY_ID.get(solution_id)


def validate_platform_sector_solution_registry() -> None:
    """Valida o registro de soluções setoriais."""

    solution_ids = [solution.solution_id for solution in PLATFORM_SECTOR_SOLUTIONS]

    if len(solution_ids) != len(set(solution_ids)):
        raise ValueError("Existem soluções setoriais duplicadas.")

    for solution in PLATFORM_SECTOR_SOLUTIONS:
        if not solution.solution_id.strip():
            raise ValueError("Solução setorial com ID vazio.")

        if not solution.areas:
            raise ValueError(f"Solução setorial sem áreas: {solution.solution_id}")

        area_ids = [area.area_id for area in solution.areas]

        if len(area_ids) != len(set(area_ids)):
            raise ValueError(f"Áreas duplicadas em: {solution.solution_id}")

        capability_ids = [
            capability.capability_id
            for area in solution.areas
            for capability in area.capabilities
        ]

        if len(capability_ids) != len(set(capability_ids)):
            raise ValueError(f"Capacidades duplicadas em: {solution.solution_id}")

        for area in solution.areas:
            if not area.capabilities:
                raise ValueError(f"Área sem capacidades: {area.area_id}")

            for capability in area.capabilities:
                if not capability.technology_dependencies:
                    raise ValueError(
                        f"Capacidade sem dependências: {capability.capability_id}"
                    )

                missing_dependencies = {
                    dependency
                    for dependency in (capability.technology_dependencies)
                    if dependency not in PLATFORM_MODULE_BY_ID
                }

                if missing_dependencies:
                    raise ValueError(
                        "Dependências tecnológicas "
                        "inexistentes em "
                        f"{capability.capability_id}: "
                        f"{sorted(missing_dependencies)}"
                    )


validate_platform_sector_solution_registry()
