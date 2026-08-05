"""Adiciona Supply Chain, Compras e Logística ao registro empresarial."""

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
    / ("supply_chain_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


SUPPLY_CHAIN_DEFINITION = """
SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION = PlatformBusinessSolution(
    solution_id="supply_chain_procurement_logistics",
    icon="📦",
    title="Supply Chain, Compras e Logística",
    description=(
        "Solução empresarial para planejamento de demanda, "
        "compras, fornecedores, estoques, armazenagem, transporte, "
        "rastreabilidade, riscos, custos e desempenho logístico."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="supply_chain_demand_planning",
            title="📈 Demanda e planejamento integrado",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_demand_forecasting",
                    title="📈 Previsão de demanda",
                    description=(
                        "Projeção de volumes, sazonalidades, tendências, "
                        "variações e necessidades futuras."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_integrated_planning",
                    title="🧩 Planejamento integrado de operações",
                    description=(
                        "Alinhamento entre demanda, compras, estoques, "
                        "capacidade, vendas e operações."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "erp_business_operations",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_inventory_policies",
                    title="📦 Políticas e níveis de estoque",
                    description=(
                        "Definição de estoque mínimo, máximo, segurança, "
                        "cobertura, reposição e critérios de abastecimento."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "data_bi_copilot",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="supply_chain_procurement_suppliers",
            title="🛒 Compras e fornecedores",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_supplier_management",
                    title="🤝 Cadastro e qualificação de fornecedores",
                    description=(
                        "Gestão de dados, documentos, categorias, riscos, "
                        "desempenho e situação dos fornecedores."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "document_ai",
                        "legal_compliance",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_sourcing_quotations",
                    title="📑 Cotações e seleção de fornecedores",
                    description=(
                        "Gestão de solicitações, propostas, comparações, "
                        "critérios, negociações e decisões de compra."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "business_automation",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_purchase_workflows",
                    title="✅ Aprovações e pedidos de compra",
                    description=(
                        "Automação de requisições, alçadas, aprovações, "
                        "pedidos, prazos e acompanhamento."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "agent_process_orchestration",
                        "business_automation",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="supply_chain_inventory_warehousing",
            title="🏭 Estoques e armazenagem",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_inventory_visibility",
                    title="👁️ Visibilidade de estoques",
                    description=(
                        "Acompanhamento de saldos, reservas, lotes, "
                        "localizações, entradas, saídas e disponibilidade."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "real_time_event_intelligence",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_warehouse_operations",
                    title="🏭 Operações de armazenagem",
                    description=(
                        "Gestão de recebimento, conferência, endereçamento, "
                        "separação, inventário e expedição."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "iot_edge_intelligence",
                        "erp_business_operations",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_replenishment_allocation",
                    title="🔄 Reposição e alocação de materiais",
                    description=(
                        "Cálculo e execução de reposições, transferências, "
                        "prioridades e distribuição entre unidades."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "enterprise_decision_intelligence",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="supply_chain_transport_distribution",
            title="🚚 Transporte e distribuição",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_shipment_planning",
                    title="🚚 Planejamento de cargas e entregas",
                    description=(
                        "Consolidação de pedidos, cargas, veículos, "
                        "janelas, destinos e capacidade de transporte."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "erp_business_operations",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_delivery_tracking",
                    title="📍 Rastreamento de entregas",
                    description=(
                        "Acompanhamento de coleta, trânsito, ocorrências, "
                        "previsão de chegada e confirmação de entrega."
                    ),
                    technology_dependencies=(
                        "real_time_event_intelligence",
                        "iot_edge_intelligence",
                        "api_integrations_connectors",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_route_freight_optimization",
                    title="🧭 Otimização de rotas e fretes",
                    description=(
                        "Comparação de rotas, custos, prazos, capacidade, "
                        "restrições e alternativas de transporte."
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
            area_id="supply_chain_traceability_quality_risks",
            title="🔎 Rastreabilidade, qualidade e riscos",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_end_to_end_traceability",
                    title="🔎 Rastreabilidade ponta a ponta",
                    description=(
                        "Registro da origem, movimentações, lotes, "
                        "documentos, responsáveis e destinos."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "document_ai",
                        "erp_business_operations",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_quality_compliance",
                    title="✅ Qualidade e conformidade logística",
                    description=(
                        "Controle de inspeções, condições, desvios, "
                        "documentos, requisitos e ações corretivas."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "legal_compliance",
                        "document_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_disruption_risk_management",
                    title="⚠️ Riscos e interrupções da cadeia",
                    description=(
                        "Identificação de atrasos, indisponibilidades, "
                        "dependências críticas, impactos e alternativas."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "real_time_event_intelligence",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="supply_chain_analytics_optimization",
            title="📊 Analytics e otimização",
            capabilities=(
                BusinessCapability(
                    capability_id="supply_chain_performance_dashboards",
                    title="📊 Indicadores da cadeia de suprimentos",
                    description=(
                        "Acompanhamento de demanda, compras, estoques, "
                        "entregas, custos, prazos e nível de serviço."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_cost_service_analysis",
                    title="💰 Custos e nível de serviço",
                    description=(
                        "Análise de custos de compra, armazenagem, "
                        "estoque, transporte, atrasos e atendimento."
                    ),
                    technology_dependencies=(
                        "financial_solutions",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="supply_chain_scenario_optimization",
                    title="🧪 Simulação e otimização de cenários",
                    description=(
                        "Comparação de redes, capacidades, estoques, "
                        "fornecedores, transportes e estratégias."
                    ),
                    technology_dependencies=(
                        "simulation_optimization_operations_research",
                        "scientific_computing_engineering",
                        "enterprise_decision_intelligence",
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

    module_id = "supply_chain_procurement_logistics"

    if module_id not in PLATFORM_MODULE_BY_ID:
        raise RuntimeError(f"O card {module_id} não existe no registro principal.")

    print("SUPPLY_CHAIN_PREREQUISITES=OK")


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
    """Adiciona Supply Chain ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if (
        "SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION = "
        "PlatformBusinessSolution(" in source
    ):
        print("SUPPLY_CHAIN_SOLUTION_ALREADY_PRESENT=OK")
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
        SUPPLY_CHAIN_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    LEGAL_COMPLIANCE_SOLUTION,
    ERP_BUSINESS_OPERATIONS_SOLUTION,
)"""

    new_registry = """    LEGAL_COMPLIANCE_SOLUTION,
    ERP_BUSINESS_OPERATIONS_SOLUTION,
    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
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

    print("SUPPLY_CHAIN_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_supply_chain_solution_is_complete" in source:
        print("SUPPLY_CHAIN_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 8"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 9"

    if old_count not in source:
        raise RuntimeError("Contagem atual de oito soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_supply_chain_solution_is_complete():
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.solution_id
        == "supply_chain_procurement_logistics"
    )
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.areas
    ) == 6
    assert (
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.capability_count
        == 18
    )


def test_supply_chain_solution_lookup():
    assert (
        platform_business_solution(
            "supply_chain_procurement_logistics"
        )
        is SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SUPPLY_CHAIN_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
        SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 9

    assert (
        platform_business_solution("supply_chain_procurement_logistics")
        is SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION
    )

    assert len(SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.areas) == 6

    assert SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 54
    assert total_capabilities == 161

    print("SPECIALIZED_BUSINESS_SOLUTIONS=9")
    print("TOTAL_BUSINESS_AREAS=54")
    print("TOTAL_BUSINESS_CAPABILITIES=161")
    print("SUPPLY_CHAIN_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
