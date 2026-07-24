# Contrato de health e readiness do Telegram

## Status

F2H5-H1.

## Objetivo

Definir probes operacionais independentes da camada HTTP para avaliar a saúde do processo e a prontidão das dependências do fluxo durável do Telegram.

## Princípios

- health e readiness possuem semânticas diferentes;
- probes não podem alterar estado operacional;
- probes não podem consumir jobs;
- probes não podem renovar leases;
- probes não podem escrever receipts;
- probes não podem chamar LLM;
- probes não podem enviar mensagens;
- probes devem ser rápidas;
- probes devem ser determinísticas;
- falhas de diagnóstico não podem derrubar o processo;
- respostas não devem conter segredos ou dados privados.

## Health

Health indica se o processo está vivo e capaz de executar código.

Um processo saudável deve conseguir:

- construir o serviço de diagnóstico;
- consultar o relógio;
- criar um snapshot seguro;
- serializar o resultado.

Health não exige que PostgreSQL, Telegram, Gmail, Gemini ou outros serviços externos estejam disponíveis.

## Readiness

Readiness indica se a aplicação pode receber e processar trabalho.

A prontidão pode depender de:

- configuração mínima;
- banco de dados;
- repositório de jobs;
- receipts;
- keyring ou criptografia;
- processor;
- runtime de métricas;
- dependências obrigatórias do worker.

## Estados

### healthy

O processo está vivo e todas as verificações obrigatórias estão disponíveis.

### degraded

O processo está vivo, mas uma dependência opcional ou funcionalidade não crítica está indisponível.

O serviço ainda pode receber trabalho limitado.

### unready

Uma dependência obrigatória está indisponível ou inconsistente.

O serviço não deve receber novos trabalhos.

## Severidade dos checks

### required

Uma falha torna o estado geral `unready`.

### optional

Uma falha torna o estado geral `degraded`.

### informational

Uma falha é registrada no diagnóstico, mas não altera o estado geral.

## Contrato de check

Cada check deve retornar:

- `name`;
- `status`;
- `severity`;
- `latency_seconds`;
- `error_category`;
- `details`.

## Privacidade

`details` deve conter apenas informações operacionais de baixa cardinalidade.

Não podem aparecer:

- tokens;
- senhas;
- DSNs completos;
- payloads;
- mensagens de usuários;
- textos brutos de exceção;
- stack traces;
- e-mails;
- identificadores de usuários;
- update IDs;
- claim tokens;
- dados financeiros.

## Categorias de erro

Categorias permitidas:

- `none`;
- `configuration`;
- `dependency`;
- `database`;
- `persistence`;
- `encryption`;
- `timeout`;
- `consistency`;
- `internal`;
- `unknown`.

## Fail-safe

Se um check lançar uma exceção:

- o erro deve ser convertido em resultado seguro;
- o texto bruto da exceção não deve ser exposto;
- a categoria deve ser normalizada;
- a avaliação geral deve continuar.

## HTTP futuro

### `/health`

- sucesso: HTTP 200;
- corpo com status do processo;
- não executa dependências externas.

### `/ready`

- `healthy`: HTTP 200;
- `degraded`: HTTP 200;
- `unready`: HTTP 503.

## Compatibilidade

A implementação deve ser utilizável por:

- FastAPI;
- worker CLI;
- testes;
- diagnóstico administrativo;
- futura coleta Prometheus;
- futuras rotinas de deploy.
