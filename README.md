# INNA Financial Coach AI

## 💰 Educadora Financeira com IA Generativa, FastAPI, PostgreSQL, Neon, Render e Dashboard Analítico

A **INNA Financial Coach AI** é uma aplicação inteligente de educação financeira que ajuda pessoas a entenderem sua situação financeira, receberem um diagnóstico personalizado e seguirem um plano de ação simples de 30 dias com apoio de IA Generativa.

O projeto nasceu como evolução da **Inna AI Copilot Multichannel**, com foco em hackathons, validação com usuários, portfólio profissional e possível monetização.

A solução combina **Streamlit**, **FastAPI**, **Google Gemini**, **PostgreSQL/Neon**, **Render**, **PDF**, **histórico individual**, **feedback de usuários** e **dashboard analítico online**.

---

## 🌐 Demo Online

O projeto INNA Financial Coach AI está publicado em ambiente online utilizando **Render** para os serviços da aplicação e **Neon PostgreSQL** como banco de dados em nuvem.

### 🔗 Links de produção

**App principal — Streamlit**

https://inna-app-streamlit.onrender.com

**API / Swagger — FastAPI**

https://inna-api.onrender.com/docs

**Health Check da API**

https://inna-api.onrender.com/health

**Dashboard analítico — Streamlit**

https://inna-dashboard-streamlit.onrender.com

---

## 🚀 Arquitetura em Produção

```text
Usuário
↓
Streamlit App online — Render
↓
FastAPI online — Render
↓
Google Gemini
↓
Neon PostgreSQL
↓
Dashboard analítico online — Render
```

### Fluxo online validado

```text
Streamlit online
↓
FastAPI online
↓
Gemini
↓
Neon PostgreSQL
↓
PDF / Histórico / Feedback / Dashboard
```

---

## ✅ Status da Versão Online

* App principal publicado no Render
* API FastAPI publicada no Render
* Dashboard analítico publicado no Render
* Banco PostgreSQL online configurado no Neon
* Integração com Google Gemini ativa
* Diagnóstico financeiro funcionando online
* Plano de ação de 30 dias gerado por IA
* Histórico individual funcionando online
* Geração de relatório PDF funcionando online
* Feedback dos usuários salvo no banco online
* Dashboard lendo métricas reais do Neon PostgreSQL
* API Swagger pública e funcional
* Health Check online validado

---

## 🧪 Validação em Produção

A versão online foi validada com o fluxo completo:

```text
Streamlit online
↓
FastAPI online
↓
Gemini
↓
Neon PostgreSQL
↓
Dashboard online
```

Testes realizados em produção:

* `GET /health` retornando status online
* `POST /diagnostico` salvando diagnóstico no Neon
* `GET /diagnosticos` listando diagnósticos salvos
* `GET /diagnosticos/usuario/{nome}` buscando histórico individual
* `GET /feedbacks` listando feedbacks enviados
* PDF gerado a partir de diagnóstico salvo
* Dashboard online exibindo indicadores, gráficos, ranking e feedbacks
* Streamlit online consumindo a API online
* FastAPI online conectada ao Neon PostgreSQL

---

## 🎯 Problema

Muitas pessoas não sabem por onde começar a organizar sua vida financeira.

Elas têm dificuldade para responder perguntas como:

* Estou gastando mais do que ganho?
* Minhas dívidas estão perigosas?
* Quanto consigo guardar por mês?
* Tenho reserva suficiente?
* Qual primeiro passo devo tomar?
* Como transformar minha situação financeira em um plano simples?
* Como acompanhar minha evolução financeira ao longo do tempo?

---

## 💡 Solução

A INNA recebe informações financeiras básicas do usuário, calcula indicadores importantes e usa IA Generativa para gerar um plano de ação personalizado.

A aplicação entrega:

* Diagnóstico financeiro educativo
* Score financeiro de 0 a 100
* Classificação de risco financeiro
* Plano de ação de 30 dias com Google Gemini
* Registro de feedback do usuário
* Persistência em PostgreSQL/Neon
* Histórico individual por usuário
* Relatório PDF
* Dashboard analítico com dados reais
* Exportação CSV de dados filtrados
* API FastAPI pronta para integrações futuras

---

## 🚀 Funcionalidades do MVP

