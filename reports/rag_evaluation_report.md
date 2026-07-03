# Resumo Executivo — Avaliação do RAG INNA

Total de perguntas avaliadas: **13**
Aprovadas: **13**
Atenção: **0**
Revisar: **0**
Taxa de aprovação: **100.0%**

## Interpretação

A avaliação verifica se a INNA usa RAG híbrido, reranking, fontes recuperadas, resposta com Gemini quando adequado e fallback controlado em perguntas com cálculo.

---

# Relatório de Avaliação do RAG — INNA

Data da avaliação: **2026-07-03 01:33:41**

## Objetivo

Avaliar a qualidade do RAG da INNA considerando busca híbrida, pgvector, busca textual, reranking, uso do Gemini quando adequado e fallback controlado para cálculos financeiros.

## Resultados

### 1. Reserva financeira

**Pergunta:** como posso começar uma reserva financeira?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7870500688976965 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.7604390715990917 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7511170506471193 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Vamos por partes. Vou te orientar de um jeito simples:
> 
> 1. Veja quanto entra e quanto sai todo mês com contas, mercado, transporte, compras e parcelas.
> 2. Separe um valor pequeno que caiba no seu bolso, sem apertar demais.
> 3. Não use esse dinheiro para compras do dia a dia.
> 4. Olhe todo mês se conseguiu guardar alguma quantia, mesmo que seja pouco.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 2. Cálculo controlado

**Pergunta:** ganho 3000 gasto 2500 e guardo 100

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, calculo_controlado_sem_gemini, calculo_com_meta, tema_correto, resposta_completa

**Fontes recuperadas:**

- Financeiro Basico | score: 0.6281332175938811 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.612221015976625 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6249952841481666 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Entendi sua anotação. Vou te orientar de forma simples.
> 
> - Renda informada: R$ 3.000 por mês.
> - Gasto informado: R$ 2.500 por mês.
> - Valor que você disse que consegue guardar: R$ 100 por mês.
> 
> Uma forma fácil de começar é dividir esse valor por semana:
> 
> - Meta no mês: R$ 100
> - Meta por semana: cerca de R$ 25
> 
> Meta desta semana:
> 
> 1. Separe cerca de R$ 25 nesta semana.
> 2. Guarde esse valor assim que receber ou assim que sobrar.
> 3. Evite usar esse dinheiro para compras do dia a dia.
> 4. No fim da semana, veja se conseguiu manter esse valor guardado.
> 
> Orientação simples:
> Se uma semana apertar, guarde menos. O importante é começar e manter o costume.
> 
> Quer que eu mostre como ficaria essa meta no mês inteiro?

---

### 3. Cartão de crédito

**Pergunta:** cartão de crédito está me apertando

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa, cartao_contexto_forte

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.660687810660314 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7130954941123786 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7009234649711438 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Olá! Que bom que você veio conversar comigo. Se o cartão de crédito está apertando, vamos por partes para a gente entender direitinho e achar um caminho.
> 
> De forma simples, o primeiro passo é dar uma olhada na sua fatura. Anote o valor total que está chegando. Depois, a gente pode separar o que foi compra essencial do que foi algo que talvez pudesse esperar.
> 
> Outra coisa importante é, enquanto a fatura está apertada, tentar evitar fazer novas compras parceladas. Assim, a gente não acumula mais para frente.
> 
> E para essa semana, que tal a gente pensar em uma meta pequena? Pode ser algo como reduzir uma compra que não seja tão essencial, ou diminuir um pouco o uso do cartão nos próximos dias.
> 
> O importante é começar a olhar para isso, viu?
> 
> Você gostaria de me contar um pouco mais sobre como tem sido o uso do seu cartão ultimamente? Assim, posso te orientar melhor.

---

### 4. Organização de gastos

**Pergunta:** como organizar gastos fixos e variáveis?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7014182371804327 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6474803236607236 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.6518220338707291 | fonte: `data/knowledge_base/financeiro_basico.md`

**Resposta gerada:**

> Vamos por partes. O melhor caminho para organizar seus gastos é:
> 
> 1. Separe seus gastos em fixos, variáveis e dívidas.
> 2. Identifique gastos pequenos recorrentes que podem ser reduzidos.
> 3. Defina um limite semanal para despesas variáveis.
> 4. Revise seu orçamento ao final de cada mês.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 5. Dívidas

