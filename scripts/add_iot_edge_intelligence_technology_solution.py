"""Adiciona IoT e Inteligência em Edge ao registro tecnológico."""

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
    / ("iot_edge_intelligence_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


IOT_EDGE_INTELLIGENCE_DEFINITION = """
_IOT_EDGE_INTELLIGENCE_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "iot_edge_intelligence"
    ]
)


IOT_EDGE_INTELLIGENCE_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="iot_edge_intelligence",
        icon="🌐",
        title="IoT e Inteligência em Edge",
        description=(
            "Arquitetura tecnológica para dispositivos conectados, "
            "sensores, gateways, telemetria, processamento local, "
            "execução de modelos de IA, automações em tempo real, "
            "operação com conectividade limitada, segurança, "
            "governança, observabilidade e gestão de frotas."
        ),
        status=(
            _IOT_EDGE_INTELLIGENCE_MODULE.status
        ),
        integration_type=(
            _IOT_EDGE_INTELLIGENCE_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="iot_edge_devices_lifecycle",
                title="📟 Dispositivos e ciclo de vida",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_device_registry",
                        title="🗂️ Registro de dispositivos e ativos",
                        description=(
                            "Cadastro de sensores, gateways, máquinas, "
                            "controladores, versões, responsáveis, "
                            "localização e relações com outros ativos."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "digital_twins_simulation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_device_provisioning",
                        title="🔐 Provisionamento e ativação segura",
                        description=(
                            "Registro, autenticação, configuração inicial "
                            "e autorização de novos dispositivos "
                            "antes de entrarem em operação."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "api_integrations_connectors",
                            "business_automation",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id=(
                            "iot_edge_firmware_configuration_lifecycle"
                        ),
                        title="🔄 Firmware e configurações",
                        description=(
                            "Versionamento, distribuição, atualização, "
                            "validação e reversão de firmware "
                            "e configurações dos equipamentos."
                        ),
                        technology_dependencies=(
                            "software_supply_chain_security",
                            "cloud_devops_finops",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_connectivity_telemetry",
                title="📡 Conectividade e telemetria",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_protocol_gateways",
                        title="🔌 Protocolos e gateways",
                        description=(
                            "Integração de protocolos, redes, gateways, "
                            "adaptadores e interfaces de comunicação "
                            "entre dispositivos e serviços."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "real_time_event_intelligence",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_telemetry_ingestion",
                        title="📨 Ingestão de telemetria",
                        description=(
                            "Recebimento contínuo de medições, estados, "
                            "eventos, comandos, erros e informações "
                            "operacionais dos equipamentos."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "data_platform_governance",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_store_forward_sync",
                        title="📴 Store-and-forward e sincronização",
                        description=(
                            "Armazenamento temporário no edge e envio "
                            "posterior dos eventos quando a conectividade "
                            "estiver novamente disponível."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "data_traceability_provenance",
                            "cloud_devops_finops",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_runtime_orchestration",
                title="⚙️ Runtime e orquestração no edge",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_runtime_management",
                        title="📦 Gestão do runtime em edge",
                        description=(
                            "Execução e gerenciamento de serviços, "
                            "containers, agentes e aplicações próximas "
                            "à origem dos dados."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "agent_process_orchestration",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_workload_scheduling",
                        title="🧭 Distribuição de workloads",
                        description=(
                            "Distribuição de tarefas conforme capacidade, "
                            "latência, prioridade, localização, energia "
                            "e disponibilidade dos dispositivos."
                        ),
                        technology_dependencies=(
                            "enterprise_decision_intelligence",
                            "cloud_devops_finops",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_resource_isolation",
                        title="🛡️ Isolamento e limites de recursos",
                        description=(
                            "Separação de processos e limitação de CPU, "
                            "memória, armazenamento, rede, dispositivos "
                            "e permissões disponíveis."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "ai_model_agent_security",
                            "software_supply_chain_security",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_ai_inference",
                title="🤖 IA e inferência no edge",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_model_deployment",
                        title="📦 Distribuição de modelos de IA",
                        description=(
                            "Versionamento, validação e implantação "
                            "controlada de modelos nos dispositivos "
                            "e gateways autorizados."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "software_supply_chain_security",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_local_inference",
                        title="🧠 Inferência local multimodal",
                        description=(
                            "Execução local de modelos para imagens, "
                            "vídeos, áudio, sensores, eventos "
                            "e outras entradas multimodais."
                        ),
                        technology_dependencies=(
                            "computer_vision_video_analytics",
                            "voice_audio_speech_ai",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_model_quality_monitoring",
                        title="📊 Qualidade e desempenho dos modelos",
                        description=(
                            "Monitoramento de acurácia, confiança, "
                            "latência, falhas, distribuição das entradas "
                            "e degradação dos modelos implantados."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "ai_operations",
                            "tools_analytics",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_events_automation",
                title="⚡ Eventos e automação local",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_complex_event_processing",
                        title="🔎 Processamento de eventos no edge",
                        description=(
                            "Correlação local de sinais, sequências, "
                            "limites, estados e padrões para identificar "
                            "situações relevantes."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "enterprise_decision_intelligence",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_local_automation",
                        title="⚙️ Ações e automações locais",
                        description=(
                            "Execução de regras, workflows, comandos "
                            "e integrações locais com baixa latência "
                            "e limites previamente autorizados."
                        ),
                        technology_dependencies=(
                            "business_automation",
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_human_escalation",
                        title="👤 Escalonamento para operadores",
                        description=(
                            "Encaminhamento de falhas, riscos, exceções "
                            "e decisões incertas para operadores "
                            "com acesso autorizado."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "tools_analytics",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_security_privacy_resilience",
                title="🔐 Segurança, privacidade e resiliência",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_identity_attestation",
                        title="🪪 Identidade e atestação dos dispositivos",
                        description=(
                            "Verificação da identidade, integridade, "
                            "firmware, configuração e estado de segurança "
                            "antes da liberação de acessos."
                        ),
                        technology_dependencies=(
                            "zero_trust_identity_access",
                            "cryptography_confidential_computing",
                            "software_supply_chain_security",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_data_privacy_protection",
                        title="🕶️ Proteção dos dados no edge",
                        description=(
                            "Criptografia, minimização, mascaramento, "
                            "retenção controlada e proteção de dados "
                            "sensíveis coletados pelos dispositivos."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "cryptography_confidential_computing",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_resilience_recovery",
                        title="♻️ Resiliência e recuperação",
                        description=(
                            "Continuidade local, reinicialização segura, "
                            "recuperação de configurações e sincronização "
                            "após falhas ou indisponibilidade."
                        ),
                        technology_dependencies=(
                            "operational_security_resilience",
                            "cloud_devops_finops",
                            "real_time_event_intelligence",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="iot_edge_operations_governance",
                title="📊 Operações, governança e observabilidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="iot_edge_fleet_observability",
                        title="📊 Observabilidade da frota",
                        description=(
                            "Monitoramento de disponibilidade, saúde, "
                            "latência, erros, eventos, versões, "
                            "conectividade e utilização dos dispositivos."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "tools_analytics",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_capacity_energy_finops",
                        title="🔋 Capacidade, energia e FinOps",
                        description=(
                            "Acompanhamento e otimização de processamento, "
                            "memória, armazenamento, conectividade, energia "
                            "e custos da infraestrutura distribuída."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "enterprise_decision_intelligence",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="iot_edge_governance_audit",
                        title="🧾 Governança e auditoria",
                        description=(
                            "Registro de acessos, comandos, atualizações, "
                            "configurações, decisões, eventos, responsáveis "
                            "e evidências operacionais."
                        ),
                        technology_dependencies=(
                            "technology_governance_policy_compliance",
                            "data_traceability_provenance",
                            "software_testing_quality_reliability",
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

    module_id = "iot_edge_intelligence"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    current_count = len(PLATFORM_TECHNOLOGY_SOLUTIONS)

    expected_totals = {
        23: (161, 483),
        24: (168, 504),
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

    print("IOT_EDGE_INTELLIGENCE_PREREQUISITES=OK")


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
    """Adiciona IoT e Inteligência em Edge."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "IOT_EDGE_INTELLIGENCE_SOLUTION =" in source:
        print("IOT_EDGE_INTELLIGENCE_ALREADY_PRESENT=OK")
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
        IOT_EDGE_INTELLIGENCE_DEFINITION + registry_anchor,
        1,
    )

    final_item = "    SPATIAL_COMPUTING_AUGMENTED_REALITY_SOLUTION,\n"

    if final_item not in source:
        raise RuntimeError("Última solução tecnológica atual não encontrada.")

    source = source.replace(
        final_item,
        (final_item + "    IOT_EDGE_INTELLIGENCE_SOLUTION,\n"),
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("IOT_EDGE_INTELLIGENCE_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_iot_edge_intelligence_is_complete" in source:
        print("IOT_EDGE_INTELLIGENCE_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "IOT_EDGE_INTELLIGENCE_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 23
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 24
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de vinte e três soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_iot_edge_intelligence_is_complete():
    assert (
        IOT_EDGE_INTELLIGENCE_SOLUTION.solution_id
        == "iot_edge_intelligence"
    )

    assert len(
        IOT_EDGE_INTELLIGENCE_SOLUTION.areas
    ) == 7

    assert (
        IOT_EDGE_INTELLIGENCE_SOLUTION.capability_count
        == 21
    )


def test_iot_edge_intelligence_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "iot_edge_intelligence"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        IOT_EDGE_INTELLIGENCE_SOLUTION.status
        is module.status
    )

    assert (
        IOT_EDGE_INTELLIGENCE_SOLUTION.integration_type
        == module.integration_type
    )


def test_iot_edge_intelligence_lookup():
    assert (
        platform_technology_solution(
            "iot_edge_intelligence"
        )
        is IOT_EDGE_INTELLIGENCE_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("IOT_EDGE_INTELLIGENCE_TESTS_CREATED=OK")


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

    iot_solution = getattr(
        module,
        "IOT_EDGE_INTELLIGENCE_SOLUTION",
    )

    assert len(solutions) == 24
    assert len(iot_solution.areas) == 7
    assert iot_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 168
    assert total_capabilities == 504

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=24")
    print("TOTAL_TECHNOLOGY_AREAS=168")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=504")
    print("IOT_EDGE_INTELLIGENCE_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
