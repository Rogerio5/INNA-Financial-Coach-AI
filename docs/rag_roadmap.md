# Ranking de Evolução RAG — INNA Financial Coach AI

Este documento apresenta a evolução planejada da arquitetura RAG da INNA Financial Coach AI.

## Ranking dos níveis de RAG

| Ranking | Nível de RAG | O que é | Status na INNA | Prioridade |
|---:|---|---|---|---|
| 1 | RAG Local sem custo | Base própria, chunks, embeddings locais e busca semântica no Neon/PostgreSQL. | Em implantação | Alta |
| 2 | RAG conectado ao Chat | O Web App consulta o endpoint /rag/ask. | Próximo passo | Alta |
| 3 | RAG com fontes | Mostra fontes usadas na resposta. | Parcialmente iniciado | Alta |
| 4 | RAG com Gemini | Usa trechos recuperados para gerar resposta com Gemini. | Planejado | Alta |
| 5 | RAG com FAQ financeiro | Base de perguntas frequentes sobre reserva, dívidas e orçamento. | Planejado | Alta |
| 6 | RAG com políticas de segurança | Regras para respostas seguras e educativas. | Planejado | Alta |
| 7 | RAG com documentos PDF | Lê PDFs, divide em chunks e salva no banco vetorial. | Planejado | Média/Alta |
| 8 | RAG com memória por usuário | Usa histórico, diagnóstico e objetivos do usuário. | Planejado | Média/Alta |
| 9 | RAG com pgvector | Usa extensão vetorial profissional no PostgreSQL/Neon. | Evolução futura | Média |
| 10 | RAG híbrido | Combina busca por palavra-chave com busca semântica. | Evolução futura | Média |
| 11 | RAG multiagente | Usa agentes de diagnóstico, educação, RAG, segurança e avaliação. | Evolução futura | Média |
| 12 | Agentic RAG completo | A IA decide quando buscar base, histórico, PDF, política ou diagnóstico. | Evolução avançada | Baixa agora |

## Ordem prática de implementação

| Ordem | Fase prática | Objetivo |
|---:|---|---|
| 1 | Fase 5.1 — RAG Local | Rodar /rag/setup, testar /rag/search e /rag/ask. |
| 2 | Fase 5.2 — Chat com RAG | Conectar a tela Conversar ao endpoint /rag/ask. |
| 3 | Fase 5.3 — Fontes na tela | Mostrar fontes e trechos usados na resposta. |
| 4 | Fase 5.4 — FAQ financeiro | Criar base de perguntas frequentes. |
| 5 | Fase 5.5 — Políticas de segurança | Criar regras de segurança financeira. |
| 6 | Fase 5.6 — RAG com Gemini | Gerar resposta com base nos trechos recuperados. |
| 7 | Fase 5.7 — PDF RAG | Permitir documentos PDF como base de conhecimento. |
| 8 | Fase 5.8 — Memória por usuário | Usar histórico e diagnóstico como contexto. |
| 9 | Fase 5.9 — pgvector | Evoluir o armazenamento vetorial. |
| 10 | Fase 5.10 — Multiagentes | Separar a INNA em agentes especialistas. |

## Arquitetura futura

Usuário
↓
Streamlit Web App
↓
FastAPI
↓
Orquestrador INNA
↓
RAG / Base de Conhecimento / Diagnóstico / Memória / Segurança
↓
Gemini
↓
Resposta com fontes
↓
Neon PostgreSQL + Dashboard Analytics

## Status atual

A estrutura inicial do RAG já foi criada com:

- base de conhecimento financeira;
- chunks de texto;
- embeddings locais sem custo;
- tabela inna_knowledge_chunks;
- endpoints /rag/setup, /rag/search e /rag/ask;
- preparação para respostas com fontes.

## Próximo passo

Testar a API, criar a base no Neon com /rag/setup e conectar o Web App ao endpoint /rag/ask.
