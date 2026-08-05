"""Adiciona Cloud, DevOps e FinOps ao registro tecnológico."""

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
    / ("cloud_devops_finops_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


CLOUD_DEVOPS_FINOPS_DEFINITION = """
_CLOUD_DEVOPS_FINOPS_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "cloud_devops_finops"
    ]
)


CLOUD_DEVOPS_FINOPS_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="cloud_devops_finops",
        icon="☁️",
        title="Cloud, DevOps e FinOps",
        description=(
            "Arquitetura tecnológica para fundação cloud, "
            "infraestrutura como código, integração e entrega "
            "contínuas, containers, observabilidade, SRE, "
            "segurança, resiliência, custos, capacidade "
            "e governança do ciclo de vida."
        ),
        status=(
            _CLOUD_DEVOPS_FINOPS_MODULE.status
        ),
        integration_type=(
            _CLOUD_DEVOPS_FINOPS_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="cloud_foundation_architecture",
                title="☁️ Fundação e arquitetura cloud",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_accounts_environments",
                        title="🏢 Contas, projetos e ambientes",
                        description=(
                            "Organização de contas, projetos, assinaturas, "
                            "ambientes, regiões, responsáveis e limites."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_networking_connectivity",
                        title="🌐 Redes e conectividade",
                        description=(
                            "Configuração de redes, sub-redes, rotas, "
                            "gateways, balanceamento e conectividade segura."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "zero_trust_identity_access",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_compute_storage_databases",
                        title="🗄️ Computação, armazenamento e bancos",
                        description=(
                            "Provisionamento governado de recursos "
                            "computacionais, armazenamento e serviços de dados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "operational_security_resilience",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="devops_source_delivery",
                title="🚀 Código, integração e entrega contínuas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="devops_source_control_branching",
                        title="🌿 Versionamento e estratégia de branches",
                        description=(
                            "Organização de repositórios, branches, revisões, "
                            "proteções, tags e histórico de alterações."
                        ),
                        technology_dependencies=(
                            "ai_software_engineering",
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="devops_continuous_integration",
                        title="🔄 Integração contínua",
                        description=(
                            "Automação de validações, testes, análise estática, "
                            "builds e geração controlada de artefatos."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "business_automation",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="devops_continuous_delivery",
                        title="🚀 Entrega e implantação contínuas",
                        description=(
                            "Promoção de versões entre ambientes com "
                            "aprovações, verificações e reversão controlada."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "business_automation",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cloud_infrastructure_platform",
                title="🏗️ Infraestrutura e plataformas",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_infrastructure_as_code",
                        title="📜 Infraestrutura como código",
                        description=(
                            "Definição versionada e reproduzível de redes, "
                            "serviços, permissões e recursos de infraestrutura."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_containers_orchestration",
                        title="📦 Containers e orquestração",
                        description=(
                            "Empacotamento, execução, escalabilidade, "
                            "descoberta e gerenciamento de aplicações."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "ai_operations",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_platform_services",
                        title="🧩 Serviços de plataforma",
                        description=(
                            "Disponibilização de componentes reutilizáveis "
                            "para aplicações, dados, agentes e integrações."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "agent_process_orchestration",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cloud_observability_sre",
                title="📊 Observabilidade e SRE",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_logs_metrics_traces",
                        title="📊 Logs, métricas e tracing",
                        description=(
                            "Coleta e correlação de logs, métricas, traces, "
                            "eventos, dependências e indicadores operacionais."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_slos_slas_error_budgets",
                        title="🎯 SLOs, SLAs e orçamento de erros",
                        description=(
                            "Definição de metas de disponibilidade, "
                            "desempenho, confiabilidade e tolerância a falhas."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_incident_response",
                        title="🚨 Incidentes e resposta operacional",
                        description=(
                            "Detecção, classificação, comunicação, mitigação, "
                            "recuperação e análise de incidentes."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "operational_security_resilience",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cloud_security_resilience",
                title="🛡️ Segurança e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_identity_secrets",
                        title="🔐 Identidade, acessos e segredos",
                        description=(
                            "Gestão de papéis, permissões, credenciais, "
                            "segredos, tokens e identidades de serviços."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "privacy_enhancing_technologies",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_policy_compliance",
                        title="🧾 Políticas e conformidade cloud",
                        description=(
                            "Aplicação de padrões, políticas, restrições, "
                            "auditoria e evidências de conformidade."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_backup_disaster_recovery",
                        title="♻️ Backup e recuperação de desastre",
                        description=(
                            "Proteção, restauração, replicação, continuidade "
                            "e testes de recuperação dos serviços."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cloud_finops_capacity",
                title="💰 FinOps e capacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_cost_allocation_tags",
                        title="🏷️ Alocação de custos e tags",
                        description=(
                            "Classificação de recursos e custos por produto, "
                            "ambiente, equipe, cliente e centro de custo."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_platform_governance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_budgets_cost_anomalies",
                        title="🚨 Orçamentos e anomalias de custo",
                        description=(
                            "Monitoramento de orçamento, consumo inesperado, "
                            "tendências e desvios financeiros."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "real_time_event_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_rightsizing_capacity",
                        title="📈 Rightsizing e planejamento de capacidade",
                        description=(
                            "Ajuste de recursos e previsão de capacidade "
                            "com base em uso, demanda e desempenho."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="cloud_lifecycle_multicloud",
                title="🔄 Ciclo de vida e ambientes híbridos",
                capabilities=(
                    TechnologyCapability(
                        capability_id="cloud_environment_promotion",
                        title="🚀 Promoção entre ambientes",
                        description=(
                            "Movimentação controlada de configurações, "
                            "artefatos e infraestrutura entre ambientes."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_operations",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_multicloud_hybrid",
                        title="🌐 Multicloud e ambientes híbridos",
                        description=(
                            "Integração de recursos locais e provedores "
                            "de nuvem com conectividade e governança comuns."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="cloud_decommissioning_sustainability",
                        title="🌱 Desativação e eficiência sustentável",
                        description=(
                            "Desativação segura de recursos ociosos, "
                            "controle de resíduos e melhoria de eficiência."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_decision_intelligence",
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

    module_id = "cloud_devops_finops"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        9: (63, 189),
        10: (70, 210),
    }

    if current_count not in expected_totals:
        raise RuntimeError(f"Quantidade atual inesperada: {current_count}")

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

    print("CLOUD_DEVOPS_FINOPS_PREREQUISITES=OK")


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

    if "CLOUD_DEVOPS_FINOPS_SOLUTION =" in source:
        print("CLOUD_DEVOPS_FINOPS_ALREADY_PRESENT=OK")
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
        CLOUD_DEVOPS_FINOPS_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    API_INTEGRATIONS_CONNECTORS_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    CLOUD_DEVOPS_FINOPS_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("CLOUD_DEVOPS_FINOPS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_cloud_devops_finops_is_complete" in source:
        print("CLOUD_DEVOPS_FINOPS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "CLOUD_DEVOPS_FINOPS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 9
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 10
"""

    if old_count not in source:
        raise RuntimeError("Contagem atual de nove soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_cloud_devops_finops_is_complete():
    assert (
        CLOUD_DEVOPS_FINOPS_SOLUTION.solution_id
        == "cloud_devops_finops"
    )

    assert len(
        CLOUD_DEVOPS_FINOPS_SOLUTION.areas
    ) == 7

    assert (
        CLOUD_DEVOPS_FINOPS_SOLUTION.capability_count
        == 21
    )


def test_cloud_devops_finops_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "cloud_devops_finops"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        CLOUD_DEVOPS_FINOPS_SOLUTION.status
        is module.status
    )

    assert (
        CLOUD_DEVOPS_FINOPS_SOLUTION.integration_type
        == module.integration_type
    )


def test_cloud_devops_finops_lookup():
    assert (
        platform_technology_solution(
            "cloud_devops_finops"
        )
        is CLOUD_DEVOPS_FINOPS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("CLOUD_DEVOPS_FINOPS_TESTS_CREATED=OK")


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

    cloud_solution = getattr(
        module,
        "CLOUD_DEVOPS_FINOPS_SOLUTION",
    )

    assert len(solutions) == 10
    assert len(cloud_solution.areas) == 7
    assert cloud_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 70
    assert total_capabilities == 210

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=10")
    print("TOTAL_TECHNOLOGY_AREAS=70")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=210")
    print("CLOUD_DEVOPS_FINOPS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
