"""Adiciona Soluções Financeiras ao registro empresarial."""

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
    / ("financial_business_solution_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


FINANCIAL_SOLUTION_DEFINITION = """
FINANCIAL_SOLUTIONS_SOLUTION = PlatformBusinessSolution(
    solution_id="financial_solutions",
    icon="💰",
    title="Soluções Financeiras",
    description=(
        "Solução empresarial para organização financeira, "
        "orçamento, fluxo de caixa, transações, conciliação, "
        "crédito, riscos, segurança, planejamento e analytics."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="financial_profiles_accounts",
            title="👤 Perfis, contas e organização financeira",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_customer_profile",
                    title="👤 Perfil e contexto financeiro",
                    description=(
                        "Organização de perfil, objetivos, preferências, "
                        "responsabilidades e contexto financeiro autorizado."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "privacy_data_protection_lgpd",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_accounts_connections",
                    title="🏦 Contas e conexões financeiras",
                    description=(
                        "Integração controlada com contas, sistemas, "
                        "fontes de dados e serviços financeiros autorizados."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "zero_trust_identity_access",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_categories_rules",
                    title="🏷️ Categorias e regras financeiras",
                    description=(
                        "Configuração de categorias, centros de custo, "
                        "regras de classificação e estruturas financeiras."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "business_automation",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="financial_budget_cash_flow",
            title="📊 Orçamento e fluxo de caixa",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_budget_management",
                    title="📊 Planejamento e controle orçamentário",
                    description=(
                        "Definição de receitas, despesas, limites, "
                        "metas, períodos e acompanhamento do orçamento."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_cash_flow_projection",
                    title="📈 Fluxo de caixa e projeções",
                    description=(
                        "Acompanhamento de entradas, saídas, saldos, "
                        "vencimentos, tendências e projeções."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_scenarios_goals",
                    title="🎯 Metas e simulação de cenários",
                    description=(
                        "Comparação de cenários, objetivos, prazos, "
                        "restrições e possíveis impactos financeiros."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "enterprise_decision_intelligence",
                        "tools_analytics",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="financial_transactions_reconciliation",
            title="💳 Transações, documentos e conciliação",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_transaction_management",
                    title="💳 Gestão de transações",
                    description=(
                        "Organização de lançamentos, pagamentos, "
                        "recebimentos, transferências e movimentações."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "data_platform_governance",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_document_processing",
                    title="🧾 Processamento de documentos financeiros",
                    description=(
                        "Captura e extração de informações de faturas, "
                        "comprovantes, extratos e outros documentos."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "multimodal_ai",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_reconciliation",
                    title="🔄 Conciliação e tratamento de divergências",
                    description=(
                        "Comparação entre registros, documentos, contas, "
                        "valores e eventos para localizar divergências."
                    ),
                    technology_dependencies=(
                        "software_testing_quality_reliability",
                        "business_automation",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="financial_credit_debt_risk",
            title="⚖️ Crédito, dívidas e riscos",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_debt_obligations",
                    title="📅 Dívidas, parcelas e obrigações",
                    description=(
                        "Acompanhamento de contratos, parcelas, juros, "
                        "prazos, vencimentos e compromissos financeiros."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "real_time_event_intelligence",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_credit_analysis_support",
                    title="🔎 Apoio à análise de crédito",
                    description=(
                        "Consolidação de dados, critérios, evidências "
                        "e explicações para análise com revisão humana."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "model_explainability_interpretability",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_risk_monitoring",
                    title="⚠️ Monitoramento de riscos financeiros",
                    description=(
                        "Identificação de atrasos, concentração, "
                        "variações, exposição e sinais de risco."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="financial_security_compliance",
            title="🔐 Segurança, prevenção e conformidade",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_anomaly_detection",
                    title="🛡️ Anomalias e movimentações suspeitas",
                    description=(
                        "Detecção assistida de padrões incomuns, "
                        "divergências e eventos que precisam de revisão."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "ai_evaluation_benchmarks_red_team",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_access_privacy",
                    title="🔐 Identidade, acesso e privacidade",
                    description=(
                        "Proteção de dados financeiros, permissões, "
                        "autenticação, mascaramento e acesso controlado."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "privacy_data_protection_lgpd",
                        "privacy_enhancing_technologies",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_compliance_audit",
                    title="🧾 Conformidade, auditoria e evidências",
                    description=(
                        "Registro de ações, alterações, decisões, "
                        "responsáveis, documentos e evidências financeiras."
                    ),
                    technology_dependencies=(
                        "legal_compliance",
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="financial_intelligence_governance",
            title="🧠 Inteligência, orientação e governança",
            capabilities=(
                BusinessCapability(
                    capability_id="financial_dashboards_indicators",
                    title="📊 Indicadores e dashboards financeiros",
                    description=(
                        "Acompanhamento de receitas, despesas, saldos, "
                        "orçamento, dívidas, riscos e resultados."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_grounded_guidance",
                    title="🧠 Orientação financeira fundamentada",
                    description=(
                        "Explicações e orientações baseadas em dados, "
                        "documentos e regras autorizadas, sem execução automática."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                BusinessCapability(
                    capability_id="financial_human_review_governance",
                    title="👤 Revisão humana e governança de decisões",
                    description=(
                        "Encaminhamento de situações sensíveis para "
                        "análise, aprovação, correção ou rejeição humana."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "model_explainability_interpretability",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
    ),
)


"""


def validate_prerequisites() -> None:
    """Valida arquivos e o card principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro empresarial não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes empresariais não encontrados.")

    from src.platform_modules import PLATFORM_MODULE_BY_ID

    module_id = "financial_solutions"

    if module_id not in PLATFORM_MODULE_BY_ID:
        raise RuntimeError(f"O card {module_id} não existe no registro principal.")

    print("FINANCIAL_SOLUTIONS_PREREQUISITES=OK")


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
    """Adiciona Soluções Financeiras ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "FINANCIAL_SOLUTIONS_SOLUTION = PlatformBusinessSolution(" in source:
        print("FINANCIAL_SOLUTIONS_ALREADY_PRESENT=OK")
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
        FINANCIAL_SOLUTION_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
    HR_PEOPLE_ANALYTICS_SOLUTION,
)"""

    new_registry = """    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
    HR_PEOPLE_ANALYTICS_SOLUTION,
    FINANCIAL_SOLUTIONS_SOLUTION,
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

    print("FINANCIAL_SOLUTIONS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_financial_solutions_solution_is_complete" in source:
        print("FINANCIAL_SOLUTIONS_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_business_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Bloco de importações empresariais não encontrado.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final do bloco de importações não encontrado.")

    import_block = source[import_start:import_end]

    solution_name = "FINANCIAL_SOLUTIONS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 10"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 11"

    if old_count not in source:
        raise RuntimeError("Contagem atual de dez soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_financial_solutions_solution_is_complete():
    assert (
        FINANCIAL_SOLUTIONS_SOLUTION.solution_id
        == "financial_solutions"
    )
    assert (
        FINANCIAL_SOLUTIONS_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        FINANCIAL_SOLUTIONS_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        FINANCIAL_SOLUTIONS_SOLUTION.areas
    ) == 6
    assert (
        FINANCIAL_SOLUTIONS_SOLUTION.capability_count
        == 18
    )


def test_financial_solutions_solution_lookup():
    assert (
        platform_business_solution(
            "financial_solutions"
        )
        is FINANCIAL_SOLUTIONS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("FINANCIAL_SOLUTIONS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        FINANCIAL_SOLUTIONS_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 11

    assert (
        platform_business_solution("financial_solutions")
        is FINANCIAL_SOLUTIONS_SOLUTION
    )

    assert len(FINANCIAL_SOLUTIONS_SOLUTION.areas) == 6

    assert FINANCIAL_SOLUTIONS_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 66
    assert total_capabilities == 197

    print("SPECIALIZED_BUSINESS_SOLUTIONS=11")
    print("TOTAL_BUSINESS_AREAS=66")
    print("TOTAL_BUSINESS_CAPABILITIES=197")
    print("FINANCIAL_SOLUTIONS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
