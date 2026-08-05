"""Adiciona Gestão de Emergências e Desastres ao registro tecnológico."""

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
        "emergency_disaster_management_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


EMERGENCY_DISASTER_MANAGEMENT_DEFINITION = """
_EMERGENCY_DISASTER_MANAGEMENT_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "emergency_disaster_management"
    ]
)


EMERGENCY_DISASTER_MANAGEMENT_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="emergency_disaster_management",
        icon="🚨",
        title="Gestão de Emergências e Desastres",
        description=(
            "Arquitetura tecnológica para identificação de ameaças, "
            "avaliação de riscos, preparação, monitoramento contínuo, "
            "alerta antecipado, comando de incidentes, coordenação "
            "de equipes, logística, evacuação, abrigos, comunicação "
            "pública, avaliação de danos, recuperação, governança, "
            "rastreabilidade e resiliência operacional."
        ),
        status=(
            _EMERGENCY_DISASTER_MANAGEMENT_MODULE.status
        ),
        integration_type=(
            _EMERGENCY_DISASTER_MANAGEMENT_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="disaster_risk_preparedness",
                title="⚠️ Riscos, cenários e preparação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_hazard_inventory",
                        title="🗺️ Inventário de ameaças e perigos",
                        description=(
                            "Registro de enchentes, incêndios, tempestades, "
                            "deslizamentos, secas, falhas de infraestrutura "
                            "e outras ameaças naturais ou operacionais."
                        ),
                        technology_dependencies=(
                            "climate_meteorological_intelligence",
                            "environmental_natural_resources_intelligence",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_risk_vulnerability_mapping",
                        title="📍 Mapeamento de risco e vulnerabilidade",
                        description=(
                            "Combinação de ameaças, exposição, população, "
                            "ativos, infraestrutura, vulnerabilidades "
                            "e capacidade territorial de resposta."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_preparedness_scenarios",
                        title="🧪 Cenários e planos de preparação",
                        description=(
                            "Simulação de ocorrências, impactos, recursos, "
                            "rotas, prioridades, tempos de resposta "
                            "e medidas preventivas."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="disaster_monitoring_early_warning",
                title="📡 Monitoramento e alerta antecipado",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_sensor_event_monitoring",
                        title="📡 Sensores e eventos em tempo real",
                        description=(
                            "Ingestão de sensores ambientais, dispositivos, "
                            "estações, equipamentos, sistemas externos "
                            "e eventos relacionados a possíveis incidentes."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_remote_observation",
                        title="🛰️ Observação remota e inteligência visual",
                        description=(
                            "Uso de satélites, drones, imagens e vídeos "
                            "para identificar mudanças, focos, alagamentos, "
                            "danos e áreas potencialmente afetadas."
                        ),
                        technology_dependencies=(
                            "geoai_earth_observation",
                            "drones_aerial_intelligence",
                            "computer_vision_video_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_early_warning_alerts",
                        title="🔔 Alertas antecipados",
                        description=(
                            "Geração de alertas conforme limites, previsões, "
                            "probabilidades, localização, velocidade "
                            "de evolução e níveis de severidade."
                        ),
                        technology_dependencies=(
                            "climate_meteorological_intelligence",
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="incident_command_coordination",
                title="🎛️ Comando e coordenação de incidentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id="incident_command_structure",
                        title="👥 Estrutura de comando do incidente",
                        description=(
                            "Definição de coordenação, funções, responsáveis, "
                            "áreas de atuação, níveis de autoridade "
                            "e regras de escalonamento."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "agent_process_orchestration",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="incident_common_operational_picture",
                        title="🗺️ Visão operacional compartilhada",
                        description=(
                            "Consolidação de mapas, ocorrências, equipes, "
                            "ativos, riscos, bloqueios, vítimas, recursos "
                            "e evolução da resposta."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "tools_analytics",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="incident_multichannel_coordination",
                        title="🔌 Coordenação multicanal",
                        description=(
                            "Integração de APIs, sistemas, agentes, equipes, "
                            "mensagens, notificações e fluxos operacionais "
                            "durante a resposta."
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
                area_id="disaster_response_resources_logistics",
                title="🚚 Recursos, equipes e logística",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_resource_inventory",
                        title="📦 Inventário de recursos de resposta",
                        description=(
                            "Registro de equipes, veículos, equipamentos, "
                            "suprimentos, instalações, capacidades, "
                            "localização e disponibilidade."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "gis_location_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_resource_allocation",
                        title="📈 Alocação e priorização de recursos",
                        description=(
                            "Distribuição de equipes e recursos conforme "
                            "severidade, distância, capacidade, prioridade, "
                            "restrições e tempo esperado de resposta."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_response_routing",
                        title="🛣️ Rotas e logística emergencial",
                        description=(
                            "Planejamento de trajetos considerando bloqueios, "
                            "riscos, acessos, localização das equipes, "
                            "abrigos e condições territoriais."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "simulation_optimization_operations_research",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="evacuation_shelters_public_communication",
                title="📣 Evacuação, abrigos e comunicação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_evacuation_planning",
                        title="🚶 Planejamento de evacuação",
                        description=(
                            "Definição de áreas, rotas, pontos de encontro, "
                            "prioridades, meios de transporte, capacidade "
                            "e condições de segurança."
                        ),
                        technology_dependencies=(
                            "gis_location_intelligence",
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_shelter_management",
                        title="🏠 Gestão de abrigos e atendimento",
                        description=(
                            "Acompanhamento de capacidade, ocupação, recursos, "
                            "necessidades, equipes, registros, encaminhamentos "
                            "e condições operacionais dos abrigos."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_public_communication",
                        title="📢 Comunicação pública acessível",
                        description=(
                            "Produção e distribuição de alertas, instruções, "
                            "boletins e atualizações por texto, voz "
                            "e diferentes canais autorizados."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "voice_audio_speech_ai",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="damage_assessment_recovery",
                title="🏚️ Danos, recuperação e reconstrução",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_damage_assessment",
                        title="🔎 Avaliação de danos e impactos",
                        description=(
                            "Identificação e classificação de danos em áreas, "
                            "edificações, redes, ativos, ambiente "
                            "e serviços essenciais."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "drones_aerial_intelligence",
                            "construction_bim_digital_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_recovery_prioritization",
                        title="📋 Priorização da recuperação",
                        description=(
                            "Definição de prioridades conforme criticidade, "
                            "população afetada, dependências, custos, riscos "
                            "e capacidade disponível."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "simulation_optimization_operations_research",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_reconstruction_monitoring",
                        title="🏗️ Reconstrução e acompanhamento",
                        description=(
                            "Monitoramento de planos, obras, recursos, "
                            "prazos, custos, entregas, riscos e recuperação "
                            "dos serviços e ativos afetados."
                        ),
                        technology_dependencies=(
                            "construction_bim_digital_engineering",
                            "digital_twins_simulation",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="disaster_governance_resilience_operations",
                title="🛡️ Governança, resiliência e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="disaster_protocol_compliance",
                        title="⚖️ Protocolos e conformidade",
                        description=(
                            "Organização e verificação de protocolos, planos, "
                            "níveis de resposta, aprovações, responsabilidades "
                            "e requisitos aplicáveis."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_audit_after_action_review",
                        title="🧾 Auditoria e revisão pós-incidente",
                        description=(
                            "Registro de eventos, decisões, comunicações, "
                            "ações, responsáveis, tempos, resultados, "
                            "falhas e oportunidades de melhoria."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "tools_analytics",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="disaster_operational_observability",
                        title="📊 Observabilidade e continuidade",
                        description=(
                            "Monitoramento de integrações, alertas, mapas, "
                            "workflows, recursos, erros, disponibilidade, "
                            "custos e segurança dos serviços."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "operational_security_resilience",
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

    module_id = "emergency_disaster_management"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        35: (245, 735),
        36: (252, 756),
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

    print("EMERGENCY_DISASTER_MANAGEMENT_PREREQUISITES=OK")


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
    """Adiciona Gestão de Emergências e Desastres."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "EMERGENCY_DISASTER_MANAGEMENT_SOLUTION =" in source:
        print("EMERGENCY_DISASTER_MANAGEMENT_ALREADY_PRESENT=OK")
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
        EMERGENCY_DISASTER_MANAGEMENT_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ESG_SUSTAINABILITY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    EMERGENCY_DISASTER_MANAGEMENT_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("EMERGENCY_DISASTER_MANAGEMENT_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_emergency_disaster_management_is_complete"

    if test_name in source:
        print("EMERGENCY_DISASTER_MANAGEMENT_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "EMERGENCY_DISASTER_MANAGEMENT_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 35
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 36
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e cinco soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_emergency_disaster_management_is_complete():
    assert (
        EMERGENCY_DISASTER_MANAGEMENT_SOLUTION.solution_id
        == "emergency_disaster_management"
    )

    assert len(
        EMERGENCY_DISASTER_MANAGEMENT_SOLUTION.areas
    ) == 7

    assert (
        EMERGENCY_DISASTER_MANAGEMENT_SOLUTION.capability_count
        == 21
    )


def test_emergency_disaster_management_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "emergency_disaster_management"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        EMERGENCY_DISASTER_MANAGEMENT_SOLUTION.status
        is module.status
    )

    assert (
        EMERGENCY_DISASTER_MANAGEMENT_SOLUTION.integration_type
        == module.integration_type
    )


def test_emergency_disaster_management_lookup():
    assert (
        platform_technology_solution(
            "emergency_disaster_management"
        )
        is EMERGENCY_DISASTER_MANAGEMENT_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("EMERGENCY_DISASTER_MANAGEMENT_TESTS_CREATED=OK")


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

    emergency_solution = getattr(
        module,
        "EMERGENCY_DISASTER_MANAGEMENT_SOLUTION",
    )

    assert len(solutions) == 36
    assert len(emergency_solution.areas) == 7

    assert emergency_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 252
    assert total_capabilities == 756

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=36")
    print("TOTAL_TECHNOLOGY_AREAS=252")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=756")
    print("EMERGENCY_DISASTER_MANAGEMENT_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
