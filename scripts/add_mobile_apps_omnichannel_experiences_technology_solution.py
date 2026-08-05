"""Adiciona Aplicativos Móveis e Experiências Omnicanal."""

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
        "mobile_apps_omnichannel_experiences_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


MOBILE_APPS_OMNICHANNEL_EXPERIENCES_DEFINITION = """
_MOBILE_APPS_OMNICHANNEL_EXPERIENCES_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "mobile_apps_omnichannel_experiences"
    ]
)


MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION = (
    PlatformTechnologySolution(
        solution_id=(
            "mobile_apps_omnichannel_experiences"
        ),
        icon="📱",
        title=(
            "Aplicativos Móveis e Experiências Omnicanal"
        ),
        description=(
            "Arquitetura tecnológica para aplicativos móveis, "
            "experiências responsivas, funcionamento offline, "
            "sincronização, continuidade entre canais, integração "
            "com recursos dos dispositivos, notificações, "
            "identidade, privacidade, segurança, acessibilidade, "
            "qualidade, distribuição, observabilidade, métricas "
            "e governança do ciclo de vida dos aplicativos."
        ),
        status=(
            _MOBILE_APPS_OMNICHANNEL_EXPERIENCES_MODULE
            .status
        ),
        integration_type=(
            _MOBILE_APPS_OMNICHANNEL_EXPERIENCES_MODULE
            .integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="mobile_platform_architecture_foundation",
                title="🏗️ Plataforma e arquitetura móvel",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_application_architecture"
                        ),
                        title="📐 Arquitetura de aplicativos móveis",
                        description=(
                            "Definição de camadas, componentes, estado, "
                            "navegação, integrações, armazenamento, "
                            "responsabilidades e padrões de desenvolvimento."
                        ),
                        technology_dependencies=(
                            "ai_software_engineering",
                            "digital_experiences_intelligent_interfaces",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_design_system_components"
                        ),
                        title="🎨 Componentes e design system móvel",
                        description=(
                            "Organização de componentes reutilizáveis, "
                            "tokens, temas, tipografia, navegação, padrões "
                            "visuais e comportamentos de interface."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "software_testing_quality_reliability",
                            "ai_software_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_remote_configuration_features"
                        ),
                        title="⚙️ Configuração e funcionalidades remotas",
                        description=(
                            "Controle versionado de configurações, "
                            "parâmetros, funcionalidades graduais, "
                            "experimentos e comportamentos do aplicativo."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "business_automation",
                            "data_traceability_provenance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_offline_data_synchronization",
                title="🔄 Dados, operação offline e sincronização",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_offline_first_experience"
                        ),
                        title="📴 Experiência offline-first",
                        description=(
                            "Disponibilização de conteúdos e operações "
                            "essenciais durante indisponibilidade ou "
                            "instabilidade da conectividade."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "data_platform_governance",
                            "digital_experiences_intelligent_interfaces",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_data_sync_conflict_resolution"
                        ),
                        title="🔁 Sincronização e resolução de conflitos",
                        description=(
                            "Sincronização de alterações locais e remotas "
                            "com versionamento, retentativas, idempotência, "
                            "prioridades e tratamento de conflitos."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_traceability_provenance",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_secure_local_storage"
                        ),
                        title="🗃️ Armazenamento local controlado",
                        description=(
                            "Persistência de preferências, dados temporários, "
                            "sessões e conteúdos necessários com proteção, "
                            "expiração e limpeza controlada."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "privacy_data_protection_lgpd",
                            "zero_trust_identity_access",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_omnichannel_journey_continuity",
                title="🌐 Jornadas e continuidade omnicanal",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_cross_channel_session_continuity"
                        ),
                        title="🔄 Continuidade de sessão entre canais",
                        description=(
                            "Preservação autorizada de contexto, progresso, "
                            "preferências e etapas ao alternar entre "
                            "aplicativo, web, atendimento e outros canais."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "data_platform_governance",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_human_digital_handoff"
                        ),
                        title="👥 Transferência entre digital e humano",
                        description=(
                            "Encaminhamento de solicitações com contexto, "
                            "histórico, documentos e motivo para equipes "
                            "ou canais de atendimento autorizados."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "ai_collaboration_meetings_productivity",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_unified_notifications_messaging"
                        ),
                        title="🔔 Notificações e mensagens unificadas",
                        description=(
                            "Coordenação de notificações push, mensagens, "
                            "alertas internos e atualizações conforme "
                            "preferências, prioridade e contexto."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "api_integrations_connectors",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_device_context_capabilities",
                title="📡 Recursos e contexto dos dispositivos",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_location_sensor_context"
                        ),
                        title="📍 Localização e sensores móveis",
                        description=(
                            "Uso autorizado de localização, movimento, "
                            "orientação, proximidade e demais sensores "
                            "para experiências contextuais."
                        ),
                        technology_dependencies=(
                            "navigation_positioning_geolocation",
                            "iot_edge_intelligence",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_camera_document_capture"
                        ),
                        title="📷 Câmera e captura de documentos",
                        description=(
                            "Captura assistida de imagens, documentos, "
                            "códigos e evidências com validação de qualidade "
                            "e processamento autorizado."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "document_ai",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_background_device_events"
                        ),
                        title="⚡ Eventos e tarefas em segundo plano",
                        description=(
                            "Execução controlada de sincronizações, alertas, "
                            "atualizações e tarefas periódicas conforme "
                            "limites do sistema e energia disponível."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "energy_smart_grids",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_identity_security_privacy",
                title="🔐 Identidade, segurança e privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_authentication_session_access"
                        ),
                        title="🪪 Autenticação e controle de sessão",
                        description=(
                            "Autenticação, renovação de sessão, revogação, "
                            "controle de dispositivos, papéis, permissões "
                            "e acesso às funções do aplicativo."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cybersecurity_fraud_prevention",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_application_data_protection"
                        ),
                        title="🛡️ Proteção dos dados do aplicativo",
                        description=(
                            "Proteção de dados em armazenamento, trânsito, "
                            "logs, memória, cache, backups, integrações "
                            "e comunicações com serviços externos."
                        ),
                        technology_dependencies=(
                            "cryptography_confidential_computing",
                            "privacy_enhancing_technologies",
                            "software_supply_chain_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_consent_permissions_privacy"
                        ),
                        title="🕶️ Consentimento e permissões",
                        description=(
                            "Gestão transparente de consentimentos, "
                            "permissões do dispositivo, finalidade, "
                            "retenção, minimização e exclusão dos dados."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "technology_governance_policy_compliance",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_quality_delivery_observability",
                title="🧪 Qualidade, distribuição e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_compatibility_automated_testing"
                        ),
                        title="🧪 Testes móveis e compatibilidade",
                        description=(
                            "Validação de dispositivos, versões, telas, "
                            "sistemas operacionais, conectividade, "
                            "permissões e comportamentos da interface."
                        ),
                        technology_dependencies=(
                            "software_testing_quality_reliability",
                            "ai_software_engineering",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_release_rollout_distribution"
                        ),
                        title="🚀 Releases e distribuição gradual",
                        description=(
                            "Planejamento de versões, assinatura, publicação, "
                            "implantação progressiva, compatibilidade, "
                            "rollback e comunicação das atualizações."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "cloud_devops_finops",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_crash_performance_observability"
                        ),
                        title="📊 Falhas, desempenho e observabilidade",
                        description=(
                            "Monitoramento de falhas, travamentos, latência, "
                            "consumo de memória, rede, bateria, inicialização "
                            "e estabilidade das versões."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "software_testing_quality_reliability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="mobile_accessibility_engagement_governance",
                title="♿ Acessibilidade, engajamento e governança",
                capabilities=(
                    TechnologyCapability(
                        capability_id=(
                            "mobile_accessibility_localization"
                        ),
                        title="♿ Acessibilidade e localização",
                        description=(
                            "Suporte a leitores de tela, contraste, "
                            "navegação alternativa, tamanhos adaptáveis, "
                            "idiomas e formatos regionais."
                        ),
                        technology_dependencies=(
                            "digital_experiences_intelligent_interfaces",
                            "voice_audio_speech_ai",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_engagement_experience_analytics"
                        ),
                        title="📈 Engajamento e experiência móvel",
                        description=(
                            "Análise responsável de jornadas, retenção, "
                            "abandono, uso de funções, desempenho, feedback "
                            "e dificuldades encontradas pelos usuários."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "privacy_enhancing_technologies",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "mobile_governance_audit_lifecycle"
                        ),
                        title="🧾 Governança e auditoria do aplicativo",
                        description=(
                            "Registro de versões, configurações, permissões, "
                            "consentimentos, integrações, falhas, custos, "
                            "acessos, alterações e resultados."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
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

    module_id = "mobile_apps_omnichannel_experiences"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        45: (315, 945),
        46: (322, 966),
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

    print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_PREREQUISITES=OK")


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
    """Adiciona Aplicativos Móveis e Experiências Omnicanal."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION =" in source:
        print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_ALREADY_PRESENT=OK")
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
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    SOFTWARE_TESTING_QUALITY_RELIABILITY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    test_name = "def test_mobile_apps_omnichannel_experiences_is_complete"

    if test_name in source:
        print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 45
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 46
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quarenta e cinco soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_mobile_apps_omnichannel_experiences_is_complete():
    assert (
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION.solution_id
        == "mobile_apps_omnichannel_experiences"
    )

    assert len(
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION.areas
    ) == 7

    assert (
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION
        .capability_count
        == 21
    )


def test_mobile_apps_omnichannel_experiences_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "mobile_apps_omnichannel_experiences"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION.status
        is module.status
    )

    assert (
        MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION
        .integration_type
        == module.integration_type
    )


def test_mobile_apps_omnichannel_experiences_lookup():
    assert (
        platform_technology_solution(
            "mobile_apps_omnichannel_experiences"
        )
        is MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_TESTS_CREATED=OK")


def validate_result() -> None:
    """Recarrega o módulo e valida os totais."""

    importlib.invalidate_caches()

    module = importlib.reload(
        importlib.import_module("src.platform_technology_solutions")
    )

    solutions = module.PLATFORM_TECHNOLOGY_SOLUTIONS

    mobile_solution = module.MOBILE_APPS_OMNICHANNEL_EXPERIENCES_SOLUTION

    assert len(solutions) == 46
    assert len(mobile_solution.areas) == 7

    assert mobile_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 322
    assert total_capabilities == 966

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=46")
    print("TOTAL_TECHNOLOGY_AREAS=322")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=966")
    print("MOBILE_APPS_OMNICHANNEL_EXPERIENCES_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
