"""Adiciona Gêmeos Digitais e Simulação ao registro tecnológico."""

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
        "digital_twins_simulation_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


DIGITAL_TWINS_SIMULATION_DEFINITION = """
_DIGITAL_TWINS_SIMULATION_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "digital_twins_simulation"
    ]
)


DIGITAL_TWINS_SIMULATION_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="digital_twins_simulation",
        icon="🏭",
        title="Gêmeos Digitais e Simulação",
        description=(
            "Arquitetura tecnológica para representar ativos, "
            "processos, instalações e ambientes físicos em modelos "
            "digitais conectados, com telemetria, sincronização, "
            "simulação de cenários, previsão, otimização, "
            "visualização, automação, governança, segurança "
            "e observabilidade operacional."
        ),
        status=(
            _DIGITAL_TWINS_SIMULATION_MODULE.status
        ),
        integration_type=(
            _DIGITAL_TWINS_SIMULATION_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="digital_twin_asset_modeling",
                title="🏗️ Modelagem de ativos e processos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_asset_registry",
                        title="🗂️ Registro de ativos físicos e digitais",
                        description=(
                            "Cadastro de máquinas, equipamentos, "
                            "instalações, componentes, sensores, "
                            "responsáveis e representações digitais."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "iot_edge_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_relationship_model",
                        title="🔗 Relações, hierarquias e dependências",
                        description=(
                            "Representação de componentes, conexões, "
                            "localizações, processos, fluxos "
                            "e dependências entre os ativos."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_state_model",
                        title="📊 Estados e propriedades operacionais",
                        description=(
                            "Definição de estados, propriedades, limites, "
                            "modos de operação, configurações "
                            "e condições esperadas dos ativos."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="digital_twin_data_synchronization",
                title="📡 Telemetria e sincronização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_telemetry_ingestion",
                        title="📨 Ingestão de telemetria",
                        description=(
                            "Recebimento contínuo de medições, eventos, "
                            "estados, comandos e informações operacionais "
                            "provenientes dos ativos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_state_synchronization",
                        title="🔄 Sincronização físico-digital",
                        description=(
                            "Atualização controlada da representação "
                            "digital conforme mudanças observadas "
                            "nos ativos e ambientes físicos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "data_traceability_provenance",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_data_quality",
                        title="✅ Qualidade e reconciliação dos dados",
                        description=(
                            "Validação de completude, sequência, precisão, "
                            "atualidade, consistência e divergências "
                            "entre fontes e estados."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "software_testing_quality_reliability",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="digital_twin_simulation_scenarios",
                title="🧪 Simulação e análise de cenários",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_scenario_definition",
                        title="🧭 Definição de cenários",
                        description=(
                            "Configuração de condições iniciais, "
                            "variáveis, eventos, restrições, objetivos "
                            "e hipóteses para execução das simulações."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_discrete_continuous_simulation",
                        title="⚙️ Simulação discreta e contínua",
                        description=(
                            "Representação de eventos, fluxos, estados "
                            "e comportamentos que evoluem ao longo "
                            "do tempo simulado."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "real_time_event_intelligence",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_monte_carlo_sensitivity",
                        title="📈 Incerteza e análise de sensibilidade",
                        description=(
                            "Avaliação de variações, probabilidades, "
                            "incertezas e influência das entradas "
                            "sobre os resultados simulados."
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
                area_id="digital_twin_prediction_optimization",
                title="🧠 Previsão e otimização",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_predictive_models",
                        title="🔮 Modelos preditivos dos ativos",
                        description=(
                            "Estimativa de estados futuros, degradação, "
                            "falhas, consumo, capacidade e comportamento "
                            "dos ativos e processos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "scientific_computing_engineering",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_operational_optimization",
                        title="📈 Otimização operacional",
                        description=(
                            "Busca de configurações, sequências, recursos "
                            "e decisões que melhorem desempenho, qualidade, "
                            "custos ou utilização."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_recommendations",
                        title="💡 Recomendações assistidas",
                        description=(
                            "Produção de recomendações fundamentadas "
                            "em telemetria, previsões, simulações, "
                            "restrições e níveis de confiança."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="digital_twin_visualization_interaction",
                title="🖥️ Visualização e interação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_operational_dashboards",
                        title="📊 Dashboards dos gêmeos digitais",
                        description=(
                            "Visualização de estados, indicadores, "
                            "eventos, riscos, alertas e tendências "
                            "dos ativos representados."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_bi_copilot",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_3d_spatial_views",
                        title="🧊 Visualização 3D e espacial",
                        description=(
                            "Representação de ativos, ambientes, "
                            "componentes, relações e estados "
                            "em experiências tridimensionais."
                        ),
                        technology_dependencies=(
                            "spatial_computing_augmented_reality",
                            "gis_location_intelligence",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_collaborative_analysis",
                        title="👥 Análise colaborativa",
                        description=(
                            "Compartilhamento de cenários, anotações, "
                            "resultados, hipóteses e decisões entre "
                            "usuários autorizados."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "api_integrations_connectors",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="digital_twin_automation_workflows",
                title="⚡ Automação e integração operacional",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_event_workflows",
                        title="🚨 Workflows orientados por eventos",
                        description=(
                            "Acionamento de tarefas, alertas, análises, "
                            "agentes e processos quando estados "
                            "ou condições relevantes forem detectados."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_control_recommendation",
                        title="🎛️ Recomendações e comandos controlados",
                        description=(
                            "Geração ou encaminhamento de comandos "
                            "dentro de limites, permissões, aprovações "
                            "e condições operacionais definidas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "zero_trust_identity_access",
                            "iot_edge_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_system_integrations",
                        title="🔌 Integrações com sistemas e ativos",
                        description=(
                            "Integração com APIs, dispositivos, bancos, "
                            "sistemas empresariais, plataformas de dados "
                            "e serviços operacionais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "iot_edge_intelligence",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="digital_twin_governance_operations",
                title="🛡️ Governança, segurança e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="digital_twin_security_access",
                        title="🔐 Segurança e controle de acesso",
                        description=(
                            "Proteção de modelos, ativos, comandos, "
                            "telemetria, cenários e informações "
                            "operacionais sensíveis."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_model_versioning_audit",
                        title="🧾 Versionamento e auditoria",
                        description=(
                            "Registro de versões, parâmetros, modelos, "
                            "simulações, alterações, responsáveis, "
                            "decisões e resultados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="digital_twin_observability_lifecycle",
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento de sincronização, latência, "
                            "erros, qualidade, uso, recursos, custos, "
                            "versões e disponibilidade da solução."
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

    module_id = "digital_twins_simulation"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        24: (168, 504),
        25: (175, 525),
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

    print("DIGITAL_TWINS_SIMULATION_PREREQUISITES=OK")


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
    """Adiciona Gêmeos Digitais e Simulação."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "DIGITAL_TWINS_SIMULATION_SOLUTION =" in source:
        print("DIGITAL_TWINS_SIMULATION_ALREADY_PRESENT=OK")
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
        DIGITAL_TWINS_SIMULATION_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    IOT_EDGE_INTELLIGENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    DIGITAL_TWINS_SIMULATION_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("DIGITAL_TWINS_SIMULATION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_digital_twins_simulation_is_complete" in source:
        print("DIGITAL_TWINS_SIMULATION_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "DIGITAL_TWINS_SIMULATION_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 24
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 25
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e quatro soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_digital_twins_simulation_is_complete():
    assert (
        DIGITAL_TWINS_SIMULATION_SOLUTION.solution_id
        == "digital_twins_simulation"
    )

    assert len(
        DIGITAL_TWINS_SIMULATION_SOLUTION.areas
    ) == 7

    assert (
        DIGITAL_TWINS_SIMULATION_SOLUTION.capability_count
        == 21
    )


def test_digital_twins_simulation_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "digital_twins_simulation"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        DIGITAL_TWINS_SIMULATION_SOLUTION.status
        is module.status
    )

    assert (
        DIGITAL_TWINS_SIMULATION_SOLUTION.integration_type
        == module.integration_type
    )


def test_digital_twins_simulation_lookup():
    assert (
        platform_technology_solution(
            "digital_twins_simulation"
        )
        is DIGITAL_TWINS_SIMULATION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("DIGITAL_TWINS_SIMULATION_TESTS_CREATED=OK")


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

    digital_twin_solution = getattr(
        module,
        "DIGITAL_TWINS_SIMULATION_SOLUTION",
    )

    assert len(solutions) == 25
    assert len(digital_twin_solution.areas) == 7

    assert digital_twin_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 175
    assert total_capabilities == 525

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=25")
    print("TOTAL_TECHNOLOGY_AREAS=175")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=525")
    print("DIGITAL_TWINS_SIMULATION_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
