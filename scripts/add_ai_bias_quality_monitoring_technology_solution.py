"""Adiciona Monitoramento de Vieses e Qualidade de IA."""

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
        "ai_bias_quality_monitoring_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


AI_BIAS_QUALITY_MONITORING_DEFINITION = """
_AI_BIAS_QUALITY_MONITORING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "ai_bias_quality_monitoring"
    ]
)


AI_BIAS_QUALITY_MONITORING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="ai_bias_quality_monitoring",
        icon="📊",
        title="Monitoramento de Vieses e Qualidade de IA",
        description=(
            "Arquitetura tecnológica para qualidade e representatividade "
            "dos dados, avaliação de vieses e equidade, qualidade das "
            "previsões e respostas, confiança, factualidade, detecção "
            "de drift, monitoramento de RAG, modelos generativos, agentes "
            "e sistemas multimodais, revisão humana, tratamento de falhas, "
            "limites operacionais, alertas, auditoria e melhoria contínua."
        ),
        status=(
            _AI_BIAS_QUALITY_MONITORING_MODULE.status
        ),
        integration_type=(
            _AI_BIAS_QUALITY_MONITORING_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "ai_data_quality_representativeness"
                ),
                title="🗃️ Qualidade e representatividade dos dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_dataset_quality_profiling"
                        ),
                        title="🔎 Perfil de qualidade dos datasets",
                        description=(
                            "Avaliação de completude, precisão, consistência, "
                            "duplicidade, atualidade, formatos, valores "
                            "inválidos e padrões inesperados nos dados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_dataset_representativeness_coverage"
                        ),
                        title="🌐 Representatividade e cobertura",
                        description=(
                            "Análise da cobertura de grupos, contextos, "
                            "regiões, idiomas, condições, comportamentos "
                            "e situações relevantes para a finalidade."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "data_platform_governance",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_label_annotation_quality"
                        ),
                        title="🏷️ Qualidade de rótulos e anotações",
                        description=(
                            "Avaliação de concordância, ambiguidades, erros, "
                            "instruções, consistência e rastreabilidade "
                            "dos rótulos utilizados em treinamento e teste."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                            "ai_collaboration_meetings_productivity",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_bias_fairness_evaluation"
                ),
                title="⚖️ Vieses e equidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_group_performance_disparity"
                        ),
                        title="📊 Diferenças de desempenho entre grupos",
                        description=(
                            "Comparação de erros, acertos, recusas, "
                            "benefícios, impactos e resultados entre grupos "
                            "relevantes para o contexto de utilização."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "ai_evaluation_benchmarks_red_team",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_intersectional_fairness_analysis"
                        ),
                        title="🧩 Análise de equidade interseccional",
                        description=(
                            "Avaliação de combinações de características "
                            "e contextos que possam revelar desigualdades "
                            "não identificadas em análises isoladas."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "responsible_ai_ethics_risk",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_proxy_bias_correlation_detection"
                        ),
                        title="🔗 Variáveis proxy e correlações indevidas",
                        description=(
                            "Identificação de atributos que possam funcionar "
                            "como substitutos indiretos de características "
                            "sensíveis ou produzir impactos injustificados."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "knowledge_graph_semantic_ai",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_prediction_response_quality"
                ),
                title="✅ Qualidade de previsões e respostas",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_accuracy_relevance_consistency"
                        ),
                        title="🎯 Precisão, relevância e consistência",
                        description=(
                            "Avaliação da correção, utilidade, aderência "
                            "à solicitação, estabilidade e consistência "
                            "dos resultados produzidos pela solução."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_calibration_confidence_quality"
                        ),
                        title="🎲 Calibração e confiança",
                        description=(
                            "Avaliação da relação entre confiança declarada, "
                            "probabilidade, incerteza e frequência real "
                            "de resultados corretos ou incorretos."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "model_explainability_interpretability",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_factuality_grounding_quality"
                        ),
                        title="📚 Factualidade e fundamentação",
                        description=(
                            "Verificação de afirmações, fontes, evidências, "
                            "citações, contradições, respostas inventadas "
                            "e suporte documental dos resultados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "data_traceability_provenance",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_drift_change_monitoring"
                ),
                title="🔄 Drift e mudanças de comportamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_input_data_drift_monitoring"
                        ),
                        title="📥 Drift dos dados de entrada",
                        description=(
                            "Monitoramento de mudanças em distribuições, "
                            "formatos, frequências, valores, grupos, fontes "
                            "e características dos dados recebidos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_concept_performance_drift"
                        ),
                        title="📉 Drift de conceito e desempenho",
                        description=(
                            "Identificação de mudanças na relação entre "
                            "entradas e resultados, perda de precisão, "
                            "alterações de padrões e redução de utilidade."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "scientific_computing_engineering",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_prompt_tool_configuration_drift"
                        ),
                        title="🛠️ Drift de prompts e configurações",
                        description=(
                            "Rastreamento de mudanças em prompts, modelos, "
                            "ferramentas, parâmetros, fontes, políticas "
                            "e configurações que alterem o comportamento."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "agent_process_orchestration",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "generative_rag_agent_quality"
                ),
                title="🤖 Qualidade de RAG, IA generativa e agentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "rag_retrieval_answer_quality_monitoring"
                        ),
                        title="📚 Qualidade da recuperação e resposta RAG",
                        description=(
                            "Monitoramento de relevância dos documentos, "
                            "cobertura, ranking, contexto, fundamentação "
                            "e qualidade das respostas geradas."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "model_explainability_interpretability",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_agent_action_tool_quality"
                        ),
                        title="🛠️ Qualidade das ações dos agentes",
                        description=(
                            "Avaliação de seleção de ferramentas, parâmetros, "
                            "sequência, repetição, autorização, conclusão "
                            "e correção das ações realizadas por agentes."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "ai_model_agent_security",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_multimodal_language_quality"
                        ),
                        title="🌐 Qualidade multimodal e multilíngue",
                        description=(
                            "Avaliação de texto, voz, imagem, documentos, "
                            "vídeo e diferentes idiomas para identificar "
                            "perdas de qualidade ou comportamentos desiguais."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "voice_audio_speech_ai",
                            "computer_vision_video_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_human_review_remediation"
                ),
                title="👥 Revisão humana e correção",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_human_review_sampling"
                        ),
                        title="👁️ Amostragem e revisão humana",
                        description=(
                            "Seleção de resultados por risco, incerteza, "
                            "impacto, novidade ou aleatoriedade para revisão "
                            "por pessoas autorizadas e qualificadas."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "enterprise_decision_intelligence",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_quality_issue_triage_root_cause"
                        ),
                        title="🩺 Triagem e causa raiz",
                        description=(
                            "Classificação e correlação de falhas com dados, "
                            "modelos, prompts, ferramentas, integrações, "
                            "configurações e condições de utilização."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "knowledge_graph_semantic_ai",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_quality_remediation_validation"
                        ),
                        title="🔧 Correção e validação das melhorias",
                        description=(
                            "Acompanhamento de correções em dados, modelos, "
                            "prompts, políticas e sistemas, seguido por "
                            "novos testes e comparação dos resultados."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_quality_governance_observability"
                ),
                title="📡 Alertas, governança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_quality_threshold_alert_management"
                        ),
                        title="🚦 Limites, alertas e escalonamentos",
                        description=(
                            "Definição de limites para qualidade, equidade, "
                            "drift, segurança e desempenho, com alertas, "
                            "prioridades e fluxos de escalonamento."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_quality_evidence_audit_provenance"
                        ),
                        title="🧾 Evidências, auditoria e proveniência",
                        description=(
                            "Registro de dados, métricas, modelos, versões, "
                            "avaliações, grupos, alertas, revisões, decisões, "
                            "correções e resultados observados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "responsible_ai_ethics_risk",
                            "ai_certification_system_evidence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_quality_dashboard_lifecycle_monitoring"
                        ),
                        title="📊 Painéis e monitoramento do ciclo de vida",
                        description=(
                            "Visualização de qualidade, vieses, drift, "
                            "incidentes, avaliações, custos, versões "
                            "e evolução dos sistemas de inteligência artificial."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "ai_operations",
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

    module_id = "ai_bias_quality_monitoring"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        54: (378, 1134),
        55: (385, 1155),
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

    print("AI_BIAS_QUALITY_MONITORING_PREREQUISITES=OK")


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
    """Adiciona Monitoramento de Vieses e Qualidade."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AI_BIAS_QUALITY_MONITORING_SOLUTION =" in source:
        print("AI_BIAS_QUALITY_MONITORING_ALREADY_PRESENT=OK")
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
        AI_BIAS_QUALITY_MONITORING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    MODEL_EXPLAINABILITY_INTERPRETABILITY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    AI_BIAS_QUALITY_MONITORING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_BIAS_QUALITY_MONITORING_SOLUTION_CREATED=OK")


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

    solution_name = "AI_BIAS_QUALITY_MONITORING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 54
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 55
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

    test_name = "def test_ai_bias_quality_monitoring_is_complete"

    if test_name not in source:
        source += """


def test_ai_bias_quality_monitoring_is_complete():
    assert (
        AI_BIAS_QUALITY_MONITORING_SOLUTION.solution_id
        == "ai_bias_quality_monitoring"
    )

    assert len(
        AI_BIAS_QUALITY_MONITORING_SOLUTION.areas
    ) == 7

    assert (
        AI_BIAS_QUALITY_MONITORING_SOLUTION
        .capability_count
        == 21
    )


def test_ai_bias_quality_monitoring_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_bias_quality_monitoring"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_BIAS_QUALITY_MONITORING_SOLUTION.status
        is module.status
    )

    assert (
        AI_BIAS_QUALITY_MONITORING_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_ai_bias_quality_monitoring_lookup():
    assert (
        platform_technology_solution(
            "ai_bias_quality_monitoring"
        )
        is AI_BIAS_QUALITY_MONITORING_SOLUTION
    )
"""

        print("AI_BIAS_QUALITY_MONITORING_TESTS_CREATED=OK")
    else:
        print("AI_BIAS_QUALITY_MONITORING_TESTS_ALREADY_PRESENT=OK")

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

    quality_solution = module.AI_BIAS_QUALITY_MONITORING_SOLUTION

    assert len(solutions) == 55
    assert len(quality_solution.areas) == 7
    assert quality_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 385
    assert total_capabilities == 1155

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=55")
    print("TOTAL_TECHNOLOGY_AREAS=385")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1155")
    print("AI_BIAS_QUALITY_MONITORING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
