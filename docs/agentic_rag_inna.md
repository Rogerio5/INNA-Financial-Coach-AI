# Fase 5.16 — Agentic RAG da INNA

## 1. Objetivo

A Fase 5.16 documenta a evolução da **INNA Financial Coach AI** para uma arquitetura de **Agentic RAG**.

O objetivo é transformar a INNA em uma assistente mais inteligente, capaz de decidir qual caminho seguir antes de responder ao usuário.

Em vez de apenas receber uma pergunta, buscar contexto e gerar uma resposta, a INNA passa a funcionar como um agente de decisão.

Ela pode analisar a intenção do usuário e escolher entre:

- buscar conhecimento no RAG;
- usar memória do usuário;
- calcular uma meta financeira;
- acionar o módulo de segurança financeira;
- pedir mais dados;
- gerar um plano financeiro;
- usar Gemini;
- usar fallback controlado;
- registrar evento no dashboard;
- retornar uma resposta educativa e segura.

---

## 2. O que é Agentic RAG

Agentic RAG é uma evolução do RAG tradicional.

No RAG tradicional, o fluxo costuma ser:

1. Usuário faz uma pergunta.
2. Sistema busca documentos relacionados.
3. Modelo gera resposta com base nos documentos.

No Agentic RAG, existe uma etapa adicional de decisão.

A INNA avalia a pergunta e decide qual estratégia usar.

Exemplo:

> Estou endividado e recebi um Pix estranho. O que faço?

Essa pergunta envolve dois temas:

- organização financeira;
- segurança financeira.

A INNA precisa entender que não basta responder apenas sobre dívidas. Ela também precisa orientar sobre risco relacionado ao Pix.

---

## 3. Diferença entre RAG tradicional e Agentic RAG

| Tipo | Funcionamento |
|---|---|
| RAG tradicional | Busca documentos e gera resposta |
| RAG híbrido | Combina busca vetorial, textual e reranking |
| Agentic RAG | Decide qual ferramenta, memória, busca ou fluxo usar antes de responder |

Na INNA, o Agentic RAG representa a passagem de um sistema de perguntas e respostas para uma assistente orientada por decisão.

---

## 4. Papel do agente da INNA

O agente da INNA atua como um roteador inteligente.

Ele analisa a pergunta e identifica:

- tema principal;
- risco financeiro;
- necessidade de cálculo;
- necessidade de RAG;
- necessidade de memória;
- necessidade de segurança;
- necessidade de pedir mais dados;
- melhor modo de resposta.

A partir disso, escolhe o caminho mais adequado.

---

## 5. Possíveis intenções detectadas

A INNA pode classificar a intenção do usuário em categorias como:

| Intenção | Exemplo |
|---|---|
| Educação financeira | Como organizar meus gastos? |
| Reserva financeira | Como começar uma reserva? |
| Dívidas | Como sair das dívidas? |
| Cartão de crédito | Meu cartão está me apertando |
| Cálculo financeiro | Ganho 3000 e gasto 2500 |
| Segurança Pix | Fiz um Pix errado |
| Fraude | Pediram meu código do banco |
| Golpe digital | Recebi um link suspeito |
| Memória | Como estava minha situação antes? |
| Plano financeiro | Monte um plano para mim |
| Dados insuficientes | O usuário pergunta algo sem informar renda, gastos ou objetivo |

---

## 6. Ferramentas internas planejadas

O Agentic RAG pode usar diferentes ferramentas internas.

| Ferramenta | Função |
|---|---|
| `rag_search` | Buscar conhecimento na base RAG |
| `hybrid_search` | Combinar busca vetorial e textual |
| `reranker` | Selecionar os melhores chunks |
| `financial_calculator` | Calcular saldo, meta semanal, margem e risco |
| `security_router` | Acionar respostas sobre Pix, fraude e golpes |
| `user_memory` | Consultar histórico simples do usuário |
| `question_clarifier` | Pedir dados faltantes |
| `gemini_answer` | Gerar resposta natural com contexto |
| `controlled_fallback` | Gerar resposta segura sem IA generativa longa |
| `event_logger` | Registrar evento no PostgreSQL/Neon |
| `dashboard_metrics` | Alimentar observabilidade e métricas |

---

## 7. Arquitetura conceitual

Fluxo planejado:

1. Usuário envia uma mensagem.
2. A INNA identifica a intenção.
3. O agente avalia se há risco financeiro ou tema sensível.
4. O agente verifica se precisa buscar no RAG.
5. O agente verifica se precisa usar memória do usuário.
6. O agente decide se precisa calcular algo.
7. O agente decide se deve usar Gemini ou fallback controlado.
8. A resposta é gerada.
9. O evento é registrado.
10. O dashboard exibe métricas de uso.

---

