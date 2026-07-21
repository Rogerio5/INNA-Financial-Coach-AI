# Validação promtool das regras Telegram

## Estado

O executável `promtool` não estava instalado no ambiente local durante esta validação.

## Validações já executadas

- carregamento dos arquivos com PyYAML;
- presença de grupos e regras;
- unicidade dos nomes;
- referências entre alertas e recording rules;
- uso apenas de métricas confirmadas;
- ausência de labels privadas;
- ausência de métricas ainda não implementadas;
- alinhamento dos limites com a política de SLO;
- existência dos runbooks;
- regressão automatizada dos contratos.

## Validação pendente no ambiente de deploy

Antes da ativação em produção, executar:

`promtool check rules prometheus/telegram_recording_rules.yml`

`promtool check rules prometheus/telegram_alert_rules.yml`

A validação estrutural com PyYAML não substitui integralmente a validação sintática de PromQL pelo Prometheus.
