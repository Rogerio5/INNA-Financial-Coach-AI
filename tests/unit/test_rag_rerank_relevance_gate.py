from src.rag_engine import rerank_knowledge_results


def _item(
    *,
    title: str,
    text: str,
    hybrid_score: float,
    text_score: float | None,
) -> dict:
    return {
        "titulo": title,
        "categoria": "educacao_financeira",
        "chunk_text": text,
        "score_hibrido": hybrid_score,
        "score_textual": text_score,
        "origem_busca": ["textual", "vetorial"],
        "modo_busca": "rag_hibrido_estruturado_3072_rrf",
    }


def test_debt_plural_theme_filters_weak_investment_chunk():
    results = [
        _item(
            title="Prioriza????o de d??vidas",
            text=(
                "D??vidas, juros, parcelas e cr??dito devem ser "
                "priorizados conforme custo e capacidade de pagamento."
            ),
            hybrid_score=0.0320,
            text_score=1.85,
        ),
        _item(
            title="Negocia????o de d??vidas",
            text=(
                "Negocie a d??vida, compare juros, parcelas e "
                "condi????es de cr??dito antes do acordo."
            ),
            hybrid_score=0.0315,
            text_score=1.85,
        ),
        _item(
            title="Princ??pios de investimentos",
            text=(
                "Antes de investir, verifique objetivo, prazo, "
                "liquidez e se existem d??vidas de custo elevado."
            ),
            hybrid_score=0.0310,
            text_score=1.0,
        ),
    ]

    reranked = rerank_knowledge_results(
        "como sair das d??vidas?",
        results,
        top_k=3,
    )

    assert len(reranked) == 2
    assert all(
        "invest" not in item["titulo"].lower()
        for item in reranked
    )
    assert reranked[0]["temas_pergunta"] == ["divida"]


def test_unknown_theme_preserves_top_k_compatibility():
    results = [
        _item(
            title=f"Documento {index}",
            text=f"Conte??do financeiro geral {index}",
            hybrid_score=0.04 - (index * 0.001),
            text_score=1.0,
        )
        for index in range(4)
    ]

    reranked = rerank_knowledge_results(
        "planejamento financeiro pessoal",
        results,
        top_k=3,
    )

    assert len(reranked) == 3


def test_strong_budget_third_result_is_retained():
    results = [
        _item(
            title="Or??amento mensal",
            text=(
                "Organize gastos, despesas fixas e vari??veis "
                "no or??amento mensal."
            ),
            hybrid_score=0.034,
            text_score=5.0,
        ),
        _item(
            title="Gastos fixos e vari??veis",
            text=(
                "Gastos fixos, gastos vari??veis e despesas "
                "devem ser classificados no or??amento."
            ),
            hybrid_score=0.033,
            text_score=5.0,
        ),
        _item(
            title="Provis??es do or??amento",
            text=(
                "Despesas e gastos vari??veis exigem provis??es "
                "no or??amento para evitar cr??dito."
            ),
            hybrid_score=0.032,
            text_score=4.8,
        ),
    ]

    reranked = rerank_knowledge_results(
        "como organizar gastos fixos e vari??veis?",
        results,
        top_k=3,
    )

    assert len(reranked) == 3
