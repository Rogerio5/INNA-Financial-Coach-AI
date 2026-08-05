"""Adiciona Orquestração de Agentes e Processos ao registro tecnológico."""

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
        "agent_process_orchestration_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


AGENT_PROCESS_ORCHESTRATION_DEFINITION = """
_AGENT_PROCESS_ORCHESTRATION_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "agent_process_orchestration"
    ]
)


AGENT_PROCESS_ORCHESTRATION_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="agent_process_orchestration",
        icon="🧩",
        title="Orquestração de Agentes e Processos",
        description=(
            "Arquitetura tecnológica para definição de agentes, "
            "workflows, estado, memória, ferramentas, integrações, "
            "segurança, revisão humana, avaliação, confiabilidade "
            "e observabilidade operacional."
        ),
        status=(
            _AGENT_PROCESS_ORCHESTRATION_MODULE.status
        ),
        integration_type=(
            _AGENT_PROCESS_ORCHESTRATION_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="agent_design_roles",
                title="🤖 Design, papéis e contratos dos agentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_roles_responsibilities",
                        title="👥 Papéis e responsabilidades",
                        description=(
                            "Definição de objetivos, responsabilidades, "
                            "limites, especializações e critérios de "
                            "encaminhamento dos agentes."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_tools_permissions",
                        title="🧰 Ferramentas e permissões",
                        description=(
                            "Definição das ferramentas disponíveis, "
                            "operações permitidas, escopos e restrições "
                            "de cada agente."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "api_integrations_connectors",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_prompt_context_contracts",
                        title="📋 Contratos de instrução e contexto",
                        description=(
                            "Padronização de instruções, entradas, saídas, "
                            "formatos, contexto esperado e regras de uso."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_workflow_orchestration",
                title="🧩 Workflows e coordenação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_graph_workflows",
                        title="🕸️ Grafos e fluxos de agentes",
                        description=(
                            "Modelagem de nós, transições, condições, "
                            "estados, ciclos e encerramento de workflows."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "ai_software_engineering",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_task_routing_delegation",
                        title="🧭 Roteamento e delegação de tarefas",
                        description=(
                            "Distribuição de solicitações entre agentes, "
                            "serviços, ferramentas e responsáveis humanos."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "knowledge_graph_semantic_ai",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_parallel_sequential_execution",
                        title="⚡ Execução sequencial e paralela",
                        description=(
                            "Coordenação de tarefas dependentes, paralelas, "
                            "assíncronas e condicionais."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_state_memory_context",
                title="🧠 Estado, memória e contexto",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_session_state",
                        title="💾 Estado de sessão e workflow",
                        description=(
                            "Persistência de dados temporários, etapas, "
                            "decisões, resultados e situação da execução."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_short_long_term_memory",
                        title="🧠 Memória de curto e longo prazo",
                        description=(
                            "Armazenamento controlado de interações, fatos, "
                            "preferências e aprendizados autorizados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_context_management",
                        title="🧩 Engenharia e gestão de contexto",
                        description=(
                            "Seleção, montagem, compressão, priorização "
                            "e atualização do contexto usado pelos agentes."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "multimodal_ai",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_tools_integrations",
                title="🔌 Ferramentas, integrações e eventos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_tool_registry",
                        title="🧰 Registro central de ferramentas",
                        description=(
                            "Catálogo de ferramentas, contratos, versões, "
                            "parâmetros, permissões e disponibilidade."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_api_connector_execution",
                        title="🔌 Execução de APIs e conectores",
                        description=(
                            "Chamadas controladas a APIs, bancos, serviços, "
                            "aplicações e integrações empresariais."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_event_driven_actions",
                        title="⚡ Ações orientadas a eventos",
                        description=(
                            "Inicialização ou continuidade de workflows "
                            "a partir de eventos, mensagens e mudanças "
                            "de estado."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "business_automation",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_safety_governance_human_review",
                title="🛡️ Segurança, governança e revisão humana",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_policy_guardrails",
                        title="🛡️ Políticas e guardrails",
                        description=(
                            "Aplicação de políticas, limites operacionais, "
                            "validações de entrada e saída e bloqueios."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_human_in_loop",
                        title="👤 Human-in-the-loop",
                        description=(
                            "Encaminhamento de casos para aprovação, "
                            "correção, rejeição, esclarecimento ou decisão "
                            "de uma pessoa autorizada."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "data_traceability_provenance",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_identity_access_secrets",
                        title="🔐 Identidade, acesso e segredos",
                        description=(
                            "Controle de identidade técnica, credenciais, "
                            "tokens, segredos, permissões e escopos."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_reliability_evaluation",
                title="🧪 Avaliação e confiabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_testing_simulation",
                        title="🧪 Testes e simulação de workflows",
                        description=(
                            "Validação de caminhos, estados, ferramentas, "
                            "erros, condições e cenários antes da produção."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "digital_twins_simulation",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_quality_evaluation",
                        title="✅ Avaliação de qualidade dos agentes",
                        description=(
                            "Medição de sucesso, aderência, utilidade, "
                            "consistência, segurança e qualidade das ações."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "ai_bias_quality_monitoring",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_failure_recovery_idempotency",
                        title="🔄 Recuperação, repetição e idempotência",
                        description=(
                            "Tratamento de falhas, retries controlados, "
                            "compensação, retomada e prevenção de ações "
                            "duplicadas."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="agent_observability_operations",
                title="📊 Observabilidade e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="agent_tracing_metrics",
                        title="📊 Tracing, logs e métricas",
                        description=(
                            "Acompanhamento de etapas, chamadas, decisões, "
                            "erros, duração, resultados e dependências."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_cost_latency_controls",
                        title="⏱️ Custos, latência e limites",
                        description=(
                            "Controle de tempo, tokens, chamadas, consumo, "
                            "orçamento e limites operacionais."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "ai_operations",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="agent_versioning_deployment_lifecycle",
                        title="🚀 Versionamento e ciclo de vida",
                        description=(
                            "Gestão de versões de agentes, workflows, "
                            "ferramentas, configurações, implantação "
                            "e reversão."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "ai_software_engineering",
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
    """Valida o registro tecnológico atual."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )

    module_id = "agent_process_orchestration"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("AGENT_PROCESS_ORCHESTRATION_PREREQUISITES=OK")


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
    """Adiciona a nova solução ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AGENT_PROCESS_ORCHESTRATION_SOLUTION =" in source:
        print("AGENT_PROCESS_ORCHESTRATION_ALREADY_PRESENT=OK")
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
        (AGENT_PROCESS_ORCHESTRATION_DEFINITION + registry_anchor),
        1,
    )

    old_registry = """    ENTERPRISE_RAG_SOLUTION,
)"""

    new_registry = """    ENTERPRISE_RAG_SOLUTION,
    AGENT_PROCESS_ORCHESTRATION_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Registro atual do Enterprise RAG não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AGENT_PROCESS_ORCHESTRATION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_agent_process_orchestration_is_complete" in source:
        print("AGENT_PROCESS_ORCHESTRATION_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_technology_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Importação das soluções tecnológicas não encontrada.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final da importação tecnológica não encontrado.")

    import_block = source[import_start:import_end]

    solution_name = "AGENT_PROCESS_ORCHESTRATION_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 1
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 2
"""

    if old_count not in source:
        raise RuntimeError("Contagem atual de uma solução tecnológica não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_agent_process_orchestration_is_complete():
    assert (
        AGENT_PROCESS_ORCHESTRATION_SOLUTION.solution_id
        == "agent_process_orchestration"
    )

    assert len(
        AGENT_PROCESS_ORCHESTRATION_SOLUTION.areas
    ) == 7

    assert (
        AGENT_PROCESS_ORCHESTRATION_SOLUTION.capability_count
        == 21
    )


def test_agent_process_orchestration_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "agent_process_orchestration"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AGENT_PROCESS_ORCHESTRATION_SOLUTION.status
        is module.status
    )

    assert (
        AGENT_PROCESS_ORCHESTRATION_SOLUTION.integration_type
        == module.integration_type
    )


def test_agent_process_orchestration_lookup():
    assert (
        platform_technology_solution(
            "agent_process_orchestration"
        )
        is AGENT_PROCESS_ORCHESTRATION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("AGENT_PROCESS_ORCHESTRATION_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    agent_solution = getattr(
        module,
        "AGENT_PROCESS_ORCHESTRATION_SOLUTION",
    )

    assert len(solutions) == 2
    assert len(agent_solution.areas) == 7
    assert agent_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 14
    assert total_capabilities == 42

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=2")
    print("TOTAL_TECHNOLOGY_AREAS=14")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=42")
    print("AGENT_PROCESS_ORCHESTRATION_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
