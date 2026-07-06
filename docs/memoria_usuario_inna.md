# Fase 5.15 — Memória por Usuário da INNA

## 1. Objetivo

A Fase 5.15 documenta a evolução da **INNA Financial Coach AI** para trabalhar com memória simples por usuário.

O objetivo é permitir que a INNA acompanhe o histórico financeiro básico informado pelo usuário, sem precisar que ele repita tudo em cada nova conversa.

Essa memória deve ser usada de forma educativa, segura e limitada, ajudando a personalizar diagnósticos, metas e orientações financeiras.

---

## 2. Por que memória por usuário é importante

Sem memória, cada conversa começa do zero.

Com memória, a INNA pode lembrar informações básicas já fornecidas, como:

- renda informada;
- gastos mensais;
- valor que o usuário consegue guardar;
- existência de dívidas;
- uso de cartão de crédito;
- preferência de idioma;
- moeda utilizada;
- último diagnóstico;
- última meta sugerida.

Isso torna a experiência mais útil, porque a INNA consegue continuar a orientação a partir do histórico do usuário.

---

## 3. Exemplo prático

Primeira conversa:

> Ganho R$ 3.000, gasto R$ 2.500 e consigo guardar R$ 100.

A INNA pode gerar um diagnóstico e salvar um resumo simples:

```text
renda = 3000
gastos = 2500
valor_para_guardar = 100
moeda = BRL
idioma = pt
```
