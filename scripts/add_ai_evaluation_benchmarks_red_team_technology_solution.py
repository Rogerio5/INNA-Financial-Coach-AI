"""Adiciona Avaliação de IA, Benchmarks e Red Team."""

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
        "ai_evaluation_benchmarks_red_team_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


AI_EVALUATION_BENCHMARKS_RED_TEAM_DEFINITION = """
_AI_EVALUATION_BENCHMARKS_RED_TEAM_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "ai_evaluation_benchmarks_red_team"
    ]
)


AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="ai_evaluation_benchmarks_red_team",
        icon="🧪",
        title="Avaliação de IA, Benchmarks e Red Team",
        description=(
            "Arquitetura tecnológica para planejamento de avaliações, "
            "datasets e cenários de teste, benchmarks funcionais "
            "e especializados, regressão, comparação de modelos, "
            "red team, testes adversariais, segurança, privacidade, "
            "factualidade, robustez, desempenho, custos, avaliação "
            "humana, critérios de aprovação, evidências, monitoramento "
            "contínuo e governança do ciclo de vida da IA."
        ),
        status=(
            _AI_EVALUATION_BENCHMARKS_RED_TEAM_MODULE.status
        ),
        integration_type=(
            _AI_EVALUATION_BENCHMARKS_RED_TEAM_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="ai_evaluation_strategy_governance",
                title="🧭 Estratégia e governança da avaliação",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_evaluation_objectives_risk_profile"
                        ),
                        title="🎯 Objetivos e perfil de risco",
                        description=(
                            "Definição das capacidades, comportamentos, "
                            "riscos, usuários, contextos e resultados "
                            "que precisam ser avaliados."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_evaluation_dataset_suite_governance"
                        ),
                        title="🗃️ Datasets e conjuntos de avaliação",
                        description=(
                            "Organização de exemplos, cenários, perguntas, "
                            "respostas esperadas, metadados, versões, "
                            "fontes e permissões dos conjuntos de teste."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_evaluation_acceptance_thresholds"
                        ),
                        title="🚦 Critérios e limites de aprovação",
                        description=(
                            "Definição de métricas, limites mínimos, "
                            "tolerâncias, exceções, riscos residuais "
                            "e condições necessárias para aprovação."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_benchmarks_regression_comparison",
                title="📊 Benchmarks, regressão e comparação",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_functional_capability_benchmarks"
                        ),
                        title="🧩 Benchmarks de capacidades",
                        description=(
                            "Avaliação de compreensão, recuperação, "
                            "classificação, geração, raciocínio, extração "
                            "e demais capacidades esperadas da solução."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "enterprise_rag",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_domain_task_benchmarks"
                        ),
                        title="🏢 Benchmarks por domínio e tarefa",
                        description=(
                            "Avaliações adaptadas ao vocabulário, regras, "
                            "documentos, riscos, processos e critérios "
                            "específicos de cada domínio empresarial."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_regression_baseline_comparison"
                        ),
                        title="🔄 Regressão e comparação de versões",
                        description=(
                            "Comparação entre modelos, prompts, agentes, "
                            "ferramentas, configurações e versões para "
                            "identificar melhorias ou perdas de qualidade."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "data_traceability_provenance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_red_team_adversarial_security",
                title="🛡️ Red Team e testes adversariais",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_prompt_injection_jailbreak_testing"
                        ),
                        title="🧨 Prompt injection e jailbreak",
                        description=(
                            "Testes controlados para verificar manipulação "
                            "de instruções, quebra de limites, substituição "
                            "de contexto e evasão de políticas."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "cybersecurity_fraud_prevention",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_agent_tool_abuse_testing"
                        ),
                        title="🛠️ Abuso de agentes e ferramentas",
                        description=(
                            "Avaliação de chamadas indevidas, escalada "
                            "de privilégios, ações fora do escopo, repetição, "
                            "encadeamento inseguro e autonomia excessiva."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "agent_process_orchestration",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_data_exfiltration_privacy_attack_testing"
                        ),
                        title="🔐 Extração de dados e ataques à privacidade",
                        description=(
                            "Testes para identificar exposição de dados, "
                            "memorização indevida, inferência de informações, "
                            "vazamentos e acesso não autorizado."
                        ),
                        technology_dependencies=(
                            "privacy_enhancing_technologies",
                            "privacy_data_protection_lgpd",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_safety_factuality_robustness",
                title="✅ Segurança, factualidade e robustez",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_harmful_content_safety_evaluation"
                        ),
                        title="🚨 Conteúdo prejudicial e segurança",
                        description=(
                            "Avaliação de respostas incompatíveis com "
                            "as políticas, comportamentos inseguros, "
                            "conteúdo prejudicial e falhas dos guardrails."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "ai_model_agent_security",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_factuality_grounding_hallucination"
                        ),
                        title="📚 Factualidade e fundamentação",
                        description=(
                            "Verificação de afirmações, fontes, citações, "
                            "evidências, contradições e respostas não "
                            "fundamentadas ou incorretamente fundamentadas."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "data_traceability_provenance",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_robustness_distribution_shift"
                        ),
                        title="♻️ Robustez e mudanças de distribuição",
                        description=(
                            "Avaliação diante de ruído, variações, entradas "
                            "incompletas, mudanças de contexto, idioma, "
                            "formato, domínio e condições inesperadas."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "software_testing_quality_reliability",
                            "scientific_computing_engineering",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_performance_cost_resilience_evaluation",
                title="⚡ Desempenho, custos e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_latency_throughput_scalability_benchmark"
                        ),
                        title="⏱️ Latência, throughput e escala",
                        description=(
                            "Medição de tempo de resposta, concorrência, "
                            "capacidade, saturação, filas e comportamento "
                            "sob diferentes volumes de utilização."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_token_cost_resource_efficiency"
                        ),
                        title="💰 Tokens, custos e eficiência",
                        description=(
                            "Avaliação do consumo de tokens, chamadas, "
                            "processamento, armazenamento, rede, energia "
                            "e custo por tarefa ou resultado."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "tools_analytics",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_failure_fallback_degraded_mode_testing"
                        ),
                        title="♻️ Falhas, fallback e operação degradada",
                        description=(
                            "Testes de indisponibilidade de modelos, "
                            "ferramentas, dados e integrações, incluindo "
                            "retentativas, fallback e interrupção segura."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_human_evaluation_scenario_lab",
                title="👥 Avaliação humana e laboratório de cenários",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_human_evaluation_rubric_calibration"
                        ),
                        title="📋 Rubricas e calibração de avaliadores",
                        description=(
                            "Definição de critérios, escalas, exemplos, "
                            "instruções e sessões de calibração para reduzir "
                            "diferenças entre avaliadores humanos."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "enterprise_decision_intelligence",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_expert_user_scenario_evaluation"
                        ),
                        title="🧑‍💼 Avaliação com especialistas e usuários",
                        description=(
                            "Execução de cenários representativos com "
                            "especialistas, operadores e usuários para "
                            "avaliar utilidade, clareza e adequação."
                        ),
                        technology_dependencies=(
                            "ai_collaboration_meetings_productivity",
                            "digital_experiences_intelligent_interfaces",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_evaluation_disagreement_adjudication"
                        ),
                        title="⚖️ Divergências e adjudicação",
                        description=(
                            "Tratamento de avaliações divergentes, casos "
                            "ambíguos, escalonamentos, revisão especializada "
                            "e registro das decisões finais."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "agent_process_orchestration",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_evaluation_evidence_release_monitoring",
                title="🧾 Evidências, liberação e monitoramento",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_evaluation_evidence_provenance"
                        ),
                        title="🧬 Evidências e proveniência da avaliação",
                        description=(
                            "Registro de datasets, versões, modelos, prompts, "
                            "ferramentas, configurações, métricas, avaliadores, "
                            "resultados e artefatos produzidos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_release_quality_certification_readiness"
                        ),
                        title="🚦 Gates de qualidade e preparação de evidências",
                        description=(
                            "Consolidação de resultados, riscos, exceções, "
                            "aprovações e evidências necessárias para "
                            "decidir sobre liberação ou certificação."
                        ),
                        technology_dependencies=(
                            "ai_certification_system_evidence",
                            "software_testing_quality_reliability",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_continuous_evaluation_retesting"
                        ),
                        title="📡 Avaliação contínua e retestes",
                        description=(
                            "Execução recorrente de avaliações após mudanças "
                            "de modelo, dados, prompts, ferramentas, políticas "
                            "ou comportamento observado em produção."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "ai_bias_quality_monitoring",
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

    module_id = "ai_evaluation_benchmarks_red_team"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        52: (364, 1092),
        53: (371, 1113),
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

    print("AI_EVALUATION_BENCHMARKS_RED_TEAM_PREREQUISITES=OK")


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
    """Adiciona Avaliação de IA, Benchmarks e Red Team."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION =" in source:
        print("AI_EVALUATION_BENCHMARKS_RED_TEAM_ALREADY_PRESENT=OK")
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
        AI_EVALUATION_BENCHMARKS_RED_TEAM_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    RESPONSIBLE_AI_ETHICS_RISK_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION_CREATED=OK")


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

    solution_name = "AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 52
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 53
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

    test_name = "def test_ai_evaluation_benchmarks_red_team_is_complete"

    if test_name not in source:
        source += """


def test_ai_evaluation_benchmarks_red_team_is_complete():
    assert (
        AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION.solution_id
        == "ai_evaluation_benchmarks_red_team"
    )

    assert len(
        AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION.areas
    ) == 7

    assert (
        AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION
        .capability_count
        == 21
    )


def test_ai_evaluation_benchmarks_red_team_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_evaluation_benchmarks_red_team"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION.status
        is module.status
    )

    assert (
        AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_ai_evaluation_benchmarks_red_team_lookup():
    assert (
        platform_technology_solution(
            "ai_evaluation_benchmarks_red_team"
        )
        is AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION
    )
"""

        print("AI_EVALUATION_BENCHMARKS_RED_TEAM_TESTS_CREATED=OK")
    else:
        print("AI_EVALUATION_BENCHMARKS_RED_TEAM_TESTS_ALREADY_PRESENT=OK")

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

    evaluation_solution = module.AI_EVALUATION_BENCHMARKS_RED_TEAM_SOLUTION

    assert len(solutions) == 53
    assert len(evaluation_solution.areas) == 7

    assert evaluation_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 371
    assert total_capabilities == 1113

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=53")
    print("TOTAL_TECHNOLOGY_AREAS=371")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1113")
    print("AI_EVALUATION_BENCHMARKS_RED_TEAM_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
