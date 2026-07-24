# Política de sanitização da observabilidade Telegram

## Objetivo

Garantir que logs, métricas e traces não exponham dados pessoais, financeiros, credenciais ou conteúdo conversacional.

## Dados proibidos

- Nome completo do usuário.
- Texto integral da mensagem.
- Renda, gastos, dívidas, reserva ou objetivo financeiro.
- Estado conversacional completo.
- Payload recebido do Telegram.
- Payload criptografado ou descriptografado.
- Token do bot.
- Segredos de webhook.
- URL do PostgreSQL.
- Usuário e senha do banco.
- Queries SQL e parâmetros.
- Mensagens brutas de exceção de infraestrutura.

## Dados permitidos

- Nome estável do evento.
- Componente.
- Operação.
- Resultado.
- Categoria sanitizada do erro.
- Duração em milissegundos.
- Versão da sessão.
- Quantidade de tentativas.
- Indicador de conflito recuperado.
- Status do worker ou receipt.

## Identificadores

- `request_id`, `update_id` e `receipt_id` podem aparecer somente em logs ou traces.
- Esses identificadores não podem ser labels do Prometheus.
- `chat_id`, `telegram_user_id` e `session_id` não devem ser registrados em texto puro.
- Caso correlação por usuário seja necessária, utilizar hash irreversível com chave operacional separada.

## Exceções

- Nunca registrar `str(exception)` diretamente em produção.
- Converter exceções para `error_category`.
- O nome da classe da exceção pode ser registrado apenas após revisão.
- URLs, credenciais e parâmetros devem ser removidos.

## Configuração ausente

É permitido registrar o nome da configuração ausente, por exemplo `TELEGRAM_BOT_TOKEN`.
Não é permitido registrar o valor da configuração.

## Métricas

Labels permitidas:

- `operation`
- `outcome`
- `error_category`
- `component`

Labels proibidas:

- `chat_id`
- `telegram_user_id`
- `update_id`
- `request_id`
- `receipt_id`
- `session_id`
- qualquer texto fornecido pelo usuário

## Falhas da telemetria

- Falhas de emissão de métricas ou eventos não podem interromper a operação principal.
- A falha de telemetria pode ser contabilizada por um sink secundário seguro.
- A exceção original da operação principal deve preservar seu comportamento.
