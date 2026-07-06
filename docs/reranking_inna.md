# Fase 5.12 — Reranking da INNA

## 1. Objetivo

A Fase 5.12 documenta o uso de reranking na arquitetura RAG da **INNA Financial Coach AI**.

O objetivo do reranking é melhorar a qualidade dos trechos recuperados antes da geração da resposta final.

Em vez de enviar qualquer resultado encontrado para a IA, a INNA reorganiza os chunks mais relevantes e seleciona os melhores para responder ao usuário.

---

## 2. Por que reranking é importante

Em um sistema RAG, a primeira busca pode retornar vários trechos parecidos.

Nem todos esses trechos são igualmente úteis.

O reranking ajuda a escolher melhor quais informações realmente devem ser usadas.

Benefícios:

- melhora a precisão da resposta;
- reduz contexto fraco ou repetido;
- diminui risco de resposta genérica;
- melhora o uso do Gemini;
- melhora a rastreabilidade das fontes;
- aumenta a confiança no RAG.

---

## 3. Fluxo do reranking na INNA

O fluxo funciona assim:

1. O usuário envia uma pergunta.
2. A INNA executa busca vetorial.
3. A INNA executa busca textual.
4. Os resultados são combinados.
5. O reranking reordena os chunks.
6. Os melhores trechos são selecionados.
7. A resposta final é gerada com base nos melhores contextos.
8. O modo usado é registrado nos logs e relatórios.

---

## 4. Exemplo prático

Pergunta:

> Tenho muitas parcelas no cartão, por onde começo?

A busca inicial pode encontrar conteúdos sobre:

- cartão de crédito;
- parcelas;
- fatura;
- dívidas;
- organização de gastos;
- reserva financeira.

O reranking ajuda a priorizar os trechos mais ligados a:

- parcelas no cartão;
- fatura atual;
- parcelas futuras;
- renda comprometida;
- evitar novas compras parceladas.

Assim, a resposta fica mais alinhada com a pergunta real do usuário.

---

## 5. Modos com reranking identificados

Nos testes reais da INNA, apareceram modos como:

| Modo | Significado |
|---|---|
| `rag_hibrido_pgvector_text_neon_rerank` | RAG híbrido com reranking e resposta controlada |
| `rag_hibrido_pgvector_text_neon_rerank_gemini_answer` | RAG híbrido com reranking e resposta final pelo Gemini |
| `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira` | RAG híbrido com reranking e camada de segurança financeira |

---

## 6. Evidência nos testes

A avaliação real do RAG mostrou que as perguntas testadas usaram modos com `rerank`.

Resultado da avaliação:

- Total de perguntas avaliadas: 13.
- Aprovadas: 13.
- Atenção: 0.
- Revisar: 0.
- Taxa de aprovação: 100%.

Isso indica que o reranking está integrado ao fluxo de resposta da INNA.

---

## 7. Relação com Gemini

Quando a resposta exige mais naturalidade, o Gemini pode ser usado depois do reranking.

Nesse caso, o Gemini não recebe uma pergunta solta. Ele recebe os melhores contextos selecionados pelo RAG.

Isso melhora:

- clareza;
- coerência;
- segurança;
- personalização;
- qualidade da resposta final.

---

## 8. Relação com segurança financeira

Em temas como Pix, golpe, senha, token, CVV, link falso e compra não reconhecida, o reranking ajuda a priorizar conteúdos específicos de segurança.

Isso evita que a INNA responda de forma genérica quando a pergunta exige cuidado.

Exemplo:

> Alguém pediu meu código do banco pelo WhatsApp.

O reranking deve priorizar conteúdos sobre:

- não enviar código;
- não compartilhar senha;
- usar canais oficiais;
- evitar WhatsApp suspeito;
- procurar o banco.

---

## 9. Valor técnico

O reranking demonstra que a INNA não faz apenas uma busca simples.

A arquitetura considera qualidade dos chunks, relevância da pergunta e escolha dos melhores contextos antes da geração.

Isso fortalece o projeto em temas como:

- Engenharia de IA;
- RAG avançado;
- busca semântica;
- busca textual;
- qualidade de resposta;
- redução de alucinação;
- observabilidade;
- segurança aplicada.

---

## 10. Próximas melhorias

Próximas evoluções possíveis:

- medir score antes e depois do reranking;
- salvar ranking dos chunks no banco;
- mostrar os chunks escolhidos no dashboard;
- comparar respostas com e sem reranking;
- avaliar reranking por tema;
- criar métrica de precisão por fonte;
- registrar tempo adicional causado pelo reranking.

---

## 11. Resumo

O reranking é uma etapa essencial para melhorar a qualidade do RAG da INNA.

Ele ajuda a selecionar os melhores trechos da base de conhecimento antes da resposta final, tornando a INNA mais precisa, segura e confiável.
