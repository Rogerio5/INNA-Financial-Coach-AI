# Fase 5 — RAG, Vetor e Embeddings

A INNA Financial Coach AI passa a ter uma base de conhecimento própria para responder perguntas com apoio de fontes internas.

## Componentes

- Base de conhecimento financeira
- Chunks de texto
- Embeddings locais sem custo
- Vetores salvos no PostgreSQL/Neon
- Busca semântica
- Respostas com fontes
- Políticas de segurança
- FAQ financeiro
- Preparação para RAG com Gemini

## Tabelas

Tabela principal:

inna_knowledge_chunks

Campos principais:

- id
- titulo
- fonte
- categoria
- idioma
- chunk_index
- chunk_text
- embedding
- metadata
- created_at

## Endpoints

- POST /rag/setup
- GET /rag/search
- POST /rag/ask

## Segurança

A INNA deve responder apenas sobre educação financeira e evitar recomendações específicas de investimento.
