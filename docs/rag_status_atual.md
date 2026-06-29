# Status Atual do RAG — INNA Financial Coach AI

## Status real do projeto

A INNA já possui uma estrutura funcional de RAG local e chat educativo.

## Fases concluídas

| Fase | Nome | Status |
|---:|---|---|
| 5.1 | RAG Local sem custo | Concluído |
| 5.2 | Chat conectado ao RAG | Concluído |
| 5.3 | Fontes na tela | Concluído |
| 5.5 | Diretrizes de segurança | Concluído |
| 5.4 | FAQ financeiro | Em evolução |

## Recursos já existentes

- Base de conhecimento financeira;
- Chunks de texto;
- Busca semântica local;
- Tabela `inna_knowledge_chunks`;
- Endpoints `/rag/setup`, `/rag/search` e `/rag/ask`;
- Chat Streamlit conectado ao RAG;
- Fonte usada pela INNA na interface;
- Continuação de conversa;
- Interpretação de anotação financeira;
- Meta semanal;
- Meta de 30 dias;
- Diretrizes de linguagem e segurança;
- Base FAQ financeiro inicial.

## Momento atual

O projeto está entre:

- Fase 5.4 — FAQ financeiro avançado;
- Fase 5.6 — RAG com Gemini usando contexto recuperado.

## Próximos passos

1. Fortalecer a base FAQ financeiro.
2. Rodar `/rag/setup` para carregar os novos conteúdos.
3. Integrar as diretrizes da INNA aos prompts.
4. Fazer o Gemini responder usando os trechos recuperados.
5. Melhorar a experiência do cliente com botões e respostas guiadas.
6. Depois evoluir para PDF RAG, memória por usuário e pgvector.

## Objetivo final

A INNA deve ser um copiloto financeiro educativo, simples e seguro.

Ela deve orientar o cliente sobre organização financeira, reserva, dívidas e metas, sem recomendar investimentos ou prometer resultados.
