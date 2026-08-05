"""Cria o registro empresarial especializado do Document AI."""

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
    / ("document_ai_business_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
)


REGISTRY_SOURCE = '''"""Registro das soluções empresariais especializadas da INNA."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.platform_modules import PLATFORM_MODULE_BY_ID


class BusinessSolutionStatus(StrEnum):
    """Situação de uma solução empresarial."""

    ACTIVE = "active"
    INTEGRATING = "integrating"
    PLANNED = "planned"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class BusinessCapability:
    """Capacidade interna de uma solução empresarial."""

    capability_id: str
    title: str
    description: str
    technology_dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BusinessArea:
    """Área especializada de uma solução empresarial."""

    area_id: str
    title: str
    capabilities: tuple[BusinessCapability, ...]


@dataclass(frozen=True, slots=True)
class PlatformBusinessSolution:
    """Solução empresarial composta por áreas e capacidades."""

    solution_id: str
    icon: str
    title: str
    description: str
    status: BusinessSolutionStatus
    integration_type: str
    areas: tuple[BusinessArea, ...]

    @property
    def capability_count(self) -> int:
        """Quantidade total de capacidades."""

        return sum(
            len(area.capabilities)
            for area in self.areas
        )

    @property
    def technology_dependencies(self) -> tuple[str, ...]:
        """Dependências tecnológicas sem repetições."""

        return tuple(
            dict.fromkeys(
                dependency
                for area in self.areas
                for capability in area.capabilities
                for dependency in (
                    capability.technology_dependencies
                )
            )
        )


DOCUMENT_AI_SOLUTION = PlatformBusinessSolution(
    solution_id="document_ai",
    icon="📄",
    title="Document AI",
    description=(
        "Solução empresarial para captura, OCR, classificação, "
        "extração, validação, compreensão, pesquisa, privacidade "
        "e automação de documentos."
    ),
    status=BusinessSolutionStatus.PLANNED,
    integration_type="hybrid",
    areas=(
        BusinessArea(
            area_id="document_intake_capture",
            title="📥 Entrada e captura de documentos",
            capabilities=(
                BusinessCapability(
                    capability_id="document_multichannel_upload",
                    title="📥 Upload e entrada multicanal",
                    description=(
                        "Recebimento de documentos por interface web, "
                        "API, e-mail, armazenamento e integrações."
                    ),
                    technology_dependencies=(
                        "api_integrations_connectors",
                        "cloud_devops_finops",
                        "mobile_apps_omnichannel_experiences",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_batch_ingestion",
                    title="📚 Ingestão individual e em lote",
                    description=(
                        "Processamento controlado de arquivos individuais, "
                        "lotes, filas e grandes volumes documentais."
                    ),
                    technology_dependencies=(
                        "data_platform_governance",
                        "real_time_event_intelligence",
                        "cloud_devops_finops",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_format_normalization",
                    title="🔄 Normalização de formatos",
                    description=(
                        "Padronização de PDF, imagens, documentos "
                        "digitalizados e outros formatos aceitos."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "data_platform_governance",
                        "business_automation",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="document_ocr_preprocessing",
            title="🔎 OCR e preparação de imagens",
            capabilities=(
                BusinessCapability(
                    capability_id="document_ocr_text_extraction",
                    title="🔎 OCR e extração de texto",
                    description=(
                        "Reconhecimento de texto em documentos digitais, "
                        "imagens e arquivos escaneados."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "multimodal_ai",
                        "scientific_computing_engineering",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_image_quality",
                    title="🖼️ Qualidade e preparação de imagens",
                    description=(
                        "Correção de rotação, ruído, contraste, recorte "
                        "e qualidade antes do processamento."
                    ),
                    technology_dependencies=(
                        "computer_vision_video_analytics",
                        "multimodal_ai",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="document_classification_routing",
            title="🗂️ Classificação e roteamento",
            capabilities=(
                BusinessCapability(
                    capability_id="document_automatic_classification",
                    title="🗂️ Classificação automática",
                    description=(
                        "Identificação do tipo documental com regras, "
                        "modelos de IA e critérios configuráveis."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "knowledge_graph_semantic_ai",
                        "ai_evaluation_benchmarks_red_team",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_metadata_taxonomy",
                    title="🏷️ Metadados e taxonomia documental",
                    description=(
                        "Organização por categorias, assuntos, entidades, "
                        "origem, datas e metadados empresariais."
                    ),
                    technology_dependencies=(
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                        "data_traceability_provenance",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_workflow_routing",
                    title="🔀 Roteamento inteligente",
                    description=(
                        "Envio do documento para equipes, filas, sistemas "
                        "e processos conforme regras de negócio."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "business_automation",
                        "real_time_event_intelligence",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="document_extraction_validation",
            title="📊 Extração e validação de dados",
            capabilities=(
                BusinessCapability(
                    capability_id="document_field_table_extraction",
                    title="📊 Extração de campos e tabelas",
                    description=(
                        "Extração estruturada de campos, entidades, "
                        "tabelas, itens, valores e relacionamentos."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_data_validation",
                    title="✅ Validação e consistência dos dados",
                    description=(
                        "Verificação de formato, obrigatoriedade, regras, "
                        "consistência e qualidade das informações."
                    ),
                    technology_dependencies=(
                        "quality_process_management",
                        "software_testing_quality_reliability",
                        "enterprise_decision_intelligence",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_human_review",
                    title="👤 Revisão humana e tratamento de exceções",
                    description=(
                        "Encaminhamento de documentos duvidosos para "
                        "aprovação, correção, rejeição ou reprocessamento."
                    ),
                    technology_dependencies=(
                        "agent_process_orchestration",
                        "ai_operations",
                        "data_traceability_provenance",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="document_understanding_search",
            title="🧠 Compreensão, pesquisa e comparação",
            capabilities=(
                BusinessCapability(
                    capability_id="document_summary_understanding",
                    title="📝 Resumo e compreensão documental",
                    description=(
                        "Geração de resumos, tópicos, entidades, pontos "
                        "importantes e informações relevantes."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "multimodal_ai",
                        "knowledge_graph_semantic_ai",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_semantic_search_qa",
                    title="🔍 Pesquisa semântica e perguntas",
                    description=(
                        "Busca por significado e respostas fundamentadas "
                        "no conteúdo dos documentos autorizados."
                    ),
                    technology_dependencies=(
                        "enterprise_rag",
                        "knowledge_graph_semantic_ai",
                        "data_platform_governance",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_comparison_versions",
                    title="⚖️ Comparação e controle de versões",
                    description=(
                        "Comparação entre documentos, cláusulas, versões, "
                        "alterações e diferenças relevantes."
                    ),
                    technology_dependencies=(
                        "multimodal_ai",
                        "data_traceability_provenance",
                        "software_testing_quality_reliability",
                    ),
                ),
            ),
        ),
        BusinessArea(
            area_id="document_privacy_governance_automation",
            title="🔐 Privacidade, governança e automação",
            capabilities=(
                BusinessCapability(
                    capability_id="document_sensitive_data_protection",
                    title="🔐 Detecção e proteção de dados sensíveis",
                    description=(
                        "Identificação, mascaramento e anonimização de "
                        "dados pessoais, confidenciais ou restritos."
                    ),
                    technology_dependencies=(
                        "privacy_data_protection_lgpd",
                        "privacy_enhancing_technologies",
                        "zero_trust_identity_access",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_audit_retention",
                    title="🧾 Auditoria, retenção e rastreabilidade",
                    description=(
                        "Registro de eventos, origem, alterações, acesso, "
                        "retenção, descarte e evidências documentais."
                    ),
                    technology_dependencies=(
                        "data_traceability_provenance",
                        "technology_governance_policy_compliance",
                        "operational_security_resilience",
                    ),
                ),
                BusinessCapability(
                    capability_id="document_process_automation",
                    title="⚙️ Automação de processos documentais",
                    description=(
                        "Acionamento de fluxos, integrações, notificações "
                        "e operações após o processamento documental."
                    ),
                    technology_dependencies=(
                        "business_automation",
                        "agent_process_orchestration",
                        "api_integrations_connectors",
                    ),
                ),
            ),
        ),
    ),
)


PLATFORM_BUSINESS_SOLUTIONS: tuple[
    PlatformBusinessSolution,
    ...
] = (
    DOCUMENT_AI_SOLUTION,
)


PLATFORM_BUSINESS_SOLUTION_BY_ID = {
    solution.solution_id: solution
    for solution in PLATFORM_BUSINESS_SOLUTIONS
}


def platform_business_solution(
    solution_id: str,
) -> PlatformBusinessSolution | None:
    """Retorna uma solução empresarial pelo ID."""

    return PLATFORM_BUSINESS_SOLUTION_BY_ID.get(
        solution_id
    )


def validate_platform_business_solution_registry() -> None:
    """Valida o registro de soluções empresariais."""

    solution_ids = [
        solution.solution_id
        for solution in PLATFORM_BUSINESS_SOLUTIONS
    ]

    if len(solution_ids) != len(set(solution_ids)):
        raise ValueError(
            "Existem soluções empresariais duplicadas."
        )

    for solution in PLATFORM_BUSINESS_SOLUTIONS:
        if solution.solution_id not in PLATFORM_MODULE_BY_ID:
            raise ValueError(
                "Card empresarial inexistente: "
                f"{solution.solution_id}"
            )

        if not solution.areas:
            raise ValueError(
                "Solução empresarial sem áreas: "
                f"{solution.solution_id}"
            )

        area_ids = [
            area.area_id
            for area in solution.areas
        ]

        if len(area_ids) != len(set(area_ids)):
            raise ValueError(
                "Áreas empresariais duplicadas em: "
                f"{solution.solution_id}"
            )

        capability_ids = [
            capability.capability_id
            for area in solution.areas
            for capability in area.capabilities
        ]

        if len(capability_ids) != len(
            set(capability_ids)
        ):
            raise ValueError(
                "Capacidades empresariais duplicadas em: "
                f"{solution.solution_id}"
            )

        for area in solution.areas:
            if not area.capabilities:
                raise ValueError(
                    "Área empresarial sem capacidades: "
                    f"{area.area_id}"
                )

            for capability in area.capabilities:
                if not capability.technology_dependencies:
                    raise ValueError(
                        "Capacidade sem dependências: "
                        f"{capability.capability_id}"
                    )

                missing_dependencies = {
                    dependency
                    for dependency in (
                        capability.technology_dependencies
                    )
                    if dependency
                    not in PLATFORM_MODULE_BY_ID
                }

                if missing_dependencies:
                    raise ValueError(
                        "Dependências inexistentes em "
                        f"{capability.capability_id}: "
                        f"{sorted(missing_dependencies)}"
                    )


validate_platform_business_solution_registry()
'''


