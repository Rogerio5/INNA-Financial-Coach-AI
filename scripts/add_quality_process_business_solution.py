"""Adiciona Gestão da Qualidade e Processos ao registro empresarial."""

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
    / ("quality_process_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


QUALITY_PROCESS_DEFINITION = """
QUALITY_PROCESS_MANAGEMENT_SOLUTION = PlatformBusinessSolution(
    solution_id="quality_process_management",
    icon="✅",
    title="Gestão da Qualidade e Processos",
    description=(
        "Solução empresarial para mapeamento, padronização, "
        "inspeções, não conformidades, ações corretivas, "
        "auditorias, riscos, indicadores e melhoria contínua."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="quality_process_architecture",
            title="🗺️ Arquitetura e padronização de processos",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_process_inventory",
                    title="🗂️ Inventário e arquitetura de processos",
                    description=(
                        "Cadastro de processos, responsáveis, entradas, "
                        "saídas, clientes, fornecedores e dependências."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_process_mapping",
                    title="🧭 Mapeamento e padronização de processos",
                    description=(
                        "Representação de atividades, decisões, fluxos, "
                        "responsabilidades, controles e padrões operacionais."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "digital_twins_simulation",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_policies_procedures",
                    title="📄 Políticas, procedimentos e instruções",
                    description=(
                        "Criação, organização, revisão, aprovação, "
                        "publicação e controle de documentos normativos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "technology_governance_policy_compliance",
                        "enterprise_rag",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="quality_control_inspections",
            title="🔍 Controle, inspeções e registros",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_checklists_inspections",
                    title="✅ Checklists e inspeções digitais",
                    description=(
                        "Execução de checklists, inspeções, verificações, "
                        "registros e coleta de evidências."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "mobile_apps_omnichannel_experiences",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_nonconformities",
                    title="⚠️ Não conformidades e desvios",
                    description=(
                        "Registro, classificação, priorização, tratamento "
                        "e acompanhamento de desvios e não conformidades."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "agent_process_orchestration",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_evidence_records",
                    title="🧾 Evidências e registros da qualidade",
                    description=(
                        "Organização de documentos, imagens, aprovações, "
                        "resultados, responsáveis e evidências."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "data_traceability_provenance",
                        "ai_certification_system_evidence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="quality_capa_improvement",
            title="🔧 Ações corretivas e melhoria contínua",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_root_cause_analysis",
                    title="🌳 Análise de causa raiz",
                    description=(
                        "Apoio à análise de causas, relações, fatores, "
                        "evidências e hipóteses de problemas."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "knowledge_graph_semantic_ai",
                        "tools_analytics",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_capa_management",
                    title="🔧 Ações corretivas e preventivas",
                    description=(
                        "Planejamento, aprovação, execução, verificação "
                        "de eficácia e encerramento de ações."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_improvement_portfolio",
                    title="📈 Portfólio de melhorias",
                    description=(
                        "Gestão de oportunidades, iniciativas, ganhos, "
                        "prioridades, responsáveis e resultados."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="quality_audits_compliance",
            title="📋 Auditorias e conformidade",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_internal_audits",
                    title="📋 Auditorias internas e externas",
                    description=(
                        "Planejamento, execução, evidências, constatações, "
                        "relatórios e acompanhamento de auditorias."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_requirements_controls",
                    title="⚖️ Requisitos, normas e controles",
                    description=(
                        "Mapeamento de requisitos, controles, documentos, "
                        "responsáveis e evidências de conformidade."
                    ),
                    technology_dependencies=(
                        "legal_compliance",
                        "technology_governance_policy_compliance",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_audit_findings",
                    title="🔄 Constatações e planos de ação",
                    description=(
                        "Tratamento de observações, não conformidades, "
                        "prazos, responsáveis e evidências de conclusão."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="quality_risk_reliability",
            title="🛡️ Riscos, confiabilidade e incidentes",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_risk_controls",
                    title="🛡️ Riscos e controles de processo",
                    description=(
                        "Identificação, avaliação, priorização, tratamento "
                        "e monitoramento de riscos e controles."
                    ),
                    technology_dependencies=(
                        "responsible_ai_ethics_risk",
                        "operational_security_resilience",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_reliability_assets",
                    title="🏭 Confiabilidade de ativos e operações",
                    description=(
                        "Acompanhamento de falhas, desempenho, manutenção, "
                        "disponibilidade e confiabilidade operacional."
                    ),
                    technology_dependencies=(
                        "asset_management_smart_maintenance",
                        "software_testing_quality_reliability",
                        "iot_edge_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_incidents_lessons",
                    title="📚 Incidentes e lições aprendidas",
                    description=(
                        "Registro de ocorrências, causas, ações, impactos, "
                        "aprendizados e prevenção de recorrências."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "knowledge_graph_semantic_ai",
                        "enterprise_rag",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="quality_analytics_governance",
            title="📊 Indicadores e governança da qualidade",
            capabilities=(
                BusinessCapability(
                    capability_id="quality_kpi_dashboards",
                    title="📊 Indicadores e dashboards da qualidade",
                    description=(
                        "Acompanhamento de desvios, auditorias, ações, "
                        "inspeções, perdas, qualidade e desempenho."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_process_performance",
                    title="📈 Desempenho e capacidade de processos",
                    description=(
                        "Análise de tempo, variação, produtividade, "
                        "gargalos, estabilidade e resultados."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="quality_management_review",
                    title="🧑‍💼 Análise crítica pela gestão",
                    description=(
                        "Consolidação de indicadores, riscos, auditorias, "
                        "ações, decisões e registros da gestão."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "technology_governance_policy_compliance",
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
    """Adiciona Gestão da Qualidade ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "QUALITY_PROCESS_MANAGEMENT_SOLUTION = PlatformBusinessSolution(" in source:
        print("QUALITY_PROCESS_SOLUTION_ALREADY_PRESENT=OK")
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
        QUALITY_PROCESS_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    INTELLIGENT_SUPPORT_SOLUTION,
    DATA_BI_COPILOT_SOLUTION,
)"""

    new_registry = """    INTELLIGENT_SUPPORT_SOLUTION,
    DATA_BI_COPILOT_SOLUTION,
    QUALITY_PROCESS_MANAGEMENT_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro empresarial não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("QUALITY_PROCESS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_quality_process_solution_is_complete" in source:
        print("QUALITY_PROCESS_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_business_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Bloco de importação empresarial não encontrado.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final do bloco de importação não encontrado.")

    import_block = source[import_start:import_end]

    if "QUALITY_PROCESS_MANAGEMENT_SOLUTION" not in import_block:
        source = (
            source[:import_end]
            + ("    QUALITY_PROCESS_MANAGEMENT_SOLUTION,\n")
            + source[import_end:]
        )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 4"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 5"

    if old_count not in source:
        raise RuntimeError("Contagem atual de quatro soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_quality_process_solution_is_complete():
    assert (
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.solution_id
        == "quality_process_management"
    )
    assert (
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.areas
    ) == 6
    assert (
        QUALITY_PROCESS_MANAGEMENT_SOLUTION.capability_count
        == 18
    )


def test_quality_process_solution_lookup():
    assert (
        platform_business_solution(
            "quality_process_management"
        )
        is QUALITY_PROCESS_MANAGEMENT_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("QUALITY_PROCESS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
        QUALITY_PROCESS_MANAGEMENT_SOLUTION,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 5

    assert (
        platform_business_solution("quality_process_management")
        is QUALITY_PROCESS_MANAGEMENT_SOLUTION
    )

    assert len(QUALITY_PROCESS_MANAGEMENT_SOLUTION.areas) == 6

    assert QUALITY_PROCESS_MANAGEMENT_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 30
    assert total_capabilities == 89

    print("SPECIALIZED_BUSINESS_SOLUTIONS=5")
    print("TOTAL_BUSINESS_AREAS=30")
    print("TOTAL_BUSINESS_CAPABILITIES=89")
    print("QUALITY_PROCESS_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
