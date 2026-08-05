"""Adiciona Visão Computacional e Análise de Vídeo ao registro tecnológico."""

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
        "computer_vision_video_analytics_technology_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
)


COMPUTER_VISION_DEFINITION = """
_COMPUTER_VISION_VIDEO_ANALYTICS_MODULE = (
    PLATFORM_MODULE_BY_ID[
        "computer_vision_video_analytics"
    ]
)


COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION = (
    PlatformTechnologySolution(
        solution_id="computer_vision_video_analytics",
        icon="👁️",
        title="Visão Computacional e Análise de Vídeo",
        description=(
            "Arquitetura tecnológica para captura, preparação, "
            "detecção, classificação, segmentação, rastreamento, "
            "inspeção visual, análise temporal, pesquisa multimodal, "
            "avaliação, privacidade, edge computing e observabilidade."
        ),
        status=(
            _COMPUTER_VISION_VIDEO_ANALYTICS_MODULE.status
        ),
        integration_type=(
            _COMPUTER_VISION_VIDEO_ANALYTICS_MODULE.integration_type
        ),
        areas=(
            TechnologyArea(
                area_id="computer_vision_inputs_datasets",
                title="📥 Entradas, mídia e conjuntos de dados",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_media_ingestion",
                        title="📥 Ingestão de imagens e vídeos",
                        description=(
                            "Recebimento de imagens, vídeos, transmissões, "
                            "eventos e arquivos por APIs e sistemas autorizados."
                        ),
                        technology_dependencies=(
                            "api_integrations_connectors",
                            "data_platform_governance",
                            "real_time_event_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_media_normalization",
                        title="🖼️ Normalização e preparação de mídia",
                        description=(
                            "Padronização de resolução, orientação, quadros, "
                            "formatos, iluminação, contraste e qualidade."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "scientific_computing_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_dataset_annotation",
                        title="🏷️ Anotação e gestão de datasets",
                        description=(
                            "Organização de classes, rótulos, regiões, "
                            "metadados, versões, origem e evidências."
                        ),
                        technology_dependencies=(
                            "data_platform_governance",
                            "data_traceability_provenance",
                            "ai_bias_quality_monitoring",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="computer_vision_detection_segmentation",
                title="🎯 Detecção, classificação e segmentação",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_object_detection",
                        title="🎯 Detecção e localização de objetos",
                        description=(
                            "Identificação e localização de elementos "
                            "relevantes em imagens e quadros de vídeo."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "ai_evaluation_benchmarks_red_team",
                            "model_explainability_interpretability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_classification_segmentation",
                        title="🧩 Classificação e segmentação visual",
                        description=(
                            "Classificação de imagens e separação de regiões, "
                            "objetos, superfícies e componentes visuais."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "scientific_computing_engineering",
                            "software_testing_quality_reliability",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_object_tracking",
                        title="🧭 Rastreamento de objetos",
                        description=(
                            "Acompanhamento temporal de objetos, trajetórias, "
                            "mudanças de posição e continuidade entre quadros."
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
                area_id="computer_vision_ocr_inspection",
                title="🔎 OCR, inspeção e anomalias visuais",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_visual_ocr",
                        title="🔤 OCR e leitura de elementos visuais",
                        description=(
                            "Reconhecimento de textos, códigos, etiquetas, "
                            "campos e informações presentes em imagens."
                        ),
                        technology_dependencies=(
                            "document_ai",
                            "multimodal_ai",
                            "enterprise_rag",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_quality_inspection",
                        title="✅ Inspeção visual de qualidade",
                        description=(
                            "Verificação assistida de características, "
                            "padrões, defeitos, conformidade e evidências."
                        ),
                        technology_dependencies=(
                            "quality_process_management",
                            "iot_edge_intelligence",
                            "enterprise_decision_intelligence",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_visual_anomalies",
                        title="⚠️ Detecção de anomalias visuais",
                        description=(
                            "Identificação de padrões incomuns, alterações, "
                            "desvios e situações que precisam de revisão."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "real_time_event_intelligence",
                            "operational_security_resilience",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="computer_vision_video_events",
                title="🎥 Vídeo, eventos e análise temporal",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_video_event_detection",
                        title="🎥 Detecção de eventos em vídeo",
                        description=(
                            "Identificação de eventos, mudanças de estado, "
                            "movimentos e situações relevantes ao longo do tempo."
                        ),
                        technology_dependencies=(
                            "real_time_event_intelligence",
                            "iot_edge_intelligence",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_temporal_understanding",
                        title="⏱️ Compreensão temporal e de cenas",
                        description=(
                            "Análise da sequência de ações, relações temporais, "
                            "cenas, transições e contexto audiovisual."
                        ),
                        technology_dependencies=(
                            "multimodal_ai",
                            "knowledge_graph_semantic_ai",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_event_workflows",
                        title="🔔 Alertas e workflows visuais",
                        description=(
                            "Acionamento de notificações, revisões humanas, "
                            "integrações e processos após eventos detectados."
                        ),
                        technology_dependencies=(
                            "agent_process_orchestration",
                            "business_automation",
                            "api_integrations_connectors",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="computer_vision_search_context",
                title="🔍 Pesquisa e contexto visual",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_visual_embeddings",
                        title="🧮 Embeddings e pesquisa visual",
                        description=(
                            "Criação de representações vetoriais e busca "
                            "por similaridade entre imagens e vídeos."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "multimodal_ai",
                            "data_platform_governance",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_cross_modal_retrieval",
                        title="🔗 Recuperação entre texto e imagem",
                        description=(
                            "Pesquisa de imagens por texto, textos por imagens "
                            "e recuperação combinada de conteúdos."
                        ),
                        technology_dependencies=(
                            "enterprise_rag",
                            "knowledge_graph_semantic_ai",
                            "multimodal_ai",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_evidence_context",
                        title="🧾 Evidências e contexto visual",
                        description=(
                            "Associação de resultados a imagens, quadros, "
                            "regiões, documentos, fontes e metadados."
                        ),
                        technology_dependencies=(
                            "data_traceability_provenance",
                            "document_ai",
                            "model_explainability_interpretability",
                        ),
                    ),
                ),
            ),
            TechnologyArea(
                area_id="computer_vision_evaluation_privacy",
                title="🛡️ Avaliação, segurança e privacidade",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_benchmark_evaluation",
                        title="🧪 Benchmarks e avaliação visual",
                        description=(
                            "Medição de precisão, cobertura, falsos alertas, "
                            "latência, robustez e qualidade dos resultados."
                        ),
                        technology_dependencies=(
                            "ai_evaluation_benchmarks_red_team",
                            "software_testing_quality_reliability",
                            "tools_analytics",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_bias_drift_robustness",
                        title="📉 Viés, drift e robustez",
                        description=(
                            "Monitoramento de diferenças de desempenho, "
                            "mudanças nos dados e degradação dos modelos."
                        ),
                        technology_dependencies=(
                            "ai_bias_quality_monitoring",
                            "responsible_ai_ethics_risk",
                            "ai_operations",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_privacy_access",
                        title="🔐 Privacidade e controle de acesso",
                        description=(
                            "Proteção de mídias, mascaramento de informações "
                            "sensíveis, permissões e acesso controlado."
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
                area_id="computer_vision_deployment_operations",
                title="🚀 Edge, implantação e operações",
                capabilities=(
                    TechnologyCapability(
                        capability_id="computer_vision_edge_inference",
                        title="📡 Inferência em edge computing",
                        description=(
                            "Execução otimizada em dispositivos, sensores, "
                            "câmeras e ambientes com recursos limitados."
                        ),
                        technology_dependencies=(
                            "iot_edge_intelligence",
                            "cloud_devops_finops",
                            "scientific_computing_engineering",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_serving_scaling",
                        title="☁️ Serving e escalabilidade",
                        description=(
                            "Disponibilização dos modelos com controle de "
                            "capacidade, disponibilidade, desempenho e custos."
                        ),
                        technology_dependencies=(
                            "cloud_devops_finops",
                            "ai_operations",
                            "operational_security_resilience",
                        ),
                    ),
                    TechnologyCapability(
                        capability_id="computer_vision_observability_lifecycle",
                        title="📊 Observabilidade e ciclo de vida",
                        description=(
                            "Monitoramento, versionamento, feedback, logs, "
                            "métricas, implantação e reversão dos modelos."
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

    module_id = "computer_vision_video_analytics"

    module = PLATFORM_MODULE_BY_ID.get(module_id)

    if module is None:
        raise RuntimeError(f"O módulo {module_id} não existe.")

    if module.category is not PlatformModuleCategory.TECHNOLOGY_CORE:
        raise RuntimeError("O módulo não pertence ao núcleo tecnológico.")

    print("COMPUTER_VISION_VIDEO_ANALYTICS_PREREQUISITES=OK")


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

    if "COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION =" in source:
        print("COMPUTER_VISION_VIDEO_ANALYTICS_ALREADY_PRESENT=OK")
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
        COMPUTER_VISION_DEFINITION + registry_anchor,
        1,
    )

    old_registry = """    KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION,
    MULTIMODAL_AI_SOLUTION,
)"""

    new_registry = """    KNOWLEDGE_GRAPH_SEMANTIC_AI_SOLUTION,
    MULTIMODAL_AI_SOLUTION,
    COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION,
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

    print("COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION_CREATED=OK")


