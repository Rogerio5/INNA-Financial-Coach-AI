"""
Recuperação semântica RAG da INNA com PostgreSQL e pgvector.

Responsabilidades:
- inferir categorias prioritárias da pergunta;
- gerar o vetor da pergunta por função injetada;
- consultar embeddings no pgvector;
- considerar somente documentos ativos;
- calcular similaridade aproximada;
- aplicar bônus de categoria;
- ordenar e retornar os melhores chunks.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from database.connection import cursor_postgres
except ImportError:
    from src.database.connection import cursor_postgres


EmbeddingGenerator = Callable[[str], list[float]]
ChunkClassifier = Callable[[str], str]


def inferir_categorias_pergunta(
    pergunta: str,
) -> list[str]:
    """
    Identifica categorias prioritárias com base na pergunta.
    """
    if not pergunta:
        return ["geral"]

    pergunta_lower = str(pergunta).lower()

    regras = [
        (
            [
                "pix",
                "transferência",
                "transferencia",
                "devolver",
                "valor estranho",
                "dinheiro estranho",
            ],
            ["pix", "seguranca"],
        ),
        (
            [
                "cartão",
                "cartao",
                "fatura",
                "parcelas",
                "parcelado",
                "limite",
                "crédito",
                "credito",
            ],
            [
                "cartao_credito",
                "organizacao_financeira",
                "dividas",
            ],
        ),
        (
            [
                "dívida",
                "divida",
                "dívidas",
                "dividas",
                "endividado",
                "juros",
                "negociar",
                "negociação",
                "negociacao",
            ],
            [
                "dividas",
                "organizacao_financeira",
                "cartao_credito",
            ],
        ),
        (
            [
                "reserva",
                "guardar",
                "poupar",
                "emergência",
                "emergencia",
            ],
            [
                "reserva_financeira",
                "organizacao_financeira",
            ],
        ),
        (
            [
                "organizar",
                "orçamento",
                "orcamento",
                "renda",
                "gastos",
                "controle financeiro",
            ],
            [
                "organizacao_financeira",
                "dividas",
                "reserva_financeira",
            ],
        ),
        (
            [
                "senha",
                "token",
                "golpe",
                "link",
                "sms",
                "segurança",
                "seguranca",
                "dados sensíveis",
                "dados sensiveis",
            ],
            ["seguranca", "pix"],
        ),
    ]

    categorias = []

    for termos, categorias_regra in regras:
        if any(termo in pergunta_lower for termo in termos):
            for categoria in categorias_regra:
                if categoria not in categorias:
                    categorias.append(categoria)

    return categorias or ["geral"]


def _validar_limite(limite: Any) -> int:
    """
    Mantém o limite entre 1 e 20 chunks.
    """
    try:
        limite_final = int(limite)
    except (TypeError, ValueError):
        limite_final = 5

    return max(1, min(limite_final, 20))


def _converter_embedding_pgvector(
    embedding: list[float],
) -> str:
    """
    Converte a lista numérica para a representação aceita pelo pgvector.
    """
    if not embedding:
        raise ValueError("O modelo não retornou um embedding válido.")

    valores = [str(float(valor)) for valor in embedding]

    return "[" + ",".join(valores) + "]"


def _calcular_similaridade(
    distancia: Any,
) -> float:
    """
    Converte distância do cosseno em similaridade aproximada.
    """
    try:
        similaridade = 1.0 - float(distancia)
    except (TypeError, ValueError):
        similaridade = 0.0

    return round(similaridade, 4)


def _calcular_score_rag(
    similaridade: float,
    prioridade_categoria: int,
    *,
    bonus_categoria: float = 0.08,
) -> float:
    """
    Combina similaridade semântica e bônus de categoria.
    """
    return round(
        float(similaridade) + (float(bonus_categoria) * int(prioridade_categoria)),
        4,
    )


def buscar_chunks_semanticos(
    pergunta: str,
    *,
    limite: int = 5,
    gerar_embedding: EmbeddingGenerator,
    classificar_chunk: ChunkClassifier,
    dimensoes: int = 3072,
    bonus_categoria: float = 0.08,
) -> dict:
    """
    Executa a recuperação semântica completa.

    As funções de embedding e classificação são recebidas como
    dependências para manter o serviço independente do dashboard.
    """
    pergunta = str(pergunta or "").strip()

    if not pergunta:
        return {
            "ok": False,
            "message": "Pergunta vazia.",
            "resultados": [],
        }

    if not callable(gerar_embedding):
        return {
            "ok": False,
            "message": "Função de geração de embedding inválida.",
            "resultados": [],
        }

    if not callable(classificar_chunk):
        return {
            "ok": False,
            "message": "Função de classificação de chunks inválida.",
            "resultados": [],
        }

    limite_final = _validar_limite(limite)
    limite_busca = max(limite_final * 4, 10)

    categorias_prioritarias = inferir_categorias_pergunta(pergunta)

    try:
        embedding_pergunta = gerar_embedding(pergunta)

        vetor_pgvector = _converter_embedding_pgvector(embedding_pergunta)

        sql = f"""
            SELECT
                ce.id,
                ce.documento_id,
                ce.chunk_id,
                ce.documento_origem,
                ce.chunk_index,
                ce.texto,
                ce.modelo_embedding,
                ce.embedding::halfvec({int(dimensoes)})
                    <=> %s::halfvec({int(dimensoes)})
                    AS distancia
            FROM chunks_embeddings_rag ce
            JOIN documentos_upload_rag du
                ON du.id = ce.documento_id
            WHERE COALESCE(du.ativo, TRUE) = TRUE
            ORDER BY
                ce.embedding::halfvec({int(dimensoes)})
                <=> %s::halfvec({int(dimensoes)})
            LIMIT %s;
        """

        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute(
                sql,
                (
                    vetor_pgvector,
                    vetor_pgvector,
                    limite_busca,
                ),
            )

            registros = cursor.fetchall()

        resultados = []

        for registro in registros:
            item = dict(registro)

            texto = item.get("texto") or ""
            distancia = float(item.get("distancia") or 0)

            categoria = classificar_chunk(texto) or "geral"

            similaridade = _calcular_similaridade(distancia)

            prioridade_categoria = int(categoria in categorias_prioritarias)

            item.update(
                {
                    "distancia": distancia,
                    "similaridade_aproximada": similaridade,
                    "categoria": categoria,
                    "categorias_prioritarias": (categorias_prioritarias),
                    "prioridade_categoria": (prioridade_categoria),
                    "score_rag": _calcular_score_rag(
                        similaridade,
                        prioridade_categoria,
                        bonus_categoria=bonus_categoria,
                    ),
                }
            )

            resultados.append(item)

        resultados = sorted(
            resultados,
            key=lambda item: (
                item.get(
                    "prioridade_categoria",
                    0,
                ),
                item.get(
                    "similaridade_aproximada",
                    0,
                ),
            ),
            reverse=True,
        )[:limite_final]

        categorias_texto = ", ".join(categorias_prioritarias)

        return {
            "ok": True,
            "message": (
                f"{len(resultados)} chunks encontrados. "
                f"Categorias priorizadas: {categorias_texto}."
            ),
            "resultados": resultados,
            "categorias_prioritarias": (categorias_prioritarias),
            "limite_utilizado": limite_final,
            "total_candidatos": len(registros),
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (f"Erro na busca semântica pgvector: {exc}"),
            "resultados": [],
        }


__all__ = [
    "inferir_categorias_pergunta",
    "buscar_chunks_semanticos",
]
