# INNA Financial Coach AI

## 💰 Educadora Financeira com IA Generativa, PostgreSQL e Dashboard Analítico

A **INNA Financial Coach AI** é uma aplicação inteligente de educação financeira que ajuda pessoas a entenderem sua situação financeira, receberem um diagnóstico personalizado e seguirem um plano de ação simples de 30 dias com apoio de IA Generativa.

O projeto nasceu como evolução da **Inna AI Copilot Multichannel**, com foco em hackathons, validação com usuários, portfólio profissional e possível monetização.

---

## 🎯 Problema

Muitas pessoas não sabem por onde começar a organizar sua vida financeira.

Elas têm dificuldade para responder perguntas como:

- Estou gastando mais do que ganho?
- Minhas dívidas estão perigosas?
- Quanto consigo guardar por mês?
- Tenho reserva suficiente?
- Qual primeiro passo devo tomar?
- Como transformar minha situação em um plano simples?

---

## 💡 Solução

A INNA recebe informações financeiras básicas do usuário, calcula indicadores importantes e usa IA Generativa para gerar um plano de ação personalizado.

A aplicação entrega:

- Diagnóstico financeiro educativo
- Score financeiro de 0 a 100
- Classificação de risco financeiro
- Plano de ação de 30 dias com Gemini
- Registro de feedback do usuário
- Persistência em PostgreSQL
- Dashboard analítico com dados reais

---

## 🚀 Funcionalidades do MVP

- Formulário de diagnóstico financeiro com Streamlit
- Cálculo de renda, gastos, dívidas, reserva e saldo estimado
- Cálculo de comprometimento da renda
- Cálculo de meses estimados de reserva
- Score financeiro de 0 a 100
- Classificação de risco: Baixo, Medio ou Alto
- Plano de ação de 30 dias gerado com Google Gemini
- Modo Mock para testes sem consumir API de IA
- API FastAPI com endpoint `/diagnostico`
- Persistência em PostgreSQL
- Registro de diagnósticos financeiros no banco
- Registro de feedbacks dos usuários no banco
- Dashboard analítico conectado ao PostgreSQL
- Testes automatizados com pytest

---

## 🧠 Diferencial

A proposta não é ser apenas um chatbot.

A INNA funciona como uma **plataforma de diagnóstico e acompanhamento financeiro**, combinando:

- IA Generativa
- Regras financeiras simples
- Banco de dados relacional
- Feedback de usuários
- Dashboard de métricas
- Linguagem acessível
- Segurança contra recomendação indevida de investimentos
- Possibilidade futura de integração com Telegram, Gmail, WhatsApp e n8n

---

## 🧰 Tecnologias Utilizadas

### Backend e IA

- Python
- FastAPI
- Google Gemini API
- SQLAlchemy
- PostgreSQL
- Pydantic
- python-dotenv
- Uvicorn

### Interface e Analytics

- Streamlit
- Pandas
- Dashboard com gráficos e métricas
- CSV como log complementar

### Qualidade

- Pytest
- Estrutura modular
- Separação entre app, API, engine financeiro, banco, feedback e dashboard

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
├── README.md
└── requirements.txt
```

---

### 🔄 Fluxo da Aplicação

```
Usuário preenche formulário financeiro
↓
Engine financeira calcula indicadores
↓
Sistema gera score e nível de risco
↓
Gemini cria plano de ação de 30 dias
↓
Diagnóstico é salvo no PostgreSQL
↓
Usuário envia feedback
↓
Feedback é salvo no PostgreSQL
↓
Dashboard lê os dados reais do banco
```

---

## 📊 Indicadores Calculados

A INNA calcula automaticamente:

- Saldo estimado mensal
- Percentual de comprometimento da renda
- Meses estimados de reserva
- Score financeiro
- Nível de risco financeiro

Classificação utilizada:
```
Score >= 75  → Baixo risco
Score >= 50  → Medio risco
Score < 50   → Alto risco
```

---

## 🗄️ Banco de Dados

O projeto utiliza PostgreSQL local com SQLAlchemy.

Tabelas principais:
```
diagnosticos_financeiros
feedbacks_usuarios
```
Tabela diagnosticos_financeiros

Armazena:

- Nome do usuário
- Renda mensal
- Gastos fixos
- Gastos variáveis
- Dívidas mensais
- Reserva atual
- Objetivo financeiro
- Saldo estimado
- Comprometimento da renda
- Meses estimados de reserva
- Score financeiro
- Nível de risco
- Diagnóstico
- Plano de ação de 30 dias


Tabela feedbacks_usuarios

Armazena:

- Nome do usuário
- Se a resposta foi útil
- Comentário do usuário
- Score financeiro
- Nível de risco

---

## 📈 Dashboard Analítico

O dashboard lê dados diretamente do PostgreSQL e apresenta:

- Total de diagnósticos
- Usuários únicos
- Score médio
- Saldo médio estimado
- Taxa de feedback útil
- Distribuição por nível de risco
- Evolução dos scores
- Evolução do saldo estimado
- Ranking de usuários
- Score médio por risco
- Últimos diagnósticos
- Últimos feedbacks
- Comentários recebidos
- Leitura executiva da base

---

## ⚙️ Como Rodar o Projeto

1. Clone o repositório
```
git clone https://github.com/SEU_USUARIO/inna-financial-coach-ai.git
cd inna-financial-coach-ai
```

2. Crie o ambiente virtual
```
python -m venv .venv
```

3. Ative o ambiente virtual no Windows
```
.\.venv\Scripts\Activate.ps1
```

4. Instale as dependências
```
pip install -r requirements.txt
```

---

## 🔐 Configuração do .env

Crie um arquivo .env com base no .env.example.

Exemplo:
```python
APP_NAME=inna-financial-coach-ai
APP_VERSION=1.0.0
APP_ENV=development

