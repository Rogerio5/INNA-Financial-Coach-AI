"""Adiciona Engenharia de Software com IA ao registro tecnológico."""

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
    / ("ai_software_engineering_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


AI_SOFTWARE_ENGINEERING_DEFINITION = """
_AI_SOFTWARE_ENGINEERING_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "ai_software_engineering"
    ]
)


AI_SOFTWARE_ENGINEERING_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="ai_software_engineering",
        icon="💻",
        title="Engenharia de Software com IA",
        description=(
            "Arquitetura tecnológica para requisitos, arquitetura, "
            "geração e modernização de código, revisão assistida, "
            "inteligência de repositórios, documentação, testes, "
            "segurança, qualidade, CI/CD, releases, observabilidade, "
            "diagnóstico, confiabilidade, produtividade, governança "
            "e rastreabilidade do ciclo de desenvolvimento."
        ),
        status=(
            _AI_SOFTWARE_ENGINEERING_MODULE.status
        ),
        integration_type=(
            _AI_SOFTWARE_ENGINEERING_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="software_requirements_architecture",
                title="🧭 Requisitos e arquitetura de software",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_requirements_analysis_traceability"
                        ),
                        title="📋 Requisitos e rastreabilidade",
                        description=(
                            "Análise, organização e relacionamento de "
                            "requisitos, regras, critérios de aceite, "
                            "fontes, dependências e decisões do produto."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "document_ai",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_architecture_design_assistance"
                        ),
                        title="🏗️ Assistência ao desenho de arquitetura",
                        description=(
                            "Apoio à definição de componentes, serviços, "
                            "interfaces, responsabilidades, padrões, "
                            "dependências e decisões arquiteturais."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_decision_intelligence",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_dependency_impact_analysis"
                        ),
                        title="🔗 Dependências e análise de impacto",
                        description=(
                            "Mapeamento de dependências entre módulos, APIs, "
                            "dados, bibliotecas, serviços, testes e equipes "
                            "para avaliar impactos de alterações."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "software_supply_chain_security",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_code_generation_modernization",
                title="⌨️ Código, refatoração e modernização",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_code_generation_assistance"
                        ),
                        title="🤖 Geração assistida de código",
                        description=(
                            "Produção controlada de funções, componentes, "
                            "integrações, modelos, configurações e exemplos "
                            "conforme padrões e contexto autorizados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "agent_process_orchestration",
                            "ai_model_agent_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_refactoring_modernization"
                        ),
                        title="♻️ Refatoração e modernização",
                        description=(
                            "Identificação e aplicação assistida de melhorias "
                            "de estrutura, legibilidade, reutilização, "
                            "manutenibilidade e atualização tecnológica."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "enterprise_rag",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_code_review_assistance"
                        ),
                        title="🔎 Revisão assistida de código",
                        description=(
                            "Análise de alterações para localizar defeitos, "
                            "riscos, inconsistências, duplicações, problemas "
                            "de manutenção e violações de padrões."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "software_supply_chain_security",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_repository_developer_intelligence",
                title="🧠 Repositórios e experiência do desenvolvedor",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_repository_semantic_search"
                        ),
                        title="🔍 Busca semântica em repositórios",
                        description=(
                            "Localização de código, documentação, commits, "
                            "testes, configurações, decisões e relações "
                            "relevantes para uma tarefa de engenharia."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_contextual_developer_assistant"
                        ),
                        title="💬 Assistente contextual ao desenvolvedor",
                        description=(
                            "Apoio a dúvidas técnicas, entendimento do código, "
                            "planejamento de alterações e identificação "
                            "de arquivos e testes relacionados."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "digital_experiences_intelligent_interfaces",
                            "agent_process_orchestration",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_documentation_generation"
                        ),
                        title="📄 Documentação técnica assistida",
                        description=(
                            "Geração e atualização de documentação de APIs, "
                            "componentes, fluxos, configurações, arquitetura "
                            "e procedimentos com fontes rastreáveis."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "enterprise_rag",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_testing_security_quality",
                title="✅ Testes, segurança e qualidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_test_generation_prioritization"
                        ),
                        title="🧪 Geração e priorização de testes",
                        description=(
                            "Criação assistida de cenários unitários, "
                            "integração e regressão conforme mudanças, "
                            "riscos, contratos e comportamento esperado."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "enterprise_decision_intelligence",
                            "agent_process_orchestration",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_secure_code_analysis"
                        ),
                        title="🔐 Análise de código seguro",
                        description=(
                            "Identificação de vulnerabilidades, exposições, "
                            "segredos, permissões excessivas, dependências "
                            "inseguras e padrões de risco."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "cybersecurity_fraud_prevention",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_quality_gate_automation"
                        ),
                        title="🚦 Automação de critérios de qualidade",
                        description=(
                            "Aplicação de verificações de testes, cobertura, "
                            "estilo, segurança, documentação, desempenho "
                            "e aprovação antes da integração."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "business_automation",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_delivery_release_automation",
                title="🚀 Entrega, infraestrutura e releases",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_ci_cd_pipeline_assistance"
                        ),
                        title="🔄 Assistência a pipelines CI/CD",
                        description=(
                            "Criação, análise e evolução de pipelines para "
                            "compilação, testes, segurança, empacotamento, "
                            "implantação e validação automatizada."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "software_supply_chain_security",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_release_change_management"
                        ),
                        title="📦 Releases e gestão de mudanças",
                        description=(
                            "Planejamento de versões, alterações, aprovações, "
                            "notas, implantação gradual, rollback "
                            "e comunicação entre equipes."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "data_traceability_provenance",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_environment_infrastructure_automation"
                        ),
                        title="☁️ Ambientes e infraestrutura automatizada",
                        description=(
                            "Apoio à definição e validação de ambientes, "
                            "configurações, recursos, dependências, custos "
                            "e controles para execução das aplicações."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_observability_reliability",
                title="📊 Observabilidade e confiabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_incident_debugging_assistance"
                        ),
                        title="🩺 Diagnóstico assistido de incidentes",
                        description=(
                            "Correlação de logs, métricas, traces, eventos, "
                            "alterações e dependências para apoiar "
                            "a investigação e resolução de problemas."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_performance_analysis"
                        ),
                        title="⚡ Análise de desempenho",
                        description=(
                            "Identificação de gargalos, latência, consumo, "
                            "operações lentas, contenção e oportunidades "
                            "de otimização em código e infraestrutura."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_reliability_risk_prediction"
                        ),
                        title="📉 Riscos e confiabilidade de mudanças",
                        description=(
                            "Estimativa de risco de falha, regressão ou "
                            "incidente com base em alterações, cobertura, "
                            "complexidade, histórico e dependências."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "enterprise_decision_intelligence",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="software_governance_productivity_lifecycle",
                title="🛡️ Governança e produtividade da engenharia",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "software_policy_architecture_governance"
                        ),
                        title="⚖️ Políticas e governança de arquitetura",
                        description=(
                            "Verificação de padrões, tecnologias permitidas, "
                            "controles, exceções, responsabilidades, "
                            "documentação e decisões arquiteturais."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "responsible_ai_ethics_risk",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_engineering_productivity_analytics"
                        ),
                        title="📈 Indicadores de produtividade técnica",
                        description=(
                            "Acompanhamento de fluxo, tempo de entrega, "
                            "qualidade, retrabalho, falhas, automação "
                            "e capacidade das práticas de engenharia."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_platform_governance",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "software_ai_audit_observability"
                        ),
                        title="🧾 Auditoria da IA na engenharia",
                        description=(
                            "Registro de prompts, contexto, fontes, modelos, "
                            "alterações sugeridas, aprovações, resultados, "
                            "custos, acessos e evidências."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "ai_model_agent_security",
                            "ai_operations",
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

    module_id = "ai_software_engineering"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        41: (287, 861),
        42: (294, 882),
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

    print("AI_SOFTWARE_ENGINEERING_PREREQUISITES=OK")


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
    """Adiciona Engenharia de Software com IA."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "AI_SOFTWARE_ENGINEERING_SOLUTION =" in source:
        print("AI_SOFTWARE_ENGINEERING_ALREADY_PRESENT=OK")
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
        AI_SOFTWARE_ENGINEERING_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    ASSET_MANAGEMENT_SMART_MAINTENANCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    AI_SOFTWARE_ENGINEERING_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("AI_SOFTWARE_ENGINEERING_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_ai_software_engineering_is_complete" in source:
        print("AI_SOFTWARE_ENGINEERING_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "AI_SOFTWARE_ENGINEERING_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 41
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 42
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quarenta e uma soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_ai_software_engineering_is_complete():
    assert (
        AI_SOFTWARE_ENGINEERING_SOLUTION.solution_id
        == "ai_software_engineering"
    )

    assert len(
        AI_SOFTWARE_ENGINEERING_SOLUTION.areas
    ) == 7

    assert (
        AI_SOFTWARE_ENGINEERING_SOLUTION.capability_count
        == 21
    )


def test_ai_software_engineering_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "ai_software_engineering"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        AI_SOFTWARE_ENGINEERING_SOLUTION.status
        is module.status
    )

    assert (
        AI_SOFTWARE_ENGINEERING_SOLUTION.integration_type
        == module.integration_type
    )


def test_ai_software_engineering_lookup():
    assert (
        platform_technology_solution(
            "ai_software_engineering"
        )
        is AI_SOFTWARE_ENGINEERING_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("AI_SOFTWARE_ENGINEERING_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    software_solution = module.AI_SOFTWARE_ENGINEERING_SOLUTION

    assert len(solutions) == 42
    assert len(software_solution.areas) == 7
    assert software_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 294
    assert total_capabilities == 882

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=42")
    print("TOTAL_TECHNOLOGY_AREAS=294")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=882")
    print("AI_SOFTWARE_ENGINEERING_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
