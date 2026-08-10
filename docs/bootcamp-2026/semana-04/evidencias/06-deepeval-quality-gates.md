# DeepEval e Quality Gates

## Classificacao

**APLICADO / VALIDADO**

## O que esta evidencia demonstra

DeepEval esta integrado a executores, metricas, testes e pipelines de avaliacao, com gates automatizados.

## Implementacao e arquitetura

- [src/evaluation/deepeval_metrics.py](../../../../src/evaluation/deepeval_metrics.py)
- [src/evaluation/deepeval_executors.py](../../../../src/evaluation/deepeval_executors.py)
- [src/evaluation/final_regression/runner.py](../../../../src/evaluation/final_regression/runner.py)

## Testes

- [tests/evaluations/test_deepeval_metrics.py](../../../../tests/evaluations/test_deepeval_metrics.py)
- [tests/evaluations/test_deepeval_executors.py](../../../../tests/evaluations/test_deepeval_executors.py)
- [tests/evaluations/test_deepeval_runner.py](../../../../tests/evaluations/test_deepeval_runner.py)

## Relatorios, auditorias e evidencias

- [.github/workflows/evaluation-ci.yml](../../../../.github/workflows/evaluation-ci.yml)

---

> Esta pagina diferencia conteudo estudado de implementacao comprovada no repositorio.
