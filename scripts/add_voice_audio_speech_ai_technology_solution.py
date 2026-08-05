"""Adiciona IA de Voz, Áudio e Fala ao registro tecnológico."""

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
    / ("voice_audio_speech_ai_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


VOICE_AUDIO_SPEECH_AI_DEFINITION = """
_VOICE_AUDIO_SPEECH_AI_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "voice_audio_speech_ai"
    ]
)


VOICE_AUDIO_SPEECH_AI_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="voice_audio_speech_ai",
        icon="🎙️",
        title="IA de Voz, Áudio e Fala",
        description=(
            "Arquitetura tecnológica para captura, preparação, "
            "transcrição, compreensão, síntese de fala, interação "
            "conversacional, análise acústica, pesquisa semântica, "
            "segurança, privacidade, avaliação e operação em tempo real."
        ),
        status=(
            _VOICE_AUDIO_SPEECH_AI_MODULE.status
        ),
        integration_type=(
            _VOICE_AUDIO_SPEECH_AI_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="voice_audio_inputs_preprocessing",
                title="📥 Captura e preparação de áudio",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_audio_ingestion_streaming",
                        title="📥 Ingestão e streaming de áudio",
                        description=(
                            "Recebimento de arquivos, microfones, chamadas, "
                            "transmissões e eventos sonoros por canais "
                            "e integrações autorizadas."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "real_time_event_intelligence",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_audio_normalization_denoising",
                        title="🧹 Normalização e redução de ruído",
                        description=(
                            "Padronização de volume, frequência, formato, "
                            "qualidade, canais e redução de interferências."
                        ),
                        technology_dependencies=(
                            "scientific_computing_engineering",
                            "multimodal_ai",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_audio_activity_segmentation",
                        title="✂️ Segmentação e atividade de voz",
                        description=(
                            "Detecção de fala, silêncio, intervalos, "
                            "mudanças de turno e segmentos relevantes."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "scientific_computing_engineering",
                            "ai_operations",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_speech_recognition_understanding",
                title="📝 Reconhecimento e compreensão da fala",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_speech_transcription",
                        title="📝 Transcrição automática de fala",
                        description=(
                            "Conversão de fala em texto com controle "
                            "de idioma, pontuação, tempo e confiança."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "ai_evaluation_benchmarks_red_team",
                            "data_traceability_provenance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_speaker_diarization",
                        title="👥 Diarização e turnos de participantes",
                        description=(
                            "Separação de participantes e organização "
                            "dos turnos de fala sem depender da identidade real."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "scientific_computing_engineering",
                            "privacy_data_protection_lgpd",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_language_intent_entities",
                        title="🧠 Idioma, intenção e entidades",
                        description=(
                            "Identificação de idioma, assunto, intenção, "
                            "entidades, comandos e contexto da fala."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "multimodal_ai",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_speech_synthesis_generation",
                title="🔊 Síntese e geração de fala",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_text_to_speech",
                        title="🔊 Conversão de texto em fala",
                        description=(
                            "Geração de áudio falado a partir de textos "
                            "e respostas produzidas pela plataforma."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "digital_experiences_intelligent_interfaces",
                            "mobile_apps_omnichannel_experiences",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_prosody_style_control",
                        title="🎚️ Ritmo, entonação e estilo",
                        description=(
                            "Controle de velocidade, pausas, entonação "
                            "e apresentação de vozes sintéticas autorizadas."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "responsible_ai_ethics_risk",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_pronunciation_lexicons",
                        title="🔤 Pronúncia e vocabulários especializados",
                        description=(
                            "Configuração de termos técnicos, nomes, siglas, "
                            "idiomas e regras específicas de pronúncia."
                        ),
                        technology_dependencies=(
                            "knowledge_graph_semantic_ai",
                            "enterprise_rag",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_conversational_orchestration",
                title="💬 Conversação e orquestração em tempo real",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_real_time_sessions",
                        title="⚡ Sessões de voz em tempo real",
                        description=(
                            "Coordenação de entrada, processamento, resposta "
                            "e reprodução com baixa latência."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "agent_process_orchestration",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_turn_taking_interruptions",
                        title="🔄 Turnos, pausas e interrupções",
                        description=(
                            "Gestão de início e encerramento de turnos, "
                            "interrupções, confirmações e retomadas."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "multimodal_ai",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_agent_tool_execution",
                        title="🧰 Agentes e ferramentas por voz",
                        description=(
                            "Encaminhamento controlado de solicitações faladas "
                            "para agentes, APIs, ferramentas e workflows."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "api_integrations_connectors",
                            "business_automation",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_audio_analytics_search",
                title="📊 Analytics e pesquisa em áudio",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_acoustic_event_detection",
                        title="🔔 Detecção de eventos acústicos",
                        description=(
                            "Identificação de sons, mudanças, ocorrências "
                            "e eventos relevantes em fluxos de áudio."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "multimodal_ai",
                            "iot_edge_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_conversation_analytics",
                        title="📊 Analytics de conversações",
                        description=(
                            "Análise de duração, turnos, assuntos, silêncio, "
                            "resolução, qualidade e indicadores de atendimento."
                        ),
                        technology_dependencies=(
                            "tools_analytics",
                            "data_bi_copilot",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_semantic_audio_search",
                        title="🔍 Pesquisa semântica em áudio",
                        description=(
                            "Busca de trechos falados, assuntos, eventos "
                            "e conteúdos usando transcrição e embeddings."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "data_platform_governance",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_evaluation_safety_privacy",
                title="🛡️ Avaliação, segurança e privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_quality_benchmarks",
                        title="🧪 Benchmarks e avaliação de qualidade",
                        description=(
                            "Medição de transcrição, compreensão, latência, "
                            "naturalidade, robustez e qualidade de áudio."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_sensitive_data_protection",
                        title="🔐 Proteção de dados sensíveis em áudio",
                        description=(
                            "Detecção, mascaramento e controle de dados "
                            "pessoais ou confidenciais presentes na fala."
                        ),
                        technology_dependencies=(
                            "privacy_data_protection_lgpd",
                            "privacy_enhancing_technologies",
                            "zero_trust_identity_access",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_adversarial_bias_safety",
                        title="🛡️ Robustez, vieses e segurança",
                        description=(
                            "Avaliação de ruídos, manipulações, sotaques, "
                            "variações linguísticas, ataques e diferenças "
                            "de desempenho."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "ai_evaluation_benchmarks_red_team",
                            "responsible_ai_ethics_risk",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="voice_deployment_operations",
                title="🚀 Implantação e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="voice_edge_low_latency_inference",
                        title="📡 Inferência em edge e baixa latência",
                        description=(
                            "Execução de processamento de voz em dispositivos "
                            "e ambientes com limitações de conexão e recursos."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "scientific_computing_engineering",
                            "cloud_devops_finops",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_serving_scalability",
                        title="☁️ Serving e escalabilidade",
                        description=(
                            "Disponibilização de serviços de voz com controle "
                            "de capacidade, concorrência, disponibilidade "
                            "e custos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "ai_operations",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="voice_observability_lifecycle",
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento de sessões, latência, erros, custos, "
                            "qualidade, versões, feedback e implantação."
                        ),
                        technology_dependencies=(
                            "ai_operations",
                            "data_traceability_provenance",
                            "technology_governance_policy_compliance",
                        ),
                    ),
                ),
            ),
        ),
    )
)


"""


def validate_prerequisites() -> None:
    """Valida o registro e o módulo principal."""

    if not REGISTRY_PATH.exists():
        raise RuntimeError("Registro tecnológico não encontrado.")

    if not TEST_PATH.exists():
        raise RuntimeError("Testes tecnológicos não encontrados.")

    from src.platform_modules import (
        PLATFORM_MODULE_BY_ID,
        PlatformModuleCategory,
    )

    module_id = "voice_audio_speech_ai"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("VOICE_AUDIO_SPEECH_AI_PREREQUISITES=OK")


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
    """Adiciona IA de Voz, Áudio e Fala."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "VOICE_AUDIO_SPEECH_AI_SOLUTION =" in source:
        print("VOICE_AUDIO_SPEECH_AI_ALREADY_PRESENT=OK")
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
        VOICE_AUDIO_SPEECH_AI_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    MULTIMODAL_AI_SOLUTION,
    COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION,
)"""

    new_registry = """    MULTIMODAL_AI_SOLUTION,
    COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION,
    VOICE_AUDIO_SPEECH_AI_SOLUTION,
)"""

    if old_registry not in source:
        raise RuntimeError("Final atual do registro tecnológico não encontrado.")

    source = source.replace(
        old_registry,
        new_registry,
        1,
    )

    REGISTRY_PATH.write_text(
        source,
        encoding="utf-8",
    )

    print("VOICE_AUDIO_SPEECH_AI_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_voice_audio_speech_ai_is_complete" in source:
        print("VOICE_AUDIO_SPEECH_AI_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "VOICE_AUDIO_SPEECH_AI_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 5
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 6
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de cinco soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_voice_audio_speech_ai_is_complete():
    assert (
        VOICE_AUDIO_SPEECH_AI_SOLUTION.solution_id
        == "voice_audio_speech_ai"
    )

    assert len(
        VOICE_AUDIO_SPEECH_AI_SOLUTION.areas
    ) == 7

    assert (
        VOICE_AUDIO_SPEECH_AI_SOLUTION.capability_count
        == 21
    )


def test_voice_audio_speech_ai_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "voice_audio_speech_ai"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        VOICE_AUDIO_SPEECH_AI_SOLUTION.status
        is module.status
    )

    assert (
        VOICE_AUDIO_SPEECH_AI_SOLUTION.integration_type
        == module.integration_type
    )


def test_voice_audio_speech_ai_lookup():
    assert (
        platform_technology_solution(
            "voice_audio_speech_ai"
        )
        is VOICE_AUDIO_SPEECH_AI_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("VOICE_AUDIO_SPEECH_AI_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    voice_solution = getattr(
        module,
        "VOICE_AUDIO_SPEECH_AI_SOLUTION",
    )

    assert len(solutions) == 6
    assert len(voice_solution.areas) == 7

    assert voice_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 42
    assert total_capabilities == 126

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=6")
    print("TOTAL_TECHNOLOGY_AREAS=42")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=126")
    print("VOICE_AUDIO_SPEECH_AI_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
