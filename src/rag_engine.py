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
            item = dict(zip(columns, row))

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



def search_knowledge_base_pgvector(query: str, idioma: str = "pt", top_k: int = 4) -> list[dict]:
    """
    Busca principal da INNA:
    Gemini Embeddings + pgvector no Neon/PostgreSQL.
    """
    query_embedding = generate_gemini_embedding(query)

    if not query_embedding:
        return []

    query_vector_sql = pgvector_to_sql(query_embedding)

    conn = get_rag_connection()
    cur = conn.cursor()

    try:
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
                metadata,
                1 - (embedding_vector <=> %s::vector) AS score
            FROM inna_knowledge_chunks
            WHERE idioma = %s
              AND embedding_vector IS NOT NULL
            ORDER BY embedding_vector <=> %s::vector
            LIMIT %s;
            """,
            (query_vector_sql, idioma, query_vector_sql, top_k),
        )

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        results = []

        for row in rows:
            item = dict(zip(columns, row))
            item["texto"] = item.get("chunk_text", "")
            item["trecho"] = item.get("chunk_text", "")
            item["score"] = float(item.get("score") or 0)
            item["modo_busca"] = "gemini_embeddings_pgvector_neon"
            results.append(item)

        return results

    finally:
        cur.close()
        conn.close()


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


def answer_with_rag(pergunta: str, idioma: str = "pt", top_k: int = 4) -> dict:
    results = search_knowledge_base_pgvector(pergunta, idioma=idioma, top_k=top_k)

    if not results:
        results = search_knowledge_base(pergunta, idioma=idioma, top_k=top_k)

    if not results:
        return {
            "resposta": "Não encontrei informação suficiente na base de conhecimento da INNA para responder com segurança.",
            "fontes": [],
            "contexto_usado": "",
            "modo": "rag_local_sem_custo",
        }

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
        return resposta_cancelar_simples()

    if intencao_continuacao == "ajustar_para_menos" and not tem_anotacao_financeira:
        return resposta_ajustar_valor(menor=True)

    if intencao_continuacao == "ajustar_para_mais" and not tem_anotacao_financeira:
        return resposta_ajustar_valor(menor=False)

    if intencao_continuacao == "meta_semana" and not tem_anotacao_financeira:
        return resposta_meta_semana_simples()

    if intencao_continuacao == "meta_mes" and not tem_anotacao_financeira:
        return resposta_meta_mes_simples()

    tem_anotacao_financeira = (
        "anotacao_financeira_do_usuario" in pergunta_normalizada
        or (
            any(p in pergunta_normalizada for p in ["ganho", "recebo", "salario", "renda"])
            and any(p in pergunta_normalizada for p in ["gasto", "gastei", "pago", "despesa", "conta"])
            and any(p in pergunta_normalizada for p in ["guardo", "guardar", "sobra", "consigo guardar", "junto"])
        )
    )

    if intencao_continuacao == "dividas" and not tem_anotacao_financeira:
        return resposta_dividas_simples()

    if intencao_continuacao == "organizar_gastos" and not tem_anotacao_financeira:
        return resposta_organizar_gastos_simples()

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

        return {
            "resposta": resposta,
            "fontes": [],
            "contexto_usado": "",
            "modo": "rag_local_sem_custo",
        }

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

        return {
            "resposta": resposta,
            "fontes": [],
            "contexto_usado": "",
            "modo": "rag_local_sem_custo",
        }

    valor_para_guardar = extrair_valor_para_guardar(pergunta)

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

        return {
            "resposta": resposta,
            "fontes": fontes,
            "contexto_usado": contexto,
            "modo": "rag_local_sem_custo",
        }

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

    return {
        "resposta": resposta,
        "fontes": fontes,
        "contexto_usado": contexto,
        "modo": "rag_local_sem_custo",
    }

