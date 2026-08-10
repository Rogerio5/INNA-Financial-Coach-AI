"""Enriquecimento semÃ¢ntico determinÃ­stico do Knowledge Graph da INNA."""

from __future__ import annotations

from dataclasses import dataclass

from src.knowledge_graph.models import (
    FinancialConceptNode,
    FinancialTopicNode,
)
from src.knowledge_graph.rag_source import (
    RagChunkRecord,
    RagKnowledgeSnapshot,
)
from src.knowledge_graph.relationships import (
    KnowledgeGraphRelationship,
    KnowledgeRelationshipType,
)

SemanticNode = FinancialConceptNode | FinancialTopicNode


@dataclass(frozen=True, slots=True)
class SemanticEnrichmentPlan:
    nodes: tuple[SemanticNode, ...]
    relationships: tuple[KnowledgeGraphRelationship, ...]
    concept_count: int
    topic_count: int
    explains_count: int
    mentions_count: int
    belongs_to_count: int

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)


def _metadata_value(
    chunk: RagChunkRecord,
    key: str,
) -> str:
    return str(
        chunk.metadata.get(key) or ""
    ).strip()


def _display_label(value: str) -> str:
    return " ".join(
        part
        for part in value.replace("_", " ").split()
        if part
    ).title()


class SemanticKnowledgeGraphEnricher:
    """Mapeia metadata.topic e metadata.area para nÃ³s semÃ¢nticos."""

    def build(
        self,
        snapshot: RagKnowledgeSnapshot,
    ) -> SemanticEnrichmentPlan:
        documents_by_id = {
            document.document_id: document
            for document in snapshot.documents
        }

        if len(documents_by_id) != len(
            snapshot.documents
        ):
            raise ValueError(
                "Snapshot contÃ©m document_id duplicado."
            )

        chunk_ids = [
            chunk.chunk_id
            for chunk in snapshot.chunks
        ]

        if len(chunk_ids) != len(
            set(chunk_ids)
        ):
            raise ValueError(
                "Snapshot contÃ©m chunk_id duplicado."
            )

        document_semantics: dict[
            int,
            tuple[str, str],
        ] = {}

        topic_to_area: dict[str, str] = {}
        chunk_semantics: list[
            tuple[RagChunkRecord, str, str]
        ] = []

        for chunk in snapshot.chunks:
            document = documents_by_id.get(
                chunk.document_id
            )

            if document is None:
                raise ValueError(
                    "Chunk referencia document_id ausente."
                )

            if (
                chunk.document_key
                != document.document_key
            ):
                raise ValueError(
                    "Chunk possui document_key incompatÃ­vel."
                )

            topic = _metadata_value(
                chunk,
                "topic",
            )
            area = _metadata_value(
                chunk,
                "area",
            )

            if not topic:
                raise ValueError(
                    "Chunk canÃ´nico sem metadata.topic."
                )

            if not area:
                raise ValueError(
                    "Chunk canÃ´nico sem metadata.area."
                )

            previous_document_semantics = (
                document_semantics.get(
                    chunk.document_id
                )
            )

            if (
                previous_document_semantics is not None
                and previous_document_semantics
                != (topic, area)
            ):
                raise ValueError(
                    "Documento possui topic/area inconsistentes."
                )

            document_semantics[
                chunk.document_id
            ] = (topic, area)

            previous_area = topic_to_area.get(
                topic
            )

            if (
                previous_area is not None
                and previous_area != area
            ):
                raise ValueError(
                    "Mesmo topic associado a Ã¡reas diferentes."
                )

            topic_to_area[topic] = area

            chunk_semantics.append(
                (
                    chunk,
                    topic,
                    area,
                )
            )

        if len(document_semantics) != len(
            snapshot.documents
        ):
            raise ValueError(
                "Nem todos os documentos receberam semÃ¢ntica."
            )

        areas = sorted(
            set(topic_to_area.values())
        )
        topics = sorted(
            topic_to_area
        )

        nodes: list[SemanticNode] = []
        relationships: list[
            KnowledgeGraphRelationship
        ] = []

        for area in areas:
            nodes.append(
                FinancialTopicNode(
                    node_id=f"topic:{area}",
                    label=_display_label(area),
                    topic_key=area,
                    description=(
                        "Ãrea semÃ¢ntica canÃ´nica derivada "
                        "do metadata.area do corpus RAG."
                    ),
                    metadata={
                        "semantic_source": (
                            "rag_metadata.area"
                        ),
                        "deterministic": True,
                    },
                )
            )

        for topic in topics:
            area = topic_to_area[topic]

            nodes.append(
                FinancialConceptNode(
                    node_id=f"concept:{topic}",
                    label=_display_label(topic),
                    concept_key=topic,
                    description=(
                        "Conceito canÃ´nico derivado do "
                        "metadata.topic do corpus RAG."
                    ),
                    aliases=(),
                    metadata={
                        "semantic_source": (
                            "rag_metadata.topic"
                        ),
                        "area": area,
                        "deterministic": True,
                    },
                )
            )

            relationships.append(
                KnowledgeGraphRelationship(
                    source_id=f"concept:{topic}",
                    target_id=f"topic:{area}",
                    relationship_type=(
                        KnowledgeRelationshipType.BELONGS_TO
                    ),
                    properties={
                        "mapping": (
                            "deterministic_rag_metadata"
                        ),
                    },
                )
            )

        for document in snapshot.documents:
            topic, _area = document_semantics[
                document.document_id
            ]

            relationships.append(
                KnowledgeGraphRelationship(
                    source_id=(
                        f"document:{document.document_key}"
                    ),
                    target_id=f"concept:{topic}",
                    relationship_type=(
                        KnowledgeRelationshipType.EXPLAINS
                    ),
                    properties={
                        "mapping": (
                            "deterministic_rag_metadata"
                        ),
                    },
                )
            )

        for chunk, topic, _area in chunk_semantics:
            relationships.append(
                KnowledgeGraphRelationship(
                    source_id=f"chunk:{chunk.chunk_id}",
                    target_id=f"concept:{topic}",
                    relationship_type=(
                        KnowledgeRelationshipType.MENTIONS
                    ),
                    properties={
                        "mapping": (
                            "deterministic_rag_metadata"
                        ),
                    },
                )
            )

        node_ids = [
            node.node_id
            for node in nodes
        ]

        if len(node_ids) != len(
            set(node_ids)
        ):
            raise ValueError(
                "Enrichment plan gerou node_id duplicado."
            )

        relationship_keys = [
            (
                relationship.source_id,
                relationship.relationship_type,
                relationship.target_id,
            )
            for relationship in relationships
        ]

        if len(relationship_keys) != len(
            set(relationship_keys)
        ):
            raise ValueError(
                "Enrichment plan gerou relacionamento duplicado."
            )

        belongs_to_count = sum(
            relationship.relationship_type
            == KnowledgeRelationshipType.BELONGS_TO
            for relationship in relationships
        )

        explains_count = sum(
            relationship.relationship_type
            == KnowledgeRelationshipType.EXPLAINS
            for relationship in relationships
        )

        mentions_count = sum(
            relationship.relationship_type
            == KnowledgeRelationshipType.MENTIONS
            for relationship in relationships
        )

        return SemanticEnrichmentPlan(
            nodes=tuple(nodes),
            relationships=tuple(
                relationships
            ),
            concept_count=len(topics),
            topic_count=len(areas),
            explains_count=explains_count,
            mentions_count=mentions_count,
            belongs_to_count=belongs_to_count,
        )


__all__ = [
    "SemanticEnrichmentPlan",
    "SemanticKnowledgeGraphEnricher",
]
