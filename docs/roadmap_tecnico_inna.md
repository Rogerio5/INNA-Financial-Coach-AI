# Roadmap Técnico — INNA Financial Coach AI

## 1. Objetivo

Este documento apresenta o roadmap técnico atualizado da **INNA Financial Coach AI**.

O objetivo é organizar a evolução do projeto de forma profissional, mostrando o que já foi construído, o que está em andamento e quais são as próximas etapas técnicas.

Este roadmap complementa o arquivo `docs/roadmap.md`, que representa o roadmap inicial do MVP.

---

## 2. Visão geral do projeto

A INNA Financial Coach AI é uma assistente financeira educativa com inteligência artificial, RAG, dashboard administrativo, banco de dados PostgreSQL/Neon, suporte multilíngue e camada de segurança financeira.

A proposta é ajudar pessoas comuns a entender melhor sua situação financeira, organizar gastos, criar metas simples, lidar com dívidas e evitar golpes financeiros.

A INNA não substitui banco, contador, advogado, consultor financeiro ou profissional certificado. Ela atua como uma orientadora educativa.

---

## 3. Estado atual do projeto

A versão atual da INNA já possui uma base técnica sólida.

Recursos já trabalhados:

- Streamlit;
- FastAPI;
- PostgreSQL/Neon;
- Gemini;
- RAG financeiro;
- RAG híbrido;
- pgvector;
- busca textual;
- reranking;
- dashboard administrativo;
- exportação CSV;
- geração de diagnóstico;
- segurança financeira;
- observabilidade;
- suporte multilíngue;
- validação real do RAG;
- documentação técnica organizada;
- deploy em nuvem com Render e Neon.

---

## 4. Fases concluídas

| Fase | Nome | Status |
|---|---|---|
| MVP inicial | Formulário financeiro e diagnóstico | Concluído |
| Deploy | Render + Neon PostgreSQL | Concluído |
| Dashboard | Painel administrativo com métricas | Concluído |
| Segurança | Camada educativa sobre Pix, fraudes e golpes | Concluído |
| RAG inicial | Base de conhecimento financeira | Concluído |
| Fase 5.11 | RAG Híbrido | Concluído |
| Fase 5.12 | Reranking | Concluído |
| Fase 5.13 | Avaliação real do RAG | Concluído |
| Fase 5.14 | Upload de documentos | Documentado |
| Fase 5.15 | Memória por usuário | Documentado |
| Fase 5.16 | Agentic RAG | Documentado |
| Fase 5.17 | Roadmap técnico atualizado | Em criação |

---

## 5. Arquitetura atual

A arquitetura atual pode ser representada assim:

```text
Usuário
↓
Streamlit App
↓
FastAPI
↓
Motor financeiro
↓
RAG Híbrido
↓
PostgreSQL/Neon + pgvector
↓
Reranking
↓
Gemini ou fallback controlado
↓
Resposta educativa
↓
Logs e dashboard
```

Essa arquitetura mostra que a INNA evoluiu de um formulário financeiro simples para uma aplicação com IA, banco de dados, RAG, observabilidade e visão de produto.

---

## 6. Componentes principais

| Componente | Função |
|---|---|
| `src/app.py` | Interface principal do usuário |
| `src/dashboard.py` | Dashboard administrativo |
| `api/main.py` | API FastAPI |
| `src/rag_engine.py` | Motor RAG |
| `src/prompts.py` | Prompts e diretrizes da INNA |
| `data/knowledge_base` | Base de conhecimento financeira |
| `reports` | Relatórios de avaliação e observabilidade |
| `docs` | Documentação técnica |
| PostgreSQL/Neon | Banco de dados |
| pgvector | Busca vetorial |
| Gemini | IA generativa |
| Streamlit | Interface visual |
| Render | Deploy em nuvem |

---

## 7. Base de conhecimento

A base de conhecimento da INNA contém conteúdos sobre:

- educação financeira;
- organização de gastos;
- reserva financeira;
- cartão de crédito;
- dívidas;
- Pix;
- fraudes;
- golpes financeiros;
- boletos falsos;
- segurança bancária;
- orientação para pessoas leigas;
- proteção de idosos.

Arquivos principais:

```text
data/knowledge_base/financeiro_basico.md
data/knowledge_base/faq_financeiro_inna.md
data/knowledge_base/seguranca_financeira.md
data/knowledge_base/cartilha_pix_golpes.md
```

---

## 8. RAG Híbrido

O RAG Híbrido da INNA combina:

- busca vetorial;
- busca textual;
- PostgreSQL/Neon;
- pgvector;
- reranking;
- Gemini quando necessário;
- fallback controlado;
- segurança financeira.

