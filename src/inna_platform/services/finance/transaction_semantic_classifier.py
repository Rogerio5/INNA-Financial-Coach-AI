from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math
from typing import Callable, Sequence

from src.inna_platform.services.finance.transaction_classifier import (
    classify_transaction,
)


# ============================================================
# CONFIGURACAO
# ============================================================

SEMANTIC_MIN_SIMILARITY = 0.60
SEMANTIC_MIN_MARGIN = 0.02
SEMANTIC_MAX_CONFIDENCE = 0.89


BASE_DIR = Path(__file__).resolve().parent

REGISTRY_PATH = (
    BASE_DIR
    / "data"
    / "transaction_category_embeddings.json"
)


# Categorias oficiais encontradas no Financeiro.
OFFICIAL_EXPENSE_CATEGORIES = (
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Compras",
    "Contas",
    "Assinaturas",
    "Dívidas",
    "Impostos",
    "Pets",
    "Seguros",
    "Outras despesas",
)


# ============================================================
# PROTOTIPOS SEMANTICOS
#
# Não são dados de usuário.
# São descrições genéricas usadas somente para representar
# semanticamente as categorias oficiais.
# ============================================================

CATEGORY_PROTOTYPES = {
    "Moradia": (
        "moradia aluguel condomínio casa apartamento "
        "manutenção residencial reforma imóvel"
    ),
    "Alimentação": (
        "alimentação supermercado restaurante almoço jantar "
        "lanche comida delivery refeição padaria mercado"
    ),
    "Transporte": (
        "transporte combustível gasolina etanol ônibus metrô "
        "aplicativo de corrida estacionamento pedágio viagem"
    ),
    "Saúde": (
        "saúde farmácia medicamento consulta médica dentista "
        "exames hospital clínica tratamento"
    ),
    "Educação": (
        "educação faculdade escola curso livros material "
        "didático mensalidade treinamento estudo"
    ),
    "Lazer": (
        "lazer cinema passeio viagem entretenimento show "
        "jogos diversão parque evento"
    ),
    "Compras": (
        "compras roupas calçados eletrônicos móveis acessórios "
        "loja ecommerce produtos pessoais"
    ),
    "Contas": (
        "contas água energia elétrica telefone internet gás "
        "serviços domésticos boleto residencial"
    ),
    "Assinaturas": (
        "assinaturas streaming software aplicativo serviço "
        "mensal recorrente plataforma digital"
    ),
    "Dívidas": (
        "dívidas empréstimo financiamento juros parcela "
        "acordo dívida crédito pagamento de dívida"
    ),
    "Impostos": (
        "impostos taxas tributos imposto de renda iptu ipva "
        "taxa pública contribuição tributária"
    ),
    "Pets": (
        "pets cachorro gato ração veterinário pet shop "
        "medicamento animal banho tosa"
    ),
    "Seguros": (
        "seguros seguro automóvel seguro residencial seguro "
        "vida proteção apólice assistência"
    ),
}


@dataclass(frozen=True)
class IntelligentTransactionClassification:
    category: str
    subcategory: str
    confidence: float
    strategy: str
    auto_assign: bool
    matched_terms: tuple[str, ...]
    needs_confirmation: bool

    semantic_attempted: bool
    semantic_used: bool
    semantic_provider_ok: bool

    semantic_similarity: float | None = None
    semantic_margin: float | None = None

    suggested_category: str | None = None
    second_category: str | None = None

    fallback_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _from_tc1(
    base,
    *,
    semantic_attempted: bool = False,
    semantic_provider_ok: bool = False,
    fallback_reason: str = "",
) -> IntelligentTransactionClassification:

    return IntelligentTransactionClassification(
        category=base.category,
        subcategory=base.subcategory,
        confidence=base.confidence,
        strategy=base.strategy,
        auto_assign=base.auto_assign,
        matched_terms=tuple(
            base.matched_terms
        ),
        needs_confirmation=(
            base.needs_confirmation
        ),
        semantic_attempted=semantic_attempted,
        semantic_used=False,
        semantic_provider_ok=(
            semantic_provider_ok
        ),
        fallback_reason=fallback_reason,
    )


def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot = sum(
        float(a) * float(b)
        for a, b
        in zip(
            vector_a,
            vector_b,
        )
    )

    norm_a = math.sqrt(
        sum(
            float(value) ** 2
            for value in vector_a
        )
    )

    norm_b = math.sqrt(
        sum(
            float(value) ** 2
            for value in vector_b
        )
    )

    if (
        norm_a <= 0.0
        or norm_b <= 0.0
    ):
        return 0.0

    return dot / (
        norm_a * norm_b
    )


