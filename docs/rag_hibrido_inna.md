# Fase 5.11 — RAG Híbrido da INNA

## 1. Objetivo

A Fase 5.11 documenta a arquitetura de RAG Híbrido utilizada pela **INNA Financial Coach AI**.

O objetivo é combinar busca vetorial, busca textual, banco de dados PostgreSQL/Neon, pgvector, reranking e geração controlada de respostas para entregar orientações financeiras mais precisas, seguras e contextualizadas.

---

## 2. O que é RAG na INNA

RAG significa **Retrieval-Augmented Generation**, ou seja, geração aumentada por recuperação de conhecimento.

Na INNA, isso significa que a assistente não responde apenas com base no modelo de IA. Antes de responder, ela busca informações relevantes em uma base de conhecimento financeira.

Essa base contém conteúdos sobre:

- educação financeira;
- reserva financeira;
- organização de gastos;
- cartão de crédito;
- dívidas;
- Pix;
- golpes financeiros;
- segurança bancária;
- orientação preventiva.

---

## 3. Por que usar RAG Híbrido

A busca apenas vetorial entende significado, mas pode perder termos exatos.

A busca apenas textual encontra palavras exatas, mas pode não entender bem o contexto.

Por isso, a INNA usa uma abordagem híbrida:

- **Busca vetorial:** encontra conteúdos parecidos pelo significado.
- **Busca textual:** encontra termos exatos, como Pix, boleto, cartão, dívida, senha, golpe.
- **Reranking:** reorganiza os melhores trechos antes da resposta final.
- **Gemini:** é usado quando a pergunta precisa de resposta mais natural e completa.
- **Fallback controlado:** usado para respostas mais diretas, cálculos simples e segurança financeira.

---

## 4. Fluxo simplificado

O fluxo do RAG Híbrido da INNA funciona assim:

1. O usuário envia uma pergunta.
2. A INNA identifica o tema principal.
3. O sistema consulta a base de conhecimento no PostgreSQL/Neon.
4. A busca vetorial encontra trechos semanticamente parecidos.
5. A busca textual encontra termos exatos importantes.
6. Os resultados são combinados.
7. O reranking escolhe os melhores chunks.
8. A resposta é gerada usando:
   - resposta controlada;
   - Gemini;
   - ou módulo específico de segurança financeira.
9. O resultado é registrado para observabilidade.

---

## 5. Modos identificados no projeto

Durante os testes reais, a INNA utilizou diferentes modos de resposta:

| Modo | Descrição |
|---|---|
| `rag_hibrido_pgvector_text_neon_rerank` | RAG híbrido com busca vetorial, textual, Neon/PostgreSQL e reranking |
| `rag_hibrido_pgvector_text_neon_rerank_gemini_answer` | RAG híbrido com resposta final gerada pelo Gemini |
| `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira` | RAG híbrido com camada específica de segurança financeira |

---

## 6. Bases de conhecimento utilizadas

A INNA utiliza arquivos de conhecimento como:

- `data/knowledge_base/faq_financeiro_inna.md`
- `data/knowledge_base/financeiro_basico.md`
- `data/knowledge_base/seguranca_financeira.md`

Esses documentos ajudam a orientar respostas sobre educação financeira, organização de gastos, dívidas, Pix, golpes e proteção do usuário.

---

## 7. Busca vetorial

A busca vetorial permite encontrar conteúdos relacionados ao significado da pergunta.

Exemplo:

Pergunta:

> Estou apertado com o cartão.

A busca vetorial pode recuperar conteúdos sobre:

- cartão de crédito;
- parcelas;
- fatura;
- juros;
- comprometimento da renda.

Mesmo que o usuário não use exatamente as mesmas palavras da base, a busca vetorial ajuda a encontrar contexto relevante.

---

## 8. Busca textual

A busca textual ajuda a encontrar palavras exatas importantes.

Exemplo:

Pergunta:

