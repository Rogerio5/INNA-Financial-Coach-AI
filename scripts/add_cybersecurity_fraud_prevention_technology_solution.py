"""Adiciona Cibersegurança e Prevenção a Fraudes ao registro tecnológico."""

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
        "cybersecurity_fraud_prevention_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


CYBERSECURITY_FRAUD_PREVENTION_DEFINITION = """
_CYBERSECURITY_FRAUD_PREVENTION_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "cybersecurity_fraud_prevention"
    ]
)


CYBERSECURITY_FRAUD_PREVENTION_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="cybersecurity_fraud_prevention",
        icon="🛡️",
        title="Cibersegurança e Prevenção a Fraudes",
        description=(
            "Arquitetura tecnológica para proteção de identidades, "
            "aplicações, APIs, dados, transações e modelos de IA, "
            "com detecção de ameaças, análise de risco, prevenção "
            "a fraudes, resposta a incidentes, governança, "
            "auditoria, resiliência e observabilidade."
        ),
        status=(
            _CYBERSECURITY_FRAUD_PREVENTION_MODULE.status
        ),
        integration_type=(
            _CYBERSECURITY_FRAUD_PREVENTION_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="cybersecurity_identity_access_protection",
                title="🔐 Identidade, acesso e proteção de contas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_identity_risk",
                        title="🪪 Risco de identidade e autenticação",
                        description=(
                            "Avaliação de tentativas de acesso, contexto, "
                            "dispositivo, localização aproximada, comportamento "
                            "e sinais de risco autorizados."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "enterprise_decision_intelligence",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_privileged_access",
                        title="🔑 Acessos privilegiados e credenciais",
                        description=(
                            "Controle de contas administrativas, credenciais, "
                            "segredos, tokens, escopos e operações sensíveis."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_account_abuse_detection",
                        title="⚠️ Detecção de abuso de contas",
                        description=(
                            "Identificação de acessos incomuns, uso indevido, "
                            "automação suspeita e mudanças de comportamento."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "tools_analytics",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cybersecurity_telemetry_threat_intelligence",
                title="📡 Telemetria e inteligência de ameaças",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_security_event_ingestion",
                        title="📥 Ingestão de eventos de segurança",
                        description=(
                            "Coleta de eventos de aplicações, APIs, redes, "
                            "identidades, bancos, dispositivos e serviços."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_threat_intelligence",
                        title="🧠 Inteligência de ameaças",
                        description=(
                            "Organização de indicadores, padrões, campanhas, "
                            "vulnerabilidades e conhecimento de ameaças."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_event_correlation",
                        title="🔗 Correlação de eventos e sinais",
                        description=(
                            "Combinação de eventos, identidades, dispositivos, "
                            "transações, alertas e contexto operacional."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="fraud_detection_risk_scoring",
                title="💳 Detecção de fraudes e análise de risco",
                capabilities=(
                    TechnologyCapability(
                        capability_id="fraud_transaction_monitoring",
                        title="💳 Monitoramento de transações",
                        description=(
                            "Análise de transações, solicitações, operações "
                            "e eventos para identificação de padrões suspeitos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="fraud_risk_scoring",
                        title="📊 Score de risco e priorização",
                        description=(
                            "Classificação de risco com regras, modelos, "
                            "contexto, histórico e níveis de confiança."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="fraud_behavior_anomaly_detection",
                        title="📉 Comportamento e anomalias",
                        description=(
                            "Identificação de desvios em frequência, valor, "
                            "sequência, origem, dispositivo e comportamento."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "scientific_computing_engineering",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cybersecurity_ai_application_protection",
                title="🤖 Proteção de aplicações, APIs e IA",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_api_application_protection",
                        title="🌐 Proteção de APIs e aplicações",
                        description=(
                            "Validação de requisições, autenticação, limites, "
                            "integridade, padrões suspeitos e operações sensíveis."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_ai_model_agent_protection",
                        title="🤖 Proteção de modelos e agentes",
                        description=(
                            "Controles contra manipulação de instruções, "
                            "uso indevido de ferramentas, vazamento e abuso."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "agent_process_orchestration",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_adversarial_testing",
                        title="🧪 Testes adversariais de segurança",
                        description=(
                            "Avaliação controlada de entradas maliciosas, "
                            "falhas de autorização, evasão e comportamentos "
                            "não esperados."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cybersecurity_investigation_response",
                title="🚨 Investigação e resposta",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_alert_triage",
                        title="🚨 Triagem e priorização de alertas",
                        description=(
                            "Classificação de alertas por impacto, confiança, "
                            "criticidade, contexto e necessidade de resposta."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_case_investigation",
                        title="🔎 Investigação e gestão de casos",
                        description=(
                            "Organização de evidências, eventos, envolvidos, "
                            "linha do tempo, hipóteses e decisões."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "data_traceability_provenance",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_automated_response",
                        title="⚡ Resposta automatizada e contenção",
                        description=(
                            "Execução controlada de bloqueios, revogações, "
                            "notificações, isolamento e encaminhamento humano."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cybersecurity_governance_privacy_audit",
                title="🧾 Governança, privacidade e auditoria",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_policy_compliance",
                        title="⚖️ Políticas e conformidade",
                        description=(
                            "Aplicação de políticas, controles mínimos, "
                            "responsabilidades, exceções e evidências."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "privacy_data_protection_lgpd",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_evidence_audit",
                        title="🧾 Evidências e trilha de auditoria",
                        description=(
                            "Registro de eventos, acessos, decisões, respostas, "
                            "alterações, responsáveis e justificativas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "operational_security_resilience",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_sensitive_data_protection",
                        title="🔐 Proteção de dados sensíveis",
                        description=(
                            "Mascaramento, minimização, criptografia, retenção "
                            "e controle de exposição de informações."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cybersecurity_resilience_observability_lifecycle",
                title="📊 Resiliência e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cybersecurity_security_observability",
                        title="📊 Métricas e observabilidade de segurança",
                        description=(
                            "Monitoramento de alertas, incidentes, tempo de "
                            "resposta, cobertura, falhas e eficácia dos controles."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_resilience_recovery",
                        title="♻️ Resiliência e recuperação",
                        description=(
                            "Continuidade, restauração, recuperação de serviços "
                            "e validação de cenários de indisponibilidade."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cybersecurity_continuous_improvement",
                        title="📈 Melhoria contínua dos controles",
                        description=(
                            "Evolução de regras, modelos, procedimentos, "
                            "playbooks e controles com base em resultados."
                        ),
                        technology_dependencies=(
                            "quality_process_management",
                            "ai_evaluation_benchmarks_red_team",
                            "enterprise_decision_intelligence",
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

    module_id = "cybersecurity_fraud_prevention"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        10: (70, 210),
        11: (77, 231),
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

    print("CYBERSECURITY_FRAUD_PREVENTION_PREREQUISITES=OK")


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
    """Adiciona a solução ao registro tecnológico."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "CYBERSECURITY_FRAUD_PREVENTION_SOLUTION =" in source:
        print("CYBERSECURITY_FRAUD_PREVENTION_ALREADY_PRESENT=OK")
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
        CYBERSECURITY_FRAUD_PREVENTION_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    CLOUD_DEVOPS_FINOPS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    CYBERSECURITY_FRAUD_PREVENTION_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CYBERSECURITY_FRAUD_PREVENTION_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_cybersecurity_fraud_prevention_is_complete" in source:
        print("CYBERSECURITY_FRAUD_PREVENTION_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "CYBERSECURITY_FRAUD_PREVENTION_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 10
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 11
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de dez soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_cybersecurity_fraud_prevention_is_complete():
    assert (
        CYBERSECURITY_FRAUD_PREVENTION_SOLUTION.solution_id
        == "cybersecurity_fraud_prevention"
    )

    assert len(
        CYBERSECURITY_FRAUD_PREVENTION_SOLUTION.areas
    ) == 7

    assert (
        CYBERSECURITY_FRAUD_PREVENTION_SOLUTION.capability_count
        == 21
    )


def test_cybersecurity_fraud_prevention_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "cybersecurity_fraud_prevention"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        CYBERSECURITY_FRAUD_PREVENTION_SOLUTION.status
        is module.status
    )

    assert (
        CYBERSECURITY_FRAUD_PREVENTION_SOLUTION.integration_type
        == module.integration_type
    )


def test_cybersecurity_fraud_prevention_lookup():
    assert (
        platform_technology_solution(
            "cybersecurity_fraud_prevention"
        )
        is CYBERSECURITY_FRAUD_PREVENTION_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CYBERSECURITY_FRAUD_PREVENTION_TESTS_CREATED=OK")


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

    cybersecurity_solution = getattr(
        module,
        "CYBERSECURITY_FRAUD_PREVENTION_SOLUTION",
    )

    assert len(solutions) == 11

    assert len(cybersecurity_solution.areas) == 7

    assert cybersecurity_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 77
    assert total_capabilities == 231

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=11")
    print("TOTAL_TECHNOLOGY_AREAS=77")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=231")
    print("CYBERSECURITY_FRAUD_PREVENTION_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