def _load_registry() -> dict:

    if not REGISTRY_PATH.is_file():

        raise FileNotFoundError(
            "Registro semântico de categorias "
            "não encontrado."
        )

    payload = json.loads(
        REGISTRY_PATH.read_text(
            encoding="utf-8",
        )
    )

    categories = payload.get(
        "categories",
        {},
    )

    if not isinstance(
        categories,
        dict,
    ) or not categories:

        raise ValueError(
            "Registro semântico inválido."
        )

    return payload


def build_semantic_registry(
    *,
    embedding_provider: Callable[
        [str],
        list[float],
    ] | None = None,
) -> dict:

    if embedding_provider is None:

        from src.compartilhado.rag.embeddings.gemini import (
            DIMENSOES_EMBEDDING,
            MODELO_EMBEDDING,
            gerar_embedding_classificacao,
        )

        embedding_provider = (
            gerar_embedding_classificacao
        )

        model = MODELO_EMBEDDING
        dimensions = DIMENSOES_EMBEDDING

    else:

        model = "test-provider"
        dimensions = None

    categories: dict[
        str,
        list[float],
    ] = {}

    resolved_dimensions = dimensions

    for (
        category,
        prototype,
    ) in CATEGORY_PROTOTYPES.items():

        vector = embedding_provider(
            prototype
        )

        vector = [
            float(value)
            for value in vector
        ]

        if not vector:

            raise ValueError(
                "Embedding vazio para categoria: "
                f"{category}"
            )

        if resolved_dimensions is None:

            resolved_dimensions = len(
                vector
            )

        if (
            len(vector)
            != resolved_dimensions
        ):

            raise ValueError(
                "Dimensão de embedding "
                "inconsistente para categoria "
                f"{category}."
            )

        categories[
            category
        ] = vector

    payload = {
        "schema_version": "1.0",
        "classifier_version": "tc2",
        "model": model,
        "dimensions": (
            resolved_dimensions
        ),
        "semantic_auto_assign": False,
        "categories": categories,
    }

    REGISTRY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = (
        REGISTRY_PATH.with_suffix(
            ".json.tmp"
        )
    )

    temporary.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ),
        encoding="utf-8",
    )

    temporary.replace(
        REGISTRY_PATH
    )

    return payload


