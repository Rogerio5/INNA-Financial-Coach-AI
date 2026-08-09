import hashlib
import math
import os
import re
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json

try:
    from observability.llm_tracking import (
        executar_generate_content_observado,
    )
except ImportError:
    from src.observability.llm_tracking import (
        executar_generate_content_observado,
    )


from src.services.llm.model_registry import (
    LLMRole,
    get_model_for_role,
)

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
        # Embedding local antigo: mantido como fallback técnico.
        embedding = text_to_embedding(chunk)

        # Embedding profissional: caminho principal com Gemini + pgvector.
        embedding_profissional = generate_gemini_embedding(chunk)
        embedding_vector_sql = pgvector_to_sql(embedding_profissional) if embedding_profissional else None

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
                embedding_vector,
                metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s);
            """,
            (
                titulo,
                fonte,
                categoria,
                idioma,
                index,
                chunk,
                Json(embedding),
                embedding_vector_sql,
                Json(
                    {
                        "tipo": "base_conhecimento",
                        "origem": "arquivo_markdown",
                        "vector_dim_local": RAG_VECTOR_DIM,
                        "vector_dim_profissional": 768 if embedding_profissional else None,
                        "embedding_provider": "gemini" if embedding_profissional else "local_fallback",
                        "embedding_model": "gemini-embedding-001" if embedding_profissional else "local",
                    }
                ),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    return len(chunks)



def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> list[str]:
    """
    Divide textos grandes em partes menores para salvar na base RAG.
    Mantém um pequeno overlap para não perder contexto entre os chunks.
    """
    if not text:
        return []

    text = text.strip()

    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(text):
            break

    return chunks



def pgvector_to_sql(vector: list[float]) -> str:
    """
    Converte lista Python para formato aceito pelo pgvector:
    [0.1,0.2,0.3]
    """
    return "[" + ",".join(str(float(x)) for x in vector) + "]"


def generate_gemini_embedding(text: str) -> list[float] | None:
    """
    Gera embedding profissional com Gemini.
    Se falhar, retorna None para o RAG local assumir como fallback.
    """
    try:
        import os

        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return None

        client = genai.Client(api_key=api_key)

        response = client.models.embed_content(
            model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            ),
        )

        embedding = response.embeddings[0].values

        if not embedding:
            return None

        return [float(x) for x in embedding]

    except Exception:
        return None


def ingest_default_knowledge_base() -> dict[str, Any]:
    """
    Carrega todos os arquivos .md da pasta data/knowledge_base no RAG local.

    Exemplo:
    - financeiro_basico.md
    - faq_financeiro_inna.md
    """
    ensure_rag_tables()

    if not KNOWLEDGE_DIR.exists():
        return {
            "status": "error",
            "message": "Diretório data/knowledge_base não encontrado.",
            "documents": [],
            "total_documents": 0,
            "total_chunks": 0,
        }

    markdown_files = sorted(KNOWLEDGE_DIR.glob("*.md"))

    if not markdown_files:
        return {
            "status": "error",
            "message": "Nenhum arquivo .md encontrado em data/knowledge_base.",
            "documents": [],
            "total_documents": 0,
            "total_chunks": 0,
        }

    documents = []
    total_chunks = 0

    for file_path in markdown_files:
        conteudo = file_path.read_text(encoding="utf-8")

        chunks_count = ingest_knowledge_document(
            titulo=file_path.stem.replace("_", " ").title(),
            fonte=str(file_path).replace("\\", "/"),
            conteudo=conteudo,
            categoria="educacao_financeira",
            idioma="pt",
        )

        documents.append(
            {
                "fonte": str(file_path).replace("\\", "/"),
                "chunks": int(chunks_count),
            }
        )

        total_chunks += int(chunks_count)

    return {
        "status": "ok",
        "documents": documents,
        "total_documents": len(documents),
        "total_chunks": total_chunks,
    }



def load_chunks(idioma: str = "pt") -> list[dict[str, Any]]:
    """
    Carrega os chunks salvos no banco para busca semântica local.
    Retorna uma lista de dicionários com aliases seguros para texto/embedding.
    """
    ensure_rag_tables()

    conn = get_rag_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT *
            FROM inna_knowledge_chunks
            WHERE idioma = %s
            ORDER BY fonte, chunk_index, id;
            """,
            (idioma,),
        )

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

        chunks = []

        for row in rows:
            item = dict(zip(columns, row, strict=True))

            texto = (
                item.get("texto")
                or item.get("conteudo")
                or item.get("chunk_text")
                or item.get("trecho")
                or ""
            )

            embedding = (
                item.get("embedding")
                or item.get("embedding_json")
                or item.get("vetor")
                or []
            )

            item["texto"] = texto
            item["conteudo"] = texto
            item["chunk_text"] = texto

            item["embedding"] = embedding
            item["embedding_json"] = embedding
            item["vetor"] = embedding

            chunks.append(item)

        return chunks

    finally:
        cur.close()
        conn.close()



def search_knowledge_base_pgvector(
    query: str,
    idioma: str = "pt",
    top_k: int = 4,
    *,
    profiling: dict[str, float] | None = None,
) -> list[dict]:
    """
    Retrieval vetorial estruturado da INNA.

    Runtime oficial:
    - Gemini embedding 3072;
    - chunks_embeddings_rag;
    - documentos_upload_rag;
    - identidade documental nativa.
    """
    try:
        from services.embeddings.gemini import (
            gerar_embedding_consulta,
        )
        from services.rag.retrieval import (
            buscar_chunks_semanticos,
        )
    except ImportError:
        from src.services.embeddings.gemini import (
            gerar_embedding_consulta,
        )
        from src.services.rag.retrieval import (
            buscar_chunks_semanticos,
        )

    limite = max(
        int(top_k or 1),
        1,
    )

    vector_detail_timings: dict[
        str,
        float,
    ] = {}

    supports_deep_profiling = False

    try:
        import inspect

        semantic_signature = inspect.signature(
            buscar_chunks_semanticos
        )

        supports_deep_profiling = (
            "profiling"
            in semantic_signature.parameters
            or any(
                parameter.kind
                is inspect.Parameter.VAR_KEYWORD
                for parameter
                in semantic_signature.parameters.values()
            )
        )
    except (TypeError, ValueError):
        supports_deep_profiling = False

    if supports_deep_profiling:
        payload = buscar_chunks_semanticos(
            query,
            limite=max(
                limite * 4,
                10,
            ),
            gerar_embedding=gerar_embedding_consulta,
            classificar_chunk=lambda _: "",
            dimensoes=3072,
            profiling=vector_detail_timings,
        )
    else:
        payload = buscar_chunks_semanticos(
            query,
            limite=max(
                limite * 4,
                10,
            ),
            gerar_embedding=gerar_embedding_consulta,
            classificar_chunk=lambda _: "",
            dimensoes=3072,
        )

    if profiling is not None:
        profiling.update(
            vector_detail_timings
        )

    if not payload.get("ok"):
        return []

    requested_language = str(
        idioma or "pt"
    ).lower().split("-")[0]

    resultados: list[dict] = []

    for raw_item in (
        payload.get("resultados")
        or []
    ):
        item = dict(raw_item)

        result_language = str(
            item.get("idioma")
            or ""
        ).lower()

        if result_language:
            result_language = (
                result_language.split("-")[0]
            )

            if (
                result_language
                != requested_language
            ):
                continue

        texto = str(
            item.get("chunk_text")
            or item.get("texto")
            or ""
        )

        item["trecho"] = texto
        item["conteudo"] = texto

        item["score"] = float(
            item.get(
                "similaridade_aproximada"
            )
            or item.get("score")
            or 0
        )

        item["modo_busca"] = (
            "rag_estruturado_3072_vetorial"
        )

        resultados.append(item)

        if len(resultados) >= limite:
            break

    return resultados


def search_knowledge_base_text(
    query: str,
    idioma: str = "pt",
    top_k: int = 4,
) -> list[dict]:
    """
    Retrieval textual estruturado da INNA.

    Consulta exclusivamente a base documental
    estruturada de 3072 dimensões.
    """
    try:
        from services.rag.retrieval import (
            buscar_chunks_textuais,
        )
    except ImportError:
        from src.services.rag.retrieval import (
            buscar_chunks_textuais,
        )

    limite = max(
        int(top_k or 1),
        1,
    )

    payload = buscar_chunks_textuais(
        query,
        limite=max(
            limite * 4,
            10,
        ),
        classificar_chunk=lambda _: "",
    )

    if not payload.get("ok"):
        return []

    requested_language = str(
        idioma or "pt"
    ).lower().split("-")[0]

    resultados: list[dict] = []

    for raw_item in (
        payload.get("resultados")
        or []
    ):
        item = dict(raw_item)

        result_language = str(
            item.get("idioma")
            or ""
        ).lower()

        if result_language:
            result_language = (
                result_language.split("-")[0]
            )

            if (
                result_language
                != requested_language
            ):
                continue

        texto = str(
            item.get("chunk_text")
            or item.get("texto")
            or ""
        )

        item["trecho"] = texto
        item["conteudo"] = texto

        item["score"] = float(
            item.get("score_textual")
            or item.get("score")
            or 0
        )

        item["modo_busca"] = (
            "rag_estruturado_3072_textual"
        )

        resultados.append(item)

        if len(resultados) >= limite:
            break

    return resultados


