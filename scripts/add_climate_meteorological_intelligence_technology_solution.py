"""Adiciona Inteligência Climática e Meteorológica ao registro."""

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
        "climate_meteorological_intelligence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


CLIMATE_METEOROLOGICAL_INTELLIGENCE_DEFINITION = """
_CLIMATE_METEOROLOGICAL_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "climate_meteorological_intelligence"
    ]
)


CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="climate_meteorological_intelligence",
        icon="🌦️",
        title="Inteligência Climática e Meteorológica",
        description=(
            "Arquitetura tecnológica para integração de observações "
            "meteorológicas, satélites, radares e sensores, controle "
            "de qualidade, previsão numérica, nowcasting, análise "
            "climática, eventos extremos, riscos territoriais, "
            "alertas, APIs, visualização, governança, rastreabilidade "
            "e operação de serviços climáticos."
        ),
        status=(
            _CLIMATE_METEOROLOGICAL_INTELLIGENCE_MODULE.status
        ),
        integration_type=(
            _CLIMATE_METEOROLOGICAL_INTELLIGENCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="climate_observation_data_sources",
                title="📡 Observações e fontes meteorológicas",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_station_sensor_ingestion"
                        ),
                        title="🌡️ Estações e sensores meteorológicos",
                        description=(
                            "Ingestão de temperatura, umidade, pressão, "
                            "vento, precipitação, radiação e demais "
                            "variáveis observadas por sensores."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_satellite_radar_ingestion"
                        ),
                        title="🛰️ Satélites e radares meteorológicos",
                        description=(
                            "Integração de imagens, produtos derivados, "
                            "estimativas de precipitação, nuvens, "
                            "tempestades e estruturas atmosféricas."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_external_data_connectors"
                        ),
                        title="🔌 APIs e fontes meteorológicas externas",
                        description=(
                            "Conectores para serviços, modelos, boletins, "
                            "dados históricos, observações públicas "
                            "e fornecedores meteorológicos autorizados."
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
                area_id="climate_data_quality_harmonization",
                title="✅ Qualidade e harmonização dos dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_observation_quality_control"
                        ),
                        title="✅ Controle de qualidade meteorológica",
                        description=(
                            "Validação de limites, consistência temporal, "
                            "continuidade, valores ausentes, duplicidades, "
                            "anomalias e falhas instrumentais."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "software_testing_quality_reliability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_spatiotemporal_harmonization"
                        ),
                        title="🗺️ Harmonização espaço-temporal",
                        description=(
                            "Alinhamento de coordenadas, resoluções, "
                            "intervalos de tempo, unidades, grades "
                            "e diferentes fontes de observação."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "scientific_computing_engineering",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_metadata_provenance"
                        ),
                        title="🧾 Metadados e proveniência",
                        description=(
                            "Registro da fonte, instrumento, processamento, "
                            "resolução, cobertura, versão, horário "
                            "e transformações aplicadas aos dados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="weather_forecasting_nowcasting",
                title="🌦️ Previsão meteorológica e nowcasting",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "weather_numerical_forecast_models"
                        ),
                        title="🧮 Modelos numéricos de previsão",
                        description=(
                            "Processamento e integração de previsões "
                            "atmosféricas com diferentes horizontes, "
                            "resoluções, membros e cenários."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "weather_short_term_nowcasting"
                        ),
                        title="⏱️ Nowcasting de curto prazo",
                        description=(
                            "Estimativas de evolução imediata de chuva, "
                            "tempestades, vento, granizo, descargas "
                            "e outras condições meteorológicas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "computer_vision_video_analytics",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "weather_ensemble_probabilistic_forecast"
                        ),
                        title="🎲 Previsão probabilística e ensembles",
                        description=(
                            "Análise de múltiplas execuções e cenários "
                            "para produzir probabilidades, intervalos "
                            "e níveis de confiança das previsões."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="climate_analysis_scenarios",
                title="🌍 Clima, tendências e cenários",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_historical_baselines"
                        ),
                        title="📊 Climatologia e linhas de base",
                        description=(
                            "Cálculo de médias, percentis, sazonalidade, "
                            "normais climatológicas e referências "
                            "históricas para regiões e períodos."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "scientific_computing_engineering",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_trends_anomalies"
                        ),
                        title="📈 Tendências e anomalias climáticas",
                        description=(
                            "Identificação de alterações persistentes, "
                            "desvios, extremos, padrões recorrentes "
                            "e mudanças nas séries climáticas."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "model_explainability_interpretability",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_scenario_downscaling"
                        ),
                        title="🗺️ Cenários e regionalização climática",
                        description=(
                            "Tratamento de projeções e cenários climáticos "
                            "com adaptação de escala para territórios, "
                            "setores, ativos e operações."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "gis_location_intelligence",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="climate_extreme_events_risk",
                title="⚠️ Eventos extremos e inteligência de risco",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_extreme_event_detection"
                        ),
                        title="🚨 Detecção de eventos extremos",
                        description=(
                            "Identificação de chuvas intensas, secas, "
                            "ondas de calor ou frio, vendavais, tempestades "
                            "e outras condições potencialmente críticas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_hazard_exposure_mapping"
                        ),
                        title="🗺️ Mapeamento de perigo e exposição",
                        description=(
                            "Combinação de ameaças meteorológicas com "
                            "territórios, infraestrutura, população, "
                            "ativos e recursos potencialmente expostos."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "geoai_earth_observation",
                            "environmental_natural_resources_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_impact_risk_assessment"
                        ),
                        title="📉 Avaliação de impactos e riscos",
                        description=(
                            "Estimativa de probabilidade, severidade, "
                            "vulnerabilidade, consequências operacionais "
                            "e prioridades de resposta."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "simulation_optimization_operations_research",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="climate_alerts_decision_services",
                title="📣 Alertas e serviços de decisão",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_threshold_alerting"
                        ),
                        title="🔔 Alertas por limites e probabilidades",
                        description=(
                            "Geração de alertas conforme valores observados, "
                            "previsões, probabilidades, localização, "
                            "duração e níveis de severidade."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "business_automation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_operational_recommendations"
                        ),
                        title="💡 Recomendações meteorológicas operacionais",
                        description=(
                            "Produção de orientações para planejamento, "
                            "proteção de ativos, mobilização de equipes "
                            "e continuidade das operações."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "agent_process_orchestration",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_api_products_delivery"
                        ),
                        title="🔌 APIs, mapas e produtos meteorológicos",
                        description=(
                            "Entrega de previsões, indicadores, alertas, "
                            "mapas, séries, boletins e dados processados "
                            "para aplicações e usuários autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "digital_experiences_intelligent_interfaces",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="climate_operations_governance",
                title="🛡️ Operações, governança e confiabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "climate_pipeline_observability"
                        ),
                        title="📊 Observabilidade dos pipelines",
                        description=(
                            "Monitoramento de ingestões, atrasos, falhas, "
                            "qualidade, previsões, jobs, APIs, recursos "
                            "e disponibilidade dos serviços."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_model_validation_audit"
                        ),
                        title="✅ Validação e auditoria dos modelos",
                        description=(
                            "Comparação entre previsões e observações, "
                            "avaliação de métricas, vieses, versões, "
                            "mudanças e desempenho por região."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_bias_quality_monitoring",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "climate_resilience_security_governance"
                        ),
                        title="🔐 Segurança, resiliência e governança",
                        description=(
                            "Controle de acesso, proteção de integrações, "
                            "continuidade operacional, políticas, retenção "
                            "e rastreabilidade das informações climáticas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "technology_governance_policy_compliance",
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

    module_id = "climate_meteorological_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        31: (217, 651),
        32: (224, 672),
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

    print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_PREREQUISITES=OK")


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
    """Adiciona Inteligência Climática e Meteorológica."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION =" in source:
        print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    CONSTRUCTION_BIM_DIGITAL_ENGINEERING_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_climate_meteorological_intelligence_is_complete"

    if test_name in source:
        print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 31
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 32
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e uma soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_climate_meteorological_intelligence_is_complete():
    assert (
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION.solution_id
        == "climate_meteorological_intelligence"
    )

    assert len(
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION
        .capability_count
        == 21
    )


def test_climate_meteorological_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "climate_meteorological_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_climate_meteorological_intelligence_lookup():
    assert (
        platform_technology_solution(
            "climate_meteorological_intelligence"
        )
        is CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_TESTS_CREATED=OK")


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

    climate_solution = getattr(
        module,
        "CLIMATE_METEOROLOGICAL_INTELLIGENCE_SOLUTION",
    )

    assert len(solutions) == 32
    assert len(climate_solution.areas) == 7

    assert climate_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 224
    assert total_capabilities == 672

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=32")
    print("TOTAL_TECHNOLOGY_AREAS=224")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=672")
    print("CLIMATE_METEOROLOGICAL_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