> Fiz um Pix errado.

A busca textual pode priorizar termos como:

- Pix;
- errado;
- banco;
- comprovante;
- canais oficiais.

Isso é importante em temas de segurança financeira, onde palavras específicas fazem diferença.

---

## 9. Reranking

Depois que a INNA recupera vários trechos da base, o reranking ajuda a escolher os mais úteis.

O objetivo é evitar que a resposta final use trechos fracos, repetidos ou pouco relacionados à pergunta.

Benefícios:

- melhora a precisão;
- reduz respostas genéricas;
- diminui risco de contexto ruim;
- ajuda o Gemini a responder com mais qualidade;
- melhora a rastreabilidade das fontes.

---

## 10. Gemini quando necessário

A INNA pode usar Gemini para gerar uma resposta final mais natural, acolhedora e completa.

Esse modo aparece principalmente em perguntas que exigem explicação mais conversacional, por exemplo:

- cartão de crédito apertando;
- reserva emergencial;
- gastos pequenos;
- muitas parcelas no cartão.

O Gemini recebe o contexto recuperado pelo RAG e responde com base nesse conteúdo.

---

## 11. Fallback controlado

Nem toda resposta precisa usar geração longa com IA.

Em alguns casos, a INNA usa fallback controlado para manter a resposta mais segura e objetiva.

Exemplos:

- cálculos simples;
- metas semanais;
- respostas educativas diretas;
- segurança financeira;
- alertas sobre golpes.

Isso ajuda a reduzir custo, latência e risco de resposta inventada.

---

## 12. Segurança financeira no RAG

A camada de segurança financeira trata perguntas sobre:

- Pix errado;
- compra não reconhecida no cartão;
- link falso de banco;
- pedido de código por WhatsApp;
- golpes financeiros;
- senha, token, CVV e dados bancários.

Nesses casos, a INNA responde de forma preventiva:

- não pede senha;
- não solicita código;
- orienta canais oficiais;
- não promete estorno;
- não confirma fraude real;
- mantém linguagem educativa.

---

## 13. Evidência da avaliação real

A avaliação real do RAG mostrou:

- Total de perguntas avaliadas: 13.
- Aprovadas: 13.
- Atenção: 0.
- Revisar: 0.
- Taxa de aprovação: 100%.

Os testes cobriram:

- reserva financeira;
- cálculo controlado;
- cartão de crédito;
- organização de gastos;
- dívidas;
- Pix;
- links falsos;
- golpes financeiros;
- pedido de código bancário;
- compra não reconhecida.

---

## 14. Observabilidade

A INNA também possui relatório de observabilidade do RAG.

Esse relatório acompanha:

- total de logs;
- uso de Gemini;
- perguntas de segurança financeira;
- fallback;
- tempo médio;
- maior tempo de resposta;
- distribuição por modo;
- últimas perguntas registradas.

Isso ajuda a analisar qualidade, desempenho e uso real do agente.

---

## 15. Valor técnico

A Fase 5.11 demonstra conhecimento aplicado em:

- IA Generativa;
- RAG;
- embeddings;
- pgvector;
- PostgreSQL/Neon;
- busca textual;
- busca semântica;
- reranking;
- avaliação de respostas;
- fallback controlado;
- observabilidade;
- segurança financeira aplicada.

---

## 16. Próximas evoluções

As próximas evoluções planejadas são:

- ampliar a base de conhecimento;
- permitir upload de novos documentos;
- criar memória por usuário;
- criar Agentic RAG;
- medir custo por resposta;
- registrar tokens usados;
- criar avaliação automática por tema;
- comparar resposta com e sem reranking.

---

## 17. Resumo

O RAG Híbrido da INNA permite que a assistente responda com mais contexto, segurança e precisão.

A arquitetura combina busca vetorial, busca textual, reranking, Gemini e fallback controlado para entregar respostas educativas sobre finanças pessoais e segurança financeira.
