"""Adiciona Ferramentas e Analytics ao registro tecnológico."""

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
    / ("tools_analytics_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


TOOLS_ANALYTICS_DEFINITION = """
_TOOLS_ANALYTICS_MODULE = (
    PLATFORM_MODULE_BY_ID["tools_analytics"]
)


TOOLS_ANALYTICS_SOLUTION = PlatformTechnologySolution(
    solution_id="tools_analytics",
    icon="📊",
    title="Ferramentas e Analytics",
    description=(
        "Arquitetura tecnológica para métricas, indicadores, "
        "dashboards, relatórios, análises exploratórias, alertas, "
        "camada semântica, autosserviço, governança, segurança, "
        "desempenho e operação de produtos analíticos."
    ),
    status=_TOOLS_ANALYTICS_MODULE.status,
    integration_type=(
        _TOOLS_ANALYTICS_MODULE.integration_type
    ),
    areas=(
        TechnologyArea(
            area_id="analytics_metrics_semantic_layer",
            title="📐 Métricas e camada semântica",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_metric_definitions",
                    title="🎯 Definição de métricas e KPIs",
                    description=(
                        "Padronização de indicadores, fórmulas, "
                        "dimensões, metas, períodos e responsáveis."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "data_bi_copilot",
                        "technology_governance_policy_compliance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_semantic_models",
                    title="🧩 Modelos e camada semântica",
                    description=(
                        "Organização de fatos, dimensões, relações, "
                        "medidas e conceitos reutilizáveis."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "enterprise_rag",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_metric_lineage",
                    title="🔗 Linhagem e origem das métricas",
                    description=(
                        "Rastreamento de fontes, transformações, "
                        "regras, versões e dependências dos indicadores."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "data_platform_governance",
                        "ai_operations",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_dashboards_reports",
            title="📊 Dashboards e relatórios",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_executive_dashboards",
                    title="📊 Dashboards executivos",
                    description=(
                        "Visualização consolidada de resultados, "
                        "tendências, metas, riscos e indicadores críticos."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                        "digital_experiences_intelligent_interfaces",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_operational_dashboards",
                    title="⚙️ Dashboards operacionais",
                    description=(
                        "Acompanhamento de volumes, filas, produtividade, "
                        "qualidade, ocorrências e desempenho operacional."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "ai_operations",
                        "quality_process_management",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_scheduled_reports",
                    title="📄 Relatórios programados",
                    description=(
                        "Geração e distribuição controlada de relatórios "
                        "por período, público, canal e finalidade."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "api_integrations_connectors",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_exploration_analysis",
            title="🔎 Exploração e análise de dados",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_ad_hoc_queries",
                    title="🔍 Consultas e análises ad hoc",
                    description=(
                        "Exploração controlada de dados por filtros, "
                        "agrupamentos, comparações e recortes."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "scientific_computing_engineering",
                        "zero_trust_identity_access",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_statistical_analysis",
                    title="📈 Análise estatística",
                    description=(
                        "Aplicação de estatísticas descritivas, relações, "
                        "distribuições, variações e testes analíticos."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_segmentation_comparison",
                    title="🧮 Segmentação e comparações",
                    description=(
                        "Comparação de grupos, períodos, produtos, "
                        "unidades, canais e perfis autorizados."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                        "ai_bias_quality_monitoring",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_events_alerts_decisions",
            title="🚨 Eventos, alertas e decisões",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_threshold_alerts",
                    title="🚨 Alertas por limites e regras",
                    description=(
                        "Notificação quando métricas ultrapassarem "
                        "limites, metas ou condições definidas."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "business_automation",
                        "api_integrations_connectors",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_anomaly_alerts",
                    title="⚠️ Alertas de anomalias",
                    description=(
                        "Identificação de mudanças inesperadas, "
                        "desvios, padrões incomuns e degradações."
                    ),
                    technology_dependencies=(
                        "ai_bias_quality_monitoring",
                        "enterprise_decision_intelligence",
                        "ai_operations",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_decision_workflows",
                    title="🧭 Workflows orientados por indicadores",
                    description=(
                        "Acionamento de tarefas, agentes, revisões "
                        "e processos conforme resultados analíticos."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_self_service_copilot",
            title="🤖 Autosserviço e copiloto analítico",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_natural_language_queries",
                    title="💬 Consultas em linguagem natural",
                    description=(
                        "Interpretação de perguntas e tradução controlada "
                        "para consultas, filtros e análises."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_explanation_summaries",
                    title="📝 Resumos e explicações analíticas",
                    description=(
                        "Geração de sínteses fundamentadas sobre "
                        "indicadores, variações e resultados."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "model_explainability_interpretability",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_recommended_insights",
                    title="💡 Insights e recomendações assistidas",
                    description=(
                        "Sugestão de pontos para investigação e ações "
                        "com evidências, contexto e nível de confiança."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "responsible_ai_ethics_risk",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_governance_security_quality",
            title="🛡️ Governança, segurança e qualidade",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_access_controls",
                    title="🔐 Acesso e segurança analítica",
                    description=(
                        "Controle de usuários, funções, linhas, colunas, "
                        "fontes, dashboards e informações sensíveis."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "privacy_data_protection_lgpd",
                        "operational_security_resilience",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_data_quality_validation",
                    title="✅ Qualidade e validação dos dados",
                    description=(
                        "Verificação de completude, consistência, "
                        "atualização, integridade e confiabilidade."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "quality_process_management",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_audit_compliance",
                    title="🧾 Auditoria e conformidade",
                    description=(
                        "Registro de acessos, consultas, exportações, "
                        "alterações, versões e responsáveis."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "privacy_data_protection_lgpd",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="analytics_performance_operations",
            title="⚙️ Desempenho e operações",
            capabilities=(
                TechnologyCapability(
                    capability_id="analytics_query_performance",
                    title="⚡ Desempenho de consultas",
                    description=(
                        "Monitoramento e otimização de consultas, "
                        "modelos, agregações, índices e tempos de resposta."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "cloud_devops_finops",
                        "scientific_computing_engineering",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_usage_observability",
                    title="📊 Uso e observabilidade",
                    description=(
                        "Acompanhamento de acessos, erros, latência, "
                        "adoção, recursos utilizados e disponibilidade."
                    ),
                    technology_dependencies=(
                        "ai_operations",
                        "cloud_devops_finops",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="analytics_lifecycle_versioning",
                    title="🔄 Versionamento e ciclo de vida",
                    description=(
                        "Gestão de versões de métricas, dashboards, "
                        "relatórios, modelos, testes e publicações."
                    ),
                    technology_dependencies=(
                        "software_testing_quality_reliability",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
    ),
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

    module_id = "tools_analytics"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        11: (77, 231),
        12: (84, 252),
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

    print("TOOLS_ANALYTICS_PREREQUISITES=OK")


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
    """Adiciona Ferramentas e Analytics."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "TOOLS_ANALYTICS_SOLUTION =" in source:
        print("TOOLS_ANALYTICS_ALREADY_PRESENT=OK")
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
        TOOLS_ANALYTICS_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    CYBERSECURITY_FRAUD_PREVENTION_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    TOOLS_ANALYTICS_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("TOOLS_ANALYTICS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_tools_analytics_is_complete" in source:
        print("TOOLS_ANALYTICS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "TOOLS_ANALYTICS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 11
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 12
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de onze soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_tools_analytics_is_complete():
    assert (
        TOOLS_ANALYTICS_SOLUTION.solution_id
        == "tools_analytics"
    )

    assert len(
        TOOLS_ANALYTICS_SOLUTION.areas
    ) == 7

    assert (
        TOOLS_ANALYTICS_SOLUTION.capability_count
        == 21
    )


def test_tools_analytics_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "tools_analytics"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        TOOLS_ANALYTICS_SOLUTION.status
        is module.status
    )

    assert (
        TOOLS_ANALYTICS_SOLUTION.integration_type
        == module.integration_type
    )


def test_tools_analytics_lookup():
    assert (
        platform_technology_solution(
            "tools_analytics"
        )
        is TOOLS_ANALYTICS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("TOOLS_ANALYTICS_TESTS_CREATED=OK")


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

    analytics_solution = getattr(
        module,
        "TOOLS_ANALYTICS_SOLUTION",
    )

    assert len(solutions) == 12
    assert len(analytics_solution.areas) == 7

    assert analytics_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 84
    assert total_capabilities == 252

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=12")
    print("TOTAL_TECHNOLOGY_AREAS=84")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=252")
    print("TOOLS_ANALYTICS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
