# Roadmap — INNA Financial Coach AI

## Versão 0.1
- Formulário financeiro
- Diagnóstico
- Score
- Plano de 30 dias
- API FastAPI
- Streamlit
- Logs em CSV

## Versão 0.2
- Deploy online
- PostgreSQL/Supabase
- Login simples
- Histórico por usuário
- Feedback de resposta

## Versão 0.3
- RAG financeiro
- n8n
- Telegram
- Gmail
- Dashboard

## Versão 1.0
- Produto público
- Página de planos
- Usuários reais
- Relatórios PDF
- Métricas para hackathon

## Privacidade contextual de metadados técnicos

**Status:** Planejado

Evoluir o detector de privacidade para reconhecer metadados
técnicos estritamente validados, sem confiar apenas no nome
das propriedades.

### Escopo planejado

- reconhecer identificadores técnicos somente com formato válido;
- validar UUIDs, hashes e referências de execução;
- validar timestamps ISO 8601 com timezone obrigatório;
- limitar tamanho e caracteres permitidos;
- diferenciar metadados técnicos de conteúdo fornecido por usuários;
- impedir conteúdo arbitrário em campos considerados técnicos;
- preservar o bloqueio de segredos e dados pessoais;
- criar testes contra bypass por nomes de campos confiáveis;
- medir falsos positivos e falsos negativos;
- exigir revisão de segurança antes da ativação.

### Solução atual

Os relatórios externos utilizam:

- `run_reference` curta e não reversível;
- `generated_date` sem horário;
- allowlist de metadados;
- bloqueio estrutural de conteúdo do usuário;
- bloqueio de campos associados a segredos;
- identificadores completos somente no relatório interno.
