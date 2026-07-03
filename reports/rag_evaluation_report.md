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

Data da avaliação: **2026-07-03 00:05:16**

## Objetivo

Avaliar a qualidade do RAG da INNA considerando busca híbrida, pgvector, busca textual, reranking, uso do Gemini quando adequado e fallback controlado para cálculos financeiros.

## Resultados

### 1. Reserva financeira

**Pergunta:** como posso começar uma reserva financeira?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7870500688976965 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.7604390715990917 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7511170506471193 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Olá! Que bom que você quer pensar na sua reserva financeira. É um passo muito importante para ter mais tranquilidade.
> 
> De forma simples, a reserva financeira é um dinheiro que a gente separa para ajudar quando aparece um imprevisto, sabe? Algo que a gente não planejou.
> 
> Para começar, **o importante é começar**! Uma ideia possível é separar um valor pequeno por semana. Pode ser R$ 10, R$ 20, R$ 50 ou o valor que você sentir que não vai atrapalhar suas contas principais. O segredo é criar o hábito de guardar, mesmo que seja pouquinho.
> 
> Você gostaria de entender como organizar seus gastos primeiro para ver quanto consegue separar?

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

> Oi! Entendo que o cartão de crédito pode trazer preocupações quando aperta o orçamento. Vou te orientar de forma simples para a gente entender o que está acontecendo.
> 
> De forma prática, o primeiro passo é olhar a sua fatura e ver quanto exatamente você precisa pagar. Vamos por partes:
> 
> 1.  **Anote o valor total da fatura:** Quanto você tem que pagar neste mês?
> 2.  **Separe o que é essencial:** Dê uma olhada nas compras. Quais delas eram realmente necessárias e quais poderiam ter esperado?
> 3.  **Evite novas parcelas:** Enquanto a fatura estiver pesada, tente não fazer novas compras parceladas. Isso evita que a bola de neve de juros e pagamentos aumente.
> 4.  **Olhe os juros:** Veja se há cobrança de juros, multas por atraso ou algum parcelamento automático que você não escolheu.
> 5.  **Priorize o que tem mais juros:** Se tiver alguma dívida que está com juros mais altos, o importante é tentar dar um jeito nela primeiro.
> 6.  **Crie uma meta pequena:** Para esta semana, que tal pensarmos em uma pequena ação para reduzir o uso do cartão? Algo simples, como dizer "não" para uma compra não essencial?
> 
> O importante é começar a organizar e entender para onde o dinheiro está indo.
> 
> Ficou mais claro como podemos começar a olhar para isso?

---

### 4. Organização de gastos

**Pergunta:** como organizar gastos fixos e variáveis?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7014182371804327 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6474803236607236 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.6518220338707291 | fonte: `data/knowledge_base/financeiro_basico.md`

**Resposta gerada:**

> Oi! Sou a INNA, sua amiga IA para te ajudar a entender melhor o seu dinheiro. Que bom que você veio conversar comigo!
> 
> Vamos por partes para organizar os gastos. De forma simples, a gente pode pensar em dois tipos de gastos:
> 
> 1.  **Gastos Fixos:** São aqueles que vêm todo mês, mais ou menos com o mesmo valor, como o aluguel ou a prestação da casa, a conta de luz, água, gás, internet, telefone e mensalidade de escola, se tiver.
> 2.  **Gastos Variáveis:** São aqueles que mudam de mês para mês e dependem mais do nosso dia a dia, como a comida do mercado, o transporte (gasolina, passagem de ônibus), farmácia, um lanche fora, ou aquela comprinha que a gente faz.
> 
> Para começar a organizar, um caminho possível é anotar tudinho! Pegue um caderninho ou o celular e anote o que você gasta em cada uma dessas categorias por um mês. Assim, você vai ver para onde seu dinheiro está indo e onde talvez seja possível fazer algum ajuste.
> 
> Já tem alguma ideia de como separa esses gastos no seu dia a dia?

---

### 5. Dívidas

