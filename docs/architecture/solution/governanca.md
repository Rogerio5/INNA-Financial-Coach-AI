# Governança de Arquitetura de Soluções — Sabino.AI

Versão inicial: 24/10/2026. Status: proposta de governança para adoção incremental.
Escopo: plataforma Sabino.AI; primeiro recorte de implementação: orçamento do Financeiro.
[Arquitetura geral](sabino-ai.md) · [Financeiro](financeiro.md)

## 1. Estado e uso deste pacote

Este documento reúne requisitos não funcionais, registros de decisão (ADRs), padrões, rastreabilidade e backlog. Não representa testes aprovados, certificação, adoção de TOGAF/BIAN ou garantia de disponibilidade. Não altera telas, APIs ou dados.

Evidência inicial: leitura dos componentes financeiros indicada na arquitetura do Financeiro. Configurações de produção, cobertura dos testes, migrations e restauração ainda precisam de verificação. Responsáveis abaixo são papéis propostos, não pessoas designadas.

Estados: **proposto → em revisão → aceito → implementado → validado**. Rejeitado e substituído também são possíveis. Aceitar uma decisão não comprova implementação; validar exige evidência reproduzível.

## 2. Requisitos não funcionais

Todos os valores numéricos abaixo são **metas candidatas de homologação**, não SLA contratado nem resultado medido. Produto e operação precisam aprová-los após a linha de base.

| ID | Requisito e meta candidata | Como verificar | Responsável proposto | Estado |
|---|---|---|---|---|
| RNF-01 | Zero leitura/escrita cruzada entre titulares | Testes com contas A/B e identificadores trocados em todas as operações do recorte | Backend e segurança | Proposto |
| RNF-02 | Sessão ausente, expirada ou revogada recusada; acesso inativo retorna 403 | Testes de sessão e contratação no orçamento | Backend | Proposto |
| RNF-03 | GET de orçamento p95 ≤ 800 ms; POST p95 ≤ 1200 ms, serviço aquecido | Homologação, 20 usuários virtuais, rampa de 1 min e 10 min estáveis; registrar volume e hardware | Backend e operação | Proposto |
| RNF-04 | Erros 5xx < 1% no cenário RNF-03 | Contar requisições válidas; separar erros de validação e autorização esperados | Operação | Proposto |
| RNF-05 | Cold start medido separadamente | Medir primeira requisição após inatividade; registrar amostra e ambiente, sem misturar com p95 aquecido | Operação | Proposto |
| RNF-06 | Precisão monetária e atualização atômica de orçamento/limites | Valores decimais, concorrência e falha entre gravações; nenhuma alteração parcial | Backend e QA | Proposto |
| RNF-07 | Ausência de duplicação para operações com contrato idempotente | Repetir e concorrer a mesma chave; payload divergente produz conflito | Backend e QA | Proposto |
| RNF-08 | Meta candidata de disponibilidade 99,5% mensal para jornada autenticada | Monitor sintético e definição de janela/exclusões; avaliar compatibilidade com hospedagem antes de assumir compromisso | Produto e operação | Proposto |
| RNF-09 | RPO candidato 24 h e RTO candidato 4 h | Restaurar backup em ambiente isolado, medir perda e tempo; ajustar plano/custo se necessário | Dados e operação | Proposto |
| RNF-10 | Logs sem senhas, cookies, tokens ou payload financeiro integral | Testes de sanitização e amostragem controlada de logs | Segurança | Proposto |
| RNF-11 | Correlação de requisições e métricas por rota/domínio | Rastrear requisição de teste sem identificadores pessoais em labels de métricas | Operação | Proposto |
| RNF-12 | Compatibilidade do frontend existente | Testes de contratos e jornada de orçamento antes/depois da refatoração | Backend e QA | Proposto |
| RNF-13 | Nenhuma ferramenta da INNA executa fora da permissão do titular | Testes negativos de ferramenta, recurso e domínio | IA e segurança | Proposto |

Não aplicar RNF-03 às respostas de IA: medir latência e custo da INNA separadamente. Dimensionar metas de IA após observar provedor, contexto e carga. Não executar carga ou falhas induzidas contra produção.

### Registro de resultados

Cada execução deverá registrar: ID do RNF, commit, ambiente, data, dataset sintético, carga, dependências, duração, resultado, limitações e link do relatório. A coluna de estado só passa a validado após revisão desse relatório.

