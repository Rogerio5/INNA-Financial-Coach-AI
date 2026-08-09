# Week 3 — Sentence-Window Production Decision

## Status

**DECISION=APPROVED**

O Sentence-Window Retrieval foi aprovado tecnicamente para
**rollout controlado em produção**.

A decisão é baseada nos experimentos da Semana 3,
na validação ponta a ponta com cinco perguntas oficiais
e nos testes locais de integração e regressão.

---

## Configuração aprovada para produção

```env
INNA_RAG_SENTENCE_WINDOW_ENABLED=true
INNA_RAG_SENTENCE_WINDOW_SIZE=5
INNA_RAG_SENTENCE_WINDOW_CHUNK_RADIUS=1
INNA_RAG_SENTENCE_WINDOW_MAX_CHARACTERS=4000
INNA_RAG_SENTENCE_WINDOW_ALLOWED_DOCUMENT_KEYS=inna-edu-orcamento-002
INNA_RAG_TOP_K=2
```

### Interpretação

A configuração de produção utiliza:

- Sentence-Window habilitado;
- window size igual a 5;
- raio de chunks igual a 1;
- limite máximo de contexto expandido de 4000 caracteres;
- rollout seletivo inicialmente limitado ao documento
  `inna-edu-orcamento-002`;
- TOP_K global de produção igual a 2.

---

## Estratégia de rollout

O rollout inicial é controlado e seletivo.

Somente o documento:

```text
inna-edu-orcamento-002
```

está autorizado inicialmente para expansão por Sentence-Window.

Resultados pertencentes a documentos fora da allowlist continuam
utilizando o comportamento normal do RAG híbrido.

Isso mantém um fallback seguro durante a ativação progressiva.

---

## Resultado consolidado

```text
QUESTION_COUNT=5
COMPLETED_COUNT=5
FAILED_COUNT=0
QUESTIONS_APPROVED=5_DE_5
END_TO_END_5_QUESTIONS=APPROVED
RECOMMENDATION=promote_sentence_window
```

Na validação ponta a ponta, as cinco perguntas oficiais obtiveram:

```text
Answer Relevancy=1.0000
Faithfulness=1.0000
Contextual Relevancy=1.0000
```

Todos os Quality Gates consolidados foram aprovados.

---

## Configuração final do Sentence-Window

```text
WINDOW_SIZE=5
CHUNK_RADIUS=1
MAX_CHARACTERS=4000
ROLLOUT=CONTROLLED
INITIAL_DOCUMENT_KEY=inna-edu-orcamento-002
GLOBAL_TOP_K=2
```

---

## Pergunta 4

A execução definitiva da Pergunta 4 utilizou:

```text
TOP_K=1
ANSWER_RELEVANCY=1.0000
FAITHFULNESS=1.0000
CONTEXTUAL_RELEVANCY=1.0000
RAG_TRIAD_AVERAGE=1.0000
MAXIMUM_REGRESSION=0.0000
QUALITY_GATE_COMPLETE=True
QUALITY_GATE_PASSED=True
RECOMMENDATION=promote_sentence_window
```

O `TOP_K=1` pertence exclusivamente à execução experimental
definitiva da Pergunta 4.

Ele **não altera o TOP_K global de produção**.

A configuração global permanece:

```env
INNA_RAG_TOP_K=2
```

Execuções anteriores da Pergunta 4 utilizando `TOP_K=2`
são preservadas como evidência intermediária do processo
experimental.

---

## Resultado de desempenho consolidado

```text
MEDIAN_LATENCY_DELTA_MS=-322.0
AVERAGE_LATENCY_DELTA_MS=-895.6
AVERAGE_CONTEXT_CHARACTER_DELTA=-89.8
```

Os valores indicam que, na consolidação final, o Sentence-Window
não introduziu regressão de qualidade e apresentou redução média
de latência e de tamanho de contexto no conjunto avaliado.

---

## Testes de integração

A restauração e integração do Sentence-Window no RAG atual foi
validada localmente com:

```text
28 passed
WEEK3_TESTS=OK
WEEK3_RUFF=OK
WEEK3_DIFF_CHECK=OK
```

Foram verificados:

- feature flag habilitada;
- feature flag desabilitada;
- configuração de window size;
- configuração de chunk radius;
- limite máximo de caracteres;
- allowlist por documento;
- aplicação do Sentence-Window ao documento permitido;
- fallback para documentos não autorizados;
- preservação do RAG baseline quando a feature flag está desligada;
- integração com `search_knowledge_base_hybrid`;
- ausência de regressão nos testes atuais do RAG Engine.

---

## Implementação técnica

Os principais componentes integrados são:

```text
src/rag_engine.py
src/services/rag/sentence_window.py
tests/unit/test_sentence_window.py
tests/unit/test_rag_engine_sentence_window_integration.py
```

A implementação possui telemetria para registrar:

```text
sentence_window_applied
sentence_window_policy
sentence_window_skip_reason
sentence_window_document_key
```

O rollout seletivo utiliza a política:

```text
selective_allowlist
```

---

## Commit técnico

```text
5dc6b20
feat(rag): restore sentence-window retrieval with controlled rollout
```

---

## Custo

A suíte registrou:

```text
TOTAL_ESTIMATED_COST=0.0
```

Esse valor **não significa que o custo real da API foi zero**.

A telemetria utilizada durante a avaliação não possuía preços
de entrada e saída configurados:

```text
MODEL_INPUT_PRICE=None
MODEL_OUTPUT_PRICE=None
COST_CALCULATION_AVAILABLE=False
REAL_BILLED_COST=NOT_VERIFIED
EQUIVALENT_ESTIMATED_COST=NOT_AVAILABLE
```

Portanto:

```text
REAL_API_COST_ZERO=NOT_CONFIRMED
REAL_BILLED_COST=NOT_VERIFIED
```

O valor `0.0` representa somente o acumulador técnico disponível
na suíte durante os experimentos.

---

## Privacidade das evidências

Os relatórios técnicos públicos devem preservar somente:

- métricas;
- hashes;
- configurações;
- resultados agregados;
- decisões técnicas;
- indicadores de qualidade;
- informações operacionais não sensíveis.

Não devem ser publicados:

- respostas completas dos usuários;
- contextos brutos recuperados pelo RAG;
- segredos;
- tokens;
- chaves de API;
- credenciais;
- conteúdo privado de usuários.

---

## Técnicas futuras

Auto-Merging Retrieval, Knowledge Graph e GraphRAG ficam
classificados como evoluções posteriores à Semana 3.

Esses itens não bloqueiam a conclusão da validação atual do
Sentence-Window.

---

## Estado final da Semana 3

```text
WEEK3_FINAL_DECISION=APPROVED
SENTENCE_WINDOW_PRODUCTION_APPROVED=True
SENTENCE_WINDOW_ROLLOUT=CONTROLLED
SENTENCE_WINDOW_ENABLED=True
WINDOW_SIZE=5
CHUNK_RADIUS=1
MAX_CHARACTERS=4000
INITIAL_DOCUMENT_KEY=inna-edu-orcamento-002
GLOBAL_TOP_K=2
QUESTION_4_FINAL_TOP_K=1
QUALITY_GATE=5/5_APPROVED
FAILED_QUESTIONS=0
RECOMMENDATION=promote_sentence_window
IMPLEMENTATION_COMMIT=5dc6b20
```

## Situação operacional

A implementação foi aprovada tecnicamente e está pronta para
integração na branch principal.

A confirmação operacional definitiva do Sentence-Window será
realizada após:

```text
merge na main
deploy da inna-api
smoke test real
POST /rag/ask = 200 OK
confirmação de sentence_window_applied=True
```

Somente após essa última evidência o estado operacional poderá ser
registrado como:

```text
SENTENCE_WINDOW_PRODUCTION_CONFIRMED=True
```
