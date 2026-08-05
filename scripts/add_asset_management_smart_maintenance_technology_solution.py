"""Adiciona Gestão de Ativos e Manutenção Inteligente ao registro."""

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
        "asset_management_smart_maintenance_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


ASSET_MANAGEMENT_SMART_MAINTENANCE_DEFINITION = """
_ASSET_MANAGEMENT_SMART_MAINTENANCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "asset_management_smart_maintenance"
    ]
)


ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="asset_management_smart_maintenance",
        icon="🛠️",
        title="Gestão de Ativos e Manutenção Inteligente",
        description=(
            "Arquitetura tecnológica para cadastro, hierarquia, "
            "criticidade, localização e ciclo de vida de ativos, "
            "sensoriamento, monitoramento de condição, diagnóstico, "
            "manutenção preditiva, planejamento, ordens de serviço, "
            "equipes de campo, peças, custos, confiabilidade, "
            "segurança, governança e observabilidade operacional."
        ),
        status=(
            _ASSET_MANAGEMENT_SMART_MAINTENANCE_MODULE.status
        ),
        integration_type=(
            _ASSET_MANAGEMENT_SMART_MAINTENANCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="asset_registry_hierarchy_criticality",
                title="🗂️ Cadastro, hierarquia e criticidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="asset_master_registry",
                        title="📋 Cadastro mestre de ativos",
                        description=(
                            "Registro de equipamentos, máquinas, veículos, "
                            "instalações, componentes, fabricantes, modelos, "
                            "números de série, localização e responsáveis."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "gis_location_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_hierarchy_relationships",
                        title="🔗 Hierarquias e relações dos ativos",
                        description=(
                            "Representação de sistemas, subsistemas, "
                            "componentes, dependências, conexões, funções "
                            "e relações entre ativos físicos e digitais."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "digital_twins_simulation",
                            "construction_bim_digital_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_criticality_risk_classification",
                        title="⚠️ Criticidade e classificação de risco",
                        description=(
                            "Classificação conforme impacto operacional, "
                            "segurança, custo, ambiente, disponibilidade, "
                            "redundância e consequências de falha."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "operational_security_resilience",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="asset_condition_monitoring_telemetry",
                title="📡 Condição, sensores e telemetria",
                capabilities=(
                    TechnologyCapability(
                        capability_id="asset_sensor_telemetry_ingestion",
                        title="📨 Sensores e telemetria de ativos",
                        description=(
                            "Ingestão de temperatura, vibração, pressão, "
                            "corrente, tensão, ruído, velocidade, posição, "
                            "consumo, estado e demais sinais operacionais."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_health_condition_indicators",
                        title="🩺 Indicadores de saúde e condição",
                        description=(
                            "Cálculo de indicadores de desgaste, condição, "
                            "desempenho, utilização, degradação e saúde "
                            "dos equipamentos e componentes."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_visual_thermal_inspection",
                        title="📷 Inspeção visual e térmica",
                        description=(
                            "Análise de imagens e vídeos para identificar "
                            "trincas, corrosão, vazamentos, aquecimento, "
                            "desalinhamento e outras condições aparentes."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "multimodal_ai",
                            "drones_aerial_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="asset_predictive_diagnostics",
                title="🔮 Diagnóstico e manutenção preditiva",
                capabilities=(
                    TechnologyCapability(
                        capability_id="asset_anomaly_fault_detection",
                        title="🚨 Detecção de anomalias e falhas",
                        description=(
                            "Identificação de desvios, padrões incomuns, "
                            "falhas emergentes e alterações relevantes "
                            "nos dados e no comportamento dos ativos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_failure_prediction",
                        title="📉 Previsão de falhas e vida útil",
                        description=(
                            "Estimativa de probabilidade de falha, tempo "
                            "remanescente de uso, degradação e necessidade "
                            "provável de intervenção."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_root_cause_diagnostics",
                        title="🔎 Diagnóstico e análise de causa",
                        description=(
                            "Correlação de sintomas, alarmes, intervenções, "
                            "condições operacionais, histórico e relações "
                            "para apoiar a investigação das causas."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="maintenance_planning_optimization",
                title="📅 Planejamento e otimização da manutenção",
                capabilities=(
                    TechnologyCapability(
                        capability_id="maintenance_strategy_planning",
                        title="🧭 Estratégias de manutenção",
                        description=(
                            "Definição de estratégias preventivas, "
                            "preditivas, corretivas e baseadas em condição "
                            "conforme criticidade, risco e desempenho."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="maintenance_schedule_optimization",
                        title="📆 Otimização de programação",
                        description=(
                            "Planejamento de intervenções conforme janelas, "
                            "prioridades, equipes, duração, disponibilidade, "
                            "dependências e impacto sobre as operações."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "business_automation",
                            "agent_process_orchestration",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="maintenance_spare_parts_optimization",
                        title="📦 Peças e materiais de manutenção",
                        description=(
                            "Previsão e otimização de estoques, peças, "
                            "materiais, ferramentas, reposição, consumo "
                            "e disponibilidade para as intervenções."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "simulation_optimization_operations_research",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="maintenance_work_orders_field_operations",
                title="👷 Ordens de serviço e operações de campo",
                capabilities=(
                    TechnologyCapability(
                        capability_id="maintenance_work_order_orchestration",
                        title="📋 Orquestração de ordens de serviço",
                        description=(
                            "Criação, priorização, aprovação, atribuição, "
                            "execução, encerramento e integração das ordens "
                            "de manutenção com sistemas corporativos."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="maintenance_mobile_field_assistance",
                        title="📱 Assistência móvel em campo",
                        description=(
                            "Disponibilização de atividades, documentos, "
                            "checklists, histórico, evidências, apontamentos "
                            "e instruções para equipes autorizadas."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="maintenance_remote_expert_guidance",
                        title="🥽 Orientação remota e realidade aumentada",
                        description=(
                            "Apoio remoto com vídeo, áudio, documentos, "
                            "marcação espacial e instruções contextuais "
                            "para inspeções e intervenções autorizadas."
                        ),
                        technology_dependencies=(
                            "spatial_computing_augmented_reality",
                            "multimodal_ai",
                            "voice_audio_speech_ai",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="asset_lifecycle_performance_sustainability",
                title="📈 Ciclo de vida, desempenho e sustentabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="asset_lifecycle_cost_performance",
                        title="💰 Custos e desempenho do ciclo de vida",
                        description=(
                            "Acompanhamento de aquisição, utilização, "
                            "manutenção, indisponibilidade, modernização, "
                            "substituição e descarte dos ativos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_energy_environmental_efficiency",
                        title="🌱 Eficiência energética e ambiental",
                        description=(
                            "Monitoramento de consumo, perdas, eficiência, "
                            "emissões associadas, resíduos e impactos "
                            "ambientais durante o ciclo de vida."
                        ),
                        technology_dependencies=(
                            "energy_smart_grids",
                            "esg_sustainability",
                            "environmental_natural_resources_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_reliability_availability_metrics",
                        title="✅ Confiabilidade e disponibilidade",
                        description=(
                            "Cálculo de disponibilidade, confiabilidade, "
                            "tempo entre falhas, tempo de reparo, paradas, "
                            "produtividade e nível de serviço."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "tools_analytics",
                            "scientific_computing_engineering",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="asset_governance_security_observability",
                title="🛡️ Governança, segurança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="maintenance_policy_compliance",
                        title="⚖️ Políticas e conformidade de manutenção",
                        description=(
                            "Controle de planos, procedimentos, inspeções, "
                            "certificações, frequências, aprovações, "
                            "requisitos e evidências operacionais."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_ot_security_access",
                        title="🔐 Segurança e acesso aos ativos conectados",
                        description=(
                            "Proteção de dispositivos, comandos, operadores, "
                            "redes, integrações e dados relacionados "
                            "a ativos industriais ou operacionais."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                            "networks_telecommunications_connectivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="asset_observability_audit_provenance",
                        title="📊 Observabilidade e auditoria dos ativos",
                        description=(
                            "Monitoramento de sensores, modelos, alertas, "
                            "ordens, intervenções, integrações, custos, "
                            "acessos, versões e resultados operacionais."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "data_traceability_provenance",
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

    module_id = "asset_management_smart_maintenance"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        40: (280, 840),
        41: (287, 861),
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

    print("ASSET_MANAGEMENT_SMART_MAINTENANCE_PREREQUISITES=OK")


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
    """Adiciona Gestão de Ativos e Manutenção Inteligente."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION =" in source:
        print("ASSET_MANAGEMENT_SMART_MAINTENANCE_ALREADY_PRESENT=OK")
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
        ASSET_MANAGEMENT_SMART_MAINTENANCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    NAVIGATION_POSITIONING_GEOLOCATION_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_asset_management_smart_maintenance_is_complete"

    if test_name in source:
        print("ASSET_MANAGEMENT_SMART_MAINTENANCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 40
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 41
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quarenta soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_asset_management_smart_maintenance_is_complete():
    assert (
        ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION.solution_id
        == "asset_management_smart_maintenance"
    )

    assert len(
        ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION.areas
    ) == 7

    assert (
        ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION
        .capability_count
        == 21
    )


def test_asset_management_smart_maintenance_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "asset_management_smart_maintenance"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION.status
        is module.status
    )

    assert (
        ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_asset_management_smart_maintenance_lookup():
    assert (
        platform_technology_solution(
            "asset_management_smart_maintenance"
        )
        is ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ASSET_MANAGEMENT_SMART_MAINTENANCE_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    asset_solution = module.ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION

    assert len(solutions) == 41
    assert len(asset_solution.areas) == 7
    assert asset_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 287
    assert total_capabilities == 861

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=41")
    print("TOTAL_TECHNOLOGY_AREAS=287")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=861")
    print("ASSET_MANAGEMENT_SMART_MAINTENANCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
