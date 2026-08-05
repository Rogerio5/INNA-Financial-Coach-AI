"""Adiciona Segurança de Modelos e Agentes de IA ao registro tecnológico."""

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
    / ("ai_model_agent_security_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


AI_MODEL_AGENT_SECURITY_DEFINITION = """
_AI_MODEL_AGENT_SECURITY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "ai_model_agent_security"
    ]
)


AI_MODEL_AGENT_SECURITY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="ai_model_agent_security",
        icon="🔐",
        title="Segurança de Modelos e Agentes de IA",
        description=(
            "Arquitetura tecnológica para modelagem de ameaças, "
            "proteção de prompts, contexto, ferramentas, modelos, "
            "dados e cadeia de fornecimento, com monitoramento, "
            "testes adversariais, governança, resposta a incidentes "
            "e gestão segura do ciclo de vida de sistemas de IA."
        ),
        status=(
            _AI_MODEL_AGENT_SECURITY_MODULE.status
        ),
        integration_type=(
            _AI_MODEL_AGENT_SECURITY_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="ai_security_threat_modeling",
                title="🧭 Ameaças e superfície de ataque",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_threat_modeling",
                        title="🧭 Modelagem de ameaças de IA",
                        description=(
                            "Identificação de ativos, agentes, modelos, "
                            "ferramentas, dados, usuários, limites de confiança "
                            "e possíveis caminhos de ataque."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "operational_security_resilience",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_attack_surface_inventory",
                        title="🗂️ Inventário da superfície de ataque",
                        description=(
                            "Registro de endpoints, modelos, prompts, "
                            "conectores, ferramentas, permissões, dados "
                            "e dependências externas."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "api_integrations_connectors",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_risk_classification",
                        title="📊 Classificação e priorização de riscos",
                        description=(
                            "Classificação de riscos conforme probabilidade, "
                            "impacto, criticidade, exposição e controles."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_prompt_context_inputs",
                title="🛡️ Prompts, contexto e entradas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_prompt_injection_defense",
                        title="🛡️ Defesa contra injeção de instruções",
                        description=(
                            "Detecção, filtragem e tratamento de instruções "
                            "maliciosas ou conflitantes em entradas e fontes."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "ai_evaluation_benchmarks_red_team",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_context_isolation",
                        title="🧩 Isolamento e controle de contexto",
                        description=(
                            "Separação de instruções, dados, histórico, "
                            "fontes recuperadas e informações entre usuários."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "zero_trust_identity_access",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_input_validation",
                        title="✅ Validação e sanitização de entradas",
                        description=(
                            "Validação de formatos, tamanhos, tipos, "
                            "conteúdos, anexos e parâmetros antes da execução."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "api_integrations_connectors",
                            "multimodal_ai",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_tools_actions_permissions",
                title="🧰 Ferramentas, ações e permissões",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_tool_allowlist",
                        title="📋 Allowlist e registro de ferramentas",
                        description=(
                            "Uso apenas de ferramentas registradas, "
                            "versionadas, autorizadas e adequadas ao agente."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_action_authorization",
                        title="🔐 Autorização de ações sensíveis",
                        description=(
                            "Validação de identidade, escopo, contexto "
                            "e permissão antes de executar operações."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "agent_process_orchestration",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_tool_sandboxing",
                        title="📦 Isolamento e sandbox de execução",
                        description=(
                            "Execução limitada de ferramentas e códigos "
                            "com restrições de recursos, rede e acesso."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "operational_security_resilience",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_model_data_supply_chain",
                title="📦 Modelos, dados e cadeia de fornecimento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_model_provenance",
                        title="🔗 Proveniência e integridade de modelos",
                        description=(
                            "Registro de origem, fornecedor, versão, "
                            "configuração, avaliações e alterações dos modelos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_operations",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_training_knowledge_data",
                        title="🗄️ Proteção de dados e conhecimento",
                        description=(
                            "Controles sobre dados de treinamento, avaliação, "
                            "memória, documentos e bases de conhecimento."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_dependency_supply_chain",
                        title="🔍 Dependências e cadeia de fornecimento",
                        description=(
                            "Verificação de bibliotecas, imagens, modelos, "
                            "serviços, conectores e artefatos externos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "cybersecurity_fraud_prevention",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_runtime_monitoring",
                title="📡 Monitoramento e proteção em execução",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_runtime_guardrails",
                        title="🚧 Guardrails em tempo de execução",
                        description=(
                            "Aplicação de regras e validações antes e depois "
                            "das respostas, decisões e chamadas de ferramentas."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "agent_process_orchestration",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_behavior_monitoring",
                        title="📊 Monitoramento de comportamento",
                        description=(
                            "Acompanhamento de ações, ferramentas, padrões, "
                            "erros, tentativas bloqueadas e desvios."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_exfiltration_detection",
                        title="🚨 Detecção de vazamento e exfiltração",
                        description=(
                            "Identificação de tentativas de revelar dados, "
                            "segredos, instruções internas ou conteúdos restritos."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_evaluation_governance",
                title="🧪 Avaliação, governança e conformidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_red_team_testing",
                        title="🧪 Red Team e testes adversariais",
                        description=(
                            "Avaliação controlada de manipulação, evasão, "
                            "vazamento, abuso de ferramentas e respostas inseguras."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "cybersecurity_fraud_prevention",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_security_benchmarks",
                        title="📈 Métricas e benchmarks de segurança",
                        description=(
                            "Medição de bloqueios, falsos alertas, cobertura, "
                            "robustez, incidentes e eficácia dos controles."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "tools_analytics",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_policy_audit",
                        title="🧾 Políticas e trilha de auditoria",
                        description=(
                            "Registro de versões, acessos, decisões, "
                            "aprovações, exceções, eventos e evidências."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="ai_security_incidents_lifecycle",
                title="🚨 Incidentes e ciclo de vida seguro",
                capabilities=(
                    TechnologyCapability(
                        capability_id="ai_security_incident_response",
                        title="🚨 Resposta a incidentes de IA",
                        description=(
                            "Detecção, contenção, investigação, comunicação, "
                            "recuperação e documentação de incidentes."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cybersecurity_fraud_prevention",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_kill_switch_recovery",
                        title="🛑 Interrupção segura e recuperação",
                        description=(
                            "Suspensão de agentes, ferramentas ou versões "
                            "e retorno controlado para configurações seguras."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="ai_security_continuous_hardening",
                        title="📈 Hardening e melhoria contínua",
                        description=(
                            "Atualização de regras, testes, permissões, "
                            "modelos de ameaça e controles de proteção."
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

    module_id = "ai_model_agent_security"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        12: (84, 252),
        13: (91, 273),
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

    print("AI_MODEL_AGENT_SECURITY_PREREQUISITES=OK")


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

    if "AI_MODEL_AGENT_SECURITY_SOLUTION =" in source:
        print("AI_MODEL_AGENT_SECURITY_ALREADY_PRESENT=OK")
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
        AI_MODEL_AGENT_SECURITY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    TOOLS_ANALYTICS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    AI_MODEL_AGENT_SECURITY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_MODEL_AGENT_SECURITY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_ai_model_agent_security_is_complete" in source:
        print("AI_MODEL_AGENT_SECURITY_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "AI_MODEL_AGENT_SECURITY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 12
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 13
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de doze soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_ai_model_agent_security_is_complete():
    assert (
        AI_MODEL_AGENT_SECURITY_SOLUTION.solution_id
        == "ai_model_agent_security"
    )

    assert len(
        AI_MODEL_AGENT_SECURITY_SOLUTION.areas
    ) == 7

    assert (
        AI_MODEL_AGENT_SECURITY_SOLUTION.capability_count
        == 21
    )


def test_ai_model_agent_security_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_model_agent_security"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_MODEL_AGENT_SECURITY_SOLUTION.status
        is module.status
    )

    assert (
        AI_MODEL_AGENT_SECURITY_SOLUTION.integration_type
        == module.integration_type
    )


def test_ai_model_agent_security_lookup():
    assert (
        platform_technology_solution(
            "ai_model_agent_security"
        )
        is AI_MODEL_AGENT_SECURITY_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("AI_MODEL_AGENT_SECURITY_TESTS_CREATED=OK")


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

    security_solution = getattr(
        module,
        "AI_MODEL_AGENT_SECURITY_SOLUTION",
    )

    assert len(solutions) == 13

    assert len(security_solution.areas) == 7

    assert security_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 91
    assert total_capabilities == 273

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=13")
    print("TOTAL_TECHNOLOGY_AREAS=91")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=273")
    print("AI_MODEL_AGENT_SECURITY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