## 3. ADRs iniciais

### ADR-SAB-001 — Aplicação modular antes de distribuição de serviços

**Estado:** proposto. **Contexto:** a aplicação FastAPI existente concentra diversos casos de uso; a evolução precisa preservar o Financeiro.
**Alternativas:** manter concentração atual; extrair módulos internos; distribuir imediatamente em microserviços.
**Decisão proposta:** módulos internos com rotas, serviços e repositórios delimitados.
**Motivo:** permite refatoração incremental e reduz complexidade operacional prematura.
**Consequências:** deployment compartilhado e necessidade de disciplina nas dependências. Não resolve isolamento por si só.
**Gatilho de revisão:** gargalo medido, necessidade de escala independente ou requisito de isolamento.
**Aceitação:** extrair orçamento preservando contratos e aprovar RNF-01/02/06/12.
**Responsável proposto:** arquitetura e backend.

### ADR-SAB-002 — PostgreSQL e migração explícita

**Estado:** proposto; PostgreSQL já é utilizado no código financeiro.
**Alternativas:** manter criação de schema em execução; migrations versionadas; trocar de banco.
**Decisão proposta:** preservar armazenamento atual e introduzir migrations versionadas após inventário.
**Motivo:** reduzir divergência de esquema sem migração tecnológica desnecessária.
**Consequências:** requer baseline, revisão de DDL, compatibilidade entre versões e restauração ensaiada.
**Gatilho de revisão:** requisitos que o armazenamento atual não atenda com evidência.
**Aceitação:** validar migration em base equivalente de homologação e recuperação. Não remover ensure_* antes de mapear seus consumidores.
**Responsável proposto:** dados e backend.

### ADR-SAB-003 — Titular pessoal distinto de organização

**Estado:** proposto para contexto empresarial; identidade por titular existe no Financeiro.
**Alternativas:** reutilizar owner_id como organização; separar identidades e vínculos explicitamente.
**Decisão proposta:** separar conta pessoal, organização, vínculo e atribuição de papel; validar escopo no servidor.
**Motivo:** vínculo de emprego não autoriza acesso às finanças pessoais.
**Consequências:** modelo e migrations adicionais; RH não fica liberado só por existir login.
**Gatilho de revisão:** novo domínio com compartilhamento explícito e regras próprias.
**Aceitação:** testes entre duas pessoas, duas organizações e papéis diferentes; preservação das contas pessoais.
**Responsável proposto:** arquitetura, segurança e produto.

### ADR-SAB-004 — Contratos compatíveis e idempotência por caso de uso

**Estado:** proposto.
**Alternativas:** renomear APIs em bloco; preservar e evoluir; criar APIs paralelas sem depreciação.
**Decisão proposta:** manter URLs e payloads atuais durante refatoração; novas versões precisam de consumidores e depreciação definidos.
**Motivo:** reduzir quebra das telas existentes.
**Consequências:** conviver temporariamente com namespaces legados; evitar duplicar regras.
**Idempotência:** definir escopo por ator/contexto/operação e chave; comparar hash do payload. Repetição equivalente retorna resultado anterior; chave com conteúdo diferente retorna conflito. Definir retenção conforme caso, antes de implementar.
**Aceitação:** RNF-07/12; não prometer exactly-once em integração distribuída.
**Responsável proposto:** backend e integrações.

### ADR-SAB-005 — INNA usa cálculos e ferramentas autorizadas

**Estado:** proposto como padrão transversal.
**Alternativas:** modelo calcula e escreve livremente; regras determinísticas e ferramentas controladas.
**Decisão proposta:** calcular valores financeiros em código; modelo interpreta contexto mínimo e usa ferramentas com autorização externa ao modelo.
**Motivo:** resultados reproduzíveis e prevenção de acesso indevido.
**Consequências:** ferramentas, memória, cache e RAG precisam respeitar domínio e escopo. Uma resposta não executa pagamento nem decisão trabalhista implicitamente.
**Aceitação:** RNF-13, testes de isolamento e evidências de origem da resposta.
**Responsável proposto:** IA, segurança e backend.

### ADR-SAB-006 — Eventos e integrações apenas com necessidade demonstrada

