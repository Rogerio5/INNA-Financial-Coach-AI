# Semana 5 — Melhorias Adicionais de Production Readiness

## INNA Financial Coach AI

Esta documentação registra as melhorias adicionais de **Production Readiness** implementadas durante a Semana 5 do projeto INNA Financial Coach AI.

O objetivo desta evolução foi tornar a arquitetura mais adaptativa, resiliente, observável e preparada para operação em produção, complementando os conteúdos da Semana 5 relacionados a:

- produção de aplicações de IA;
- Agentic RAG;
- sistemas multiagentes;
- avaliação contínua;
- observabilidade;
- governança;
- segurança operacional;
- escalabilidade;
- operação de agentes em ambientes corporativos.

Estas implementações são consideradas **extensões adicionais e avançadas da Semana 5**.

As atividades específicas relacionadas ao Google Cloud, como Cloud Run, Artifact Registry, Cloud Build e Vertex AI Evaluation, serão documentadas separadamente.

---

# 1. Objetivo da melhoria

A evolução teve como objetivo transformar o Planner do Agentic RAG em um componente capaz de escolher dinamicamente a estratégia mais apropriada para cada solicitação.

Antes, uma estratégia única poderia ser aplicada independentemente da complexidade da consulta.

Com a evolução, a INNA passou a utilizar:

```text
Consulta
   |
   v
Adaptive Planner
   |
   +-- Simple
   |      |
   |      +--> Deterministic Planner
   |
   +-- Complex
          |
          +--> Redis
                 |
                 +-- HIT
                 |    |
                 |    +--> reutiliza plano validado
                 |
                 +-- MISS
                      |
                      v
                    Gemini
                      |
                      v
                 validação
                      |
             +--------+--------+
             |                 |
           válido           inválido/falha
             |                 |
             v                 v
          utiliza       deterministic fallback
```

Essa arquitetura reduz chamadas desnecessárias ao LLM e permite combinar:

- previsibilidade;
- desempenho;
- cache;
- inteligência generativa;
- resiliência;
- observabilidade.

---

# 2. Adaptive Planner

O Planner foi evoluído para suportar execução adaptativa.

Configuração utilizada:

```text
INNA_AGENTIC_RAG_PLANNER_MODE=adaptive
```

O modo `adaptive` decide como cada solicitação deve ser planejada.

Ele não significa que todas as consultas utilizarão Gemini.

O fluxo é:

```text
Adaptive Planner
       |
       v
Complexity Detector
       |
   +---+---+
   |       |
 simple  complex
   |       |
   v       v
deterministic
          |
          v
        Redis
       /     \
     HIT     MISS
      |        |
      v        v
    cache    Gemini
                |
                v
            validation
                |
           +----+----+
           |         |
         valid     invalid/failure
           |         |
           v         v
        execute   fallback
```

---

# 3. Classificação de complexidade

A decisão entre `simple` e `complex` é realizada por regras determinísticas.

Isso evita gastar tokens apenas para decidir se uma requisição precisa ou não de um LLM.

O detector considera sinais como:

- comparação;
- análise de risco;
- múltiplos objetivos;
- múltiplos conectores;
- múltiplas perguntas;
- consultas longas;
- necessidade de histórico financeiro;
- outros sinais estruturais da solicitação.

O threshold utilizado atualmente é:

```text
score >= 2 -> complex
score < 2  -> simple
```

Exemplo de consulta simples:

```text
O que é uma reserva de emergência?
```

Resultado observado:

```text
query_complexity = simple
planner_route    = deterministic
```

Exemplo de consulta complexa:

```text
Explique juros compostos e compare com juros simples,
destacando as principais diferenças e também os riscos,
depois apresente três exemplos práticos de aplicação.
```

Resultado:

```text
query_complexity = complex
```

---

# 4. Planner determinístico

Consultas classificadas como simples podem ser tratadas por uma estratégia determinística.

Fluxo:

