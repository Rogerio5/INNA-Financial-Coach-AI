"""Adiciona RH e People Analytics ao registro empresarial."""

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
    / ("hr_people_analytics_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


HR_PEOPLE_ANALYTICS_DEFINITION = """
HR_PEOPLE_ANALYTICS_SOLUTION = PlatformBusinessSolution(
    solution_id="hr_people_analytics",
    icon="👥",
    title="RH e People Analytics",
    description=(
        "Solução empresarial para estrutura organizacional, "
        "recrutamento, integração, competências, desempenho, "
        "desenvolvimento, experiência, capacidade e analytics de pessoas."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="hr_people_structure_records",
            title="🏢 Estrutura organizacional e cadastros",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_people_profiles_records",
                    title="👤 Perfis e registros profissionais",
                    description=(
                        "Organização de dados profissionais, documentos, "
                        "experiências, competências, vínculos e histórico."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "document_ai",
                        "privacy_data_protection_lgpd",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_organization_structure",
                    title="🏢 Estrutura organizacional",
                    description=(
                        "Cadastro de áreas, equipes, cargos, posições, "
                        "gestores, unidades e relações organizacionais."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_employee_lifecycle",
                    title="🔄 Ciclo de vida profissional",
                    description=(
                        "Acompanhamento de admissões, movimentações, "
                        "alterações, afastamentos administrativos e desligamentos."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="hr_recruitment_onboarding",
            title="🎯 Recrutamento e integração",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_job_position_management",
                    title="📋 Vagas, cargos e requisitos",
                    description=(
                        "Definição de vagas, responsabilidades, requisitos, "
                        "competências, etapas e responsáveis."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "knowledge_graph_semantic_ai",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_candidate_screening",
                    title="🔎 Triagem e compatibilidade de candidatos",
                    description=(
                        "Análise assistida de currículos, requisitos, "
                        "competências e aderência à vaga, com revisão humana."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "document_ai",
                        "ai_bias_quality_monitoring",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_onboarding_workflows",
                    title="🤝 Integração e onboarding",
                    description=(
                        "Coordenação de documentos, tarefas, treinamentos, "
                        "acessos, responsáveis e acompanhamento inicial."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "zero_trust_identity_access",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="hr_performance_skills",
            title="🎯 Desempenho e competências",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_goals_performance_reviews",
                    title="🎯 Metas e avaliações de desempenho",
                    description=(
                        "Gestão de metas, ciclos, critérios, avaliações, "
                        "feedbacks, resultados e planos de ação."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "business_automation",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_skills_mapping",
                    title="🧠 Mapeamento de competências",
                    description=(
                        "Organização de competências técnicas, comportamentais, "
                        "níveis esperados, evidências e lacunas."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "enterprise_rag",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_feedback_development_plans",
                    title="📈 Feedbacks e planos de desenvolvimento",
                    description=(
                        "Registro de feedbacks, necessidades, objetivos, "
                        "ações de desenvolvimento e acompanhamento."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "intelligent_support",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="hr_learning_career_succession",
            title="🎓 Aprendizagem, carreira e sucessão",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_learning_paths",
                    title="🎓 Trilhas de aprendizagem",
                    description=(
                        "Organização de cursos, conteúdos, competências, "
                        "pré-requisitos, progresso e conclusão."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "document_ai",
                        "digital_experiences_intelligent_interfaces",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_career_paths",
                    title="🧭 Carreira e mobilidade interna",
                    description=(
                        "Mapeamento de trajetórias, oportunidades internas, "
                        "competências necessárias e possíveis evoluções."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "enterprise_decision_intelligence",
                        "data_bi_copilot",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_succession_planning",
                    title="🔄 Planejamento de sucessão",
                    description=(
                        "Análise de posições críticas, continuidade, "
                        "preparação, riscos e planos de desenvolvimento."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "simulation_optimization_operations_research",
                        "responsible_ai_ethics_risk",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="hr_experience_engagement_capacity",
            title="💬 Experiência, engajamento e capacidade",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_employee_experience",
                    title="💬 Experiência do colaborador",
                    description=(
                        "Centralização de solicitações, comunicações, "
                        "serviços internos, dúvidas e jornadas profissionais."
                    ),
                    technology_dependencies=(
                        "intelligent_support",
                        "mobile_apps_omnichannel_experiences",
                        "business_automation",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_engagement_feedback",
                    title="⭐ Engajamento e feedback organizacional",
                    description=(
                        "Coleta e análise de pesquisas, comentários, "
                        "percepções, oportunidades e planos de melhoria."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "tools_analytics",
                        "ai_bias_quality_monitoring",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_workforce_capacity_planning",
                    title="📅 Capacidade e planejamento da força de trabalho",
                    description=(
                        "Análise de demanda, disponibilidade, competências, "
                        "carga, necessidades futuras e cenários."
                    ),
                    technology_dependencies=(
                        "scientific_computing_engineering",
                        "simulation_optimization_operations_research",
                        "enterprise_decision_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="hr_analytics_governance_privacy",
            title="📊 People Analytics, governança e privacidade",
            capabilities=(
                BusinessCapability(
                    capability_id="hr_people_dashboards",
                    title="📊 Indicadores de pessoas",
                    description=(
                        "Acompanhamento de quadro, movimentações, vagas, "
                        "desempenho, competências, aprendizagem e capacidade."
                    ),
                    technology_dependencies=(
                        "data_bi_copilot",
                        "tools_analytics",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_people_risk_forecasting",
                    title="📈 Tendências e riscos organizacionais",
                    description=(
                        "Análise assistida de tendências, capacidade, "
                        "lacunas, movimentações e cenários organizacionais."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "scientific_computing_engineering",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                BusinessCapability(
                    capability_id="hr_privacy_fairness_audit",
                    title="🔐 Privacidade, equidade e auditoria",
                    description=(
                        "Proteção de dados, controle de acesso, avaliação "
                        "de vieses, rastreabilidade e evidências de decisões."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "ai_bias_quality_monitoring",
                        "data_traceability_provenance",
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

    module_id = "hr_people_analytics"

    if module_id not in PLATFORM_MODULE_BY_ID:
        raise RuntimeError(f"O card {module_id} não existe no registro principal.")

    print("HR_PEOPLE_ANALYTICS_PREREQUISITES=OK")


def create_backup() -> None:
    """Cria cópias dos arquivos antes da alteração."""

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
    """Adiciona RH e People Analytics ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "HR_PEOPLE_ANALYTICS_SOLUTION = PlatformBusinessSolution(" in source:
        print("HR_PEOPLE_ANALYTICS_ALREADY_PRESENT=OK")
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
        HR_PEOPLE_ANALYTICS_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    ERP_BUSINESS_OPERATIONS_SOLUTION,
    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
)"""

    new_registry = """    ERP_BUSINESS_OPERATIONS_SOLUTION,
    SUPPLY_CHAIN_PROCUREMENT_LOGISTICS_SOLUTION,
    HR_PEOPLE_ANALYTICS_SOLUTION,
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

    print("HR_PEOPLE_ANALYTICS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Atualiza os testes empresariais."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_hr_people_analytics_solution_is_complete" in source:
        print("HR_PEOPLE_ANALYTICS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "HR_PEOPLE_ANALYTICS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 9"

    new_count = "assert len(PLATFORM_BUSINESS_SOLUTIONS) == 10"

    if old_count not in source:
        raise RuntimeError("Contagem atual de nove soluções não encontrada.")

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_hr_people_analytics_solution_is_complete():
    assert (
        HR_PEOPLE_ANALYTICS_SOLUTION.solution_id
        == "hr_people_analytics"
    )
    assert (
        HR_PEOPLE_ANALYTICS_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        HR_PEOPLE_ANALYTICS_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        HR_PEOPLE_ANALYTICS_SOLUTION.areas
    ) == 6
    assert (
        HR_PEOPLE_ANALYTICS_SOLUTION.capability_count
        == 18
    )


def test_hr_people_analytics_solution_lookup():
    assert (
        platform_business_solution(
            "hr_people_analytics"
        )
        is HR_PEOPLE_ANALYTICS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("HR_PEOPLE_ANALYTICS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Confirma o resultado da expansão."""

    from src.platform_business_solutions import (
        HR_PEOPLE_ANALYTICS_SOLUTION,
        PLATFORM_BUSINESS_SOLUTIONS,
        platform_business_solution,
    )

    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 10

    assert (
        platform_business_solution("hr_people_analytics")
        is HR_PEOPLE_ANALYTICS_SOLUTION
    )

    assert len(HR_PEOPLE_ANALYTICS_SOLUTION.areas) == 6

    assert HR_PEOPLE_ANALYTICS_SOLUTION.capability_count == 18

    total_areas = sum(len(solution.areas) for solution in PLATFORM_BUSINESS_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_BUSINESS_SOLUTIONS
    )

    assert total_areas == 60
    assert total_capabilities == 179

    print("SPECIALIZED_BUSINESS_SOLUTIONS=10")
    print("TOTAL_BUSINESS_AREAS=60")
    print("TOTAL_BUSINESS_CAPABILITIES=179")
    print("HR_PEOPLE_ANALYTICS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
