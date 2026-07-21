# Runtime resiliente de health e readiness do Telegram

## Status

F2H5-H3.

## Objetivo

Controlar a execução concorrente das probes de readiness, reduzir consultas repetidas e garantir resposta fail-safe.

## Cache

O runtime pode reutilizar um snapshot enquanto ele estiver dentro do TTL configurado.

O cache:

- é protegido por lock;
- é imutável para os consumidores;
- possui idade calculada com relógio monotônico;
- nunca altera o snapshot operacional original.

## Single-flight

Somente uma avaliação pode estar em andamento por runtime.

Chamadas concorrentes:

1. aguardam por um tempo limitado;
2. reutilizam o resultado recém-criado quando disponível;
3. retornam `unready` se o limite de espera for excedido.

## Falha fechada

Um snapshot antigo saudável não pode esconder uma falha atual.

Em caso de:

- exceção interna;
- timeout de concorrência;
- avaliação acima do orçamento;
- snapshot inválido;

o resultado deve ser `unready`.

## Orçamento de latência

A avaliação possui um orçamento total.

Quando a execução termina acima do orçamento:

- o resultado é convertido em `unready`;
- um check seguro `readiness_runtime_budget` é adicionado;
- a duração é preservada;
- nenhuma mensagem bruta de erro é exposta.

## Timeout rígido

Timeouts rígidos devem ser configurados nas dependências:

- timeout de conexão PostgreSQL;
- timeout de statement;
- timeout de rede;
- timeout de APIs externas.

A camada de runtime não tenta cancelar à força uma thread Python bloqueada.

## Metadados seguros

A resposta do runtime contém:

- `sequence`;
- `cache_hit`;
- `cache_age_seconds`;
- `generated_at_epoch_seconds`;
- `reason`;
- snapshot operacional seguro.

## Privacidade

Não podem aparecer:

- DSN;
- senha;
- token;
- payload;
- texto bruto de exceção;
- stack trace;
- identificadores de usuários;
- claim tokens;
- chaves de criptografia.

## HTTP futuro

O endpoint `/ready` consumirá o runtime, e não executará diretamente todas as probes.