## 8. Exemplo de roteamento

Mensagem do usuário:

> Ganho R$ 3.000, gasto R$ 2.500 e tenho muitas parcelas no cartão.

Decisão do agente:

| Etapa | Decisão |
|---|---|
| Intenção | Organização financeira + cartão |
| Precisa cálculo? | Sim |
| Precisa RAG? | Sim |
| Precisa segurança? | Não |
| Precisa memória? | Talvez |
| Melhor resposta | Cálculo controlado + orientação RAG |
| Modo esperado | `rag_hibrido_pgvector_text_neon_rerank` |

Resposta esperada:

- calcular sobra estimada;
- avaliar comprometimento;
- orientar sobre parcelas;
- sugerir meta simples;
- evitar novas compras parceladas;
- pedir dados adicionais se necessário.

---

## 9. Exemplo com segurança financeira

Mensagem do usuário:

> Alguém pediu meu código do banco pelo WhatsApp.

Decisão do agente:

| Etapa | Decisão |
|---|---|
| Intenção | Segurança financeira |
| Tema | Código bancário / WhatsApp |
| Precisa RAG? | Sim |
| Precisa Gemini? | Não necessariamente |
| Precisa fallback seguro? | Sim |
| Precisa memória? | Não |
| Melhor resposta | Segurança financeira controlada |
| Modo esperado | `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira` |

Resposta esperada:

- não informar código;
- não informar senha;
- acessar app oficial;
- falar com o banco;
- bloquear contato suspeito;
- orientar de forma educativa;
- não confirmar fraude real;
- não prometer solução.

---

## 10. Exemplo com múltiplas intenções

Mensagem do usuário:

> Estou endividado e recebi um Pix estranho. O que faço?

Decisão do agente:

| Etapa | Decisão |
|---|---|
| Intenção 1 | Dívidas |
| Intenção 2 | Segurança Pix |
| Precisa RAG financeiro? | Sim |
| Precisa RAG segurança? | Sim |
| Precisa cálculo? | Talvez |
| Precisa pedir dados? | Sim, se quiser plano detalhado |
| Melhor resposta | Orientação híbrida com prioridade para segurança |
| Modo esperado | RAG híbrido + segurança financeira |

Ordem da resposta:

1. Primeiro orientar sobre o Pix estranho.
2. Depois orientar sobre organização das dívidas.
3. Separar o que é urgente do que é planejamento.
4. Pedir dados financeiros se o usuário quiser um plano mais completo.

---

## 11. Decisão sobre Gemini

O Agentic RAG não precisa usar Gemini em todas as perguntas.

A INNA pode usar Gemini quando:

- a pergunta exige explicação mais natural;
- o usuário precisa de acolhimento;
- há vários temas na mesma pergunta;
- a resposta precisa combinar diferentes fontes;
- o contexto recuperado é suficiente e seguro.

A INNA pode evitar Gemini quando:

- a resposta é de segurança financeira sensível;
- há cálculo simples;
- existe resposta controlada pronta;
- a pergunta exige máxima previsibilidade;
- o custo ou latência deve ser reduzido.

---

## 12. Fallback controlado

O fallback controlado é uma camada importante do Agentic RAG.

Ele é usado quando a INNA precisa responder com segurança, sem depender totalmente de geração livre.

Exemplos:

- cálculo de meta semanal;
- orientação sobre Pix errado;
- pedido de código bancário;
- link suspeito;
- compra não reconhecida;
- aviso sobre não compartilhar senha;
- orientação educativa curta.

Benefícios:

- reduz alucinação;
- reduz custo;
- reduz latência;
- aumenta previsibilidade;
- melhora segurança em temas sensíveis.

---

## 13. Uso da memória por usuário

A memória por usuário pode ser consultada pelo agente quando a pergunta depende de histórico.

Exemplo:

> Como está minha situação financeira agora?

O agente pode verificar:

- última renda informada;
- últimos gastos;
- última meta;
- último risco;
- último score;
- moeda;
- idioma preferido.

Com isso, a INNA pode responder:

> Na última análise, você informou renda de R$ 3.000 e gastos de R$ 2.500. Isso indicava uma sobra estimada de R$ 500. Quer atualizar esses valores para eu recalcular?

A memória deve ser usada com cuidado, sem expor dados sensíveis demais.

---

## 14. Quando pedir mais dados

O Agentic RAG deve saber quando a pergunta não tem informação suficiente.

Exemplo:

> Estou sem dinheiro, o que faço?

A INNA pode pedir:

- renda aproximada;
- gastos principais;
- dívidas;
- valor da fatura;
- objetivo financeiro;
- urgência da situação.

Resposta esperada:

> Posso te ajudar melhor se você me disser, de forma aproximada, quanto entra por mês, quanto sai e se existe alguma dívida ou parcela que está pesando mais.