**Pergunta:** como sair das dívidas?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Financeiro Basico | score: 0.734657414261252 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.7309024114663539 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7416262597189681 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Vamos por partes. O melhor caminho para reduzir suas dívidas é:
> 
> 1. Liste todas as dívidas, parcelas, juros e vencimentos.
> 2. Priorize o pagamento das dívidas mais caras ou com maior impacto no orçamento.
> 3. Evite assumir novas dívidas durante o plano de organização.
> 4. Negocie condições melhores quando possível.
> 
> Quer que eu monte uma meta simples para esta semana?

---

### 6. Reserva emergencial

**Pergunta:** o que é reserva de emergência?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Financeiro Basico | score: 0.7119344188884856 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.6888318318859966 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6602684278515575 | fonte: `data/knowledge_base/financeiro_basico.md`

**Resposta gerada:**

> Olá! Eu sou a INNA, sua amiga aqui para te ajudar a entender melhor sobre dinheiro. Vamos conversar sobre reserva de emergência?
> 
> De forma simples, **reserva financeira** é um dinheirinho que a gente separa para usar quando acontece algum imprevisto, sabe? É como ter um "colchãozinho" para não passar aperto.
> 
> **Por que ela é importante?** Porque a vida tem dessas coisas! Às vezes o carro quebra, alguém da família precisa de um remédio, ou acontece alguma coisa inesperada que a gente não planejou. Com a reserva, você fica mais tranquila para lidar com esses sustos sem precisar se apertar ou se endividar.
> 
> **Um caminho possível é pensar assim:** O quanto você gasta por mês, contando tudo (moradia, comida, transporte, as parcelinhas), te ajuda a ter uma ideia de quanto seria bom ter guardado para cobrir alguns desses gastos em caso de emergência. Quanto mais você tiver guardado comparado com seus gastos, mais protegida você vai se sentir.
> 
> Quer saber como podemos começar a pensar em ter essa reserva? Ou talvez você queira falar um pouco mais sobre suas dívidas?

---

### 7. Gastos pequenos

**Pergunta:** gasto muito com pequenas compras, como posso organizar?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7067015603385549 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6972376313889488 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6777007932644881 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Olá! Que bom que você veio conversar sobre isso. É super comum a gente se perder um pouquinho com as pequenas compras, elas parecem inofensivas, né? Mas juntas podem pesar no bolso.
> 
> Vou te orientar de forma simples, vamos por partes:
> 
> O primeiro passo é entender quanto da sua renda já está comprometida com esses gastos menores. Sabe aquela comprinha aqui, um cafezinho ali, um lanche no meio do dia? Se anotarmos tudo, vamos ter uma ideia mais clara.
> 
> Depois de saber para onde o dinheiro está indo, o importante é começar a organizar. Um caminho possível é tentar **evitar novas compras pequenas que não sejam essenciais** nesta semana. Que tal escolher uma pequena ação para esta semana, como reduzir uma dessas compras não essenciais?
> 
> E se você quiser montar uma meta para te ajudar, podemos pensar juntos em algo bem pequeno para começar. Por exemplo, se você quer tentar economizar R$ 20 na semana, pode ser uma boa meta para começar.
> 
> Ficou com alguma dúvida sobre por onde começar a anotar?

---

### 8. Parcelas

**Pergunta:** tenho muitas parcelas no cartão, por onde começo?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa, cartao_contexto_forte, parcelas_plano_pratico

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.8057115493327506 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7879543222181152 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.8240515497733375 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Olá! Que bom que você buscou ajuda para organizar as suas parcelas no cartão. Vou te orientar de forma simples, como sempre gostamos por aqui.
> 
> Quando a gente tem muitas parcelas, o primeiro passo é entender o quanto da sua renda já está comprometida com essas compras. **Vamos por partes**:
> 
> 1.  **Olhar a fatura atual**: Dê uma olhada na sua fatura atual e veja quanto você já gastou e quanto ainda tem para pagar dela.
> 2.  **Ver as parcelas futuras**: Agora, separe todas as outras parcelas que você já assumiu e que vão aparecer nas próximas faturas. É importante ver o total que vai sair do seu bolso nos próximos meses.
> 3.  **Quanto da sua renda está comprometida?**: Junte o valor da fatura atual com o total das parcelas futuras e veja qual parte da sua renda já está "destinada" a essas dívidas.
> 
> A partir daí, **um caminho possível é**:
> 
> *   **Evitar novas compras parceladas por enquanto**: Sei que às vezes a gente se empolga com uma oferta, mas agora é a hora de dar um respiro para o seu orçamento. Deixe as novas parcelas para depois, quando a situação estiver mais leve.
> *   **Olhar os juros**: Se alguma parcela tem juros altos, ou se você já se atrasou e gerou mais juros, isso também precisa da sua atenção. Às vezes, vale a pena focar em quitar essas dívidas que estão "engordando".
> *   **Separar o essencial do impulso**: Pense se aquela compra que virou parcela era algo que você realmente precisava agora, ou se foi mais um impulso. Isso ajuda a gente a aprender para as próximas vezes.
> 
> Para começar, que tal criarmos uma meta simples para esta semana? Pode ser algo como **reduzir um gasto não essencial** que você costuma fazer. O importante é começar, mesmo que seja com um passo pequeno.
> 
> Como você se sente olhando para o total dessas parcelas?