* Formulário de diagnóstico financeiro com Streamlit
* Streamlit consumindo a FastAPI
* API FastAPI com endpoints de diagnóstico, feedback, histórico, PDF e consultas
* Cálculo de renda, gastos, dívidas, reserva e saldo estimado
* Cálculo de comprometimento da renda
* Cálculo de meses estimados de reserva
* Score financeiro de 0 a 100
* Classificação de risco: Baixo, Medio ou Alto
* Plano de ação de 30 dias gerado com Google Gemini
* Fallback seguro caso a IA esteja indisponível
* Modo Mock para testes sem consumir API de IA
* Persistência de diagnósticos em PostgreSQL/Neon
* Persistência de feedbacks em PostgreSQL/Neon
* Histórico individual por usuário
* Geração de relatório PDF
* Dashboard analítico conectado ao PostgreSQL/Neon
* Filtro por data no dashboard
* Filtro por mês no dashboard
* Exportação CSV dos dados filtrados
* Health Check da API
* Tratamento amigável de erro quando a API estiver offline
* Testes automatizados com pytest
* Deploy online com Render
* Banco PostgreSQL online com Neon

---

## 🧠 Diferencial

A proposta não é ser apenas um chatbot.

A INNA funciona como uma **plataforma de diagnóstico e acompanhamento financeiro**, combinando:

* IA Generativa
* Regras financeiras simples
* API backend
* Banco de dados relacional
* Histórico financeiro
* Relatório PDF
* Feedback de usuários
* Dashboard de métricas
* Linguagem acessível
* Segurança contra recomendação indevida de investimentos
* Possibilidade futura de integração com Telegram, Gmail, WhatsApp, n8n, React ou mobile

O diferencial principal é que a INNA não apenas responde perguntas. Ela calcula indicadores, classifica risco, gera plano personalizado, salva histórico e permite acompanhar evolução por meio de dashboard.

---

## 🏗️ Arquitetura Atual

A arquitetura atual foi evoluída para separar interface, API, inteligência artificial, persistência e analytics.

```text
Usuário
↓
Streamlit
↓
FastAPI
↓
Google Gemini
↓
PostgreSQL / Neon
↓
Dashboard Analítico
```

### Fluxo principal

1. O usuário preenche o formulário financeiro no Streamlit.
2. O Streamlit envia os dados para a FastAPI.
3. A FastAPI calcula o diagnóstico financeiro.
4. A FastAPI chama o Gemini para gerar o plano de ação de 30 dias.
5. A FastAPI salva o diagnóstico no PostgreSQL/Neon.
6. O usuário pode baixar um relatório PDF.
7. O usuário pode consultar histórico individual.
8. O usuário envia feedback pela interface.
9. O Streamlit envia o feedback para a FastAPI.
10. A FastAPI salva o feedback no PostgreSQL/Neon.
11. O dashboard lê os dados reais do banco e exibe métricas.

### Benefício da arquitetura

Essa separação deixa o projeto mais próximo de uma aplicação real, permitindo que outros canais consumam a mesma API no futuro, como:

* Frontend React
* n8n
* Telegram
* WhatsApp
* Gmail
* Aplicativo mobile
* Dashboard externo
* Integrações corporativas

---

## 🧰 Tecnologias Utilizadas

### Backend e IA

* Python
* FastAPI
* Google Gemini API
* SQLAlchemy
* PostgreSQL
* Neon PostgreSQL
* Pydantic
* python-dotenv
* Uvicorn
* Requests

### Interface e Analytics

* Streamlit
* Pandas
* Dashboard com gráficos e métricas
* Exportação CSV
* ReportLab para PDF

### Deploy e Cloud

* Render
* Neon PostgreSQL
* GitHub

### Qualidade

* Pytest
* Estrutura modular
* Separação entre app, API, engine financeiro, banco, feedback, PDF e dashboard
* Health Check
* Tratamento de erro para API offline

---

## 📂 Estrutura do Projeto