Isso evita respostas genéricas demais.

---

## 15. Critérios de decisão do agente

A INNA pode seguir regras como:

| Condição | Ação |
|---|---|
| Pergunta contém Pix, senha, token, código, CVV ou link suspeito | Acionar segurança financeira |
| Pergunta contém renda e gastos | Acionar cálculo financeiro |
| Pergunta contém cartão, parcelas ou fatura | Buscar RAG sobre cartão |
| Pergunta contém dívida, juros ou negociação | Buscar RAG sobre dívidas |
| Pergunta contém reserva ou emergência | Buscar RAG sobre reserva |
| Pergunta depende de histórico | Consultar memória |
| Pergunta está incompleta | Pedir mais dados |
| Pergunta é simples e segura | Usar fallback controlado |
| Pergunta exige explicação longa | Usar Gemini com contexto |

---

## 16. Pseudocódigo conceitual

```python
def agentic_rag_inna(pergunta, usuario_id=None):
    intencoes = classificar_intencao(pergunta)
    contexto_memoria = None
    contexto_rag = []
    resposta = None

    if usuario_id:
        contexto_memoria = buscar_memoria_usuario(usuario_id)

    if contem_risco_financeiro(pergunta):
        contexto_rag = buscar_rag_segurança(pergunta)
        resposta = responder_segurança_financeira(pergunta, contexto_rag)
        registrar_evento(pergunta, modo="agentic_rag_seguranca")
        return resposta

    if precisa_calculo(pergunta):
        calculo = calcular_diagnostico(pergunta, contexto_memoria)
        contexto_rag = buscar_rag_financeiro(pergunta)
        resposta = gerar_resposta_com_calculo(pergunta, calculo, contexto_rag)
        registrar_evento(pergunta, modo="agentic_rag_calculo")
        return resposta

    if precisa_mais_dados(pergunta):
        resposta = pedir_dados_faltantes(pergunta)
        registrar_evento(pergunta, modo="agentic_rag_clarificacao")
        return resposta

    contexto_rag = buscar_rag_hibrido(pergunta)
    chunks = aplicar_reranking(contexto_rag)

    if deve_usar_gemini(pergunta, chunks):
        resposta = gerar_com_gemini(pergunta, chunks, contexto_memoria)
        modo = "agentic_rag_gemini"
    else:
        resposta = gerar_fallback_controlado(pergunta, chunks)
        modo = "agentic_rag_fallback"

    registrar_evento(pergunta, modo=modo)
    return resposta 
```

---

## 17. Logs e observabilidade

O Agentic RAG precisa registrar eventos para que seja possível entender como a INNA está tomando decisões.

A observabilidade permite acompanhar:

- qual intenção foi detectada;
- qual ferramenta foi acionada;
- se houve uso de RAG;
- se houve uso de memória;
- se houve cálculo financeiro;
- se houve módulo de segurança financeira;
- se Gemini foi usado;
- se houve fallback controlado;
- quanto tempo a resposta levou;
- se a resposta foi concluída com sucesso.

Esses dados ajudam a transformar a INNA em uma aplicação mais confiável, auditável e preparada para evolução.

---

### 17.1 Campos de log planejados

Cada interação pode registrar informações como:

| Campo | Descrição |
|---|---|
| `id` | Identificador único do evento |
| `usuario_id` | Identificador do usuário, quando existir |
| `pergunta` | Pergunta enviada pelo usuário |
| `intencao_detectada` | Intenção principal identificada |
| `intencoes_secundarias` | Outras intenções encontradas |
| `modo_resposta` | Modo usado pela INNA |
| `usou_rag` | Indica se houve busca RAG |
| `usou_memoria` | Indica se a memória do usuário foi usada |
| `usou_calculo` | Indica se houve cálculo financeiro |
| `usou_seguranca` | Indica se o módulo de segurança foi acionado |
| `usou_gemini` | Indica se Gemini foi usado |
| `usou_fallback` | Indica se houve fallback controlado |
| `chunks_recuperados` | Quantidade de chunks encontrados |
| `chunks_usados` | Quantidade de chunks usados na resposta |
| `fontes_usadas` | Fontes ou documentos usados |
| `tempo_resposta_ms` | Tempo total de resposta em milissegundos |
| `status` | Sucesso, erro ou fallback |
| `idioma` | Idioma usado na resposta |
| `canal` | Origem da interação, como web, dashboard ou API |
| `criado_em` | Data e hora do evento |

---

### 17.2 Exemplo de evento registrado

