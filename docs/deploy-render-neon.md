# Deploy Render + Neon — INNA Financial Coach AI

## 1. Visão Geral

Este documento registra o processo de deploy em nuvem do projeto **INNA Financial Coach AI**, uma aplicação de educação financeira com IA Generativa.

O objetivo do deploy foi transformar o projeto de uma aplicação local em uma solução online, acessível por navegador, com API pública, banco de dados em nuvem e dashboard analítico.

A arquitetura final utiliza:

* **Render** para hospedar a API FastAPI
* **Render** para hospedar o app principal em Streamlit
* **Render** para hospedar o dashboard em Streamlit
* **Neon PostgreSQL** como banco de dados em nuvem
* **Google Gemini** como modelo de IA Generativa
* **GitHub** como repositório de versionamento

---

## 2. Arquitetura em Produção

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

### Fluxo em produção

1. O usuário acessa o app principal em Streamlit.
2. O usuário preenche o formulário financeiro.
3. O Streamlit envia os dados para a API FastAPI online.
4. A API calcula os indicadores financeiros.
5. A API chama o Google Gemini para gerar o plano de ação de 30 dias.
6. A API salva o diagnóstico no Neon PostgreSQL.
7. O usuário pode gerar relatório PDF.
8. O usuário pode consultar histórico individual.
9. O usuário pode enviar feedback.
10. O dashboard online lê os dados diretamente do Neon PostgreSQL.
11. O dashboard exibe métricas, gráficos, ranking e comentários.

---

## 3. Links de Produção

### App principal — Streamlit

```text
https://inna-app-streamlit.onrender.com
```

### API / Swagger — FastAPI

```text
https://inna-api.onrender.com/docs
```

### Health Check da API

```text
https://inna-api.onrender.com/health
```

### Dashboard analítico — Streamlit

```text
https://inna-dashboard-streamlit.onrender.com
```

### Repositório GitHub

```text
https://github.com/Rogerio5/INNA-Financial-Coach-AI
```

---

## 4. Serviços Criados no Render

Foram criados três serviços separados no Render.

### 4.1 Serviço da API

```text
Nome: inna-api
Tipo: Web Service
Runtime: Python
Plataforma: Render
Framework: FastAPI
```

Responsabilidades:

* Receber dados financeiros
* Calcular diagnóstico
* Chamar Google Gemini
* Salvar diagnósticos no Neon
* Salvar feedbacks no Neon
* Gerar PDF
* Expor endpoints REST
* Disponibilizar Swagger

### 4.2 Serviço do App Principal

```text
Nome: inna-app-streamlit
Tipo: Web Service
Runtime: Python
Plataforma: Render
Framework: Streamlit
```

Responsabilidades:

* Exibir formulário financeiro
* Consumir a API FastAPI online
* Mostrar diagnóstico ao usuário
* Exibir plano de ação de 30 dias
* Permitir envio de feedback
* Permitir consulta de histórico individual
* Permitir geração de relatório PDF

### 4.3 Serviço do Dashboard

```text
Nome: inna-dashboard-streamlit
Tipo: Web Service
Runtime: Python
Plataforma: Render
Framework: Streamlit
```

Responsabilidades:

* Ler dados diretamente do Neon PostgreSQL
* Exibir indicadores gerais
* Exibir gráficos
* Exibir ranking de usuários
* Exibir evolução de score
* Exibir evolução de saldo estimado
* Exibir feedbacks recebidos
* Permitir filtros por data e mês
* Permitir exportação CSV

---

## 5. Banco de Dados em Produção

O banco de dados utilizado em produção é o **Neon PostgreSQL**.

### Configuração geral

```text
Banco: Neon PostgreSQL
Projeto: inna-financial-coach-ai
Banco utilizado: neondb
Usuário: neondb_owner
Região: São Paulo / sa-east-1
```

### Tabelas principais

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
* Diagnóstico textual
* Plano de ação de 30 dias

### Tabela `feedbacks_usuarios`

Armazena:

* Nome do usuário
* Se a resposta foi útil
* Comentário do usuário
* Score financeiro
* Nível de risco

---

## 6. Variáveis de Ambiente

As variáveis sensíveis não são enviadas para o GitHub.

Elas são configuradas diretamente no Render e no arquivo `.env` local.

---

### 6.1 Variáveis do serviço `inna-api`

