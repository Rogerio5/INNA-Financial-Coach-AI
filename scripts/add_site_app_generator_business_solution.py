"""Adiciona Gerador de Sites e Apps ao registro empresarial."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

REGISTRY_PATH = ROOT / "src" / "platform_business_solutions.py"

TEST_PATH = ROOT / "tests" / "unit" / "test_platform_business_solutions.py"

BACKUP_ROOT = (
    ROOT
    / ".migration_backups"
    / ("site_app_generator_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


SITE_APP_GENERATOR_DEFINITION = """
SITE_APP_GENERATOR_SOLUTION = PlatformBusinessSolution(
    solution_id="site_app_generator",
    icon="🌐",
    title="Gerador de Sites e Apps",
    description=(
        "Solução empresarial para planejamento, prototipação, "
        "geração de interfaces, desenvolvimento assistido, "
        "integrações, testes, segurança, publicação e evolução "
        "de sites e aplicações."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="site_app_discovery_planning",
            title="🧭 Descoberta e planejamento do produto",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_requirements_scope",
                    title="📋 Requisitos, objetivos e escopo",
                    description=(
                        "Organização de objetivos, público, requisitos, "
                        "restrições, funcionalidades e critérios de sucesso."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "knowledge_graph_semantic_ai",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_user_journeys_architecture",
                    title="🗺️ Jornadas e arquitetura da informação",
                    description=(
                        "Mapeamento de usuários, jornadas, páginas, "
                        "navegação, conteúdos, fluxos e relacionamentos."
                    ),
                    technology_dependencies=(
                        "digital_experiences_intelligent_interfaces",
                        "knowledge_graph_semantic_ai",
                        "tools_analytics",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_backlog_roadmap",
                    title="📅 Backlog e roteiro de evolução",
                    description=(
                        "Priorização de funcionalidades, entregas, "
                        "dependências, versões, responsáveis e etapas."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "business_automation",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="site_app_design_prototyping",
            title="🎨 Design e prototipação",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_design_system",
                    title="🎨 Identidade visual e sistema de design",
                    description=(
                        "Definição de componentes, tipografia, espaçamento, "
                        "ícones, padrões visuais e consistência de interface."
                    ),
                    technology_dependencies=(
                        "digital_experiences_intelligent_interfaces",
                        "multimodal_ai",
                        "mobile_apps_omnichannel_experiences",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_interactive_prototypes",
                    title="🖼️ Wireframes e protótipos interativos",
                    description=(
                        "Criação assistida de estruturas, telas, páginas, "
                        "fluxos e protótipos para validação."
                    ),
                    technology_dependencies=(
                        "digital_experiences_intelligent_interfaces",
                        "multimodal_ai",
                        "ai_software_engineering",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_accessibility_usability",
                    title="♿ Acessibilidade e usabilidade",
                    description=(
                        "Verificação de navegação, leitura, contraste, "
                        "responsividade, clareza e experiência de uso."
                    ),
                    technology_dependencies=(
                        "software_testing_quality_reliability",
                        "digital_experiences_intelligent_interfaces",
                        "quality_process_management",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="site_app_frontend_generation",
            title="💻 Interfaces e front-end",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_pages_components_generation",
                    title="🧩 Geração de páginas e componentes",
                    description=(
                        "Criação assistida de páginas, componentes, "
                        "layouts, seções e elementos reutilizáveis."
                    ),
                    technology_dependencies=(
                        "ai_software_engineering",
                        "digital_experiences_intelligent_interfaces",
                        "software_testing_quality_reliability",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_responsive_themes",
                    title="📱 Responsividade e temas",
                    description=(
                        "Adaptação para computadores, tablets, celulares, "
                        "temas visuais e diferentes experiências."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "digital_experiences_intelligent_interfaces",
                        "multimodal_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_forms_navigation_state",
                    title="📝 Formulários, navegação e estado",
                    description=(
                        "Construção de formulários, validações, menus, "
                        "rotas, filtros, interações e estados da interface."
                    ),
                    technology_dependencies=(
                        "ai_software_engineering",
                        "business_automation",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="site_app_backend_data_integrations",
            title="🔌 Back-end, dados e integrações",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_api_business_logic",
                    title="🔌 APIs e regras de negócio",
                    description=(
                        "Criação assistida de endpoints, serviços, "
                        "validações, regras e operações empresariais."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "ai_software_engineering",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_data_models_persistence",
                    title="🗄️ Modelos de dados e persistência",
                    description=(
                        "Definição de entidades, relacionamentos, "
                        "armazenamento, consultas e regras de consistência."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "ai_software_engineering",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_auth_external_integrations",
                    title="🔐 Autenticação e integrações externas",
                    description=(
                        "Integração com identidade, permissões, APIs, "
                        "serviços empresariais e plataformas externas."
                    ),
                    technology_dependencies=(
                        "zero_trust_identity_access",
                        "api_integrations_connectors",
                        "cloud_devops_finops",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="site_app_quality_security_deployment",
            title="✅ Qualidade, segurança e publicação",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_automated_testing",
                    title="🧪 Testes automatizados e validação",
                    description=(
                        "Execução de testes unitários, integração, "
                        "interface, regressão, desempenho e confiabilidade."
                    ),
                    technology_dependencies=(
                        "software_testing_quality_reliability",
                        "ai_software_engineering",
                        "quality_process_management",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_security_privacy",
                    title="🛡️ Segurança e privacidade",
                    description=(
                        "Verificação de acessos, entradas, dependências, "
                        "dados pessoais, configurações e riscos."
                    ),
                    technology_dependencies=(
                        "operational_security_resilience",
                        "privacy_data_protection_lgpd",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_deployment_observability",
                    title="🚀 Deploy e observabilidade",
                    description=(
                        "Publicação controlada, ambientes, logs, métricas, "
                        "alertas, disponibilidade e acompanhamento."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "ai_operations",
                        "operational_security_resilience",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="site_app_lifecycle_analytics_governance",
            title="📊 Evolução, analytics e governança",
            capabilities=(
                BusinessCapability(
                    capability_id="site_app_content_configuration",
                    title="📝 Conteúdo e configurações",
                    description=(
                        "Gestão de textos, imagens, páginas, parâmetros, "
                        "versões, publicação e atualização de conteúdo."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "business_automation",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_usage_analytics_feedback",
                    title="📊 Analytics e feedback de uso",
                    description=(
                        "Acompanhamento de acessos, jornadas, eventos, "
                        "conversões, erros, avaliações e oportunidades."
                    ),
                    technology_dependencies=(
                        "tools_analytics",
                        "data_bi_copilot",
                        "real_time_event_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="site_app_versions_governance_review",
                    title="🧾 Versões, governança e revisão humana",
                    description=(
                        "Controle de alterações, responsáveis, aprovações, "
                        "evidências, reversões e decisões de publicação."
                    ),
                    technology_dependencies=(
                        "technology_governance_policy_compliance",
                        "data_traceability_provenance",
                        "responsible_ai_ethics_risk",
                    ),
                ),
            ),
        ),
    ),
)


"""


def validate_prerequisites() -> None:
    """Valida arquivos e o card principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro empresarial não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes empresariais não encontrados.")

    from src.platform_modules import PLATFORM_MODULE_BY_ID

    module_id = "site_app_generator"

    if module_id not in PLATFORM_MODULE_BY_ID:
        raise RuntimeError(f"O card {module_id} não existe no registro principal.")

    print("SITE_APP_GENERATOR_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria cópias antes da alteração."""

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
    """Adiciona Gerador de Sites e Apps ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "SITE_APP_GENERATOR_SOLUTION = PlatformBusinessSolution(" in source:
        print("SITE_APP_GENERATOR_ALREADY_PRESENT=OK")
        return

    registry_anchor = """PLATFORM_BUSINESS_SOLUTIONS: tuple[
    PlatformBusinessSolution,
    ...
] = (
"""

    if registry_anchor not in source:
        raise RuntimeError("Âncora do registro empresarial não encontrada.")

    source = source.replace(
        registry_anchor,
        SITE_APP_GENERATOR_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    HR_PEOPLE_ANALYTICS_SOLUTION,
    FINANCIAL_SOLUTIONS_SOLUTION,
)"""

    new_registry = """    HR_PEOPLE_ANALYTICS_SOLUTION,
    FINANCIAL_SOLUTIONS_SOLUTION,
    SITE_APP_GENERATOR_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro empresarial não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("SITE_APP_GENERATOR_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_site_app_generator_solution_is_complete" in source:
        print("SITE_APP_GENERATOR_TESTS_ALREADY_PRESENT=OK")
        return

    import_start = source.find("from src.platform_business_solutions import (\n")

    if import_start == -1:
        raise RuntimeError("Bloco de importações empresariais não encontrado.")

    import_end = source.find(
        ")\n",
        import_start,
    )

    if import_end == -1:
        raise RuntimeError("Final do bloco de importações não encontrado.")

    import_block = source[import_start:import_end]

    solution_name = "SITE_APP_GENERATOR_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 11"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 12"

    if old_count not in source:
        raise RuntimeError("Contagem atual de onze soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_site_app_generator_solution_is_complete():
    assert (
        SITE_APP_GENERATOR_SOLUTION.solution_id
        == "site_app_generator"
    )
    assert (
        SITE_APP_GENERATOR_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        SITE_APP_GENERATOR_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        SITE_APP_GENERATOR_SOLUTION.areas
    ) == 6
    assert (
        SITE_APP_GENERATOR_SOLUTION.capability_count
        == 18
    )


def test_site_app_generator_solution_lookup():
    assert (
        platform_business_solution(
            "site_app_generator"
        )
        is SITE_APP_GENERATOR_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("SITE_APP_GENERATOR_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        PLATFORM_BUSINESS_SOLUTIONS,
        SITE_APP_GENERATOR_SOLUTION,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 12

    assert (
        platform_business_solution("site_app_generator") is SITE_APP_GENERATOR_SOLUTION
    )

    assert len(SITE_APP_GENERATOR_SOLUTION.areas) == 6

    assert SITE_APP_GENERATOR_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 72
    assert total_capabilities == 215

    business_solution_ids = {
        solution.solution_id for solution in PLATFORM_BUSINESS_SOLUTIONS
    }

    assert len(business_solution_ids) == 12

    print("SPECIALIZED_BUSINESS_SOLUTIONS=12")
    print("TOTAL_BUSINESS_AREAS=72")
    print("TOTAL_BUSINESS_CAPABILITIES=215")
    print("SITE_APP_GENERATOR_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