TEST_SOURCE = """from src.platform_business_solutions import (
    DOCUMENT_AI_SOLUTION,
    PLATFORM_BUSINESS_SOLUTIONS,
    BusinessSolutionStatus,
    platform_business_solution,
    validate_platform_business_solution_registry,
)


def test_business_solution_registry_is_valid():
    validate_platform_business_solution_registry()


def test_document_ai_is_registered():
    assert len(PLATFORM_BUSINESS_SOLUTIONS) == 1

    assert (
        platform_business_solution("document_ai")
        is DOCUMENT_AI_SOLUTION
    )


def test_document_ai_solution_is_complete():
    assert (
        DOCUMENT_AI_SOLUTION.solution_id
        == "document_ai"
    )
    assert (
        DOCUMENT_AI_SOLUTION.status
        is BusinessSolutionStatus.PLANNED
    )
    assert (
        DOCUMENT_AI_SOLUTION.integration_type
        == "hybrid"
    )
    assert len(
        DOCUMENT_AI_SOLUTION.areas
    ) == 6
    assert (
        DOCUMENT_AI_SOLUTION.capability_count
        == 16
    )


def test_document_ai_capabilities_have_dependencies():
    for area in DOCUMENT_AI_SOLUTION.areas:
        assert area.capabilities

        for capability in area.capabilities:
            assert capability.technology_dependencies


def test_document_ai_dependency_list_has_no_duplicates():
    dependencies = (
        DOCUMENT_AI_SOLUTION.technology_dependencies
    )

    assert dependencies
    assert len(dependencies) == len(set(dependencies))


def test_unknown_business_solution_returns_none():
    assert (
        platform_business_solution(
            "unknown_business_solution"
        )
        is None
    )
"""


def create_backup() -> None:
    """Cria backup se os arquivos já existirem."""

    existing_paths = tuple(
        path
        for path in (
            REGISTRY_PATH,
            TEST_PATH,
        )
        if path.exists()
    )

    if not existing_paths:
        print("BACKUP_NOT_REQUIRED=OK")
        return

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    for source_path in existing_paths:
        shutil.copy2(
            source_path,
            BACKUP_ROOT / source_path.name,
        )

    print(f"BACKUP_CREATED={BACKUP_ROOT}")


def create_files() -> None:
    """Cria o registro e seus testes."""

    if REGISTRY_PATH.exists():
        raise RuntimeError(
            "src/platform_business_solutions.py já existe. Audite antes de substituir."
        )

    if TEST_PATH.exists():
        raise RuntimeError(
            "O teste do registro empresarial já existe. Audite antes de substituir."
        )

    REGISTRY_PATH.write_text(
        REGISTRY_SOURCE,
        encoding="utf-8",
    )

    TEST_PATH.write_text(
        TEST_SOURCE,
        encoding="utf-8",
    )

    print("DOCUMENT_AI_BUSINESS_REGISTRY_CREATED=OK")


create_backup()
create_files()
