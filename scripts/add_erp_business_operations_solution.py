"""Adiciona ERP e Operações Empresariais ao registro empresarial."""

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
    / ("erp_business_operations_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


ERP_BUSINESS_OPERATIONS_DEFINITION = """
ERP_BUSINESS_OPERATIONS_SOLUTION = PlatformBusinessSolution(
    solution_id="erp_business_operations",
    icon="🏢",
    title="ERP e Operações Empresariais",
    description=(
        "Solução empresarial para cadastros mestres, vendas, "
        "compras, estoque, faturamento, finanças, operações, "
        "recursos, controles, integrações e indicadores."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="erp_master_data_organization",
            title="🗂️ Cadastros mestres e organização",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_companies_business_units",
                    title="🏢 Empresas, unidades e estruturas",
                    description=(
                        "Cadastro de empresas, filiais, departamentos, "
                        "centros de responsabilidade e estruturas operacionais."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_customers_suppliers_partners",
                    title="🤝 Clientes, fornecedores e parceiros",
                    description=(
                        "Organização de cadastros, contatos, documentos, "
                        "condições, relacionamentos e situações cadastrais."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "supply_chain_procurement_logistics",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_products_services_catalog",
                    title="📦 Produtos, serviços e catálogos",
                    description=(
                        "Gestão de produtos, serviços, categorias, unidades, "
                        "preços, características e regras empresariais."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "knowledge_graph_semantic_ai",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="erp_sales_purchases_orders",
            title="🛒 Vendas, compras e pedidos",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_sales_orders",
                    title="🛒 Pedidos e operações de venda",
                    description=(
                        "Registro de propostas, pedidos, condições, itens, "
                        "aprovações, separação e acompanhamento."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "business_automation",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_purchase_requests_orders",
                    title="🧾 Solicitações e pedidos de compra",
                    description=(
                        "Gestão de requisições, cotações, aprovações, "
                        "fornecedores, pedidos e recebimentos."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "agent_process_orchestration",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_commercial_conditions",
                    title="💼 Condições e regras comerciais",
                    description=(
                        "Configuração de preços, descontos, limites, "
                        "condições de pagamento e regras de aprovação."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "financial_solutions",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="erp_inventory_warehouse_logistics",
            title="📦 Estoque, armazéns e movimentações",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_inventory_control",
                    title="📦 Controle de estoques",
                    description=(
                        "Acompanhamento de saldos, entradas, saídas, "
                        "reservas, transferências, lotes e localizações."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "real_time_event_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_warehouse_operations",
                    title="🏭 Operações de armazenagem",
                    description=(
                        "Gestão de recebimento, conferência, endereçamento, "
                        "separação, inventário e expedição."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "business_automation",
                        "iot_edge_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_material_traceability",
                    title="🔎 Rastreabilidade de materiais",
                    description=(
                        "Registro da origem, movimentações, lotes, "
                        "responsáveis, documentos e destinos."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "document_ai",
                        "quality_process_management",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="erp_finance_billing_treasury",
            title="💰 Finanças, faturamento e tesouraria",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_accounts_payable_receivable",
                    title="💳 Contas a pagar e receber",
                    description=(
                        "Controle de títulos, vencimentos, recebimentos, "
                        "pagamentos, baixas, atrasos e responsáveis."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "business_automation",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_billing_documents",
                    title="🧾 Faturamento e documentos",
                    description=(
                        "Geração e controle de cobranças, faturamentos, "
                        "documentos, aprovações e integrações."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "financial_solutions",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_cash_reconciliation",
                    title="🏦 Caixa e conciliação",
                    description=(
                        "Acompanhamento de movimentações financeiras, "
                        "saldos, conciliações, divergências e previsões."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="erp_production_services_resources",
            title="⚙️ Produção, serviços e recursos",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_production_work_orders",
                    title="🏭 Planejamento e ordens de produção",
                    description=(
                        "Planejamento de demandas, materiais, etapas, "
                        "ordens, apontamentos, perdas e resultados."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "asset_management_smart_maintenance",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_service_work_orders",
                    title="🛠️ Ordens e execução de serviços",
                    description=(
                        "Gestão de solicitações, atividades, equipes, "
                        "materiais, prazos e conclusão de serviços."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "asset_management_smart_maintenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_capacity_resource_planning",
                    title="📅 Capacidade e planejamento de recursos",
                    description=(
                        "Análise de equipes, equipamentos, materiais, "
                        "disponibilidade, carga e necessidades futuras."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="erp_controls_analytics_integrations",
            title="📊 Controles, analytics e integrações",
            capabilities=(
                BusinessCapability(
                    capability_id="erp_approvals_access_controls",
                    title="🔐 Aprovações e controles de acesso",
                    description=(
                        "Definição de permissões, responsabilidades, "
                        "alçadas, aprovações e separação de funções."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "technology_governance_policy_compliance",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_operational_dashboards",
                    title="📊 Indicadores operacionais e executivos",
                    description=(
                        "Acompanhamento de vendas, compras, estoque, "
                        "finanças, produção, serviços e produtividade."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="erp_integrations_audit",
                    title="🔌 Integrações, auditoria e rastreabilidade",
                    description=(
                        "Integração com sistemas e registro de eventos, "
                        "alterações, usuários, documentos e operações."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "data_traceability_provenance",
                        "operational_security_resilience",
                    ),
                ),
            ),
        ),
    ),
)


"""


def validate_prerequisites() -> None:
    """Valida arquivos e ID do módulo antes da alteração."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro empresarial não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes empresariais não encontrados.")

    from src.platform_modules import PLATFORM_MODULE_BY_ID

    if "erp_business_operations" not in PLATFORM_MODULE_BY_ID:
        raise RuntimeError(
            "O card erp_business_operations não existe no registro principal."
        )

    print("ERP_BUSINESS_OPERATIONS_PREREQUISITES=OK")


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
    """Adiciona ERP e Operações Empresariais."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ERP_BUSINESS_OPERATIONS_SOLUTION = PlatformBusinessSolution(" in source:
        print("ERP_BUSINESS_OPERATIONS_ALREADY_PRESENT=OK")
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
        (ERP_BUSINESS_OPERATIONS_DEFINITION + registry_anchor),
        1,
    )

    old_registry = """    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
    LEGAL_COMPLIANCE_SOLUTION,
)"""

    new_registry = """    CRM_CUSTOMER_EXPERIENCE_SOLUTION,
    LEGAL_COMPLIANCE_SOLUTION,
    ERP_BUSINESS_OPERATIONS_SOLUTION,
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

    print("ERP_BUSINESS_OPERATIONS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_erp_business_operations_solution_is_complete" in source:
        print("ERP_BUSINESS_OPERATIONS_TESTS_ALREADY_PRESENT=OK")
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

    if "ERP_BUSINESS_OPERATIONS_SOLUTION" not in import_block:
        source = (
            source[:import_end]
            + ("    ERP_BUSINESS_OPERATIONS_SOLUTION,\n")
            + source[import_end:]
        )

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 7"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 8"

    if old_count not in source:
        raise RuntimeError("Contagem atual de sete soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_erp_business_operations_solution_is_complete():
    assert (
        ERP_BUSINESS_OPERATIONS_SOLUTION.solution_id
        == "erp_business_operations"
    )
    assert (
        ERP_BUSINESS_OPERATIONS_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        ERP_BUSINESS_OPERATIONS_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        ERP_BUSINESS_OPERATIONS_SOLUTION.areas
    ) == 6
    assert (
        ERP_BUSINESS_OPERATIONS_SOLUTION.capability_count
        == 18
    )


def test_erp_business_operations_solution_lookup():
    assert (
        platform_business_solution(
            "erp_business_operations"
        )
        is ERP_BUSINESS_OPERATIONS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ERP_BUSINESS_OPERATIONS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        ERP_BUSINESS_OPERATIONS_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 8

    assert (
        platform_business_solution("erp_business_operations")
        is ERP_BUSINESS_OPERATIONS_SOLUTION
    )

    assert len(ERP_BUSINESS_OPERATIONS_SOLUTION.areas) == 6

    assert ERP_BUSINESS_OPERATIONS_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 48
    assert total_capabilities == 143

    print("SPECIALIZED_BUSINESS_SOLUTIONS=8")
    print("TOTAL_BUSINESS_AREAS=48")
    print("TOTAL_BUSINESS_CAPABILITIES=143")
    print("ERP_BUSINESS_OPERATIONS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
