"""Adiciona APIs, Integrações e Conectores ao registro tecnológico."""

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
        "api_integrations_connectors_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


API_INTEGRATIONS_CONNECTORS_DEFINITION = """
_API_INTEGRATIONS_CONNECTORS_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "api_integrations_connectors"
    ]
)


API_INTEGRATIONS_CONNECTORS_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="api_integrations_connectors",
        icon="🔌",
        title="APIs, Integrações e Conectores",
        description=(
            "Arquitetura tecnológica para contratos de APIs, "
            "conectores empresariais, autenticação, segurança, "
            "eventos, webhooks, transformação de dados, resiliência, "
            "observabilidade, governança e ciclo de vida das integrações."
        ),
        status=(
            _API_INTEGRATIONS_CONNECTORS_MODULE.status
        ),
        integration_type=(
            _API_INTEGRATIONS_CONNECTORS_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="api_design_contracts",
                title="📋 Design e contratos de APIs",
                capabilities=(
                    TechnologyCapability(
                        capability_id="api_rest_contracts",
                        title="🌐 APIs REST e contratos de recursos",
                        description=(
                            "Definição de endpoints, recursos, métodos, "
                            "parâmetros, respostas e códigos de estado."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "technology_governance_policy_compliance",
                            "ai_software_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="api_schema_validation",
                        title="✅ Esquemas e validação de dados",
                        description=(
                            "Validação de tipos, campos obrigatórios, "
                            "formatos, restrições e compatibilidade."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "software_testing_quality_reliability",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="api_versioning_compatibility",
                        title="🗃️ Versionamento e compatibilidade",
                        description=(
                            "Gestão de versões, mudanças incompatíveis, "
                            "depreciação e períodos de migração."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "cloud_devops_finops",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_connectors_adapters",
                title="🔌 Conectores e adaptadores",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_database_connectors",
                        title="🗄️ Conectores de bancos de dados",
                        description=(
                            "Integração controlada com bancos relacionais, "
                            "analíticos, vetoriais e outros armazenamentos."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_business_system_adapters",
                        title="🏢 Adaptadores de sistemas empresariais",
                        description=(
                            "Conexão com CRM, ERP, atendimento, documentos, "
                            "operações, pagamentos e sistemas autorizados."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_external_service_connectors",
                        title="☁️ Conectores de serviços externos",
                        description=(
                            "Integração com provedores de nuvem, modelos, "
                            "mensageria, arquivos e serviços especializados."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "operational_security_resilience",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_authentication_security",
                title="🔐 Autenticação e segurança",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_oauth_tokens_keys",
                        title="🔑 OAuth, tokens e chaves de API",
                        description=(
                            "Gestão de credenciais, tokens, chaves, "
                            "renovação, expiração e escopos de acesso."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "operational_security_resilience",
                            "privacy_enhancing_technologies",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_service_identity",
                        title="🪪 Identidade entre serviços",
                        description=(
                            "Autenticação e autorização de aplicações, "
                            "workers, agentes, serviços e integrações internas."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "technology_governance_policy_compliance",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_payload_protection",
                        title="🛡️ Proteção de requisições e dados",
                        description=(
                            "Assinatura, criptografia, validação, proteção "
                            "contra repetição e redução de exposição."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_events_orchestration",
                title="⚡ Eventos e orquestração",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_webhooks_callbacks",
                        title="🔔 Webhooks e callbacks",
                        description=(
                            "Recebimento e envio de notificações assíncronas "
                            "com autenticação, validação e rastreabilidade."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "zero_trust_identity_access",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_queues_events_streams",
                        title="📨 Filas, eventos e streams",
                        description=(
                            "Troca assíncrona de mensagens, processamento "
                            "orientado a eventos e desacoplamento de serviços."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_workflow_orchestration",
                        title="🧩 Orquestração de integrações",
                        description=(
                            "Coordenação de chamadas, condições, dependências, "
                            "etapas, compensações e processos distribuídos."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_transformation_routing",
                title="🔄 Transformação e roteamento",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_data_mapping",
                        title="🔄 Mapeamento e transformação de dados",
                        description=(
                            "Conversão de estruturas, campos, formatos, "
                            "valores e representações entre sistemas."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "knowledge_graph_semantic_ai",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_content_routing",
                        title="🧭 Roteamento por conteúdo e regras",
                        description=(
                            "Direcionamento de mensagens e solicitações "
                            "conforme origem, conteúdo, prioridade e contexto."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "agent_process_orchestration",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_batch_file_exchange",
                        title="📁 Arquivos e integrações em lote",
                        description=(
                            "Troca controlada de arquivos, importações, "
                            "exportações e processamentos programados."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "business_automation",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_reliability_resilience",
                title="🔄 Confiabilidade e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_timeouts_retries",
                        title="⏱️ Timeouts e retries controlados",
                        description=(
                            "Controle de tempo limite, novas tentativas, "
                            "espera progressiva e limites operacionais."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "software_testing_quality_reliability",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_circuit_breaker_fallback",
                        title="🛑 Circuit breaker e fallback",
                        description=(
                            "Interrupção temporária de chamadas problemáticas "
                            "e uso de alternativas seguras."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_idempotency_deduplication",
                        title="♻️ Idempotência e deduplicação",
                        description=(
                            "Prevenção de operações duplicadas e tratamento "
                            "seguro de mensagens ou requisições repetidas."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "software_testing_quality_reliability",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="integration_governance_observability",
                title="📊 Governança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="integration_logs_metrics_tracing",
                        title="📊 Logs, métricas e tracing",
                        description=(
                            "Acompanhamento de chamadas, respostas, latência, "
                            "erros, dependências e identificadores de correlação."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_catalog_documentation",
                        title="📚 Catálogo e documentação",
                        description=(
                            "Registro de APIs, conectores, contratos, "
                            "responsáveis, versões e condições de utilização."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "enterprise_rag",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="integration_testing_lifecycle",
                        title="🧪 Testes e ciclo de vida",
                        description=(
                            "Testes de contrato, integração, carga, segurança, "
                            "compatibilidade, implantação e desativação."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "cloud_devops_finops",
                            "ai_evaluation_benchmarks_red_team",
                        ),
                    ),
                ),
            ),
        ),
    )
)


"""


