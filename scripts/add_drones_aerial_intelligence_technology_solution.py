"""Adiciona Drones e Inteligência Aérea ao registro tecnológico."""

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
        "drones_aerial_intelligence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


DRONES_AERIAL_INTELLIGENCE_DEFINITION = """
_DRONES_AERIAL_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "drones_aerial_intelligence"
    ]
)


DRONES_AERIAL_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="drones_aerial_intelligence",
        icon="🚁",
        title="Drones e Inteligência Aérea",
        description=(
            "Arquitetura tecnológica para planejamento de missões, "
            "gestão de frotas, captura aérea, sensores, processamento "
            "em edge, visão computacional, GeoAI, transmissão de "
            "eventos, segurança operacional, conformidade, "
            "observabilidade e ciclo de vida de operações aéreas."
        ),
        status=(
            _DRONES_AERIAL_INTELLIGENCE_MODULE.status
        ),
        integration_type=(
            _DRONES_AERIAL_INTELLIGENCE_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="drone_mission_fleet_management",
                title="🧭 Missões e gestão de frotas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_mission_planning",
                        title="🗺️ Planejamento de missões aéreas",
                        description=(
                            "Definição de áreas, rotas, altitude, "
                            "objetivos, restrições, horários, sensores "
                            "e critérios de conclusão da missão."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "geoai_earth_observation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_fleet_asset_registry",
                        title="🚁 Cadastro de drones e equipamentos",
                        description=(
                            "Registro de aeronaves, sensores, baterias, "
                            "controladores, versões, responsáveis "
                            "e condições operacionais."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "iot_edge_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_route_resource_optimization",
                        title="📈 Otimização de rotas e recursos",
                        description=(
                            "Otimização de trajetos, cobertura, duração, "
                            "energia, capacidade e utilização da frota."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "gis_location_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_sensor_data_acquisition",
                title="📷 Sensores e aquisição de dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_visual_sensor_capture",
                        title="📷 Captura visual e multiespectral",
                        description=(
                            "Aquisição de imagens, vídeos e bandas "
                            "espectrais com parâmetros e metadados "
                            "associados à missão."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_position_telemetry_capture",
                        title="📡 Posicionamento e telemetria",
                        description=(
                            "Coleta de localização, altitude, velocidade, "
                            "orientação, energia, conectividade "
                            "e estado dos equipamentos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_sensor_calibration_quality",
                        title="✅ Calibração e qualidade dos sensores",
                        description=(
                            "Validação de calibração, resolução, ruído, "
                            "sincronização, cobertura e integridade "
                            "das medições coletadas."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_bias_quality_monitoring",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_edge_onboard_intelligence",
                title="🧠 Inteligência embarcada e edge",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_onboard_inference",
                        title="🤖 Inferência embarcada",
                        description=(
                            "Execução local de modelos para classificação, "
                            "detecção, segmentação e análise durante "
                            "a operação aérea."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "computer_vision_video_analytics",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_edge_event_filtering",
                        title="⚡ Filtragem de eventos no edge",
                        description=(
                            "Seleção, priorização, compressão e envio "
                            "apenas de eventos e evidências relevantes."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "iot_edge_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_offline_resilient_operation",
                        title="📴 Operação resiliente sem conectividade",
                        description=(
                            "Continuidade controlada da missão, armazenamento "
                            "local e sincronização posterior quando "
                            "a conexão estiver disponível."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "iot_edge_intelligence",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_aerial_visual_geoanalytics",
                title="🛰️ Análise visual e geoespacial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_object_feature_detection",
                        title="🎯 Detecção de objetos e feições",
                        description=(
                            "Identificação de ativos, estruturas, áreas, "
                            "ocorrências e padrões relevantes "
                            "nas imagens aéreas."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "geoai_earth_observation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_mapping_orthomosaic_models",
                        title="🗺️ Mapas, ortomosaicos e modelos",
                        description=(
                            "Produção de mapas, mosaicos, modelos de "
                            "superfície, elevação e representações "
                            "georreferenciadas."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_change_inspection_analysis",
                        title="🔎 Inspeção e detecção de mudanças",
                        description=(
                            "Comparação de missões e períodos para detectar "
                            "alterações, danos, expansão, redução "
                            "e condições anormais."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "computer_vision_video_analytics",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_realtime_command_workflows",
                title="📡 Eventos e workflows operacionais",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_live_mission_monitoring",
                        title="📊 Monitoramento da missão em tempo real",
                        description=(
                            "Acompanhamento de posição, rota, bateria, "
                            "sensores, alertas, progresso e condições "
                            "da operação aérea."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "tools_analytics",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_event_alert_workflows",
                        title="🚨 Alertas e workflows de eventos",
                        description=(
                            "Acionamento de notificações, análises, APIs, "
                            "agentes e equipes após eventos detectados."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_human_control_escalation",
                        title="👤 Controle humano e escalonamento",
                        description=(
                            "Encaminhamento de decisões críticas, exceções "
                            "e situações incertas para operadores "
                            "devidamente autorizados."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "agent_process_orchestration",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_safety_security_compliance",
                title="🛡️ Segurança e conformidade operacional",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_geofence_airspace_rules",
                        title="🚧 Geofencing e restrições operacionais",
                        description=(
                            "Aplicação de limites geográficos, altitude, "
                            "horários, zonas restritas e regras "
                            "associadas à missão."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "technology_governance_policy_compliance",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_identity_access_security",
                        title="🔐 Identidade e proteção dos controles",
                        description=(
                            "Autenticação de operadores, aeronaves, "
                            "serviços e equipamentos, com controle "
                            "de comandos e permissões."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                            "cryptography_confidential_computing",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_ai_operational_safety",
                        title="🤖 Segurança dos modelos e automações",
                        description=(
                            "Validação de modelos, limites de automação, "
                            "ações permitidas, confiança e comportamento "
                            "durante as missões."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "responsible_ai_ethics_risk",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="drone_operations_lifecycle_governance",
                title="📊 Operações, governança e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="drone_maintenance_readiness",
                        title="🔧 Manutenção e prontidão operacional",
                        description=(
                            "Gestão de inspeções, ciclos, baterias, "
                            "calibrações, falhas, peças e disponibilidade "
                            "dos equipamentos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "digital_twins_simulation",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_data_audit_provenance",
                        title="🧾 Auditoria e proveniência dos dados",
                        description=(
                            "Registro de missão, equipamento, operador, "
                            "localização, captura, processamento, versão "
                            "e transformações realizadas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="drone_observability_cost_lifecycle",
                        title="📈 Observabilidade, custos e ciclo de vida",
                        description=(
                            "Monitoramento de uso, desempenho, falhas, "
                            "armazenamento, processamento, integrações, "
                            "custos e versões da solução."
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

    module_id = "drones_aerial_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        21: (147, 441),
        22: (154, 462),
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

    print("DRONES_AERIAL_INTELLIGENCE_PREREQUISITES=OK")


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

    if "DRONES_AERIAL_INTELLIGENCE_SOLUTION =" in source:
        print("DRONES_AERIAL_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        DRONES_AERIAL_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    GIS_LOCATION_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    DRONES_AERIAL_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("DRONES_AERIAL_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_drones_aerial_intelligence_is_complete" in source:
        print("DRONES_AERIAL_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "DRONES_AERIAL_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 21
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 22
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e uma soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_drones_aerial_intelligence_is_complete():
    assert (
        DRONES_AERIAL_INTELLIGENCE_SOLUTION.solution_id
        == "drones_aerial_intelligence"
    )

    assert len(
        DRONES_AERIAL_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        DRONES_AERIAL_INTELLIGENCE_SOLUTION.capability_count
        == 21
    )


def test_drones_aerial_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "drones_aerial_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        DRONES_AERIAL_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        DRONES_AERIAL_INTELLIGENCE_SOLUTION.integration_type
        == module.integration_type
    )


def test_drones_aerial_intelligence_lookup():
    assert (
        platform_technology_solution(
            "drones_aerial_intelligence"
        )
        is DRONES_AERIAL_INTELLIGENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("DRONES_AERIAL_INTELLIGENCE_TESTS_CREATED=OK")


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

    drone_solution = getattr(
        module,
        "DRONES_AERIAL_INTELLIGENCE_SOLUTION",
    )

    assert len(solutions) == 22
    assert len(drone_solution.areas) == 7
    assert drone_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 154
    assert total_capabilities == 462

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=22")
    print("TOTAL_TECHNOLOGY_AREAS=154")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=462")
    print("DRONES_AERIAL_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
