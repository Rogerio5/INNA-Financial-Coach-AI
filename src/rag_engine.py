import hashlib
import math
import os
import re
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json


load_dotenv(".env")

RAG_VECTOR_DIM = int(os.getenv("INNA_RAG_VECTOR_DIM", "384"))
KNOWLEDGE_DIR = Path("data/knowledge_base")


def get_rag_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrada no ambiente.")

    return psycopg2.connect(database_url)


def ensure_rag_tables() -> None:
    conn = get_rag_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inna_knowledge_chunks (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            titulo TEXT NOT NULL,
            fonte TEXT NOT NULL,
            categoria TEXT DEFAULT 'educacao_financeira',
            idioma TEXT DEFAULT 'pt',
            chunk_index INTEGER DEFAULT 0,
            chunk_text TEXT NOT NULL,
            embedding JSONB NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb
        );
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inna_knowledge_chunks_fonte
        ON inna_knowledge_chunks(fonte);
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_inna_knowledge_chunks_idioma
        ON inna_knowledge_chunks(idioma);
        """
    )

    conn.commit()
    cur.close()
    conn.close()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-záàâãéèêíïóôõöúçñ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [token for token in normalized.split(" ") if len(token) >= 2]


def text_to_embedding(text: str, dim: int = RAG_VECTOR_DIM) -> list[float]:
    """
    Embedding local determinístico sem custo.
    Ele transforma texto em vetor numérico e permite busca semântica simples no Neon.
    Depois pode ser trocado por embeddings Gemini/OpenAI sem mudar a arquitetura.
    """
    vector = [0.0] * dim
    tokens = tokenize(text)

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dim
        sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [round(value / norm, 8) for value in vector]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if not vector_a or not vector_b:
        return 0.0

    size = min(len(vector_a), len(vector_b))

    dot = sum(vector_a[i] * vector_b[i] for i in range(size))
    norm_a = math.sqrt(sum(vector_a[i] * vector_a[i] for i in range(size)))
    norm_b = math.sqrt(sum(vector_b[i] * vector_b[i] for i in range(size)))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def split_text_into_chunks(text: str, max_chars: int = 900, overlap: int = 150) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            if current:
                chunks.append(current)

            if len(paragraph) > max_chars:
                start = 0
                while start < len(paragraph):
                    end = start + max_chars
                    chunks.append(paragraph[start:end].strip())
                    start = max(0, end - overlap)
            else:
                current = paragraph

    if current:
        chunks.append(current)

    return chunks


def ingest_knowledge_document(
    titulo: str,
    fonte: str,
    conteudo: str,
    categoria: str = "educacao_financeira",
    idioma: str = "pt",
) -> int:
    ensure_rag_tables()

    chunks = split_text_into_chunks(conteudo)

    conn = get_rag_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM inna_knowledge_chunks WHERE fonte = %s;", (fonte,))

    for index, chunk in enumerate(chunks):
        embedding = text_to_embedding(chunk)

        cur.execute(
            """
            INSERT INTO inna_knowledge_chunks (
                titulo,
                fonte,
                categoria,
                idioma,
                chunk_index,
                chunk_text,
                embedding,
                metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                titulo,
                fonte,
                categoria,
                idioma,
                index,
                chunk,
                Json(embedding),
                Json(
                    {
                        "tipo": "base_conhecimento",
                        "origem": "arquivo_markdown",
                        "vector_dim": RAG_VECTOR_DIM,
                    }
                ),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    return len(chunks)


def ingest_default_knowledge_base() -> dict[str, Any]:
    ensure_rag_tables()

    results = []

    if not KNOWLEDGE_DIR.exists():
        return {
            "status": "empty",
            "message": "Diretório data/knowledge_base não encontrado.",
            "documents": [],
        }

    files = sorted(
        list(KNOWLEDGE_DIR.glob("*.md"))
        + list(KNOWLEDGE_DIR.glob("*.txt"))
    )

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        chunks_count = ingest_knowledge_document(
            titulo=file_path.stem.replace("_", " ").title(),
            fonte=str(file_path).replace("\\", "/"),
            conteudo=content,
            categoria="educacao_financeira",
            idioma="pt",
        )

        results.append(
            {
                "fonte": str(file_path).replace("\\", "/"),
                "chunks": chunks_count,
            }
        )

    return {
        "status": "ok",
        "documents": results,
        "total_documents": len(results),
        "total_chunks": sum(item["chunks"] for item in results),
    }


def load_chunks(idioma: str = "pt") -> list[dict[str, Any]]:
    ensure_rag_tables()

    conn = get_rag_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            titulo,
            fonte,
            categoria,
            idioma,
            chunk_index,
            chunk_text,
            embedding,
            metadata
        FROM inna_knowledge_chunks
        WHERE idioma = %s OR idioma = 'pt'
        ORDER BY id ASC;
        """,
        (idioma,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    chunks = []

    for row in rows:
        chunks.append(
            {
                "id": row[0],
                "titulo": row[1],
                "fonte": row[2],
                "categoria": row[3],
                "idioma": row[4],
                "chunk_index": row[5],
                "chunk_text": row[6],
                "embedding": row[7],
                "metadata": row[8],
            }
        )

    return chunks


def search_knowledge_base(
    query: str,
    idioma: str = "pt",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    ensure_rag_tables()

    query_embedding = text_to_embedding(query)
    chunks = load_chunks(idioma=idioma)

    scored = []

    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])

        scored.append(
            {
                "score": round(float(score), 4),
                "id": chunk["id"],
                "titulo": chunk["titulo"],
                "fonte": chunk["fonte"],
                "categoria": chunk["categoria"],
                "idioma": chunk["idioma"],
                "chunk_index": chunk["chunk_index"],
                "trecho": chunk["chunk_text"],
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)

    return scored[: max(1, min(int(top_k or 5), 10))]


def answer_with_rag(
    pergunta: str,
    idioma: str = "pt",
    top_k: int = 4,
) -> dict[str, Any]:
    sources = search_knowledge_base(pergunta, idioma=idioma, top_k=top_k)

    if not sources:
        return {
            "resposta": (
                "Não encontrei informações suficientes na base de conhecimento da INNA. "
                "Posso responder apenas de forma educativa sobre organização financeira."
            ),
            "fontes": [],
            "modo": "rag_sem_fontes",
        }

    context = "\n\n".join(
        [
            f"Fonte: {source['fonte']} | Trecho: {source['trecho']}"
            for source in sources
        ]
    )

    resposta = (
        "Com base na base de conhecimento da INNA, a orientação educativa é:\n\n"
        f"{sources[0]['trecho']}\n\n"
        "Resumo prático:\n"
        "- organize seus dados financeiros;\n"
        "- compare renda, gastos, dívidas e reserva;\n"
        "- priorize ações simples e mensuráveis;\n"
        "- evite decisões financeiras arriscadas sem orientação profissional.\n\n"
        "Observação: esta resposta é educativa e não substitui consultoria financeira profissional."
    )

    return {
        "resposta": resposta,
        "fontes": sources,
        "contexto_usado": context,
        "modo": "rag_local_sem_custo",
    }
