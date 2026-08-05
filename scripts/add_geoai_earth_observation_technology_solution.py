"""Adiciona GeoAI e Observação da Terra ao registro tecnológico."""

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
    / ("geoai_earth_observation_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


GEOAI_EARTH_OBSERVATION_DEFINITION = """
_GEOAI_EARTH_OBSERVATION_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "geoai_earth_observation"
    ]
)


GEOAI_EARTH_OBSERVATION_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="geoai_earth_observation",
        icon="🛰️",
        title="GeoAI e Observação da Terra",
        description=(
            "Arquitetura tecnológica para ingestão, preparação, "
            "análise e distribuição de imagens orbitais, dados "
            "geoespaciais, mapas, sensores e séries temporais, "
            "com visão computacional, detecção de mudanças, "
            "modelagem espacial, alertas, governança, "
            "observabilidade e apoio à decisão."
        ),
        status=(
            _GEOAI_EARTH_OBSERVATION_MODULE.status
        ),
        integration_type=(
            _GEOAI_EARTH_OBSERVATION_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="geoai_sources_ingestion",
                title="📥 Fontes e ingestão geoespacial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_satellite_imagery_ingestion",
                        title="🛰️ Imagens orbitais e sensoriamento remoto",
                        description=(
                            "Recebimento de imagens de satélite, "
                            "produtos de observação da Terra, bandas "
                            "espectrais e metadados associados."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_drone_sensor_ingestion",
                        title="🚁 Drones, sensores e imagens aéreas",
                        description=(
                            "Integração de imagens aéreas, sensores, "
                            "dispositivos de campo e eventos produzidos "
                            "por equipamentos autorizados."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_gis_data_connectors",
                        title="🗺️ Conectores GIS e dados territoriais",
                        description=(
                            "Ingestão de camadas vetoriais, rasters, "
                            "limites, pontos, linhas, polígonos "
                            "e bases territoriais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_preprocessing_georeferencing",
                title="🧭 Preparação e georreferenciamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_coordinate_reference_systems",
                        title="🌐 Sistemas de coordenadas e projeções",
                        description=(
                            "Padronização, transformação e validação "
                            "de coordenadas, projeções e referências "
                            "espaciais."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_image_correction_mosaics",
                        title="🖼️ Correção, recorte e mosaicos",
                        description=(
                            "Correção geométrica e radiométrica, "
                            "recorte por área de interesse e combinação "
                            "de cenas georreferenciadas."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_quality_cloud_masking",
                        title="☁️ Qualidade, nuvens e dados ausentes",
                        description=(
                            "Identificação de nuvens, sombras, ruídos, "
                            "lacunas, baixa qualidade e outras condições "
                            "que afetam a análise."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "data_traceability_provenance",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_visual_analysis",
                title="👁️ Análise visual e territorial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_land_cover_classification",
                        title="🌱 Classificação de cobertura terrestre",
                        description=(
                            "Classificação assistida de vegetação, água, "
                            "solo, áreas construídas e outras coberturas."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_object_feature_detection",
                        title="🎯 Detecção de objetos e feições",
                        description=(
                            "Identificação de estruturas, vias, áreas, "
                            "cultivos, ativos e feições relevantes "
                            "nas imagens."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "iot_edge_intelligence",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_change_detection",
                        title="🔄 Detecção de mudanças territoriais",
                        description=(
                            "Comparação de períodos para identificar "
                            "mudanças, expansão, redução, transformação "
                            "e eventos espaciais."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "computer_vision_video_analytics",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_spatial_analytics",
                title="📐 Analytics e modelagem espacial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_spatial_joins_geofencing",
                        title="📍 Junções espaciais e geofencing",
                        description=(
                            "Relacionamento de dados por localização, "
                            "proximidade, interseção, contenção "
                            "e entrada ou saída de áreas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "data_platform_governance",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_terrain_network_analysis",
                        title="⛰️ Terreno, rotas e redes espaciais",
                        description=(
                            "Análise de elevação, declividade, distância, "
                            "acessibilidade, rotas e conexões territoriais."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "digital_twins_simulation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_spatiotemporal_analytics",
                        title="⏱️ Análise espaço-temporal",
                        description=(
                            "Estudo de padrões, tendências e eventos "
                            "considerando simultaneamente localização "
                            "e período."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "real_time_event_intelligence",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_intelligence_decision",
                title="🧠 Inteligência geoespacial e decisão",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_embeddings_semantic_search",
                        title="🔎 Embeddings e pesquisa geoespacial",
                        description=(
                            "Recuperação de imagens, regiões, documentos "
                            "e entidades usando similaridade, localização "
                            "e contexto semântico."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "multimodal_ai",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_predictive_modeling",
                        title="📈 Modelagem preditiva espacial",
                        description=(
                            "Estimativa de tendências, ocorrência, "
                            "distribuição e evolução de fenômenos "
                            "territoriais."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_risk_priority_decisions",
                        title="🚨 Risco e priorização territorial",
                        description=(
                            "Classificação de áreas, eventos e ativos "
                            "conforme risco, impacto, urgência, evidências "
                            "e nível de confiança."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_serving_visualization_workflows",
                title="🗺️ Mapas, visualização e workflows",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_map_tiles_services",
                        title="🗺️ Mapas, tiles e serviços geoespaciais",
                        description=(
                            "Disponibilização de mapas, camadas, tiles, "
                            "consultas e resultados por interfaces "
                            "e serviços controlados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "cloud_devops_finops",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_dashboards_digital_twins",
                        title="📊 Dashboards e gêmeos digitais",
                        description=(
                            "Visualização de indicadores, ativos, eventos, "
                            "cenários e condições territoriais em mapas "
                            "interativos."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "digital_twins_simulation",
                            "data_bi_copilot",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_alerts_automated_workflows",
                        title="🔔 Alertas e workflows geoespaciais",
                        description=(
                            "Acionamento de notificações, agentes, APIs "
                            "e processos após eventos ou mudanças "
                            "detectadas no território."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="geoai_governance_operations",
                title="🛡️ Governança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="geoai_access_privacy_security",
                        title="🔐 Acesso, privacidade e segurança",
                        description=(
                            "Controle de usuários, áreas restritas, "
                            "fontes, camadas, coordenadas e informações "
                            "territoriais sensíveis."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_catalog_provenance",
                        title="🧾 Catálogo, metadados e proveniência",
                        description=(
                            "Registro de origem, aquisição, processamento, "
                            "resolução, período, versão e transformações "
                            "dos dados geoespaciais."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="geoai_observability_lifecycle",
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento de pipelines, processamento, "
                            "latência, custos, qualidade, versões, "
                            "publicação e atualização dos produtos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
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

    module_id = "geoai_earth_observation"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        19: (133, 399),
        20: (140, 420),
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

    print("GEOAI_EARTH_OBSERVATION_PREREQUISITES=OK")


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

    if "GEOAI_EARTH_OBSERVATION_SOLUTION =" in source:
        print("GEOAI_EARTH_OBSERVATION_ALREADY_PRESENT=OK")
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
        GEOAI_EARTH_OBSERVATION_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    PRIVACY_ENHANCING_TECHNOLOGIES_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    GEOAI_EARTH_OBSERVATION_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("GEOAI_EARTH_OBSERVATION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_geoai_earth_observation_is_complete" in source:
        print("GEOAI_EARTH_OBSERVATION_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "GEOAI_EARTH_OBSERVATION_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 19
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 20
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de dezenove soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_geoai_earth_observation_is_complete():
    assert (
        GEOAI_EARTH_OBSERVATION_SOLUTION.solution_id
        == "geoai_earth_observation"
    )

    assert len(
        GEOAI_EARTH_OBSERVATION_SOLUTION.areas
    ) == 7

    assert (
        GEOAI_EARTH_OBSERVATION_SOLUTION.capability_count
        == 21
    )


def test_geoai_earth_observation_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "geoai_earth_observation"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        GEOAI_EARTH_OBSERVATION_SOLUTION.status
        is module.status
    )

    assert (
        GEOAI_EARTH_OBSERVATION_SOLUTION.integration_type
        == module.integration_type
    )


def test_geoai_earth_observation_lookup():
    assert (
        platform_technology_solution(
            "geoai_earth_observation"
        )
        is GEOAI_EARTH_OBSERVATION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("GEOAI_EARTH_OBSERVATION_TESTS_CREATED=OK")


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

    geoai_solution = getattr(
        module,
        "GEOAI_EARTH_OBSERVATION_SOLUTION",
    )

    assert len(solutions) == 20
    assert len(geoai_solution.areas) == 7

    assert geoai_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 140
    assert total_capabilities == 420

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=20")
    print("TOTAL_TECHNOLOGY_AREAS=140")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=420")
    print("GEOAI_EARTH_OBSERVATION_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
