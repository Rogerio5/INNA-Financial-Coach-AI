from __future__ import annotations

import re
from pathlib import Path


SOURCE_PATH = Path("src/platform_sector_solutions.py")
TEST_PATH = Path("tests/unit/test_platform_sector_solutions.py")


SOLUTIONS = (
    {
        "constant": "PET_SHOPS_VETERINARY_SOLUTION",
        "solution_id": "pet_shops_veterinary_services",
        "icon": "🐾",
        "title": "Pet Shops e Serviços Veterinários",
        "description": (
            "Solução para atendimento, agenda, serviços, saúde veterinária, "
            "estoque, pagamentos e relacionamento com tutores."
        ),
        "areas": (
            {
                "area_id": "pet_customer_registration",
                "title": "👤 Atendimento, tutores e animais",
                "capabilities": (
                    (
                        "pet_tutor_registration",
                        "👤 Cadastro de tutores e animais",
                        "Cadastro centralizado de tutores, animais, contatos, preferências e histórico.",
                        (
                            "crm_sales_intelligence",
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    (
                        "pet_digital_profile",
                        "🐕 Perfil digital do animal",
                        "Organização de espécie, raça, idade, peso, características, alertas e informações gerais.",
                        (
                            "document_ai",
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    (
                        "pet_service_history",
                        "📋 Histórico de atendimentos",
                        "Linha do tempo de consultas, serviços, compras, observações e ocorrências.",
                        (
                            "data_traceability_provenance",
                            "crm_sales_intelligence",
                            "tools_analytics",
                        ),
                    ),
                ),
            },
            {
                "area_id": "pet_schedule_services",
                "title": "📅 Agenda e serviços",
                "capabilities": (
                    (
                        "pet_intelligent_schedule",
                        "📅 Agenda inteligente",
                        "Agendamento de consultas, banho, tosa, vacinas, retornos e serviços recorrentes.",
                        (
                            "business_automation",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                    (
                        "pet_bath_grooming",
                        "🛁 Banho, tosa e estética animal",
                        "Gestão de serviços, profissionais, duração, preferências e acompanhamento da execução.",
                        (
                            "erp_business_operations",
                            "business_automation",
                            "tools_analytics",
                        ),
                    ),
                    (
                        "pet_reminders_notifications",
                        "🔔 Lembretes e notificações",
                        "Avisos de agendamentos, retornos, vacinas, medicações e serviços pendentes.",
                        (
                            "intelligent_support",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            },
            {
                "area_id": "veterinary_health",
                "title": "🩺 Saúde veterinária",
                "capabilities": (
                    (
                        "veterinary_medical_records",
                        "🩺 Prontuário veterinário",
                        "Registro de consultas, avaliações, exames, diagnósticos e orientações profissionais.",
                        (
                            "document_ai",
                            "privacy_data_protection_lgpd",
                            "data_traceability_provenance",
                        ),
                    ),
                    (
                        "veterinary_vaccination_control",
                        "💉 Vacinação e prevenção",
                        "Controle de vacinas, antiparasitários, protocolos preventivos e datas futuras.",
                        (
                            "business_automation",
                            "real_time_event_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    (
                        "veterinary_exams_documents",
                        "📄 Exames e documentos veterinários",
                        "Organização e análise assistida de exames, laudos, receitas e documentos.",
                        (
                            "document_ai",
                            "multimodal_ai",
                            "enterprise_rag",
                        ),
                    ),
                ),
            },
            {
                "area_id": "pet_inventory_pharmacy",
                "title": "📦 Estoque e farmácia",
                "capabilities": (
                    (
                        "pet_inventory_management",
                        "📦 Estoque de produtos e medicamentos",
                        "Controle de rações, acessórios, medicamentos, lotes, validade e disponibilidade.",
                        (
                            "erp_business_operations",
                            "supply_chain_procurement_logistics",
                            "data_traceability_provenance",
                        ),
                    ),
                    (
                        "pet_stock_replenishment",
                        "🔄 Reposição inteligente",
                        "Previsão de demanda, ponto de reposição, alertas e sugestões de compra.",
                        (
                            "enterprise_decision_intelligence",
                            "real_time_event_intelligence",
                            "supply_chain_procurement_logistics",
                        ),
                    ),
                ),
            },
            {
                "area_id": "pet_finance_payments",
                "title": "💰 Financeiro e pagamentos",
                "capabilities": (
                    (
                        "pet_billing_payments",
                        "💳 Cobranças e pagamentos",
                        "Orçamentos, cobranças, recebimentos, parcelamentos e conciliação.",
                        (
                            "financial_solutions",
                            "erp_business_operations",
                            "api_integrations_connectors",
                        ),
                    ),
                    (
                        "pet_financial_indicators",
                        "📊 Indicadores financeiros",
                        "Receita, custos, margem, ticket médio, inadimplência e rentabilidade.",
                        (
                            "data_bi_copilot",
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            },
            {
                "area_id": "pet_relationship_loyalty",
                "title": "🤝 Relacionamento e fidelização",
                "capabilities": (
                    (
                        "pet_customer_relationship",
                        "🤝 Relacionamento com tutores",
                        "Comunicação, histórico, preferências, feedbacks e atendimento personalizado.",
                        (
                            "crm_sales_intelligence",
                            "intelligent_support",
                            "multimodal_ai",
                        ),
                    ),
                    (
                        "pet_loyalty_campaigns",
                        "🎁 Fidelidade e campanhas",
                        "Programas de pontos, campanhas, ofertas e segmentação de clientes.",
                        (
                            "crm_sales_intelligence",
                            "enterprise_decision_intelligence",
                            "business_automation",
                        ),
                    ),
                ),
            },
        ),
    },
    {
        "constant": "SUPERMARKETS_WHOLESALE_SOLUTION",
        "solution_id": "supermarkets_wholesale",
        "icon": "🛒",
        "title": "Supermercados e Atacado",
        "description": (
            "Solução para compras, fornecedores, estoque, validade, preços, "
            "vendas, reposição, clientes, perdas e rentabilidade."
        ),
        "areas": (
            {
                "area_id": "supermarket_procurement_suppliers",
                "title": "🤝 Compras e fornecedores",
                "capabilities": (
                    (
                        "supplier_management",
                        "🤝 Gestão de fornecedores",
                        "Cadastro, desempenho, prazos, condições, qualidade e histórico de fornecedores.",
                        (
                            "supply_chain_procurement_logistics",
                            "erp_business_operations",
                            "data_platform_governance",
                        ),
                    ),
                    (
                        "intelligent_procurement",
                        "🧠 Compras inteligentes",
                        "Sugestões de compra baseadas em demanda, estoque, sazonalidade e prazo.",
                        (
                            "enterprise_decision_intelligence",
                            "scientific_computing_engineering",
                            "tools_analytics",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_inventory_expiration",
                "title": "📦 Estoque e validade",
                "capabilities": (
                    (
                        "supermarket_inventory_control",
                        "📦 Controle de estoque",
                        "Entradas, saídas, transferências, inventário, disponibilidade e divergências.",
                        (
                            "erp_business_operations",
                            "data_traceability_provenance",
                            "real_time_event_intelligence",
                        ),
                    ),
                    (
                        "product_expiration_control",
                        "⏳ Controle de validade e lotes",
                        "Monitoramento de validade, lotes, alertas, rastreabilidade e prevenção de perdas.",
                        (
                            "data_traceability_provenance",
                            "real_time_event_intelligence",
                            "business_automation",
                        ),
                    ),
                    (
                        "smart_shelf_monitoring",
                        "👁️ Monitoramento inteligente de gôndolas",
                        "Identificação de ruptura, organização, disponibilidade e exposição de produtos.",
                        (
                            "computer_vision_video_analytics",
                            "iot_edge_intelligence",
                            "multimodal_ai",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_pricing_promotions",
                "title": "🏷️ Preços e promoções",
                "capabilities": (
                    (
                        "intelligent_pricing",
                        "🏷️ Precificação inteligente",
                        "Análise de custos, margem, concorrência, estoque e demanda para apoiar preços.",
                        (
                            "enterprise_decision_intelligence",
                            "data_bi_copilot",
                            "scientific_computing_engineering",
                        ),
                    ),
                    (
                        "promotion_management",
                        "📣 Promoções e campanhas",
                        "Planejamento, segmentação, execução e avaliação de campanhas promocionais.",
                        (
                            "crm_sales_intelligence",
                            "business_automation",
                            "tools_analytics",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_sales_checkout",
                "title": "💳 Vendas e frente de caixa",
                "capabilities": (
                    (
                        "checkout_sales_operations",
                        "💳 Operações de venda e caixa",
                        "Vendas, pagamentos, cancelamentos, descontos, operadores e fechamento de caixa.",
                        (
                            "erp_business_operations",
                            "api_integrations_connectors",
                            "operational_security_resilience",
                        ),
                    ),
                    (
                        "checkout_fraud_anomalies",
                        "🛡️ Fraudes e anomalias no caixa",
                        "Detecção de comportamentos incomuns, perdas, cancelamentos e operações suspeitas.",
                        (
                            "cybersecurity_fraud_prevention",
                            "real_time_event_intelligence",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_replenishment_logistics",
                "title": "🚚 Logística e reposição",
                "capabilities": (
                    (
                        "automatic_replenishment",
                        "🔄 Reposição automática",
                        "Sugestões e alertas de reposição conforme vendas, estoque, demanda e prazos.",
                        (
                            "supply_chain_procurement_logistics",
                            "enterprise_decision_intelligence",
                            "real_time_event_intelligence",
                        ),
                    ),
                    (
                        "distribution_logistics",
                        "🚚 Distribuição e logística",
                        "Centros de distribuição, entregas, rotas, transferências e acompanhamento logístico.",
                        (
                            "mobility_traffic_transport",
                            "gis_location_intelligence",
                            "supply_chain_procurement_logistics",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_customers_loyalty",
                "title": "👥 Clientes e fidelidade",
                "capabilities": (
                    (
                        "supermarket_customer_intelligence",
                        "👥 Inteligência de clientes",
                        "Segmentação, perfil de compra, frequência, preferências e comportamento.",
                        (
                            "crm_sales_intelligence",
                            "data_bi_copilot",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    (
                        "supermarket_loyalty_program",
                        "🎁 Programa de fidelidade",
                        "Pontos, benefícios, ofertas personalizadas e acompanhamento de engajamento.",
                        (
                            "crm_sales_intelligence",
                            "business_automation",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            },
            {
                "area_id": "supermarket_losses_profitability",
                "title": "📊 Dados, perdas e rentabilidade",
                "capabilities": (
                    (
                        "retail_loss_prevention",
                        "⚠️ Prevenção de perdas",
                        "Análise de quebras, vencimentos, furtos, divergências e causas de perdas.",
                        (
                            "computer_vision_video_analytics",
                            "cybersecurity_fraud_prevention",
                            "quality_process_management",
                        ),
                    ),
                    (
                        "supermarket_profitability",
                        "📈 Margem e rentabilidade",
                        "Margem por produto, categoria, loja, período e perfil de cliente.",
                        (
                            "data_bi_copilot",
                            "tools_analytics",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            },
        ),
    },
)


def render_solution(solution: dict[str, object]) -> str:
    lines = [
        f"{solution['constant']} = PlatformSectorSolution(",
        f"    solution_id={solution['solution_id']!r},",
        f"    icon={solution['icon']!r},",
        f"    title={solution['title']!r},",
        f"    description={solution['description']!r},",
        "    status=SectorSolutionStatus.PLANNED,",
        '    integration_type="hybrid",',
        "    areas=(",
    ]

    for area in solution["areas"]:
        lines.extend(
            [
                "        SectorArea(",
                f"            area_id={area['area_id']!r},",
                f"            title={area['title']!r},",
                "            capabilities=(",
            ]
        )

        for capability_id, title, description, dependencies in area["capabilities"]:
            lines.extend(
                [
                    "                SectorCapability(",
                    f"                    capability_id={capability_id!r},",
                    f"                    title={title!r},",
                    f"                    description={description!r},",
                    "                    technology_dependencies=(",
                ]
            )

            for dependency in dependencies:
                lines.append(f"                        {dependency!r},")

            lines.extend(
                [
                    "                    ),",
                    "                ),",
                ]
            )

        lines.extend(
            [
                "            ),",
                "        ),",
            ]
        )

    lines.extend(
        [
            "    ),",
            ")",
            "",
            "",
        ]
    )

    return "\n".join(lines)


def update_source() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    definitions = "".join(
        render_solution(solution)
        for solution in SOLUTIONS
        if f"{solution['constant']} = " not in source
    )

    marker = "\nPLATFORM_SECTOR_SOLUTIONS: tuple["

    if definitions:
        if marker not in source:
            raise RuntimeError("Âncora PLATFORM_SECTOR_SOLUTIONS não encontrada.")

        source = source.replace(
            marker,
            f"\n{definitions}{marker}",
            1,
        )

    registry_pattern = re.compile(
        r"("
        r"PLATFORM_SECTOR_SOLUTIONS:\s*tuple\[\s*"
        r"PlatformSectorSolution,\s*\.\.\.\s*\]\s*=\s*\(\s*\n"
        r")"
        r"(?P<body>.*?)"
        r"("
        r"\)\s*\n\s*\nPLATFORM_SECTOR_SOLUTION_BY_ID"
        r")",
        re.DOTALL,
    )
    match = registry_pattern.search(source)

    if match is None:
        raise RuntimeError("Registro PLATFORM_SECTOR_SOLUTIONS não encontrado.")

    body = match.group("body")

    for solution in SOLUTIONS:
        registry_line = f"    {solution['constant']},\n"

        if registry_line not in body:
            body += registry_line

    source = source[: match.start("body")] + body + source[match.end("body") :]

    SOURCE_PATH.write_text(source, encoding="utf-8")


def update_tests() -> None:
    source = TEST_PATH.read_text(encoding="utf-8")

    import_pattern = re.compile(
        r"from src\.platform_sector_solutions import \(\n"
        r"(?P<body>.*?)"
        r"\n\)",
        re.DOTALL,
    )
    match = import_pattern.search(source)

    if match is None:
        raise RuntimeError("Importação de platform_sector_solutions não encontrada.")

    body_lines = [line for line in match.group("body").splitlines() if line.strip()]
    imported_names = {line.strip().rstrip(",") for line in body_lines}

    for solution in SOLUTIONS:
        constant = str(solution["constant"])

        if constant not in imported_names:
            body_lines.append(f"    {constant},")

    new_import_body = "\n".join(body_lines)
    source = (
        source[: match.start("body")] + new_import_body + source[match.end("body") :]
    )

    source = source.replace(
        "def test_two_specialized_sector_solutions_are_registered():",
        "def test_specialized_sector_solutions_are_registered():",
    )

    source = re.sub(
        r"assert len\(PLATFORM_SECTOR_SOLUTIONS\) == \d+",
        "assert len(PLATFORM_SECTOR_SOLUTIONS) == 4",
        source,
        count=1,
    )

    expected_anchor = '        "agribusiness_smart_agriculture_bioeconomy",\n'

    if expected_anchor not in source:
        raise RuntimeError("Conjunto esperado de IDs não encontrado.")

    additions = ""

    for solution in SOLUTIONS:
        solution_id_line = f'        "{solution["solution_id"]}",\n'

        if solution_id_line not in source:
            additions += solution_id_line

    if additions:
        source = source.replace(
            expected_anchor,
            expected_anchor + additions,
            1,
        )

    if "def test_pet_shop_solution_is_complete" not in source:
        source += """


def test_pet_shop_solution_is_complete():
    assert len(
        PET_SHOPS_VETERINARY_SOLUTION.areas
    ) == 6
    assert (
        PET_SHOPS_VETERINARY_SOLUTION.capability_count
        == 15
    )


def test_supermarket_solution_is_complete():
    assert len(
        SUPERMARKETS_WHOLESALE_SOLUTION.areas
    ) == 7
    assert (
        SUPERMARKETS_WHOLESALE_SOLUTION.capability_count
        == 15
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )


update_source()
update_tests()

print("PET_SUPERMARKET_SOLUTIONS_CREATED=OK")
print("PET_AREAS=6")
print("PET_CAPABILITIES=15")
print("SUPERMARKET_AREAS=7")
print("SUPERMARKET_CAPABILITIES=15")
