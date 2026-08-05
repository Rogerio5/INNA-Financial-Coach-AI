"""Adiciona AI Operations ao registro tecnológico especializado."""

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
    / ("ai_operations_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


AI_OPERATIONS_DEFINITION = """
_AI_OPERATIONS_MODULE = (
    PLATFORM_MODULE_BY_ID["ai_operations"]
)


AI_OPERATIONS_SOLUTION = PlatformTechnologySolution(
    solution_id="ai_operations",
    icon="⚙️",
    title="AI Operations — AIOps",
    description=(
        "Arquitetura tecnológica para registro, implantação, "
        "monitoramento, observabilidade, avaliação, segurança, "
        "controle de custos, incidentes, versões e ciclo de vida "
        "de modelos, agentes, pipelines e aplicações de inteligência artificial."
    ),
    status=_AI_OPERATIONS_MODULE.status,
    integration_type=(
        _AI_OPERATIONS_MODULE.integration_type
    ),
    areas=(
        TechnologyArea(
            area_id="aiops_assets_registry",
            title="🗂️ Registro e inventário de ativos de IA",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_model_agent_registry",
                    title="🤖 Registro de modelos e agentes",
                    description=(
                        "Catálogo centralizado de modelos, agentes, "
                        "provedores, versões, responsáveis e finalidades."
                    ),
                    technology_dependencies=(
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                        "agent_process_orchestration",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_prompt_tool_registry",
                    title="🧰 Registro de prompts e ferramentas",
                    description=(
                        "Organização de instruções, ferramentas, contratos, "
                        "parâmetros, versões e permissões operacionais."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "api_integrations_connectors",
                        "zero_trust_identity_access",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_dataset_evaluation_registry",
                    title="📚 Registro de datasets e avaliações",
                    description=(
                        "Controle de conjuntos de dados, casos de teste, "
                        "benchmarks, resultados, origem e versões."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "ai_evaluation_benchmarks_red_team",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_deployment_serving",
            title="🚀 Implantação e serving",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_environment_deployment",
                    title="🚀 Ambientes e implantação controlada",
                    description=(
                        "Publicação em desenvolvimento, homologação e produção "
                        "com configurações e aprovações controladas."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "technology_governance_policy_compliance",
                        "business_automation",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_model_agent_serving",
                    title="☁️ Serving de modelos e agentes",
                    description=(
                        "Disponibilização de modelos, agentes e pipelines "
                        "por serviços, APIs, filas e processos."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "api_integrations_connectors",
                        "agent_process_orchestration",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_scaling_capacity",
                    title="📈 Escalabilidade e capacidade",
                    description=(
                        "Ajuste de recursos, concorrência, filas, limites, "
                        "disponibilidade e capacidade operacional."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "real_time_event_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_observability_tracing",
            title="📊 Observabilidade, tracing e telemetria",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_distributed_tracing",
                    title="🔎 Tracing distribuído de IA",
                    description=(
                        "Rastreamento de solicitações, agentes, ferramentas, "
                        "modelos, etapas, dependências e resultados."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "agent_process_orchestration",
                        "operational_security_resilience",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_logs_metrics_events",
                    title="📊 Logs, métricas e eventos",
                    description=(
                        "Coleta de latência, tokens, erros, respostas, "
                        "eventos, consumo e indicadores operacionais."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "real_time_event_intelligence",
                        "data_platform_governance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_service_health",
                    title="❤️ Saúde e disponibilidade dos serviços",
                    description=(
                        "Monitoramento de disponibilidade, dependências, "
                        "filas, conexões, provedores e componentes críticos."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "cloud_devops_finops",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_quality_evaluation_monitoring",
            title="✅ Qualidade e avaliação contínua",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_online_quality_evaluation",
                    title="🧪 Avaliação online de qualidade",
                    description=(
                        "Medição contínua de utilidade, fidelidade, "
                        "consistência, aderência e qualidade das respostas."
                    ),
                    technology_dependencies=(
                        "ai_evaluation_benchmarks_red_team",
                        "ai_bias_quality_monitoring",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_drift_degradation_monitoring",
                    title="📉 Drift e degradação de desempenho",
                    description=(
                        "Identificação de mudanças nos dados, comportamento, "
                        "qualidade e desempenho dos componentes de IA."
                    ),
                    technology_dependencies=(
                        "ai_bias_quality_monitoring",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_feedback_human_review",
                    title="👤 Feedback e revisão humana",
                    description=(
                        "Coleta de avaliações e encaminhamento de casos "
                        "para correção, aprovação ou investigação."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "quality_process_management",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_incidents_reliability",
            title="🚨 Incidentes e confiabilidade",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_incident_detection",
                    title="🚨 Detecção e classificação de incidentes",
                    description=(
                        "Identificação de falhas, indisponibilidade, erros, "
                        "degradação e comportamentos inesperados."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "operational_security_resilience",
                        "tools_analytics",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_retries_fallbacks_recovery",
                    title="🔄 Retries, fallback e recuperação",
                    description=(
                        "Execução de tentativas controladas, alternativas, "
                        "compensações, retomadas e recuperação de falhas."
                    ),
                    technology_dependencies=(
                        "software_testing_quality_reliability",
                        "agent_process_orchestration",
                        "operational_security_resilience",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_root_cause_analysis",
                    title="🌳 Análise de causa raiz",
                    description=(
                        "Correlação de logs, métricas, eventos, dependências "
                        "e alterações para apoiar a investigação."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "enterprise_decision_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_security_governance_cost",
            title="🛡️ Segurança, governança e custos",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_access_secrets_security",
                    title="🔐 Acesso, segredos e segurança",
                    description=(
                        "Controle de identidade, credenciais, segredos, "
                        "permissões, escopos e acessos técnicos."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "operational_security_resilience",
                        "privacy_enhancing_technologies",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_policy_compliance_audit",
                    title="🧾 Políticas, conformidade e auditoria",
                    description=(
                        "Aplicação de políticas e registro de alterações, "
                        "aprovações, decisões e evidências operacionais."
                    ),
                    technology_dependencies=(
                        "technology_governance_policy_compliance",
                        "responsible_ai_ethics_risk",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_cost_token_finops",
                    title="💰 Custos, tokens e FinOps",
                    description=(
                        "Monitoramento de consumo, tokens, chamadas, "
                        "provedores, orçamento, limites e eficiência."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="aiops_lifecycle_release_optimization",
            title="🔄 Ciclo de vida e otimização",
            capabilities=(
                TechnologyCapability(
                    capability_id="aiops_version_release_management",
                    title="🗃️ Versionamento e gestão de releases",
                    description=(
                        "Controle de versões de modelos, agentes, prompts, "
                        "ferramentas, configurações e implantações."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "cloud_devops_finops",
                        "technology_governance_policy_compliance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_canary_ab_rollout",
                    title="🧪 Canary, testes A/B e rollout gradual",
                    description=(
                        "Liberação progressiva, comparação de versões, "
                        "avaliação de resultados e interrupção controlada."
                    ),
                    technology_dependencies=(
                        "ai_evaluation_benchmarks_red_team",
                        "software_testing_quality_reliability",
                        "cloud_devops_finops",
                    ),
                ),
                TechnologyCapability(
                    capability_id="aiops_continuous_optimization",
                    title="📈 Otimização operacional contínua",
                    description=(
                        "Análise de qualidade, custos, latência, capacidade "
                        "e confiabilidade para orientar melhorias."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                        "business_automation",
                    ),
                ),
            ),
        ),
    ),
)


"""


def validate_prerequisites() -> None:
    """Valida o registro e o módulo tecnológico principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )

    module_id = "ai_operations"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("AI_OPERATIONS_PREREQUISITES=OK")


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
    """Adiciona AI Operations ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AI_OPERATIONS_SOLUTION = PlatformTechnologySolution(" in source:
        print("AI_OPERATIONS_ALREADY_PRESENT=OK")
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
        AI_OPERATIONS_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION,
    VOICE_AUDIO_SPEECH_AI_SOLUTION,
)"""

    new_registry = """    COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION,
    VOICE_AUDIO_SPEECH_AI_SOLUTION,
    AI_OPERATIONS_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro tecnológico não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_OPERATIONS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_ai_operations_is_complete" in source:
        print("AI_OPERATIONS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "AI_OPERATIONS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 6
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 7
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de seis soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_ai_operations_is_complete():
    assert (
        AI_OPERATIONS_SOLUTION.solution_id
        == "ai_operations"
    )

    assert len(
        AI_OPERATIONS_SOLUTION.areas
    ) == 7

    assert (
        AI_OPERATIONS_SOLUTION.capability_count
        == 21
    )


def test_ai_operations_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_operations"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_OPERATIONS_SOLUTION.status
        is module.status
    )

    assert (
        AI_OPERATIONS_SOLUTION.integration_type
        == module.integration_type
    )


def test_ai_operations_lookup():
    assert (
        platform_technology_solution(
            "ai_operations"
        )
        is AI_OPERATIONS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("AI_OPERATIONS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    ai_operations_solution = getattr(
        module,
        "AI_OPERATIONS_SOLUTION",
    )

    assert len(solutions) == 7
    assert len(ai_operations_solution.areas) == 7

    assert ai_operations_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 49
    assert total_capabilities == 147

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=7")
    print("TOTAL_TECHNOLOGY_AREAS=49")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=147")
    print("AI_OPERATIONS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
