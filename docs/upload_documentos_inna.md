# Fase 5.14 — Upload de Documentos da INNA

## 1. Objetivo

A Fase 5.14 documenta a evolução da **INNA Financial Coach AI** para permitir upload de novos documentos na base de conhecimento.

O objetivo é transformar a INNA em uma assistente com base de conhecimento expansível, permitindo adicionar novos conteúdos sobre educação financeira, Pix, fraude, golpes, dívidas, cartão de crédito e organização financeira.

Essa fase prepara o projeto para crescer de forma mais profissional, permitindo que novos materiais sejam adicionados ao RAG sem depender de alterações manuais no código principal.

---

## 2. Por que upload de documentos é importante

Atualmente, a INNA utiliza arquivos de conhecimento já existentes no projeto.

Com a funcionalidade de upload de documentos, será possível adicionar novos conteúdos de forma mais flexível, mantendo a base de conhecimento sempre atualizada.

Exemplos de documentos que podem ser adicionados:

- PDFs educativos;
- arquivos Markdown;
- arquivos TXT;
- cartilhas sobre Pix;
- orientações sobre golpes financeiros;
- conteúdos de educação financeira;
- materiais internos de treinamento;
- FAQs atualizadas;
- guias de prevenção contra fraudes;
- materiais sobre organização de gastos, dívidas e cartão de crédito.

Essa funcionalidade aproxima a INNA de uma solução real de IA com base de conhecimento dinâmica.

---

## 3. Fluxo planejado

O fluxo de upload de documentos funciona assim:

1. O administrador envia um documento.
2. O sistema identifica o tipo do arquivo.
3. O conteúdo textual é extraído.
4. O texto é dividido em chunks menores.
5. Cada chunk recebe metadados.
6. O sistema gera embeddings para cada chunk.
7. Os chunks são salvos no PostgreSQL/Neon.
8. O RAG passa a recuperar esses novos conteúdos.
9. O dashboard pode exibir documentos carregados, fontes usadas e status da ingestão.

Esse fluxo permite que a INNA aprenda novos conteúdos a partir de documentos controlados e organizados.

---

## 4. Tipos de arquivos planejados

| Tipo | Uso |
|---|---|
| `.pdf` | Cartilhas, materiais educativos e documentos externos |
| `.md` | Base de conhecimento escrita em Markdown |
| `.txt` | Conteúdos simples e FAQs |
| `.csv` | Perguntas e respostas estruturadas |
| `.json` | Conteúdos estruturados para ingestão futura |

Inicialmente, os formatos mais importantes são `.md`, `.txt` e `.pdf`.

---

## 5. Estrutura de dados esperada

Cada documento enviado pode gerar vários chunks.

Cada chunk salvo na base pode conter:

| Campo | Descrição |
|---|---|
| `id` | Identificador único do chunk |
| `documento_id` | Identificador do documento original |
| `titulo` | Título do documento |
| `fonte` | Caminho ou origem do arquivo |
| `conteudo` | Texto do chunk |
| `embedding` | Vetor semântico gerado |
| `categoria` | Tema do conteúdo |
| `idioma` | Idioma do documento |
| `data_upload` | Data de envio |
| `ativo` | Indica se o chunk pode ser usado pelo RAG |

Essa estrutura ajuda a manter rastreabilidade entre o documento original e os trechos usados pela INNA.

---

## 6. Exemplo de tabela planejada

```sql
CREATE TABLE IF NOT EXISTS documentos_rag (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    fonte TEXT,
    categoria TEXT,
    idioma TEXT DEFAULT 'pt',
    data_upload TIMESTAMP DEFAULT NOW(),
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS chunks_rag (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER REFERENCES documentos_rag(id),
    conteudo TEXT NOT NULL,
    embedding vector,
    categoria TEXT,
    idioma TEXT DEFAULT 'pt',
    data_criacao TIMESTAMP DEFAULT NOW(),
    ativo BOOLEAN DEFAULT TRUE
);
```