**Estado:** proposto.
**Alternativas:** chamadas diretas; mensageria para todo fluxo; eventos para processos assíncronos delimitados.
**Decisão proposta:** contratos síncronos simples onde suficientes; eventos somente em casos documentados.
**Motivo:** evitar infraestrutura sem demanda e tornar falhas explícitas.
**Consequências:** quando adotados, eventos exigem versão, deduplicação, retry limitado, tratamento de falhas e possível outbox. Provedor/broker ainda não selecionado.
**Aceitação:** teste de entrega repetida, indisponibilidade e recuperação; operação documentada.
**Responsável proposto:** integrações e operação.

## 4. Guidelines de backend e APIs

Estas regras orientam novas mudanças; não afirmam conformidade integral do código existente.

### Camadas e dependências

- Rotas traduzem HTTP e validam contratos; serviços coordenam casos de uso; repositórios persistem.
- Regras financeiras determinísticas não dependem de UI nem de modelo de linguagem.
- Não acessar tabelas de outro domínio diretamente: usar contrato explícito.
- Aplicar princípios de responsabilidade única e desacoplamento com mudanças pequenas; não introduzir abstrações sem consumidor concreto.
- Não mover tudo de app.py em um único trabalho. Preservar a definição efetiva das funções e rotas legadas.

### Contratos

- Identidade e escopo são resolvidos/validados no servidor.
- Validar moeda, precisão, datas, limites e campos aceitos. Usar Decimal para cálculo monetário.
- Diferenciar data financeira de instante de auditoria, com convenção de fuso explícita.
- Documentar paginação, ordenação e limites; evitar listagens sem limite.
- Usar 401 para sessão inválida, 403 para ausência de permissão, 404 sem revelar recurso alheio, 409 para conflito e 422 para validação conforme o contrato adotado.
- Novas respostas de erro devem incluir código estável e correlação, sem stack trace ou segredos. Não quebrar o formato legado durante a extração.
- Documentar operações de escrita e idempotência; o cliente não confirma seu próprio direito de acesso.

### Segurança e integração

- Verificar cookie Secure na configuração efetiva e manter HttpOnly/SameSite conforme fluxo.
- Avaliar proteção de origem/CSRF em cada mutação autenticada por cookie.
- Segredos somente no ambiente/gestão de segredos; nunca no frontend, documentação ou logs.
- Chamadas externas precisam de timeout, retry limitado a operações seguras e política de erro; orçamento de tempo total deve ser explícito.
- Webhooks, se adotados, precisam de autenticidade, prevenção de replay e deduplicação.
- Eventos futuros: event_id, tipo, versão, instante, correlação e payload mínimo autorizado.
- Fila de falhas e reprocessamento requerem permissão, auditoria e limite operacional.

### Banco e operação

- Definir fronteira transacional antes de múltiplas gravações.
- Revisar índices por consulta real; não fazer otimizações sem medição.
- Migrations versionadas e compatíveis, com estratégia de recuperação. Nem todo DDL tem rollback simples.
- Logs estruturados e métricas com baixa cardinalidade; não usar email/CPF/user_id como labels.
- Testes de carga, migração e restauração usam dados sintéticos ou sanitizados em ambiente separado.

## 5. Matriz de rastreabilidade inicial

Os caminhos abaixo são evidência de código, não evidência de teste aprovado.

| Negócio | Caso de uso | Componente observado | RNFs | Evidência a produzir |
|---|---|---|---|---|
| BR-01: proteger dados pessoais | Consultar orçamento do titular | app.py: sabino_budget_api_owner e GET /api/finance/budget/{reference_month} | 01,02,10 | Testes A/B, sessão e contratação |
| BR-02: planejar despesas | Salvar orçamento e limites | POST /api/finance/budget; finance_setup_repository.py | 03,04,06,12 | Contrato antes/depois e falha transacional |
| BR-03: registrar despesas | CRUD de transações | finance_transaction_routes.py; transaction_repository.py | 01,06,07 | Repetição, concorrência e reconciliação |
| BR-04: receber orientação | Cotar, executar e consultar análise INNA | paid_analysis_routes.py; paid_analysis.py | 10,11,13 | Isolamento de contexto e consistência em timeout |
| BR-05: ampliar para empresas | Vincular pessoa e organização | Arquitetura proposta; implementação não verificada | 01,02,10 | Modelo, contratos e testes entre organizações |
| BR-06: operar com continuidade | Recuperar serviço e dados | Render observado; plano de recuperação pendente | 05,08,09,11 | Relatório de restauração e monitoramento |

