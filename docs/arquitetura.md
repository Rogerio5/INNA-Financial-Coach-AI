# Arquitetura — INNA Financial Coach AI

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
