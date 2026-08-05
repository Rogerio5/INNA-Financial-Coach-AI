"""
Testes da Fase 3 da Semana 4:
Evidence Collector profissional.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.agent_tools.financial_history_tools import (
    ConsultarHistoricoFinanceiroOutput,
)
from src.agent_tools.rag_tools import (
    BuscarConhecimentoRagOutput,
)
from src.agentic_rag import (
    EvidenceCollectionError,
    EvidenceCollectionResult,
    EvidenceCollectionStatus,
    EvidenceItem,
    ResearchSource,
    ResearchSubquery,
    UnsupportedEvidenceSourceError,
    collect_evidence_from_tool_output,
    collect_evidence_from_tool_result,
    content_sha256,
    deduplicate_evidence,
    lexical_relevance,
)


def _knowledge_step() -> ResearchSubquery:
    return ResearchSubquery(
        step_id="step_01_knowledge",
        question=("Como criar uma reserva de emergência?"),
        source=(ResearchSource.KNOWLEDGE_BASE),
        tool_name="buscar_conhecimento_rag",
        top_k=4,
    )


def _history_step() -> ResearchSubquery:
    return ResearchSubquery(
        step_id="step_02_history",
        question=("Compare meu histórico financeiro e minha evolução."),
        source=(ResearchSource.FINANCIAL_HISTORY),
        tool_name=("consultar_historico_financeiro"),
        max_results=5,
    )


def test_real_rag_output_model_is_collected():
    output = BuscarConhecimentoRagOutput(
        pergunta=("Como criar uma reserva de emergência?"),
        idioma="pt",
        resposta=("Comece definindo uma meta mensal."),
        fontes=[
            "educacao_financeira.md",
            "reserva_emergencia.md",
        ],
        modo="hybrid_rerank",
        documentos_recuperados=2,
        contexto_recuperado=[
            ("A reserva de emergência ajuda a cobrir imprevistos financeiros."),
            (
                "A formação da reserva deve ocorrer "
                "gradualmente, respeitando o orçamento."
            ),
        ],
        duracao_rag_ms=120,
    )

    result = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
        call_id="call-rag-1",
    )

    assert result.status == EvidenceCollectionStatus.COLLECTED
    assert len(result.evidence) == 2
    assert result.selected_count == 2
    assert result.source_schema == "BuscarConhecimentoRagOutput"
    assert result.tool_answer == ("Comece definindo uma meta mensal.")
    assert all(item.sensitive is False for item in result.evidence)
    assert all(
        item.metadata["answer_used_as_evidence"] is False for item in result.evidence
    )


def test_rag_references_are_associated_by_position():
    output = {
        "resposta": "Resposta fundamentada.",
        "fontes": [
            "fonte-a.md",
            "fonte-b.md",
        ],
        "contexto_recuperado": [
            "Conteúdo financeiro da fonte A.",
            "Conteúdo financeiro da fonte B.",
        ],
        "documentos_recuperados": 2,
    }

    result = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )

    assert result.evidence[0].references in (
        ["fonte-a.md"],
        ["fonte-b.md"],
    )

    all_references = {item.references[0] for item in result.evidence}

    assert all_references == {
        "fonte-a.md",
        "fonte-b.md",
    }


def test_evidence_ids_are_deterministic():
    output = {
        "resposta": "Resposta.",
        "fontes": ["fonte.md"],
        "contexto_recuperado": [
            ("A reserva financeira deve ser construída gradualmente.")
        ],
    }

    first = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )
    second = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )

    assert first.evidence[0].evidence_id == second.evidence[0].evidence_id
    assert first.evidence[0].content_sha256 == second.evidence[0].content_sha256
    assert first.output_sha256 == second.output_sha256


def test_generated_answer_is_not_used_as_evidence():
    output = {
        "resposta": ("Esta resposta foi gerada pelo modelo."),
        "fontes": [],
        "contexto_recuperado": [],
        "documentos_recuperados": 0,
    }

    result = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )

    assert result.status == EvidenceCollectionStatus.EMPTY
    assert result.evidence == []
    assert result.tool_answer
    assert "answer_without_retrieval_context" in result.warnings


def test_duplicate_rag_context_is_removed():
    output = {
        "resposta": "Resposta.",
        "fontes": ["fonte.md"],
        "contexto_recuperado": [
            ("A reserva de emergência cobre imprevistos financeiros."),
            ("A reserva de emergência cobre imprevistos financeiros."),
        ],
        "documentos_recuperados": 2,
    }

    result = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )

    assert len(result.evidence) == 1
    assert "duplicate_evidence_removed" in result.warnings


def test_english_rag_aliases_are_supported():
    output = {
        "answer": "Grounded answer.",
        "sources": ["source.md"],
        "retrieval_context": [("An emergency fund helps cover unexpected expenses.")],
        "mode": "hybrid",
        "retrieved_documents": 1,
        "duration_ms": 50,
    }

    result = collect_evidence_from_tool_output(
        step=_knowledge_step(),
        output=output,
    )

    assert result.status == EvidenceCollectionStatus.COLLECTED
    assert len(result.evidence) == 1
    assert result.metadata["retrieval_mode"] == "hybrid"


def test_history_keeps_only_authorized_fields():
    output = {
        "possui_historico": True,
        "total": 1,
        "diagnosticos": [
            {
                "data_hora": ("2026-08-01T10:00:00"),
                "saldo_estimado": 500.0,
                "comprometimento_renda_percentual": (58.5),
                "meses_reserva_estimados": 1.5,
                "score_financeiro": 62,
                "nivel_risco": "Medio",
                "situacao": "saldo_positivo",
                "moeda": "BRL",
                "idioma": "pt",
                "user_id": "secret-user-id",
                "email": "private@example.com",
                "campo_interno": "não expor",
            }
        ],
    }

    result = collect_evidence_from_tool_output(
        step=_history_step(),
        output=output,
        call_id="call-history-1",
    )

    assert result.status == EvidenceCollectionStatus.COLLECTED
    assert len(result.evidence) == 1

    evidence = result.evidence[0]
    serialized = evidence.model_dump_json()

    assert evidence.sensitive is True
    assert "secret-user-id" not in serialized
    assert "private@example.com" not in serialized
    assert "campo_interno" not in serialized
    assert "identity_fields_removed" in result.warnings
    assert result.metadata["identity_in_evidence"] is False


def test_empty_history_is_explicit_evidence():
    output = {
        "possui_historico": False,
        "total": 0,
        "diagnosticos": [],
    }

    result = collect_evidence_from_tool_output(
        step=_history_step(),
        output=output,
    )

    assert result.status == EvidenceCollectionStatus.COLLECTED
    assert len(result.evidence) == 1
    assert result.evidence[0].metadata["empty_result"] is True
    assert result.evidence[0].references == ["financial_history:empty"]


def test_inconsistent_history_is_rejected():
    output = {
        "possui_historico": True,
        "total": 1,
        "diagnosticos": [],
    }

    result = collect_evidence_from_tool_output(
        step=_history_step(),
        output=output,
    )

    assert result.status == EvidenceCollectionStatus.REJECTED
    assert result.evidence == []
    assert "inconsistent_history_output" in result.warnings


def test_real_history_contract_contains_expected_fields():
    output_fields = set(ConsultarHistoricoFinanceiroOutput.model_fields)

    assert "diagnosticos" in output_fields
    assert "possui_historico" in output_fields


def test_tool_result_is_integrated_without_execution():
    fake_result = SimpleNamespace(
        call_id="call-formal-1",
        tool_name=("buscar_conhecimento_rag"),
        output={
            "resposta": "Resposta.",
            "fontes": ["fonte.md"],
            "contexto_recuperado": [("Reserva financeira para imprevistos.")],
        },
        duration_ms=25.0,
        error=None,
    )

    result = collect_evidence_from_tool_result(
        step=_knowledge_step(),
        tool_result=fake_result,
    )

    assert result.status == EvidenceCollectionStatus.COLLECTED
    assert result.evidence[0].metadata["call_id"] == "call-formal-1"


def test_tool_result_mismatch_is_rejected():
    fake_result = SimpleNamespace(
        call_id="call-wrong",
        tool_name=("consultar_historico_financeiro"),
        output={},
        duration_ms=1.0,
        error=None,
    )

    with pytest.raises(
        EvidenceCollectionError,
        match="não corresponde",
    ):
        collect_evidence_from_tool_result(
            step=_knowledge_step(),
            tool_result=fake_result,
        )


def test_unsupported_source_is_rejected():
    invalid_step = ResearchSubquery.model_construct(
        step_id="step_99_external",
        question="Consultar uma fonte externa.",
        source="external_web",
        tool_name="web_search",
        priority=50,
        required=True,
        top_k=4,
        max_results=5,
    )

    with pytest.raises(
        UnsupportedEvidenceSourceError,
        match="não possui",
    ):
        collect_evidence_from_tool_output(
            step=invalid_step,
            output={},
        )


def test_collection_contract_rejects_wrong_step():
    step = _knowledge_step()

    evidence = EvidenceItem(
        evidence_id=("ev_knowledge_00_0123456789abcdefabcd"),
        step_id="different_step",
        source=(ResearchSource.KNOWLEDGE_BASE),
        tool_name="buscar_conhecimento_rag",
        query=step.question,
        content="Conteúdo de evidência.",
        references=["fonte.md"],
        relevance_score=0.5,
        content_sha256=content_sha256("Conteúdo de evidência."),
        sensitive=False,
    )

    with pytest.raises(
        ValidationError,
        match="não pertence",
    ):
        EvidenceCollectionResult(
            step=step,
            status=(EvidenceCollectionStatus.COLLECTED),
            evidence=[evidence],
            source_schema="test",
            output_sha256=content_sha256("{}"),
            raw_item_count=1,
            selected_count=1,
        )


def test_lexical_relevance_is_bounded():
    score = lexical_relevance(
        "Como criar reserva de emergência?",
        ("Uma reserva de emergência ajuda a cobrir gastos inesperados."),
    )

    assert 0.0 <= score <= 1.0
    assert score > 0.0


def test_deduplication_preserves_best_evidence():
    step = _knowledge_step()
    content = "A reserva de emergência cobre imprevistos financeiros."

    low = EvidenceItem(
        evidence_id=("ev_knowledge_00_11111111111111111111"),
        step_id=step.step_id,
        source=step.source,
        tool_name=step.tool_name,
        query=step.question,
        content=content,
        references=["fonte-a.md"],
        relevance_score=0.2,
        content_sha256=content_sha256(content),
        sensitive=False,
    )

    high = EvidenceItem(
        evidence_id=("ev_knowledge_01_22222222222222222222"),
        step_id=step.step_id,
        source=step.source,
        tool_name=step.tool_name,
        query=step.question,
        content=content,
        references=["fonte-b.md"],
        relevance_score=0.9,
        content_sha256=content_sha256(content),
        sensitive=False,
    )

    selected = deduplicate_evidence([low, high])

    assert len(selected) == 1
    assert selected[0].evidence_id == high.evidence_id
    assert set(selected[0].references) == {
        "fonte-a.md",
        "fonte-b.md",
    }
    assert selected[0].metadata["deduplication_mode"] == "exact_content_merge"
    assert selected[0].metadata["merged_evidence_count"] == 2