```text
inna-financial-coach-ai/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── assets/
├── data/
│   ├── interacoes.csv
│   └── feedbacks.csv
├── docs/
│   ├── arquitetura.md
│   ├── pitch.md
│   └── roadmap.md
├── src/
│   ├── __init__.py
│   ├── api_client.py
│   ├── app.py
│   ├── config.py
│   ├── dashboard.py
│   ├── database.py
│   ├── feedback.py
│   ├── financial_engine.py
│   ├── gemini_client.py
│   ├── logger.py
│   ├── models.py
│   ├── pdf_report.py
│   ├── prompts.py
│   └── repository.py
├── tests/
│   ├── conftest.py
│   ├── test_api_health.py
│   └── test_financial_engine.py
├── .env.example
├── .gitignore
├── .python-version
├── runtime.txt
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 🔄 Fluxo da Aplicação

```text
Usuário preenche formulário financeiro
↓
Streamlit envia os dados para a FastAPI
↓
FastAPI calcula indicadores financeiros
↓
FastAPI gera score e nível de risco
↓
FastAPI chama o Google Gemini
↓
Gemini cria plano de ação de 30 dias
↓
FastAPI salva diagnóstico no PostgreSQL/Neon
↓
Usuário baixa relatório PDF
↓
Usuário consulta histórico individual
↓
Usuário envia feedback pelo Streamlit
↓
Streamlit envia feedback para a FastAPI
↓
FastAPI salva feedback no PostgreSQL/Neon
↓
Dashboard lê dados reais do banco
```

---

## 📊 Indicadores Calculados

A INNA calcula automaticamente:

* Saldo estimado mensal
* Percentual de comprometimento da renda
* Meses estimados de reserva
* Score financeiro
* Nível de risco financeiro

Classificação utilizada:

```text
Score >= 75  → Baixo risco
Score >= 50  → Medio risco
Score < 50   → Alto risco
```

---

## 🗄️ Banco de Dados

O projeto utiliza **PostgreSQL** com SQLAlchemy.

Ambientes suportados:

* PostgreSQL local para desenvolvimento
* Neon PostgreSQL para produção online

Tabelas principais:

```text
diagnosticos_financeiros
feedbacks_usuarios
```

### Tabela `diagnosticos_financeiros`

Armazena:

* Nome do usuário
* Renda mensal
* Gastos fixos
* Gastos variáveis
* Dívidas mensais
* Reserva atual
* Objetivo financeiro
* Saldo estimado
* Comprometimento da renda
* Meses estimados de reserva
* Score financeiro
* Nível de risco
* Diagnóstico
* Plano de ação de 30 dias

### Tabela `feedbacks_usuarios`

Armazena:

* Nome do usuário
* Se a resposta foi útil
* Comentário do usuário
* Score financeiro
* Nível de risco

---

## 📈 Dashboard Analítico

O dashboard lê dados diretamente do PostgreSQL configurado no projeto, podendo ser local ou Neon.

Ele apresenta:

* Total de diagnósticos
* Usuários únicos
* Score médio
* Saldo médio estimado
* Taxa de feedback útil
* Distribuição por nível de risco
* Evolução dos scores
* Evolução do saldo estimado
* Ranking de usuários
* Score médio por risco
* Últimos diagnósticos
* Últimos feedbacks
* Comentários recebidos
* Leitura executiva da base
* Filtro por data
* Filtro por mês
* Exportação CSV dos diagnósticos filtrados
* Exportação CSV dos feedbacks filtrados

Dashboard online:

```text
https://inna-dashboard-streamlit.onrender.com
```

---

## 🔌 Endpoints da API

A FastAPI disponibiliza os seguintes endpoints:

```text
GET  /
GET  /health
POST /diagnostico
POST /feedback
GET  /diagnosticos
GET  /feedbacks
GET  /diagnosticos/{diagnostico_id}/relatorio
GET  /diagnosticos/usuario/{nome}
```

### `GET /`

Rota inicial da API.

Exemplo:

```text
https://inna-api.onrender.com
```

### `GET /health`

Verifica se a API está online.

Exemplo:

```text
https://inna-api.onrender.com/health
```

Exemplo de resposta:

```json
{
  "status": "ok",
  "app": "INNA Financial Coach AI",
  "message": "API online e pronta para receber requisições."
}
```

### `POST /diagnostico`

Gera diagnóstico financeiro, chama o Gemini, salva no PostgreSQL/Neon e retorna a resposta completa.

Exemplo de payload:

```json
{
  "nome": "Ronaldo",
  "renda_mensal": 3000,
  "gastos_fixos": 1400,
  "gastos_variaveis": 700,
  "dividas_mensais": 300,
  "reserva_atual": 500,
  "objetivo": "Organizar minha vida financeira"
}
```

Exemplo de resposta:

```json
{
  "id": 1,
  "nome": "Ronaldo",
  "saldo_estimado": 600,
  "comprometimento_renda_percentual": 80,
  "meses_reserva_estimados": 0.21,
  "score_financeiro": 60,
  "nivel_risco": "Medio",
  "diagnostico": "Seu saldo estimado mensal é de R$ 600.00...",
  "plano_30_dias": "Plano personalizado gerado pela IA..."
}
```

### `POST /feedback`

Registra feedback do usuário no PostgreSQL/Neon.

Exemplo de payload:

```json
{
  "nome": "Ronaldo",
  "util": "Sim",
  "comentario": "Gostei da orientação",
  "score_financeiro": 60,
  "nivel_risco": "Medio"
}
```

Exemplo de resposta:

```json
{
  "status": "success",
  "message": "Feedback registrado com sucesso no PostgreSQL."
}
```

### `GET /diagnosticos`

Lista diagnósticos salvos no PostgreSQL/Neon.

Exemplo local:

```text
http://127.0.0.1:8000/diagnosticos?limit=10
```

Exemplo online:

```text
https://inna-api.onrender.com/diagnosticos?limit=10
```

### `GET /feedbacks`

Lista feedbacks salvos no PostgreSQL/Neon.

Exemplo local:

```text
http://127.0.0.1:8000/feedbacks?limit=10
```

Exemplo online:

```text
https://inna-api.onrender.com/feedbacks?limit=10
```

### `GET /diagnosticos/{diagnostico_id}/relatorio`

Gera relatório PDF de um diagnóstico salvo.

Exemplo:

```text
https://inna-api.onrender.com/diagnosticos/1/relatorio
```

### `GET /diagnosticos/usuario/{nome}`

Busca o histórico individual de diagnósticos por nome.

Exemplo:

```text
https://inna-api.onrender.com/diagnosticos/usuario/Ronaldo?limit=10
```

---

## ⚙️ Como Rodar o Projeto Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/Rogerio5/INNA-Financial-Coach-AI.git
cd INNA-Financial-Coach-AI
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual no Windows

```bash
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuração do `.env`

