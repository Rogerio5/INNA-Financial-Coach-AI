# INNA Financial Coach AI

## 💰 Educadora Financeira com IA Generativa, FastAPI, PostgreSQL e Dashboard Analítico

A **INNA Financial Coach AI** é uma aplicação inteligente de educação financeira que ajuda pessoas a entenderem sua situação financeira, receberem um diagnóstico personalizado e seguirem um plano de ação simples de 30 dias com apoio de IA Generativa.

O projeto nasceu como evolução da **Inna AI Copilot Multichannel**, com foco em hackathons, validação com usuários, portfólio profissional e possível monetização.

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

---

## 💡 Solução

A INNA recebe informações financeiras básicas do usuário, calcula indicadores importantes e usa IA Generativa para gerar um plano de ação personalizado.

A aplicação entrega:

* Diagnóstico financeiro educativo
* Score financeiro de 0 a 100
* Classificação de risco financeiro
* Plano de ação de 30 dias com Google Gemini
* Registro de feedback do usuário
* Persistência em PostgreSQL
* Dashboard analítico com dados reais
* API FastAPI pronta para integrações futuras

---

## 🚀 Funcionalidades do MVP

* Formulário de diagnóstico financeiro com Streamlit
* Streamlit consumindo a FastAPI
* API FastAPI com endpoints de diagnóstico, feedback e consulta
* Cálculo de renda, gastos, dívidas, reserva e saldo estimado
* Cálculo de comprometimento da renda
* Cálculo de meses estimados de reserva
* Score financeiro de 0 a 100
* Classificação de risco: Baixo, Medio ou Alto
* Plano de ação de 30 dias gerado com Google Gemini
* Modo Mock para testes sem consumir API de IA
* Persistência de diagnósticos em PostgreSQL
* Persistência de feedbacks em PostgreSQL
* Dashboard analítico conectado ao PostgreSQL
* Testes automatizados com pytest

---

## 🧠 Diferencial

A proposta não é ser apenas um chatbot.

A INNA funciona como uma **plataforma de diagnóstico e acompanhamento financeiro**, combinando:

* IA Generativa
* Regras financeiras simples
* API backend
* Banco de dados relacional
* Feedback de usuários
* Dashboard de métricas
* Linguagem acessível
* Segurança contra recomendação indevida de investimentos
* Possibilidade futura de integração com Telegram, Gmail, WhatsApp, n8n, React ou mobile

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
PostgreSQL
↓
Dashboard Analítico
```

### Fluxo principal

1. O usuário preenche o formulário financeiro no Streamlit.
2. O Streamlit envia os dados para a FastAPI.
3. A FastAPI calcula o diagnóstico financeiro.
4. A FastAPI chama o Gemini para gerar o plano de ação de 30 dias.
5. A FastAPI salva o diagnóstico no PostgreSQL.
6. O usuário envia feedback pela interface.
7. O Streamlit envia o feedback para a FastAPI.
8. A FastAPI salva o feedback no PostgreSQL.
9. O dashboard lê os dados reais do banco e exibe métricas.

### Benefício da arquitetura

Essa separação deixa o projeto mais próximo de uma aplicação real, permitindo que outros canais consumam a mesma API no futuro, como:

* Frontend React
* n8n
* Telegram
* WhatsApp
* Gmail
* Aplicativo mobile
* Dashboard externo

---

## 🧰 Tecnologias Utilizadas

### Backend e IA

* Python
* FastAPI
* Google Gemini API
* SQLAlchemy
* PostgreSQL
* Pydantic
* python-dotenv
* Uvicorn
* Requests

### Interface e Analytics

* Streamlit
* Pandas
* Dashboard com gráficos e métricas
* CSV como log complementar

### Qualidade

* Pytest
* Estrutura modular
* Separação entre app, API, engine financeiro, banco, feedback e dashboard

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
│   ├── prompts.py
│   └── repository.py
├── tests/
│   ├── conftest.py
│   └── test_financial_engine.py
├── .env.example
├── .gitignore
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
FastAPI salva diagnóstico no PostgreSQL
↓
Usuário envia feedback pelo Streamlit
↓
Streamlit envia feedback para a FastAPI
↓
FastAPI salva feedback no PostgreSQL
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

O projeto utiliza **PostgreSQL local** com SQLAlchemy.

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

O dashboard lê dados diretamente do PostgreSQL e apresenta:

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

---

## 🔌 Endpoints da API

A FastAPI disponibiliza os seguintes endpoints:

```text
GET  /
POST /diagnostico
POST /feedback
GET  /diagnosticos
GET  /feedbacks
```

### `GET /`

Verifica se a API está funcionando.

### `POST /diagnostico`

Gera diagnóstico financeiro, chama o Gemini, salva no PostgreSQL e retorna a resposta completa.

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

Registra feedback do usuário no PostgreSQL.

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

Lista diagnósticos salvos no PostgreSQL.

Exemplo:

```text
http://127.0.0.1:8000/diagnosticos?limit=10
```

### `GET /feedbacks`

Lista feedbacks salvos no PostgreSQL.

Exemplo:

```text
http://127.0.0.1:8000/feedbacks?limit=10
```

---

## ⚙️ Como Rodar o Projeto

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

DATABASE_URL=postgresql://postgres:sua_senha_aqui@localhost:5432/inna_db

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

## ▶️ Rodar API FastAPI

A API precisa ficar rodando para que o Streamlit consiga consumir os endpoints.

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Acesse a documentação automática:

```text
http://127.0.0.1:8000/docs
```

---

## ▶️ Rodar Interface Streamlit

Em outro terminal, com a API já rodando:

```bash
streamlit run src/app.py --server.port 8504
```

Acesse:

```text
http://localhost:8504
```

---

## 📊 Rodar Dashboard

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
2 passed
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

## ✅ Validação Técnica Atual

O projeto já foi validado localmente com:

* Streamlit consumindo FastAPI
* FastAPI gerando diagnóstico financeiro
* FastAPI chamando Gemini real
* FastAPI salvando diagnósticos no PostgreSQL
* FastAPI salvando feedbacks no PostgreSQL
* Dashboard lendo dados reais do PostgreSQL
* Endpoint `POST /diagnostico` funcionando
* Endpoint `POST /feedback` funcionando
* Endpoint `GET /diagnosticos` funcionando
* Endpoint `GET /feedbacks` funcionando
* Testes automatizados passando com pytest

---

## ✅ Status Atual do MVP

* App Streamlit funcionando
* API FastAPI funcionando
* Gemini real integrado
* PostgreSQL validado
* Diagnósticos salvos no banco
* Feedbacks salvos no banco
* Dashboard lendo dados reais
* Streamlit consumindo API
* Testes automatizados passando
* Projeto publicado no GitHub

---

## 🛣️ Roadmap

Próximas evoluções planejadas:

* Autenticação de usuários
* Histórico individual por usuário
* Exportação de relatório em PDF
* Deploy online
* Supabase ou PostgreSQL gerenciado
* Integração com n8n
* Integração com WhatsApp, Telegram ou Gmail
* RAG com base de conhecimento financeira
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

Ela transforma dados financeiros simples em diagnóstico, plano de ação e acompanhamento com IA Generativa, usando uma arquitetura moderna com Streamlit, FastAPI, Gemini, PostgreSQL e dashboard analítico.

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
