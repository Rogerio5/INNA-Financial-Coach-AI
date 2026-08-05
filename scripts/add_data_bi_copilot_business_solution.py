"""Adiciona Data & BI Copilot ao registro empresarial."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_business_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_business_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("data_bi_copilot_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


DATA_BI_COPILOT_DEFINITION = """
DATA_BI_COPILOT_SOLUTION = PlatformBusinessSolution(
    solution_id="data_bi_copilot",
    icon="📊",
    title="Data & BI Copilot",
    description=(
        "Solução empresarial para integração, modelagem, "
        "qualidade, análise, visualização, pesquisa conversacional "
        "e apoio à tomada de decisão baseada em dados."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="data_bi_connections_ingestion",
            title="🔌 Conexões e ingestão de dados",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_source_connectors",
                    title="🔌 Conectores de fontes de dados",
                    description=(
                        "Integração com bancos de dados, APIs, arquivos, "
                        "sistemas empresariais e serviços em nuvem."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "data_platform_governance",
                        "cloud_devops_finops",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_batch_stream_ingestion",
                    title="📥 Ingestão em lote e tempo real",
                    description=(
                        "Recebimento controlado de dados por lotes, "
                        "eventos, filas, streams e integrações."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "data_platform_governance",
                        "cloud_devops_finops",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_data_preparation",
                    title="🧹 Preparação e transformação de dados",
                    description=(
                        "Limpeza, padronização, combinação, transformação "
                        "e preparação de dados para análise."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "scientific_computing_engineering",
                        "business_automation",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="data_bi_modeling_semantic_layer",
            title="🧩 Modelagem e camada semântica",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_business_modeling",
                    title="🧩 Modelagem de dados empresariais",
                    description=(
                        "Definição de entidades, dimensões, fatos, "
                        "relacionamentos, medidas e regras analíticas."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                        "scientific_computing_engineering",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_semantic_metrics",
                    title="📐 Métricas e camada semântica",
                    description=(
                        "Centralização de indicadores, cálculos, conceitos "
                        "empresariais e definições compartilhadas."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "technology_governance_policy_compliance",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_metadata_catalog",
                    title="🏷️ Catálogo e metadados",
                    description=(
                        "Organização de fontes, tabelas, campos, métricas, "
                        "proprietários, descrições e linhagem."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "data_traceability_provenance",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="data_bi_dashboards_visualization",
            title="📊 Dashboards e visualização",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_dashboard_builder",
                    title="📊 Construção de dashboards",
                    description=(
                        "Criação assistida de painéis, gráficos, tabelas, "
                        "indicadores, filtros e análises visuais."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "digital_experiences_intelligent_interfaces",
                        "ai_software_engineering",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_executive_indicators",
                    title="🎯 Indicadores executivos e operacionais",
                    description=(
                        "Acompanhamento de metas, resultados, tendências, "
                        "desvios e desempenho empresarial."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_reports_distribution",
                    title="📄 Relatórios e distribuição automática",
                    description=(
                        "Geração, exportação, agendamento e distribuição "
                        "de relatórios para públicos autorizados."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="data_bi_conversational_analytics",
            title="💬 Análise conversacional",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_natural_language_questions",
                    title="💬 Perguntas em linguagem natural",
                    description=(
                        "Consulta de indicadores, dados e tendências "
                        "por meio de perguntas empresariais."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "multimodal_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_explain_insights",
                    title="🧠 Explicação de indicadores e insights",
                    description=(
                        "Explicação assistida de variações, tendências, "
                        "relações, desvios e possíveis causas."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "model_explainability_interpretability",
                        "tools_analytics",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_query_generation",
                    title="⌨️ Geração assistida de consultas",
                    description=(
                        "Apoio à criação e validação de consultas "
                        "analíticas sobre fontes autorizadas."
                    ),
                    technology_dependencies=(
                        "ai_software_engineering",
                        "data_platform_governance",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="data_bi_quality_governance_security",
            title="✅ Qualidade, governança e segurança",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_quality_monitoring",
                    title="✅ Qualidade e confiabilidade dos dados",
                    description=(
                        "Monitoramento de completude, consistência, "
                        "duplicidade, validade, atualização e anomalias."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "software_testing_quality_reliability",
                        "ai_bias_quality_monitoring",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_access_privacy",
                    title="🔐 Acesso, segurança e privacidade",
                    description=(
                        "Controle de permissões, identidade, proteção "
                        "de dados e acesso conforme necessidade."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "privacy_data_protection_lgpd",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_lineage_audit",
                    title="🧾 Linhagem, auditoria e rastreabilidade",
                    description=(
                        "Registro da origem, transformações, consultas, "
                        "alterações e uso das informações."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "operational_security_resilience",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="data_bi_decision_monitoring",
            title="📈 Decisão, previsão e monitoramento",
            capabilities=(
                BusinessCapability(
                    capability_id="data_bi_forecasting_scenarios",
                    title="📈 Previsões e análise de cenários",
                    description=(
                        "Projeções, tendências, simulações e comparação "
                        "de cenários para planejamento empresarial."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "simulation_optimization_operations_research",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_anomaly_alerts",
                    title="⚠️ Anomalias, desvios e alertas",
                    description=(
                        "Detecção de comportamentos incomuns, variações, "
                        "riscos e mudanças relevantes nos indicadores."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                        "tools_analytics",
                    ),
                ),
                BusinessCapability(
                    capability_id="data_bi_action_automation",
                    title="⚙️ Automação orientada por dados",
                    description=(
                        "Acionamento de tarefas, notificações, workflows "
                        "e decisões após eventos analíticos."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
    ),
)


"""


def create_backup() -> None:
    """Cria cópias antes da alteração."""

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
    """Adiciona Data & BI Copilot ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "DATA_BI_COPILOT_SOLUTION = PlatformBusinessSolution(" in source:
        print("DATA_BI_COPILOT_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_BUSINESS_SOLUTIONS: tuple[
    PlatformBusinessSolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro empresarial não encontrada.")

    source = source.replace(
        registry_anchor,
        DATA_BI_COPILOT_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    DOCUMENT_AI_SOLUTION,
    BUSINESS_AUTOMATION_SOLUTION,
    INTELLIGENT_SUPPORT_SOLUTION,
)"""

    new_registry = """    DOCUMENT_AI_SOLUTION,
    BUSINESS_AUTOMATION_SOLUTION,
    INTELLIGENT_SUPPORT_SOLUTION,
    DATA_BI_COPILOT_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Registro empresarial atual não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("DATA_BI_COPILOT_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_data_bi_copilot_solution_is_complete" in source:
        print("DATA_BI_COPILOT_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    DOCUMENT_AI_SOLUTION,\n"

    import_replacement = "    DATA_BI_COPILOT_SOLUTION,\n    DOCUMENT_AI_SOLUTION,\n"

    if import_anchor not in source:
        raise RuntimeError("Importação do Document AI não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 3"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 4"

    if old_count not in source:
        raise RuntimeError("Contagem atual de três soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_data_bi_copilot_solution_is_complete():
    assert (
        DATA_BI_COPILOT_SOLUTION.solution_id
        == "data_bi_copilot"
    )
    assert (
        DATA_BI_COPILOT_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        DATA_BI_COPILOT_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        DATA_BI_COPILOT_SOLUTION.areas
    ) == 6
    assert (
        DATA_BI_COPILOT_SOLUTION.capability_count
        == 18
    )


def test_data_bi_copilot_lookup():
    assert (
        platform_business_solution(
            "data_bi_copilot"
        )
        is DATA_BI_COPILOT_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("DATA_BI_COPILOT_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        DATA_BI_COPILOT_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 4

    assert platform_business_solution("data_bi_copilot") is DATA_BI_COPILOT_SOLUTION

    assert len(DATA_BI_COPILOT_SOLUTION.areas) == 6

    assert DATA_BI_COPILOT_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 24
    assert total_capabilities == 71

    print("SPECIALIZED_BUSINESS_SOLUTIONS=4")
    print("TOTAL_BUSINESS_AREAS=24")
    print("TOTAL_BUSINESS_CAPABILITIES=71")
    print("DATA_BI_COPILOT_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