def rerank_knowledge_results(query: str, results: list[dict], top_k: int = 4) -> list[dict]:
    """
    Reordena os chunks recuperados pelo RAG híbrido.

    Critérios:
    - score original do pgvector/textual;
    - bônus se veio de busca vetorial + textual;
    - bônus por palavras importantes da pergunta;
    - bônus por tema financeiro identificado;
    - penalização leve para chunks muito genéricos.
    """
    if not results:
        return []

    query_norm = normalize_text(query)

    stopwords = {
        "como", "posso", "comecar", "começar", "uma", "um", "para", "por",
        "que", "qual", "quais", "sobre", "minha", "meu", "me", "da", "de",
        "do", "das", "dos", "com", "sem", "isso", "esse", "essa", "estou",
        "esta", "aqui", "ali", "voce", "você"
    }

    termos_query = []

    for termo in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", query_norm):
        termo = normalize_text(termo).strip()

        if len(termo) < 3:
            continue

        if termo in stopwords:
            continue

        if termo not in termos_query:
            termos_query.append(termo)

    temas = {
        "reserva": ["reserva", "emergencia", "guardar", "poupar", "imprevisto"],
        "divida": ["divida", "dívida", "cartao", "cartão", "credito", "crédito", "parcelas", "juros"],
        "orcamento": ["orcamento", "orçamento", "gastos", "fixos", "variaveis", "variáveis", "despesas"],
        "renda": ["renda", "salario", "salário", "ganho", "recebo"],
    }

    temas_pergunta = []

    for tema, palavras in temas.items():
        if any(normalize_text(palavra) in query_norm for palavra in palavras):
            temas_pergunta.append(tema)

    reranked = []

    for item in results:
        texto = normalize_text(
            str(item.get("chunk_text") or item.get("texto") or item.get("trecho") or "")
        )
        titulo = normalize_text(str(item.get("titulo") or ""))
        categoria = normalize_text(str(item.get("categoria") or ""))

        score_base = float(item.get("score_hibrido") or item.get("score") or 0)

        origem = item.get("origem_busca") or []
        if isinstance(origem, str):
            origem = [origem]

        bonus_origem = 0.0

        if "vetorial" in origem and "textual" in origem:
            bonus_origem += 0.25
        elif "vetorial" in origem:
            bonus_origem += 0.10
        elif "textual" in origem:
            bonus_origem += 0.08

        termos_encontrados = 0

        for termo in termos_query:
            if termo in texto or termo in titulo or termo in categoria:
                termos_encontrados += 1

        bonus_termos = min(0.30, termos_encontrados * 0.06)

        bonus_tema = 0.0

        for tema in temas_pergunta:
            palavras_tema = temas.get(tema, [])

            if any(normalize_text(palavra) in texto for palavra in palavras_tema):
                bonus_tema += 0.12

        bonus_tema = min(0.30, bonus_tema)

        penalidade_generico = 0.0

        texto_generico = (
            "organize seus dados financeiros" in texto
            or "compare renda, gastos, dívidas e reserva" in texto
            or "ações simples e mensuráveis" in texto
        )

        if texto_generico and termos_encontrados <= 1:
            penalidade_generico = 0.20

        score_rerank = score_base + bonus_origem + bonus_termos + bonus_tema - penalidade_generico

        novo_item = dict(item)
        novo_item["score_rerank"] = round(score_rerank, 6)
        novo_item["termos_encontrados"] = termos_encontrados
        novo_item["temas_pergunta"] = temas_pergunta
        current_mode = str(
            novo_item.get("modo_busca")
            or "rag_hibrido_pgvector_text_neon"
        )

        if not current_mode.endswith(
            "_rerank"
        ):
            current_mode += "_rerank"

        novo_item["modo_busca"] = (
            current_mode
        )

        reranked.append(novo_item)

    reranked.sort(
        key=lambda item: float(item.get("score_rerank") or 0),
        reverse=True,
    )

    return reranked[:top_k]



def _sentence_window_boolean_setting(
    value: bool | None,
) -> bool:
    """
    Resolve a ativação sem alterar o padrão atual do RAG.
    """

    if value is not None:
        return bool(value)

    import os

    rendered = (
        str(
            os.getenv(
                "INNA_RAG_SENTENCE_WINDOW_ENABLED",
                "false",
            )
            or "false"
        )
        .strip()
        .lower()
    )

    return rendered in {
        "1",
        "true",
        "yes",
        "on",
        "sim",
    }


