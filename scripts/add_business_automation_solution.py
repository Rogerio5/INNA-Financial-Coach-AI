"""Adiciona a solução especializada de Automação Empresarial."""

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
    / ("business_automation_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


BUSINESS_AUTOMATION_DEFINITION = """
BUSINESS_AUTOMATION_SOLUTION = PlatformBusinessSolution(
    solution_id="business_automation",
    icon="🤖",
    title="Automação Empresarial",
    description=(
        "Solução para descoberta, modelagem, execução, "
        "integração, monitoramento e melhoria contínua "
        "de processos empresariais automatizados."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="automation_process_discovery",
            title="🔎 Descoberta e modelagem de processos",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_process_inventory",
                    title="🗂️ Inventário de processos",
                    description=(
                        "Mapeamento centralizado de processos, "
                        "responsáveis, sistemas, entradas, saídas "
                        "e dependências operacionais."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_process_mapping",
                    title="🧭 Mapeamento e desenho de fluxos",
                    description=(
                        "Representação de etapas, decisões, eventos, "
                        "regras, aprovações e integrações do processo."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "digital_twins_simulation",
                        "quality_process_management",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_opportunity_analysis",
                    title="💡 Identificação de oportunidades",
                    description=(
                        "Análise de tarefas repetitivas, gargalos, "
                        "retrabalho, atrasos, riscos e potencial "
                        "de automação."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                        "data_bi_copilot",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="automation_workflow_orchestration",
            title="🧩 Workflows e orquestração",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_workflow_builder",
                    title="🧩 Construtor de workflows",
                    description=(
                        "Configuração de fluxos com etapas, regras, "
                        "condições, responsáveis, prazos e ações."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "digital_experiences_intelligent_interfaces",
                        "ai_software_engineering",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_agent_orchestration",
                    title="🤖 Orquestração de agentes e serviços",
                    description=(
                        "Coordenação de agentes de IA, APIs, serviços, "
                        "ferramentas e decisões automatizadas."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "ai_operations",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_rules_decisions",
                    title="⚖️ Regras e decisões automatizadas",
                    description=(
                        "Execução controlada de regras empresariais, "
                        "condições, validações e critérios de decisão."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "technology_governance_policy_compliance",
                        "responsible_ai_ethics_risk",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="automation_tasks_documents",
            title="⚙️ Tarefas e documentos",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_repetitive_tasks",
                    title="⚙️ Automação de tarefas repetitivas",
                    description=(
                        "Execução de cadastros, consultas, atualizações, "
                        "movimentações e rotinas administrativas."
                    ),
                    technology_dependencies=(
                        "ai_software_engineering",
                        "api_integrations_connectors",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_document_workflows",
                    title="📄 Automação documental",
                    description=(
                        "Recebimento, classificação, validação, "
                        "aprovação, arquivamento e encaminhamento "
                        "de documentos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "agent_process_orchestration",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_notifications",
                    title="🔔 Alertas e notificações automáticas",
                    description=(
                        "Envio de avisos, lembretes, confirmações, "
                        "escalonamentos e comunicações multicanal."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "mobile_apps_omnichannel_experiences",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="automation_integrations_events",
            title="🔌 Integrações e eventos",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_system_integrations",
                    title="🔌 Integração entre sistemas",
                    description=(
                        "Conexão com APIs, bancos de dados, sistemas "
                        "empresariais, plataformas e serviços externos."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "data_platform_governance",
                        "cloud_devops_finops",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_event_driven_flows",
                    title="⚡ Fluxos orientados a eventos",
                    description=(
                        "Acionamento de processos em resposta a eventos, "
                        "mudanças de estado, mensagens e sinais."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "iot_edge_intelligence",
                        "agent_process_orchestration",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_data_synchronization",
                    title="🔄 Sincronização de dados",
                    description=(
                        "Atualização coordenada de registros, estados "
                        "e informações entre diferentes sistemas."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "api_integrations_connectors",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="automation_human_review_exceptions",
            title="👤 Aprovações e exceções",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_human_approvals",
                    title="👤 Aprovações humanas",
                    description=(
                        "Encaminhamento de atividades para revisão, "
                        "aprovação, correção, rejeição ou comentário."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "zero_trust_identity_access",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_exception_management",
                    title="⚠️ Gestão de exceções",
                    description=(
                        "Identificação, classificação, tratamento "
                        "e escalonamento de falhas e situações não previstas."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "ai_operations",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_service_levels",
                    title="⏱️ Prazos e níveis de serviço",
                    description=(
                        "Controle de prazos, filas, prioridades, "
                        "responsáveis, atrasos e escalonamentos."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "tools_analytics",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="automation_monitoring_governance",
            title="📊 Monitoramento e governança",
            capabilities=(
                BusinessCapability(
                    capability_id="automation_operational_monitoring",
                    title="📊 Monitoramento de automações",
                    description=(
                        "Acompanhamento de execuções, filas, falhas, "
                        "tempos, resultados e saúde operacional."
                    ),
                    technology_dependencies=(
                        "ai_operations",
                        "tools_analytics",
                        "cloud_devops_finops",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_audit_governance",
                    title="🧾 Auditoria e governança",
                    description=(
                        "Registro de ações, versões, responsáveis, "
                        "decisões, acessos e evidências de execução."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="automation_process_optimization",
                    title="📈 Otimização contínua de processos",
                    description=(
                        "Análise de indicadores, gargalos, custos, "
                        "qualidade e oportunidades de melhoria."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "quality_process_management",
                        "data_bi_copilot",
                    ),
                ),
            ),
        ),
    ),
)


"""


def create_backup() -> None:
    """Cria cópias dos arquivos antes da alteração."""

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
    """Adiciona Automação Empresarial ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "BUSINESS_AUTOMATION_SOLUTION = PlatformBusinessSolution(" in source:
        print("BUSINESS_AUTOMATION_ALREADY_PRESENT=OK")
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
        BUSINESS_AUTOMATION_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    DOCUMENT_AI_SOLUTION,
)"""

    new_registry = """    DOCUMENT_AI_SOLUTION,
    BUSINESS_AUTOMATION_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Registro atual do Document AI não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("BUSINESS_AUTOMATION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_business_automation_solution_is_complete" in source:
        print("BUSINESS_AUTOMATION_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    DOCUMENT_AI_SOLUTION,\n"

    import_replacement = (
        "    BUSINESS_AUTOMATION_SOLUTION,\n    DOCUMENT_AI_SOLUTION,\n"
    )

    if import_anchor not in source:
        raise RuntimeError("Importação do Document AI não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 1"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 2"

    if old_count not in source:
        raise RuntimeError("Contagem atual de uma solução não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_business_automation_solution_is_complete():
    assert (
        BUSINESS_AUTOMATION_SOLUTION.solution_id
        == "business_automation"
    )
    assert (
        BUSINESS_AUTOMATION_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        BUSINESS_AUTOMATION_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        BUSINESS_AUTOMATION_SOLUTION.areas
    ) == 6
    assert (
        BUSINESS_AUTOMATION_SOLUTION.capability_count
        == 18
    )


def test_business_automation_lookup():
    assert (
        platform_business_solution(
            "business_automation"
        )
        is BUSINESS_AUTOMATION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("BUSINESS_AUTOMATION_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        BUSINESS_AUTOMATION_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 2

    assert (
        platform_business_solution("business_automation")
        is BUSINESS_AUTOMATION_SOLUTION
    )

    assert len(BUSINESS_AUTOMATION_SOLUTION.areas) == 6

    assert BUSINESS_AUTOMATION_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 12
    assert total_capabilities == 35

    print("SPECIALIZED_BUSINESS_SOLUTIONS=2")
    print("TOTAL_BUSINESS_AREAS=12")
    print("TOTAL_BUSINESS_CAPABILITIES=35")
    print("BUSINESS_AUTOMATION_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