```env
APP_ENV=production
INNA_MOCK_MODE=false
GEMINI_API_KEY=sua_chave_gemini
GEMINI_MODEL=gemini-2.5-flash-lite
DATABASE_URL=sua_url_neon
API_BASE_URL=https://inna-api.onrender.com
PYTHON_VERSION=3.12.1
```

### Função dessas variáveis

| Variável         | Função                              |
| ---------------- | ----------------------------------- |
| `APP_ENV`        | Define o ambiente como produção     |
| `INNA_MOCK_MODE` | Desativa modo mock e usa IA real    |
| `GEMINI_API_KEY` | Chave da API do Google Gemini       |
| `GEMINI_MODEL`   | Modelo Gemini utilizado             |
| `DATABASE_URL`   | URL de conexão com Neon PostgreSQL  |
| `API_BASE_URL`   | URL pública da própria API          |
| `PYTHON_VERSION` | Força o Render a usar Python 3.12.1 |

---

### 6.2 Variáveis do serviço `inna-app-streamlit`

```env
APP_ENV=production
API_BASE_URL=https://inna-api.onrender.com
INNA_MOCK_MODE=false
PYTHON_VERSION=3.12.1
```

### Função dessas variáveis

| Variável         | Função                               |
| ---------------- | ------------------------------------ |
| `APP_ENV`        | Define o ambiente como produção      |
| `API_BASE_URL`   | Aponta o Streamlit para a API online |
| `INNA_MOCK_MODE` | Mantém modo real ativado             |
| `PYTHON_VERSION` | Força o Render a usar Python 3.12.1  |

Observação:

O serviço `inna-app-streamlit` não precisa da variável `GEMINI_API_KEY`, porque quem chama o Gemini é a API FastAPI.

---

### 6.3 Variáveis do serviço `inna-dashboard-streamlit`

```env
APP_ENV=production
DATABASE_URL=sua_url_neon
PYTHON_VERSION=3.12.1
```

### Função dessas variáveis

| Variável         | Função                                |
| ---------------- | ------------------------------------- |
| `APP_ENV`        | Define o ambiente como produção       |
| `DATABASE_URL`   | Permite ao dashboard ler o banco Neon |
| `PYTHON_VERSION` | Força o Render a usar Python 3.12.1   |

Observação:

O dashboard não precisa da variável `GEMINI_API_KEY`, porque ele não gera respostas com IA. Ele apenas lê os dados salvos no banco.

---

## 7. Comandos de Build e Start

### 7.1 Build Command

Todos os serviços usam o mesmo comando de build:

```bash
pip install -r requirements.txt
```

---

### 7.2 Start Command da API

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

### 7.3 Start Command do App Streamlit

```bash
streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0
```

---

### 7.4 Start Command do Dashboard Streamlit

```bash
streamlit run src/dashboard.py --server.port $PORT --server.address 0.0.0.0
```

---

## 8. Arquivos de Configuração de Deploy

### 8.1 `.python-version`

Arquivo utilizado para orientar o Render a usar uma versão compatível do Python:

```text
3.12.1
```

### 8.2 `runtime.txt`

Arquivo complementar de runtime:

```text
python-3.12.1
```

### 8.3 `.streamlit/config.toml`

Configuração usada para rodar Streamlit corretamente em ambiente de nuvem:

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

---

## 9. Problemas Encontrados e Correções

### 9.1 Render usando Python 3.14

Durante o primeiro deploy, o Render tentou usar Python 3.14, causando erro na instalação de dependências, especialmente em pacotes como `pydantic_core`.

### Correção aplicada

Foi adicionada a configuração de Python 3.12.1:

```text
.python-version
runtime.txt
PYTHON_VERSION=3.12.1
```

Resultado:

```text
Build successful
```

---

### 9.2 Streamlit online mostrando API offline

O app principal em Streamlit abriu online, mas inicialmente exibiu mensagem informando que a API estava offline.

### Causa

O serviço Streamlit não estava apontando corretamente para a URL pública da API.

### Correção aplicada

Foi configurada a variável:

```env
API_BASE_URL=https://inna-api.onrender.com
```

no serviço:

```text
inna-app-streamlit
```

Depois foi executado:

```text
Save, rebuild, and deploy
```

Resultado:

O Streamlit passou a consumir a API online corretamente.

