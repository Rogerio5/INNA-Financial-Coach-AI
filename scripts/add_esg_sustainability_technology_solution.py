"""Adiciona ESG e Sustentabilidade ao registro tecnológico."""

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
    / ("esg_sustainability_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


ESG_SUSTAINABILITY_DEFINITION = """
_ESG_SUSTAINABILITY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "esg_sustainability"
    ]
)


ESG_SUSTAINABILITY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="esg_sustainability",
        icon="🌱",
        title="ESG e Sustentabilidade",
        description=(
            "Arquitetura tecnológica para estratégia ESG, "
            "materialidade, metas, governança, inventários "
            "de emissões, riscos climáticos, transição energética, "
            "recursos naturais, circularidade, indicadores sociais, "
            "finanças sustentáveis, relatórios, evidências, "
            "conformidade, auditoria e observabilidade."
        ),
        status=(
            _ESG_SUSTAINABILITY_MODULE.status
        ),
        integration_type=(
            _ESG_SUSTAINABILITY_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="esg_strategy_materiality_governance",
                title="🧭 Estratégia, materialidade e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="esg_strategy_targets",
                        title="🎯 Estratégia e metas ESG",
                        description=(
                            "Definição de objetivos, indicadores, metas, "
                            "prazos, responsáveis, prioridades e critérios "
                            "de acompanhamento da estratégia ESG."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_double_materiality_assessment"
                        ),
                        title="⚖️ Avaliação de dupla materialidade",
                        description=(
                            "Análise dos impactos da organização sobre "
                            "sociedade e ambiente, além dos riscos "
                            "e oportunidades financeiros associados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_governance_accountability"
                        ),
                        title="👥 Governança e responsabilidades",
                        description=(
                            "Definição de papéis, comitês, aprovações, "
                            "responsáveis, segregação de funções "
                            "e prestação de contas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "data_traceability_provenance",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_climate_emissions_transition",
                title="🌍 Clima, emissões e transição",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "esg_ghg_emissions_inventory"
                        ),
                        title="🏭 Inventário de emissões",
                        description=(
                            "Coleta, classificação, cálculo e consolidação "
                            "de emissões associadas a operações, energia, "
                            "ativos, fornecedores e atividades."
                        ),
                        technology_dependencies=(
                            "energy_smart_grids",
                            "climate_meteorological_intelligence",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_climate_risk_scenarios"
                        ),
                        title="⚠️ Riscos e cenários climáticos",
                        description=(
                            "Avaliação de riscos físicos e de transição "
                            "conforme localização, ativos, operações, "
                            "horizontes e cenários climáticos."
                        ),
                        technology_dependencies=(
                            "climate_meteorological_intelligence",
                            "simulation_optimization_operations_research",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_decarbonization_transition_plans"
                        ),
                        title="📉 Planos de descarbonização",
                        description=(
                            "Planejamento de iniciativas, investimentos, "
                            "metas intermediárias, eficiência energética "
                            "e alternativas de redução de emissões."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "energy_smart_grids",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_environment_resources_circularity",
                title="🌿 Recursos naturais e circularidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "esg_energy_resource_efficiency"
                        ),
                        title="⚡ Eficiência energética e de recursos",
                        description=(
                            "Monitoramento e otimização do consumo "
                            "de energia, água, materiais e demais recursos "
                            "utilizados nas operações."
                        ),
                        technology_dependencies=(
                            "energy_smart_grids",
                            "environmental_natural_resources_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_water_biodiversity_impacts"
                        ),
                        title="💧 Água, biodiversidade e território",
                        description=(
                            "Avaliação de dependências, impactos, riscos "
                            "e oportunidades relacionados à água, "
                            "biodiversidade, habitats e territórios."
                        ),
                        technology_dependencies=(
                            "environmental_natural_resources_intelligence",
                            "geoai_earth_observation",
                            "gis_location_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_circularity_waste_management"
                        ),
                        title="♻️ Circularidade e gestão de resíduos",
                        description=(
                            "Acompanhamento de materiais, resíduos, "
                            "reutilização, reciclagem, recuperação, "
                            "destinação e eficiência do ciclo de vida."
                        ),
                        technology_dependencies=(
                            "materials_product_engineering",
                            "construction_bim_digital_engineering",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_social_human_capital",
                title="👥 Dimensão social e capital humano",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "esg_workforce_wellbeing_indicators"
                        ),
                        title="🧑‍💼 Pessoas, saúde e bem-estar",
                        description=(
                            "Acompanhamento de indicadores de trabalho, "
                            "saúde, segurança, desenvolvimento, retenção "
                            "e bem-estar das pessoas."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "privacy_data_protection_lgpd",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_diversity_inclusion_metrics"
                        ),
                        title="🤝 Diversidade, equidade e inclusão",
                        description=(
                            "Monitoramento responsável de indicadores "
                            "de representação, oportunidades, progressão, "
                            "participação e inclusão."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "privacy_data_protection_lgpd",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_community_supply_chain_social_risk"
                        ),
                        title="🌐 Comunidades e riscos sociais da cadeia",
                        description=(
                            "Avaliação de impactos sobre comunidades, "
                            "direitos, fornecedores, territórios, relações "
                            "sociais e condições da cadeia de valor."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "knowledge_graph_semantic_ai",
                            "software_supply_chain_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_sustainable_finance_investment",
                title="💰 Finanças e investimentos sustentáveis",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "esg_financial_impact_modeling"
                        ),
                        title="📊 Impactos financeiros ESG",
                        description=(
                            "Modelagem de custos, riscos, receitas, perdas, "
                            "investimentos e efeitos financeiros associados "
                            "a fatores ambientais, sociais e de governança."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "simulation_optimization_operations_research",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_sustainable_investment_screening"
                        ),
                        title="🔎 Avaliação de investimentos sustentáveis",
                        description=(
                            "Análise de projetos e alternativas conforme "
                            "critérios ESG, evidências, riscos, políticas "
                            "e objetivos estratégicos."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_green_capex_portfolio_prioritization"
                        ),
                        title="📈 Priorização de portfólio sustentável",
                        description=(
                            "Priorização de investimentos, projetos "
                            "e iniciativas conforme impacto, retorno, "
                            "risco, capacidade e metas ESG."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "simulation_optimization_operations_research",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_reporting_disclosure_assurance",
                title="📄 Indicadores, relatórios e asseguração",
                capabilities=(
                    TechnologyCapability(
                        capability_id="esg_kpi_data_collection",
                        title="📥 Coleta e consolidação de indicadores",
                        description=(
                            "Integração de sistemas, formulários, APIs "
                            "e bases para coleta, validação e consolidação "
                            "dos indicadores ESG."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_reporting_disclosure_generation"
                        ),
                        title="📄 Relatórios e divulgações ESG",
                        description=(
                            "Produção assistida de relatórios, tabelas, "
                            "narrativas, indicadores, anexos e divulgações "
                            "com base em dados aprovados."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "enterprise_rag",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_assurance_evidence_traceability"
                        ),
                        title="🧾 Evidências, rastreabilidade e asseguração",
                        description=(
                            "Preservação de fontes, cálculos, versões, "
                            "aprovações, responsáveis e evidências "
                            "necessárias à revisão e auditoria."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "software_testing_quality_reliability",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="esg_compliance_operations_observability",
                title="🛡️ Conformidade e operações ESG",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "esg_policy_compliance_monitoring"
                        ),
                        title="⚖️ Políticas e conformidade ESG",
                        description=(
                            "Monitoramento de políticas, compromissos, "
                            "requisitos, limites, prazos, controles "
                            "e obrigações aplicáveis."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_alerts_corrective_workflows"
                        ),
                        title="🚨 Alertas e ações corretivas",
                        description=(
                            "Acionamento de alertas, responsáveis, "
                            "investigações, planos de ação, aprovações "
                            "e acompanhamento de correções."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "esg_observability_audit_lifecycle"
                        ),
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento de integrações, indicadores, "
                            "jobs, relatórios, qualidade, erros, acessos, "
                            "custos, versões e evidências ESG."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
        ),
    )
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

    module_id = "esg_sustainability"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        34: (238, 714),
        35: (245, 735),
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

    print("ESG_SUSTAINABILITY_PREREQUISITES=OK")


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
    """Adiciona ESG e Sustentabilidade."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ESG_SUSTAINABILITY_SOLUTION =" in source:
        print("ESG_SUSTAINABILITY_ALREADY_PRESENT=OK")
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
        ESG_SUSTAINABILITY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ENERGY_SMART_GRIDS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ESG_SUSTAINABILITY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ESG_SUSTAINABILITY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_esg_sustainability_is_complete" in source:
        print("ESG_SUSTAINABILITY_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "ESG_SUSTAINABILITY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 34
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 35
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de trinta e quatro soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_esg_sustainability_is_complete():
    assert (
        ESG_SUSTAINABILITY_SOLUTION.solution_id
        == "esg_sustainability"
    )

    assert len(
        ESG_SUSTAINABILITY_SOLUTION.areas
    ) == 7

    assert (
        ESG_SUSTAINABILITY_SOLUTION.capability_count
        == 21
    )


def test_esg_sustainability_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "esg_sustainability"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ESG_SUSTAINABILITY_SOLUTION.status
        is module.status
    )

    assert (
        ESG_SUSTAINABILITY_SOLUTION.integration_type
        == module.integration_type
    )


def test_esg_sustainability_lookup():
    assert (
        platform_technology_solution(
            "esg_sustainability"
        )
        is ESG_SUSTAINABILITY_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("ESG_SUSTAINABILITY_TESTS_CREATED=OK")


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

    esg_solution = getattr(
        module,
        "ESG_SUSTAINABILITY_SOLUTION",
    )

    assert len(solutions) == 35
    assert len(esg_solution.areas) == 7
    assert esg_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 245
    assert total_capabilities == 735

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=35")
    print("TOTAL_TECHNOLOGY_AREAS=245")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=735")
    print("ESG_SUSTAINABILITY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