```text
Simple Request
      |
      v
Deterministic Planner
      |
      v
Research Plan
```

Essa abordagem possui algumas vantagens:

- latência muito baixa;
- comportamento previsível;
- ausência de custo de LLM para planejamento;
- menor risco de respostas estruturais inesperadas.

Em produção foi observado:

```text
planner_mode     = adaptive
query_complexity = simple
planner_route    = deterministic
cache_hit        = false
plan_source      = deterministic
plan_valid       = true
fallback_used    = false
planner_outcome  = success
duration_ms      = 1.26
```

---

# 5. Planejamento complexo com Gemini

Quando uma requisição é classificada como complexa, o Planner pode utilizar Gemini para gerar um plano mais elaborado.

Fluxo:

```text
Complex Request
      |
      v
Redis Cache
      |
    MISS
      |
      v
Gemini Planner
      |
      v
Generated Plan
```

Em produção foi comprovada uma execução real:

```text
planner_mode     = adaptive
query_complexity = complex
planner_route    = gemini
cache_hit        = false
plan_source      = gemini
plan_valid       = true
fallback_used    = false
planner_outcome  = success
duration_ms      = 6807.35
```

---

# 6. Cache inteligente com Redis

Para evitar geração repetida do mesmo plano complexo, a arquitetura utiliza Redis.

Fluxo:

```text
Complex Request
      |
      v
Redis
  |
  +-- HIT
  |    |
  |    +--> utiliza plano validado do cache
  |
  +-- MISS
       |
       +--> Gemini
             |
             +--> valida plano
             |
             +--> armazena plano válido
```

O cache possui versionamento e utiliza informações normalizadas para construir sua chave.

A arquitetura também foi projetada de forma **fail-open**.

Isso significa que:

```text
Redis indisponível
      |
      v
Planner continua funcionando
```

A indisponibilidade do cache não deve interromper a INNA.

---

# 7. Redis MISS e HIT comprovados em produção

Foi realizada uma prova controlada em produção.

Primeira execução da consulta complexa:

```text
Redis MISS
   |
   v
Gemini
```

Resultado:

```text
planner_route   = gemini
cache_hit       = false
plan_source     = gemini
planner_outcome = success
duration_ms     = 6807.35
```

A mesma pergunta foi enviada novamente.

Segunda execução:

```text
Redis HIT
```

Resultado:

```text
planner_route   = redis_hit
cache_hit       = true
plan_source     = cache
planner_outcome = success
duration_ms     = 3.56
```

Isso demonstrou uma redução significativa de latência no planejamento de consultas repetidas.

Comparação observada:

```text
Gemini    = 6807.35 ms
Redis HIT =    3.56 ms
```

---

# 8. Validação pós-LLM

Planos gerados pelo Gemini não são utilizados automaticamente.

Antes da execução, passam por validação.

Fluxo:

```text
Gemini
   |
   v
Generated Plan
   |
   v
Semantic Validation
   |
   +-- Valid
   |     |
   |     +--> aceita
   |
   +-- Invalid
         |
         +--> deterministic fallback
```

A validação ajuda a evitar que planos inválidos sejam:

- utilizados;
- executados;
- armazenados em cache.

---

# 9. Validação do cache

Planos recuperados do Redis também precisam continuar válidos.

O fluxo inclui validação antes da utilização.

```text
Redis HIT
   |
   v
Cached Plan
   |
   v
Validation
   |
   +-- valid
   |     |
   |     +--> utiliza cache
   |
   +-- invalid
         |
         +--> ignora cache
         |
         +--> gera novo plano
```

Isso evita reutilizar indefinidamente estruturas antigas ou inválidas.

---

# 10. Deterministic Fallback

Caso Gemini falhe ou produza um plano inválido, a INNA possui fallback determinístico.

Fluxo:

```text
Complex Request
      |
      v
Gemini
      |
   failure
      |
      v
Deterministic Fallback
```