Fontes relativas à raiz: src/inna_platform/app.py e src/inna_platform/services/finance/.
Esta matriz será atualizada com links de commits, testes e relatórios quando existirem.

## 6. Backlog priorizado

| ID | Prioridade | Entrega | Dependência | Critério de conclusão | Responsável proposto |
|---|---|---|---|---|---|
| GOV-01 | P0 | Inventário de rotas, tabelas, consumidores e testes do orçamento | Nenhuma | Contratos atuais e lacunas registrados | Backend |
| GOV-02 | P0 | Testes de caracterização e isolamento | GOV-01 | A/B, sessão e contratação reproduzíveis em homologação | QA/backend |
| GOV-03 | P1 | Extrair router/serviço de orçamento | GOV-02 | Mesmas URLs/respostas e regressão aprovada | Backend |
| GOV-04 | P1 | Verificar transação de orçamento e limites | GOV-01/02 | Falha intermediária sem persistência parcial | Backend/dados |
| GOV-05 | P1 | Baseline de migrations e recuperação | Inventário de schema | Migration ensaiada e restauração registrada | Dados/operação |
| GOV-06 | P1 | Medir RNFs do orçamento | GOV-03/04 | Relatório com commit, carga e ambiente | QA/operação |
| GOV-07 | P1 | Reconciliar capabilities e demonstração | Inventário de comportamento | Metadados coerentes; números demo identificados | Backend/produto |
| GOV-08 | P2 | Definir resumo financeiro real por titular | GOV-02/04 | Totais reconciliados e sem vazamento | Backend |
| GOV-09 | P2 | Conectar contexto financeiro autorizado à INNA | GOV-08 | Evidências, isolamento e cobrança consistente | IA/backend |
| GOV-10 | P2 | Reconciliar catálogo da interface e registro técnico | Inventário dos módulos | Código, estado e rota consistentes sem habilitar módulos prematuramente | Produto/backend |
| GOV-11 | P2 | Detalhar integração RH e identidade empresarial | GOV-10 e responsável da integração | Contrato, organização, papéis e primeiro fluxo definidos | Arquitetura/RH |
| GOV-12 | P3 | Avaliar eventos e distribuição de serviços | Demanda e métricas concretas | ADR com alternativas, custo e operação | Arquitetura/operação |

P0 prepara evidência antes da refatoração. Não há prazo ou pessoa atribuída nesta entrega. Prioridades podem mudar por falha comprovada de segurança ou operação.

## 7. Revisão arquitetural e governança

```mermaid
flowchart LR
  N["Necessidade de negócio"] --> R["Requisitos e RNFs"]
  R --> D["Desenho e alternativas"]
  D --> A["ADR em revisão"]
  A --> I["Implementação delimitada"]
  I --> T["Testes e evidências"]
  T --> G{"Critérios atendidos?"}
  G -->|Sim| P["Liberação e acompanhamento"]
  G -->|Não| D
  P --> R
```

Revisão antes de implementar: escopo, consumidores, dados, permissões, alternativas, custo e recuperação.
Revisão antes de liberar: contratos, testes, migrations, configuração, métricas, rollback e limitações.
Mudança pequena não exige comitê formal: registrar revisão proporcional ao impacto. Produto valida negócio; backend e dados validam viabilidade; segurança revisa fronteiras; operação revisa implantação. Papéis podem ser exercidos pela mesma pessoa em equipe pequena, com decisões registradas.

Checklist de aceite:
- Requisito de negócio e RNFs identificados.
- ADR necessário registrado com alternativas e consequências.
- Evidências de implementação e validação diferenciadas.
- Compatibilidade e acesso verificados.
- Impacto de dados/migrations e recuperação documentado.
- Limitações e decisões abertas explícitas.

## 8. Próxima execução concreta

Iniciar GOV-01 e GOV-02 no backend de orçamento: inventariar GET/POST, funções de persistência, transações, autenticação e consumidores; preparar testes de caracterização antes de extrair código. Não alterar dados de clientes para validar.

Este pacote inicia a governança. Sua publicação não conclui as entregas do backlog nem comprova RNFs.
