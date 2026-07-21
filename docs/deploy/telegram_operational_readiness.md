# Deploy do health e readiness do Telegram

## Status

F2H5-H7 — Contrato de deploy operacional.

## Objetivo

Documentar a implantação segura dos endpoints de liveness e readiness da INNA, incluindo Render, Kubernetes, variáveis de ambiente, segurança, testes pós-deploy e rollback.

## Endpoints operacionais

| Endpoint | Finalidade | Dependências externas | Exposição |
|---|---|---:|---|
| GET /health | Liveness do processo | Não | Pública |
| GET /ready | Readiness produtivo do worker | Sim | Pública |
| GET /internal/ready | Diagnóstico detalhado | Sim | Protegida |

## Liveness

O endpoint /health verifica somente se o processo da API consegue executar seu núcleo básico.

Ele não deve:

- consultar PostgreSQL;
- carregar keyring;
- consumir jobs;
- executar claim;
- acessar Telegram API;
- chamar Gemini;
- enviar e-mails;
- gerar relatórios;
- realizar operações de escrita.

Uma falha de liveness indica que o processo pode precisar ser reiniciado.

## Readiness

O endpoint /ready verifica se o worker está apto a receber e processar trabalho.

Ele pode validar:

- configuração do worker;
- conexão PostgreSQL por meio de SELECT 1;
- contratos do repositório de jobs;
- contratos do repositório de receipts;
- keyring;
- processor;
- runtime de métricas.

Uma falha de readiness não exige obrigatoriamente reinício do processo.

A infraestrutura deve retirar temporariamente a instância do balanceamento até que as dependências se recuperem.

## Resposta interna

A rota /internal/ready fica:

- desabilitada por padrão;
- fora do OpenAPI;
- protegida por token;
- configurada com comparação em tempo constante;
- sem exposição de segredos;
- disponível somente quando explicitamente habilitada.

Não utilize o token interno em:

- query string;
- URL;
- logs;
- commits;
- arquivos versionados;
- imagens Docker;
- mensagens de erro;
- documentação pública.

Utilize o header:

X-INNA-Operations-Token: <segredo>

## Variáveis de ambiente

### INNA_INTERNAL_READY_ENABLED

Habilita ou desabilita o diagnóstico interno.

Valores aceitos:

- true;
- false;
- 1;
- 0;
- yes;
- no;
- on;
- off;
- enabled;
- disabled.

Valor padrão:

false

### INNA_INTERNAL_OPERATIONS_TOKEN

Obrigatória somente quando INNA_INTERNAL_READY_ENABLED=true.

Requisitos:

- pelo menos 32 caracteres;
- boa diversidade de caracteres;
- valor aleatório e imprevisível;
- armazenamento como secret;
- rotação em caso de suspeita de exposição.

Não reutilize:

- token do Telegram;
- senha do PostgreSQL;
- chave Gemini;
- credenciais Gmail;
- chave de criptografia dos jobs.

### INNA_READINESS_CACHE_TTL_SECONDS

Tempo durante o qual um resultado pode ser reutilizado pelo runtime.

Valor padrão: 1

Faixa aceita: 0 a 60 segundos.

### INNA_READINESS_CONCURRENT_WAIT_SECONDS

Tempo máximo de espera por uma avaliação concorrente já em andamento.

Valor padrão: 0.25

Faixa aceita: 0 a 10 segundos.

### INNA_READINESS_EVALUATION_BUDGET_SECONDS

Orçamento máximo esperado para a avaliação completa.

Valor padrão: 2

Faixa aceita: 0.001 a 30 segundos.

## Configuração recomendada

Configuração pública padrão:

INNA_INTERNAL_READY_ENABLED=false
INNA_READINESS_CACHE_TTL_SECONDS=1
INNA_READINESS_CONCURRENT_WAIT_SECONDS=0.25
INNA_READINESS_EVALUATION_BUDGET_SECONDS=2

Quando o diagnóstico interno for necessário:

INNA_INTERNAL_READY_ENABLED=true
INNA_INTERNAL_OPERATIONS_TOKEN=<segredo-gerado-no-provedor>

## Render

Configure o Health Check Path do serviço como:

/health

O Render deve utilizar o liveness, e não o readiness, para decidir quando reiniciar o processo.

O endpoint /ready pode ser utilizado por:

