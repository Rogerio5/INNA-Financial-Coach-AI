"""Adiciona Computação Espacial e Realidade Aumentada ao registro."""

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
        "spatial_computing_augmented_reality_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


SPATIAL_COMPUTING_AUGMENTED_REALITY_DEFINITION = """
_SPATIAL_COMPUTING_AUGMENTED_REALITY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "spatial_computing_augmented_reality"
    ]
)


SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="spatial_computing_augmented_reality",
        icon="🥽",
        title="Computação Espacial e Realidade Aumentada",
        description=(
            "Arquitetura tecnológica para mapeamento espacial, "
            "ancoragem, compreensão de ambientes, conteúdo 3D, "
            "realidade aumentada, interação multimodal, colaboração, "
            "gêmeos digitais, processamento em edge, integração com "
            "workflows, privacidade, segurança e observabilidade."
        ),
        status=(
            _SPATIAL_COMPUTING_AUGMENTED_REALITY_MODULE.status
        ),
        integration_type=(
            _SPATIAL_COMPUTING_AUGMENTED_REALITY_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="spatial_mapping_scene_understanding",
                title="🗺️ Mapeamento e compreensão espacial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_environment_mapping",
                        title="📐 Mapeamento de ambientes",
                        description=(
                            "Construção de representações espaciais "
                            "de superfícies, objetos, distâncias, "
                            "profundidade e estruturas do ambiente."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_anchors_alignment",
                        title="📍 Âncoras e alinhamento espacial",
                        description=(
                            "Posicionamento persistente de conteúdos "
                            "digitais em coordenadas, superfícies, "
                            "objetos ou locais físicos."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "geoai_earth_observation",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_semantic_scene",
                        title="🧠 Compreensão semântica da cena",
                        description=(
                            "Identificação de objetos, regiões, relações, "
                            "contexto e significado dos elementos "
                            "presentes no ambiente."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "knowledge_graph_semantic_ai",
                            "multimodal_ai",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="augmented_reality_content_rendering",
                title="🎨 Conteúdo 3D e realidade aumentada",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ar_overlay_composition",
                        title="🖼️ Composição de sobreposições digitais",
                        description=(
                            "Combinação de informações, indicadores, "
                            "instruções e objetos digitais com "
                            "a visualização do ambiente físico."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "multimodal_ai",
                            "computer_vision_video_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_3d_content_rendering",
                        title="🧊 Renderização de conteúdo 3D",
                        description=(
                            "Apresentação de modelos, animações, "
                            "simulações e representações tridimensionais "
                            "com posicionamento espacial."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "cloud_devops_finops",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ar_device_display_adaptation",
                        title="📱 Adaptação a dispositivos e displays",
                        description=(
                            "Ajuste da experiência para celulares, "
                            "tablets, óculos, displays e diferentes "
                            "capacidades de processamento."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "digital_experiences_intelligent_interfaces",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="spatial_multimodal_interaction",
                title="🤝 Interação e presença multimodal",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_gesture_gaze_tracking",
                        title="👁️ Gestos, olhar e movimento",
                        description=(
                            "Interpretação de gestos, direção do olhar, "
                            "movimento corporal e interação com "
                            "elementos do ambiente."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_voice_commands",
                        title="🎙️ Voz e comandos multimodais",
                        description=(
                            "Controle da experiência por voz, linguagem "
                            "natural, gestos e contexto espacial."
                        ),
                        technology_dependencies=(
                            "voice_audio_speech_ai",
                            "multimodal_ai",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_shared_presence",
                        title="👥 Presença compartilhada e colaboração",
                        description=(
                            "Sincronização de usuários, posições, "
                            "anotações, objetos e interações em "
                            "experiências colaborativas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="spatial_context_location_intelligence",
                title="📍 Contexto e inteligência de localização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_location_context_fusion",
                        title="🧩 Fusão de localização e contexto",
                        description=(
                            "Combinação de localização, sensores, mapas, "
                            "objetos, histórico e condições do ambiente."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "iot_edge_intelligence",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_event_detection",
                        title="🚨 Detecção de eventos espaciais",
                        description=(
                            "Identificação de entrada, saída, aproximação, "
                            "movimento, alteração de cena e interação "
                            "com áreas ou objetos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "computer_vision_video_analytics",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_context_recommendations",
                        title="💡 Recomendações contextuais",
                        description=(
                            "Apresentação de orientações e informações "
                            "conforme localização, tarefa, ambiente, "
                            "perfil autorizado e evidências disponíveis."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "enterprise_rag",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="spatial_twins_simulation_training",
                title="🏭 Gêmeos digitais, simulação e treinamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_asset_twin_visualization",
                        title="🏭 Visualização de gêmeos digitais",
                        description=(
                            "Representação de equipamentos, instalações, "
                            "processos e ativos digitais alinhados "
                            "ao ambiente físico."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "iot_edge_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_scenario_simulation",
                        title="🧪 Simulação de cenários espaciais",
                        description=(
                            "Avaliação de alterações, movimentos, riscos, "
                            "rotas, posicionamentos e condições antes "
                            "da execução no ambiente real."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_training_remote_assistance",
                        title="🎓 Treinamento e assistência remota",
                        description=(
                            "Orientações visuais, procedimentos, "
                            "anotações compartilhadas e suporte remoto "
                            "durante atividades autorizadas."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "voice_audio_speech_ai",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="spatial_platform_delivery_integrations",
                title="⚙️ Plataforma, entrega e integrações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_edge_runtime",
                        title="📡 Runtime espacial em edge",
                        description=(
                            "Execução próxima ao dispositivo para reduzir "
                            "latência, manter contexto e permitir operação "
                            "com conectividade limitada."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_content_pipeline",
                        title="📦 Pipeline de conteúdo espacial",
                        description=(
                            "Versionamento, validação, transformação, "
                            "publicação e distribuição de modelos, "
                            "cenas, âncoras e experiências."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "software_supply_chain_security",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_api_workflow_integration",
                        title="🔌 APIs e workflows empresariais",
                        description=(
                            "Integração da experiência espacial com APIs, "
                            "agentes, sistemas, dados e processos "
                            "organizacionais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "agent_process_orchestration",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="spatial_safety_privacy_governance",
                title="🛡️ Segurança, privacidade e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="spatial_privacy_boundaries",
                        title="🔐 Privacidade e limites espaciais",
                        description=(
                            "Proteção de imagens, localização, ambientes, "
                            "pessoas, movimentos e informações sensíveis "
                            "capturadas pelos dispositivos."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_ai_content_safety",
                        title="🤖 Segurança da IA e do conteúdo",
                        description=(
                            "Validação de modelos, comandos, conteúdos, "
                            "ações, recomendações e objetos apresentados "
                            "na experiência espacial."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "responsible_ai_ethics_risk",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="spatial_observability_lifecycle",
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento de latência, erros, uso, "
                            "dispositivos, versões, eventos, qualidade, "
                            "custos e desempenho da experiência."
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

    module_id = "spatial_computing_augmented_reality"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        22: (154, 462),
        23: (161, 483),
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

    print("SPATIAL_COMPUTING_AUGMENTED_REALITY_PREREQUISITES=OK")


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

    if "SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION =" in source:
        print("SPATIAL_COMPUTING_AUGMENTED_REALITY_ALREADY_PRESENT=OK")
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
        SPATIAL_COMPUTING_AUGMENTED_REALITY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    DRONES_AERIAL_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_spatial_computing_augmented_reality_is_complete"

    if test_name in source:
        print("SPATIAL_COMPUTING_AUGMENTED_REALITY_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 22
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 23
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e duas soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_spatial_computing_augmented_reality_is_complete():
    assert (
        SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION.solution_id
        == "spatial_computing_augmented_reality"
    )

    assert len(
        SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION.areas
    ) == 7

    assert (
        SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION.capability_count
        == 21
    )


def test_spatial_computing_augmented_reality_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "spatial_computing_augmented_reality"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION.status
        is module.status
    )

    assert (
        SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION.integration_type
        == module.integration_type
    )


def test_spatial_computing_augmented_reality_lookup():
    assert (
        platform_technology_solution(
            "spatial_computing_augmented_reality"
        )
        is SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SPATIAL_COMPUTING_AUGMENTED_REALITY_TESTS_CREATED=OK")


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

    spatial_solution = getattr(
        module,
        "SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION",
    )

    assert len(solutions) == 23
    assert len(spatial_solution.areas) == 7

    assert spatial_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 161
    assert total_capabilities == 483

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=23")
    print("TOTAL_TECHNOLOGY_AREAS=161")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=483")
    print("SPATIAL_COMPUTING_AUGMENTED_REALITY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
