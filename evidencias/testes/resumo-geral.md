# Evidencias de Testes da INNA

Relatorio consolidado por ownership principal.

## Resultado geral

- Modulos: **12**
- Arquivos classificados: **402**
- Execucoes de testes: **4961**
- Passed: **4958**
- Skipped: **3**
- Failures: **0**
- Errors: **0**
- Tempo acumulado: **119.03s**

> O total de execucoes por modulo nao deve ser comparado
> diretamente com a regressao global de 4958 testes.
> Este relatorio representa execucoes separadas por ownership.

## Resultado por modulo

| Modulo | Arquivos | Passed | Skipped | Failed | Errors | Tempo |
|---|---:|---:|---:|---:|---:|---:|
| a2a | 5 | 18 | 0 | 0 | 0 | 5.11s |
| admin_ui | 19 | 122 | 0 | 0 | 0 | 5.81s |
| avaliacao_llmops | 57 | 1268 | 1 | 0 | 0 | 27.61s |
| financeiro | 31 | 358 | 0 | 0 | 0 | 14.34s |
| infra_compartilhada | 17 | 122 | 0 | 0 | 0 | 4.62s |
| mcp | 7 | 32 | 0 | 0 | 0 | 4.10s |
| observabilidade | 35 | 231 | 0 | 0 | 0 | 5.68s |
| plataforma | 62 | 698 | 2 | 0 | 0 | 15.73s |
| rag | 74 | 521 | 0 | 0 | 0 | 15.27s |
| resiliencia | 19 | 208 | 0 | 0 | 0 | 6.49s |
| seguranca | 1 | 3 | 0 | 0 | 0 | 0.06s |
| telegram | 75 | 1377 | 0 | 0 | 0 | 14.21s |

## Evidencias disponiveis

Cada modulo possui:

- `manifest.txt`
- `resumo.md`
- `pytest.txt`
- `junit.xml`

Os testes oficiais continuam localizados em `tests/`.

## Baseline global

- Regressao completa: **4958 passed**
- Skipped esperados: **3**
- Failures: **0**
- Errors: **0**