```json
{
  "usuario_id": "user_001",
  "pergunta": "Recebi um Pix estranho, o que faço?",
  "intencao_detectada": "seguranca_pix",
  "intencoes_secundarias": ["fraude", "orientacao_preventiva"],
  "modo_resposta": "agentic_rag_seguranca_financeira",
  "usou_rag": true,
  "usou_memoria": false,
  "usou_calculo": false,
  "usou_seguranca": true,
  "usou_gemini": false,
  "usou_fallback": true,
  "chunks_recuperados": 5,
  "chunks_usados": 3,
  "fontes_usadas": ["cartilha_pix_golpes.md"],
  "tempo_resposta_ms": 820,
  "status": "sucesso",
  "idioma": "pt",
  "canal": "web"
}
```

---

## 17.3 Exemplo de tabela planejada

```python
CREATE TABLE IF NOT EXISTS agentic_rag_logs (
    id SERIAL PRIMARY KEY,
    usuario_id TEXT,
    pergunta TEXT NOT NULL,
    intencao_detectada TEXT,
    intencoes_secundarias TEXT,
    modo_resposta TEXT,
    usou_rag BOOLEAN DEFAULT FALSE,
    usou_memoria BOOLEAN DEFAULT FALSE,
    usou_calculo BOOLEAN DEFAULT FALSE,
    usou_seguranca BOOLEAN DEFAULT FALSE,
    usou_gemini BOOLEAN DEFAULT FALSE,
    usou_fallback BOOLEAN DEFAULT FALSE,
    chunks_recuperados INTEGER DEFAULT 0,
    chunks_usados INTEGER DEFAULT 0,
    fontes_usadas TEXT,
    tempo_resposta_ms INTEGER,
    status TEXT DEFAULT 'sucesso',
    idioma TEXT DEFAULT 'pt',
    canal TEXT DEFAULT 'web',
    criado_em TIMESTAMP DEFAULT NOW()
); 
```

---

## 17.4 Valor da observabilidade


> A observabilidade ajuda a responder perguntas importantes sobre o funcionamento da INNA:

- Quais temas os usuários mais perguntam?
- Quantas vezes a INNA usou RAG?
- Quantas vezes o módulo de segurança financeira foi acionado?
- Quais respostas precisaram de fallback?
- Quais perguntas demoraram mais?
- Quais fontes foram mais usadas?
- Onde o sistema precisa melhorar?
- O Agentic RAG está escolhendo o caminho certo?

Isso permite melhorar a INNA com base em dados reais, não apenas em opinião.

---

## 18. Métricas planejadas

> As métricas do Agentic RAG ajudam a acompanhar qualidade, custo, segurança e experiência do usuário.

Métricas úteis:

| Métrica                      | Objetivo                            |
| ---------------------------- | ----------------------------------- |
| Total de perguntas           | Medir volume de uso                 |
| Perguntas por intenção       | Entender temas mais comuns          |
| Uso de RAG                   | Ver frequência de busca na base     |
| Uso de memória               | Ver personalização aplicada         |
| Uso de segurança financeira  | Medir casos de Pix, golpe e fraude  |
| Uso de cálculo financeiro    | Medir diagnósticos e simulações     |
| Uso de Gemini                | Acompanhar custo e geração avançada |
| Uso de fallback              | Medir respostas controladas         |
| Tempo médio de resposta      | Avaliar performance                 |
| Taxa de erro                 | Monitorar estabilidade              |
| Fontes mais usadas           | Entender documentos mais relevantes |
| Perguntas sem resposta ideal | Melhorar base de conhecimento       |

---

## 18.1 Métricas por modo de resposta

> A INNA pode acompanhar quantas vezes cada modo foi usado.

Exemplos:

| Modo                               | Quando é usado                                    |
| ---------------------------------- | ------------------------------------------------- |
| `agentic_rag_financeiro`           | Perguntas gerais de educação financeira           |
| `agentic_rag_calculo`              | Perguntas com renda, gastos, metas ou dívidas     |
| `agentic_rag_seguranca_financeira` | Pix, fraude, golpe, senha, token ou link suspeito |
| `agentic_rag_memoria`              | Perguntas que dependem de histórico do usuário    |
| `agentic_rag_gemini`               | Respostas mais completas com IA generativa        |
| `agentic_rag_fallback`             | Respostas controladas e previsíveis               |
| `agentic_rag_clarificacao`         | Quando faltam dados para responder bem            |

---

## 18.2 Métricas para dashboard

O dashboard administrativo poderá mostrar:

- total de interações;
- total por intenção;
- total por idioma;
- total por canal;
- tempo médio de resposta;
- perguntas com segurança financeira;
- perguntas com cálculo;
- perguntas com memória;
- perguntas com fallback;
- documentos mais usados;
- fontes mais usadas;
- evolução diária ou semanal;
- erros por tipo;
- taxa de sucesso.

Essas métricas fortalecem a INNA como produto real, com monitoramento e melhoria contínua.