- monitor externo;
- teste pós-deploy;
- painel operacional;
- verificação de release;
- smoke test de dependências.

O token da rota interna deve ser criado diretamente no painel de variáveis secretas do Render.

Nunca coloque o token verdadeiro no render.yaml, no repositório ou no arquivo .env.example.

## Kubernetes

Configuração recomendada:

- /health como startupProbe;
- /health como livenessProbe;
- /ready como readinessProbe;
- porta nomeada http;
- timeout coerente com o orçamento do runtime;
- failureThreshold suficiente para evitar flapping.

A rota /internal/ready não deve ser utilizada como probe do Kubernetes.

## Política de códigos HTTP

| Estado | /health | /ready |
|---|---:|---:|
| healthy | 200 | 200 |
| degraded | 200 | 200 |
| unready | 503 | 503 |

## Headers operacionais

As respostas devem incluir:

- Content-Type: application/json; charset=utf-8;
- Cache-Control: no-store;
- X-Content-Type-Options: nosniff;
- X-INNA-Schema-Version: telegram-operational-status.v1;
- X-INNA-Operational-Status: healthy, degraded ou unready.

## Cache

As respostas HTTP utilizam Cache-Control: no-store.

O cache TTL configurado é interno ao runtime e reduz consultas repetidas.

Ele não autoriza armazenamento por:

- navegador;
- proxy;
- CDN;
- gateway;
- balanceador.

## Timeouts

O orçamento do runtime detecta avaliações que terminaram acima do limite esperado.

Timeouts rígidos também devem ser configurados nas próprias dependências:

- timeout de conexão PostgreSQL;
- timeout de statement;
- timeout de rede;
- timeout de APIs externas;
- timeout do proxy reverso.

## Segurança

Nunca versionar:

- token operacional real;
- DATABASE_URL;
- token do Telegram;
- chave Gemini;
- credenciais Gmail;
- chaves de criptografia;
- payloads de usuários;
- claim tokens;
- dados financeiros.

## Teste local público

PowerShell:

Invoke-RestMethod http://localhost:8000/health

Invoke-RestMethod http://localhost:8000/ready

## Teste local interno

Somente quando a rota interna estiver habilitada:

$headers = @{ "X-INNA-Operations-Token" = $env:INNA_INTERNAL_OPERATIONS_TOKEN }

Invoke-RestMethod -Uri "http://localhost:8000/internal/ready" -Headers $headers

## Teste pós-deploy

Health público:

curl --fail --silent --show-error https://SEU-DOMINIO/health

Readiness público:

curl --fail --silent --show-error https://SEU-DOMINIO/ready

Diagnóstico interno:

curl --fail --silent --show-error -H "X-INNA-Operations-Token: $INNA_INTERNAL_OPERATIONS_TOKEN" https://SEU-DOMINIO/internal/ready

## Critérios de aprovação do deploy

O deploy é considerado aprovado quando:

- /health retorna HTTP 200;
- /ready retorna HTTP 200 em ambiente corretamente configurado;
- /internal/ready retorna HTTP 404 quando desabilitado;
- /internal/ready retorna HTTP 401 com token incorreto;
- /internal/ready retorna HTTP 200 com token correto;
- a rota interna não aparece no OpenAPI;
- nenhum segredo aparece nas respostas;
- não existem rotas duplicadas;
- a regressão operacional está aprovada.

## Rollback

Realize rollback quando:

- /health deixar de responder HTTP 200;
- /ready permanecer HTTP 503 após a inicialização;
- ocorrer duplicidade de rota;
- a rota interna aparecer no OpenAPI;
- algum segredo aparecer no payload;
- a configuração operacional não puder ser carregada;
- a regressão operacional falhar.

## Resposta a incidentes

Em caso de exposição do token operacional:

1. desabilitar INNA_INTERNAL_READY_ENABLED;
2. rotacionar INNA_INTERNAL_OPERATIONS_TOKEN;
3. reiniciar as instâncias;
4. revisar logs e histórico de acesso;
5. confirmar que o token não foi versionado;
6. reabilitar a rota somente após validação.

## Princípios finais

- liveness não consulta dependências externas;
- readiness não consome jobs;
- diagnóstico interno é opt-in;
- segredos nunca entram no Git;
- falhas retornam estado fechado e seguro;
- observabilidade não deve alterar o estado do sistema.