Objetivos do fallback:

- manter disponibilidade;
- reduzir falhas de runtime;
- evitar dependência absoluta do LLM;
- garantir comportamento previsível;
- aumentar resiliência.

A rota possui representação própria nas métricas:

```text
planner_route    = fallback
plan_source      = deterministic
cache_hit        = false
plan_valid       = true
fallback_used    = true
planner_outcome  = fallback
```

---

# 11. Terminal Error Handling

Também foi criado um contrato explícito para situações em que o Planner realmente termina em erro.

Formato do evento:

```text
planner_mode     = adaptive
query_complexity = unknown
planner_route    = error
cache_hit        = false
plan_source      = none
plan_valid       = false
fallback_used    = false
planner_outcome  = error
```

O erro original continua sendo propagado.

A coleta da métrica não substitui a exceção original.

Fluxo:

```text
Planner
   |
terminal exception
   |
   +--> registra evento error
   |
   +--> preserva exceção original
```

---

# 12. Fail-open de observabilidade

A observabilidade não deve derrubar o sistema principal.

Por isso, a persistência das métricas também utiliza estratégia fail-open.

```text
Planner executa
      |
      v
Metrics Writer
      |
   erro no DB
      |
      v
Planner continua
```

Se o banco responsável pelas métricas estiver temporariamente indisponível, a operação principal não deve ser interrompida apenas por falha de telemetria.

---

# 13. Métricas operacionais dedicadas

Foi criada uma fonte dedicada para os eventos do Planner:

```text
planner_metric_events_inna
```

Essa fonte registra somente informações operacionais.

Campos principais:

```text
planner_mode
query_complexity
planner_route
cache_hit
plan_source
plan_valid
fallback_used
duration_ms
planner_outcome
```

---

# 14. Outcomes suportados

Foram definidos três resultados finais:

```text
success
fallback
error
```

Significado:

### success

O Planner terminou normalmente.

Exemplos:

```text
deterministic
gemini
redis_hit
```

### fallback

Uma estratégia principal falhou, mas o fallback conseguiu continuar.

Exemplo:

```text
Gemini failure
   |
   v
deterministic fallback
```

### error

O Planner não conseguiu concluir a operação.

```text
terminal error
```

---

# 15. Rotas operacionais suportadas

As rotas atuais são:

```text
deterministic
gemini
redis_hit
fallback
error
```

Isso permite medir separadamente como o Planner está operando em produção.

---

# 16. Privacidade das métricas

As métricas foram desenhadas para não armazenar conteúdo do usuário.

Não são persistidos:

```text
question
prompt
response
user_id
subqueries
cache_key
error_message
exception message
```

A fonte contém apenas metadados operacionais.

Objetivo:

```text
observabilidade
sem exportar conteúdo sensível
```

---

# 17. Prova real de persistência no Neon

O writer das métricas foi validado diretamente no PostgreSQL/Neon.

Foram comprovadas as cinco rotas:

```text
deterministic
gemini
redis_hit
fallback
error
```

Também foram comprovados os três outcomes:

```text
success
fallback
error
```

Os dados utilizados na prova foram sintéticos e posteriormente removidos.

Resultado:

```text
SYNTHETIC_WRITE_RESULT_COUNT=5
ALL_SYNTHETIC_WRITES_GREEN=True

SYNTHETIC_ROWS_FOUND=5
ALL_5_ROUTES_PERSISTED=True
ALL_3_OUTCOMES_PERSISTED=True

PERSISTED_ROWS_PRIVACY_SAFE=True

SYNTHETIC_ROWS_DELETED=5
SYNTHETIC_ROWS_REMAINING=0
SYNTHETIC_CLEANUP_GREEN=True
```

---

# 18. Observabilidade com Phoenix / OpenTelemetry

A INNA utiliza Phoenix/OpenTelemetry para tracing e diagnóstico.

A arquitetura diferencia dois tipos de observabilidade:

```text
Phoenix / OpenTelemetry
        |
        +--> tracing
        +--> diagnóstico
        +--> análise de execução

Planner Metric Events
        |
        +--> métricas exatas
        +--> SLO
        +--> indicadores operacionais
```

Phoenix pode trabalhar com sampling.

As métricas dedicadas do Planner são utilizadas para estatísticas operacionais completas.

---

# 19. Planner SLO Aggregator

Foi criado o módulo:

```text
src/observability/planner_slo.py
```

Responsabilidade:

```text
planner_metric_events_inna
          |
          v
Planner SLO Aggregator
          |
          +--> success rate
          +--> fallback rate
          +--> error rate
          +--> route distribution
          +--> cache hit rate
          +--> AVG latency
          +--> P95 latency
```

---

# 20. Métricas disponíveis no SLO

Atualmente são calculadas:

```text
total_plans
clean_success_rate
terminal_success_rate
fallback_rate
planner_error_rate
deterministic_route_rate
gemini_route_rate
complex_cache_hit_rate
average_duration
p95_duration
```

---

# 21. Clean Success Rate

Representa execuções concluídas diretamente com `success`.

Fórmula:

```text
success
-------
total
```

---

# 22. Terminal Success Rate

Representa solicitações que conseguiram terminar operacionalmente, incluindo fallback bem-sucedido.

Fórmula:

```text
success + fallback
------------------
total
```

Essa métrica diferencia:

```text
execução perfeita
```

de:

```text
execução recuperada por fallback
```

---

# 23. Fallback Rate

Representa a proporção de solicitações que precisaram usar fallback.

```text
fallback
--------
total
```

Um crescimento anormal dessa métrica pode indicar problemas em:

- Gemini;
- validação;
- cache;
- infraestrutura;
- configuração.

---

# 24. Planner Error Rate

Representa execuções que terminaram em erro.

```text
error
-----
total
```

Essa é uma das métricas que futuramente poderá participar de um Promotion Gate.

---

# 25. Cache Hit Rate

Para consultas complexas, é importante acompanhar quantas vezes Redis consegue reutilizar um plano.

Métrica:

```text
redis_hit
---------
complex_requests
```

Isso permite acompanhar a eficiência do cache.

---

# 26. Gemini Route Rate

Outra métrica operacional importante é a quantidade de consultas que realmente precisam utilizar Gemini.

```text
gemini
------
total
```

Ela ajuda a acompanhar:

- custo;
- latência;
- dependência de LLM;
- comportamento do Adaptive Planner.

---

# 27. Deterministic Route Rate

Também é registrada a quantidade de consultas solucionadas pelo Planner determinístico.

```text
deterministic
-------------
total
```

Essa métrica ajuda a demonstrar quanto trabalho pode ser realizado sem necessidade de LLM.

---

# 28. Latência média

O Planner registra a duração completa do planejamento.

O agregador calcula:

```text
AVG duration_ms
```

Essa métrica permite acompanhar desempenho médio.

---

# 29. P95

Também é calculado o percentil 95 da latência.

```text
P95 duration_ms
```

O P95 ajuda a responder:

> Quanto tempo demora o Planner para aproximadamente 95% das execuções?

Essa métrica é mais útil que apenas a média quando existem chamadas mais lentas, como as que dependem de Gemini.

---

# 30. Baseline inicial

O primeiro snapshot real em produção foi:

```text
SLO_WINDOW_HOURS=24

TOTAL_PLANS=3

CLEAN_SUCCESS_RATE_PCT=100.0

TERMINAL_SUCCESS_RATE_PCT=100.0

FALLBACK_RATE_PCT=0.0

PLANNER_ERROR_RATE_PCT=0.0

DETERMINISTIC_ROUTE_RATE_PCT=33.33

GEMINI_ROUTE_RATE_PCT=33.33

COMPLEX_CACHE_HIT_RATE_PCT=50.0

AVG_DURATION_MS=2270.72

P95_DURATION_MS=6126.97
```

