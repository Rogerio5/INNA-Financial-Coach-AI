document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    console.log("SABINO_CONTRACT_DOCUMENTS_V1=LOADED");


    const STORAGE_KEY =
        "inna_contract_document_reads_v51";


    const REQUIRED_DOCUMENTS = [
        "contract",
        "proposal",
        "terms",
        "sla",
        "privacy",
        "security",
        "commercial"
    ];


    function getJson(key) {

        try {

            const raw =
                localStorage.getItem(key);

            return raw
                ? JSON.parse(raw)
                : null;

        }
        catch {

            return null;

        }

    }


    function escapeHtml(value) {

        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    function formatBRL(value) {

        if (
            value === null ||
            value === undefined ||
            Number.isNaN(Number(value))
        ) {
            return "Sob consulta";
        }


        return new Intl.NumberFormat(
            "pt-BR",
            {
                style: "currency",
                currency: "BRL",
                maximumFractionDigits: 0
            }
        ).format(
            Number(value)
        );

    }


    function currentContext() {

        const config =
            getJson(
                "inna_solution_config"
            ) || {};


        const proposal =
            getJson(
                "inna_final_proposal"
            ) || {};


        const term =
            Number(
                document.querySelector(
                    'input[name="contract-term"]:checked'
                )?.value || 1
            );


        const billing =
            document.querySelector(
                'input[name="billing"]:checked'
            )?.value || "monthly";


        const monthly =
            proposal?.finalEstimate ??
            config?.pricing?.estimatedTotal ??
            null;


        return {

            solutionId:
                localStorage.getItem(
                    "inna_solution_id"
                ) || "A definir",

            company:
                document.getElementById(
                    "contract-company"
                )?.value.trim() ||
                "Empresa contratante",

            companyDocument:
                document.getElementById(
                    "contract-company-document"
                )?.value.trim() ||
                "Não informado",

            representative:
                document.getElementById(
                    "contract-representative"
                )?.value.trim() ||
                "Representante autorizado",

            role:
                document.getElementById(
                    "contract-role"
                )?.value.trim() ||
                "Não informado",

            email:
                document.getElementById(
                    "contract-email"
                )?.value.trim() ||
                "Não informado",

            plan:
                config
                    ?.recommendedPlan
                    ?.name || "Não definido",

            modules:
                config?.modules || [],

            channels:
                config?.channels || [],

            integrations:
                config?.integrations || [],

            resources:
                config?.resources || [],

            users:
                config?.users?.label ||
                config?.users?.value ||
                "-",

            data:
                config?.data?.label ||
                config?.data?.value ||
                "-",

            rag:
                config?.rag?.label ||
                config?.rag?.value ||
                "-",

            ragUpdate:
                config?.ragUpdate?.label ||
                config?.ragUpdate?.value ||
                "-",

            monthly,

            monthlyFormatted:
                formatBRL(monthly),

            term,

            termLabel:
                term === 1
                    ? "1 mês"
                    : `${term} meses`,

            billing:
                billing === "annual"
                    ? "Anual"
                    : "Mensal",

            periodFormatted:
                monthly === null
                    ? "Sob consulta"
                    : formatBRL(
                        Number(monthly) *
                        term
                    ),

            date:
                new Date()
                    .toLocaleDateString(
                        "pt-BR"
                    )

        };

    }


    function applyTokens(html, ctx) {

        const values = {

            SOLUTION_ID:
                ctx.solutionId,

            COMPANY:
                ctx.company,

            CNPJ:
                ctx.companyDocument,

            REPRESENTATIVE:
                ctx.representative,

            ROLE:
                ctx.role,

            EMAIL:
                ctx.email,

            PLAN:
                ctx.plan,

            MONTHLY_PRICE:
                ctx.monthlyFormatted,

            PERIOD_PRICE:
                ctx.periodFormatted,

            TERM:
                ctx.termLabel,

            BILLING:
                ctx.billing,

            USERS:
                ctx.users,

            DATA:
                ctx.data,

            RAG:
                ctx.rag,

            RAG_UPDATE:
                ctx.ragUpdate,

            MODULES:
                ctx.modules.length
                    ? ctx.modules.join(", ")
                    : "Nenhum módulo informado",

            CHANNELS:
                ctx.channels.length
                    ? ctx.channels.join(", ")
                    : "Nenhum canal informado",

            INTEGRATIONS:
                ctx.integrations.length
                    ? ctx.integrations.join(", ")
                    : "Nenhuma integração informada",

            RESOURCES:
                ctx.resources.length
                    ? ctx.resources.join(", ")
                    : "Nenhum recurso informado",

            DATE:
                ctx.date

        };


        let output =
            html;


        Object.entries(
            values
        ).forEach(
            ([key, value]) => {

                output =
                    output.replaceAll(
                        `{{${key}}}`,
                        escapeHtml(value)
                    );

            }
        );


        return output;

    }


    const docs = {


        /* ==================================================
   CONTRATO PRINCIPAL - 20 PAGINAS
   ================================================== */

        contract: {
  "type": "CONTRATO PRINCIPAL",
  "title": "Contrato da solução Sabino.AI",
  "version": "Versão 1.0-demo",
  "pages": [
    {
      "html": "<h3>Identificação das partes</h3>\n\n<p>\nEste instrumento apresenta, em caráter demonstrativo,\nas condições aplicáveis à contratação da plataforma\nSabino.AI entre a fornecedora da solução e a\norganização contratante.\n</p>\n\n<div class=\"document-data-box\">\n\n<p><strong>Empresa:</strong> {{COMPANY}}</p>\n<p><strong>CNPJ:</strong> {{CNPJ}}</p>\n<p><strong>Representante:</strong> {{REPRESENTATIVE}}</p>\n<p><strong>Cargo:</strong> {{ROLE}}</p>\n<p><strong>E-mail:</strong> {{EMAIL}}</p>\n<p><strong>Solução:</strong> {{SOLUTION_ID}}</p>\n\n</div>\n\n<p>\nO representante declara que as informações fornecidas\ndeverão corresponder aos dados efetivos da organização\ne da pessoa autorizada a representá-la.\n</p>\n\n<p>\nNa versão comercial definitiva deverão constar\na qualificação completa das partes, endereços\ne demais informações juridicamente necessárias.\n</p>",
      "title": "1. Identificação das partes"
    },
    {
      "html": "<h3>Definições</h3>\n\n<p>\nPara fins deste contrato, os seguintes termos\npossuem significado específico.\n</p>\n\n<ul>\n\n<li>\n<strong>Sabino.AI:</strong>\nplataforma tecnológica objeto da contratação.\n</li>\n\n<li>\n<strong>INNA:</strong>\ncamada inteligente de assistência, coordenação\ne contextualização da plataforma.\n</li>\n\n<li>\n<strong>Módulo:</strong>\ncomponente funcional especializado habilitado\nna solução.\n</li>\n\n<li>\n<strong>Usuário:</strong>\npessoa autorizada pela organização contratante.\n</li>\n\n<li>\n<strong>RAG:</strong>\nmecanismo de recuperação de informações\ne conhecimento contextual.\n</li>\n\n<li>\n<strong>Integração:</strong>\nconexão da plataforma com sistemas,\nAPIs, bancos de dados ou serviços externos.\n</li>\n\n<li>\n<strong>Go Live:</strong>\nmomento de liberação da solução para operação.\n</li>\n\n<li>\n<strong>Dados da contratante:</strong>\ndados, documentos, registros e conteúdos\nfornecidos pela organização cliente.\n</li>\n\n</ul>",
      "title": "2. Definições contratuais"
    },
    {
      "html": "<h3>Objeto da contratação</h3>\n\n<p>\nO objeto deste instrumento consiste na\ndisponibilização, implantação, configuração\ne utilização da plataforma tecnológica Sabino.AI.\n</p>\n\n<p>\nA solução será disponibilizada de acordo\ncom plano, módulos, capacidades, integrações\ne recursos selecionados pela contratante.\n</p>\n\n<p>\nA plataforma poderá compreender automação,\nanálise de dados, inteligência artificial,\nagentes, RAG, APIs, observabilidade,\ngovernança e recursos de assistência\natravés da INNA.\n</p>\n\n<p>\nO escopo efetivamente contratado será determinado\npela proposta comercial, configuração registrada\ne anexos aplicáveis.\n</p>",
      "title": "3. Objeto do contrato"
    },
    {
      "html": "<h3>Escopo contratado</h3>\n\n<div class=\"document-data-box\">\n\n<p><strong>Plano:</strong> {{PLAN}}</p>\n<p><strong>Módulos:</strong> {{MODULES}}</p>\n<p><strong>Canais:</strong> {{CHANNELS}}</p>\n<p><strong>Integrações:</strong> {{INTEGRATIONS}}</p>\n<p><strong>Recursos:</strong> {{RESOURCES}}</p>\n\n</div>\n\n<p>\nSomente funcionalidades, capacidades e serviços\nexpressamente apresentados na configuração\nou proposta são considerados parte do escopo.\n</p>\n\n<p>\nNão são automaticamente incluídos:\ndesenvolvimento sob medida, migração extraordinária,\nintegrações adicionais, consultoria especializada,\nexpansão de infraestrutura ou recursos não previstos.\n</p>\n\n<p>\nAlterações relevantes de escopo poderão exigir\nnova análise técnica, prazo adicional\ne revisão comercial.\n</p>",
      "title": "4. Escopo e exclusões"
    },
    {
      "html": "<h3>Dimensionamento da solução</h3>\n\n<div class=\"document-data-box\">\n\n<p><strong>Usuários:</strong> {{USERS}}</p>\n<p><strong>Volume de dados:</strong> {{DATA}}</p>\n<p><strong>Base RAG:</strong> {{RAG}}</p>\n<p><strong>Atualização RAG:</strong> {{RAG_UPDATE}}</p>\n\n</div>\n\n<p>\nAs capacidades contratadas orientam\no dimensionamento de infraestrutura,\ndesempenho, segurança, governança\ne formação de preços.\n</p>\n\n<p>\nConsumo persistentemente superior aos limites\ncontratados poderá exigir upgrade de plano,\nexpansão de capacidade ou contratação adicional.\n</p>\n\n<p>\nLimites técnicos detalhados deverão constar\nda documentação comercial ou técnica\ncorrespondente ao plano contratado.\n</p>",
      "title": "5. Capacidades e limites de utilização"
    },
    {
      "html": "<h3>Implantação da solução</h3>\n\n<p>\nApós a formalização da contratação,\na Sabino.AI seguirá um processo controlado\nde implantação.\n</p>\n\n<ol>\n\n<li>Validação técnica e comercial.</li>\n<li>Preparação do ambiente.</li>\n<li>Configuração de identidade e acessos.</li>\n<li>Aplicação dos controles de segurança.</li>\n<li>Configuração das integrações.</li>\n<li>Preparação de dados e conhecimento.</li>\n<li>Testes técnicos e funcionais.</li>\n<li>Validação pela contratante.</li>\n<li>Go Live.</li>\n\n</ol>\n\n<p>\nCritérios objetivos de aceite, responsáveis\npela aprovação, evidências necessárias\ne prazos deverão constar do plano\nde implantação definitivo.\n</p>\n\n<p>\nA indisponibilidade de dados, acessos,\ncredenciais ou validações dependentes\nda contratante poderá impactar o cronograma.\n</p>",
      "title": "6. Implantação, testes e critérios de aceite"
    },
    {
      "html": "<h3>Condições financeiras</h3>\n\n<div class=\"document-data-box\">\n\n<p><strong>Plano:</strong> {{PLAN}}</p>\n<p><strong>Valor mensal estimado:</strong> {{MONTHLY_PRICE}}</p>\n<p><strong>Prazo:</strong> {{TERM}}</p>\n<p><strong>Faturamento:</strong> {{BILLING}}</p>\n<p><strong>Valor estimado do período:</strong> {{PERIOD_PRICE}}</p>\n\n</div>\n\n<p>\nOs valores apresentados nesta versão\npossuem caráter demonstrativo.\n</p>\n\n<p>\nA versão comercial definitiva deverá estabelecer\nvalor contratado, vencimento, meio de pagamento,\ntributos e demais condições financeiras.\n</p>\n\n<p>\nCustomizações, serviços extraordinários,\nintegrações adicionais ou excedentes de capacidade\npoderão possuir cobrança adicional,\nmediante aprovação.\n</p>\n\n<p class=\"document-legal-note\">\nRegras sobre inadimplência, multas, juros,\nsuspensão ou outros encargos somente deverão\nser aplicadas depois de definição comercial\ne validação jurídica.\n</p>",
      "title": "7. Preço, faturamento e pagamento"
    },
    {
      "html": "<h3>Vigência contratual</h3>\n\n<p>\nO período atualmente selecionado para esta\ncontratação é de <strong>{{TERM}}</strong>.\n</p>\n\n<p>\nA versão definitiva deverá identificar claramente\na data de início da vigência, data de faturamento\ne eventual período dedicado à implantação.\n</p>\n\n<p>\nRegras de renovação automática ou expressa,\naviso prévio e alteração de plano deverão\nser apresentadas de forma clara e destacada.\n</p>\n\n<p>\nQualquer política de reajuste deverá indicar\nperiodicidade, índice ou outro critério\ncomercial juridicamente aprovado.\n</p>",
      "title": "8. Prazo, vigência, renovação e reajuste"
    },
    {
      "html": "<h3>Responsabilidades da fornecedora</h3>\n\n<p>\nNo escopo efetivamente contratado,\na Sabino.AI deverá disponibilizar\nos serviços e recursos previstos.\n</p>\n\n<ul>\n\n<li>\nManter disponíveis os recursos formalmente contratados.\n</li>\n\n<li>\nAplicar controles apropriados de identidade e acesso.\n</li>\n\n<li>\nManter registros operacionais pertinentes.\n</li>\n\n<li>\nManter observabilidade quando incluída no escopo.\n</li>\n\n<li>\nExecutar processos de suporte conforme plano e SLA.\n</li>\n\n<li>\nComunicar incidentes relevantes quando aplicável.\n</li>\n\n<li>\nManter documentação necessária à operação.\n</li>\n\n<li>\nAdotar práticas de segurança compatíveis\ncom os serviços prestados.\n</li>\n\n</ul>",
      "title": "9. Obrigações da Sabino.AI"
    },
    {
      "html": "<h3>Responsabilidades da organização contratante</h3>\n\n<p>\nA contratante deverá colaborar com a implantação\ne utilizar adequadamente os recursos disponibilizados.\n</p>\n\n<ul>\n\n<li>\nGarantir legitimidade sobre dados e conteúdos fornecidos.\n</li>\n\n<li>\nAdministrar usuários, credenciais e permissões.\n</li>\n\n<li>\nFornecer informações corretas e atualizadas.\n</li>\n\n<li>\nDisponibilizar acessos necessários às integrações.\n</li>\n\n<li>\nParticipar das validações que dependam de sua atuação.\n</li>\n\n<li>\nNão utilizar a plataforma para atividades ilícitas.\n</li>\n\n<li>\nPreservar revisão humana em decisões relevantes.\n</li>\n\n<li>\nComunicar alterações significativas de ambiente.\n</li>\n\n</ul>",
      "title": "10. Obrigações da contratante"
    },
    {
      "html": "<h3>Níveis de serviço</h3>\n\n<p>\nO SLA definitivo deverá estabelecer metas\nde disponibilidade, canais de atendimento,\nhorários de suporte, prioridades\ne tempos de resposta.\n</p>\n\n<div class=\"document-data-box\">\n\n<p>\n<strong>Disponibilidade:</strong>\nconforme SLA comercial aprovado.\n</p>\n\n<p>\n<strong>Severidades:</strong>\nP1, P2, P3 e P4 ou classificação equivalente.\n</p>\n\n<p>\n<strong>Resposta inicial:</strong>\nconforme plano contratado.\n</p>\n\n</div>\n\n<p>\nEsta versão não fixa percentuais nem tempos\nespecíficos, pois tais compromissos devem\nrefletir a capacidade operacional efetivamente\noferecida pela Sabino.AI.\n</p>\n\n<p>\nManutenções programadas, indisponibilidades\nde terceiros e hipóteses de exclusão deverão\nser detalhadas no Anexo de SLA.\n</p>",
      "title": "11. SLA, disponibilidade e suporte"
    },
    {
      "html": "<h3>Recursos de inteligência artificial</h3>\n\n<p>\nA solução poderá utilizar modelos de IA,\nagentes, automações, RAG, classificação\ne mecanismos de apoio à tomada de decisão.\n</p>\n\n<p>\nA INNA poderá atuar como camada de assistência,\ncoordenação, contextualização e encaminhamento\nde funcionalidades da plataforma.\n</p>\n\n<p>\nSistemas de inteligência artificial podem produzir\nresultados imprecisos, incompletos ou inadequados\nao contexto.\n</p>\n\n<p>\nA utilização desses resultados deverá considerar\nfinalidade, criticidade e controles apropriados.\n</p>\n\n<p>\nProcessos sensíveis ou de alto impacto deverão\npreservar revisão e responsabilidade humana\nsempre que aplicável.\n</p>",
      "title": "12. Inteligência artificial, INNA e revisão humana"
    },
    {
      "html": "<h3>Titularidade e propriedade intelectual</h3>\n\n<p>\nA titularidade dos dados fornecidos pela contratante\npermanecerá de acordo com os direitos previamente\nexistentes e a legislação aplicável.\n</p>\n\n<p>\nSoftware, arquitetura, componentes, interfaces,\nmarcas, documentação e demais ativos da plataforma\npermanecem sujeitos aos direitos de seus\nrespectivos titulares.\n</p>\n\n<p>\nA versão definitiva deverá estabelecer regras\npara documentos processados, bases RAG,\ncustomizações, conteúdos produzidos e propriedade\nintelectual eventualmente desenvolvida.\n</p>\n\n<p>\nTambém deverá ser informado se e em quais condições\ndados da contratante poderão ser utilizados\npara avaliação, melhoria ou treinamento de modelos.\n</p>",
      "title": "13. Dados, conteúdos e propriedade intelectual"
    },
    {
      "html": "<h3>Controles de segurança</h3>\n\n<p>\nA proteção da solução deverá ser compatível\ncom a arquitetura, criticidade da operação,\nnatureza dos dados e plano contratado.\n</p>\n\n<ul>\n\n<li>Autenticação e autorização.</li>\n<li>MFA e SSO quando aplicáveis.</li>\n<li>RBAC e princípio de menor privilégio.</li>\n<li>Criptografia em trânsito e/ou em repouso.</li>\n<li>Gestão de segredos e credenciais.</li>\n<li>Logs e trilhas de auditoria.</li>\n<li>Monitoramento e observabilidade.</li>\n<li>Backups e mecanismos de recuperação.</li>\n<li>Segregação de ambientes.</li>\n<li>Processo de resposta a incidentes.</li>\n\n</ul>\n\n<p>\nRTO, RPO e demais compromissos técnicos\nsomente deverão ser definidos quando forem\nefetivamente suportados pela arquitetura\ne pela operação contratadas.\n</p>",
      "title": "14. Segurança da informação"
    },
    {
      "html": "<h3>Informações confidenciais</h3>\n\n<p>\nAs partes deverão proteger informações\nconfidenciais obtidas em razão da relação contratual.\n</p>\n\n<p>\nEssas informações deverão ser utilizadas\nsomente para finalidades relacionadas\nà execução dos serviços.\n</p>\n\n<p>\nA versão jurídica definitiva deverá estabelecer\nconceito de informação confidencial, exceções,\nprocedimentos de proteção, prazo das obrigações\ne hipóteses de divulgação exigida por lei.\n</p>\n\n<p>\nCredenciais, segredos de integração,\ndocumentação interna, informações empresariais\ne dados estratégicos deverão receber proteção\ncompatível com sua sensibilidade.\n</p>",
      "title": "15. Confidencialidade"
    },
    {
      "html": "<h3>Proteção de dados pessoais</h3>\n\n<p>\nQuando houver tratamento de dados pessoais,\nas partes deverão observar a legislação aplicável,\nincluindo a Lei Geral de Proteção de Dados.\n</p>\n\n<p>\nO instrumento definitivo deverá definir:\n</p>\n\n<ul>\n\n<li>Papéis de controlador e operador.</li>\n<li>Finalidades e instruções de tratamento.</li>\n<li>Categorias de dados envolvidos.</li>\n<li>Medidas técnicas e administrativas.</li>\n<li>Retenção e eliminação.</li>\n<li>Atendimento aos titulares.</li>\n<li>Tratamento de incidentes.</li>\n<li>Utilização de suboperadores.</li>\n<li>Transferências internacionais, quando existentes.</li>\n\n</ul>\n\n<p>\nRegras detalhadas deverão constar\ndo Anexo de Privacidade/LGPD\nou de instrumento específico de tratamento de dados.\n</p>",
      "title": "16. Privacidade, LGPD e tratamento de dados"
    },
    {
      "html": "<h3>Dependências externas</h3>\n\n<p>\nAlgumas funcionalidades poderão depender\nde provedores de nuvem, modelos de IA,\nbancos de dados, APIs, sistemas corporativos\nou outros serviços de terceiros.\n</p>\n\n<p>\nA contratação definitiva deverá definir,\nquando necessário, responsabilidades relacionadas\na esses serviços e impactos decorrentes\nde eventual indisponibilidade externa.\n</p>\n\n<p>\nQuando terceiros participarem do tratamento\nde dados pessoais, deverão ser observadas\nas exigências legais e contratuais aplicáveis\naos respectivos suboperadores.\n</p>",
      "title": "17. Serviços de terceiros e subcontratados"
    },
    {
      "html": "<h3>Responsabilidade contratual</h3>\n\n<p>\nA distribuição das responsabilidades deverá\nconsiderar a natureza dos serviços,\nos riscos envolvidos, as obrigações assumidas\ne a legislação aplicável.\n</p>\n\n<p>\nQualquer limitação financeira de responsabilidade,\nexclusão de determinadas categorias de danos,\nindenização ou exceção deverá ser validada\njuridicamente antes do uso comercial.\n</p>\n\n<p>\nEsta versão demonstrativa não estabelece\num teto definitivo de responsabilidade.\n</p>\n\n<p>\nSituações relacionadas a fraude, dolo,\nconfidencialidade, proteção de dados,\npropriedade intelectual ou outras matérias\nespecíficas poderão exigir tratamento diferente.\n</p>\n\n<p class=\"document-legal-note\">\nOs limites de responsabilidade da versão comercial\nserão definidos após análise jurídica.\n</p>",
      "title": "18. Responsabilidade, limitações e indenização"
    },
    {
      "html": "<h3>Encerramento da relação contratual</h3>\n\n<p>\nA versão definitiva deverá estabelecer hipóteses\nde suspensão, cancelamento, rescisão\ne encerramento.\n</p>\n\n<p>\nTambém deverão ser definidos prazos,\nnotificações e consequências aplicáveis.\n</p>\n\n<p>\nNo encerramento poderão ocorrer:\n</p>\n\n<ul>\n\n<li>Revogação de acessos.</li>\n<li>Desativação de integrações.</li>\n<li>Exportação de dados, quando prevista.</li>\n<li>Retenção obrigatória.</li>\n<li>Eliminação ou anonimização de dados.</li>\n<li>Encerramento de ambientes.</li>\n<li>Tratamento de valores pendentes.</li>\n\n</ul>\n\n<p>\nObrigações que, por sua natureza,\ndevam sobreviver ao encerramento\npoderão permanecer vigentes.\n</p>",
      "title": "19. Suspensão, rescisão e encerramento"
    },
    {
      "html": "<h3>Disposições finais</h3>\n\n<p>\nEste contrato deverá ser interpretado em conjunto\ncom a proposta comercial, Termos de Serviço,\nSLA, documentos de privacidade, segurança\ne demais anexos incorporados à contratação.\n</p>\n\n<p>\nA versão jurídica final deverá tratar,\nquando aplicável, de:\n</p>\n\n<ul>\n\n<li>Força maior.</li>\n<li>Cessão contratual.</li>\n<li>Comunicações entre as partes.</li>\n<li>Alterações contratuais.</li>\n<li>Independência das cláusulas.</li>\n<li>Integralidade do acordo.</li>\n<li>Legislação aplicável.</li>\n<li>Foro ou mecanismo de solução de conflitos.</li>\n\n</ul>\n\n<div class=\"document-data-box\">\n\n<p><strong>Empresa:</strong> {{COMPANY}}</p>\n<p><strong>CNPJ:</strong> {{CNPJ}}</p>\n<p><strong>Representante:</strong> {{REPRESENTATIVE}}</p>\n<p><strong>Cargo:</strong> {{ROLE}}</p>\n<p><strong>E-mail:</strong> {{EMAIL}}</p>\n<p><strong>Solução:</strong> {{SOLUTION_ID}}</p>\n<p><strong>Data de referência:</strong> {{DATE}}</p>\n\n</div>\n\n<p>\nEm produção, o aceite eletrônico deverá registrar\nde forma verificável usuário, organização,\nversão do documento, data e hora,\nevidência de consentimento e trilha de auditoria.\n</p>\n\n<p>\nA versão aceita deverá possuir identificação\ne hash próprio para permitir verificação\nda integridade do conteúdo posteriormente.\n</p>\n\n<p class=\"document-legal-note\">\nSTATUS: PENDING_LEGAL_REVIEW.\nDocumento demonstrativo, versão 1.0-demo.\nNão utilizar como contrato comercial definitivo\nsem revisão jurídica.\n</p>",
      "title": "20. Disposições gerais, aceite e assinatura eletrônica"
    }
  ]
},

        /* ==================================================
           PROPOSTA - 3 PAGINAS
           ================================================== */

        proposal: {

            type:
                "ANEXO I",

            title:
                "Proposta comercial",

            version:
                "Versão dinâmica",

            pages: [

                {
                    title:
                        "1. Resumo executivo",

                    html: `
                        <h3>Resumo da solução proposta</h3>

                        <div class="document-data-box">
                            <p><strong>Plano:</strong> {{PLAN}}</p>
                            <p><strong>Solução:</strong> {{SOLUTION_ID}}</p>
                            <p><strong>Módulos:</strong> {{MODULES}}</p>
                            <p><strong>Usuários:</strong> {{USERS}}</p>
                        </div>

                        <p>
                            Esta proposta consolida a configuração
                            preparada durante o fluxo comercial
                            da plataforma.
                        </p>
                    `
                },

                {
                    title:
                        "2. Arquitetura e capacidades",

                    html: `
                        <h3>Componentes selecionados</h3>

                        <p><strong>Canais:</strong> {{CHANNELS}}</p>
                        <p><strong>Integrações:</strong> {{INTEGRATIONS}}</p>
                        <p><strong>Recursos:</strong> {{RESOURCES}}</p>
                        <p><strong>Dados:</strong> {{DATA}}</p>
                        <p><strong>RAG:</strong> {{RAG}}</p>

                        <p>
                            O dimensionamento final poderá ser
                            refinado durante a validação técnica.
                        </p>
                    `
                },

                {
                    title:
                        "3. Condições financeiras",

                    html: `
                        <h3>Resumo comercial</h3>

                        <div class="document-data-box">
                            <p><strong>Mensal:</strong> {{MONTHLY_PRICE}}</p>
                            <p><strong>Prazo:</strong> {{TERM}}</p>
                            <p><strong>Faturamento:</strong> {{BILLING}}</p>
                            <p><strong>Período estimado:</strong> {{PERIOD_PRICE}}</p>
                        </div>

                        <p class="document-legal-note">
                            Valores demonstrativos até formalização
                            comercial definitiva.
                        </p>
                    `
                }

            ]

        },


        /* ==================================================
           TERMOS - 4 PAGINAS
           ================================================== */

        terms: {

            type:
                "ANEXO II",

            title:
                "Termos de Serviço",

            version:
                "Versão 1.0",

            pages: [

                {
                    title: "1. Acesso e conta",
                    html: `
                        <h3>Acesso à plataforma</h3>
                        <p>
                            O acesso deverá ocorrer por usuários
                            autorizados pela organização contratante.
                            Credenciais são pessoais e não devem
                            ser compartilhadas de forma indevida.
                        </p>
                        <p>
                            A empresa deverá manter os perfis de
                            acesso compatíveis com as funções
                            exercidas por cada usuário.
                        </p>
                    `
                },

                {
                    title: "2. Uso aceitável",
                    html: `
                        <h3>Uso aceitável</h3>
                        <p>
                            A plataforma não deverá ser utilizada
                            para atividades ilícitas, abusivas,
                            fraudulentas ou que violem direitos
                            de terceiros.
                        </p>
                        <p>
                            A contratante é responsável pelos dados
                            e instruções enviados por seus usuários.
                        </p>
                    `
                },

                {
                    title: "3. Serviços e integrações",
                    html: `
                        <h3>Integrações e terceiros</h3>
                        <p>
                            Algumas funcionalidades podem depender
                            de APIs, serviços de nuvem, modelos
                            de IA ou sistemas de terceiros.
                        </p>
                        <p>
                            Disponibilidade e regras desses serviços
                            poderão afetar determinadas funcionalidades.
                        </p>
                    `
                },

                {
                    title: "4. Alterações e encerramento",
                    html: `
                        <h3>Alterações dos serviços</h3>
                        <p>
                            Evoluções técnicas poderão ocorrer
                            durante o ciclo de vida da plataforma,
                            respeitando os compromissos contratuais
                            aplicáveis.
                        </p>
                        <p>
                            Condições de suspensão ou encerramento
                            deverão observar o contrato principal
                            e as condições comerciais.
                        </p>
                    `
                }

            ]

        },


        /* ==================================================
           SLA - 3 PAGINAS
           ================================================== */

        sla: {

            type:
                "ANEXO III",

            title:
                "SLA e suporte",

            version:
                "Versão 1.0",

            pages: [

                {
                    title: "1. Disponibilidade",
                    html: `
                        <h3>Disponibilidade do serviço</h3>
                        <p>
                            Metas específicas de disponibilidade
                            deverão ser definidas na versão comercial
                            do SLA conforme plano e arquitetura.
                        </p>
                        <p>
                            Janelas programadas de manutenção,
                            eventos externos e situações previstas
                            contratualmente poderão ser excluídas
                            dos cálculos.
                        </p>
                    `
                },

                {
                    title: "2. Incidentes",
                    html: `
                        <h3>Classificação de incidentes</h3>
                        <ul>
                            <li>Crítico: indisponibilidade relevante.</li>
                            <li>Alto: impacto expressivo com operação degradada.</li>
                            <li>Médio: impacto parcial.</li>
                            <li>Baixo: dúvidas, melhorias ou baixo impacto.</li>
                        </ul>
                        <p>
                            Tempos específicos de resposta deverão
                            ser vinculados ao plano contratado.
                        </p>
                    `
                },

                {
                    title: "3. Canais de suporte",
                    html: `
                        <h3>Atendimento e comunicação</h3>
                        <p>
                            Os canais poderão incluir portal,
                            e-mail, chat, INNA Assistant e outros
                            meios previstos no plano.
                        </p>
                        <p>
                            Escalonamento e atendimento especializado
                            deverão seguir a matriz de suporte
                            definida para a contratação.
                        </p>
                    `
                }

            ]

        },


        /* ==================================================
           PRIVACIDADE - 4 PAGINAS
           ================================================== */

        privacy: {

            type:
                "ANEXO IV",

            title:
                "Privacidade e LGPD",

            version:
                "Versão 1.0",

            pages: [

                {
                    title: "1. Papéis e tratamento",
                    html: `
                        <h3>Tratamento de dados pessoais</h3>
                        <p>
                            Os papéis de controlador, operador
                            ou agentes relacionados deverão ser
                            definidos de acordo com cada operação.
                        </p>
                        <p>
                            O tratamento deve estar vinculado
                            a finalidades legítimas e instruções
                            compatíveis com a legislação aplicável.
                        </p>
                    `
                },

                {
                    title: "2. Segurança dos dados",
                    html: `
                        <h3>Proteção de dados</h3>
                        <p>
                            Devem ser adotadas medidas técnicas
                            e administrativas adequadas ao risco,
                            incluindo controle de acesso, registro
                            de eventos e proteção de credenciais.
                        </p>
                    `
                },

                {
                    title: "3. Retenção e eliminação",
                    html: `
                        <h3>Ciclo de vida dos dados</h3>
                        <p>
                            Prazos de retenção devem observar
                            finalidades, obrigações legais,
                            requisitos contratuais e políticas
                            internas aplicáveis.
                        </p>
                        <p>
                            Após o término, dados deverão ser
                            devolvidos, anonimizados ou eliminados
                            conforme as condições acordadas.
                        </p>
                    `
                },

                {
                    title: "4. Direitos e incidentes",
                    html: `
                        <h3>Governança de privacidade</h3>
                        <p>
                            Solicitações relacionadas a titulares,
                            autoridades ou incidentes deverão seguir
                            processos apropriados e responsabilidades
                            definidas entre as partes.
                        </p>
                        <p class="document-legal-note">
                            O instrumento definitivo de tratamento
                            de dados deve ser revisado juridicamente.
                        </p>
                    `
                }

            ]

        },


        /* ==================================================
           SEGURANCA - 3 PAGINAS
           ================================================== */

        security: {

            type:
                "ANEXO V",

            title:
                "Segurança da informação",

            version:
                "Versão 1.0",

            pages: [

                {
                    title: "1. Identidade e acesso",
                    html: `
                        <h3>Controle de acesso</h3>
                        <p>
                            Usuários, funções e permissões deverão
                            seguir o princípio de menor privilégio.
                        </p>
                        <p>
                            Recursos como MFA, SSO e RBAC poderão
                            ser aplicados conforme o plano
                            e a configuração contratada.
                        </p>
                    `
                },

                {
                    title: "2. Proteção e monitoramento",
                    html: `
                        <h3>Proteção operacional</h3>
                        <p>
                            A arquitetura poderá utilizar logs,
                            monitoramento, criptografia, backups,
                            gestão de segredos e controles de rede.
                        </p>
                        <p>
                            A profundidade dos controles dependerá
                            dos serviços efetivamente utilizados.
                        </p>
                    `
                },

                {
                    title: "3. Incidentes de segurança",
                    html: `
                        <h3>Resposta a incidentes</h3>
                        <p>
                            Eventos relevantes deverão ser
                            investigados, registrados e tratados
                            de acordo com procedimentos internos
                            e obrigações aplicáveis.
                        </p>
                        <p>
                            Comunicação entre as partes deverá
                            ocorrer conforme criticidade e impacto.
                        </p>
                    `
                }

            ]

        },


        /* ==================================================
           COMERCIAL - 3 PAGINAS
           ================================================== */

        commercial: {

            type:
                "ANEXO VI",

            title:
                "Condições comerciais",

            version:
                "Versão 1.0",

            pages: [

                {
                    title: "1. Prazo e faturamento",
                    html: `
                        <h3>Condições selecionadas</h3>

                        <div class="document-data-box">
                            <p><strong>Plano:</strong> {{PLAN}}</p>
                            <p><strong>Prazo:</strong> {{TERM}}</p>
                            <p><strong>Faturamento:</strong> {{BILLING}}</p>
                            <p><strong>Mensal:</strong> {{MONTHLY_PRICE}}</p>
                        </div>
                    `
                },

                {
                    title: "2. Expansões e alterações",
                    html: `
                        <h3>Alterações comerciais</h3>
                        <p>
                            Inclusões de módulos, capacidade,
                            integrações ou recursos poderão alterar
                            os valores originalmente previstos.
                        </p>
                        <p>
                            Mudanças relevantes deverão ser
                            apresentadas para aprovação antes
                            de sua aplicação comercial.
                        </p>
                    `
                },

                {
                    title: "3. Renovação e encerramento",
                    html: `
                        <h3>Renovação e término</h3>
                        <p>
                            Critérios definitivos de renovação,
                            reajuste, aviso prévio, cancelamento
                            e multas, quando aplicáveis, deverão
                            constar da versão jurídica final.
                        </p>

                        <p class="document-legal-note">
                            Este documento é demonstrativo e não
                            estabelece sozinho condições comerciais
                            juridicamente vinculantes.
                        </p>
                    `
                }

            ]

        }

    };


    /* ======================================================
       ESTADO
       ====================================================== */

    let readState =
        getJson(
            STORAGE_KEY
        ) || {};


    let activeDocument =
        null;


    let activePage =
        0;


    const modal =
        document.getElementById(
            "contract-document-modal"
        );


    const content =
        document.getElementById(
            "document-page-content"
        );


    const title =
        document.getElementById(
            "document-viewer-title"
        );


    const type =
        document.getElementById(
            "document-viewer-type"
        );


    const version =
        document.getElementById(
            "document-viewer-version"
        );


    const pagesLabel =
        document.getElementById(
            "document-viewer-pages"
        );


    const paperPage =
        document.getElementById(
            "document-paper-page"
        );


    const paperReference =
        document.getElementById(
            "document-paper-reference"
        );


    const progress =
        document.getElementById(
            "document-page-progress"
        );


    const prev =
        document.getElementById(
            "document-prev"
        );


    const next =
        document.getElementById(
            "document-next"
        );


    const confirmRead =
        document.getElementById(
            "document-confirm-read"
        );


    function saveState() {

        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(
                readState
            )
        );

    }


    function ensureDocumentState(id) {

        if (!readState[id]) {

            readState[id] = {
                visitedPages: [],
                confirmed: false,
                confirmedAt: null
            };

        }

        return readState[id];

    }


    function markPageVisited() {

        if (!activeDocument) {
            return;
        }


        const state =
            ensureDocumentState(
                activeDocument
            );


        if (
            !state.visitedPages.includes(
                activePage
            )
        ) {

            state.visitedPages.push(
                activePage
            );


            saveState();

        }

    }


    function renderStatuses() {

        let confirmedCount =
            0;


        REQUIRED_DOCUMENTS
            .forEach(id => {

                const state =
                    readState[id];


                const badge =
                    document.querySelector(
                        `[data-doc-status="${id}"]`
                    );


                if (!badge) {
                    return;
                }


                badge.classList.remove(
                    "reading",
                    "read"
                );


                if (state?.confirmed) {

                    confirmedCount += 1;

                    badge.textContent =
                        "✓ Leitura confirmada";

                    badge.classList.add(
                        "read"
                    );

                }

                else if (
                    state?.visitedPages?.length
                ) {

                    badge.textContent =
                        "Em leitura";

                    badge.classList.add(
                        "reading"
                    );

                }

                else {

                    badge.textContent =
                        "Não lido";

                }

            });


        const counter =
            document.getElementById(
                "contract-docs-read-count"
            );


        if (counter) {

            counter.textContent =
                `${confirmedCount} / ${REQUIRED_DOCUMENTS.length}`;

        }


        const bar =
            document.getElementById(
                "contract-docs-progress-bar"
            );


        if (bar) {

            bar.style.width =
                `${
                    (
                        confirmedCount /
                        REQUIRED_DOCUMENTS.length
                    ) * 100
                }%`;

        }

    }


    function renderPage() {

        const doc =
            docs[activeDocument];


        if (!doc) {
            return;
        }


        const page =
            doc.pages[activePage];


        markPageVisited();


        const ctx =
            currentContext();


        type.textContent =
            doc.type;


        title.textContent =
            doc.title;


        version.textContent =
            doc.version;


        pagesLabel.textContent =
            `Página ${activePage + 1} de ${doc.pages.length}`;


        paperPage.textContent =
            `Página ${activePage + 1} de ${doc.pages.length}`;


        paperReference.textContent =
            `${doc.title} · ${doc.version}`;


        content.innerHTML = `
            <span class="document-page-section">
                ${escapeHtml(page.title)}
            </span>

            ${applyTokens(
                page.html,
                ctx
            )}
        `;


        progress.style.width =
            `${
                (
                    (activePage + 1) /
                    doc.pages.length
                ) * 100
            }%`;


        prev.disabled =
            activePage === 0;


        if (
            activePage ===
            doc.pages.length - 1
        ) {

            next.hidden =
                true;

        }
        else {

            next.hidden =
                false;

        }


        const state =
            ensureDocumentState(
                activeDocument
            );


        const allVisited =
            state.visitedPages.length >=
            doc.pages.length;


        confirmRead.disabled =
            !allVisited;


        confirmRead.textContent =
            state.confirmed
                ? "✓ Leitura já confirmada"
                : "Confirmar leitura ✓";


        renderStatuses();

    }


    function openDocument(id) {

        if (!docs[id]) {
            return;
        }


        activeDocument =
            id;


        const state =
            ensureDocumentState(
                id
            );


        if (
            state.visitedPages.length
        ) {

            activePage =
                Math.max(
                    ...state.visitedPages
                );

        }
        else {

            activePage =
                0;

        }


        modal.hidden =
            false;


        document.body.classList.add(
            "contract-document-open"
        );


        renderPage();

    }


    function closeDocument() {

        modal.hidden =
            true;


        document.body.classList.remove(
            "contract-document-open"
        );


        activeDocument =
            null;

    }


    document
        .querySelectorAll(
            ".contract-open-document"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    openDocument(
                        button.dataset.document
                    );

                }
            );

        });


    prev?.addEventListener(
        "click",
        () => {

            if (activePage > 0) {

                activePage -= 1;

                renderPage();

            }

        }
    );


    next?.addEventListener(
        "click",
        () => {

            const doc =
                docs[activeDocument];


            if (
                doc &&
                activePage <
                doc.pages.length - 1
            ) {

                activePage += 1;

                renderPage();

            }

        }
    );


    confirmRead?.addEventListener(
        "click",
        () => {

            if (!activeDocument) {
                return;
            }


            const doc =
                docs[activeDocument];


            const state =
                ensureDocumentState(
                    activeDocument
                );


            if (
                state.visitedPages.length <
                doc.pages.length
            ) {
                return;
            }


            state.confirmed =
                true;


            state.confirmedAt =
                new Date()
                    .toISOString();


            saveState();


            renderStatuses();


            confirmRead.textContent =
                "✓ Leitura confirmada";


            setTimeout(
                closeDocument,
                500
            );

        }
    );


    document
        .getElementById(
            "contract-viewer-close"
        )
        ?.addEventListener(
            "click",
            closeDocument
        );


    document
        .getElementById(
            "contract-document-backdrop"
        )
        ?.addEventListener(
            "click",
            closeDocument
        );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape" &&
                !modal.hidden
            ) {

                closeDocument();

            }

        }
    );


    /* ======================================================
       IMPRESSAO / SALVAR PDF
       ====================================================== */

    document
        .getElementById(
            "document-print"
        )
        ?.addEventListener(
            "click",
            () => {

                if (!activeDocument) {
                    return;
                }


                const doc =
                    docs[activeDocument];


                const ctx =
                    currentContext();


                const body =
                    doc.pages.map(
                        (page, index) => `
                            <section class="print-page">
                                <header>
                                    <strong>Sabino.AI</strong>
                                    <span>
                                        ${escapeHtml(doc.title)}
                                    </span>
                                </header>

                                <h2>
                                    ${escapeHtml(page.title)}
                                </h2>

                                ${applyTokens(
                                    page.html,
                                    ctx
                                )}

                                <footer>
                                    Página ${index + 1}
                                    de ${doc.pages.length}
                                </footer>
                            </section>
                        `
                    ).join("");


                const printWindow =
                    window.open(
                        "",
                        "_blank"
                    );


                if (!printWindow) {
                    return;
                }


                printWindow.document.write(`
                    <!doctype html>

                    <html lang="pt-BR">

                    <head>

                        <meta charset="utf-8">

                        <title>
                            ${escapeHtml(doc.title)}
                        </title>

                        <style>

                            body {
                                margin: 0;
                                font-family:
                                    Arial,
                                    sans-serif;
                                color: #17202a;
                            }

                            .print-page {
                                min-height: 250mm;
                                padding: 18mm;
                                box-sizing: border-box;
                                page-break-after: always;
                            }

                            .print-page header,
                            .print-page footer {
                                display: flex;
                                justify-content: space-between;
                                color: #666;
                                font-size: 10px;
                            }

                            .print-page header {
                                padding-bottom: 12px;
                                border-bottom: 1px solid #ddd;
                            }

                            .print-page footer {
                                margin-top: 30px;
                                padding-top: 12px;
                                border-top: 1px solid #ddd;
                            }

                            h2 {
                                margin-top: 34px;
                            }

                            h3 {
                                margin-top: 26px;
                            }

                            p,
                            li {
                                font-size: 12px;
                                line-height: 1.7;
                            }

                            .document-data-box {
                                padding: 15px;
                                margin: 20px 0;
                                border: 1px solid #ddd;
                            }

                            @media print {

                                .print-page {
                                    page-break-after:
                                        always;
                                }

                            }

                        </style>

                    </head>

                    <body>
                        ${body}
                    </body>

                    </html>
                `);


                printWindow.document.close();


                printWindow.focus();


                setTimeout(
                    () => {
                        printWindow.print();
                    },
                    300
                );

            }
        );


    renderStatuses();

});

