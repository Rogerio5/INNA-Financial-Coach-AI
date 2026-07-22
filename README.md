# INNA Financial Coach AI

A **INNA Financial Coach AI** é uma aplicação inteligente de educação financeira que ajuda pessoas a entenderem sua situação financeira, receberem um diagnóstico personalizado e seguirem um plano de ação simples de 30 dias com apoio de IA Generativa.

Educadora Financeira com IA Generativa, arquitetura multiagente, RAG, memória, FastAPI, Streamlit, PostgreSQL, Neon, Render e observabilidade profissional.

Diagnóstico financeiro • Plano de ação • Histórico • Relatórios • Telegram • RAG híbrido • LangGraph • Prometheus • Grafana

---

## Sumário

- [Visão geral](#visão-geral)
- [Demonstração online](#demonstração-online)
- [Problema](#problema)
- [Solução](#solução)
- [Diferenciais](#diferenciais)
- [Status atual](#status-atual)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Arquitetura multiagente](#arquitetura-multiagente)
- [RAG, memória e Context Engineering](#rag-memória-e-context-engineering)
- [Tool Calling e persistência](#tool-calling-e-persistência)
- [Telegram multilíngue](#telegram-multilíngue)
- [Observabilidade](#observabilidade)
- [Banco de dados](#banco-de-dados)
- [Dashboard analítico](#dashboard-analítico)
- [API](#api)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como navegar pelo projeto](#como-navegar-pelo-projeto)
- [Tecnologias](#tecnologias)
- [Instalação local](#instalação-local)
- [Configuração do ambiente](#configuração-do-ambiente)
- [Execução local](#execução-local)
- [Testes](#testes)
- [Deploy](#deploy)
- [Documentação técnica](#documentação-técnica)
- [Segurança e limitações](#segurança-e-limitações)
- [Evidências visuais](#evidências-visuais)
- [Roadmap](#roadmap)
- [Panorama de evolução](#panorama-de-evolução)
- [Desenvolvedores](#desenvolvedores)

---

# Visão geral

A **INNA Financial Coach AI** é uma plataforma inteligente de educação, diagnóstico e acompanhamento financeiro.

A aplicação ajuda pessoas a:

- entender sua situação financeira;
- calcular indicadores importantes;
- identificar riscos;
- organizar renda, gastos, dívidas e reserva;
- receber um plano de ação educativo;
- acompanhar sua evolução;
- consultar histórico;
- gerar relatórios;
- conversar com uma IA com memória e contexto;
- receber atendimento por diferentes canais.

O projeto nasceu como evolução da **INNA AI Copilot Multichannel**, com foco em:

- hackathons;
- portfólio profissional;
- validação técnica;
- uso educacional;
- validação com usuários;
- evolução comercial;
- futura transformação em produto SaaS.

A INNA evoluiu de um MVP em Streamlit para uma arquitetura modular e profissional com:

- Streamlit;
- FastAPI;
- Google Gemini;
- LangGraph;
- agentes especializados;
- RAG híbrido;
- memória financeira;
- resumo conversacional incremental;
- Tool Calling formal;
- PostgreSQL e Neon;
- pgvector;
- Telegram;
- PDF;
- e-mail;
- dashboards;
- Prometheus;
- Grafana;
- alertas;
- auditoria;
- testes automatizados.

> A INNA oferece educação financeira. Ela não substitui consultoria financeira profissional e não recomenda compra ou venda de ativos.

---

# Demonstração online

A versão pública utiliza **Render** para os serviços da aplicação e **Neon PostgreSQL** como banco de dados em nuvem.

## Links de produção

| Recurso | Link |
|---|---|
| App principal — Streamlit | https://inna-app-streamlit.onrender.com |
| API e Swagger — FastAPI | https://inna-api.onrender.com/docs |
| Health Check | https://inna-api.onrender.com/health |
| Dashboard analítico | https://inna-dashboard-streamlit.onrender.com |
| Repositório | https://github.com/Rogerio5/INNA-Financial-Coach-AI |

## Fluxo online validado

```text
Usuário
  ↓
Streamlit online — Render
  ↓
FastAPI online — Render
  ↓
LangGraph / Motor financeiro / RAG / Gemini
  ↓
PostgreSQL / Neon / pgvector
  ↓
Histórico /PDF / Feedback / Telegram / Dashboard
```

---

## Status da versão online

- App principal publicado no Render;
- API FastAPI publicada no Render;
- dashboard publicado no Render;
- PostgreSQL configurado no Neon;
- integração com Gemini ativa;
- diagnóstico financeiro funcionando;
- plano de ação gerado por IA;
- histórico individual funcionando;
- relatório PDF funcionando;
- feedback persistido;
- dashboard lendo dados reais;
- Swagger público;
- health check validado;
- Telegram integrado;
- observabilidade operacional;
- RAG e memória integrados ao núcleo agentic.

---

## Problema

Muitas pessoas não sabem por onde começar a organizar sua vida financeira.

Dúvidas comuns:

- Estou gastando mais do que ganho?
- Minhas dívidas estão perigosas?
- Quanto consigo guardar por mês?
- Minha reserva é suficiente?
- Qual deve ser meu primeiro passo?
- Como criar um plano simples?
- Como acompanhar minha evolução?
- Como manter contexto entre diferentes conversas?
- Como obter orientação educativa sem receber recomendações financeiras indevidas?

---

## Solução

A INNA recebe informações financeiras básicas, calcula indicadores de forma determinística e utiliza IA Generativa para produzir orientações educativas.

A aplicação entrega:

- diagnóstico financeiro;
- score de 0 a 100;
- nível de risco;
- saldo mensal estimado;
- comprometimento da renda;
- estimativa de reserva;
- plano de ação;
- histórico individual;
- memória conversacional;
- relatório PDF;
- respostas contextualizadas por RAG;
- feedback;
- exportação CSV;
- dashboard;
- API para integrações;
- atendimento via Telegram;
- alertas e observabilidade.

---

## Diferenciais

A INNA não é apenas um chatbot.

Ela combina:

- regras financeiras determinísticas;
- IA Generativa;
- arquitetura multiagente;
- Context Engineering;
- RAG híbrido;
- memória por usuário;
- resumo incremental;
- Tool Calling;
- banco relacional;
- busca vetorial;
- histórico;
- relatórios;
- canais múltiplos;
- observabilidade;
- segurança financeira;
- testes e auditorias.

O sistema:

- entende a intenção;
- monta o contexto;
- seleciona o agente;
- executa ferramentas formais;
- usa memória e RAG;
- gera a resposta;
- atualiza o resumo da conversa;
- persiste os dados;
- registra rastreabilidade e métricas.

---

## Status atual
```
Panorama por semana
Semana	Área	Situação
Semana 1	LangGraph e núcleo agentic	✅ 100%
Semana 2	RAG, memória e Context Engineering	✅ 100%
Semana 3	Supervisor e arquitetura multiagente	✅ 100%
Semana 4	Tool Calling e persistência	✅ 100%
Semana 5	Confiabilidade e observabilidade	✅ 100%
Semana 6	Produção, integração e entrega	🟡 Em evolução
```

Validação automatizada mais recente
```
2028 passed
1 skipped
0 failed
```
Regressões específicas também foram executadas para:

- memória;
- RAG;
- contexto;
- agentes;
- supervisor;
- ferramentas;
- persistência;
- topologia;
- Telegram;
- observabilidade.

---

## Funcionalidades

# Diagnóstico financeiro
- formulário financeiro;
- cálculo de renda;
- gastos fixos;
- gastos variáveis;
- dívidas;
- reserva;
- saldo mensal;
- comprometimento da renda;
- meses estimados de reserva;
- score financeiro;
- risco baixo, médio ou alto;
- diagnóstico educativo;
- plano de ação;
- fallback seguro;
- modo mock.

# Histórico e acompanhamento
- histórico individual;
- recuperação por usuário;
- evolução do score;
- evolução de saldo;
- persistência por thread;
- retomada de conversas;
- memória financeira;
- resumo incremental;
- substituição de fatos antigos;
- preservação de fatos relevantes.
  
# Relatórios e exportações
- PDF;
- CSV;
- histórico;
- feedback;
- relatórios técnicos;
- auditorias;
- dashboards;
- métricas.

# Canais
- Streamlit;
- FastAPI;
- Telegram;
- e-mail;
- dashboard;
- API preparada para outros frontends.

---

## Arquitetura
Arquitetura de alto nível
```flowchart TD
    U[Usuário] --> Channels[Streamlit / Telegram / API]
    Channels --> API[FastAPI]
    API --> Context[Context Engineering]
    Context --> Supervisor[Supervisor híbrido]
    Supervisor --> Governance[Governança de execução]

    Governance --> Financial[Agente financeiro]
    Governance --> Education[Agente educacional]
    Governance --> RAGAgent[Agente RAG]
    Governance --> Report[Agente de relatório]
    Governance --> Fallback[Agente fallback]

    Financial --> Summary[Resumo incremental]
    Education --> Summary
    RAGAgent --> Summary
    Report --> Summary
    Fallback --> Summary

    Summary --> Tools[Tool Calling]
    Tools --> DB[(PostgreSQL / Neon)]
    Tools --> Vector[(pgvector)]
    Tools --> Gemini[Google Gemini]

    API --> PDF[Relatório PDF]
    API --> Email[E-mail / Resend]
    API --> Dashboard[Dashboard]
    API --> Metrics[Prometheus]
    Metrics --> Grafana[Grafana]
```

---