def classify_transaction_intelligent(
    *,
    description: str,
    transaction_type: str = "Despesa",
    merchant: str = "",
    amount: float | None = None,
    embedding_provider: Callable[
        [str],
        list[float],
    ] | None = None,
    registry: dict | None = None,
) -> IntelligentTransactionClassification:

    # ========================================================
    # PRIMEIRO: TC1
    # ========================================================

    base = classify_transaction(
        description=description,
        transaction_type=(
            transaction_type
        ),
        merchant=merchant,
        amount=amount,
    )

    # Uma decisão forte do TC1 não chama Gemini.
    if base.auto_assign:

        return _from_tc1(
            base,
            fallback_reason=(
                "tc1_high_confidence"
            ),
        )

    # TC2 semântico desta fase é voltado às
    # categorias oficiais de DESPESAS.
    if base.category == "Receitas":

        return _from_tc1(
            base,
            fallback_reason=(
                "semantic_expense_only"
            ),
        )

    # ========================================================
    # REGISTRO SEMANTICO
    # ========================================================

    try:

        semantic_registry = (
            registry
            if registry is not None
            else _load_registry()
        )

        categories = (
            semantic_registry[
                "categories"
            ]
        )

    except (
        FileNotFoundError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):

        return _from_tc1(
            base,
            semantic_attempted=False,
            semantic_provider_ok=False,
            fallback_reason=(
                "semantic_registry_unavailable"
            ),
        )

    # ========================================================
    # TEXTO ENVIADO AO EMBEDDING
    #
    # Valor financeiro NÃO é enviado.
    # ========================================================

    semantic_text = " ".join(
        part
        for part in (
            str(
                description
                or ""
            ).strip(),
            str(
                merchant
                or ""
            ).strip(),
        )
        if part
    )

    if not semantic_text:

        return _from_tc1(
            base,
            fallback_reason=(
                "semantic_text_empty"
            ),
        )

    # ========================================================
    # PROVIDER
    # ========================================================

    if embedding_provider is None:

        try:

            from src.compartilhado.rag.embeddings.gemini import (
                gerar_embedding_classificacao,
            )

            embedding_provider = (
                gerar_embedding_classificacao
            )

        except Exception:

            return _from_tc1(
                base,
                semantic_attempted=True,
                semantic_provider_ok=False,
                fallback_reason=(
                    "semantic_provider_import_failed"
                ),
            )

    try:

        query_vector = (
            embedding_provider(
                semantic_text
            )
        )

    except Exception:

        # Fail-safe:
        # nunca impede lançamento financeiro.
        return _from_tc1(
            base,
            semantic_attempted=True,
            semantic_provider_ok=False,
            fallback_reason=(
                "semantic_provider_unavailable"
            ),
        )

    # ========================================================
    # SIMILARIDADE
    # ========================================================

    scored: list[
        tuple[
            float,
            str,
        ]
    ] = []

    for (
        category,
        category_vector,
    ) in categories.items():

        similarity = cosine_similarity(
            query_vector,
            category_vector,
        )

        scored.append(
            (
                similarity,
                str(category),
            )
        )

    if not scored:

        return _from_tc1(
            base,
            semantic_attempted=True,
            semantic_provider_ok=True,
            fallback_reason=(
                "semantic_registry_empty"
            ),
        )

    scored.sort(
        reverse=True,
        key=lambda item: item[0],
    )

    best_similarity, best_category = (
        scored[0]
    )

    second_similarity = (
        scored[1][0]
        if len(scored) > 1
        else 0.0
    )

    second_category = (
        scored[1][1]
        if len(scored) > 1
        else None
    )

    margin = (
        best_similarity
        - second_similarity
    )

    # ========================================================
    # CONFIDENCE GATE SEMANTICO
    #
    # Nesta fase TC2:
    # semântica SUGERE, mas não auto-classifica.
    # ========================================================

    if (
        best_similarity
        < SEMANTIC_MIN_SIMILARITY
        or margin
        < SEMANTIC_MIN_MARGIN
    ):

        return IntelligentTransactionClassification(
            category="Outras despesas",
            subcategory="A confirmar",
            confidence=round(
                max(
                    0.35,
                    min(
                        SEMANTIC_MAX_CONFIDENCE,
                        best_similarity,
                    ),
                ),
                4,
            ),
            strategy=(
                "semantic_low_confidence"
            ),
            auto_assign=False,
            matched_terms=(),
            needs_confirmation=True,
            semantic_attempted=True,
            semantic_used=False,
            semantic_provider_ok=True,
            semantic_similarity=round(
                best_similarity,
                4,
            ),
            semantic_margin=round(
                margin,
                4,
            ),
            suggested_category=(
                best_category
            ),
            second_category=(
                second_category
            ),
            fallback_reason=(
                "semantic_confidence_gate"
            ),
        )

    return IntelligentTransactionClassification(
        category=best_category,
        subcategory="Sugestão semântica",
        confidence=round(
            min(
                SEMANTIC_MAX_CONFIDENCE,
                max(
                    0.40,
                    best_similarity,
                ),
            ),
            4,
        ),
        strategy=(
            "gemini_semantic_embedding"
        ),
        auto_assign=False,
        matched_terms=(),
        needs_confirmation=True,
        semantic_attempted=True,
        semantic_used=True,
        semantic_provider_ok=True,
        semantic_similarity=round(
            best_similarity,
            4,
        ),
        semantic_margin=round(
            margin,
            4,
        ),
        suggested_category=(
            best_category
        ),
        second_category=(
            second_category
        ),
        fallback_reason="",
    )


def semantic_classifier_capabilities() -> dict:

    registry_exists = (
        REGISTRY_PATH.is_file()
    )

    category_count = 0

    if registry_exists:

        try:

            payload = _load_registry()

            category_count = len(
                payload.get(
                    "categories",
                    {},
                )
            )

        except Exception:

            registry_exists = False

    return {
        "version": "tc2",
        "tc1_fallback": True,
        "gemini_embeddings": True,
        "semantic_registry_ready": (
            registry_exists
        ),
        "semantic_categories": (
            category_count
        ),
        "official_expense_categories": (
            len(
                OFFICIAL_EXPENSE_CATEGORIES
            )
        ),
        "semantic_auto_assign": False,
        "confirmation_required": True,
        "amount_sent_to_embedding": False,
        "database_write": False,
        "personal_learning": False,
        "minimum_similarity": (
            SEMANTIC_MIN_SIMILARITY
        ),
        "minimum_margin": (
            SEMANTIC_MIN_MARGIN
        ),
    }


__all__ = [
    "OFFICIAL_EXPENSE_CATEGORIES",
    "CATEGORY_PROTOTYPES",
    "SEMANTIC_MIN_SIMILARITY",
    "SEMANTIC_MIN_MARGIN",
    "IntelligentTransactionClassification",
    "cosine_similarity",
    "build_semantic_registry",
    "classify_transaction_intelligent",
    "semantic_classifier_capabilities",
]