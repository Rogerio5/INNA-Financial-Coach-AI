"""Adiciona Segurança da Cadeia de Suprimentos de Software."""

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
        "software_supply_chain_security_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


SOFTWARE_SUPPLY_CHAIN_SECURITY_DEFINITION = """
_SOFTWARE_SUPPLY_CHAIN_SECURITY_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "software_supply_chain_security"
    ]
)


SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="software_supply_chain_security",
        icon="🔗",
        title="Segurança da Cadeia de Suprimentos de Software",
        description=(
            "Arquitetura tecnológica para inventário, proveniência, "
            "dependências, builds, pipelines, artefatos, containers, "
            "assinaturas, SBOM, políticas de implantação, monitoramento "
            "de vulnerabilidades, resposta a incidentes, auditoria "
            "e governança da cadeia de desenvolvimento."
        ),
        status=(
            _SOFTWARE_SUPPLY_CHAIN_SECURITY_MODULE.status
        ),
        integration_type=(
            _SOFTWARE_SUPPLY_CHAIN_SECURITY_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="supply_chain_inventory_provenance",
                title="🗂️ Inventário e proveniência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_asset_inventory",
                        title="🗂️ Inventário de ativos de software",
                        description=(
                            "Registro de repositórios, aplicações, serviços, "
                            "bibliotecas, containers, modelos e artefatos."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_source_provenance",
                        title="🔗 Proveniência do código-fonte",
                        description=(
                            "Rastreamento da origem, autoria, revisão, "
                            "branch, commit, versão e histórico do código."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_ownership_responsibility",
                        title="👥 Propriedade e responsáveis",
                        description=(
                            "Definição de equipes, proprietários, revisores, "
                            "aprovadores e responsáveis pelos ativos."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "zero_trust_identity_access",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_dependencies_packages",
                title="📦 Dependências e pacotes",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_dependency_scanning",
                        title="🔍 Análise de dependências",
                        description=(
                            "Identificação de bibliotecas vulneráveis, "
                            "desatualizadas, abandonadas ou incompatíveis."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "software_testing_quality_reliability",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_lockfile_integrity",
                        title="🔒 Integridade de lockfiles e versões",
                        description=(
                            "Validação de versões fixadas, hashes, origem "
                            "e alterações em arquivos de dependências."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_malicious_packages",
                        title="⚠️ Detecção de pacotes maliciosos",
                        description=(
                            "Identificação de typosquatting, código suspeito, "
                            "pacotes comprometidos e fontes não autorizadas."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_build_pipeline_security",
                title="🏗️ Builds e pipelines seguros",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_protected_ci",
                        title="🛡️ Integração contínua protegida",
                        description=(
                            "Proteção de runners, pipelines, branches, "
                            "aprovações e configurações de build."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_pipeline_secrets",
                        title="🔐 Segredos nos pipelines",
                        description=(
                            "Proteção, rotação e restrição de tokens, "
                            "credenciais e chaves usadas nas automações."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cryptography_confidential_computing",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_reproducible_builds",
                        title="♻️ Builds reproduzíveis e verificáveis",
                        description=(
                            "Produção consistente de artefatos a partir "
                            "das mesmas fontes e configurações autorizadas."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "cloud_devops_finops",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_artifacts_containers",
                title="📦 Artefatos e containers",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_artifact_signing",
                        title="✍️ Assinatura de artefatos",
                        description=(
                            "Assinatura e verificação de pacotes, imagens, "
                            "binários, modelos e arquivos distribuídos."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "data_traceability_provenance",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_container_scanning",
                        title="🔍 Análise de imagens e containers",
                        description=(
                            "Verificação de vulnerabilidades, configurações, "
                            "pacotes, permissões e conteúdo das imagens."
                        ),
                        technology_dependencies=(
                            "cybersecurity_fraud_prevention",
                            "cloud_devops_finops",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_registry_policies",
                        title="📋 Políticas de registries",
                        description=(
                            "Controle de origens, versões, assinaturas, "
                            "retenção, acesso e promoção de artefatos."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "zero_trust_identity_access",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_sbom_attestation_deployment",
                title="📜 SBOM, atestação e implantação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_sbom_generation",
                        title="📜 Geração e gestão de SBOM",
                        description=(
                            "Inventário dos componentes, versões, licenças "
                            "e dependências contidos em cada artefato."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_build_attestations",
                        title="✅ Atestações de build e proveniência",
                        description=(
                            "Evidências verificáveis sobre origem, processo, "
                            "ambiente e responsáveis pela geração."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_admission_controls",
                        title="🚧 Controles de admissão",
                        description=(
                            "Bloqueio de implantações que não atendam "
                            "assinaturas, políticas, avaliações e requisitos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "technology_governance_policy_compliance",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_monitoring_incidents",
                title="🚨 Monitoramento e incidentes",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_vulnerability_monitoring",
                        title="📡 Monitoramento de vulnerabilidades",
                        description=(
                            "Acompanhamento contínuo de novas vulnerabilidades "
                            "relacionadas aos componentes utilizados."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "cybersecurity_fraud_prevention",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_exposure_analysis",
                        title="📊 Análise de exposição e impacto",
                        description=(
                            "Identificação das aplicações, clientes, ambientes "
                            "e processos afetados por uma vulnerabilidade."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_revocation_rollback",
                        title="♻️ Revogação e rollback",
                        description=(
                            "Bloqueio de artefatos comprometidos, reversão "
                            "de versões e restauração controlada."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "operational_security_resilience",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="supply_chain_governance_audit_resilience",
                title="🧾 Governança e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="supply_chain_security_policies",
                        title="📋 Políticas da cadeia de software",
                        description=(
                            "Definição de requisitos mínimos para código, "
                            "dependências, builds, artefatos e implantações."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "cybersecurity_fraud_prevention",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_third_party_risk",
                        title="🤝 Risco de fornecedores e terceiros",
                        description=(
                            "Avaliação de fornecedores, serviços, componentes, "
                            "licenças, suporte e dependências externas."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "legal_compliance",
                            "cybersecurity_fraud_prevention",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="supply_chain_audit_metrics",
                        title="📊 Auditoria, métricas e melhoria contínua",
                        description=(
                            "Registro de alterações, violações, exceções, "
                            "tempo de correção e eficácia dos controles."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "tools_analytics",
                            "quality_process_management",
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

    module_id = "software_supply_chain_security"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        17: (119, 357),
        18: (126, 378),
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

    print("SOFTWARE_SUPPLY_CHAIN_SECURITY_PREREQUISITES=OK")


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

    if "SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION =" in source:
        print("SOFTWARE_SUPPLY_CHAIN_SECURITY_ALREADY_PRESENT=OK")
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
        SOFTWARE_SUPPLY_CHAIN_SECURITY_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    CRYPTOGRAPHY_CONFIDENTIAL_COMPUTING_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_software_supply_chain_security_is_complete" in source:
        print("SOFTWARE_SUPPLY_CHAIN_SECURITY_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 17
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 18
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de dezessete soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_software_supply_chain_security_is_complete():
    assert (
        SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION.solution_id
        == "software_supply_chain_security"
    )

    assert len(
        SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION.areas
    ) == 7

    assert (
        SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION.capability_count
        == 21
    )


def test_software_supply_chain_security_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "software_supply_chain_security"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION.status
        is module.status
    )

    assert (
        SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION.integration_type
        == module.integration_type
    )


def test_software_supply_chain_security_lookup():
    assert (
        platform_technology_solution(
            "software_supply_chain_security"
        )
        is SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SOFTWARE_SUPPLY_CHAIN_SECURITY_TESTS_CREATED=OK")


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

    supply_chain_solution = getattr(
        module,
        "SOFTWARE_SUPPLY_CHAIN_SECURITY_SOLUTION",
    )

    assert len(solutions) == 18

    assert len(supply_chain_solution.areas) == 7

    assert supply_chain_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 126
    assert total_capabilities == 378

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=18")
    print("TOTAL_TECHNOLOGY_AREAS=126")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=378")
    print("SOFTWARE_SUPPLY_CHAIN_SECURITY_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
