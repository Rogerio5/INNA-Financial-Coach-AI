"""Adiciona IA Responsável, Ética e Gestão de Riscos."""

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
        "responsible_ai_ethics_risk_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


RESPONSIBLE_AI_ETHICS_RISK_DEFINITION = """
_RESPONSIBLE_AI_ETHICS_RISK_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "responsible_ai_ethics_risk"
    ]
)


RESPONSIBLE_AI_ETHICS_RISK_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="responsible_ai_ethics_risk",
        icon="⚖️",
        title="IA Responsável, Ética e Gestão de Riscos",
        description=(
            "Arquitetura tecnológica para princípios de IA responsável, "
            "papéis e responsabilidades, inventário de casos de uso, "
            "avaliação de riscos e impactos, equidade, inclusão, "
            "transparência, explicabilidade, supervisão humana, "
            "segurança, privacidade, prevenção de abuso, monitoramento, "
            "incidentes, evidências, auditoria e melhoria contínua."
        ),
        status=(
            _RESPONSIBLE_AI_ETHICS_RISK_MODULE.status
        ),
        integration_type=(
            _RESPONSIBLE_AI_ETHICS_RISK_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "responsible_ai_governance_accountability"
                ),
                title="🏛️ Governança e responsabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_principles_policy"
                        ),
                        title="📜 Princípios e políticas de IA responsável",
                        description=(
                            "Definição de princípios, limites, critérios, "
                            "práticas obrigatórias e comportamentos "
                            "proibidos para sistemas de inteligência artificial."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_roles_accountability"
                        ),
                        title="👥 Papéis e prestação de contas",
                        description=(
                            "Definição de responsáveis por desenvolvimento, "
                            "aprovação, operação, revisão, risco, incidentes "
                            "e resultados produzidos pelos sistemas de IA."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "digital_identity_verifiable_credentials",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_use_case_inventory"
                        ),
                        title="📚 Inventário e classificação de casos de uso",
                        description=(
                            "Registro de modelos, agentes, finalidades, "
                            "usuários, dados, decisões apoiadas, criticidade "
                            "e estágio do ciclo de vida de cada solução."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_risk_impact_assessment"
                ),
                title="⚠️ Riscos e avaliação de impactos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_risk_assessment"
                        ),
                        title="⚠️ Avaliação de riscos de IA",
                        description=(
                            "Identificação e classificação de riscos "
                            "técnicos, humanos, sociais, financeiros, "
                            "operacionais, legais e reputacionais."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_stakeholder_harm_analysis"
                        ),
                        title="👥 Impactos sobre pessoas e grupos",
                        description=(
                            "Análise de pessoas afetadas, benefícios, "
                            "possíveis danos, desigualdades, vulnerabilidades "
                            "e consequências diretas ou indiretas."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "model_explainability_interpretability",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_risk_treatment_approval"
                        ),
                        title="🧑‍⚖️ Tratamento e aceitação de riscos",
                        description=(
                            "Definição de controles, responsáveis, prazos, "
                            "riscos residuais, aprovações, exceções "
                            "e condições necessárias para utilização."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_fairness_inclusion"
                ),
                title="🤝 Equidade, vieses e inclusão",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_fairness_evaluation"
                        ),
                        title="⚖️ Avaliação de equidade",
                        description=(
                            "Avaliação de resultados entre grupos, contextos "
                            "e condições diferentes por métricas adequadas "
                            "à finalidade e ao impacto do sistema."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "ai_evaluation_benchmarks_red_team",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_bias_data_model_monitoring"
                        ),
                        title="🔎 Vieses em dados e modelos",
                        description=(
                            "Identificação de vieses em coleta, amostragem, "
                            "rótulos, atributos, treinamento, avaliação, "
                            "inferência e utilização dos resultados."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "data_traceability_provenance",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_inclusion_accessibility_review"
                        ),
                        title="♿ Inclusão e acessibilidade",
                        description=(
                            "Revisão de barreiras, linguagem, interfaces, "
                            "canais, tecnologias assistivas e condições "
                            "que possam limitar a participação dos usuários."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "mobile_apps_omnichannel_experiences",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_transparency_explainability"
                ),
                title="🔍 Transparência e explicabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_transparency_disclosure"
                        ),
                        title="📢 Transparência sobre o uso de IA",
                        description=(
                            "Comunicação de que existe utilização de IA, "
                            "sua finalidade, responsabilidades, fontes, "
                            "limites e formas de solicitar suporte."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "enterprise_rag",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_explainability_support"
                        ),
                        title="🧠 Explicações para decisões e recomendações",
                        description=(
                            "Apresentação dos fatores, evidências, regras, "
                            "modelos, alternativas e limitações relevantes "
                            "para compreender o resultado produzido."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "enterprise_decision_intelligence",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_uncertainty_limitations"
                        ),
                        title="🎲 Incertezas e limitações",
                        description=(
                            "Comunicação de confiança, lacunas, hipóteses, "
                            "situações não cobertas, possíveis erros "
                            "e condições em que o resultado não deve ser usado."
                        ),
                        technology_dependencies=(
                            "model_explainability_interpretability",
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_human_oversight_safety"
                ),
                title="👤 Supervisão humana e segurança",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_human_oversight"
                        ),
                        title="👁️ Supervisão e intervenção humana",
                        description=(
                            "Mecanismos para revisar, corrigir, pausar, "
                            "aprovar, rejeitar ou substituir decisões "
                            "e ações realizadas com apoio de IA."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "enterprise_decision_intelligence",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_guardrails_fail_safe"
                        ),
                        title="🛑 Guardrails e comportamento seguro",
                        description=(
                            "Limites de ferramentas, dados, ações, escopo, "
                            "autonomia, recursos e respostas, incluindo "
                            "interrupção segura diante de falhas."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "operational_security_resilience",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_high_impact_controls"
                        ),
                        title="🚦 Controles para decisões de alto impacto",
                        description=(
                            "Aplicação de revisão adicional, dupla aprovação, "
                            "segregação de funções, explicação, contestação "
                            "e registro para decisões críticas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_privacy_security_misuse"
                ),
                title="🔐 Privacidade, segurança e prevenção de abuso",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_privacy_data_protection"
                        ),
                        title="🕶️ Privacidade e proteção de dados",
                        description=(
                            "Aplicação de finalidade, minimização, retenção, "
                            "consentimento, proteção, anonimização "
                            "e controle de acesso aos dados utilizados."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_security_misuse_prevention"
                        ),
                        title="🛡️ Segurança e prevenção de uso indevido",
                        description=(
                            "Proteção contra manipulação, extração de dados, "
                            "evasão de controles, abuso de ferramentas, "
                            "acessos indevidos e comportamentos maliciosos."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "cybersecurity_fraud_prevention",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_content_harm_controls"
                        ),
                        title="🚨 Conteúdo prejudicial e integridade",
                        description=(
                            "Detecção e tratamento de conteúdo inseguro, "
                            "enganoso, discriminatório, inadequado ou "
                            "incompatível com as políticas da solução."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "multimodal_ai",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "responsible_ai_monitoring_evidence_improvement"
                ),
                title="📊 Monitoramento, evidências e melhoria",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_monitoring_incident_response"
                        ),
                        title="📡 Monitoramento e resposta a incidentes",
                        description=(
                            "Monitoramento de falhas, desvios, reclamações, "
                            "impactos inesperados, violações, mudanças "
                            "de comportamento e eventos de risco."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_evidence_audit_traceability"
                        ),
                        title="🧾 Evidências e auditoria de IA",
                        description=(
                            "Registro de dados, modelos, versões, avaliações, "
                            "riscos, aprovações, intervenções, incidentes, "
                            "custos, decisões e resultados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_certification_system_evidence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "responsible_ai_remediation_improvement"
                        ),
                        title="🔄 Correção e melhoria contínua",
                        description=(
                            "Planejamento e acompanhamento de correções, "
                            "novas avaliações, atualização de controles, "
                            "revisão de modelos e validação das melhorias."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "business_automation",
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

    module_id = "responsible_ai_ethics_risk"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        51: (357, 1071),
        52: (364, 1092),
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

    print("RESPONSIBLE_AI_ETHICS_RISK_PREREQUISITES=OK")


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
    """Adiciona IA Responsável, Ética e Gestão de Riscos."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "RESPONSIBLE_AI_ETHICS_RISK_SOLUTION =" in source:
        print("RESPONSIBLE_AI_ETHICS_RISK_ALREADY_PRESENT=OK")
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
        RESPONSIBLE_AI_ETHICS_RISK_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    OPERATIONAL_SECURITY_RESILIENCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    RESPONSIBLE_AI_ETHICS_RISK_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("RESPONSIBLE_AI_ETHICS_RISK_SOLUTION_CREATED=OK")


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

    solution_name = "RESPONSIBLE_AI_ETHICS_RISK_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 51
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 52
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

    test_name = "def test_responsible_ai_ethics_risk_is_complete"

    if test_name not in source:
        source += """


def test_responsible_ai_ethics_risk_is_complete():
    assert (
        RESPONSIBLE_AI_ETHICS_RISK_SOLUTION.solution_id
        == "responsible_ai_ethics_risk"
    )

    assert len(
        RESPONSIBLE_AI_ETHICS_RISK_SOLUTION.areas
    ) == 7

    assert (
        RESPONSIBLE_AI_ETHICS_RISK_SOLUTION
        .capability_count
        == 21
    )


def test_responsible_ai_ethics_risk_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "responsible_ai_ethics_risk"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        RESPONSIBLE_AI_ETHICS_RISK_SOLUTION.status
        is module.status
    )

    assert (
        RESPONSIBLE_AI_ETHICS_RISK_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_responsible_ai_ethics_risk_lookup():
    assert (
        platform_technology_solution(
            "responsible_ai_ethics_risk"
        )
        is RESPONSIBLE_AI_ETHICS_RISK_SOLUTION
    )
"""

        print("RESPONSIBLE_AI_ETHICS_RISK_TESTS_CREATED=OK")
    else:
        print("RESPONSIBLE_AI_ETHICS_RISK_TESTS_ALREADY_PRESENT=OK")

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

    responsible_ai_solution = module.RESPONSIBLE_AI_ETHICS_RISK_SOLUTION

    assert len(solutions) == 52
    assert len(responsible_ai_solution.areas) == 7

    assert responsible_ai_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 364
    assert total_capabilities == 1092

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=52")
    print("TOTAL_TECHNOLOGY_AREAS=364")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1092")
    print("RESPONSIBLE_AI_ETHICS_RISK_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