---

# 31. Interpretação do P95 atual

O valor:

```text
P95 = 6126.97 ms
```

ainda não deve ser interpretado como limite definitivo.

O motivo é que o baseline possui apenas:

```text
3 execuções
```

Uma das execuções foi uma chamada real ao Gemini de aproximadamente:

```text
6807.35 ms
```

Com uma amostra tão pequena, essa chamada influencia fortemente o percentil.

Por isso:

```text
BASELINE_SAMPLE_IS_SMALL=True
BASELINE_READY_FOR_FINAL_SLO=False
```

A coleta continuará em produção antes da definição dos thresholds finais.

---

# 32. SHADOW Rollout

A configuração atual permanece:

```text
INNA_AGENTIC_RAG_MODE=shadow
INNA_AGENTIC_RAG_PLANNER_MODE=adaptive
INNA_PLANNER_METRICS_ENABLED=true
```

O modo SHADOW permite validar o comportamento do Agentic RAG antes de uma eventual promoção.

---

# 33. Diferença entre Adaptive e SHADOW

Esses conceitos possuem responsabilidades diferentes.

## Adaptive

Decide como a consulta deve ser planejada.

```text
simple
   |
deterministic

complex
   |
Redis / Gemini / fallback
```

## SHADOW

Controla o nível de exposição do Agentic RAG.

```text
Agentic RAG
    |
 SHADOW
```

Portanto:

```text
adaptive != shadow
```

E também:

```text
complex != active
simple  != shadow
```

Uma consulta complexa pode ser processada enquanto o Agentic RAG continua em SHADOW.

Isso foi comprovado em produção.

---

# 34. SHADOW e ACTIVE

A decisão entre SHADOW e ACTIVE é operacional.

```text
SHADOW
   |
   v
coleta de baseline
   |
   v
SLO
   |
   v
avaliação de estabilidade
   |
   v
Promotion Gate
   |
   v
ACTIVE
```

O Adaptive Planner não alterna automaticamente entre SHADOW e ACTIVE.

---

# 35. ACTIVE

O modo ACTIVE deverá ser considerado somente depois de existir evidência operacional suficiente.

Antes da promoção, deverão ser avaliados indicadores como:

```text
terminal_success_rate
planner_error_rate
fallback_rate
p95_duration
complex_cache_hit_rate
gemini_route_rate
```

Também poderão ser avaliados aspectos de custo.

---

# 36. Promotion Gate futuro

Uma evolução futura poderá implementar uma política formal de promoção.

Exemplo:

```text
SHADOW
   |
   v
Operational Baseline
   |
   v
SLO Evaluation
   |
   +-- error rate aceitável
   |
   +-- fallback rate aceitável
   |
   +-- P95 aceitável
   |
   +-- cache eficiente
   |
   +-- custo Gemini aceitável
   |
   v
Promotion Gate
   |
   +-- reprova --> SHADOW
   |
   +-- aprova --> CANARY / ACTIVE
```

---

# 37. Possível estratégia de Canary

Uma evolução futura poderá utilizar rollout progressivo.

Exemplo:

```text
SHADOW
   |
   v
CANARY 5%
   |
   v
CANARY 25%
   |
   v
CANARY 50%
   |
   v
ACTIVE
```

Com rollback automático caso alguma métrica piore.

---

# 38. Arquitetura final da melhoria

A arquitetura desta evolução ficou:

```text
User Request
     |
     v
Supervisor
     |
     v
Specialized Agent
     |
     v
Agentic RAG
     |
     v
Adaptive Planner
     |
     +-----------------------+
     |                       |
   simple                  complex
     |                       |
     v                       v
deterministic             Redis
                          /   \
                        HIT   MISS
                         |      |
                         v      v
                       cache  Gemini
                               |
                               v
                           validation
                               |
                         +-----+-----+
                         |           |
                       valid      invalid
                         |           |
                         v           v
                      execute     fallback
                                      |
                                      v
                               deterministic

            |
            v

Planner Metric Events
            |
            v
PostgreSQL / Neon
            |
            v
Planner SLO Aggregator
            |
     +------+------+------+------+
     |      |      |      |      |
 success fallback error cache latency/P95
```

