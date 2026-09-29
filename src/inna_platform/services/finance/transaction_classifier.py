from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import unicodedata
from typing import Iterable


AUTO_CLASSIFY_THRESHOLD = 0.90


@dataclass(frozen=True)
class TransactionClassification:
    category: str
    subcategory: str
    confidence: float
    strategy: str
    auto_assign: bool
    matched_terms: tuple[str, ...]
    needs_confirmation: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize(value: str) -> str:
    text = unicodedata.normalize(
        "NFKD",
        str(value or ""),
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.casefold()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _contains_any(
    text: str,
    terms: Iterable[str],
) -> tuple[str, ...]:

    found = []

    for term in terms:
        normalized_term = _normalize(term)

        if normalized_term in text:
            found.append(term)

    return tuple(found)


_RULES = (
    {
        "category": "Lazer",
        "subcategory": "Cinema",
        "confidence": 0.98,
        "terms": (
            "cinema",
            "cinemark",
            "cinepolis",
            "ingresso cinema",
        ),
    },
    {
        "category": "Alimentação",
        "subcategory": "Delivery",
        "confidence": 0.97,
        "terms": (
            "ifood",
            "i food",
            "rappi",
            "delivery",
        ),
    },
    {
        "category": "Alimentação",
        "subcategory": "Restaurante",
        "confidence": 0.94,
        "terms": (
            "restaurante",
            "churrascaria",
            "pizzaria",
            "hamburgueria",
        ),
    },
    {
        "category": "Alimentação",
        "subcategory": "Lanches",
        "confidence": 0.93,
        "terms": (
            "sorvete",
            "lanche",
            "salgado",
            "padaria",
            "cafeteria",
            "cafe",
        ),
    },
    {
        "category": "Alimentação",
        "subcategory": "Supermercado",
        "confidence": 0.95,
        "terms": (
            "supermercado",
            "mercado",
            "atacadao",
            "assai",
            "carrefour",
        ),
    },
    {
        "category": "Moradia",
        "subcategory": "Aluguel",
        "confidence": 0.97,
        "terms": (
            "aluguel",
            "locacao apartamento",
            "locacao casa",
        ),
    },
    {
        "category": "Moradia",
        "subcategory": "Contas da casa",
        "confidence": 0.93,
        "terms": (
            "energia",
            "conta de luz",
            "agua",
            "saneamento",
            "condominio",
            "gas",
        ),
    },
    {
        "category": "Transporte",
        "subcategory": "Aplicativo",
        "confidence": 0.97,
        "terms": (
            "uber",
            "99 app",
            "99pop",
            "cabify",
        ),
    },
    {
        "category": "Transporte",
        "subcategory": "Combustível",
        "confidence": 0.96,
        "terms": (
            "combustivel",
            "gasolina",
            "etanol",
            "posto",
        ),
    },
    {
        "category": "Transporte",
        "subcategory": "Transporte público",
        "confidence": 0.93,
        "terms": (
            "onibus",
            "metro",
            "passagem",
        ),
    },
    {
        "category": "Saúde",
        "subcategory": "Medicamentos",
        "confidence": 0.96,
        "terms": (
            "farmacia",
            "drogaria",
            "medicamento",
            "remedio",
        ),
    },
    {
        "category": "Saúde",
        "subcategory": "Consultas",
        "confidence": 0.95,
        "terms": (
            "consulta medica",
            "dentista",
            "psicologo",
            "clinica",
        ),
    },
    {
        "category": "Educação",
        "subcategory": "Cursos",
        "confidence": 0.95,
        "terms": (
            "curso",
            "faculdade",
            "mensalidade faculdade",
            "alura",
            "udemy",
        ),
    },
    {
        "category": "Lazer",
        "subcategory": "Streaming",
        "confidence": 0.97,
        "terms": (
            "netflix",
            "spotify",
            "disney plus",
            "prime video",
            "hbo",
        ),
    },
    {
        "category": "Compras",
        "subcategory": "E-commerce",
        "confidence": 0.94,
        "terms": (
            "shopee",
            "amazon",
            "mercado livre",
            "aliexpress",
        ),
    },
    {
        "category": "Dívidas",
        "subcategory": "Empréstimos",
        "confidence": 0.95,
        "terms": (
            "emprestimo",
            "financiamento",
            "parcela financiamento",
        ),
    },
    {
        "category": "Investimentos",
        "subcategory": "Aplicações",
        "confidence": 0.96,
        "terms": (
            "investimento",
            "tesouro direto",
            "cdb",
            "aplicacao",
        ),
    },
)


_INCOME_RULES = (
    {
        "category": "Receitas",
        "subcategory": "Salário",
        "confidence": 0.98,
        "terms": (
            "salario",
            "pagamento salario",
            "folha de pagamento",
        ),
    },
    {
        "category": "Receitas",
        "subcategory": "Renda extra",
        "confidence": 0.93,
        "terms": (
            "freelance",
            "renda extra",
            "comissao",
            "venda",
        ),
    },
)


def _is_income(
    transaction_type: str,
) -> bool:

    normalized = _normalize(
        transaction_type
    )

    return normalized in {
        "entrada",
        "receita",
        "income",
        "credito",
        "credit",
    }


def _context_override(
    text: str,
) -> TransactionClassification | None:
    """
    Regras em que o contexto completo é mais importante
    que palavras isoladas.
    """

    cinema_terms = {
        "cinema",
        "cinemark",
        "cinepolis",
    }

    food_terms = {
        "pipoca",
        "refrigerante",
        "refri",
        "lanche",
    }

    has_cinema = any(
        term in text
        for term in cinema_terms
    )

    has_food = any(
        term in text
        for term in food_terms
    )

    if has_cinema and has_food:

        return TransactionClassification(
            category="Lazer",
            subcategory="Cinema",
            confidence=0.99,
            strategy="context_rule",
            auto_assign=True,
            matched_terms=(
                "cinema",
                "alimentação no cinema",
            ),
            needs_confirmation=False,
        )

    return None


def classify_transaction(
    *,
    description: str,
    transaction_type: str = "Despesa",
    merchant: str = "",
    amount: float | None = None,
    threshold: float = AUTO_CLASSIFY_THRESHOLD,
) -> TransactionClassification:

    description = str(
        description or ""
    ).strip()

    merchant = str(
        merchant or ""
    ).strip()

    if not description and not merchant:

        return TransactionClassification(
            category="Outros",
            subcategory="Não identificado",
            confidence=0.20,
            strategy="insufficient_context",
            auto_assign=False,
            matched_terms=(),
            needs_confirmation=True,
        )

    text = _normalize(
        f"{description} {merchant}"
    )

    contextual = _context_override(
        text
    )

    if contextual is not None:
        return contextual

    rules = (
        _INCOME_RULES
        if _is_income(transaction_type)
        else _RULES
    )

    best = None

    for rule in rules:

        found = _contains_any(
            text,
            rule["terms"],
        )

        if not found:
            continue

        score = float(
            rule["confidence"]
        )

        # Pequeno reforço quando descrição e
        # estabelecimento apontam para o mesmo domínio.
        if len(found) > 1:
            score = min(
                0.99,
                score + 0.01,
            )

        candidate = (
            score,
            rule,
            found,
        )

        if (
            best is None
            or candidate[0] > best[0]
        ):
            best = candidate

    if best is None:

        return TransactionClassification(
            category=(
                "Receitas"
                if _is_income(transaction_type)
                else "Outros"
            ),
            subcategory="A confirmar",
            confidence=0.35,
            strategy="fallback",
            auto_assign=False,
            matched_terms=(),
            needs_confirmation=True,
        )

    score, rule, found = best

    auto_assign = (
        score >= threshold
    )

    return TransactionClassification(
        category=rule["category"],
        subcategory=rule["subcategory"],
        confidence=round(
            score,
            4,
        ),
        strategy="deterministic_rule",
        auto_assign=auto_assign,
        matched_terms=tuple(found),
        needs_confirmation=(
            not auto_assign
        ),
    )


def classifier_capabilities() -> dict:
    """
    Capacidades declaradas do TC1.

    semantic_embedding_ready=True significa que a
    arquitetura já possui um serviço de embedding
    de classificação, mas ele ainda não é acionado
    em toda transação no TC1.
    """

    return {
        "version": "tc1",
        "rules_enabled": True,
        "context_enabled": True,
        "confidence_gate_enabled": True,
        "semantic_embedding_ready": True,
        "semantic_embedding_enabled": False,
        "personal_learning_enabled": False,
        "feedback_dataset_enabled": False,
        "automatic_threshold": (
            AUTO_CLASSIFY_THRESHOLD
        ),
    }


__all__ = [
    "AUTO_CLASSIFY_THRESHOLD",
    "TransactionClassification",
    "classify_transaction",
    "classifier_capabilities",
]