"""Adiciona IA Multimodal ao registro tecnológico especializado."""

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
    / ("multimodal_ai_technology_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


MULTIMODAL_AI_DEFINITION = """
_MULTIMODAL_AI_MODULE = (
    PLATFORM_MODULE_BY_ID["multimodal_ai"]
)


MULTIMODAL_AI_SOLUTION = PlatformTechnologySolution(
    solution_id="multimodal_ai",
    icon="🧠",
    title="IA Multimodal",
    description=(
        "Arquitetura tecnológica para entrada, preparação, "
        "compreensão, combinação, recuperação, raciocínio, "
        "geração, avaliação, segurança e operação de conteúdos "
        "em texto, imagem, áudio, vídeo e documentos."
    ),
    status=_MULTIMODAL_AI_MODULE.status,
    integration_type=(
        _MULTIMODAL_AI_MODULE.integration_type
    ),
    areas=(
        TechnologyArea(
            area_id="multimodal_inputs_preprocessing",
            title="📥 Entradas e preparação multimodal",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_input_connectors",
                    title="🔌 Conectores de entradas multimodais",
                    description=(
                        "Recebimento de textos, imagens, áudios, vídeos, "
                        "documentos, eventos e dados de aplicações."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "document_ai",
                        "data_platform_governance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_format_normalization",
                    title="🔄 Normalização de formatos",
                    description=(
                        "Conversão, padronização e validação de formatos, "
                        "codificações, resoluções, canais e metadados."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "computer_vision_video_analytics",
                        "voice_audio_speech_ai",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_quality_preprocessing",
                    title="🧹 Qualidade e pré-processamento",
                    description=(
                        "Tratamento de ruído, orientação, contraste, "
                        "segmentação, volume, duração e qualidade da entrada."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "voice_audio_speech_ai",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_perception_extraction",
            title="👁️ Percepção e extração de informações",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_visual_understanding",
                    title="👁️ Compreensão de imagens e vídeos",
                    description=(
                        "Identificação de objetos, cenas, elementos, "
                        "eventos, textos visuais e relações espaciais."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "ai_evaluation_benchmarks_red_team",
                        "model_explainability_interpretability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_audio_speech_understanding",
                    title="🎙️ Compreensão de áudio e fala",
                    description=(
                        "Transcrição, segmentação, identificação de eventos "
                        "sonoros e compreensão de conteúdos falados."
                    ),
                    technology_dependencies=(
                        "voice_audio_speech_ai",
                        "ai_evaluation_benchmarks_red_team",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_document_understanding",
                    title="📄 Compreensão de documentos",
                    description=(
                        "Análise conjunta de texto, tabelas, imagens, "
                        "estrutura, campos, páginas e elementos visuais."
                    ),
                    technology_dependencies=(
                        "document_ai",
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_representations_fusion",
            title="🧩 Representações e fusão multimodal",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_embeddings",
                    title="🧮 Embeddings multimodais",
                    description=(
                        "Criação de representações vetoriais para textos, "
                        "imagens, áudio, vídeo e documentos."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "scientific_computing_engineering",
                        "data_platform_governance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_alignment",
                    title="🔗 Alinhamento entre modalidades",
                    description=(
                        "Associação entre trechos de texto, regiões de imagem, "
                        "momentos de áudio, cenas e elementos documentais."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_traceability_provenance",
                        "model_explainability_interpretability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_information_fusion",
                    title="🧩 Fusão de informações",
                    description=(
                        "Combinação controlada de sinais provenientes "
                        "de diferentes modalidades e fontes."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "knowledge_graph_semantic_ai",
                        "scientific_computing_engineering",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_retrieval_reasoning",
            title="🔎 Recuperação e raciocínio multimodal",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_cross_modal_search",
                    title="🔎 Pesquisa entre modalidades",
                    description=(
                        "Busca de imagens por texto, textos por imagens, "
                        "trechos por áudio e outras combinações."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_context_assembly",
                    title="🧠 Montagem de contexto multimodal",
                    description=(
                        "Seleção e organização de textos, imagens, áudios, "
                        "vídeos, documentos, evidências e metadados."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "agent_process_orchestration",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_reasoning",
                    title="🧭 Raciocínio entre fontes e modalidades",
                    description=(
                        "Análise conjunta de diferentes entradas para "
                        "comparações, relações e respostas fundamentadas."
                    ),
                    technology_dependencies=(
                        "enterprise_decision_intelligence",
                        "responsible_ai_ethics_risk",
                        "model_explainability_interpretability",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_generation_interaction",
            title="💬 Geração e interação multimodal",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_grounded_responses",
                    title="💬 Respostas fundamentadas",
                    description=(
                        "Geração de respostas apoiadas em conteúdos "
                        "multimodais recuperados e evidências autorizadas."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_content_generation",
                    title="🎨 Geração assistida de conteúdo",
                    description=(
                        "Produção controlada de textos, descrições, "
                        "resumos, estruturas e outros conteúdos."
                    ),
                    technology_dependencies=(
                        "digital_experiences_intelligent_interfaces",
                        "ai_software_engineering",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_omnichannel_interaction",
                    title="📱 Interação omnichannel",
                    description=(
                        "Uso de texto, voz, imagens, anexos e interfaces "
                        "em diferentes canais e dispositivos."
                    ),
                    technology_dependencies=(
                        "mobile_apps_omnichannel_experiences",
                        "voice_audio_speech_ai",
                        "digital_experiences_intelligent_interfaces",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_evaluation_safety_privacy",
            title="🛡️ Avaliação, segurança e privacidade",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_quality_evaluation",
                    title="🧪 Avaliação de qualidade multimodal",
                    description=(
                        "Medição de precisão, relevância, consistência, "
                        "fidelidade, cobertura e utilidade dos resultados."
                    ),
                    technology_dependencies=(
                        "ai_evaluation_benchmarks_red_team",
                        "ai_bias_quality_monitoring",
                        "software_testing_quality_reliability",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_adversarial_safety",
                    title="🛡️ Segurança e testes adversariais",
                    description=(
                        "Avaliação de entradas manipuladas, instruções ocultas, "
                        "conteúdos enganosos e combinações de risco."
                    ),
                    technology_dependencies=(
                        "ai_evaluation_benchmarks_red_team",
                        "operational_security_resilience",
                        "responsible_ai_ethics_risk",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_sensitive_data_protection",
                    title="🔐 Proteção de dados sensíveis",
                    description=(
                        "Detecção, mascaramento e controle de informações "
                        "sensíveis presentes em diferentes modalidades."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "privacy_enhancing_technologies",
                        "zero_trust_identity_access",
                    ),
                ),
            ),
        ),
        TechnologyArea(
            area_id="multimodal_operations_lifecycle",
            title="📊 Operações e ciclo de vida",
            capabilities=(
                TechnologyCapability(
                    capability_id="multimodal_serving_scaling",
                    title="🚀 Disponibilização e escalabilidade",
                    description=(
                        "Execução de modelos e pipelines multimodais com "
                        "controle de capacidade, desempenho e disponibilidade."
                    ),
                    technology_dependencies=(
                        "cloud_devops_finops",
                        "ai_operations",
                        "operational_security_resilience",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_observability",
                    title="📊 Logs, métricas e observabilidade",
                    description=(
                        "Monitoramento de entradas, modelos, latência, "
                        "custos, falhas, qualidade e resultados."
                    ),
                    technology_dependencies=(
                        "ai_operations",
                        "tools_analytics",
                        "data_traceability_provenance",
                    ),
                ),
                TechnologyCapability(
                    capability_id="multimodal_versioning_feedback",
                    title="🔄 Versionamento, feedback e evolução",
                    description=(
                        "Controle de versões, conjuntos de avaliação, "
                        "feedback humano, alterações e reversões."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "quality_process_management",
                        "technology_governance_policy_compliance",
                    ),
                ),
            ),
        ),
    ),
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

    module = PLATFORM_MODULE_BY_ID.get("multimodal_ai")

    if module is None:
        raise RuntimeError("O módulo multimodal_ai não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("MULTIMODAL_AI_PREREQUISITES=OK")


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
    """Adiciona IA Multimodal ao registro."""

    source = REGISTRY_PATH.read_text(
        encoding="utf-8",
    )

    if "MULTIMODAL_AI_SOLUTION = PlatformTechnologySolution(" in source:
        print("MULTIMODAL_AI_ALREADY_PRESENT=OK")
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
        MULTIMODAL_AI_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    AGENT_PROCESS_ORCHESTRATION_SOLUTION,
    KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION,
)"""

    new_registry = """    AGENT_PROCESS_ORCHESTRATION_SOLUTION,
    KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION,
    MULTIMODAL_AI_SOLUTION,
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

    print("MULTIMODAL_AI_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da IA Multimodal."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_multimodal_ai_is_complete" in source:
        print("MULTIMODAL_AI_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "MULTIMODAL_AI_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 3
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 4
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de três soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_multimodal_ai_is_complete():
    assert (
        MULTIMODAL_AI_SOLUTION.solution_id
        == "multimodal_ai"
    )

    assert len(
        MULTIMODAL_AI_SOLUTION.areas
    ) == 7

    assert (
        MULTIMODAL_AI_SOLUTION.capability_count
        == 21
    )


def test_multimodal_ai_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "multimodal_ai"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        MULTIMODAL_AI_SOLUTION.status
        is module.status
    )

    assert (
        MULTIMODAL_AI_SOLUTION.integration_type
        == module.integration_type
    )


def test_multimodal_ai_lookup():
    assert (
        platform_technology_solution(
            "multimodal_ai"
        )
        is MULTIMODAL_AI_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("MULTIMODAL_AI_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    multimodal_solution = getattr(
        module,
        "MULTIMODAL_AI_SOLUTION",
    )

    assert len(solutions) == 4
    assert len(multimodal_solution.areas) == 7

    assert multimodal_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 28
    assert total_capabilities == 84

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=4")
    print("TOTAL_TECHNOLOGY_AREAS=28")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=84")
    print("MULTIMODAL_AI_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
