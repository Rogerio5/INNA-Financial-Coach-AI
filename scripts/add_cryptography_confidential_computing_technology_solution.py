"""Adiciona Criptografia e Computação Confidencial ao registro tecnológico."""

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
        "cryptography_confidential_computing_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_DEFINITION = """
_CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "cryptography_confidential_computing"
    ]
)


CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="cryptography_confidential_computing",
        icon="🔒",
        title="Criptografia e Computação Confidencial",
        description=(
            "Arquitetura tecnológica para gestão de chaves, "
            "criptografia em trânsito e armazenamento, assinaturas "
            "digitais, certificados, execução em ambientes confiáveis, "
            "atestação, proteção de cargas de trabalho, governança, "
            "auditoria, resiliência e preparação criptográfica futura."
        ),
        status=(
            _CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_MODULE.status
        ),
        integration_type=(
            _CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="cryptography_key_management",
                title="🔑 Gestão de chaves criptográficas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_key_inventory_lifecycle",
                        title="🗂️ Inventário e ciclo de vida de chaves",
                        description=(
                            "Registro de chaves, responsáveis, finalidades, "
                            "algoritmos, versões, validade e sistemas associados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_kms_hsm",
                        title="🛡️ KMS, HSM e armazenamento protegido",
                        description=(
                            "Proteção de chaves em serviços especializados, "
                            "módulos de segurança e ambientes controlados."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "operational_security_resilience",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_rotation_revocation",
                        title="🔄 Rotação, revogação e expiração",
                        description=(
                            "Substituição periódica, revogação emergencial, "
                            "expiração e atualização segura das chaves."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "real_time_event_intelligence",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cryptography_data_protection",
                title="🗄️ Proteção criptográfica dos dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_data_at_rest",
                        title="🗄️ Criptografia em armazenamento",
                        description=(
                            "Proteção de bancos, arquivos, backups, objetos, "
                            "volumes e bases de conhecimento armazenadas."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_data_in_transit",
                        title="🌐 Criptografia em trânsito",
                        description=(
                            "Proteção das comunicações entre usuários, APIs, "
                            "serviços, agentes, bancos e ambientes."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_field_level_tokenization",
                        title="🕶️ Criptografia de campos e tokenização",
                        description=(
                            "Proteção seletiva de identificadores, documentos, "
                            "valores e informações sensíveis."
                        ),
                        technology_dependencies=(
                            "privacy_enhancing_technologies",
                            "privacy_data_protection_lgpd",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cryptography_signatures_certificates",
                title="✍️ Assinaturas, certificados e confiança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_digital_signatures",
                        title="✍️ Assinaturas digitais",
                        description=(
                            "Assinatura e verificação de documentos, mensagens, "
                            "artefatos, eventos e operações autorizadas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "legal_compliance",
                            "document_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_pki_certificates",
                        title="📜 Certificados e infraestrutura de chaves",
                        description=(
                            "Emissão, validação, renovação, revogação "
                            "e governança de certificados digitais."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_workload_identity",
                        title="🤖 Identidade criptográfica de workloads",
                        description=(
                            "Identificação e autenticação de serviços, agentes, "
                            "containers, dispositivos e pipelines."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cloud_devops_finops",
                            "software_supply_chain_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="confidential_computing_execution",
                title="🧠 Computação confidencial",
                capabilities=(
                    TechnologyCapability(
                        capability_id="confidential_trusted_execution",
                        title="🛡️ Ambientes de execução confiável",
                        description=(
                            "Execução de cargas de trabalho em regiões "
                            "protegidas contra acesso externo não autorizado."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "operational_security_resilience",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="confidential_workload_protection",
                        title="📦 Proteção de workloads confidenciais",
                        description=(
                            "Isolamento de aplicações, agentes, modelos, "
                            "dados e cálculos durante a execução."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "cloud_devops_finops",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="confidential_remote_attestation",
                        title="✅ Atestação remota",
                        description=(
                            "Verificação da integridade, identidade e estado "
                            "do ambiente antes da liberação de dados ou chaves."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "software_supply_chain_security",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cryptography_privacy_ai",
                title="🤖 Criptografia aplicada à IA e privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_encrypted_processing",
                        title="🧮 Processamento protegido de dados",
                        description=(
                            "Processamento com redução da exposição dos dados "
                            "durante análises e operações autorizadas."
                        ),
                        technology_dependencies=(
                            "privacy_enhancing_technologies",
                            "scientific_computing_engineering",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_ai_secrets_protection",
                        title="🔐 Proteção de modelos, prompts e segredos",
                        description=(
                            "Proteção de credenciais, configurações, prompts, "
                            "modelos, embeddings e dados privados da IA."
                        ),
                        technology_dependencies=(
                            "ai_model_agent_security",
                            "enterprise_rag",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_privacy_integrations",
                        title="🔌 Integrações com privacidade preservada",
                        description=(
                            "Troca de informações entre sistemas com "
                            "criptografia, tokenização e exposição mínima."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "privacy_enhancing_technologies",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cryptography_governance_compliance",
                title="🧾 Governança e conformidade criptográfica",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_policy_standards",
                        title="📋 Políticas e padrões criptográficos",
                        description=(
                            "Definição de algoritmos permitidos, tamanhos "
                            "de chave, finalidades, responsabilidades e exceções."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "cybersecurity_fraud_prevention",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_audit_evidence",
                        title="🧾 Auditoria e evidências",
                        description=(
                            "Registro de criação, acesso, utilização, rotação, "
                            "revogação e alterações dos ativos criptográficos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "tools_analytics",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_post_quantum_readiness",
                        title="🧪 Preparação pós-quântica",
                        description=(
                            "Inventário de dependências criptográficas, "
                            "avaliação de riscos e planejamento de migrações."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "software_supply_chain_security",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cryptography_operations_resilience",
                title="📊 Operações e resiliência criptográfica",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cryptography_monitoring_alerts",
                        title="📊 Monitoramento e alertas",
                        description=(
                            "Acompanhamento de validade, uso, falhas, acessos, "
                            "configurações inseguras e eventos criptográficos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "real_time_event_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_backup_recovery",
                        title="♻️ Backup e recuperação de chaves",
                        description=(
                            "Proteção, recuperação e validação controlada "
                            "de materiais criptográficos essenciais."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cryptography_incident_response",
                        title="🚨 Resposta a incidentes criptográficos",
                        description=(
                            "Revogação, substituição, investigação, contenção "
                            "e recuperação após comprometimento ou falha."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "operational_security_resilience",
                            "agent_process_orchestration",
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

    module_id = "cryptography_confidential_computing"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        16: (112, 336),
        17: (119, 357),
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

    print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_PREREQUISITES=OK")


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

    if "CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION =" in source:
        print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_ALREADY_PRESENT=OK")
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
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ZERO_TRUST_IDENTITY_ACCESS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_cryptography_confidential_computing_is_complete"

    if test_name in source:
        print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 16
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 17
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de dezesseis soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_cryptography_confidential_computing_is_complete():
    assert (
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION.solution_id
        == "cryptography_confidential_computing"
    )

    assert len(
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION.areas
    ) == 7

    assert (
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION.capability_count
        == 21
    )


def test_cryptography_confidential_computing_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "cryptography_confidential_computing"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION.status
        is module.status
    )

    assert (
        CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION.integration_type
        == module.integration_type
    )


def test_cryptography_confidential_computing_lookup():
    assert (
        platform_technology_solution(
            "cryptography_confidential_computing"
        )
        is CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_TESTS_CREATED=OK")


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

    cryptography_solution = getattr(
        module,
        "CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION",
    )

    assert len(solutions) == 17

    assert len(cryptography_solution.areas) == 7

    assert cryptography_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 119
    assert total_capabilities == 357

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=17")
    print("TOTAL_TECHNOLOGY_AREAS=119")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=357")
    print("CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
