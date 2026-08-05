"""Adiciona Explicabilidade e Interpretabilidade de Modelos."""

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
        "model_explainability_interpretability_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


MODEL_EXPLAINABILITY_INTERPRETABILITY_DEFINITION = """
_MODEL_EXPLAINABILITY_INTERPRETABILITY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "model_explainability_interpretability"
    ]
)


MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id=(
            "model_explainability_interpretability"
        ),
        icon="🔍",
        title=(
            "Explicabilidade e Interpretabilidade de Modelos"
        ),
        description=(
            "Arquitetura tecnológica para documentação transparente, "
            "interpretação global e local, importância de atributos, "
            "análises contrafactuais, proveniência de dados, "
            "explicações de previsões, recomendações, RAG, modelos "
            "generativos e agentes, comunicação adaptada aos usuários, "
            "validação humana, segurança, privacidade, monitoramento, "
            "governança, evidências e auditoria."
        ),
        status=(
            _MODEL_EXPLAINABILITY_INTERPRETABILITY_MODULE
            .status
        ),
        integration_type=(
            _MODEL_EXPLAINABILITY_INTERPRETABILITY_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "model_explainability_documentation_transparency"
                ),
                title="📚 Documentação e transparência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "model_explainability_model_cards"
                        ),
                        title="📄 Model cards e documentação",
                        description=(
                            "Documentação de finalidade, arquitetura, "
                            "dados, versões, métricas, limitações, riscos, "
                            "responsáveis e condições adequadas de uso."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "responsible_ai_ethics_risk",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_explainability_usage_boundaries"
                        ),
                        title="🚧 Limites e condições de utilização",
                        description=(
                            "Registro de situações cobertas, casos não "
                            "recomendados, incertezas, dependências, "
                            "restrições e condições de interrupção."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "ai_evaluation_benchmarks_red_team",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_explainability_version_change_notes"
                        ),
                        title="🔄 Versões e alterações explicáveis",
                        description=(
                            "Registro de mudanças em modelos, dados, "
                            "parâmetros, prompts, ferramentas, métricas "
                            "e impactos esperados nos resultados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_operations",
                            "ai_software_engineering",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="model_global_interpretability",
                title="🌐 Interpretabilidade global",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "model_global_feature_importance"
                        ),
                        title="📊 Importância global de atributos",
                        description=(
                            "Análise da influência geral de atributos, "
                            "variáveis, sinais e componentes sobre "
                            "o comportamento global do modelo."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "scientific_computing_engineering",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_global_behavior_patterns"
                        ),
                        title="🧩 Padrões de comportamento do modelo",
                        description=(
                            "Identificação de relações, tendências, "
                            "segmentos, regras aproximadas e regiões "
                            "com comportamentos diferentes."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "knowledge_graph_semantic_ai",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_global_sensitivity_analysis"
                        ),
                        title="🎛️ Sensibilidade e estabilidade",
                        description=(
                            "Avaliação das mudanças nos resultados diante "
                            "de variações controladas nas entradas, "
                            "parâmetros, contexto e condições de operação."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "simulation_optimization_operations_research",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "model_local_explanations_counterfactuals"
                ),
                title="🎯 Explicações locais e contrafactuais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "model_local_prediction_explanation"
                        ),
                        title="🔎 Explicação de previsões individuais",
                        description=(
                            "Apresentação dos principais fatores, sinais, "
                            "evidências e contribuições relacionados "
                            "a uma previsão ou recomendação específica."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_counterfactual_explanations"
                        ),
                        title="🔄 Explicações contrafactuais",
                        description=(
                            "Apresentação de alterações possíveis nas "
                            "entradas ou condições que poderiam produzir "
                            "um resultado diferente."
                        ),
                        technology_dependencies=(
                            "simulation_optimization_operations_research",
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_uncertainty_confidence_explanation"
                        ),
                        title="🎲 Confiança e incerteza",
                        description=(
                            "Comunicação de níveis de confiança, intervalos, "
                            "lacunas, ambiguidades, hipóteses e fatores "
                            "que reduzem a segurança do resultado."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "ai_evaluation_benchmarks_red_team",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "model_data_provenance_feature_explanations"
                ),
                title="🧬 Dados, atributos e proveniência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "model_input_data_provenance_explanation"
                        ),
                        title="🗂️ Origem dos dados utilizados",
                        description=(
                            "Identificação das fontes, versões, horários, "
                            "transformações, permissões e qualidade dos dados "
                            "utilizados para produzir o resultado."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_feature_engineering_trace"
                        ),
                        title="⚙️ Transformação e engenharia de atributos",
                        description=(
                            "Rastreamento de cálculos, agregações, filtros, "
                            "codificações e transformações que originaram "
                            "os atributos utilizados pelo modelo."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_software_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "model_missing_data_quality_explanation"
                        ),
                        title="⚠️ Qualidade e ausência de dados",
                        description=(
                            "Explicação de dados ausentes, inconsistências, "
                            "estimativas, substituições, baixa qualidade "
                            "e possíveis impactos sobre o resultado."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="generative_rag_explainability",
                title="📚 Explicabilidade de IA generativa e RAG",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "rag_source_citation_explanation"
                        ),
                        title="🔗 Fontes e citações do RAG",
                        description=(
                            "Apresentação dos documentos, trechos, "
                            "metadados, rankings e evidências recuperadas "
                            "para fundamentar uma resposta."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "data_traceability_provenance",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "generative_response_reasoning_summary"
                        ),
                        title="📝 Resumo justificativo da resposta",
                        description=(
                            "Geração de justificativas verificáveis sobre "
                            "os fatores e evidências usados, sem expor "
                            "processos internos privados de raciocínio."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "responsible_ai_ethics_risk",
                            "ai_model_agent_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "generative_grounding_conflict_detection"
                        ),
                        title="🚨 Fundamentação e conflitos entre fontes",
                        description=(
                            "Identificação de respostas sem suporte, "
                            "fontes contraditórias, evidências insuficientes "
                            "e diferenças relevantes entre documentos."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "agent_decision_action_explainability"
                ),
                title="🤖 Explicabilidade de agentes e decisões",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "agent_plan_tool_selection_explanation"
                        ),
                        title="🛠️ Planos e seleção de ferramentas",
                        description=(
                            "Registro explicável das ferramentas, fontes, "
                            "etapas e critérios selecionados por agentes "
                            "para executar uma tarefa autorizada."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "ai_model_agent_security",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "agent_action_approval_explanation"
                        ),
                        title="🧑‍⚖️ Ações e aprovações humanas",
                        description=(
                            "Apresentação das ações propostas, impactos, "
                            "dados utilizados, permissões, riscos "
                            "e motivos para solicitar aprovação humana."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "enterprise_decision_intelligence",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "agent_failure_fallback_explanation"
                        ),
                        title="♻️ Falhas, fallback e interrupções",
                        description=(
                            "Explicação de erros, ferramentas indisponíveis, "
                            "limites atingidos, respostas alternativas, "
                            "fallbacks e razões para interrupção segura."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "operational_security_resilience",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "explainability_human_governance_monitoring"
                ),
                title="👥 Experiência humana, governança e monitoramento",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "explainability_audience_adaptive_interfaces"
                        ),
                        title="👤 Explicações adaptadas ao público",
                        description=(
                            "Adaptação do nível técnico, linguagem, formato, "
                            "profundidade e canal da explicação conforme "
                            "usuário, tarefa, risco e contexto."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "multimodal_ai",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "explainability_human_validation_feedback"
                        ),
                        title="✅ Validação e feedback humano",
                        description=(
                            "Coleta de avaliações sobre clareza, utilidade, "
                            "correção, confiança e capacidade das explicações "
                            "de apoiar decisões responsáveis."
                        ),
                        technology_dependencies=(
                            "ai_collaboration_meetings_productivity",
                            "tools_analytics",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "explainability_monitoring_audit_governance"
                        ),
                        title="🧾 Monitoramento, auditoria e governança",
                        description=(
                            "Registro de métodos, versões, dados, modelos, "
                            "explicações, usuários, aprovações, falhas, "
                            "custos, métricas e evidências."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "technology_governance_policy_compliance",
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
    """Valida o registro atual."""

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

    module_id = "model_explainability_interpretability"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        53: (371, 1113),
        54: (378, 1134),
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

    print("MODEL_EXPLAINABILITY_INTERPRETABILITY_PREREQUISITES=OK")


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
    """Adiciona a solução ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION =" in source:
        print("MODEL_EXPLAINABILITY_INTERPRETABILITY_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_TECHNOLOGY_SOLUTIONS: tuple[
    PlatformTechnologySolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro não encontrada.")

    source = source.replace(
        registry_anchor,
        MODEL_EXPLAINABILITY_INTERPRETABILITY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

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
        raise RuntimeError("Final da importação não encontrado.")

    import_block = source[import_start:import_end]

    solution_name = "MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 53
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 54
"""

    if old_count in source:
        source = source.replace(
            old_count,
            new_count,
            1,
        )
    elif new_count not in source:
        raise RuntimeError("Contagem esperada não encontrada.")

    test_name = "def test_model_explainability_interpretability_is_complete"

    if test_name not in source:
        source += """


def test_model_explainability_interpretability_is_complete():
    assert (
        MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION.solution_id
        == "model_explainability_interpretability"
    )

    assert len(
        MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION.areas
    ) == 7

    assert (
        MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION
        .capability_count
        == 21
    )


def test_model_explainability_interpretability_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "model_explainability_interpretability"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION.status
        is module.status
    )

    assert (
        MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_model_explainability_interpretability_lookup():
    assert (
        platform_technology_solution(
            "model_explainability_interpretability"
        )
        is MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION
    )
"""

        print("MODEL_EXPLAINABILITY_INTERPRETABILITY_TESTS_CREATED=OK")
    else:
        print("MODEL_EXPLAINABILITY_INTERPRETABILITY_TESTS_ALREADY_PRESENT=OK")

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )


def validate_result() -> None:
    """Recarrega e valida o resultado."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    explainability_solution = module.MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION

    assert len(solutions) == 54
    assert len(explainability_solution.areas) == 7
    assert explainability_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 378
    assert total_capabilities == 1134

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=54")
    print("TOTAL_TECHNOLOGY_AREAS=378")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1134")
    print("MODEL_EXPLAINABILITY_INTERPRETABILITY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