def _sentence_window_integer_setting(
    *,
    explicit_value: int | None,
    environment_name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    if explicit_value is not None:
        raw_value = explicit_value
    else:
        import os

        raw_value = os.getenv(
            environment_name,
            str(default),
        )

    try:
        parsed = int(raw_value)
    except (
        TypeError,
        ValueError,
    ):
        parsed = default

    return max(
        minimum,
        min(
            parsed,
            maximum,
        ),
    )


def _load_sentence_window_neighbor_chunks(
    item: dict,
    *,
    idioma: str,
    chunk_radius: int,
    connection=None,
) -> list[dict]:
    """
    Carrega chunks vizinhos do mesmo documento estruturado.

    Em qualquer falha, preserva somente o resultado original.
    """
    try:
        document_id = int(
            item.get(
                "documento_id",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        document_id = 0

    try:
        chunk_index = int(
            item.get(
                "chunk_index",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        chunk_index = 0

    if document_id <= 0:
        return [
            dict(item),
        ]

    minimum_index = max(
        0,
        chunk_index - chunk_radius,
    )

    maximum_index = (
        chunk_index
        + chunk_radius
    )

    normalized_language = normalize_text(idioma or "pt")

    language_pattern = (
        "pt%"
        if normalized_language.startswith("pt")
        else normalized_language + "%"
    )

    owns_connection = connection is None
    cursor = None

    try:
        if connection is None:
            connection = get_rag_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.id,
                c.documento_id,
                COALESCE(
                    c.metadata ->> 'document_title',
                    d.nome_original,
                    d.nome_logico,
                    'Documento INNA'
                ) AS titulo,
                COALESCE(
                    c.documento_origem,
                    d.caminho_upload,
                    d.nome_salvo,
                    d.nome_logico
                ) AS fonte,
                COALESCE(
                    c.metadata ->> 'area',
                    d.origem,
                    'conhecimento_inna'
                ) AS categoria,
                COALESCE(
                    c.metadata ->> 'language',
                    'pt-BR'
                ) AS idioma,
                c.chunk_index,
                c.texto AS chunk_text,
                c.metadata,
                d.nome_logico AS documento_key,
                c.chunk_id
            FROM public.chunks_embeddings_rag c
            JOIN public.documentos_upload_rag d
                ON d.id = c.documento_id
            WHERE c.documento_id = %s
              AND COALESCE(d.ativo, TRUE) IS TRUE
              AND LOWER(
                  COALESCE(
                      c.metadata ->> 'language',
                      'pt-BR'
                  )
              ) LIKE %s
              AND c.chunk_index
                  BETWEEN %s AND %s
            ORDER BY
                c.chunk_index ASC,
                c.id ASC;
            """,
            (
                document_id,
                language_pattern,
                minimum_index,
                maximum_index,
            ),
        )

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        neighbors = []

        for row in rows:
            neighbor = dict(
                zip(
                    columns,
                    row,
                    strict=True,
                )
            )

            text = str(
                neighbor.get("chunk_text")
                or ""
            )

            neighbor["texto"] = text
            neighbor["trecho"] = text
            neighbor["conteudo"] = text

            neighbors.append(neighbor)

        return neighbors or [
            dict(item),
        ]

    except Exception:
        return [
            dict(item),
        ]

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        if (
            owns_connection
            and connection is not None
        ):
            try:
                connection.close()
            except Exception:
                pass


def _sentence_window_allowed_document_keys() -> set[str]:
    """
    Resolve os documentos autorizados para Sentence Window.

    O padrão inclui somente temas aprovados nos testes
    de estabilidade. A lista pode ser alterada por variável
    de ambiente sem modificar código.
    """
    import os

    configured = str(
        os.getenv(
            "INNA_RAG_SENTENCE_WINDOW_ALLOWED_DOCUMENT_KEYS",
            (
                "inna-edu-reserva-002,"
                "inna-edu-orcamento-002"
            ),
        )
        or ""
    )

    return {
        item.strip()
        for item in configured.split(",")
        if item.strip()
    }


def _sentence_window_document_allowed(
    item: dict,
    *,
    allowed_document_keys: set[str],
) -> bool:
    """
    Verifica se o resultado pertence a um documento aprovado.
    """
    document_key = str(
        item.get(
            "documento_key",
            "",
        )
        or ""
    ).strip()

    return bool(
        document_key
        and document_key in allowed_document_keys
    )


def _apply_sentence_window_to_results(
    *,
    query: str,
    idioma: str,
    results: list[dict],
    window_size: int,
    chunk_radius: int,
    max_characters: int,
) -> list[dict]:
    """
    Aplica Sentence Window somente aos documentos aprovados.

    Resultados não autorizados preservam integralmente
    o chunk original, funcionando como fallback seguro.
    """
    try:
        from services.rag.sentence_window import (
            expand_result_with_sentence_window,
        )
    except ImportError:
        from src.services.rag.sentence_window import (
            expand_result_with_sentence_window,
        )

    allowed_document_keys = (
        _sentence_window_allowed_document_keys()
    )

    expanded_results: list[dict] = []

    shared_connection = None
    shared_connection_attempted = False

    supports_shared_connection = False

    try:
        import inspect

        loader_signature = inspect.signature(
            _load_sentence_window_neighbor_chunks
        )

        supports_shared_connection = (
            "connection"
            in loader_signature.parameters
            or any(
                parameter.kind
                is inspect.Parameter.VAR_KEYWORD
                for parameter
                in loader_signature.parameters.values()
            )
        )
    except (TypeError, ValueError):
        supports_shared_connection = False

    for item in results:
        original_item = dict(item)

        document_key = str(
            original_item.get(
                "documento_key",
                "",
            )
            or ""
        ).strip()

        if not _sentence_window_document_allowed(
            original_item,
            allowed_document_keys=allowed_document_keys,
        ):
            original_item["sentence_window_applied"] = False
            original_item["sentence_window_policy"] = (
                "selective_allowlist"
            )
            original_item["sentence_window_skip_reason"] = (
                "document_not_allowed"
            )
            original_item[
                "sentence_window_document_key"
            ] = document_key

            expanded_results.append(
                original_item
            )

            continue

        if (
            supports_shared_connection
            and not shared_connection_attempted
        ):
            shared_connection_attempted = True

            try:
                shared_connection = (
                    get_rag_connection()
                )
            except Exception:
                shared_connection = None

        if (
            supports_shared_connection
            and shared_connection is not None
        ):
            neighbor_chunks = (
                _load_sentence_window_neighbor_chunks(
                    original_item,
                    idioma=idioma,
                    chunk_radius=chunk_radius,
                    connection=shared_connection,
                )
            )
        else:
            neighbor_chunks = (
                _load_sentence_window_neighbor_chunks(
                    original_item,
                    idioma=idioma,
                    chunk_radius=chunk_radius,
                )
            )

        try:
            expanded_item = (
                expand_result_with_sentence_window(
                    query=query,
                    result=original_item,
                    chunks=neighbor_chunks,
                    window_size=window_size,
                    max_characters=max_characters,
                )
            )
        except Exception:
            expanded_item = dict(
                original_item
            )

            expanded_item["sentence_window_applied"] = False
            expanded_item["sentence_window_skip_reason"] = (
                "expansion_failed"
            )

        expanded_item["sentence_window_policy"] = (
            "selective_allowlist"
        )
        expanded_item[
            "sentence_window_document_key"
        ] = document_key

        if expanded_item.get(
            "sentence_window_applied"
        ):
            expanded_item["sentence_window_skip_reason"] = None
        else:
            expanded_item.setdefault(
                "sentence_window_skip_reason",
                "empty_window",
            )

        expanded_results.append(
            expanded_item
        )

    if shared_connection is not None:
        try:
            shared_connection.close()
        except Exception:
            pass

    return expanded_results


def search_knowledge_base_hybrid(
    query: str,
    idioma: str = "pt",
    top_k: int = 4,
    *,
    sentence_window_enabled: bool | None = None,
    sentence_window_size: int | None = None,
    sentence_window_chunk_radius: int | None = None,
    profiling: dict[str, float] | None = None,
) -> list[dict]:
    """
    Hybrid RAG estruturado 3072 da INNA.

    Combina retrieval vetorial e textual com
    Reciprocal Rank Fusion (RRF), evitando comparar
    diretamente scores de escalas diferentes.
    """
    import time

    retrieval_started = time.perf_counter()

    candidate_limit = max(
        int(top_k or 1),
        6,
    )

    vector_started = time.perf_counter()

    vector_detail_timings: dict[
        str,
        float,
    ] = {}

    supports_vector_profiling = False

    try:
        import inspect

        vector_signature = inspect.signature(
            search_knowledge_base_pgvector
        )

        supports_vector_profiling = (
            "profiling"
            in vector_signature.parameters
            or any(
                parameter.kind
                is inspect.Parameter.VAR_KEYWORD
                for parameter
                in vector_signature.parameters.values()
            )
        )
    except (TypeError, ValueError):
        supports_vector_profiling = False

    if supports_vector_profiling:
        vector_results = (
            search_knowledge_base_pgvector(
                query,
                idioma=idioma,
                top_k=candidate_limit,
                profiling=vector_detail_timings,
            )
        )
    else:
        vector_results = (
            search_knowledge_base_pgvector(
                query,
                idioma=idioma,
                top_k=candidate_limit,
            )
        )

    vector_retrieval_ms = round(
        (time.perf_counter() - vector_started)
        * 1000,
        2,
    )

    if profiling is not None:
        profiling.update(
            vector_detail_timings
        )

    text_started = time.perf_counter()

    text_results = (
        search_knowledge_base_text(
            query,
            idioma=idioma,
            top_k=candidate_limit,
        )
    )

    text_retrieval_ms = round(
        (time.perf_counter() - text_started)
        * 1000,
        2,
    )

    rrf_started = time.perf_counter()

    rrf_constant = 60.0

    combinados: dict[
        tuple,
        dict,
    ] = {}

    def result_key(
        item: dict,
    ) -> tuple:
        document_id = item.get(
            "documento_id"
        )

        chunk_id = item.get(
            "chunk_id"
        )

        if (
            document_id is not None
            and chunk_id
        ):
            return (
                "structured",
                document_id,
                str(chunk_id),
            )

        return (
            "legacy-compatible-id",
            item.get("id"),
        )

    def register_ranked_results(
        items: list[dict],
        origin: str,
    ) -> None:
        for rank, raw_item in enumerate(
            items,
            start=1,
        ):
            item = dict(raw_item)
            key = result_key(item)

            contribution = (
                1.0
                / (
                    rrf_constant
                    + float(rank)
                )
            )

            if key not in combinados:
                item["origem_busca"] = []
                item["score_hibrido"] = 0.0

                combinados[key] = item

            current = combinados[key]

            origins = list(
                current.get(
                    "origem_busca"
                )
                or []
            )

            if origin not in origins:
                origins.append(origin)

            current["origem_busca"] = sorted(
                origins
            )

            current["score_hibrido"] = (
                float(
                    current.get(
                        "score_hibrido"
                    )
                    or 0
                )
                + contribution
            )

            current[
                f"rrf_rank_{origin}"
            ] = rank

            current[
                f"rrf_contribution_{origin}"
            ] = round(
                contribution,
                8,
            )

            if (
                origin == "textual"
                and item.get(
                    "score_textual"
                )
                is not None
            ):
                current["score_textual"] = (
                    item.get(
                        "score_textual"
                    )
                )

            if (
                origin == "vetorial"
                and item.get(
                    "similaridade_aproximada"
                )
                is not None
            ):
                current[
                    "similaridade_aproximada"
                ] = item.get(
                    "similaridade_aproximada"
                )

            current["modo_busca"] = (
                "rag_hibrido_"
                "estruturado_3072_rrf"
            )

    register_ranked_results(
        vector_results,
        "vetorial",
    )

    register_ranked_results(
        text_results,
        "textual",
    )

    results = sorted(
        combinados.values(),
        key=lambda item: float(
            item.get("score_hibrido")
            or 0
        ),
        reverse=True,
    )

    rrf_ms = round(
        (time.perf_counter() - rrf_started)
        * 1000,
        2,
    )

    rerank_started = time.perf_counter()

    reranked_results = (
        rerank_knowledge_results(
            query,
            results,
            top_k=top_k,
        )
    )

    rerank_ms = round(
        (time.perf_counter() - rerank_started)
        * 1000,
        2,
    )

    if not _sentence_window_boolean_setting(
        sentence_window_enabled
    ):
        sentence_window_ms = 0.0

        retrieval_total_ms = round(
            (
                time.perf_counter()
                - retrieval_started
            )
            * 1000,
            2,
        )

        if profiling is not None:
            profiling.update(
                {
                    "vector_retrieval_ms": (
                        vector_retrieval_ms
                    ),
                    "text_retrieval_ms": (
                        text_retrieval_ms
                    ),
                    "rrf_ms": rrf_ms,
                    "rerank_ms": rerank_ms,
                    "sentence_window_ms": (
                        sentence_window_ms
                    ),
                    "retrieval_total_ms": (
                        retrieval_total_ms
                    ),
                }
            )

        return reranked_results

    resolved_window_size = (
        _sentence_window_integer_setting(
            explicit_value=(
                sentence_window_size
            ),
            environment_name=(
                "INNA_RAG_"
                "SENTENCE_WINDOW_SIZE"
            ),
            default=2,
            minimum=0,
            maximum=8,
        )
    )

    resolved_chunk_radius = (
        _sentence_window_integer_setting(
            explicit_value=(
                sentence_window_chunk_radius
            ),
            environment_name=(
                "INNA_RAG_SENTENCE_WINDOW_"
                "CHUNK_RADIUS"
            ),
            default=1,
            minimum=0,
            maximum=4,
        )
    )

    resolved_max_characters = (
        _sentence_window_integer_setting(
            explicit_value=None,
            environment_name=(
                "INNA_RAG_SENTENCE_WINDOW_"
                "MAX_CHARACTERS"
            ),
            default=4000,
            minimum=300,
            maximum=12000,
        )
    )

    sentence_window_started = (
        time.perf_counter()
    )

    final_results = (
        _apply_sentence_window_to_results(
            query=query,
            idioma=idioma,
            results=reranked_results,
            window_size=resolved_window_size,
            chunk_radius=resolved_chunk_radius,
            max_characters=(
                resolved_max_characters
            ),
        )
    )

    sentence_window_ms = round(
        (
            time.perf_counter()
            - sentence_window_started
        )
        * 1000,
        2,
    )

    retrieval_total_ms = round(
        (
            time.perf_counter()
            - retrieval_started
        )
        * 1000,
        2,
    )

    if profiling is not None:
        profiling.update(
            {
                "vector_retrieval_ms": (
                    vector_retrieval_ms
                ),
                "text_retrieval_ms": (
                    text_retrieval_ms
                ),
                "rrf_ms": rrf_ms,
                "rerank_ms": rerank_ms,
                "sentence_window_ms": (
                    sentence_window_ms
                ),
                "retrieval_total_ms": (
                    retrieval_total_ms
                ),
            }
        )

    return final_results


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



def extrair_valor_para_guardar(pergunta: str) -> float | None:
    texto = normalize_text(pergunta)

    # Palavras simples que pessoas podem usar:
    # "guardo 100", "sobra 100", "consigo guardar 100",
    # "dá pra guardar 100", "posso juntar 100", "separo 100".
    padroes = [
        r"consigo\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"consigo\s+juntar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"consigo\s+separar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"posso\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"posso\s+juntar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"posso\s+separar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"da\s+pra\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"da\s+para\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"daria\s+pra\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"daria\s+para\s+guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"eu\s+guardo\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"guardo\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"guardar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"eu\s+junto\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"junto\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"juntar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"eu\s+separo\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"separo\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"separar\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"me\s+sobra\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"sobra\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"sobrou\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"fica\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"resta\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",

        r"tenho\s+livre\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"dinheiro\s+livre\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
        r"livre\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            valor = match.group(1).replace(".", "").replace(",", ".")
            try:
                return float(valor)
            except Exception:
                return None

    return None



def extrair_valor_por_palavras(pergunta: str, palavras: list[str]) -> float | None:
    texto = normalize_text(pergunta)

    for palavra in palavras:
        padrao = rf"{palavra}\s*(?:de|do|da|é|e|:)?\s*(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)"
        match = re.search(padrao, texto)

        if match:
            valor = match.group(1).replace(".", "").replace(",", ".")
            try:
                return float(valor)
            except Exception:
                return None

    return None


def extrair_renda_mensal(pergunta: str) -> float | None:
    return extrair_valor_por_palavras(
        pergunta,
        ["ganho", "recebo", "salario", "renda", "entra", "aposentadoria", "beneficio", "pensao"],
    )


def extrair_gasto_mensal(pergunta: str) -> float | None:
    return extrair_valor_por_palavras(
        pergunta,
        ["gasto", "gastei", "pago", "conta", "contas", "despesa", "despesas", "custos"],
    )


def formatar_reais_simples(valor: float) -> str:
    if valor >= 1000:
        texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        texto = f"{valor:.2f}".replace(".", ",")

    if texto.endswith(",00"):
        texto = texto[:-3]

    return f"R$ {texto}"



def detectar_intencao_continuacao(pergunta: str) -> str:
    texto = normalize_text(pergunta)

    confirmou = any(p in texto for p in [
        "sim", "quero", "pode", "mostre", "me mostre", "continue", "ok", "vamos", "claro"
    ])

    negou = any(p in texto for p in [
        "nao", "não", "cancelar", "pare", "agora nao", "agora não", "depois"
    ])

    if negou:
        return "cancelar"

    if any(p in texto for p in [
        "nao consigo", "não consigo", "muito alto", "apertado", "pesado",
        "guardar menos", "valor menor", "diminuir", "reduzir valor"
    ]):
        return "ajustar_para_menos"

    if any(p in texto for p in [
        "guardar mais", "valor maior", "aumentar", "consigo mais"
    ]):
        return "ajustar_para_mais"

    if any(p in texto for p in [
        "divida", "dívida", "devo", "parcelas", "emprestimo", "empréstimo",
        "cartao", "cartão", "financiamento"
    ]):
        return "dividas"

    if any(p in texto for p in [
        "gasto", "gastos", "conta", "contas", "mercado", "aluguel",
        "luz", "agua", "internet", "transporte", "organizar"
    ]):
        return "organizar_gastos"

    if any(p in texto for p in [
        "reserva", "guardar dinheiro", "juntar dinheiro", "emergencia", "emergência"
    ]):
        return "reserva"

    if any(p in texto for p in [
        "esta semana", "desta semana", "semana", "7 dias"
    ]) and confirmou:
        return "meta_semana"

    if any(p in texto for p in [
        "mes inteiro", "mês inteiro", "30 dias", "mes", "mês", "4 semanas"
    ]) and confirmou:
        return "meta_mes"

    if confirmou and any(p in texto for p in [
        "meta simples para esta semana", "esta semana", "semana"
    ]):
        return "meta_semana"

    if confirmou and any(p in texto for p in [
        "meta no mes inteiro", "meta no mês inteiro", "mes inteiro",
        "mês inteiro", "30 dias"
    ]):
        return "meta_mes"

    if confirmou:
        return "confirmacao"

    return "pergunta_normal"


def resposta_cancelar_simples() -> dict:
    return {
        "resposta": """Tudo bem. Podemos parar por aqui.

Quando quiser continuar, você pode perguntar sobre:
- reserva;
- dívidas;
- gastos;
- meta da semana;
- meta de 30 dias.

A INNA está aqui para orientar de forma simples, no seu ritmo.""",
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }


def resposta_ajustar_valor(menor: bool = True) -> dict:
    if menor:
        resposta = """Tudo bem. Vamos deixar mais leve.

Quando o valor fica pesado, o melhor é começar menor.

Você pode fazer assim:

1. Escolha um valor que não aperte seu mês.
2. Pode começar com R$ 10, R$ 20 ou R$ 50 por semana.
3. Guarde primeiro o que for possível.
4. Quando melhorar, aumente aos poucos.

Me diga um valor menor que cabe no seu bolso, por exemplo:
"consigo guardar 50 por mês"."""
    else:
        resposta = """Ótimo. Se você consegue guardar mais, vamos ajustar com cuidado.

Faça assim:

1. Veja se esse valor maior não vai apertar suas contas.
2. Separe primeiro o valor das contas importantes.
3. Depois aumente a reserva aos poucos.
4. Não precisa subir tudo de uma vez.

Me diga o novo valor, por exemplo:
"posso guardar 300 por mês"."""

    return {
        "resposta": resposta,
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }


def resposta_meta_semana_simples() -> dict:
    return {
        "resposta": """Claro. Vamos fazer só a meta desta semana.

Meta da semana:
Guardar um valor pequeno e possível, sem apertar demais.

O que fazer nesta semana:

1. Escolha um valor que caiba no seu bolso.
2. Separe esse valor assim que receber ou assim que sobrar.
3. Não use esse dinheiro para compras comuns.
4. No fim da semana, veja se conseguiu manter o valor guardado.

Orientação simples:
Se não conseguir guardar tudo, guarde uma parte. O importante é começar.

Depois você pode me dizer quanto conseguiu guardar, e eu te ajudo a ajustar.""",
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }


def resposta_meta_mes_simples() -> dict:
    return {
        "resposta": """Claro. Vou mostrar uma ideia simples para o mês inteiro.

Meta de 30 dias:
Guardar um valor pequeno toda semana, sem apertar demais.

Plano simples de 4 semanas:

1. Semana 1:
Guarde o primeiro valor da semana. O importante é começar.

2. Semana 2:
Tente repetir o mesmo valor da semana anterior.

3. Semana 3:
Veja se sobrou um pouco mais. Se não sobrou, mantenha o mesmo valor.

4. Semana 4:
Some tudo que conseguiu guardar e veja seu progresso.

Orientação simples:
Se uma semana apertar, guarde menos. O importante é não desistir.

Depois você pode me dizer se quer uma meta menor ou maior.""",
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }


def resposta_dividas_simples() -> dict:
    return {
        "resposta": """Vamos por partes. Para olhar as dívidas de forma simples:

1. Anote todas as dívidas ou parcelas.
2. Coloque o valor de cada uma.
3. Veja qual pesa mais no mês.
4. Evite fazer novas dívidas enquanto organiza as atuais.

O que fazer hoje:
Anote quanto você paga por mês em dívidas ou parcelas.

Depois me diga aqui no chat, por exemplo:
"pago 600 de dívida por mês".

Aí eu te ajudo a organizar o próximo passo.""",
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }


def resposta_organizar_gastos_simples() -> dict:
    return {
        "resposta": """Vamos organizar seus gastos de forma simples.

Separe em 3 grupos:

1. Contas fixas:
aluguel, luz, água, internet, telefone.

2. Gastos do dia a dia:
mercado, transporte, comida fora, compras pequenas.

3. Dívidas ou parcelas:
cartão, empréstimo, financiamento ou compras parceladas.

O que fazer hoje:
Anote quanto vai para cada grupo.

Depois me diga, por exemplo:
"gasto 1200 em contas, 800 em mercado e 400 em parcelas".

Aí eu te ajudo a enxergar onde pode melhorar.""",
        "fontes": [],
        "contexto_usado": "",
        "modo": "rag_local_sem_custo",
    }





def answer_security_financeira(pergunta: str, modo_base: str = "rag_hibrido_pgvector_text_neon_rerank") -> dict | None:
    pergunta_norm = pergunta.lower()

    termos_seguranca = [
        "golpe", "golpes", "fraude", "fraudes", "pix", "link", "sms",
        "whatsapp", "senha", "token", "cvv", "código", "codigo",
        "compra desconhecida", "compra não reconhecida", "compra nao reconhecida",
        "não reconheço", "nao reconheco", "não reconheci",
        "nao reconheci", "cartão clonado", "cartao clonado",
        "bloqueada", "bloqueado", "conta do banco"
    ]

    if not any(termo in pergunta_norm for termo in termos_seguranca):
        return None

    if "pix" in pergunta_norm:
        resposta = (
            "Se você fez um PIX errado, o primeiro passo é conferir o comprovante, "
            "verificar o nome de quem recebeu e entrar em contato com seu banco pelos canais oficiais o quanto antes. "
            "Se for possível, tente falar com o recebedor de forma segura. "
            "Não aceite ajuda de desconhecidos por WhatsApp, SMS ou redes sociais e nunca informe senha, token ou código de segurança. "
            "A INNA orienta de forma educativa e não consegue recuperar PIX nem prometer estorno."
        )
    elif "código" in pergunta_norm or "codigo" in pergunta_norm or "token" in pergunta_norm or "senha" in pergunta_norm or "whatsapp" in pergunta_norm:
        resposta = (
            "Não envie código do banco, senha, token ou código SMS pelo WhatsApp. "
            "Esse tipo de informação pode permitir acesso à sua conta ou autorizar transações. "
            "Bancos não costumam pedir esse tipo de dado por mensagem. "
            "Entre no aplicativo oficial do banco ou fale com a central oficial para verificar a situação. "
            "Se você já informou algum dado, troque as senhas, bloqueie cartões se necessário e procure o banco imediatamente pelos canais oficiais. A INNA orienta de forma educativa e preventiva."
        )
    elif "link" in pergunta_norm or "bloqueada" in pergunta_norm or "bloqueado" in pergunta_norm:
        resposta = (
            "Se você recebeu um link dizendo que sua conta do banco será bloqueada, desconfie. "
            "Não clique no link e não informe senha, token, código SMS, CVV ou número completo do cartão. "
            "Acesse apenas o aplicativo oficial do banco ou entre em contato pelos canais oficiais. "
            "Mensagens com urgência, ameaça de bloqueio ou pedido de dados costumam ser sinais de golpe. A INNA orienta de forma educativa e preventiva."
        )
    elif (
        ("compra" in pergunta_norm and (
            "não reconheço" in pergunta_norm
            or "nao reconheco" in pergunta_norm
            or "não reconheci" in pergunta_norm
            or "nao reconheci" in pergunta_norm
            or "desconhecida" in pergunta_norm
            or "suspeita" in pergunta_norm
        ))
        or "cartão clonado" in pergunta_norm
        or "cartao clonado" in pergunta_norm
    ):
        resposta = (
            "Se apareceu uma compra no cartão que você não reconhece, confira primeiro se o nome do estabelecimento é familiar "
            "ou se alguém autorizado usou o cartão. "
            "Se continuar suspeito, bloqueie temporariamente o cartão pelo aplicativo oficial do banco e entre em contato com o banco pelos canais oficiais. "
            "Não informe senha, código SMS, token, CVV ou número completo do cartão para terceiros. "
            "A INNA orienta de forma educativa, não confirma fraude real e não promete estorno."
        )
    else:
        resposta = (
            "Para se proteger de golpes financeiros, evite clicar em links suspeitos, confira os dados antes de fazer PIX "
            "e nunca informe senha, token, código SMS, CVV ou número completo do cartão. "
            "Use apenas aplicativos oficiais do banco, ative notificações de compra e procure os canais oficiais se algo parecer estranho. "
            "A INNA orienta de forma educativa e preventiva."
        )

    return {
        "resposta": resposta,
        "modo": f"{modo_base}_seguranca_financeira",
        "fontes": [
            {
                "titulo": "Segurança Financeira",
                "fonte": "data/knowledge_base/seguranca_financeira.md",
                "score": None,
            }
        ],
    }


def generate_gemini_rag_answer(pergunta: str, contexto: str, idioma: str = "pt") -> str | None:
    """
    Gera resposta final usando Gemini + contexto recuperado pelo RAG.
    Se falhar, retorna None para manter o fallback local.
    """
    try:
        import os

        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return None

        client = genai.Client(api_key=api_key)

        idioma_normalizado = str(
            idioma or "pt"
        ).strip().lower().replace("-", "_")

        aliases_idioma = {
            "pt_br": "pt",
            "en": "en_us",
            "en_us": "en_us",
            "en_gb": "en_gb",
            "es_es": "es",
            "fr_fr": "fr",
            "de_de": "de",
            "it_it": "it",
            "ro_ro": "ro",
            "uk": "ua",
            "uk_ua": "ua",
            "ru_ru": "ru",
            "ar": "sa",
            "ar_sa": "sa",
            "de_ch": "ch",
        }

        idioma_normalizado = aliases_idioma.get(
            idioma_normalizado,
            idioma_normalizado,
        )

        nomes_idioma = {
            "pt": "português do Brasil",
            "en_us": "inglês dos Estados Unidos",
            "en_gb": "inglês do Reino Unido",
            "es": "espanhol",
            "fr": "francês",
            "de": "alemão",
            "it": "italiano",
            "ro": "romeno",
            "ua": "ucraniano",
            "ru": "russo",
            "sa": "árabe",
            "ch": "alemão da Suíça",
        }

        idioma_resposta = nomes_idioma.get(
            idioma_normalizado,
            nomes_idioma["pt"],
        )

        prompt = f"""
Você é a INNA, uma educadora financeira com IA.

Seu papel é orientar de forma simples, acolhedora e educativa.
Você NÃO deve recomendar investimentos, produtos financeiros ou decisões obrigatórias.
Você NÃO substitui consultoria financeira, contábil, jurídica ou bancária profissional.

Use uma linguagem fácil para trabalhador, idoso, leigo e pessoa com pouco estudo.
Explique de forma prática, curta e humana.
Prefira frases como:
- "vou te orientar"
- "vamos por partes"
- "de forma simples"
- "um caminho possível é"
- "o importante é começar"

Evite:
- linguagem difícil;
- prometer resultado;
- mandar a pessoa fazer algo;
- recomendar investimento;
- parecer banco, corretora ou consultor.

Contexto recuperado da base da INNA:
{contexto}

Pergunta do usuário:
{pergunta}

Responda obrigatoriamente em {idioma_resposta}.
Não misture o idioma solicitado com português ou inglês,
exceto em nomes técnicos, marcas, códigos e identificadores.

A resposta deve:
1. Ser simples e clara.
2. Usar o contexto recuperado quando fizer sentido.
3. Mostrar passos práticos.
4. Manter tom educativo.
5. Não inventar dados que o usuário não informou.
6. Preserve a moeda apresentada pelo usuário ou pelo contexto. Não converta valores e não invente moedas.
7. Terminar com uma pergunta curta para continuar a conversa, quando fizer sentido.
"""

        modelo_gemini = get_model_for_role(
            LLMRole.RAG
        )

        response = executar_generate_content_observado(
            client,
            modelo=modelo_gemini,
            contents=prompt,
            operacao="rag_answer",
            origem="rag_engine",
            metadados={
                "fluxo": "rag_hibrido",
                "usa_contexto_recuperado": True,
            },
        )

        resposta = getattr(response, "text", "") or ""

        resposta = resposta.strip()

        if not resposta:
            return None

        # Pequenas correções de espaçamento em respostas geradas.
        correcoes_espaco = {
            "aquelesimprevistos": "aqueles imprevistos",
            "tododia": "todo dia",
            "todomês": "todo mês",
            "umpouco": "um pouco",
            "umpouquinho": "um pouquinho",
            "R$ 10, R$ 20, ou R$ 50": "R$ 10, R$ 20 ou R$ 50",
            "R$ 10, R$ 20, R$ 50, ou": "R$ 10, R$ 20, R$ 50 ou",
            "se o trabalho": "se o trabalho",
        }

        for errado, certo in correcoes_espaco.items():
            resposta = resposta.replace(errado, certo)

        return resposta

    except Exception:
        return None




def save_rag_log(
    pergunta: str,
    resultado: dict,
    tempo_resposta_ms: int | None = None,
) -> None:
    """
    Salva o log da resposta RAG.

    A telemetria nunca pode interromper
    a resposta entregue ao usuário.
    """
    import json

    conn = None
    cur = None

    try:
        resultado = (
            resultado
            if isinstance(resultado, dict)
            else {}
        )

        modo = str(
            resultado.get("modo")
            or ""
        )

        resposta = str(
            resultado.get("resposta")
            or ""
        )

        fontes = (
            resultado.get("fontes")
            or []
        )

        if not isinstance(
            fontes,
            (
                list,
                tuple,
            ),
        ):
            fontes = []

        trace_id = (
            resultado.get("trace_id")
            or None
        )

        retrieval_trace = (
            resultado.get(
                "retrieval_trace"
            )
            or None
        )

        retrieval_trace_json = (
            json.dumps(
                retrieval_trace,
                ensure_ascii=False,
                default=str,
            )
            if retrieval_trace is not None
            else None
        )

        conn = get_rag_connection()
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS
                inna_rag_logs (
                    id SERIAL PRIMARY KEY,
                    pergunta TEXT,
                    modo TEXT,
                    resposta_preview TEXT,
                    fontes_total INTEGER DEFAULT 0,
                    usou_gemini BOOLEAN DEFAULT FALSE,
                    usou_seguranca BOOLEAN DEFAULT FALSE,
                    usou_fallback BOOLEAN DEFAULT FALSE,
                    tempo_resposta_ms INTEGER,
                    trace_id TEXT,
                    retrieval_trace JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """
        )

        cur.execute(
            """
            ALTER TABLE inna_rag_logs
            ADD COLUMN IF NOT EXISTS
                trace_id TEXT;
            """
        )

        cur.execute(
            """
            ALTER TABLE inna_rag_logs
            ADD COLUMN IF NOT EXISTS
                retrieval_trace JSONB;
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_inna_rag_logs_trace_id
            ON inna_rag_logs (
                trace_id
            )
            WHERE trace_id IS NOT NULL;
            """
        )

        cur.execute(
            """
            INSERT INTO inna_rag_logs (
                pergunta,
                modo,
                resposta_preview,
                fontes_total,
                usou_gemini,
                usou_seguranca,
                usou_fallback,
                tempo_resposta_ms,
                trace_id,
                retrieval_trace
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb
            );
            """,
            (
                str(pergunta or ""),
                modo,
                resposta[:500],
                len(fontes),
                "_gemini_answer" in modo,
                (
                    "seguranca_financeira"
                    in modo
                ),
                (
                    "fallback" in modo
                    or (
                        "rag_local_sem_custo"
                        in modo
                    )
                ),
                tempo_resposta_ms,
                (
                    str(trace_id)
                    if trace_id
                    else None
                ),
                retrieval_trace_json,
            ),
        )

        conn.commit()

    except Exception:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        # O log não pode quebrar a resposta.
        return

    finally:
        if cur:
            try:
                cur.close()
            except Exception:
                pass

        if conn:
            try:
                conn.close()
            except Exception:
                pass



def answer_with_rag(pergunta: str, idioma: str = "pt", top_k: int = 4) -> dict:
    resposta_seguranca = answer_security_financeira(pergunta)
    if resposta_seguranca:
        return resposta_seguranca

    try:
        from services.rag.retrieval_trace import (
            start_retrieval_trace,
        )
    except ImportError:
        from src.services.rag.retrieval_trace import (
            start_retrieval_trace,
        )

    retrieval_trace = start_retrieval_trace(
        query=pergunta,
        language=idioma,
        search_mode="pending",
        top_k=top_k,
    )

    retrieval_phase_timings: dict[
        str,
        float,
    ] = {}

    supports_profiling = False

    try:
        import inspect

        hybrid_signature = inspect.signature(
            search_knowledge_base_hybrid
        )

        supports_profiling = (
            "profiling"
            in hybrid_signature.parameters
            or any(
                parameter.kind
                is inspect.Parameter.VAR_KEYWORD
                for parameter
                in hybrid_signature.parameters.values()
            )
        )
    except (TypeError, ValueError):
        supports_profiling = False

    if supports_profiling:
        results = search_knowledge_base_hybrid(
            pergunta,
            idioma=idioma,
            top_k=top_k,
            profiling=retrieval_phase_timings,
        )
    else:
        results = search_knowledge_base_hybrid(
            pergunta,
            idioma=idioma,
            top_k=top_k,
        )

    # Runtime RAG 3072-only.
    # Não retorna ao armazenamento legado 768
    # quando o retrieval estruturado não encontra
    # evidência suficiente.

    modo_busca = (
        results[0].get(
            "modo_busca",
            "rag_local_fallback",
        )
        if results
        else "sem_resultados"
    )

    retrieval_trace.finish(
        results,
        search_mode=modo_busca,
    )

    def finalizar_resposta_rag(
        resultado: dict,
        *,
        modo: str | None = None,
    ) -> dict:
        """
        Acrescenta rastreabilidade sem alterar
        os campos históricos da resposta RAG.
        """
        payload = dict(resultado or {})

        trace_payload = (
            retrieval_trace.to_dict()
        )

        if modo:
            trace_payload["search_mode"] = modo

        payload["trace_id"] = (
            retrieval_trace.trace_id
        )

        payload["retrieval_trace"] = (
            trace_payload
        )

        payload[
            "retrieval_phase_timings"
        ] = dict(
            retrieval_phase_timings
        )

        return payload

    if not results:
        return finalizar_resposta_rag(
            {
            "resposta": "Não encontrei informação suficiente na base de conhecimento da INNA para responder com segurança.",
            "fontes": [],
            "contexto_usado": "",
            "modo": modo_busca,
        },
            modo=modo_busca,
        )

    def get_chunk_text(item: dict) -> str:
        return (
            item.get("chunk_text")
            or item.get("texto")
            or item.get("trecho")
            or item.get("conteudo")
            or item.get("content")
            or ""
        )

    contexto = "\n\n".join([get_chunk_text(item) for item in results])
    pergunta_normalizada = normalize_text(pergunta)
    intencao_continuacao = detectar_intencao_continuacao(pergunta)

    tem_anotacao_financeira = (
        "anotacao_financeira_do_usuario" in pergunta_normalizada
        or (
            any(p in pergunta_normalizada for p in ["ganho", "recebo", "salario", "renda"])
            and any(p in pergunta_normalizada for p in ["gasto", "gastei", "pago", "despesa", "conta"])
            and any(p in pergunta_normalizada for p in ["guardo", "guardar", "sobra", "consigo guardar", "junto"])
        )
    )

    if intencao_continuacao == "cancelar" and not tem_anotacao_financeira:
        return finalizar_resposta_rag(
            resposta_cancelar_simples(),
            modo=modo_busca,
        )

    if intencao_continuacao == "ajustar_para_menos" and not tem_anotacao_financeira:
        return finalizar_resposta_rag(
            resposta_ajustar_valor(
                menor=True
            ),
            modo=modo_busca,
        )

    if intencao_continuacao == "ajustar_para_mais" and not tem_anotacao_financeira:
        return finalizar_resposta_rag(
            resposta_ajustar_valor(
                menor=False
            ),
            modo=modo_busca,
        )

    if intencao_continuacao == "meta_semana" and not tem_anotacao_financeira:
        return finalizar_resposta_rag(
            resposta_meta_semana_simples(),
            modo=modo_busca,
        )

    if intencao_continuacao == "meta_mes" and not tem_anotacao_financeira:
        return finalizar_resposta_rag(
            resposta_meta_mes_simples(),
            modo=modo_busca,
        )

    tem_anotacao_financeira = (
        "anotacao_financeira_do_usuario" in pergunta_normalizada
        or (
            any(p in pergunta_normalizada for p in ["ganho", "recebo", "salario", "renda"])
            and any(p in pergunta_normalizada for p in ["gasto", "gastei", "pago", "despesa", "conta"])
            and any(p in pergunta_normalizada for p in ["guardo", "guardar", "sobra", "consigo guardar", "junto"])
        )
    )

    # Dívidas e organização de gastos agora passam pelo RAG híbrido + Gemini
    # quando não houver cálculo numérico específico.

    # Quando o usuário responde "sim", a INNA precisa olhar a última pergunta.
    # Se a última pergunta foi sobre "esta semana", responde só a meta semanal.
    # Se foi sobre "mês inteiro" ou "30 dias", responde as 4 semanas.
    usuario_confirmou = (
        "sim" in pergunta_normalizada
        or "quero" in pergunta_normalizada
        or "pode" in pergunta_normalizada
        or "continue" in pergunta_normalizada
        or "me mostre" in pergunta_normalizada
        or "mostre" in pergunta_normalizada
    )

    pedido_semana = (
        "esta semana" in pergunta_normalizada
        or "desta semana" in pergunta_normalizada
        or "meta simples para esta semana" in pergunta_normalizada
        or "meta para esta semana" in pergunta_normalizada
    )

    pedido_mes = (
        "mes inteiro" in pergunta_normalizada
        or "mês inteiro" in pergunta_normalizada
        or "30 dias" in pergunta_normalizada
        or "meta do mes" in pergunta_normalizada
        or "meta do mês" in pergunta_normalizada
    )

    if usuario_confirmou and pedido_mes:
        resposta = """Claro. Vou mostrar uma ideia simples para o mês inteiro.

Meta de 30 dias:
Guardar um valor pequeno toda semana, sem apertar demais.

Plano simples de 4 semanas:

1. Semana 1:
Guarde o primeiro valor da semana. O importante é começar.

2. Semana 2:
Tente repetir o mesmo valor da semana anterior.

3. Semana 3:
Veja se sobrou um pouco mais. Se não sobrou, mantenha o mesmo valor.

4. Semana 4:
Some tudo que conseguiu guardar e veja seu progresso.

Orientação simples:
Se uma semana apertar, guarde menos. O importante é não desistir.

Depois você pode me dizer se quer uma meta menor ou maior."""

        return finalizar_resposta_rag(
            {
            "resposta": resposta,
            "fontes": [],
            "contexto_usado": "",
            "modo": modo_busca,
        },
            modo=modo_busca,
        )

    if usuario_confirmou and pedido_semana:
        resposta = """Claro. Vamos fazer só a meta desta semana.

Meta da semana:
Guardar um valor pequeno e possível, sem apertar demais.

O que fazer nesta semana:

1. Escolha um valor que caiba no seu bolso.
2. Separe esse valor assim que receber ou assim que sobrar.
3. Não use esse dinheiro para compras comuns.
4. No fim da semana, veja se conseguiu manter o valor guardado.

Orientação simples:
Se não conseguir guardar tudo, guarde uma parte. O importante é começar.

Depois você pode me dizer quanto conseguiu guardar, e eu te ajudo a ajustar."""

        return finalizar_resposta_rag(
            {
            "resposta": resposta,
            "fontes": [],
            "contexto_usado": "",
            "modo": modo_busca,
        },
            modo=modo_busca,
        )

    valor_para_guardar = extrair_valor_para_guardar(pergunta)

    fontes = [
        {
            "titulo": item["titulo"],
            "fonte": item["fonte"],
            "score": item["score"],
            "trecho": get_chunk_text(item)[:500],
        }
        for item in results
    ]

    numeros_na_pergunta = re.findall(r"(?<!\\w)(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)(?!\\w)", pergunta_normalizada)

    pergunta_tem_calculo = (
        tem_anotacao_financeira
        or len(numeros_na_pergunta) > 0
        or valor_para_guardar is not None
    )

    # BLOCO_FORCADO_GEMINI_ABERTO_INICIO
    tema_aberto_para_gemini = (
        pergunta_normalizada.startswith("como ")
        or pergunta_normalizada.startswith("o que ")
        or pergunta_normalizada.startswith("qual ")
        or pergunta_normalizada.startswith("por que ")
        or pergunta_normalizada.startswith("porque ")
        or "como posso" in pergunta_normalizada
        or "reserva" in pergunta_normalizada
        or "cartao" in pergunta_normalizada
        or "cartão" in pergunta_normalizada
        or "credito" in pergunta_normalizada
        or "crédito" in pergunta_normalizada
        or "divida" in pergunta_normalizada
        or "dívida" in pergunta_normalizada
        or "dividas" in pergunta_normalizada
        or "dívidas" in pergunta_normalizada
        or "gastos fixos" in pergunta_normalizada
        or "gastos variaveis" in pergunta_normalizada
        or "gastos variáveis" in pergunta_normalizada
        or "organizar gastos" in pergunta_normalizada
    )

    if tema_aberto_para_gemini and not pergunta_tem_calculo:
        resposta_gemini = generate_gemini_rag_answer(pergunta, contexto, idioma=idioma)

        if resposta_gemini:
            return finalizar_resposta_rag(
                {
                "resposta": resposta_gemini,
                "fontes": fontes,
                "contexto_usado": contexto,
                "modo": modo_busca + "_gemini_answer",
            },
                modo=modo_busca,
            )
    # BLOCO_FORCADO_GEMINI_ABERTO_FIM

    pergunta_explicativa = (
        pergunta_normalizada.startswith("como ")
        or pergunta_normalizada.startswith("o que ")
        or pergunta_normalizada.startswith("qual ")
        or pergunta_normalizada.startswith("por que ")
        or pergunta_normalizada.startswith("porque ")
        or "como posso" in pergunta_normalizada
        or "me explica" in pergunta_normalizada
        or "explique" in pergunta_normalizada
        or intencao_continuacao in ["dividas", "organizar_gastos"]
        or "cartao" in pergunta_normalizada
        or "cartão" in pergunta_normalizada
        or "credito" in pergunta_normalizada
        or "crédito" in pergunta_normalizada
        or "divida" in pergunta_normalizada
        or "dívida" in pergunta_normalizada
        or "dividas" in pergunta_normalizada
        or "dívidas" in pergunta_normalizada
    )

    pergunta_aberta_para_gemini = (
        not pergunta_tem_calculo
        and not usuario_confirmou
        and not pedido_mes
        and not pedido_semana
        and intencao_continuacao not in ["cancelar", "ajustar_para_menos", "ajustar_para_mais"]
        and pergunta_explicativa
    )

    if pergunta_aberta_para_gemini:
        resposta_gemini = generate_gemini_rag_answer(pergunta, contexto, idioma=idioma)

        if resposta_gemini:
            return finalizar_resposta_rag(
                {
                "resposta": resposta_gemini,
                "fontes": fontes,
                "contexto_usado": contexto,
                "modo": modo_busca + "_gemini_answer",
            },
                modo=modo_busca,
            )

    if valor_para_guardar and (
        "anotacao_financeira_do_usuario" in pergunta_normalizada
        or "guardar" in pergunta_normalizada
        or "guardo" in pergunta_normalizada
        or "juntar" in pergunta_normalizada
        or "junto" in pergunta_normalizada
        or "separar" in pergunta_normalizada
        or "separo" in pergunta_normalizada
        or "sobra" in pergunta_normalizada
        or "sobrou" in pergunta_normalizada
        or "resta" in pergunta_normalizada
        or "fica" in pergunta_normalizada
        or "consigo" in pergunta_normalizada
        or "posso" in pergunta_normalizada
        or "ganho" in pergunta_normalizada
        or "recebo" in pergunta_normalizada
        or "gasto" in pergunta_normalizada
        or "gastei" in pergunta_normalizada
        or "pago" in pergunta_normalizada
        or "salario" in pergunta_normalizada
        or "renda" in pergunta_normalizada
        or "conta" in pergunta_normalizada
        or "despesa" in pergunta_normalizada
    ):
        renda_mensal = extrair_renda_mensal(pergunta) if "extrair_renda_mensal" in globals() else None
        gasto_mensal = extrair_gasto_mensal(pergunta) if "extrair_gasto_mensal" in globals() else None

        valor_semana = valor_para_guardar / 4

        linhas = []

        if renda_mensal:
            linhas.append(f"- Renda informada: {formatar_reais_simples(renda_mensal)} por mês.")

        if gasto_mensal:
            linhas.append(f"- Gasto informado: {formatar_reais_simples(gasto_mensal)} por mês.")

        linhas.append(f"- Valor que você disse que consegue guardar: {formatar_reais_simples(valor_para_guardar)} por mês.")

        contexto_financeiro = "\n".join(linhas)

        resposta = f"""Entendi sua anotação. Vou te orientar de forma simples.

{contexto_financeiro}

Uma forma fácil de começar é dividir esse valor por semana:

- Meta no mês: {formatar_reais_simples(valor_para_guardar)}
- Meta por semana: cerca de {formatar_reais_simples(valor_semana)}

Meta desta semana:

1. Separe cerca de {formatar_reais_simples(valor_semana)} nesta semana.
2. Guarde esse valor assim que receber ou assim que sobrar.
3. Evite usar esse dinheiro para compras do dia a dia.
4. No fim da semana, veja se conseguiu manter esse valor guardado.

Orientação simples:
Se uma semana apertar, guarde menos. O importante é começar e manter o costume.

Quer que eu mostre como ficaria essa meta no mês inteiro?"""

        fontes = [
            {
                "titulo": item["titulo"],
                "fonte": item["fonte"],
                "score": item["score"],
                "trecho": get_chunk_text(item)[:500],
            }
            for item in results
        ]

        return finalizar_resposta_rag(
            {
            "resposta": resposta,
            "fontes": fontes,
            "contexto_usado": contexto,
            "modo": modo_busca,
        },
            modo=modo_busca,
        )

    fontes = [
        {
            "titulo": item["titulo"],
            "fonte": item["fonte"],
            "score": item["score"],
            "trecho": get_chunk_text(item)[:500],
        }
        for item in results
    ]

    numeros_na_pergunta = re.findall(r"(?<!\\w)(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)(?!\\w)", pergunta_normalizada)

    pergunta_tem_calculo = (
        tem_anotacao_financeira
        or len(numeros_na_pergunta) > 0
        or valor_para_guardar is not None
    )

    pergunta_aberta_para_gemini = (
        not pergunta_tem_calculo
        and not usuario_confirmou
        and not pedido_mes
        and not pedido_semana
        and intencao_continuacao not in ["cancelar", "ajustar_para_menos", "ajustar_para_mais"]
    )

    if pergunta_aberta_para_gemini:
        resposta_gemini = generate_gemini_rag_answer(pergunta, contexto, idioma=idioma)

        if resposta_gemini:
            return finalizar_resposta_rag(
                {
                "resposta": resposta_gemini,
                "fontes": fontes,
                "contexto_usado": contexto,
                "modo": modo_busca + "_gemini_answer",
            },
                modo=modo_busca,
            )

    fontes = [
        {
            "titulo": item["titulo"],
            "fonte": item["fonte"],
            "score": item["score"],
            "trecho": get_chunk_text(item)[:500],
        }
        for item in results
    ]

    numeros_na_pergunta = re.findall(r"(?<!\\w)(?:r\$)?\s*([0-9]+(?:[,.][0-9]+)?)(?!\\w)", pergunta_normalizada)

    pergunta_explicativa = (
        pergunta_normalizada.startswith("como ")
        or pergunta_normalizada.startswith("o que ")
        or pergunta_normalizada.startswith("qual ")
        or pergunta_normalizada.startswith("por que ")
        or pergunta_normalizada.startswith("porque ")
        or "como posso" in pergunta_normalizada
        or "me explica" in pergunta_normalizada
        or "explique" in pergunta_normalizada
        or intencao_continuacao in ["dividas", "organizar_gastos"]
        or "cartao" in pergunta_normalizada
        or "cartão" in pergunta_normalizada
        or "credito" in pergunta_normalizada
        or "crédito" in pergunta_normalizada
        or "divida" in pergunta_normalizada
        or "dívida" in pergunta_normalizada
        or "dividas" in pergunta_normalizada
        or "dívidas" in pergunta_normalizada
    )

    pergunta_tem_calculo = (
        tem_anotacao_financeira
        or len(numeros_na_pergunta) > 0
        or valor_para_guardar is not None
    )

    if pergunta_explicativa and not pergunta_tem_calculo:
        resposta_gemini = generate_gemini_rag_answer(pergunta, contexto, idioma=idioma)

        if resposta_gemini:
            return finalizar_resposta_rag(
                {
                "resposta": resposta_gemini,
                "fontes": fontes,
                "contexto_usado": contexto,
                "modo": modo_busca + "_gemini_answer",
            },
                modo=modo_busca,
            )

    # Perguntas abertas sobre temas financeiros usam Gemini com contexto RAG.
    # Perguntas com números/cálculo continuam controladas pelo código.
    tema_aberto_para_gemini = (
        pergunta_normalizada.startswith("como ")
        or pergunta_normalizada.startswith("o que ")
        or pergunta_normalizada.startswith("qual ")
        or pergunta_normalizada.startswith("por que ")
        or pergunta_normalizada.startswith("porque ")
        or "como posso" in pergunta_normalizada
        or "cartao" in pergunta_normalizada
        or "cartão" in pergunta_normalizada
        or "credito" in pergunta_normalizada
        or "crédito" in pergunta_normalizada
        or "divida" in pergunta_normalizada
        or "dívida" in pergunta_normalizada
        or "dividas" in pergunta_normalizada
        or "dívidas" in pergunta_normalizada
        or "gastos fixos" in pergunta_normalizada
        or "gastos variaveis" in pergunta_normalizada
        or "gastos variáveis" in pergunta_normalizada
        or "organizar gastos" in pergunta_normalizada
        or "reserva" in pergunta_normalizada
    )

    if tema_aberto_para_gemini and not pergunta_tem_calculo:
        resposta_gemini = generate_gemini_rag_answer(pergunta, contexto, idioma=idioma)

        if resposta_gemini:
            return finalizar_resposta_rag(
                {
                "resposta": resposta_gemini,
                "fontes": fontes,
                "contexto_usado": contexto,
                "modo": modo_busca + "_gemini_answer",
            },
                modo=modo_busca,
            )

    pergunta_sobre_tipos_de_gastos = (
        "gastos fixos" in pergunta_normalizada
        and (
            "gastos variaveis"
            in pergunta_normalizada
            or "gastos variáveis"
            in pergunta_normalizada
        )
        and "reserva" in pergunta_normalizada
    )

    if pergunta_sobre_tipos_de_gastos:
        resposta = """Gastos fixos são despesas recorrentes e geralmente previsíveis, como aluguel, mensalidades e parcelas.

Gastos variáveis mudam conforme o consumo e as escolhas do mês, como mercado, transporte, energia e lazer.

A reserva de emergência é um valor separado para situações inesperadas, como perda de renda, consertos ou despesas urgentes. Ela ajuda a evitar empréstimos e o uso do cartão em momentos de dificuldade.

Uma forma simples de começar é registrar os gastos fixos e variáveis, verificar quanto sobra no orçamento e guardar uma quantia possível todos os meses para construir a reserva."""

    elif "reserva" in pergunta_normalizada:
        resposta = """Vamos por partes. Vou te orientar de um jeito simples:

1. Veja quanto entra e quanto sai todo mês com contas, mercado, transporte, compras e parcelas.
2. Separe um valor pequeno que caiba no seu bolso, sem apertar demais.
3. Não use esse dinheiro para compras do dia a dia.
4. Olhe todo mês se conseguiu guardar alguma quantia, mesmo que seja pouco.\n\nQuer que eu monte uma meta simples para esta semana?"""
    elif "divida" in pergunta_normalizada or "dívida" in pergunta_normalizada:
        resposta = """Vamos por partes. O melhor caminho para reduzir suas dívidas é:

1. Liste todas as dívidas, parcelas, juros e vencimentos.
2. Priorize o pagamento das dívidas mais caras ou com maior impacto no orçamento.
3. Evite assumir novas dívidas durante o plano de organização.
4. Negocie condições melhores quando possível.\n\nQuer que eu monte uma meta simples para esta semana?"""
    elif "gasto" in pergunta_normalizada or "organizar" in pergunta_normalizada:
        resposta = """Vamos por partes. O melhor caminho para organizar seus gastos é:

1. Separe seus gastos em fixos, variáveis e dívidas.
2. Identifique gastos pequenos recorrentes que podem ser reduzidos.
3. Defina um limite semanal para despesas variáveis.
4. Revise seu orçamento ao final de cada mês.\n\nQuer que eu monte uma meta simples para esta semana?"""
    else:
        resposta = """Com base na base de conhecimento da INNA, a orientação educativa é:

1. Organize seus dados financeiros.
2. Compare renda, gastos, dívidas e reserva.
3. Priorize ações simples e mensuráveis.
4. Evite decisões financeiras arriscadas sem orientação profissional.\n\nQuer que eu monte uma meta simples para esta semana?"""

    fontes = [
        {
            "titulo": item["titulo"],
            "fonte": item["fonte"],
            "score": item["score"],
            "trecho": get_chunk_text(item)[:500],
        }
        for item in results
    ]

    return finalizar_resposta_rag(
        {
        "resposta": resposta,
        "fontes": fontes,
        "contexto_usado": contexto,
        "modo": modo_busca,
    },
        modo=modo_busca,
    )
