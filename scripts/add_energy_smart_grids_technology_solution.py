"""Adiciona Energia e Redes Elétricas Inteligentes ao registro."""

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
    / ("energy_smart_grids_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


ENERGY_SMART_GRIDS_DEFINITION = """
_ENERGY_SMART_GRIDS_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "energy_smart_grids"
    ]
)


ENERGY_SMART_GRIDS_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="energy_smart_grids",
        icon="⚡",
        title="Energia e Redes Elétricas Inteligentes",
        description=(
            "Arquitetura tecnológica para ativos e topologia "
            "de redes elétricas, medidores e sensores conectados, "
            "telemetria, previsão de demanda e geração, fluxo "
            "de potência, despacho, resposta da demanda, recursos "
            "energéticos distribuídos, armazenamento, veículos "
            "elétricos, confiabilidade, segurança cibernética, "
            "governança, custos e observabilidade operacional."
        ),
        status=(
            _ENERGY_SMART_GRIDS_MODULE.status
        ),
        integration_type=(
            _ENERGY_SMART_GRIDS_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="energy_grid_assets_topology",
                title="🗺️ Ativos e topologia da rede",
                capabilities=(
                    TechnologyCapability(
                        capability_id="energy_grid_asset_registry",
                        title="🗂️ Registro de ativos elétricos",
                        description=(
                            "Cadastro de subestações, linhas, circuitos, "
                            "transformadores, medidores, dispositivos, "
                            "geradores, cargas e responsáveis."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "digital_twins_simulation",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_grid_topology_connectivity"
                        ),
                        title="🔗 Topologia e conectividade elétrica",
                        description=(
                            "Representação de barras, alimentadores, "
                            "conexões, dependências, localização, "
                            "hierarquias e estados da rede."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "gis_location_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_grid_model_versioning"
                        ),
                        title="🔄 Versionamento dos modelos da rede",
                        description=(
                            "Controle de versões, alterações, aprovações, "
                            "configurações, parâmetros, responsáveis "
                            "e histórico dos modelos elétricos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_telemetry_edge_state",
                title="📡 Telemetria, edge e estado da rede",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "energy_meter_sensor_ingestion"
                        ),
                        title="📨 Medidores, sensores e telemetria",
                        description=(
                            "Ingestão de tensão, corrente, potência, "
                            "frequência, energia, qualidade, estado "
                            "de equipamentos e eventos operacionais."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_edge_control_runtime"
                        ),
                        title="⚙️ Processamento e controle em edge",
                        description=(
                            "Execução próxima aos ativos para filtragem, "
                            "agregação, detecção de eventos e ações "
                            "de baixa latência dentro de limites seguros."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_data_quality_state_estimation"
                        ),
                        title="✅ Qualidade e estimação de estado",
                        description=(
                            "Validação de medições, tratamento de falhas, "
                            "reconciliação de dados e estimativa "
                            "das condições operacionais da rede."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "ai_bias_quality_monitoring",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_forecasting_scenarios",
                title="🔮 Previsão e cenários energéticos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "energy_load_demand_forecasting"
                        ),
                        title="📈 Previsão de carga e demanda",
                        description=(
                            "Estimativa da demanda por região, circuito, "
                            "período, perfil de consumo e condições "
                            "operacionais ou meteorológicas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "climate_meteorological_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_renewable_generation_forecasting"
                        ),
                        title="☀️ Previsão de geração renovável",
                        description=(
                            "Estimativa de geração solar, eólica, hídrica "
                            "e outras fontes conforme clima, ambiente, "
                            "capacidade e condições dos ativos."
                        ),
                        technology_dependencies=(
                            "climate_meteorological_intelligence",
                            "environmental_natural_resources_intelligence",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_probabilistic_scenarios"
                        ),
                        title="🎲 Cenários probabilísticos e incerteza",
                        description=(
                            "Construção de cenários para variações "
                            "de demanda, geração, preços, disponibilidade, "
                            "falhas e condições externas."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "model_explainability_interpretability",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_grid_operations_optimization",
                title="⚙️ Operação e otimização da rede",
                capabilities=(
                    TechnologyCapability(
                        capability_id="energy_power_flow_analysis",
                        title="🧮 Fluxo de potência e análise elétrica",
                        description=(
                            "Cálculo de fluxos, tensões, carregamentos, "
                            "perdas, limites, contingências e estados "
                            "operacionais da rede elétrica."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "digital_twins_simulation",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_dispatch_optimization"
                        ),
                        title="📈 Despacho e otimização operacional",
                        description=(
                            "Otimização da utilização de geração, cargas, "
                            "armazenamento e recursos da rede conforme "
                            "custos, limites e confiabilidade."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_demand_response_automation"
                        ),
                        title="⚡ Resposta da demanda",
                        description=(
                            "Coordenação de reduções, deslocamentos "
                            "ou ajustes de consumo conforme eventos, "
                            "tarifas, restrições e acordos autorizados."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_distributed_resources_storage",
                title="🔋 Recursos distribuídos e armazenamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "energy_distributed_resources_orchestration"
                        ),
                        title="☀️ Orquestração de recursos distribuídos",
                        description=(
                            "Coordenação de geração local, microrredes, "
                            "prosumidores, dispositivos controláveis "
                            "e recursos energéticos distribuídos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_storage_optimization"
                        ),
                        title="🔋 Otimização de armazenamento",
                        description=(
                            "Planejamento de carga, descarga, reserva, "
                            "degradação, disponibilidade e utilização "
                            "de sistemas de armazenamento energético."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_ev_charging_coordination"
                        ),
                        title="🚗 Coordenação de recarga elétrica",
                        description=(
                            "Planejamento de pontos, horários, potência, "
                            "prioridades, capacidade disponível e impactos "
                            "da recarga de veículos elétricos."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "business_automation",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_reliability_security_resilience",
                title="🛡️ Confiabilidade, segurança e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "energy_outage_fault_detection"
                        ),
                        title="🚨 Detecção de falhas e interrupções",
                        description=(
                            "Identificação de desligamentos, anomalias, "
                            "sobrecargas, variações, falhas de equipamentos "
                            "e eventos que afetem o fornecimento."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_grid_resilience_recovery"
                        ),
                        title="♻️ Resiliência e recuperação da rede",
                        description=(
                            "Simulação e coordenação de isolamento, "
                            "reconfiguração, restauração, contingência "
                            "e continuidade dos serviços energéticos."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "digital_twins_simulation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_ot_identity_cybersecurity"
                        ),
                        title="🔐 Segurança cibernética e identidade OT",
                        description=(
                            "Proteção de dispositivos, comandos, sistemas "
                            "de controle, operadores, integrações "
                            "e comunicações da infraestrutura elétrica."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                            "cryptography_confidential_computing",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="energy_governance_markets_operations",
                title="📊 Governança, custos e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "energy_market_tariff_cost_analysis"
                        ),
                        title="💰 Tarifas, mercados e custos",
                        description=(
                            "Análise de preços, tarifas, contratos, custos "
                            "operacionais, consumo, capacidade, eficiência "
                            "e alternativas econômicas."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "cloud_devops_finops",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_environmental_performance_reporting"
                        ),
                        title="🌱 Desempenho ambiental e energético",
                        description=(
                            "Acompanhamento de eficiência, perdas, fontes, "
                            "consumo, emissões associadas, impactos "
                            "ambientais e indicadores territoriais."
                        ),
                        technology_dependencies=(
                            "environmental_natural_resources_intelligence",
                            "climate_meteorological_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "energy_observability_compliance_audit"
                        ),
                        title="🧾 Observabilidade, conformidade e auditoria",
                        description=(
                            "Monitoramento de ativos, integrações, modelos, "
                            "eventos, qualidade, custos, acessos, decisões, "
                            "versões e evidências operacionais."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "technology_governance_policy_compliance",
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

    module_id = "energy_smart_grids"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        33: (231, 693),
        34: (238, 714),
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

    print("ENERGY_SMART_GRIDS_PREREQUISITES=OK")


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
    """Adiciona Energia e Redes Elétricas Inteligentes."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ENERGY_SMART_GRIDS_SOLUTION =" in source:
        print("ENERGY_SMART_GRIDS_ALREADY_PRESENT=OK")
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
        ENERGY_SMART_GRIDS_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ENVIRONMENTAL_NATURAL_RESOURCES_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ENERGY_SMART_GRIDS_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ENERGY_SMART_GRIDS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_energy_smart_grids_is_complete" in source:
        print("ENERGY_SMART_GRIDS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "ENERGY_SMART_GRIDS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 33
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 34
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e três soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_energy_smart_grids_is_complete():
    assert (
        ENERGY_SMART_GRIDS_SOLUTION.solution_id
        == "energy_smart_grids"
    )

    assert len(
        ENERGY_SMART_GRIDS_SOLUTION.areas
    ) == 7

    assert (
        ENERGY_SMART_GRIDS_SOLUTION.capability_count
        == 21
    )


def test_energy_smart_grids_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "energy_smart_grids"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ENERGY_SMART_GRIDS_SOLUTION.status
        is module.status
    )

    assert (
        ENERGY_SMART_GRIDS_SOLUTION.integration_type
        == module.integration_type
    )


def test_energy_smart_grids_lookup():
    assert (
        platform_technology_solution(
            "energy_smart_grids"
        )
        is ENERGY_SMART_GRIDS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ENERGY_SMART_GRIDS_TESTS_CREATED=OK")


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

    energy_solution = getattr(
        module,
        "ENERGY_SMART_GRIDS_SOLUTION",
    )

    assert len(solutions) == 34
    assert len(energy_solution.areas) == 7

    assert energy_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 238
    assert total_capabilities == 714

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=34")
    print("TOTAL_TECHNOLOGY_AREAS=238")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=714")
    print("ENERGY_SMART_GRIDS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
