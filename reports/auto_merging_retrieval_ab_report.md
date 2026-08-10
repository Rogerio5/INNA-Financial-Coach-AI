# Auto-Merging Retrieval — Experimento A/B/C

Comparação isolada entre:

- Hybrid Baseline
- Hybrid + Sentence Window
- Hybrid + Auto-Merging

## Resumo

| Variante | Queries | Retrieval médio ms | Contexto médio chars | Resultados médios | Auto-Merges | Sentence Windows |
|---|---:|---:|---:|---:|---:|---:|
| hybrid_baseline | 6 | 2464.7 | 2774.33 | 3.0 | 0 | 0 |
| hybrid_sentence_window | 6 | 2236.03 | 2708.67 | 3.0 | 0 | 3 |
| hybrid_auto_merging | 6 | 2234.16 | 2776.0 | 2.17 | 5 | 0 |

## Política experimental

Sentence Window e Auto-Merging são avaliados isoladamente nesta fase.

Nenhuma variante experimental é ativada automaticamente em produção.