---

### 9. Segurança Financeira

**Pergunta:** apareceu uma compra no meu cartão que eu não reconheço

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, seguranca_educativa, resposta_completa

**Fontes recuperadas:**

- Segurança Financeira | score: None | fonte: `data/knowledge_base/seguranca_financeira.md`

**Resposta gerada:**

> Se apareceu uma compra no cartão que você não reconhece, confira primeiro se o nome do estabelecimento é familiar ou se alguém autorizado usou o cartão. Se continuar suspeito, bloqueie temporariamente o cartão pelo aplicativo oficial do banco e entre em contato com a central oficial. Não informe senha, código SMS, token, CVV ou número completo do cartão para terceiros. A INNA orienta de forma educativa e não confirma fraude real nem promete estorno.

---

### 10. Segurança Financeira

**Pergunta:** recebi um link dizendo que minha conta do banco será bloqueada

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, seguranca_educativa, resposta_completa

**Fontes recuperadas:**

- Segurança Financeira | score: None | fonte: `data/knowledge_base/seguranca_financeira.md`

**Resposta gerada:**

> Se você recebeu um link dizendo que sua conta do banco será bloqueada, desconfie. Não clique no link e não informe senha, token, código SMS, CVV ou número completo do cartão. Acesse apenas o aplicativo oficial do banco ou entre em contato pelos canais oficiais. Mensagens com urgência, ameaça de bloqueio ou pedido de dados costumam ser sinais de golpe. A INNA orienta de forma educativa e preventiva.

---

### 11. Segurança Financeira

**Pergunta:** fiz um pix errado, o que devo fazer?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, seguranca_educativa, resposta_completa

**Fontes recuperadas:**

- Segurança Financeira | score: None | fonte: `data/knowledge_base/seguranca_financeira.md`

**Resposta gerada:**

> Se você fez um PIX errado, o primeiro passo é conferir o comprovante, verificar o nome de quem recebeu e entrar em contato com seu banco pelos canais oficiais o quanto antes. Se for possível, tente falar com o recebedor de forma segura. Não aceite ajuda de desconhecidos por WhatsApp, SMS ou redes sociais e nunca informe senha, token ou código de segurança. A INNA orienta de forma educativa e não consegue recuperar PIX nem prometer estorno.

---

### 12. Segurança Financeira

**Pergunta:** alguém pediu meu código do banco pelo whatsapp

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, seguranca_educativa, resposta_completa

**Fontes recuperadas:**

- Segurança Financeira | score: None | fonte: `data/knowledge_base/seguranca_financeira.md`

**Resposta gerada:**

> Não envie código do banco, senha, token ou código SMS pelo WhatsApp. Esse tipo de informação pode permitir acesso à sua conta ou autorizar transações. Bancos não costumam pedir esse tipo de dado por mensagem. Entre no aplicativo oficial do banco ou fale com a central oficial para verificar a situação. Se você já informou algum dado, troque as senhas, bloqueie cartões se necessário e procure o banco imediatamente pelos canais oficiais. A INNA orienta de forma educativa e preventiva.

---

### 13. Segurança Financeira

**Pergunta:** como me proteger de golpes financeiros?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_seguranca_financeira`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, seguranca_educativa, resposta_completa

**Fontes recuperadas:**

- Segurança Financeira | score: None | fonte: `data/knowledge_base/seguranca_financeira.md`

**Resposta gerada:**

> Para se proteger de golpes financeiros, evite clicar em links suspeitos, confira os dados antes de fazer PIX e nunca informe senha, token, código SMS, CVV ou número completo do cartão. Use apenas aplicativos oficiais do banco, ative notificações de compra e procure os canais oficiais se algo parecer estranho. A INNA orienta de forma educativa e preventiva.

---