---

# 39. Segurança operacional

A melhoria possui diferentes mecanismos para reduzir risco:

```text
deterministic path
Redis fail-open
LLM validation
cache validation
deterministic fallback
terminal error contract
metrics fail-open
SHADOW rollout
privacy-safe telemetry
```

---

# 40. Avaliação contínua

A INNA já possui diferentes camadas complementares:

```text
DeepEval
   |
   +--> avaliação de qualidade

Phoenix / OpenTelemetry
   |
   +--> tracing

Planner Metrics
   |
   +--> métricas operacionais

Planner SLO
   |
   +--> confiabilidade e latência
```

Essa arquitetura permite separar:

```text
qualidade
observabilidade
confiabilidade
desempenho
```

---

# 41. Evidências de produção

## Simple -> Deterministic

```text
planner_mode     = adaptive
query_complexity = simple
planner_route    = deterministic
cache_hit        = false
plan_source      = deterministic
plan_valid       = true
fallback_used    = false
planner_outcome  = success
duration_ms      = 1.26
```

## Complex -> Gemini

```text
planner_mode     = adaptive
query_complexity = complex
planner_route    = gemini
cache_hit        = false
plan_source      = gemini
plan_valid       = true
fallback_used    = false
planner_outcome  = success
duration_ms      = 6807.35
```

## Complex -> Redis HIT

```text
planner_mode     = adaptive
query_complexity = complex
planner_route    = redis_hit
cache_hit        = true
plan_source      = cache
plan_valid       = true
fallback_used    = false
planner_outcome  = success
duration_ms      = 3.56
```

---

# 42. Testes

A evolução foi protegida por testes automatizados.

Resultado final da regressão:

```text
50 passed
```

Qualidade:

```text
Ruff
All checks passed!
```

O agregador SLO possui testes específicos para:

- cálculo de taxas;
- denominadores zero;
- valores de duração inválidos;
- fail-open;
- privacidade;
- janela temporal.

Resultado:

```text
6 passed
```

---

# 43. Commits principais

## Adaptive Planner

```text
3c088e1
feat: adiciona planner adaptativo com cache seguro
```

## Métricas operacionais

```text
01f7dec
feat: adiciona metricas SLO ao planner adaptativo
```

## Agregador SLO

```text
bc7691d
feat: adiciona agregador SLO do planner adaptativo
```

O commit final:

```text
bc7691d
```

foi publicado e implantado em produção.

---

# 44. Status final

```text
Adaptive Planner                     ✅
Simple -> deterministic              ✅
Complex -> Gemini                    ✅
Redis MISS                           ✅
Redis HIT                            ✅
Cache V2                             ✅
Validação pós-LLM                    ✅
Validação de plano cacheado          ✅
Deterministic fallback               ✅
Terminal error contract              ✅
Fail-open                            ✅
Planner metrics                      ✅
PostgreSQL / Neon persistence        ✅
Privacy-safe telemetry               ✅
Planner SLO Aggregator               ✅
Average latency                      ✅
P95                                  ✅
Phoenix / OpenTelemetry              ✅
SHADOW rollout                       ✅
Produção                             ✅
ACTIVE                               ⏳ não promovido
Baseline final                       ⏳ coletando
```

---

# 45. Classificação dentro da Semana 5

Esta evolução deve ser registrada como:

> **Melhorias adicionais de Production Readiness — Semana 5**

Ela complementa os conteúdos da semana relacionados a:

- produção em escala;
- Agentic RAG;
- observabilidade;
- avaliação contínua;
- governança;
- segurança operacional;
- confiabilidade;
- arquiteturas corporativas;
- operação de agentes.

---

# 46. Relação com a trilha principal da Semana 5

A trilha da Semana 5 trabalha temas como:

```text
LLM / Agent / RAG Evaluation
Agentic RAG
MCP
A2A
Deploy
Observability
Monitoring
Cloud Infrastructure
Advanced RAG
Scalable Architecture
Governance
```

As melhorias registradas neste documento aprofundam principalmente:

```text
Agentic RAG
Observability
Continuous Evaluation
Reliability
Governance
Scalable Architecture
Production Readiness
```

---

# 47. O que não pertence a esta melhoria

Não foram realizadas nesta etapa migrações para:

```text
Cloud Run
GKE
Cloud SQL
AlloyDB
Vertex AI Evaluation
Cloud Monitoring
```

Esses itens fazem parte da próxima evolução específica de infraestrutura Google Cloud.

---

# 48. Próxima etapa da Semana 5

A próxima parte será documentada separadamente em:

```text
docs/semana-5/cloud-deployment.md
```

A prioridade será:

```text
GitHub
   |
   v
Docker
   |
   v
Artifact Registry
   |
   v
Cloud Build
   |
   v
Cloud Run
   |
   v
INNA API
```

---

# 49. Melhorias Google Cloud planejadas

## Prioridade principal

```text
Cloud Run
Artifact Registry
Cloud Build
```

Objetivo:

> Demonstrar deployment real de uma aplicação de IA Generativa e agentes em infraestrutura Google Cloud.

## Melhoria adicional recomendada

```text
Vertex AI Evaluation
```

Objetivo:

> Complementar DeepEval e as métricas próprias da INNA com avaliação de qualidade em ambiente Google Cloud.

---

# 50. Arquitetura futura

Uma evolução possível:

```text
                     Google Cloud

GitHub
   |
   v
Cloud Build
   |
   v
Artifact Registry
   |
   v
Cloud Run
   |
   v
INNA API
   |
   +--> Supervisor
   |
   +--> LangGraph
   |
   +--> Specialized Agents
   |
   +--> Agentic RAG
   |
   +--> Adaptive Planner
   |       |
   |       +--> deterministic
   |       +--> Redis
   |       +--> Gemini
   |       +--> fallback
   |
   +--> A2A
   |
   +--> Observability
   |
   +--> Planner SLO
   |
   v
PostgreSQL / Neon
```

O banco PostgreSQL/Neon poderá permanecer inicialmente, evitando uma migração desnecessária apenas para demonstrar deployment cloud.

---

# 51. Conclusão

A melhoria adicional da Semana 5 evoluiu o Agentic RAG da INNA para uma arquitetura mais preparada para produção.

O sistema passou a possuir:

```text
Adaptive Planning
Complexity Routing
Deterministic Planning
Gemini Planning
Redis Caching
Semantic Validation
Deterministic Fallback
Terminal Error Handling
Fail-open Observability
Operational Metrics
SLO Aggregation
P95 Monitoring
SHADOW Rollout
```

A arquitetura também passou a gerar evidências operacionais suficientes para acompanhar:

```text
success
fallback
errors
cache
Gemini usage
latency
P95
```

O sistema permanece em:

```text
INNA_AGENTIC_RAG_MODE=shadow
```

enquanto acumula um baseline maior.

A promoção futura para ACTIVE deverá ocorrer somente depois da análise das métricas e da definição de limites SLO adequados.

Com isso, esta etapa é considerada concluída como uma:

> **Extensão avançada de Production Readiness da Semana 5 do projeto INNA Financial Coach AI.**

A próxima evolução será a implementação da camada específica de **Google Cloud**, começando por:

```text
Cloud Run
Artifact Registry
Cloud Build
```

e, opcionalmente:

```text
Vertex AI Evaluation
Cloud Monitoring / Trace
```