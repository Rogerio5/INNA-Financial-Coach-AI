"""Adiciona GIS e Inteligência de Localização ao registro tecnológico."""

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
        "gis_location_intelligence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


GIS_LOCATION_INTELLIGENCE_DEFINITION = """
_GIS_LOCATION_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "gis_location_intelligence"
    ]
)


GIS_LOCATION_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="gis_location_intelligence",
        icon="📍",
        title="GIS e Inteligência de Localização",
        description=(
            "Arquitetura tecnológica para ingestão, organização, "
            "geocodificação, consulta, análise e visualização de "
            "dados geográficos, endereços, territórios, rotas, "
            "eventos e ativos, com geofencing, inteligência "
            "espaço-temporal, APIs, governança, segurança, "
            "observabilidade e apoio à decisão."
        ),
        status=(
            _GIS_LOCATION_INTELLIGENCE_MODULE.status
        ),
        integration_type=(
            _GIS_LOCATION_INTELLIGENCE_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="gis_location_data_foundation",
                title="🗂️ Dados e fundamentos geográficos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_spatial_data_ingestion",
                        title="📥 Ingestão de dados espaciais",
                        description=(
                            "Recebimento de pontos, linhas, polígonos, "
                            "rasters, endereços, coordenadas, limites "
                            "territoriais e metadados geográficos."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_spatial_reference_management",
                        title="🌐 Sistemas de referência espacial",
                        description=(
                            "Gestão de coordenadas, projeções, escalas, "
                            "unidades, transformações e compatibilidade "
                            "entre diferentes fontes geográficas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_spatial_catalog_metadata",
                        title="🧾 Catálogo e metadados geográficos",
                        description=(
                            "Registro de origem, cobertura, precisão, "
                            "resolução, período, responsável, licença "
                            "e versão das camadas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="gis_geocoding_address_intelligence",
                title="🏠 Geocodificação e endereços",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_forward_geocoding",
                        title="📍 Geocodificação de endereços",
                        description=(
                            "Conversão de endereços, estabelecimentos "
                            "e referências territoriais em coordenadas "
                            "geográficas verificáveis."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_reverse_geocoding",
                        title="🏠 Geocodificação reversa",
                        description=(
                            "Conversão de coordenadas em endereços, "
                            "regiões administrativas, locais próximos "
                            "e referências territoriais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "geoai_earth_observation",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_address_normalization_quality",
                        title="✅ Normalização e qualidade de endereços",
                        description=(
                            "Padronização, validação, deduplicação "
                            "e enriquecimento de endereços incompletos, "
                            "inconsistentes ou ambíguos."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "enterprise_rag",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="gis_spatial_queries_analytics",
                title="🔎 Consultas e analytics espaciais",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_spatial_relationship_queries",
                        title="🔗 Relações e consultas espaciais",
                        description=(
                            "Consultas por interseção, proximidade, "
                            "contenção, sobreposição, vizinhança "
                            "e distância entre entidades."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_spatial_aggregation_hotspots",
                        title="🔥 Agregações e hotspots",
                        description=(
                            "Identificação de concentrações, densidades, "
                            "clusters, padrões territoriais e regiões "
                            "com maior ocorrência de eventos."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_spatiotemporal_analysis",
                        title="⏱️ Análise espaço-temporal",
                        description=(
                            "Avaliação de eventos e indicadores conforme "
                            "localização, período, sequência, frequência "
                            "e evolução territorial."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "tools_analytics",
                            "geoai_earth_observation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="gis_routes_proximity_accessibility",
                title="🛣️ Rotas, proximidade e acessibilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_route_calculation",
                        title="🛣️ Cálculo e comparação de rotas",
                        description=(
                            "Cálculo de caminhos conforme distância, "
                            "tempo, restrições, prioridades e condições "
                            "operacionais disponíveis."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_service_area_analysis",
                        title="🗺️ Áreas de cobertura e atendimento",
                        description=(
                            "Determinação de áreas alcançáveis, regiões "
                            "de atendimento, tempos de deslocamento "
                            "e cobertura de serviços."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_nearest_resource_search",
                        title="🎯 Busca por recursos próximos",
                        description=(
                            "Localização de unidades, ativos, equipes, "
                            "serviços ou pontos de interesse mais próximos "
                            "de uma posição ou ocorrência."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "api_integrations_connectors",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="gis_geofencing_location_events",
                title="🚨 Geofencing e eventos de localização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_geofence_management",
                        title="🧭 Gestão de geofences",
                        description=(
                            "Criação e versionamento de áreas virtuais "
                            "com regras, horários, prioridades, entidades "
                            "e finalidades associadas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "data_platform_governance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_entry_exit_dwell_events",
                        title="📡 Entrada, saída e permanência",
                        description=(
                            "Detecção de entrada, saída, permanência, "
                            "aproximação ou movimentação em regiões "
                            "geográficas monitoradas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "iot_edge_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_location_event_workflows",
                        title="⚡ Workflows orientados por localização",
                        description=(
                            "Acionamento de alertas, agentes, APIs, "
                            "tarefas e processos com base em eventos "
                            "de localização autorizados."
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
                area_id="gis_maps_location_experiences",
                title="🗺️ Mapas e experiências de localização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_interactive_maps_layers",
                        title="🗺️ Mapas e camadas interativas",
                        description=(
                            "Exibição de camadas, marcadores, regiões, "
                            "rotas, eventos, filtros e indicadores "
                            "em interfaces geográficas."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_location_dashboards",
                        title="📊 Dashboards territoriais",
                        description=(
                            "Acompanhamento de indicadores, ocorrências, "
                            "ativos, cobertura, risco e desempenho "
                            "por território."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_bi_copilot",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_location_api_services",
                        title="🌐 APIs e serviços de localização",
                        description=(
                            "Disponibilização controlada de geocodificação, "
                            "rotas, proximidade, camadas, consultas "
                            "e eventos geográficos."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "cloud_devops_finops",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="gis_governance_security_operations",
                title="🛡️ Governança, segurança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="gis_location_privacy_access",
                        title="🔐 Privacidade e acesso geográfico",
                        description=(
                            "Controle de acesso a coordenadas, trajetos, "
                            "endereços, áreas sensíveis, ativos "
                            "e dados de localização."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_spatial_quality_audit",
                        title="🧪 Qualidade e auditoria espacial",
                        description=(
                            "Validação de precisão, completude, atualidade, "
                            "consistência, origem e transformações "
                            "dos dados geográficos."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="gis_observability_scalability",
                        title="📊 Observabilidade e escalabilidade",
                        description=(
                            "Monitoramento de consultas, tiles, APIs, "
                            "latência, erros, armazenamento, utilização "
                            "e custos dos serviços geográficos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "tools_analytics",
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

    module_id = "gis_location_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        20: (140, 420),
        21: (147, 441),
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

    print("GIS_LOCATION_INTELLIGENCE_PREREQUISITES=OK")


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
    """Adiciona a solução ao registro tecnológico."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "GIS_LOCATION_INTELLIGENCE_SOLUTION =" in source:
        print("GIS_LOCATION_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        GIS_LOCATION_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    GEOAI_EARTH_OBSERVATION_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    GIS_LOCATION_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("GIS_LOCATION_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_gis_location_intelligence_is_complete" in source:
        print("GIS_LOCATION_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "GIS_LOCATION_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 20
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 21
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_gis_location_intelligence_is_complete():
    assert (
        GIS_LOCATION_INTELLIGENCE_SOLUTION.solution_id
        == "gis_location_intelligence"
    )

    assert len(
        GIS_LOCATION_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        GIS_LOCATION_INTELLIGENCE_SOLUTION.capability_count
        == 21
    )


def test_gis_location_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "gis_location_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        GIS_LOCATION_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        GIS_LOCATION_INTELLIGENCE_SOLUTION.integration_type
        == module.integration_type
    )


def test_gis_location_intelligence_lookup():
    assert (
        platform_technology_solution(
            "gis_location_intelligence"
        )
        is GIS_LOCATION_INTELLIGENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("GIS_LOCATION_INTELLIGENCE_TESTS_CREATED=OK")


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

    gis_solution = getattr(
        module,
        "GIS_LOCATION_INTELLIGENCE_SOLUTION",
    )

    assert len(solutions) == 21
    assert len(gis_solution.areas) == 7
    assert gis_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 147
    assert total_capabilities == 441

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=21")
    print("TOTAL_TECHNOLOGY_AREAS=147")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=441")
    print("GIS_LOCATION_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
