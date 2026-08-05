"""Adiciona Inteligência de Decisão Empresarial."""

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
        "enterprise_decision_intelligence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


ENTERPRISE_DECISION_INTELLIGENCE_DEFINITION = """
_ENTERPRISE_DECISION_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "enterprise_decision_intelligence"
    ]
)


ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="enterprise_decision_intelligence",
        icon="🧠",
        title="Inteligência de Decisão Empresarial",
        description=(
            "Arquitetura tecnológica para definição de problemas, "
            "objetivos, restrições e critérios de decisão, integração "
            "de dados e evidências, análise de cenários, simulação, "
            "previsão, otimização, recomendações explicáveis, "
            "aprovação humana, execução controlada, riscos, ética, "
            "governança, aprendizado, auditoria e observabilidade."
        ),
        status=(
            _ENTERPRISE_DECISION_INTELLIGENCE_MODULE.status
        ),
        integration_type=(
            _ENTERPRISE_DECISION_INTELLIGENCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="decision_context_objectives_constraints",
                title="🧭 Contexto, objetivos e restrições",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_problem_context_definition"
                        ),
                        title="📋 Definição do problema decisório",
                        description=(
                            "Organização do contexto, problema, escopo, "
                            "responsáveis, horizonte, dependências "
                            "e resultados esperados da decisão."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "document_ai",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_objectives_constraints_management"
                        ),
                        title="🎯 Objetivos, critérios e restrições",
                        description=(
                            "Definição de objetivos, métricas, prioridades, "
                            "limites, recursos, regras e condições "
                            "que orientam a decisão."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "tools_analytics",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_stakeholder_policy_alignment"
                        ),
                        title="👥 Partes interessadas e alinhamento",
                        description=(
                            "Mapeamento de interessados, responsabilidades, "
                            "expectativas, conflitos, aprovações "
                            "e políticas aplicáveis ao processo."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_data_evidence_quality",
                title="📊 Dados, evidências e confiança",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_data_evidence_integration"
                        ),
                        title="📥 Integração de dados e evidências",
                        description=(
                            "Consolidação de dados, documentos, indicadores, "
                            "eventos, análises e fontes necessárias "
                            "para apoiar a decisão."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_evidence_quality_confidence"
                        ),
                        title="✅ Qualidade e confiança das evidências",
                        description=(
                            "Avaliação de completude, atualidade, precisão, "
                            "consistência, origem, cobertura e confiança "
                            "das informações utilizadas."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "data_traceability_provenance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_assumption_uncertainty_tracking"
                        ),
                        title="🎲 Premissas e incertezas",
                        description=(
                            "Registro de premissas, lacunas, dependências, "
                            "intervalos, probabilidades e incertezas "
                            "presentes no processo decisório."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "scientific_computing_engineering",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_scenarios_simulation_forecasting",
                title="🔮 Cenários, simulação e previsão",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_scenario_generation"
                        ),
                        title="🧩 Geração de cenários",
                        description=(
                            "Construção de cenários alternativos conforme "
                            "variáveis, eventos, tendências, restrições "
                            "e hipóteses relevantes."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "scientific_computing_engineering",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_what_if_simulation"
                        ),
                        title="🧪 Simulação e análise what-if",
                        description=(
                            "Avaliação das consequências de alterações "
                            "em parâmetros, políticas, recursos, demanda "
                            "e condições operacionais."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "digital_twins_simulation",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_outcome_forecasting"
                        ),
                        title="📈 Previsão de resultados",
                        description=(
                            "Estimativa de resultados, impactos, riscos, "
                            "custos, benefícios e probabilidades associados "
                            "às alternativas analisadas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "tools_analytics",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_optimization_recommendations",
                title="⚙️ Otimização e recomendações",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_multi_criteria_optimization"
                        ),
                        title="⚖️ Otimização multicritério",
                        description=(
                            "Otimização de alternativas considerando "
                            "múltiplos objetivos, prioridades, restrições, "
                            "recursos e critérios conflitantes."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "scientific_computing_engineering",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_recommendation_ranking"
                        ),
                        title="📌 Classificação de alternativas",
                        description=(
                            "Classificação e recomendação de alternativas "
                            "conforme critérios, resultados previstos, "
                            "riscos, custos e preferências aprovadas."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "responsible_ai_ethics_risk",
                            "ai_model_agent_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_tradeoff_explanation"
                        ),
                        title="🔎 Explicação de escolhas e compensações",
                        description=(
                            "Apresentação dos fatores, evidências, pesos, "
                            "benefícios, riscos, limitações e compensações "
                            "que influenciaram as recomendações."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_human_approval_execution",
                title="👥 Aprovação humana e execução",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_human_review_approval"
                        ),
                        title="🧑‍⚖️ Revisão e aprovação humana",
                        description=(
                            "Fluxos para revisar evidências, corrigir "
                            "premissas, ajustar recomendações, aprovar, "
                            "rejeitar ou solicitar nova análise."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_action_orchestration"
                        ),
                        title="🚀 Orquestração das ações aprovadas",
                        description=(
                            "Conversão de decisões aprovadas em tarefas, "
                            "integrações, notificações e processos "
                            "com limites e confirmações controladas."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_feedback_outcome_capture"
                        ),
                        title="🔄 Resultados e feedback da decisão",
                        description=(
                            "Registro dos resultados reais, efeitos, "
                            "desvios, feedbacks, ações concluídas "
                            "e consequências observadas."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "data_traceability_provenance",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_risk_ethics_governance",
                title="🛡️ Riscos, ética e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_risk_control_assessment"
                        ),
                        title="⚠️ Riscos e controles da decisão",
                        description=(
                            "Avaliação de riscos financeiros, operacionais, "
                            "tecnológicos, ambientais, sociais, legais "
                            "e reputacionais das alternativas."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "operational_security_resilience",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_fairness_ethics_validation"
                        ),
                        title="⚖️ Ética, equidade e impacto",
                        description=(
                            "Validação de impactos indevidos, vieses, "
                            "grupos afetados, proporcionalidade, transparência "
                            "e critérios de responsabilidade."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "ai_bias_quality_monitoring",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_policy_compliance_enforcement"
                        ),
                        title="📜 Políticas e conformidade",
                        description=(
                            "Verificação de regras, limites, aprovações, "
                            "segregação de funções, requisitos, exceções "
                            "e controles obrigatórios."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "zero_trust_identity_access",
                            "enterprise_rag",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="decision_observability_learning_audit",
                title="📈 Aprendizado, auditoria e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "decision_performance_monitoring"
                        ),
                        title="📊 Desempenho das decisões",
                        description=(
                            "Monitoramento de resultados, acertos, desvios, "
                            "tempo de decisão, custos, benefícios, riscos "
                            "e qualidade das recomendações."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "ai_operations",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_drift_learning_improvement"
                        ),
                        title="🧠 Aprendizado e melhoria contínua",
                        description=(
                            "Identificação de mudanças nas condições, "
                            "redução de desempenho, novas evidências "
                            "e oportunidades de melhoria dos modelos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "ai_bias_quality_monitoring",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "decision_traceability_audit"
                        ),
                        title="🧾 Rastreabilidade e auditoria decisória",
                        description=(
                            "Registro de dados, fontes, modelos, premissas, "
                            "alternativas, recomendações, aprovações, "
                            "ações, custos e resultados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "cloud_devops_finops",
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

    module_id = "enterprise_decision_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        49: (343, 1029),
        50: (350, 1050),
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

    print("ENTERPRISE_DECISION_INTELLIGENCE_PREREQUISITES=OK")


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
    """Adiciona Inteligência de Decisão Empresarial."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION =" in source:
        print("ENTERPRISE_DECISION_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        ENTERPRISE_DECISION_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    DATA_TRACEABILITY_PROVENANCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona ou completa os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

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

    solution_name = "ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 49
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 50
"""

    if old_count in source:
        source = source.replace(
            old_count,
            new_count,
            1,
        )
    elif new_count not in source:
        raise RuntimeError(
            "Contagem esperada das soluções tecnológicas não encontrada."
        )

    test_name = "def test_enterprise_decision_intelligence_is_complete"

    if test_name not in source:
        source += """


def test_enterprise_decision_intelligence_is_complete():
    assert (
        ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION.solution_id
        == "enterprise_decision_intelligence"
    )

    assert len(
        ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION
        .capability_count
        == 21
    )


def test_enterprise_decision_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "enterprise_decision_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_enterprise_decision_intelligence_lookup():
    assert (
        platform_technology_solution(
            "enterprise_decision_intelligence"
        )
        is ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION
    )
"""

        print("ENTERPRISE_DECISION_INTELLIGENCE_TESTS_CREATED=OK")
    else:
        print("ENTERPRISE_DECISION_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    decision_solution = module.ENTERPRISE_DECISION_INTELLIGENCE_SOLUTION

    assert len(solutions) == 50
    assert len(decision_solution.areas) == 7

    assert decision_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 350
    assert total_capabilities == 1050

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=50")
    print("TOTAL_TECHNOLOGY_AREAS=350")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1050")
    print("ENTERPRISE_DECISION_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
