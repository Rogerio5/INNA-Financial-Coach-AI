"""Adiciona Certificação de IA e Evidências do Sistema."""

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
        "ai_certification_system_evidence_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


AI_CERTIFICATION_SYSTEM_EVIDENCE_DEFINITION = """
_AI_CERTIFICATION_SYSTEM_EVIDENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "ai_certification_system_evidence"
    ]
)


AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="ai_certification_system_evidence",
        icon="🏅",
        title="Certificação de IA e Evidências do Sistema",
        description=(
            "Arquitetura tecnológica para definição do escopo de "
            "certificação, classificação de riscos, requisitos e "
            "controles, coleta e integridade de evidências, validação "
            "técnica, segurança, qualidade, equidade, explicabilidade, "
            "documentação, revisão independente, aprovação, atestação, "
            "credenciais verificáveis, monitoramento contínuo, "
            "recertificação, suspensão, revogação, auditoria "
            "e observabilidade do ciclo de vida da IA."
        ),
        status=(
            _AI_CERTIFICATION_SYSTEM_EVIDENCE_MODULE.status
        ),
        integration_type=(
            _AI_CERTIFICATION_SYSTEM_EVIDENCE_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id=(
                    "ai_certification_scope_governance"
                ),
                title="🏛️ Escopo, requisitos e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_scope_risk_classification"
                        ),
                        title="🎯 Escopo e classificação de risco",
                        description=(
                            "Definição do sistema, modelos, agentes, "
                            "finalidades, usuários, decisões, ambientes, "
                            "limites e nível de risco da certificação."
                        ),
                        technology_dependencies=(
                            "responsible_ai_ethics_risk",
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_requirements_control_mapping"
                        ),
                        title="🧩 Requisitos e controles aplicáveis",
                        description=(
                            "Mapeamento de políticas, requisitos, riscos, "
                            "controles, testes, evidências, responsáveis "
                            "e critérios necessários à certificação."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_roles_independence"
                        ),
                        title="👥 Papéis e independência da avaliação",
                        description=(
                            "Definição de proprietários, desenvolvedores, "
                            "avaliadores, aprovadores, auditores e regras "
                            "de independência e segregação de funções."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "digital_identity_verifiable_credentials",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_evidence_provenance"
                ),
                title="🧬 Evidências, integridade e proveniência",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_evidence_inventory"
                        ),
                        title="📚 Inventário de evidências",
                        description=(
                            "Organização de documentos, datasets, modelos, "
                            "avaliações, logs, aprovações, políticas, "
                            "incidentes e demais artefatos comprobatórios."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "data_platform_governance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_automated_evidence_collection"
                        ),
                        title="📥 Coleta automatizada de evidências",
                        description=(
                            "Coleta controlada de métricas, testes, "
                            "configurações, versões, logs, alertas "
                            "e resultados por integrações autorizadas."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "business_automation",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_evidence_integrity"
                        ),
                        title="🔐 Integridade e cadeia de custódia",
                        description=(
                            "Proteção de evidências por hashes, assinaturas, "
                            "controle de versões, horários, identidades, "
                            "transferências e histórico de alterações."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "data_traceability_provenance",
                            "digital_identity_verifiable_credentials",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_technical_assurance"
                ),
                title="🧪 Validação técnica e garantia",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_model_system_validation"
                        ),
                        title="✅ Validação de modelos e sistemas",
                        description=(
                            "Verificação de capacidades, qualidade, "
                            "robustez, desempenho, confiabilidade, "
                            "limitações e condições operacionais."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_security_red_team_assurance"
                        ),
                        title="🛡️ Segurança e red team",
                        description=(
                            "Consolidação de testes adversariais, "
                            "vulnerabilidades, ataques, abuso de agentes, "
                            "exposição de dados e eficácia dos controles."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "ai_model_agent_security",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_quality_fairness_explainability"
                        ),
                        title="⚖️ Qualidade, equidade e explicabilidade",
                        description=(
                            "Avaliação de qualidade, vieses, equidade, "
                            "drift, transparência, explicações, confiança "
                            "e impactos sobre pessoas e grupos."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "model_explainability_interpretability",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_documentation_findings"
                ),
                title="📄 Documentação, achados e correções",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_system_dossier"
                        ),
                        title="📁 Dossiê do sistema de IA",
                        description=(
                            "Consolidação de arquitetura, finalidade, dados, "
                            "modelos, agentes, avaliações, riscos, controles, "
                            "responsáveis, versões e evidências."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_findings_remediation"
                        ),
                        title="🔧 Achados e planos de correção",
                        description=(
                            "Registro de não conformidades, observações, "
                            "causas, criticidade, responsáveis, prazos, "
                            "ações corretivas e validação da resolução."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_exception_residual_risk"
                        ),
                        title="⚠️ Exceções e riscos residuais",
                        description=(
                            "Avaliação de exceções, justificativas, "
                            "controles compensatórios, prazo de validade, "
                            "aprovação e aceitação do risco residual."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "responsible_ai_ethics_risk",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_review_attestation"
                ),
                title="🏅 Revisão, aprovação e atestação",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_independent_review"
                        ),
                        title="🔎 Revisão técnica independente",
                        description=(
                            "Revisão das evidências, testes, riscos, "
                            "exceções e conclusões por avaliadores "
                            "autorizados e independentes do desenvolvimento."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "digital_identity_verifiable_credentials",
                            "ai_collaboration_meetings_productivity",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_approval_attestation"
                        ),
                        title="✍️ Aprovação e atestação",
                        description=(
                            "Registro da decisão de aprovar, aprovar "
                            "com condições, rejeitar ou solicitar novas "
                            "evidências, incluindo identidade e justificativa."
                        ),
                        technology_dependencies=(
                            "digital_identity_verifiable_credentials",
                            "cryptography_confidential_computing",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_credential_status"
                        ),
                        title="🪪 Credencial e estado da certificação",
                        description=(
                            "Emissão controlada de credencial verificável "
                            "com escopo, validade, versão, condições, "
                            "emissor e estado atual da certificação."
                        ),
                        technology_dependencies=(
                            "digital_identity_verifiable_credentials",
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_lifecycle_compliance"
                ),
                title="🔄 Ciclo de vida e conformidade contínua",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_change_reassessment"
                        ),
                        title="🔁 Mudanças e reavaliação",
                        description=(
                            "Identificação de mudanças em modelos, dados, "
                            "prompts, agentes, ferramentas, políticas "
                            "e infraestrutura que exijam nova avaliação."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_software_engineering",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_continuous_monitoring"
                        ),
                        title="📡 Monitoramento contínuo",
                        description=(
                            "Monitoramento de qualidade, vieses, drift, "
                            "segurança, incidentes, desempenho, custos "
                            "e cumprimento das condições certificadas."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_suspension_revocation"
                        ),
                        title="🛑 Suspensão e revogação",
                        description=(
                            "Suspensão, restrição ou revogação controlada "
                            "diante de incidentes, violações, mudanças "
                            "não aprovadas ou perda dos requisitos."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "technology_governance_policy_compliance",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id=(
                    "ai_certification_reporting_audit"
                ),
                title="📊 Interoperabilidade, relatórios e auditoria",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_machine_readable_evidence"
                        ),
                        title="🔌 Evidências interoperáveis",
                        description=(
                            "Representação estruturada de requisitos, "
                            "controles, resultados, credenciais e evidências "
                            "para integração com sistemas autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_stakeholder_reporting"
                        ),
                        title="📢 Relatórios e transparência",
                        description=(
                            "Geração de relatórios adaptados para gestão, "
                            "auditoria, equipes técnicas, usuários "
                            "e demais partes interessadas autorizadas."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "digital_experiences_intelligent_interfaces",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "ai_certification_audit_observability"
                        ),
                        title="🧾 Auditoria e observabilidade",
                        description=(
                            "Registro de versões, avaliações, evidências, "
                            "revisões, aprovações, credenciais, mudanças, "
                            "incidentes, custos e decisões do ciclo completo."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
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

    module_id = "ai_certification_system_evidence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        55: (385, 1155),
        56: (392, 1176),
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

    print("AI_CERTIFICATION_SYSTEM_EVIDENCE_PREREQUISITES=OK")


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
    """Adiciona Certificação de IA e Evidências."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION =" in source:
        print("AI_CERTIFICATION_SYSTEM_EVIDENCE_ALREADY_PRESENT=OK")
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
        AI_CERTIFICATION_SYSTEM_EVIDENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    AI_BIAS_QUALITY_MONITORING_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION_CREATED=OK")


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

    solution_name = "AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 55
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 56
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

    test_name = "def test_ai_certification_system_evidence_is_complete"

    if test_name not in source:
        source += """


def test_ai_certification_system_evidence_is_complete():
    assert (
        AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION.solution_id
        == "ai_certification_system_evidence"
    )

    assert len(
        AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION.areas
    ) == 7

    assert (
        AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION
        .capability_count
        == 21
    )


def test_ai_certification_system_evidence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_certification_system_evidence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION.status
        is module.status
    )

    assert (
        AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_ai_certification_system_evidence_lookup():
    assert (
        platform_technology_solution(
            "ai_certification_system_evidence"
        )
        is AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION
    )
"""

        print("AI_CERTIFICATION_SYSTEM_EVIDENCE_TESTS_CREATED=OK")
    else:
        print("AI_CERTIFICATION_SYSTEM_EVIDENCE_TESTS_ALREADY_PRESENT=OK")

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

    certification_solution = module.AI_CERTIFICATION_SYSTEM_EVIDENCE_SOLUTION

    assert len(solutions) == 56
    assert len(certification_solution.areas) == 7
    assert certification_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 392
    assert total_capabilities == 1176

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=56")
    print("TOTAL_TECHNOLOGY_AREAS=392")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=1176")
    print("AI_CERTIFICATION_SYSTEM_EVIDENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