def update_tests() -> None:
    """Adiciona os testes da nova solução."""

    source = TEST_PATH.read_text(
        encoding="utf-8",
    )

    if "def test_computer_vision_video_analytics_is_complete" in source:
        print("COMPUTER_VISION_VIDEO_ANALYTICS_TESTS_ALREADY_PRESENT=OK")
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

    solution_name = "COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION"

    if solution_name not in import_block:
        source = source[:import_end] + f"    {solution_name},\n" + source[import_end:]

    old_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 4
"""

    new_count = """    assert len(
        PLATFORM_TECHNOLOGY_SOLUTIONS
    ) == 5
"""

    if old_count not in source:
        raise RuntimeError(
            "Contagem atual de quatro soluções tecnológicas não encontrada."
        )

    source = source.replace(
        old_count,
        new_count,
        1,
    )

    source += """


def test_computer_vision_video_analytics_is_complete():
    assert (
        COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION.solution_id
        == "computer_vision_video_analytics"
    )

    assert len(
        COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION.areas
    ) == 7

    assert (
        COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION.capability_count
        == 21
    )


def test_computer_vision_video_analytics_matches_main_module():
    module = PLATFORM_MODULE_BY_ID[
        "computer_vision_video_analytics"
    ]

    assert (
        module.category
        is PlatformModuleCategory.TECHNOLOGY_CORE
    )

    assert (
        COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION.status
        is module.status
    )

    assert (
        COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION.integration_type
        == module.integration_type
    )


