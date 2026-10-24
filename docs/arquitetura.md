# Arquitetura — INNA Financial Coach AI e Sabino.AI

## Arquitetura de Solução — Financeiro

[Abrir a arquitetura de solução completa do Financeiro](architecture/solution/financeiro.md)

Documento de referência com contexto de negócio, arquitetura atual e proposta, backend, dados, segurança, integração da INNA, implantação, atributos de qualidade, decisões técnicas e plano de evolução. Inclui seis diagramas Mermaid e distingue implementação observada de proposta e validação em produção.

## Outras visões

- [Arquitetura da INNA](arquitetura_inna.md)
- [Arquiteturas e contratos técnicos](architecture/)
- [Implantação Render e Neon](deploy-render-neon.md)

## Histórico: visão inicial do MVP

A visão abaixo é histórica; não representa a arquitetura atual completa.


```text
Usuário
  ↓
Streamlit / Web App
  ↓
FastAPI /diagnostico
  ↓
Financial Engine
  ↓
Gemini API ou Mock Mode
  ↓
Resposta educativa + plano de 30 dias
  ↓
Logs / Analytics / Feedback
```

## Componentes

- Interface: Streamlit
- API: FastAPI
- Motor financeiro: regras simples em Python
- IA: Gemini API ou Mock Mode
- Logs: CSV no MVP
- Próxima etapa: PostgreSQL/Supabase
