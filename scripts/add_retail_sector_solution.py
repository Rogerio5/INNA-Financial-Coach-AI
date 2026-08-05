"""Adiciona a solução especializada de Lojas e Varejo."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_sector_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_sector_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("retail_sector_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


RETAIL_DEFINITION = """
RETAIL_STORES_SOLUTION = PlatformSectorSolution(
    solution_id="retail_stores",
    icon="🏪",
    title="Lojas e Varejo",
    description=(
        "Solução para catálogo, produtos, vendas, pedidos, "
        "estoque, abastecimento, relacionamento com clientes, "
        "operações omnichannel, entregas e rentabilidade."
    ),
    status=SectorSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        SectorArea(
            area_id="retail_catalog_products",
            title="🏷️ Catálogo e produtos",
            capabilities=(
                SectorCapability(
                    capability_id="retail_product_catalog",
                    title="🏷️ Catálogo inteligente de produtos",
                    description=(
                        "Cadastro centralizado de produtos, categorias, "
                        "marcas, variações, atributos, imagens e preços."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "data_platform_governance",
                        "multimodal_ai",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_product_content",
                    title="📝 Conteúdo e descrição de produtos",
                    description=(
                        "Geração e padronização assistida de descrições, "
                        "características, títulos e conteúdo comercial."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "enterprise_rag",
                        "business_automation",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_pricing_promotions",
                    title="🏷️ Preços, descontos e promoções",
                    description=(
                        "Gestão de preços, descontos, campanhas, regras "
                        "promocionais, margem e períodos de validade."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                        "business_automation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_sales_orders",
            title="🛍️ Vendas e pedidos",
            capabilities=(
                SectorCapability(
                    capability_id="retail_sales_checkout",
                    title="💳 Vendas e frente de caixa",
                    description=(
                        "Operações de venda, pagamento, desconto, troca, "
                        "devolução, cancelamento e fechamento de caixa."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "api_integrations_connectors",
                        "operational_security_resilience",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_order_management",
                    title="📋 Gestão inteligente de pedidos",
                    description=(
                        "Recebimento, separação, aprovação, faturamento, "
                        "expedição, entrega e acompanhamento de pedidos."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_sales_fraud",
                    title="🛡️ Fraudes e anomalias em vendas",
                    description=(
                        "Detecção de transações incomuns, abuso de "
                        "descontos, devoluções suspeitas e divergências."
                    ),
                    technology_dependencies=(
                        "cybersecurity_fraud_prevention",
                        "real_time_event_intelligence",
                        "ai_bias_quality_monitoring",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_inventory_supply",
            title="📦 Estoque e abastecimento",
            capabilities=(
                SectorCapability(
                    capability_id="retail_inventory_control",
                    title="📦 Controle integrado de estoque",
                    description=(
                        "Entradas, saídas, reservas, transferências, "
                        "inventários e disponibilidade por unidade."
                    ),
                    technology_dependencies=(
                        "erp_business_operations",
                        "data_traceability_provenance",
                        "real_time_event_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_smart_replenishment",
                    title="🔄 Reposição e abastecimento inteligente",
                    description=(
                        "Previsão de demanda, ponto de reposição, "
                        "sugestões de compra e transferências de estoque."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_loss_prevention",
                    title="⚠️ Prevenção de perdas no varejo",
                    description=(
                        "Análise de furtos, avarias, divergências, "
                        "rupturas, devoluções e causas de perdas."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "cybersecurity_fraud_prevention",
                        "quality_process_management",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_customer_experience",
            title="🤝 CRM e experiência do cliente",
            capabilities=(
                SectorCapability(
                    capability_id="retail_customer_profile",
                    title="👤 Perfil e inteligência do cliente",
                    description=(
                        "Histórico de compras, preferências, frequência, "
                        "segmentação, comportamento e valor do cliente."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "data_bi_copilot",
                        "enterprise_decision_intelligence",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_loyalty_service",
                    title="🎁 Fidelização e atendimento inteligente",
                    description=(
                        "Programas de fidelidade, benefícios, campanhas, "
                        "feedbacks e suporte personalizado."
                    ),
                    technology_dependencies=(
                        "crm_sales_intelligence",
                        "intelligent_support",
                        "business_automation",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_omnichannel_delivery",
            title="📱 Omnichannel e entregas",
            capabilities=(
                SectorCapability(
                    capability_id="retail_omnichannel_operations",
                    title="📱 Experiência omnichannel",
                    description=(
                        "Integração entre loja física, aplicativo, site, "
                        "marketplace, atendimento e canais de venda."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "digital_experiences_intelligent_interfaces",
                        "api_integrations_connectors",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_delivery_fulfillment",
                    title="🚚 Entregas e atendimento de pedidos",
                    description=(
                        "Separação, retirada em loja, entrega local, "
                        "rastreamento, rotas e confirmação de recebimento."
                    ),
                    technology_dependencies=(
                        "supply_chain_procurement_logistics",
                        "mobility_traffic_transport",
                        "gis_location_intelligence",
                    ),
                ),
            ),
        ),
        SectorArea(
            area_id="retail_analytics_profitability",
            title="📊 Indicadores e rentabilidade",
            capabilities=(
                SectorCapability(
                    capability_id="retail_business_analytics",
                    title="📊 Analytics e indicadores do varejo",
                    description=(
                        "Vendas, conversão, ticket médio, estoque, "
                        "clientes, desempenho e metas operacionais."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                SectorCapability(
                    capability_id="retail_profitability_forecasting",
                    title="📈 Rentabilidade e previsão de demanda",
                    description=(
                        "Margem, custos, rentabilidade por produto, "
                        "unidade, canal e previsão de demanda."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "data_bi_copilot",
                    ),
                ),
            ),
        ),
    ),
)


"""


def create_backup() -> None:
    """Salva cópias dos arquivos antes da alteração."""

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
    """Adiciona Lojas e Varejo ao registro especializado."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "RETAIL_STORES_SOLUTION = PlatformSectorSolution(" in source:
        print("RETAIL_SECTOR_SOLUTION_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_SECTOR_SOLUTIONS: tuple[
    PlatformSectorSolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro especializado não encontrada.")

    source = source.replace(
        registry_anchor,
        RETAIL_DEFINITION + registry_anchor,
        1,
    )

    current_registry_tail = """    PET_SHOPS_VETERINARY_SOLUTION,
    SUPERMARKETS_WHOLESALE_SOLUTION,
)"""

    updated_registry_tail = """    PET_SHOPS_VETERINARY_SOLUTION,
    SUPERMARKETS_WHOLESALE_SOLUTION,
    RETAIL_STORES_SOLUTION,
)"""

    if current_registry_tail not in source:
        raise RuntimeError("Final atual do registro especializado não encontrado.")

    source = source.replace(
        current_registry_tail,
        updated_registry_tail,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("RETAIL_SECTOR_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes do registro especializado."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_retail_solution_is_complete" in source:
        print("RETAIL_SECTOR_TESTS_ALREADY_PRESENT=OK")
        return

    import_anchor = "    PET_SHOPS_VETERINARY_SOLUTION,\n"

    import_replacement = (
        "    PET_SHOPS_VETERINARY_SOLUTION,\n    RETAIL_STORES_SOLUTION,\n"
    )

    if import_anchor not in source:
        raise RuntimeError("Âncora de importação dos testes não encontrada.")

    source = source.replace(
        import_anchor,
        import_replacement,
        1,
    )

    old_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 4"

    new_count = "assert len(PLATFORM_SECTOR_SOLUTIONS) == 5"

    if old_count not in source:
        raise RuntimeError("Contagem atual de quatro soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    expected_anchor = """        "supermarkets_wholesale",
    }"""

    expected_replacement = """        "supermarkets_wholesale",
        "retail_stores",
    }"""

    if expected_anchor not in source:
        raise RuntimeError("Conjunto esperado de soluções não encontrado.")

    source = source.replace(
        expected_anchor,
        expected_replacement,
        1,
    )

    source += """


def test_retail_solution_is_complete():
    assert (
        RETAIL_STORES_SOLUTION.solution_id
        == "retail_stores"
    )
    assert (
        RETAIL_STORES_SOLUTION.status
        is SectorSolutionStatus.PLANNED
    )
    assert (
        RETAIL_STORES_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        RETAIL_STORES_SOLUTION.areas
    ) == 6
    assert (
        RETAIL_STORES_SOLUTION.capability_count
        == 15
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("RETAIL_SECTOR_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma a estrutura criada."""

    from src.platform_sector_solutions import (
        PLATFORM_SECTOR_SOLUTIONS,
        RETAIL_STORES_SOLUTION,
        platform_sector_solution,
    )

    assert len(PLATFORM_SECTOR_SOLUTIONS) == 5

    assert platform_sector_solution("retail_stores") is RETAIL_STORES_SOLUTION

    assert len(RETAIL_STORES_SOLUTION.areas) == 6

    assert RETAIL_STORES_SOLUTION.capability_count == 15

    total_areas = sum(len(solution.areas) for solution in PLATFORM_SECTOR_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_SECTOR_SOLUTIONS
    )

    assert total_areas == 33
    assert total_capabilities == 86

    print("SPECIALIZED_SECTOR_SOLUTIONS=5")
    print("TOTAL_SECTOR_AREAS=33")
    print("TOTAL_SECTOR_CAPABILITIES=86")
    print("RETAIL_SECTOR_EXPANSION_VALIDATED=OK")


create_backup()
update_registry()
update_tests()
validate_result()