Crie um arquivo `.env` com base no `.env.example`.

Exemplo:

```env
APP_NAME=inna-financial-coach-ai
APP_VERSION=1.0.0
APP_ENV=development

INNA_APP_NAME=INNA Financial Coach AI
INNA_NOME=INNA
INNA_TITULO=Educadora Financeira com IA Generativa

INNA_MOCK_MODE=false

GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash-lite

API_HOST=127.0.0.1
API_PORT=8000
API_BASE_URL=http://127.0.0.1:8000

STREAMLIT_HOST=localhost
STREAMLIT_PORT=8504
STREAMLIT_BASE_URL=http://localhost:8504

# Banco local
DATABASE_URL=postgresql://postgres:sua_senha_aqui@localhost:5432/inna_db

# Banco Neon em produção
# DATABASE_URL=postgresql://neondb_owner:sua_senha@seu-host-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

DATA_DIR=data
INTERACTIONS_LOG_FILE=data/interacoes.csv
FEEDBACK_FILE=data/feedbacks.csv

USE_FAKE_DATA=true
ALLOW_REAL_BANK_DATA=false

LOG_LEVEL=INFO
ENABLE_INTERACTION_LOGS=true
ENABLE_FEEDBACK_LOGS=true
```

Atenção: nunca envie o arquivo `.env` para o GitHub.

---

## ▶️ Rodar API FastAPI Localmente

A API precisa ficar rodando para que o Streamlit consiga consumir os endpoints.

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Acesse a documentação automática:

```text
http://127.0.0.1:8000/docs
```

Health Check local:

```text
http://127.0.0.1:8000/health
```

---

## ▶️ Rodar Interface Streamlit Localmente

Em outro terminal, com a API já rodando:

```bash
streamlit run src/app.py --server.port 8504
```

Acesse:

```text
http://localhost:8504
```

---

## 📊 Rodar Dashboard Localmente

