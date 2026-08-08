export type NodeUsageContent = {
  summary: string;
  examples: string[];
};

type NodeUsageDefinition = NodeUsageContent & {
  keys: readonly string[];
};

const NODE_USAGE_DEFINITIONS:
  readonly NodeUsageDefinition[] = [
    // ==================================================
    // MÓDULO DE REDES
    // ==================================================

    {
      keys: [
        "inna",
        "M-TEC-09",
        "redes-telecomunicacoes-conectividade",
        "Redes, Telecomunicações e Conectividade",
      ],
      summary:
        "Centraliza a conectividade, a comunicação e o monitoramento de rede da plataforma INNA.",
      examples: [
        "🌐 Monitorar redes e internet",
        "📊 Detectar falhas de conexão",
        "📡 Gerenciar equipamentos de rede",
        "🚨 Gerar alertas de indisponibilidade",
        "📈 Analisar o desempenho da rede",
      ],
    },

    // ==================================================
    // OUTROS MÓDULOS EXECUTIVOS DA PLATAFORMA
    // ==================================================

    {
      keys: [
        "mod-testes-qualidade",
        "testes-qualidade-software",
        "Testes, Qualidade e Confiabilidade de Software",
      ],
      summary:
        "Valida se aplicações, integrações e recursos da INNA funcionam corretamente, com qualidade e confiabilidade.",
      examples: [
        "✅ Executar testes automáticos",
        "🐞 Detectar erros e regressões",
        "📊 Medir cobertura de testes",
        "⚡ Validar desempenho",
        "📋 Gerar relatórios de qualidade",
      ],
    },

    {
      keys: [
        "mod-mobile-omnichannel",
        "aplicativos-moveis-omnichannel",
        "Aplicativos Móveis e Experiências Omnicanal",
      ],
      summary:
        "Entrega experiências integradas em aplicativos, web, mensageria, e-mail e outros canais digitais.",
      examples: [
        "📱 Disponibilizar aplicativo Android e iPhone",
        "💻 Operar a plataforma web",
        "💬 Atender pelo WhatsApp",
        "🤖 Integrar o Telegram",
        "📧 Enviar comunicações por e-mail",
        "🌐 Disponibilizar sites e portais",
      ],
    },

    {
      keys: [
        "mod-identidade-digital",
        "identidade-digital",
        "Identidade Digital e Credenciais Verificáveis",
      ],
      summary:
        "Confirma identidades, controla acessos e valida credenciais ou documentos digitais com segurança.",
      examples: [
        "👤 Realizar login seguro",
        "🪪 Verificar identidade",
        "📄 Validar certificados e diplomas",
        "✍️ Aplicar assinaturas digitais",
        "🔐 Controlar acessos e permissões",
      ],
    },

    {
      keys: [
        "mod-governanca-conformidade",
        "governanca-politicas-conformidade",
        "Governança, Políticas e Conformidade Tecnológica",
      ],
      summary:
        "Define políticas, controles, responsabilidades e regras para o uso seguro da tecnologia na INNA.",
      examples: [
        "🔐 Controlar acessos e permissões",
        "📋 Registrar auditorias",
        "🛡️ Aplicar proteção de dados e LGPD",
        "⚖️ Definir políticas de uso da IA",
        "✅ Aprovar ações sensíveis",
      ],
    },

    {
      keys: [
        "mod-rastreabilidade-dados",
        "rastreabilidade-proveniencia-dados",
        "Rastreabilidade e Proveniência de Dados",
      ],
      summary:
        "Registra a origem, as alterações e os responsáveis pelos dados utilizados pela plataforma.",
      examples: [
        "📄 Registrar a origem dos dados",
        "🕘 Manter histórico de alterações",
        "👤 Identificar quem realizou cada ação",
        "🔍 Auditar informações",
        "✅ Garantir confiabilidade dos dados",
      ],
    },

    {
      keys: [
        "mod-inteligencia-decisao",
        "inteligencia-decisao-empresarial",
        "Inteligência de Decisão Empresarial",
      ],
      summary:
        "Transforma indicadores, dados e análises em previsões, alertas e recomendações para decisões empresariais.",
      examples: [
        "📊 Analisar indicadores",
        "📈 Fazer previsões",
        "⚠️ Identificar riscos",
        "💡 Sugerir ações",
        "📋 Gerar recomendações executivas",
      ],
    },

    {
      keys: [
        "mod-seguranca-resiliencia",
        "seguranca-operacional-resiliencia",
        "Segurança Operacional e Resiliência",
      ],
      summary:
        "Protege a operação da INNA e mantém os serviços disponíveis diante de falhas ou incidentes.",
      examples: [
        "🔒 Proteger contra ataques",
        "⚠️ Detectar incidentes",
        "💾 Executar backup e recuperação",
        "🔄 Garantir continuidade do serviço",
        "📊 Monitorar a saúde da plataforma",
      ],
    },

    {
      keys: [
        "mod-ia-responsavel",
        "ia-responsavel-etica-riscos",
        "IA Responsável, Ética e Gestão de Riscos",
      ],
      summary:
        "Garante que as soluções de IA sejam seguras, éticas, explicáveis e alinhadas às políticas da organização.",
      examples: [
        "🤖 Evitar respostas inadequadas",
        "⚖️ Reduzir vieses",
        "🔒 Proteger dados dos usuários",
        "📋 Cumprir leis e políticas",
        "🚨 Identificar riscos e ações inseguras",
      ],
    },

    {
      keys: [
        "mod-avaliacao-ia",
        "avaliacao-ia-benchmarks-red-team",
        "Avaliação de IA, Benchmarks e Red Team",
      ],
      summary:
        "Avalia qualidade, segurança, precisão, robustez e desempenho dos modelos de inteligência artificial.",
      examples: [
        "✅ Medir o desempenho da IA",
        "📊 Comparar modelos e benchmarks",
        "🛡️ Simular ataques e falhas",
        "🚨 Detectar alucinações e riscos",
        "📋 Gerar relatórios de avaliação",
      ],
    },

    {
      keys: [
        "mod-certificacao-ia",
        "certificacao-ia-evidencias",
        "Certificação de IA e Evidências do Sistema",
      ],
      summary:
        "Organiza evidências para comprovar que modelos, processos e controles da IA foram avaliados corretamente.",
      examples: [
        "📋 Gerar evidências de testes",
        "✅ Registrar validações e auditorias",
        "📊 Comprovar desempenho da IA",
        "🔒 Demonstrar conformidade",
        "📄 Emitir relatórios para clientes e auditorias",
      ],
    },

    // ==================================================
    // MÓDULOS PRINCIPAIS JÁ DEFINIDOS PARA A INNA
    // ==================================================

    {
      keys: [
        "financial_solutions",
        "financial-solutions",
        "solucoes-financeiras",
        "Soluções Financeiras",
      ],
      summary:
        "Reúne educação financeira, diagnósticos, planejamento, orçamento, dívidas e orientação inteligente.",
      examples: [
        "💰 Criar diagnósticos financeiros",
        "📊 Analisar receitas e despesas",
        "🎯 Planejar objetivos financeiros",
        "💳 Orientar sobre dívidas",
        "🧠 Gerar recomendações personalizadas",
      ],
    },

    {
      keys: [
        "data_platform_governance",
        "data-platform-governance",
        "plataforma-dados-governanca",
        "Plataforma de Dados e Governança",
      ],
      summary:
        "Organiza ingestão, transformação, qualidade, catálogo, linhagem, armazenamento e acesso aos dados.",
      examples: [
        "🗄️ Operar Data Lake e Lakehouse",
        "🔄 Executar processos ETL e ELT",
        "📚 Manter catálogo de dados",
        "🔍 Acompanhar linhagem e qualidade",
        "🔐 Controlar acesso e retenção",
      ],
    },

    {
      keys: [
        "cybersecurity_fraud_prevention",
        "cybersecurity-fraud-prevention",
        "ciberseguranca-prevencao-fraudes",
        "Cibersegurança e Prevenção a Fraudes",
      ],
      summary:
        "Detecta ameaças, golpes, phishing, fraudes e comportamentos suspeitos na plataforma.",
      examples: [
        "🛡️ Detectar tentativas de fraude",
        "🎣 Identificar phishing",
        "🚨 Gerar alertas de segurança",
        "🔍 Investigar eventos suspeitos",
        "📋 Registrar incidentes e evidências",
      ],
    },

    {
      keys: [
        "cloud_devops_finops",
        "cloud-devops-finops",
        "cloud-devops-e-finops",
        "Cloud, DevOps e FinOps",
      ],
      summary:
        "Gerencia infraestrutura em nuvem, entregas de software, disponibilidade, observabilidade e custos.",
      examples: [
        "☁️ Operar ambientes em nuvem",
        "🚀 Automatizar deploys",
        "🔄 Executar pipelines de CI/CD",
        "📊 Monitorar disponibilidade",
        "💰 Controlar custos com FinOps",
      ],
    },

    {
      keys: [
        "ai_operations",
        "ai-operations",
        "operacoes-de-ia",
        "Operações de IA",
      ],
      summary:
        "Monitora modelos, agentes, custos, desempenho, eventos e saúde operacional das soluções de IA.",
      examples: [
        "🤖 Monitorar agentes e modelos",
        "📊 Acompanhar tokens e custos",
        "🚨 Detectar falhas e degradações",
        "🕘 Registrar eventos e versões",
        "⚙️ Gerenciar operações de LLMOps",
      ],
    },

    {
      keys: [
        "tools_analytics",
        "tools-analytics",
        "ferramentas-analytics",
        "Ferramentas e Analytics",
      ],
      summary:
        "Centraliza métricas, logs, eventos, análises e monitoramento das ferramentas utilizadas pela INNA.",
      examples: [
        "📊 Criar dashboards operacionais",
        "📝 Consultar logs",
        "🔍 Investigar falhas",
        "🚨 Configurar alertas",
        "📈 Analisar uso e desempenho",
      ],
    },

    // ==================================================
    // ÁREAS DO MÓDULO DE REDES
    // ==================================================

    {
      keys: [
        "area-1",
        "Conectividade e Acesso",
      ],
      summary:
        "Gerencia os meios utilizados por usuários, dispositivos e unidades para acessar a rede.",
      examples: [
        "📶 Disponibilizar Wi-Fi corporativo",
        "🌐 Acompanhar links de internet",
        "📱 Controlar acessos fixos e móveis",
      ],
    },

    {
      keys: [
        "area-2",
        "Redes de Transporte",
      ],
      summary:
        "Transporta dados entre unidades, aplicações, provedores, data centers e ambientes de nuvem.",
      examples: [
        "🌍 Operar o backbone",
        "💡 Monitorar redes ópticas",
        "🔗 Gerenciar conexões MPLS",
      ],
    },

    {
      keys: [
        "area-3",
        "Redes Móveis",
      ],
      summary:
        "Sustenta a conectividade móvel e o tráfego das redes celulares utilizadas pela plataforma.",
      examples: [
        "📱 Monitorar redes 4G e 5G",
        "📦 Gerenciar o core de pacotes",
        "📡 Acompanhar estações-base",
      ],
    },

    {
      keys: [
        "area-4",
        "Serviços de Comunicação",
      ],
      summary:
        "Entrega serviços de voz, mensagens e notificações aos usuários e sistemas da INNA.",
      examples: [
        "☎️ Realizar chamadas VoIP",
        "💬 Enviar mensagens SMS",
        "🔔 Disparar notificações push",
      ],
    },

    {
      keys: [
        "area-5",
        "Segurança de Redes",
      ],
      summary:
        "Protege acessos, conexões e tráfego contra ataques, invasões e comportamentos suspeitos.",
      examples: [
        "🧱 Aplicar regras de firewall",
        "🔐 Criar conexões VPN",
        "🛡️ Detectar ataques e ameaças",
      ],
    },

    {
      keys: [
        "area-6",
        "Monitoramento e Gestão",
      ],
      summary:
        "Monitora disponibilidade, incidentes, alarmes, capacidade e desempenho da infraestrutura de rede.",
      examples: [
        "📊 Acompanhar ativos em tempo real",
        "🚨 Detectar indisponibilidades",
        "📈 Analisar capacidade e desempenho",
      ],
    },

    {
      keys: [
        "area-7",
        "Infraestrutura e Suporte",
      ],
      summary:
        "Mantém a infraestrutura física e os serviços necessários para sustentar a operação da rede.",
      examples: [
        "🏢 Operar data centers e POPs",
        "⚡ Monitorar energia e ambiente",
        "🛠️ Executar manutenção e suporte",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — CONECTIVIDADE E ACESSO
    // ==================================================

    {
      keys: [
        "submodule-1.1",
        "Acesso Fixo e Móvel",
      ],
      summary:
        "Gerencia conexões fixas e móveis utilizadas por pessoas, dispositivos e unidades.",
      examples: [
        "📱 Acompanhar cobertura móvel",
        "🔌 Monitorar acessos fixos",
        "📊 Medir disponibilidade de conexão",
      ],
    },

    {
      keys: [
        "submodule-1.2",
        "Banda Larga e Internet",
      ],
      summary:
        "Controla links de internet e capacidade de banda utilizada pelos serviços da INNA.",
      examples: [
        "🌐 Monitorar provedores",
        "📈 Medir consumo de banda",
        "🚨 Identificar quedas de internet",
      ],
    },

    {
      keys: [
        "submodule-1.3",
        "Wi-Fi e Redes Locais",
      ],
      summary:
        "Gerencia redes locais e acesso sem fio em escritórios, unidades e ambientes operacionais.",
      examples: [
        "📶 Gerenciar pontos de acesso",
        "🖥️ Monitorar dispositivos conectados",
        "🔐 Proteger redes internas",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — REDES DE TRANSPORTE
    // ==================================================

    {
      keys: [
        "submodule-2.1",
        "Backbone e Trânsito",
      ],
      summary:
        "Mantém as rotas principais responsáveis pelo transporte de grandes volumes de dados.",
      examples: [
        "🌍 Monitorar trânsito de dados",
        "🔀 Gerenciar rotas principais",
        "📊 Acompanhar capacidade do backbone",
      ],
    },

    {
      keys: [
        "submodule-2.2",
        "Redes Ópticas e DWDM",
      ],
      summary:
        "Gerencia redes ópticas de alta capacidade para transmissões de longa distância.",
      examples: [
        "💡 Monitorar enlaces ópticos",
        "📡 Operar canais DWDM",
        "🚨 Identificar perda de sinal",
      ],
    },

    {
      keys: [
        "submodule-2.3",
        "SDH/SONET e MPLS",
      ],
      summary:
        "Controla tecnologias de transporte e roteamento utilizadas em redes corporativas.",
      examples: [
        "🔗 Gerenciar circuitos MPLS",
        "📊 Acompanhar rotas e latência",
        "🚨 Detectar falhas de transporte",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — REDES MÓVEIS
    // ==================================================

    {
      keys: [
        "submodule-3.1",
        "2G / 3G / 4G / 5G",
      ],
      summary:
        "Monitora diferentes gerações de redes móveis e sua disponibilidade.",
      examples: [
        "📱 Acompanhar cobertura 4G e 5G",
        "📊 Medir qualidade do sinal",
        "🚨 Detectar indisponibilidade móvel",
      ],
    },

    {
      keys: [
        "submodule-3.2",
        "Core de Pacotes",
      ],
      summary:
        "Gerencia o núcleo responsável pelo encaminhamento de dados nas redes móveis.",
      examples: [
        "📦 Monitorar sessões de dados",
        "🔀 Acompanhar roteamento de pacotes",
        "📈 Medir utilização do core",
      ],
    },

    {
      keys: [
        "submodule-3.3",
        "RAN e Estações-Base",
      ],
      summary:
        "Gerencia a infraestrutura de acesso por rádio e suas estações-base.",
      examples: [
        "📡 Monitorar antenas",
        "📶 Analisar cobertura",
        "🛠️ Planejar manutenção de estações",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — SERVIÇOS DE COMUNICAÇÃO
    // ==================================================

    {
      keys: [
        "submodule-4.1",
        "Voz sobre IP (VoIP)",
      ],
      summary:
        "Entrega chamadas de voz utilizando a infraestrutura de dados da plataforma.",
      examples: [
        "☎️ Realizar chamadas internas",
        "🎧 Integrar atendimento por voz",
        "📊 Monitorar qualidade das chamadas",
      ],
    },

    {
      keys: [
        "submodule-4.2",
        "Mensageria e SMS",
      ],
      summary:
        "Distribui mensagens transacionais, avisos e confirmações por serviços de mensageria.",
      examples: [
        "💬 Enviar SMS",
        "🔑 Enviar códigos de verificação",
        "📨 Confirmar eventos e operações",
      ],
    },

    {
      keys: [
        "submodule-4.3",
        "Push e Notificações",
      ],
      summary:
        "Envia notificações em tempo real para aplicativos, navegadores e dispositivos.",
      examples: [
        "🔔 Enviar alertas importantes",
        "📱 Notificar usuários no aplicativo",
        "🚨 Comunicar indisponibilidades",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — SEGURANÇA DE REDES
    // ==================================================

    {
      keys: [
        "submodule-5.1",
        "Firewall e NGFW",
      ],
      summary:
        "Filtra conexões e bloqueia tráfego não autorizado ou potencialmente perigoso.",
      examples: [
        "🧱 Aplicar regras de acesso",
        "🛡️ Bloquear ameaças",
        "📋 Registrar eventos de segurança",
      ],
    },

    {
      keys: [
        "submodule-5.2",
        "VPN e Túnel Seguro",
      ],
      summary:
        "Cria conexões criptografadas para usuários, unidades e serviços remotos.",
      examples: [
        "🔐 Permitir acesso remoto seguro",
        "🔗 Conectar unidades",
        "🛡️ Proteger dados em trânsito",
      ],
    },

    {
      keys: [
        "submodule-5.3",
        "IDS/IPS e DDoS",
      ],
      summary:
        "Detecta ataques, bloqueia invasões e reduz o impacto de tentativas de indisponibilidade.",
      examples: [
        "🚨 Detectar invasões",
        "🛡️ Bloquear ataques",
        "📊 Analisar tráfego suspeito",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — MONITORAMENTO E GESTÃO
    // ==================================================

    {
      keys: [
        "submodule-6.1",
        "Monitoramento de Redes",
      ],
      summary:
        "Acompanha continuamente disponibilidade, uso e condição dos ativos de rede.",
      examples: [
        "🟢 Verificar ativos disponíveis",
        "📊 Exibir métricas em tempo real",
        "🚨 Detectar falhas",
      ],
    },

    {
      keys: [
        "submodule-6.2",
        "NMS e Alarmes",
      ],
      summary:
        "Centraliza o gerenciamento da rede e os alertas gerados por dispositivos e serviços.",
      examples: [
        "🚨 Receber alarmes",
        "🖥️ Gerenciar equipamentos",
        "📋 Registrar incidentes",
      ],
    },

    {
      keys: [
        "submodule-6.3",
        "Análise de Desempenho",
      ],
      summary:
        "Analisa latência, capacidade, erros e tendências de utilização da rede.",
      examples: [
        "📈 Avaliar desempenho",
        "⏱️ Medir latência",
        "💡 Planejar melhorias",
      ],
    },

    // ==================================================
    // SUBMÓDULOS — INFRAESTRUTURA E SUPORTE
    // ==================================================

    {
      keys: [
        "submodule-7.1",
        "Data Centers e POPs",
      ],
      summary:
        "Mantém os ambientes físicos onde equipamentos e serviços de rede são hospedados.",
      examples: [
        "🏢 Gerenciar data centers",
        "📡 Operar pontos de presença",
        "📊 Monitorar capacidade física",
      ],
    },

    {
      keys: [
        "submodule-7.2",
        "Energia e Ambiente",
      ],
      summary:
        "Monitora energia, temperatura, umidade e condições necessárias para os equipamentos.",
      examples: [
        "⚡ Monitorar alimentação elétrica",
        "🌡️ Acompanhar temperatura",
        "🚨 Detectar riscos ambientais",
      ],
    },

    {
      keys: [
        "submodule-7.3",
        "Manutenção e Suporte",
      ],
      summary:
        "Coordena manutenção preventiva, correções, atendimento e suporte à infraestrutura.",
      examples: [
        "🛠️ Executar manutenção",
        "🎫 Gerenciar chamados",
        "✅ Validar correções",
      ],
    },
  ];

const normalizeKey = (
  value: string,
): string => {
  return value
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      "",
    )
    .toLowerCase()
    .replace(
      /[^a-z0-9]+/g,
      "-",
    )
    .replace(
      /^-+|-+$/g,
      "",
    );
};

const CONTENT_INDEX:
  ReadonlyMap<string, NodeUsageContent> = (() => {
    const index =
      new Map<string, NodeUsageContent>();

    NODE_USAGE_DEFINITIONS.forEach(
      (definition) => {
        const content:
          NodeUsageContent = {
            summary:
              definition.summary,
            examples: [
              ...definition.examples,
            ],
          };

        definition.keys.forEach(
          (key) => {
            index.set(
              normalizeKey(key),
              content,
            );
          },
        );
      },
    );

    return index;
  })();

export const resolveNodeUsageContent = (
  nodeId: string,
  title: string,
  description: string,
): NodeUsageContent => {
  const candidates = [
    nodeId,
    title,
  ];

  for (const candidate of candidates) {
    const content =
      CONTENT_INDEX.get(
        normalizeKey(candidate),
      );

    if (content) {
      return content;
    }
  }

  const safeTitle =
    title.trim() ||
    "este módulo";

  return {
    summary:
      description.trim() ||
      `${safeTitle} integra a estrutura da plataforma INNA.`,

    examples: [
      `📊 Monitorar informações de ${safeTitle}`,
      "🚨 Identificar eventos importantes",
      "📋 Consultar detalhes e indicadores",
    ],
  };
};