INNA_APP_NAME=INNA Financial Coach AI
INNA_NOME=INNA
INNA_TITULO=Educadora Financeira com IA Generativa

INNA_MOCK_MODE=false

GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash-lite

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
Atenção: nunca envie o arquivo .env para o GitHub.

---

## ▶️ Rodar Interface Streamlit
```
streamlit run src/app.py --server.port 8504
```

Acesse:
```
http://localhost:8504
```

---

## 📊 Rodar Dashboard
```
streamlit run src/dashboard.py --server.port 8505
```

Acesse:
```
http://localhost:8505
```

--- 

## 🚀 Rodar API FastAPI
```
python -m uvicorn api.main:app --reload --port 8000
```
Acesse a documentação automática:
```
http://127.0.0.1:8000/docs
```

---

## 🔌 Endpoint Principal

POST /diagnostico

Exemplo de payload:
```bash
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
```bash
{
  "saldo_estimado": 600,
  "comprometimento_renda_percentual": 80,
  "meses_reserva_estimados": 0.21,
  "score_financeiro": 60,
  "nivel_risco": "Medio",
  "diagnostico": "Seu saldo estimado mensal é de R$ 600.00...",
  "plano_30_dias": "Plano personalizado gerado pela IA..."
}
```

---

## 🧪 Rodar Testes
```
pytest
```
Resultado validado:
```
2 passed
```

---

## 🤖 Modo Mock e Gemini Real

O projeto possui dois modos de execução.

Mock Mode

Usado para testes rápidos sem consumir API de IA:
```
INNA_MOCK_MODE=true
```

Gemini Real

Usado para gerar planos personalizados com IA Generativa:
```
INNA_MOCK_MODE=false
GEMINI_API_KEY=sua_chave_real
```

---

## ✅ Status Atual do MVP

- App Streamlit funcionando
- API FastAPI funcionando
- Gemini real integrado
- PostgreSQL validado
- Diagnósticos salvos no banco
- Feedbacks salvos no banco
- Dashboard lendo dados reais
- Testes automatizados passando

---

## 🛣️ Roadmap

Próximas evoluções planejadas:

- Autenticação de usuários
- Histórico individual por usuário
- Exportação de relatório em PDF
- Integração com WhatsApp, Telegram ou Gmail via n8n
- Deploy em nuvem
- Supabase ou PostgreSQL gerenciado
- RAG com base de conhecimento financeira
- Agentes especializados com LangChain ou CrewAI
- Alertas automáticos e recomendações recorrentes
- Métricas de produto e validação com usuários reais

---

## 🔐 Segurança e Limitações

A INNA atua como educadora financeira.

Ela não:

- recomenda compra ou venda de ativos;
- promete rentabilidade;
- substitui consultor financeiro certificado;
- acessa dados bancários reais;
- solicita senhas;
- toma decisões pelo usuário.

---

## 👨‍💻 Desenvolvedor / Developer

- [Rogerio](https://github.com/Rogerio5)
- [Ronaldo](https://github.com/Ronaldo94-GITHUB)

- Engenharia de Software
- IA Generativa
- Python
- Dados
- Automação
- Cloud

  '@ | Set-Content -Path .\README.md -Encoding UTF8

```
Depois rode:

```powershell
git add README.md
git commit -m "docs: update README with Gemini PostgreSQL and dashboard"
```

---

## 🏁 Conclusão

A INNA Financial Coach AI é um MVP pensado para hackathons, portfólio profissional, validação com usuários e evolução comercial.

Ela transforma dados financeiros simples em diagnóstico, plano de ação e acompanhamento com IA Generativa.