Essa abordagem melhora a precisão das respostas e reduz o risco de respostas genéricas.

Documentação relacionada:

```text
docs/rag_hibrido_inna.md
docs/reranking_inna.md
docs/testes_rag_inna.md
```

---

## 9. Validação do RAG

A avaliação real do RAG mostrou:

| Métrica | Resultado |
|---|---|
| Perguntas avaliadas | 13 |
| Perguntas aprovadas | 13 |
| Perguntas em atenção | 0 |
| Perguntas para revisar | 0 |
| Taxa de aprovação | 100% |

Temas testados:

- reserva financeira;
- organização de gastos;
- cartão de crédito;
- dívidas;
- Pix;
- fraude;
- link suspeito;
- boleto falso;
- proteção de idosos;
- compra não reconhecida.

---

## 10. Segurança financeira

A camada de segurança financeira é uma das partes mais importantes da INNA.

Ela trata situações como:

- Pix estranho;
- Pix errado;
- pedido de código bancário;
- pedido de senha;
- token;
- CVV;
- link falso;
- boleto suspeito;
- falso funcionário de banco;
- golpe contra idosos;
- compra não reconhecida.

A INNA deve orientar sempre de forma educativa, sem prometer recuperação de valores e sem substituir canais oficiais.

Documentação relacionada:

```text
docs/seguranca_financeira_inna.md
docs/inna_guidelines.md
data/knowledge_base/seguranca_financeira.md
data/knowledge_base/cartilha_pix_golpes.md
```

---

## 11. Upload de documentos

A Fase 5.14 prepara a INNA para receber novos documentos na base de conhecimento.

Objetivo:

- permitir expansão da base RAG;
- aceitar novos materiais educativos;
- gerar chunks;
- criar embeddings;
- salvar conteúdo no Neon;
- permitir atualização contínua da base.

Status atual:

```text
Documentado
```

Próxima evolução:

```text
Implementar upload real no Streamlit
```

Documentação relacionada:

```text
docs/upload_documentos_inna.md
```

---

## 12. Memória por usuário

A Fase 5.15 prepara a INNA para lembrar informações básicas do usuário.

Exemplos de dados possíveis:

- renda informada;
- gastos mensais;
- valor que consegue guardar;
- existência de dívidas;
- uso de cartão;
- último diagnóstico;
- última meta;
- preferência de idioma;
- moeda utilizada.

Status atual:

```text
Documentado
```

Próxima evolução:

```text
Criar tabela e integrar memória ao fluxo real
```

Documentação relacionada:

```text
docs/memoria_usuario_inna.md
```

---

## 13. Agentic RAG

A Fase 5.16 representa uma evolução avançada da INNA.

O Agentic RAG permite que a assistente escolha o melhor caminho antes de responder.

Possíveis decisões:

- buscar no RAG;
- usar memória;
- calcular diagnóstico;
- acionar segurança financeira;
- pedir mais dados;
- usar Gemini;
- usar fallback controlado;
- registrar logs;
- alimentar dashboard.

Status atual:

```text
Documentado
```

Próxima evolução:

```text
Implementar classificador de intenção e roteador de ferramentas
```

Documentação relacionada:

```text
docs/agentic_rag_inna.md
```

---

## 14. Observabilidade

A observabilidade permite acompanhar como a INNA está funcionando.

Métricas importantes:

- total de perguntas;
- perguntas por intenção;
- uso de Gemini;
- uso de fallback;
- uso de segurança financeira;
- uso de RAG;
- tempo médio de resposta;
- erros;
- fontes mais usadas;
- temas mais frequentes.

Próxima evolução:

```text
Criar painel específico de observabilidade do Agentic RAG
```

Relatórios relacionados:

```text
reports/rag_evaluation_report.md
reports/rag_evaluation_results.csv
reports/rag_observability_report.md
```

---

## 15. Roadmap técnico por prioridade

### Prioridade alta

| Item | Objetivo | Status |
|---|---|---|
| Corrigir e organizar documentação | Melhorar portfólio | Em andamento |
| Atualizar README | Facilitar navegação no GitHub | Em andamento |
| Implementar upload real de documentos | Expandir base RAG | Planejado |
| Criar tabela de memória | Personalizar respostas | Planejado |
| Melhorar testes RAG | Aumentar validação | Planejado |
| Criar logs estruturados | Melhorar observabilidade | Planejado |

---

### Prioridade média