def test_computer_vision_video_analytics_lookup():
    assert (
        platform_technology_solution(
            "computer_vision_video_analytics"
        )
        is COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION
    )
"""

    TEST_PATH.write_text(
        source.rstrip() + "\n",
        encoding="utf-8",
    )

    print("COMPUTER_VISION_VIDEO_ANALYTICS_TESTS_CREATED=OK")


def validate_result() -> None:
    """Valida os totais após a expansão."""

    importlib.invalidate_caches()

    module = importlib.import_module("src.platform_technology_solutions")

    solutions = getattr(
        module,
        "PLATFORM_TECHNOLOGY_SOLUTIONS",
    )

    computer_vision_solution = getattr(
        module,
        "COMPUTER_VISION_VIDEO_ANALYTICS_SOLUTION",
    )

    assert len(solutions) == 5

    assert len(computer_vision_solution.areas) == 7

    assert computer_vision_solution.capability_count == 21

    total_areas = sum(len(solution.areas) for solution in solutions)

    total_capabilities = sum(solution.capability_count for solution in solutions)

    assert total_areas == 35
    assert total_capabilities == 105

    print("SPECIALIZED_TECHNOLOGY_SOLUTIONS=5")
    print("TOTAL_TECHNOLOGY_AREAS=35")
    print("TOTAL_TECHNOLOGY_CAPABILITIES=105")
    print("COMPUTER_VISION_VIDEO_ANALYTICS_EXPANSION_VALIDATED=OK")


validate_prerequisites()
create_backup()
update_registry()
update_tests()
validate_result()
