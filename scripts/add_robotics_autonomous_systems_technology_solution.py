"""Adiciona Robótica e Sistemas Autônomos ao registro tecnológico."""

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
        "robotics_autonomous_systems_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


ROBOTICS_AUTONOMOUS_SYSTEMS_DEFINITION = """
_ROBOTICS_AUTONOMOUS_SYSTEMS_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "robotics_autonomous_systems"
    ]
)


ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="robotics_autonomous_systems",
        icon="🤖",
        title="Robótica e Sistemas Autônomos",
        description=(
            "Arquitetura tecnológica para gestão de robôs, "
            "sensores, percepção, localização, navegação, "
            "planejamento, controle, coordenação de frotas, "
            "interação humana, simulação, segurança, resiliência, "
            "observabilidade e governança de sistemas autônomos."
        ),
        status=(
            _ROBOTICS_AUTONOMOUS_SYSTEMS_MODULE.status
        ),
        integration_type=(
            _ROBOTICS_AUTONOMOUS_SYSTEMS_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="robotics_assets_fleet_lifecycle",
                title="🗂️ Robôs, ativos e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="robotics_asset_fleet_registry",
                        title="🤖 Registro de robôs e frotas",
                        description=(
                            "Cadastro de robôs, manipuladores, veículos, "
                            "sensores, atuadores, controladores, versões, "
                            "localização e responsáveis."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "data_platform_governance",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_provisioning_configuration"
                        ),
                        title="⚙️ Provisionamento e configuração",
                        description=(
                            "Ativação segura, identificação, configuração, "
                            "calibração e autorização dos equipamentos "
                            "antes da entrada em operação."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "iot_edge_intelligence",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_maintenance_readiness"
                        ),
                        title="🔧 Manutenção e prontidão operacional",
                        description=(
                            "Gestão de inspeções, ciclos, componentes, "
                            "falhas, calibrações, peças, disponibilidade "
                            "e condições de operação."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "tools_analytics",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_perception_sensor_fusion",
                title="👁️ Percepção e fusão de sensores",
                capabilities=(
                    TechnologyCapability(
                        capability_id="robotics_visual_perception",
                        title="📷 Percepção visual",
                        description=(
                            "Detecção, classificação, segmentação "
                            "e rastreamento de objetos, pessoas, sinais "
                            "e estruturas presentes no ambiente."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="robotics_sensor_fusion",
                        title="📡 Fusão de sensores",
                        description=(
                            "Combinação de câmeras, profundidade, "
                            "posição, movimento, proximidade, áudio "
                            "e outros sinais disponíveis."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "iot_edge_intelligence",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_environment_understanding"
                        ),
                        title="🧠 Compreensão do ambiente",
                        description=(
                            "Construção de contexto sobre espaços, "
                            "obstáculos, áreas de trabalho, agentes, "
                            "objetos e condições operacionais."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "spatial_computing_augmented_reality",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_localization_navigation",
                title="🧭 Localização e navegação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="robotics_localization_slam",
                        title="🗺️ Localização e SLAM",
                        description=(
                            "Estimativa da posição e construção ou "
                            "atualização de mapas durante a movimentação "
                            "no ambiente."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "spatial_computing_augmented_reality",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="robotics_path_motion_planning",
                        title="🛣️ Planejamento de trajetórias",
                        description=(
                            "Cálculo de caminhos e movimentos conforme "
                            "destino, obstáculos, limites, prioridades "
                            "e condições do ambiente."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_geofencing_workspace_control"
                        ),
                        title="🚧 Geofencing e áreas operacionais",
                        description=(
                            "Definição de zonas permitidas, restritas, "
                            "compartilhadas ou críticas para movimentação "
                            "e realização das tarefas."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "real_time_event_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_planning_control_autonomy",
                title="⚙️ Planejamento, controle e autonomia",
                capabilities=(
                    TechnologyCapability(
                        capability_id="robotics_task_planning",
                        title="📋 Planejamento de tarefas",
                        description=(
                            "Decomposição de objetivos em etapas, ações, "
                            "recursos, dependências, prioridades "
                            "e critérios de conclusão."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "enterprise_decision_intelligence",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="robotics_motion_control",
                        title="🎛️ Controle de movimento e atuação",
                        description=(
                            "Conversão dos planos em comandos controlados "
                            "para motores, manipuladores, atuadores "
                            "e demais componentes físicos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "scientific_computing_engineering",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_multi_robot_coordination"
                        ),
                        title="🤝 Coordenação entre múltiplos robôs",
                        description=(
                            "Distribuição de tarefas, prevenção de conflitos, "
                            "compartilhamento de estado e sincronização "
                            "entre diferentes equipamentos."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "real_time_event_intelligence",
                            "simulation_optimization_operations_research",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_human_interaction_collaboration",
                title="👥 Interação e colaboração humana",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "robotics_voice_gesture_interaction"
                        ),
                        title="🎙️ Voz, gestos e interação multimodal",
                        description=(
                            "Interpretação de voz, comandos, gestos, "
                            "movimentos e sinais visuais para interação "
                            "com operadores autorizados."
                        ),
                        technology_dependencies=(
                            "voice_audio_speech_ai",
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="robotics_human_supervision",
                        title="👤 Supervisão e intervenção humana",
                        description=(
                            "Acompanhamento das ações e possibilidade "
                            "de aprovação, pausa, correção, cancelamento "
                            "ou retomada segura da operação."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "agent_process_orchestration",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_collaborative_workflows"
                        ),
                        title="🤝 Workflows colaborativos",
                        description=(
                            "Coordenação entre pessoas, robôs, agentes, "
                            "sistemas empresariais e processos físicos "
                            "durante a execução das atividades."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_safety_security_resilience",
                title="🛡️ Segurança e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="robotics_safety_guardrails",
                        title="🚨 Guardrails de segurança física",
                        description=(
                            "Aplicação de limites de velocidade, força, "
                            "área, distância, movimento, operação "
                            "e interrupção de emergência."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "real_time_event_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_identity_command_security"
                        ),
                        title="🔐 Identidade e proteção de comandos",
                        description=(
                            "Autenticação de equipamentos e operadores, "
                            "autorização de comandos e proteção contra "
                            "ações ou alterações indevidas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cryptography_confidential_computing",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="robotics_fault_recovery",
                        title="♻️ Detecção de falhas e recuperação",
                        description=(
                            "Identificação de falhas, entrada em estado "
                            "seguro, isolamento, recuperação, rollback "
                            "e encaminhamento para manutenção."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "iot_edge_intelligence",
                            "digital_twins_simulation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="robotics_operations_governance_lifecycle",
                title="📊 Operações, governança e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "robotics_telemetry_observability"
                        ),
                        title="📊 Telemetria e observabilidade",
                        description=(
                            "Monitoramento de estados, trajetórias, "
                            "comandos, erros, latência, energia, utilização, "
                            "eventos e disponibilidade dos equipamentos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_simulation_validation"
                        ),
                        title="🧪 Simulação e validação",
                        description=(
                            "Validação de comportamentos, rotas, tarefas, "
                            "falhas, interações e limites de segurança "
                            "antes da operação física."
                        ),
                        technology_dependencies=(
                            "digital_twins_simulation",
                            "simulation_optimization_operations_research",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "robotics_governance_audit_lifecycle"
                        ),
                        title="🧾 Governança, auditoria e versionamento",
                        description=(
                            "Registro de modelos, software, configurações, "
                            "comandos, responsáveis, decisões, intervenções "
                            "e evidências da operação."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "software_supply_chain_security",
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

    module_id = "robotics_autonomous_systems"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        25: (175, 525),
        26: (182, 546),
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

    print("ROBOTICS_AUTONOMOUS_SYSTEMS_PREREQUISITES=OK")


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
    """Adiciona Robótica e Sistemas Autônomos."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION =" in source:
        print("ROBOTICS_AUTONOMOUS_SYSTEMS_ALREADY_PRESENT=OK")
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
        ROBOTICS_AUTONOMOUS_SYSTEMS_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    DIGITAL_TWINS_SIMULATION_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_robotics_autonomous_systems_is_complete" in source:
        print("ROBOTICS_AUTONOMOUS_SYSTEMS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 25
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 26
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e cinco soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_robotics_autonomous_systems_is_complete():
    assert (
        ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION.solution_id
        == "robotics_autonomous_systems"
    )

    assert len(
        ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION.areas
    ) == 7

    assert (
        ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION.capability_count
        == 21
    )


def test_robotics_autonomous_systems_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "robotics_autonomous_systems"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION.status
        is module.status
    )

    assert (
        ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION.integration_type
        == module.integration_type
    )


def test_robotics_autonomous_systems_lookup():
    assert (
        platform_technology_solution(
            "robotics_autonomous_systems"
        )
        is ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ROBOTICS_AUTONOMOUS_SYSTEMS_TESTS_CREATED=OK")


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

    robotics_solution = getattr(
        module,
        "ROBOTICS_AUTONOMOUS_SYSTEMS_SOLUTION",
    )

    assert len(solutions) == 26
    assert len(robotics_solution.areas) == 7

    assert robotics_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 182
    assert total_capabilities == 546

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=26")
    print("TOTAL_TECHNOLOGY_AREAS=182")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=546")
    print("ROBOTICS_AUTONOMOUS_SYSTEMS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