**Pergunta:** como sair das dívidas?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank_gemini_answer`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, gemini_final, tem_fontes, tema_correto, resposta_completa

**Fontes recuperadas:**

- Financeiro Basico | score: 0.734657414261252 | fonte: `data/knowledge_base/financeiro_basico.md`
- Financeiro Basico | score: 0.7309024114663539 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.7416262597189681 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Olá! Eu sou a INNA, sua amiga IA para organização financeira. Fico feliz em te orientar nessa jornada para sair das dívidas. Vamos por partes?
> 
> Para sair das dívidas, o importante é começar com um bom entendimento da sua situação atual. Vou te orientar com alguns passos práticos:
> 
> 1.  **Vamos levantar tudo:** De forma simples, o primeiro passo é saber exatamente quanto você deve. Pegue papel e caneta (ou use um bloco de notas no celular) e anote todas as suas dívidas. Para cada uma, escreva:
>     *   Para quem você deve (nome do banco, loja, pessoa).
>     *   Qual o valor total da dívida.
>     *   Quanto você paga por mês.
>     *   Se tem juros e quanto é mais ou menos.
>     *   Qual a data de vencimento de cada parcela.
> 
> 2.  **Entendendo a sua lista:** Agora que você tem a lista, vamos olhar com atenção. Algumas dívidas podem ser mais urgentes que outras. Geralmente, aquelas com juros mais altos pesam mais no seu bolso a longo prazo. Pense em quais parcelas estão mais difíceis de pagar ou quais estão crescendo mais por causa dos juros.
> 
> 3.  **Negociar é um caminho:** Com a lista em mãos, é possível ver onde você pode tentar negociar. Falar com quem você deve para ver se é possível mudar o valor da parcela para algo que caiba melhor no seu orçamento pode ajudar muito.
> 
> 4.  **Um respiro nas despesas:** Para conseguir pagar as dívidas e organizar suas finanças, pode ser um bom momento para dar uma olhada em todos os seus gastos. Vamos categorizar seus gastos para entender para onde o dinheiro está indo. Você pode separar em: moradia, alimentação, transporte, saúde, educação, lazer, as próprias dívidas, e o que sobrar pode ser uma "reserva" ou gastos variáveis. Identificar onde é possível cortar um pouco, mesmo que temporariamente, faz toda a diferença.
> 
> 5.  **Sem novas compras parceladas:** Enquanto você está nesse plano para sair das dívidas, é fundamental evitar fazer novas compras parceladas. Assim, você não cria mais um peso para o seu orçamento.
> 
> 6.  **Acompanhamento é chave:** É muito importante acompanhar sua evolução. Uma vez por semana, olhe sua lista de dívidas e veja se já pagou alguma ou se os valores diminuíram. Isso te ajuda a ver que você está no caminho certo!
> 
> Lembre-se, a organização financeira é um processo. O importante é começar e ir ajustando aos poucos.
> 
> Como você se sente em começar anotando todas as suas dívidas?

---

### 6. Reserva emergencial

**Pergunta:** o que é reserva de emergência?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Financeiro Basico | score: 0.7119344188884856 | fonte: `data/knowledge_base/financeiro_basico.md`
- Faq Financeiro Inna | score: 0.6888318318859966 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Financeiro Basico | score: 0.6602684278515575 | fonte: `data/knowledge_base/financeiro_basico.md`

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

### 7. Gastos pequenos

**Pergunta:** gasto muito com pequenas compras, como posso organizar?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 10/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, tema_correto, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.7067015603385549 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6972376313889488 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.6777007932644881 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

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

### 8. Parcelas

**Pergunta:** tenho muitas parcelas no cartão, por onde começo?

**Modo:** `rag_hibrido_pgvector_text_neon_rerank`

**Nota:** 9/10

**Status:** APROVADO

**Critérios atendidos:** usa_rag_hibrido, usa_rerank, fallback_rag_controlado, tem_fontes, seguranca_educativa, resposta_completa, pergunta_de_acao

**Fontes recuperadas:**

- Faq Financeiro Inna | score: 0.8057115493327506 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.7879543222181152 | fonte: `data/knowledge_base/faq_financeiro_inna.md`
- Faq Financeiro Inna | score: 0.8240515497733375 | fonte: `data/knowledge_base/faq_financeiro_inna.md`

**Resposta gerada:**

> Com base na base de conhecimento da INNA, a orientação educativa é:
> 
> 1. Organize seus dados financeiros.
> 2. Compare renda, gastos, dívidas e reserva.
> 3. Priorize ações simples e mensuráveis.
> 4. Evite decisões financeiras arriscadas sem orientação profissional.
> 
> Quer que eu monte uma meta simples para esta semana?

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