def validate_prerequisites() -> None:
    """Valida o estado atual do registro tecnológico."""

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

    module_id = "api_integrations_connectors"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_solution_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    total_areas = sum(len(solution.areas) for solution in PLATFORM_TECHNOLOGY_SOLUTIONS)

    total_capabilities = sum(
        solution.capability_count for solution in PLATFORM_TECHNOLOGY_SOLUTIONS
    )

    expected_totals = {
        8: (56, 168),
        9: (63, 189),
    }

    if current_solution_count not in expected_totals:
        raise RuntimeError(
            f"Quantidade tecnológica inesperada: {current_solution_count}"
        )

    expected_areas, expected_capabilities = expected_totals[current_solution_count]

    if total_areas != expected_areas:
        raise RuntimeError(f"Total atual de áreas inesperado: {total_areas}")

    if total_capabilities != expected_capabilities:
        raise RuntimeError(
            f"Total atual de capacidades inesperado: {total_capabilities}"
        )

    print("API_INTEGRATIONS_CONNECTORS_PREREQUISITES=OK")


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

    if "API_INTEGRATIONS_CONNECTORS_SOLUTION =" in source:
        print("API_INTEGRATIONS_CONNECTORS_ALREADY_PRESENT=OK")
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
        API_INTEGRATIONS_CONNECTORS_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    DATA_PLATFORM_GOVERNANCE_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError(
            "Última solução tecnológica atual não encontrada no registro."
        )

    source = source.replace(
        final_item,
        (final_item + "    API_INTEGRATIONS_CONNECTORS_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("API_INTEGRATIONS_CONNECTORS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_api_integrations_connectors_is_complete"

    if test_name in source:
        print("API_INTEGRATIONS_CONNECTORS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "API_INTEGRATIONS_CONNECTORS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 8
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 9
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de oito soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_api_integrations_connectors_is_complete():
    assert (
        API_INTEGRATIONS_CONNECTORS_SOLUTION.solution_id
        == "api_integrations_connectors"
    )

    assert len(
        API_INTEGRATIONS_CONNECTORS_SOLUTION.areas
    ) == 7

    assert (
        API_INTEGRATIONS_CONNECTORS_SOLUTION.capability_count
        == 21
    )


def test_api_integrations_connectors_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "api_integrations_connectors"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        API_INTEGRATIONS_CONNECTORS_SOLUTION.status
        is module.status
    )

    assert (
        API_INTEGRATIONS_CONNECTORS_SOLUTION.integration_type
        == module.integration_type
    )


def test_api_integrations_connectors_lookup():
    assert (
        platform_technology_solution(
            "api_integrations_connectors"
        )
        is API_INTEGRATIONS_CONNECTORS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("API_INTEGRATIONS_CONNECTORS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Importa novamente e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    integration_solution = getattr(
        module,
        "API_INTEGRATIONS_CONNECTORS_SOLUTION",
    )

    assert len(solutions) == 9
    assert len(integration_solution.areas) == 7

    assert integration_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 63
    assert total_capabilities == 189

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=9")
    print("TOTAL_TECHNOLOGY_AREAS=63")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=189")
    print("API_INTEGRATIONS_CONNECTORS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