```bash
streamlit run src/dashboard.py --server.port 8505
```

Acesse:

```text
http://localhost:8505
```

---

## 🧪 Rodar Testes

```bash
pytest
```

Resultado validado:

```text
3 passed
```

---

## 🤖 Modo Mock e Gemini Real

O projeto possui dois modos de execução.

### Mock Mode

Usado para testes rápidos sem consumir API de IA:

```env
INNA_MOCK_MODE=true
```

### Gemini Real

Usado para gerar planos personalizados com IA Generativa:

```env
INNA_MOCK_MODE=false
GEMINI_API_KEY=sua_chave_real
```

---

## ☁️ Deploy Online

O projeto está publicado usando:

* Render para FastAPI
* Render para Streamlit principal
* Render para Dashboard
* Neon PostgreSQL para banco online

### Serviços publicados

```text
inna-api
inna-app-streamlit
inna-dashboard-streamlit
```

### Comandos de produção

FastAPI:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Streamlit principal:

```bash
streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0
```

Dashboard:

```bash
streamlit run src/dashboard.py --server.port $PORT --server.address 0.0.0.0
```

### Variáveis de ambiente principais

Serviço `inna-api`:

```env
APP_ENV=production
INNA_MOCK_MODE=false
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash-lite
DATABASE_URL=sua_url_neon
API_BASE_URL=https://inna-api.onrender.com
PYTHON_VERSION=3.12.1
```

Serviço `inna-app-streamlit`:

```env
APP_ENV=production
API_BASE_URL=https://inna-api.onrender.com
INNA_MOCK_MODE=false
PYTHON_VERSION=3.12.1
```

Serviço `inna-dashboard-streamlit`:

```env
APP_ENV=production
DATABASE_URL=sua_url_neon
PYTHON_VERSION=3.12.1
```

---

## ✅ Validação Técnica Atual

O projeto já foi validado localmente e online com:

* Streamlit consumindo FastAPI
* FastAPI gerando diagnóstico financeiro
* FastAPI chamando Gemini real
* FastAPI salvando diagnósticos no PostgreSQL/Neon
* FastAPI salvando feedbacks no PostgreSQL/Neon
* Dashboard lendo dados reais do PostgreSQL/Neon
* Endpoint `GET /health` funcionando
* Endpoint `POST /diagnostico` funcionando
* Endpoint `POST /feedback` funcionando
* Endpoint `GET /diagnosticos` funcionando
* Endpoint `GET /feedbacks` funcionando
* Endpoint `GET /diagnosticos/usuario/{nome}` funcionando
* Endpoint `GET /diagnosticos/{id}/relatorio` funcionando
* Relatório PDF funcionando online
* Histórico individual funcionando online
* Feedback funcionando online
* Testes automatizados passando com pytest

---

## ✅ Status Atual do MVP

* App Streamlit funcionando localmente e online
* API FastAPI funcionando localmente e online
* Dashboard funcionando localmente e online
* Gemini real integrado
* Neon PostgreSQL validado
* Diagnósticos salvos no banco online
* Feedbacks salvos no banco online
* Dashboard lendo dados reais online
* Streamlit consumindo API online
* Testes automatizados passando
* Projeto publicado no GitHub
* Deploy online concluído no Render

---

## 🖼️ Evidências Visuais

### App principal online
![App online](docs/prints/app-online.png)

### Diagnóstico gerado
![Diagnóstico online](docs/prints/diagnostico-online.png)

### Relatório PDF gerado
![PDF online](docs/prints/pdf-online.png)

### Histórico individual funcionando
![Histórico online](docs/prints/historico-online.png)

### API Swagger
![Swagger online](docs/prints/swagger-online.png)

### Dashboard analítico
![Dashboard online](docs/prints/dashboard-online.png)

### Dashboard com dados, feedbacks e leitura executiva
![Dashboard dados online](docs/prints/dashboard-dados-online.png)

### Serviços no Render
![Serviços no Render](docs/prints/render-servicos.png)

### Banco Neon PostgreSQL
![Neon dados](docs/prints/neon-dados.png)

---

## 🛣️ Roadmap

Próximas evoluções planejadas:

* Melhorar página inicial e experiência visual
* Criar documentação com prints do sistema online
* Criar vídeo demo curto
* Autenticação de usuários
* Área individual por usuário
* Evolução comparativa do score financeiro
* RAG com base de conhecimento financeira
* Embeddings e busca vetorial com pgvector no Neon
* Integração com n8n
* Integração com WhatsApp, Telegram ou Gmail
* Agentes especializados com LangChain ou CrewAI
* Alertas automáticos e recomendações recorrentes
* Métricas de produto e validação com usuários reais
* Versão SaaS simples com plano gratuito e plano pago

---

## 🔐 Segurança e Limitações

A INNA atua como educadora financeira.

Ela não:

* recomenda compra ou venda de ativos;
* promete rentabilidade;
* substitui consultor financeiro certificado;
* acessa dados bancários reais;
* solicita senhas;
* toma decisões pelo usuário.

O projeto utiliza dados fictícios para demonstração, aprendizado e validação técnica.

---

## 🏁 Conclusão

A **INNA Financial Coach AI** é um MVP pensado para hackathons, portfólio profissional, validação com usuários e evolução comercial.

Ela transforma dados financeiros simples em diagnóstico, plano de ação, histórico, relatório PDF e acompanhamento com IA Generativa, usando uma arquitetura moderna com Streamlit, FastAPI, Gemini, Neon PostgreSQL, Render e dashboard analítico.

---

## 👨‍💻 Desenvolvedores / Developers

* [Rogerio](https://github.com/Rogerio5)
* [Ronaldo](https://github.com/Ronaldo94-GITHUB)

Áreas relacionadas:

* Engenharia de Software
* IA Generativa
* Python
* Dados
* Automação
* Cloud
* APIs
* PostgreSQL
* Deploy

## Bot Telegram Multilíngue

A INNA também funciona pelo Telegram, integrada à FastAPI online por meio de webhook.  
O bot conduz o usuário por perguntas simples, identifica o idioma escolhido e formata os valores conforme a moeda associada ao país/idioma.

### Funcionalidades do Telegram

- Atendimento guiado por perguntas simples
- Seleção de idioma no início da conversa
- Formatação de moedas por idioma/país
- Diagnóstico financeiro salvo na base online
- Resposta resumida no Telegram
- Plano completo disponível pelo app web, dashboard e relatório PDF
- Comandos `/start`, `/idioma`, `/help` e `/cancelar`
- Descrição multilíngue configurada no perfil do bot via Telegram Bot API

### Idiomas e moedas disponíveis

- Português Brasil — BRL / R$
- English US — USD / US$
- English UK — GBP / £
- Español — EUR / €
- Deutsch — EUR / €
- Français — EUR / €
- Italiano — EUR / €
- Русский — RUB / ₽
- العربية — SAR
- Română — RON
- Українська — UAH / ₴
- Schweiz — CHF

### Arquitetura do Telegram

Telegram  
↓  
Webhook FastAPI online  
↓  
https://inna-api.onrender.com/telegram/webhook  
↓  
Motor financeiro + Gemini  
↓  
Neon PostgreSQL  
↓  
Dashboard / App Web / PDF

---

## 🚀 Versão atual do projeto

A versão atual da **INNA Financial Coach AI** consolida a aplicação como uma solução educativa, multilíngue e orientada por dados reais.

### Funcionalidades implementadas

- Dashboard administrativo multilíngue.
- RAG financeiro para respostas contextualizadas.
- Eventos reais registrados no PostgreSQL/Neon.
- Segurança educativa sobre Pix, fraude e golpes financeiros.
- Geração de diagnóstico financeiro personalizado.
- Exportação de dados em CSV.
- Observabilidade, métricas e validação do agente.
- Suporte a múltiplos canais e idiomas.
- Preservação dos dados reais salvos no banco, separando interface traduzida de informações originais do usuário.

### Idiomas principais validados no dashboard

- Português.
- Inglês.
- Árabe.
- Russo.

### Objetivo da versão

Esta versão tem como objetivo demonstrar que a INNA não é apenas um protótipo visual, mas uma aplicação com:

- uso real de banco de dados;
- rastreabilidade de eventos;
- camada de IA com RAG;
- preocupação com segurança financeira;
- painel administrativo;
- suporte multilíngue;
- base preparada para validação com usuários reais.

