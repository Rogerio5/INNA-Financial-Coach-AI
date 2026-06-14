# INNA Financial Coach AI

## 💰 Educadora Financeira com IA Generativa, Diagnóstico Financeiro e Plano de Ação de 30 Dias

A **INNA Financial Coach AI** é uma aplicação inteligente de educação financeira que ajuda pessoas a entenderem sua situação financeira, receberem um diagnóstico personalizado e seguirem um plano de ação simples de 30 dias.

Este projeto nasceu como evolução da **Inna AI Copilot Multichannel**, focando em uma versão mais direta para hackathons, validação com usuários e possível monetização.

---

## 🎯 Problema

Muitas pessoas não sabem por onde começar a organizar sua vida financeira.

Elas têm dificuldade para responder perguntas como:

- Estou gastando mais do que ganho?
- Minhas dívidas estão perigosas?
- Quanto consigo guardar por mês?
- Qual primeiro passo devo tomar?
- Como transformar tudo isso em um plano simples?

---

## 💡 Solução

A INNA recebe informações básicas do usuário, calcula indicadores financeiros e usa IA Generativa para gerar:

- Diagnóstico financeiro educativo
- Score financeiro simples
- Classificação de risco
- Plano de ação de 30 dias
- Recomendações seguras e sem promessa de investimento
- Registro de feedback para melhoria contínua

---

## 🚀 Funcionalidades do MVP

- Formulário de diagnóstico financeiro
- Cálculo de renda, gastos, dívidas e saldo
- Classificação de risco financeiro
- Geração de plano de ação com IA
- Modo Mock para rodar sem chave de API
- API FastAPI com endpoint `/diagnostico`
- Interface Streamlit
- Registro de interações em CSV
- Estrutura preparada para Gemini, PostgreSQL, RAG, n8n e dashboard

---

## 🧠 Diferencial

A proposta não é ser apenas um chatbot.

A INNA funciona como uma **plataforma de diagnóstico e acompanhamento financeiro**, combinando:

- IA Generativa
- Regras financeiras simples
- Métricas de comportamento
- Linguagem acessível
- Segurança contra recomendação indevida de investimentos
- Possibilidade de integração com Telegram, Gmail, WhatsApp e n8n

---

## 🧰 Tecnologias

- Python
- FastAPI
- Streamlit
- Pandas
- Pydantic
- Gemini API
- dotenv
- Uvicorn
- Pytest

---

## 📂 Estrutura

```text
inna-financial-coach-ai/
├── api/
│   ├── main.py
│   └── schemas.py
├── src/
│   ├── app.py
│   ├── config.py
│   ├── financial_engine.py
│   ├── gemini_client.py
│   ├── logger.py
│   └── prompts.py
├── data/
│   └── interacoes.csv
├── docs/
│   ├── pitch.md
│   ├── arquitetura.md
│   └── roadmap.md
├── assets/
├── tests/
│   └── test_financial_engine.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/inna-financial-coach-ai.git
cd inna-financial-coach-ai
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure o ambiente

```bash
copy .env.example .env
```

Preencha sua chave Gemini se quiser usar IA real.

Para rodar sem chave, deixe:

```env
INNA_MOCK_MODE=true
```

---

## ▶️ Rodar API

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Acesse:

```text
http://127.0.0.1:8000/docs
```

---

## ▶️ Rodar Interface Streamlit

Em outro terminal:

```bash
streamlit run src/app.py --server.port 8501
```

Acesse:

```text
http://localhost:8501
```

---

## 🧪 Rodar Testes

```bash
pytest
```

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

## 📈 Próximas Evoluções

- Deploy online
- PostgreSQL/Supabase
- Login simples por usuário
- Histórico financeiro
- Dashboard de métricas
- Integração com n8n
- Telegram/Gmail
- RAG com base financeira
- Relatório PDF
- Plano pago simples

---

## 🏁 Conclusão

A INNA Financial Coach AI é um MVP pensado para hackathons, portfólio e validação comercial rápida.

Ela transforma dados financeiros simples em diagnóstico, plano de ação e acompanhamento com IA.