---

### 9.3 Separação das variáveis Gemini

Houve dúvida se o app Streamlit também precisava da chave Gemini.

### Decisão técnica

A chave Gemini deve ficar apenas no serviço da API:

```text
inna-api
```

Motivo:

```text
Streamlit → chama FastAPI
FastAPI → chama Gemini
```

Assim, o app principal não expõe nem precisa acessar diretamente a chave Gemini.

---

### 9.4 Dashboard online separado do app principal

O dashboard foi publicado como um serviço separado para manter responsabilidades isoladas.

### Decisão técnica

Foram usados dois serviços Streamlit:

```text
inna-app-streamlit
inna-dashboard-streamlit
```

Benefício:

* App principal focado no usuário
* Dashboard focado em análise
* Deploys independentes
* Melhor organização da arquitetura

---

## 10. Validação Final

A validação final confirmou que os serviços online estão integrados.

### API FastAPI

Validado:

* API online
* Swagger funcionando
* Health Check funcionando
* Diagnóstico funcionando
* Feedback funcionando
* Histórico individual funcionando
* PDF funcionando
* Banco Neon conectado

Endpoints testados:

```text
GET /health
POST /diagnostico
POST /feedback
GET /diagnosticos
GET /feedbacks
GET /diagnosticos/usuario/{nome}
GET /diagnosticos/{diagnostico_id}/relatorio
```

---

### App Streamlit

Validado:

* App abrindo online
* Formulário carregando
* Diagnóstico sendo gerado
* API online sendo consumida
* Plano de 30 dias aparecendo
* PDF sendo gerado
* Histórico individual funcionando
* Feedback sendo enviado

---

### Dashboard Streamlit

Validado:

* Dashboard abrindo online
* Dados lidos do Neon PostgreSQL
* Indicadores exibidos
* Gráficos exibidos
* Últimos diagnósticos exibidos
* Feedbacks exibidos
* Comentários exibidos
* Exportação CSV disponível

---

### Neon PostgreSQL

Validado:

* Diagnósticos salvos no banco
* Feedbacks salvos no banco
* API lendo e gravando dados
* Dashboard lendo dados reais
* Persistência funcionando em produção

---

## 11. Testes Automatizados

O projeto possui testes automatizados com pytest.

Comando:

```bash
pytest
```

Resultado validado:

```text
3 passed
```

Testes cobrem:

* Regras do motor financeiro
* Cálculo de score
* Validação do endpoint de health da API

---

## 12. Resultado Final do Deploy

O projeto saiu de uma aplicação local para uma aplicação online completa.

### Antes

```text
Streamlit local
FastAPI local
PostgreSQL local
Dashboard local
```

### Depois

```text
Streamlit online no Render
FastAPI online no Render
Dashboard online no Render
Neon PostgreSQL online
Gemini integrado
```

---

## 13. Status Final

```text
Deploy concluído com sucesso.
```

Entregas finalizadas:

* API online
* App principal online
* Dashboard online
* Banco online
* Gemini integrado
* Histórico funcionando
* PDF funcionando
* Feedback funcionando
* Dashboard lendo dados reais
* README atualizado com links de produção
* Documentação técnica de deploy criada

---

## 14. Próximas Melhorias

Possíveis evoluções futuras:

* Criar vídeo demo do projeto
* Adicionar prints no README e na pasta `docs`
* Melhorar layout visual do Streamlit
* Criar autenticação de usuários
* Criar área individual protegida
* Adicionar RAG financeiro
* Adicionar embeddings
* Usar pgvector no Neon
* Criar base de conhecimento financeira
* Integrar com n8n
* Integrar com WhatsApp, Telegram ou Gmail
* Criar versão React do frontend
* Criar versão SaaS simples
* Criar métricas de produto
* Criar painel administrativo

---

## 15. Conclusão

O deploy do **INNA Financial Coach AI** consolidou o projeto como uma aplicação real em nuvem.

A solução agora possui:

* Interface online
* API pública
* Banco de dados em nuvem
* IA Generativa integrada
* Dashboard analítico
* Histórico individual
* Relatório PDF
* Feedback de usuários
* Testes automatizados
* Documentação técnica

Essa estrutura deixa o projeto pronto para apresentação em portfólio, processos seletivos, hackathons e futuras evoluções comerciais.