| Item | Objetivo | Status |
|---|---|---|
| Agentic RAG real | Orquestrar decisões | Planejado |
| Dashboard de documentos | Acompanhar uploads | Planejado |
| Dashboard de intenção | Medir temas mais frequentes | Planejado |
| Testes por idioma | Validar multilíngue | Planejado |
| API para RAG | Expor busca e resposta via endpoint | Planejado |
| Histórico por usuário | Melhorar continuidade | Planejado |

---

### Prioridade futura

| Item | Objetivo | Status |
|---|---|---|
| Login de usuários | Criar área individual | Futuro |
| Plano premium | Monetização | Futuro |
| WhatsApp ou Telegram | Canal multicanal | Futuro |
| n8n | Automações externas | Futuro |
| React frontend | Interface mais profissional | Futuro |
| SaaS simples | Produto comercial | Futuro |

---

## 16. Próximas fases recomendadas

### Fase 5.18 — Upload Real no Streamlit

Objetivo:

- criar tela de upload;
- aceitar `.md`, `.txt` e `.pdf`;
- salvar documentos;
- gerar chunks;
- salvar no banco;
- permitir ativar e desativar documentos.

---

### Fase 5.19 — Memória Real por Usuário

Objetivo:

- criar tabela `memoria_usuarios_inna`;
- salvar resumo do usuário;
- recuperar histórico;
- atualizar dados;
- permitir apagar memória.

---

### Fase 5.20 — Agentic RAG Real

Objetivo:

- criar classificador de intenção;
- criar roteador de ferramentas;
- integrar RAG, memória, cálculo e segurança;
- registrar modo de resposta;
- criar testes agentic.

---

### Fase 5.21 — Dashboard de Observabilidade Avançada

Objetivo:

- mostrar intenções detectadas;
- mostrar tempo médio por modo;
- mostrar uso de Gemini;
- mostrar uso de fallback;
- mostrar uso de segurança financeira;
- mostrar documentos mais usados.

---

## 17. Checklist técnico atual

| Item | Status |
|---|---|
| Projeto local funcionando | Concluído |
| API FastAPI | Concluído |
| App Streamlit | Concluído |
| Dashboard Streamlit | Concluído |
| Banco Neon | Concluído |
| Gemini integrado | Concluído |
| Deploy Render | Concluído |
| RAG financeiro | Concluído |
| RAG Híbrido | Concluído |
| Reranking | Concluído |
| Segurança financeira | Concluído |
| Testes RAG | Concluído |
| Upload de documentos | Documentado |
| Memória por usuário | Documentado |
| Agentic RAG | Documentado |
| Roadmap técnico | Em criação |

---

## 18. Organização recomendada das pastas

Estrutura recomendada:

```text
docs/
├── arquitetura.md
├── deploy-render-neon.md
├── inna_guidelines.md
├── pitch.md
├── roadmap.md
├── roadmap_tecnico_inna.md
├── rag_architecture.md
├── rag_roadmap.md
├── rag_status_atual.md
├── rag_hibrido_inna.md
├── reranking_inna.md
├── testes_rag_inna.md
├── seguranca_financeira_inna.md
├── upload_documentos_inna.md
├── memoria_usuario_inna.md
├── agentic_rag_inna.md
└── validacao_produto_inna.md
```

Base de conhecimento:

```text
data/
└── knowledge_base/
    ├── financeiro_basico.md
    ├── faq_financeiro_inna.md
    ├── seguranca_financeira.md
    └── cartilha_pix_golpes.md
```

Relatórios:

```text
reports/
├── rag_evaluation_report.md
├── rag_evaluation_results.csv
└── rag_observability_report.md
```

---

## 19. Valor para portfólio

Este roadmap mostra que a INNA não é apenas um protótipo visual.

Ela possui:

- arquitetura;
- banco de dados;
- IA generativa;
- RAG;
- segurança financeira;
- dashboard;
- deploy;
- testes;
- documentação;
- roadmap evolutivo;
- visão de produto;
- visão técnica.

Isso fortalece o projeto para:

- GitHub;
- LinkedIn;
- entrevistas;
- hackathons;
- processos seletivos;
- apresentação para empresas;
- evolução para produto real.

---

## 20. Resumo executivo

O roadmap técnico da INNA organiza a evolução do projeto em uma trilha clara.

A solução já saiu do MVP básico e avançou para uma arquitetura com RAG Híbrido, reranking, Neon PostgreSQL, dashboard, segurança financeira, observabilidade e documentação técnica.

As próximas etapas são implementar upload real de documentos, memória por usuário e Agentic RAG real.

Com isso, a INNA se posiciona como uma assistente financeira educativa inteligente, segura, rastreável e preparada para evolução como produto digital.