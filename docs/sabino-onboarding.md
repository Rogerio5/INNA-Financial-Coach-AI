# Primeiros passos na central Sabino.AI

A jornada fica em `/dashboard`; a administração fica em `/admin/primeiros-passos`.
Não há mudança nas telas do módulo Financeiro, concessão de créditos ou ativação de pilotos.

## Progresso

- `account_reviewed`: confirmação explícita do participante após conferir a conta.
- `platforms_explored`: confirmação explícita após conhecer as plataformas.
- `inna_analysis`: derivado de `inna_paid_analyses.state='completed'`. Cliques, orçamentos, análises em andamento, estornadas ou em revisão não concluem esse passo.

Os dois primeiros passos são autodeclarados. A interface identifica essa diferença.
O acompanhamento não é uma medição completa de uso de todos os módulos. Sem passos registrados significa ausência desses três sinais; não prova que o usuário nunca usou outra função.
Análises históricas concluídas contam para o guia. Se a tabela de análises não existe, o estado é desconhecido, nunca inatividade comprovada.

## Administração

Configure `SABINO_ADMIN_USERS` com os identificadores exatos das contas administrativas, separados por vírgula. Sem configuração, acesso negado. Não confundir com a lista de convidados do piloto ou revisores Pix. Nunca preencher a partir de dados enviados pelo navegador.

A API e a página exigem sessão autenticada e autorização administrativa. Contas comuns só podem consultar ou confirmar o próprio progresso. Identidades fornecidas no corpo são rejeitadas. Respostas usam `Cache-Control: no-store`.

O painel lista os inscritos em `inna_finance_pilot_enrollments` e mostra o progresso geral da Sabino.AI. Busca, filtro e priorização são por página (50 participantes), com navegação anterior/próxima. Não mostra conteúdo de análises nem dados de despesas.

## Publicação

Publicar os novos arquivos de serviço, HTML, CSS e JS antes de registrar o router no app e incluir o bloco em `sabino-dashboard.html`. A tabela de progresso é criada idempotentemente no primeiro acesso autenticado, com chave por usuário/passo e referência à conta existente.

O checkout local contém mudanças anteriores e não representa o HEAD remoto. Não enviar um push desse snapshot nem sobrescrever o app remoto inteiro. Aplicar somente a inclusão do router e do bloco da central à versão remota atual.

Nenhum administrador real foi configurado por esta implementação. Identificar a conta autorizada antes da configuração em produção.

## Resumo e acompanhamento (13/10/2026)

Rosca: situações mutuamente exclusivas, total de todos os inscritos no piloto, sem efeito da paginação ou dos filtros. Prioridade: situação manual vigente (dificuldade/desistência/impedimento), conta inativa, dados de análise indisponíveis, ativo (evento nos últimos 7 dias), sem atividade recente, não começou. Atividade medida: confirmações de passos e MAX(updated_at) de análises concluídas. Ausência desses sinais não equivale a ausência de toda atividade na plataforma.

Barras: um motivo por pessoa com acompanhamento manual vigente. Resolver remove do agregado atual, mas preserva o histórico na tabela sabino_participant_followups. Todos os registros incluem administrador e horário; notas limitadas a 1.000 caracteres. Desistência e impedimento exigem contexto. Não altera acesso, plano ou créditos. Conta inativa é distinta de um impedimento informado.

Busca e situação agora filtram todos os inscritos no servidor. O resumo permanece global. Indicadores de jornada concluída e plano Financeiro não piloto ativo ficam fora da rosca, pois podem se sobrepor às situações. Consultas do relatório compartilham snapshot REPEATABLE READ. Adequado ao piloto: o serviço agrega a coorte inteira em memória antes de paginar; revisar para agregação SQL quando crescer significativamente.

Validação: 9 testes PostgreSQL passaram, incluindo totais além da página, classificação de 7 dias, última análise, histórico e autorização. Frontend: filtro pela legenda e resolução atualizando gráficos verificados com dados fictícios.
