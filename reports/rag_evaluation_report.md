# Resumo Executivo — Avaliação do RAG INNA

Total de perguntas avaliadas: **8**
Aprovadas: **8**
Atenção: **0**
Revisar: **0**
Taxa de aprovação: **100.0%**

## Interpretação

A avaliação verifica se a INNA usa RAG híbrido, reranking, fontes recuperadas, resposta com Gemini quando adequado e fallback controlado em perguntas com cálculo.

---

# Relatório de Avaliação do RAG — INNA

Data da avaliação: **2026-07-02 00:56:03**

## Objetivo

Avaliar a qualidade do RAG da INNA considerando busca híbrida, pgvector, busca textual, reranking, uso do Gemini quando adequado e fallback controlado para cálculos financeiros.

## Resultados

### 1. Reserva financeira

**Pergunta:** como posso começar uma reserva financeira?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7870500688976965 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.7604390715990917 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7511170506471193 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Vamos por partes. Vou te orientar de um jeito simples:
> 
> 1. Veja quanto entra e quanto sai todo mês com contas, mercado, transporte, compras e parcelas.
> 2. Separe um valor pequeno que caiba no seu bolso, sem apertar demais.
> 3. Não use esse dinheiro para compras do dia a dia.
> 4. Olhe todo mês se conseguiu guardar alguma quantia, mesmo que seja pouco.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 2. Cálculo controlado

**Pergunta:** ganho 3000 gasto 2500 e guardo 100

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, calculo_controlado_sem_gemini, calculo_com_meta, tema_correto, resposta_completa

**Fontes recuperadas:**

- Financeiro Basico | score: 0.6281332175938811 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.612221015976625 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6249952841481666 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Entendi sua anotação. Vou te orientar de forma simples.
> 
> - Renda informada: R$ 3.000 por mês.
> - Gasto informado: R$ 2.500 por mês.
> - Valor que você disse que consegue guardar: R$ 100 por mês.
> 
> Uma forma fácil de começar é dividir esse valor por semana:
> 
> - Meta no mês: R$ 100
> - Meta por semana: cerca de R$ 25
> 
> Meta desta semana:
> 
> 1. Separe cerca de R$ 25 nesta semana.
> 2. Guarde esse valor assim que receber ou assim que sobrar.
> 3. Evite usar esse dinheiro para compras do dia a dia.
> 4. No fim da semana, veja se conseguiu manter esse valor guardado.
> 
> Orientação simples:
> Se uma semana apertar, guarde menos. O importante é começar e manter o costume.
> 
> Quer que eu mostre como ficaria essa meta no mês inteiro?

---

### 3. Cartão de crédito

**Pergunta:** cartão de crédito está me apertando

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 9/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, seguranca_educativa, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.660687810660314 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7130954941123786 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7009234649711438 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Com base na base de conhecimento da INNA, a orientação educativa é:
> 
> 1. Organize seus dados financeiros.
> 2. Compare renda, gastos, dívidas e reserva.
> 3. Priorize ações simples e mensuráveis.
> 4. Evite decisões financeiras arriscadas sem orientação profissional.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 4. Organização de gastos

**Pergunta:** como organizar gastos fixos e variáveis?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7014182371804327 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6474803236607236 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.6518220338707291 | fonte: `data/knowledge_base/financeiro_basico.md`

**Resposta gerada:**

> Olá! Que bom que você veio conversar comigo. Sou a INNA e estou aqui para te ajudar a entender melhor o seu dinheiro, de um jeito bem fácil. Vamos lá!
> 
> Sobre organizar seus gastos fixos e variáveis, vou te orientar de forma simples. Pense assim:
> 
> **1. Descobrir para onde o dinheiro vai:**
> *   Primeiro, vamos entender quanto dinheiro entra por mês na sua casa.
> *   Depois, vamos anotar tudo o que sai. Sabe, as contas que a gente paga, o que a gente compra no mercado, o transporte, um lanchinho... tudo mesmo!
> 
> **2. Separar as contas:**
> *   **Gastos Fixos:** São aqueles que vêm todo mês com o mesmo valor, como o aluguel, a mensalidade da escola, ou a conta de luz (que pode variar um pouquinho, mas é algo que você sabe que vai ter).
> *   **Gastos Variáveis:** São os gastos que mudam todo mês, dependendo do que você usa ou compra. Por exemplo, a comida do mercado, a gasolina do carro, um passeio no fim de semana, uma roupa nova.
> *   **Dívidas:** Se você tiver alguma dívida, é bom anotar também, para não esquecer.
> 
> **Um caminho possível é:** pegue um caderninho ou um aplicativo e anote tudo por um mês. No fim desse mês, você vai ter uma ideia bem clara de onde o seu dinheiro está sendo usado.
> 
> O importante é começar! Assim, você vai vendo se sobra algum dinheiro no final do mês ou onde dá para ajustar um pouquinho para começar a guardar.
> 
> Ficou mais claro para você como começar a organizar esses gastos?

---

### 5. Dívidas

**Pergunta:** como sair das dívidas?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Financeiro Basico | score: 0.734657414261252 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.7309024114663539 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7416262597189681 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Vamos por partes. O melhor caminho para reduzir suas dívidas é:
> 
> 1. Liste todas as dívidas, parcelas, juros e vencimentos.
> 2. Priorize o pagamento das dívidas mais caras ou com maior impacto no orçamento.
> 3. Evite assumir novas dívidas durante o plano de organização.
> 4. Negocie condições melhores quando possível.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 6. Reserva emergencial

**Pergunta:** o que é reserva de emergência?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Financeiro Basico | score: 0.7119344188884856 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.6888318318859966 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6602684278515575 | fonte: `data/knowledge_base/financeiro_basico.md`

**Resposta gerada:**

> Vamos por partes. Vou te orientar de um jeito simples:
> 
> 1. Veja quanto entra e quanto sai todo mês com contas, mercado, transporte, compras e parcelas.
> 2. Separe um valor pequeno que caiba no seu bolso, sem apertar demais.
> 3. Não use esse dinheiro para compras do dia a dia.
> 4. Olhe todo mês se conseguiu guardar alguma quantia, mesmo que seja pouco.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 7. Gastos pequenos

**Pergunta:** gasto muito com pequenas compras, como posso organizar?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7067015603385549 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6972376313889488 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6777007932644881 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Vamos por partes. O melhor caminho para organizar seus gastos é:
> 
> 1. Separe seus gastos em fixos, variáveis e dívidas.
> 2. Identifique gastos pequenos recorrentes que podem ser reduzidos.
> 3. Defina um limite semanal para despesas variáveis.
> 4. Revise seu orçamento ao final de cada mês.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 8. Parcelas

**Pergunta:** tenho muitas parcelas no cartão, por onde começo?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 9/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, seguranca_educativa, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.8057115493327506 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7879543222181152 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.8240515497733375 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Com base na base de conhecimento da INNA, a orientação educativa é:
> 
> 1. Organize seus dados financeiros.
> 2. Compare renda, gastos, dívidas e reserva.
> 3. Priorize ações simples e mensuráveis.
> 4. Evite decisões financeiras arriscadas sem orientação profissional.
> 
> Quer que eu monte uma meta simples para esta semana?

---
