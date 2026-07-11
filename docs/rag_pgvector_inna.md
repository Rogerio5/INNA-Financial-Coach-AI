# RAG com pgvector, Gemini Embeddings e Documentos Ativos

**Projeto:** INNA Financial Coach AI

---

# 1. Introdução

A INNA Financial Coach AI utiliza uma arquitetura **Retrieval-Augmented Generation (RAG)** para ampliar o conhecimento da Inteligência Artificial utilizando documentos enviados pelo usuário.

Ao invés de depender somente do conhecimento do modelo de linguagem, a INNA consulta uma base própria de documentos vetorizados antes de gerar cada resposta.

Dessa forma, a IA consegue responder utilizando informações específicas da empresa, manuais, políticas, documentos técnicos ou qualquer conteúdo enviado pelo usuário.

---

# 2. Objetivos

A arquitetura RAG foi construída para permitir:

- Upload de documentos pelo usuário
- Processamento automático do conteúdo
- Divisão inteligente em chunks
- Geração de embeddings utilizando Gemini
- Armazenamento vetorial com pgvector
- Busca semântica
- Priorização por categoria
- Controle de documentos ativos e inativos
- Geração de respostas utilizando contexto real

---

# 3. Arquitetura Geral

A arquitetura funciona em várias etapas.

```
Documento
      │
      ▼
Upload
      │
      ▼
Limpeza do texto
      │
      ▼
Divisão em Chunks
      │
      ▼
Arquivo JSONL
      │
      ▼
Embeddings Gemini
      │
      ▼
pgvector (Neon PostgreSQL)
      │
      ▼
Busca Semântica
      │
      ▼
Categorias
      │
      ▼
Score RAG
      │
      ▼
Resposta Final da INNA
```

---

# 4. Fluxo Completo

O fluxo executado pela aplicação é:

```
Upload
↓

Salvar documento

↓

Limpeza

↓

Chunking

↓

JSONL

↓

Metadata PostgreSQL

↓

Embeddings Gemini

↓

pgvector

↓

Busca Vetorial

↓

Categorias

↓

Resposta Final
```

Todo o processo é automático.

---

# 5. Estrutura de Pastas

A organização atual utilizada pelo projeto é:

```
data/

knowledge_base/

uploads/

chunks/

embedding_ready/

archive/

src/

dashboard.py

scripts/

docs/

rag_pgvector_inna.md
```

Cada pasta possui uma responsabilidade específica.

---

# 6. Upload de Documentos

O Dashboard possui uma área dedicada ao envio de documentos.

Atualmente são aceitos:

- Markdown (.md)
- Texto (.txt)

Quando o usuário realiza um upload, o documento é salvo em:

```
data/knowledge_base/uploads
```

Neste momento ainda não existe processamento vetorial.

O sistema apenas registra:

- nome original
- nome salvo
- tamanho
- extensão
- data
- status

Esses dados são enviados para o Neon PostgreSQL.

---

# 7. Registro do Documento

Após o upload é criado um registro na tabela:

```
documentos_upload_rag
```

Campos principais:

- id
- nome_original
- nome_salvo
- extensão
- tamanho
- quantidade de chunks
- status
- ativo
- origem
- caminho_upload
- caminho_chunks
- caminho_embedding_ready
- criado_em

Essa tabela controla toda a vida útil dos documentos.

---

# 8. Limpeza do Texto

Antes da divisão em chunks é realizada uma etapa de normalização.

São executadas diversas correções:

- remoção de tabs
- remoção de espaços duplicados
- padronização de quebras de linha
- remoção de linhas vazias repetidas
- preservação dos parágrafos
- preservação dos títulos

Isso melhora significativamente a qualidade dos embeddings.

---

# 9. Chunking

Após a limpeza, o documento é dividido em pequenos blocos chamados **Chunks**.

Cada chunk representa um pedaço do conhecimento.

Exemplo:

```
Documento

↓

Chunk 1

↓

Chunk 2

↓

Chunk 3

↓

Chunk 4
```

Cada chunk será transformado posteriormente em um embedding.

---

# 10. Chunking Inteligente

A divisão procura respeitar a estrutura do documento.

Por exemplo:

```
## Pix

↓

Chunk Pix

## Cartão

↓

Chunk Cartão

## Segurança

↓

Chunk Segurança
```

Isso reduz mistura de assuntos e melhora a recuperação semântica.

---

# 11. Benefícios do Chunking

As principais vantagens são:

- maior precisão
- menor custo
- recuperação mais rápida
- menos contexto irrelevante
- respostas mais específicas

O chunking é uma das etapas mais importantes do pipeline RAG.

---

# 12. Arquivo JSONL

Após gerar os chunks, a aplicação cria automaticamente um arquivo JSONL.

Esses arquivos ficam em:

```
data/knowledge_base/embedding_ready
```

Cada linha representa um chunk.

Exemplo:

```json
{
  "chunk_id":"pix_01",
  "texto":"Recebi um Pix estranho...",
  "categoria":"pix"
}
```

Esses arquivos são utilizados posteriormente na geração dos embeddings.

---

# 13. Situação Atual da Implementação

Até esta etapa o sistema já possui:

- Upload funcional
- Limpeza automática
- Chunking inteligente
- JSONL
- Registro no Neon PostgreSQL
- Dashboard de acompanhamento
- Organização automática dos arquivos locais

Essas etapas formam a base do pipeline RAG.

---

# 14. Geração de Embeddings

Depois que o documento foi dividido em chunks, cada chunk é convertido em um **embedding**, ou seja, uma representação numérica do seu significado semântico.

Ao contrário de uma simples busca por palavras, os embeddings permitem que a IA compreenda o contexto do texto.

Fluxo:

```text
Chunk de texto
        ↓
Gemini Embedding
        ↓
Vetor Numérico
        ↓
Armazenamento no pgvector
```

Cada chunk gera exatamente um embedding.

Exemplos:

| Documento | Chunks | Embeddings |
|-----------|--------|------------|
| Documento pequeno | 1 | 1 |
| Documento médio | 5 | 5 |
| Documento grande | 20 | 20 |

Portanto, a quantidade de embeddings depende diretamente da quantidade de chunks gerados.

---

# 15. Modelo de Embedding Utilizado

O projeto utiliza o modelo oficial da API Gemini:

```text
models/gemini-embedding-001
```

Esse modelo foi escolhido por oferecer:

- alta qualidade semântica;
- boa capacidade de compreensão do português;
- integração oficial com a API Gemini;
- ótima precisão para sistemas RAG.

---

# 16. Dimensão dos Vetores

Cada embedding possui:

```text
3072 dimensões
```

Na prática significa que um único chunk é transformado em um vetor semelhante a:

```text
[0.182,
-0.417,
0.093,
...
3072 valores]
```

Esses números representam matematicamente o significado do texto.

---

# 17. Por que utilizar 3072 dimensões?

Vetores maiores conseguem representar muito melhor pequenas diferenças de contexto.

Exemplo:

```
Pix

Pix suspeito

Transferência bancária

TED

Cartão de crédito
```

Embora alguns desses textos compartilhem palavras parecidas, os embeddings conseguem diferenciar seus significados.

Isso melhora muito a precisão da busca.

---

# 18. Armazenamento no pgvector

Após gerar o embedding, ele é armazenado no PostgreSQL utilizando a extensão pgvector.

Tabela utilizada:

```text
chunks_embeddings_rag
```

Cada registro representa um único chunk vetorizado.

---

# 19. Estrutura da Tabela

A tabela contém informações suficientes para reconstruir completamente um documento.

Principais campos:

- id
- documento_id
- chunk_id
- documento_origem
- chunk_index
- texto
- metadata
- embedding
- modelo_embedding
- criado_em

Relacionamento:

```text
chunks_embeddings_rag.documento_id

↓

documentos_upload_rag.id
```

Assim cada embedding sabe exatamente de qual documento foi originado.

---

# 20. Metadata do Chunk

Além do vetor, também são armazenados diversos metadados importantes.

Exemplo:

```json
{
  "categoria": "pix",
  "origem": "upload_usuario",
  "idioma": "pt",
  "tipo": "documento_upload"
}
```

Esses metadados são utilizados posteriormente durante a busca e na geração da resposta.

---

# 21. Índices do Banco

Para acelerar consultas foram criados índices tradicionais:

- documento_id
- chunk_id

Além disso existe um índice vetorial específico para embeddings.

---

# 22. Índice Vetorial HNSW

Como os embeddings possuem 3072 dimensões, foi utilizado o índice:

```text
HNSW
```

convertendo o vetor para:

```text
halfvec(3072)
```

Esse índice reduz drasticamente o tempo de busca.

Sem índice:

```
Busca Linear
```

Com índice:

```
Busca Aproximada HNSW
```

Permitindo crescimento da base sem perda significativa de desempenho.

---

# 23. Busca Semântica

Quando o usuário realiza uma pergunta, o fluxo ocorre da seguinte forma:

```text
Pergunta

↓

Embedding da pergunta

↓

Comparação com todos os embeddings

↓

Ordenação por similaridade

↓

Retorno dos melhores chunks
```

Todo esse processo acontece automaticamente.

---

# 24. Similaridade Vetorial

A busca utiliza distância vetorial baseada em similaridade.

Interpretação:

- distância menor → textos mais parecidos;
- distância maior → textos menos relacionados.

O dashboard também converte essa distância para uma similaridade aproximada apenas para facilitar a interpretação visual.

---

# 25. Quantidade de Chunks Recuperados

A INNA permite diferentes estratégias de recuperação.

Exemplos:

```text
3 chunks

5 chunks

8 chunks

10 chunks
```

Também existe um modo automático.

Nesse modo o sistema analisa a pergunta e escolhe quantos chunks utilizar.

Perguntas simples normalmente utilizam poucos chunks.

Perguntas mais complexas utilizam uma quantidade maior de contexto.

---

# 26. Busca Inteligente

A recuperação não depende apenas de palavras iguais.

Perguntas como:

```
Recebi um Pix estranho.
```

podem localizar chunks contendo:

```
transferência suspeita

golpe

aplicativo oficial

segurança
```

Mesmo que as palavras utilizadas sejam diferentes.

Essa é uma das maiores vantagens da busca vetorial.

---

# 27. Benefícios da Busca Semântica

Em comparação com buscas tradicionais por palavra-chave, a busca vetorial oferece:

- compreensão de contexto;
- identificação de sinônimos;
- recuperação de assuntos relacionados;
- redução de falsos negativos;
- respostas mais naturais;
- melhor qualidade no RAG.

Essas características tornam a experiência do usuário muito superior.

---

# 28. Situação Atual da Implementação

Ao final desta etapa, a arquitetura da INNA já possui:

- geração automática de embeddings;
- utilização do Gemini Embedding;
- vetores com 3072 dimensões;
- armazenamento no pgvector;
- índice HNSW;
- consulta vetorial;
- cálculo de similaridade;
- recuperação dos melhores chunks;
- integração completa com o banco Neon PostgreSQL.

Essa etapa representa o núcleo técnico da recuperação de conhecimento da INNA.

---

# 29. Categorias Automáticas dos Chunks

Após a geração dos chunks, cada um deles passa por uma etapa de classificação automática.

O objetivo dessa classificação é identificar o assunto predominante daquele trecho do documento.

Essa informação é armazenada no campo `categoria` dentro do metadata do chunk e posteriormente utilizada pela busca RAG.

Atualmente, a INNA identifica automaticamente as seguintes categorias:

- pix
- cartao_credito
- organizacao_financeira
- reserva_financeira
- seguranca
- dividas
- geral

Exemplo:

```text
Chunk

↓

"Recebi um Pix estranho..."

↓

Categoria = pix
```

Outro exemplo:

```text
Chunk

↓

"Meu cartão está comprometendo toda minha renda."

↓

Categoria = cartao_credito
```

Essa classificação acontece automaticamente durante o processamento do documento.

---

# 30. Metadata Inteligente

Além do texto e do embedding, cada chunk armazena informações adicionais.

Exemplo simplificado:

```json
{
    "categoria":"pix",
    "origem":"upload_usuario",
    "tipo":"documento_upload",
    "idioma":"pt",
    "documento_origem":"guia_pix.md"
}
```

Esses metadados tornam a recuperação de contexto muito mais eficiente.

---

# 31. Inferência da Categoria da Pergunta

Quando o usuário faz uma pergunta, a INNA também tenta identificar automaticamente o assunto principal.

Exemplo:

Pergunta:

```text
Recebi um Pix estranho, devo devolver?
```

Categorias inferidas:

```text
pix

seguranca
```

Outro exemplo:

Pergunta:

```text
Meu cartão está apertando.
```

Categorias inferidas:

```text
cartao_credito

organizacao_financeira

dividas
```

Essa etapa acontece antes da busca vetorial.

---

# 32. Priorização Inteligente

Depois de recuperar os chunks semanticamente mais próximos, a INNA realiza uma segunda análise.

Ela verifica se a categoria do chunk coincide com a categoria inferida da pergunta.

Exemplo:

Pergunta:

```text
Recebi um Pix estranho
```

Resultado inicial:

```
Chunk Pix

Chunk Cartão

Chunk Reserva
```

Após a priorização:

```
Chunk Pix

Chunk Segurança

Chunk Cartão
```

Ou seja, a IA reorganiza os resultados antes de montar o contexto.

---

# 33. Score RAG

O sistema não utiliza apenas a similaridade vetorial.

Foi criado um Score RAG que considera dois fatores:

- similaridade vetorial;
- prioridade da categoria.

Representação simplificada:

```text
Score RAG

=

Similaridade

+

Bônus da Categoria
```

Isso melhora significativamente a qualidade dos resultados recuperados.

---

# 34. Benefícios do Score

Sem Score RAG:

```
Apenas Similaridade
```

Com Score RAG:

```
Similaridade

+

Categoria

+

Contexto
```

Na prática, perguntas sobre Pix deixam de retornar chunks de cartão quando existem chunks muito mais adequados.

---

# 35. Documentos Ativos

Nem todo documento enviado deve participar das respostas.

Por esse motivo foi criado o conceito de documento ativo.

Documento ativo significa:

- participa da busca semântica;
- pode aparecer na resposta;
- entra na geração do contexto.

---

# 36. Documentos Inativos

Documentos antigos podem permanecer armazenados no banco sem serem utilizados.

Documento inativo:

- continua salvo;
- mantém seus embeddings;
- não participa das buscas;
- pode ser reativado futuramente.

Nenhuma informação é perdida.

---

# 37. Controle pelo Dashboard

O Dashboard permite alterar o estado do documento.

Opções disponíveis:

```
Ativar Documento

Desativar Documento
```

Toda alteração é refletida imediatamente na busca RAG.

---

# 38. Filtragem dos Documentos

Durante a busca semântica somente documentos ativos são considerados.

Fluxo:

```text
Pergunta

↓

Busca Vetorial

↓

Filtrar documentos ativos

↓

Ordenar resultados

↓

Montar contexto
```

Isso evita que documentos antigos ou de teste influenciem as respostas.

---

# 39. Resposta Final da INNA

Depois da recuperação dos melhores chunks, a aplicação monta automaticamente um contexto.

Exemplo:

```
Pergunta

+

Chunk 1

+

Chunk 2

+

Chunk 3
```

Esse contexto é enviado ao modelo Gemini.

O modelo utiliza exclusivamente esse material como base para construir a resposta.

---

# 40. Regras da Resposta

Antes de enviar o prompt ao Gemini, a INNA adiciona diversas regras de segurança.

Entre elas:

- utilizar linguagem simples;
- responder de forma educativa;
- evitar recomendações financeiras específicas;
- não solicitar senhas;
- não solicitar token;
- não solicitar código de segurança;
- orientar utilização do aplicativo oficial do banco;
- recomendar canais oficiais quando necessário.

Essas regras tornam a IA mais segura e adequada ao contexto financeiro.

---

# 41. Fontes Utilizadas

Ao final da resposta, a aplicação apresenta as fontes utilizadas.

Exemplo:

```
Documento:

guia_pix.md

Chunk:

2

Categoria:

pix

Similaridade:

0.84
```

Isso aumenta a transparência da resposta e permite auditoria do conteúdo utilizado.

---

# 42. Benefícios da Arquitetura Atual

A implementação atual oferece:

- busca semântica vetorial;
- categorias automáticas;
- score inteligente;
- controle de documentos ativos;
- recuperação contextual;
- respostas fundamentadas em documentos reais;
- transparência das fontes;
- arquitetura preparada para expansão.

Essa combinação transforma a INNA em uma plataforma RAG robusta, escalável e preparada para bases documentais cada vez maiores.

---

# 43. Dashboard de Gerenciamento RAG

A INNA possui um Dashboard dedicado para administração completa da base de conhecimento.

O objetivo é permitir que todo o fluxo RAG seja acompanhado visualmente, sem necessidade de executar comandos diretamente no banco de dados.

Atualmente o Dashboard permite:

- upload de documentos;
- visualização dos documentos cadastrados;
- reprocessamento de documentos;
- geração de embeddings;
- otimização do pgvector;
- busca semântica;
- geração da resposta final;
- gerenciamento de documentos ativos e inativos;
- organização dos arquivos locais.

Todo esse processo é executado através da interface Streamlit.

---

# 44. Observabilidade da Base RAG

O Dashboard apresenta indicadores importantes para acompanhamento da base.

Entre eles:

- quantidade de documentos cadastrados;
- quantidade total de chunks;
- quantidade de embeddings;
- documentos ativos;
- documentos inativos;
- embeddings ativos;
- embeddings inativos.

Esses indicadores permitem acompanhar a evolução da base de conhecimento e identificar possíveis inconsistências.

---

# 45. Processo de Reprocessamento

Sempre que um documento é alterado, a INNA permite realizar o reprocessamento.

O fluxo é:

```text
Documento

↓

Nova limpeza

↓

Novos chunks

↓

Novo JSONL

↓

Novos embeddings

↓

Atualização no pgvector
```

O reprocessamento garante que a base permaneça sincronizada com a versão mais recente do documento.

---

# 46. Reprocessamento de Embeddings

Caso um documento já possua embeddings, o Dashboard oferece a opção de forçar um novo processamento.

Quando essa opção é utilizada:

- os embeddings antigos são removidos;
- novos embeddings são gerados;
- o banco permanece consistente.

Essa abordagem evita duplicidade de vetores.

---

# 47. Otimização do pgvector

Após a geração dos embeddings, o Dashboard permite validar e criar automaticamente os índices necessários.

Entre eles:

- índice HNSW;
- índice por documento;
- índice por chunk.

Essa etapa melhora significativamente o desempenho das consultas vetoriais.

---

# 48. Busca Semântica

O Dashboard permite testar a busca vetorial antes da geração da resposta final.

Fluxo:

```text
Pergunta

↓

Embedding

↓

Busca pgvector

↓

Ranking

↓

Chunks encontrados
```

O usuário pode visualizar exatamente quais chunks foram recuperados.

---

# 49. Resposta Final

Após validar os chunks recuperados, o Dashboard permite gerar a resposta final da INNA.

Fluxo:

```text
Pergunta

↓

Chunks Recuperados

↓

Contexto

↓

Gemini

↓

Resposta
```

A resposta sempre apresenta as fontes utilizadas.

---

# 50. Organização Local dos Arquivos

Além do banco de dados, a aplicação organiza automaticamente os arquivos locais.

Pastas utilizadas:

```text
uploads/

chunks/

embedding_ready/

archive/
```

Arquivos antigos podem ser movidos para a pasta de arquivamento.

Nenhum documento é excluído automaticamente.

---

# 51. Arquivamento

Para evitar acúmulo de arquivos, o Dashboard permite arquivar automaticamente os documentos mais antigos.

O usuário define quantos arquivos recentes deseja manter.

Exemplo:

```text
Manter:

5 arquivos

↓

Arquivar os demais
```

Os arquivos são movidos para:

```text
data/knowledge_base/archive
```

Essa estratégia mantém o projeto organizado sem perda de informações.

---

# 52. Segurança

Durante toda a implementação foram adotadas boas práticas de segurança.

Entre elas:

- utilização de variáveis de ambiente;
- armazenamento seguro da DATABASE_URL;
- utilização de API Key fora do código;
- controle de documentos ativos;
- prevenção de duplicidade de embeddings;
- isolamento entre documentos.

Essas práticas facilitam futuras implantações em produção.

---

# 53. Testes Realizados

Durante o desenvolvimento foram realizados diversos testes.

Entre eles:

- upload de documentos;
- geração de chunks;
- criação do JSONL;
- geração de embeddings;
- gravação no pgvector;
- busca semântica;
- priorização por categoria;
- documentos ativos;
- documentos inativos;
- resposta final da INNA.

Todos os testes foram validados com sucesso.

---

# 54. Estado Atual do Projeto

Ao final desta etapa, a arquitetura RAG da INNA contempla:

- Upload de documentos
- Limpeza de texto
- Chunking inteligente
- JSONL para embeddings
- Metadata no PostgreSQL
- Embeddings Gemini
- pgvector
- Índice HNSW
- Busca semântica
- Categorias automáticas
- Score RAG
- Documentos ativos e inativos
- Dashboard administrativo
- Organização local dos arquivos
- Resposta final baseada em contexto

Essa arquitetura fornece uma base sólida para evolução futura do projeto.

---

# 55. Arquitetura Completa da INNA

A arquitetura da INNA foi projetada utilizando componentes independentes que trabalham de forma integrada.

Visão geral:

```text
                 Usuário
                    │
                    ▼
          Interface Streamlit
                    │
                    ▼
      Dashboard Administrativo
                    │
      ┌─────────────┴─────────────┐
      │                           │
      ▼                           ▼
 Upload de Arquivos          Chat da INNA
      │                           │
      ▼                           ▼
 Processamento              Pergunta do Usuário
      │                           │
      ▼                           ▼
 Chunking                 Embedding da Pergunta
      │                           │
      ▼                           ▼
 JSONL                 Busca Semântica pgvector
      │                           │
      ▼                           ▼
 Embeddings Gemini       Recuperação dos Chunks
      │                           │
      └─────────────┬─────────────┘
                    ▼
              Contexto Final
                    │
                    ▼
            Gemini Generate Content
                    │
                    ▼
            Resposta da INNA
```

---

# 56. Componentes da Arquitetura

Atualmente o projeto é composto pelos seguintes módulos:

## Interface

- Streamlit

Responsável por:

- Dashboard
- Upload
- Busca
- Administração
- Visualização

---

## Banco de Dados

Neon PostgreSQL

Responsável por:

- documentos
- embeddings
- metadata
- controle de documentos

---

## Busca Vetorial

pgvector

Responsável por:

- armazenamento vetorial
- cálculo de similaridade
- busca semântica

---

## Inteligência Artificial

Google Gemini

Responsável por:

- geração de embeddings
- geração da resposta final

---

# 57. Fluxo Completo da Pergunta

Quando um usuário faz uma pergunta, o fluxo completo é:

```text
Usuário

↓

Pergunta

↓

Embedding da Pergunta

↓

Busca Vetorial

↓

Ranking

↓

Categorias

↓

Score RAG

↓

Contexto

↓

Gemini

↓

Resposta

↓

Fontes Utilizadas
```

Todo esse processo acontece automaticamente.

---

# 58. Fluxo Completo do Upload

Quando um documento é enviado:

```text
Upload

↓

Salvar Arquivo

↓

Limpeza

↓

Chunking

↓

JSONL

↓

Metadata PostgreSQL

↓

Embeddings

↓

pgvector

↓

Documento Disponível para Busca
```

Após essa etapa o conhecimento já pode ser utilizado pela IA.

---

# 59. Organização da Base de Conhecimento

A base RAG foi organizada para permitir crescimento contínuo.

Cada documento possui:

- metadata
- chunks
- embeddings
- categoria
- status
- origem

Isso facilita futuras expansões da arquitetura.

---

# 60. Escalabilidade

A arquitetura foi construída pensando em crescimento.

Ela suporta:

- milhares de documentos;
- milhares de embeddings;
- novos tipos de arquivos;
- novas categorias;
- novos modelos de IA;
- novas estratégias de recuperação.

O uso do pgvector permite que a busca continue eficiente mesmo com uma base muito maior.

---

# 61. Melhorias Futuras

Entre as melhorias planejadas estão:

## Novos formatos

- PDF
- DOCX
- XLSX
- CSV
- HTML

---

## OCR

Leitura automática de imagens.

Exemplos:

- comprovantes
- extratos
- documentos digitalizados

---

## Busca Híbrida

Combinação de:

- busca textual;
- busca vetorial.

Isso melhora ainda mais a recuperação de contexto.

---

## Re-ranking

Após recuperar vários chunks, um modelo adicional poderá reorganizar os resultados antes da resposta.

Essa técnica aumenta ainda mais a precisão.

---

## Multimodal

Permitir que documentos com imagens também sejam compreendidos pela IA.

---

## Memória Conversacional

Permitir que a INNA utilize o histórico das conversas para melhorar as respostas.

---

## Avaliação Automática

Criar métricas como:

- precisão;
- recall;
- relevância;
- cobertura.

Esses indicadores permitirão acompanhar a qualidade do sistema RAG.

---

# 62. Benefícios da Arquitetura

A implementação atual oferece diversas vantagens.

Entre elas:

- escalabilidade;
- manutenção simples;
- separação de responsabilidades;
- fácil evolução;
- alta qualidade das respostas;
- transparência das fontes;
- organização dos documentos;
- recuperação semântica eficiente.

---

# 63. Lições Aprendidas

Durante o desenvolvimento foram aprendidos diversos conceitos importantes.

Entre eles:

- Engenharia de Prompt;
- Embeddings;
- Chunking;
- Busca Vetorial;
- pgvector;
- PostgreSQL;
- Streamlit;
- Google Gemini;
- Organização de bases RAG;
- Recuperação Semântica;
- Engenharia de Software aplicada à IA.

Esses conhecimentos servem como base para projetos mais complexos.

---

# 64. Roadmap

Próximas evoluções planejadas:

- Multiagentes
- Agentes Financeiros
- Memória Persistente
- Avaliação automática do RAG
- RAG híbrido
- Dashboard analítico
- API REST
- Autenticação de usuários
- Controle de permissões
- Integração com n8n
- Integração com WhatsApp
- Integração com Telegram
- Integração com Gmail
- Integração com calendário
- Pipeline ETL automático
- Versionamento da Base de Conhecimento

---

# 65. Conclusão

A arquitetura RAG desenvolvida para a INNA Financial Coach AI representa uma base sólida para aplicações de Inteligência Artificial Generativa voltadas ao domínio financeiro.

O projeto integra processamento de documentos, geração de embeddings com Gemini, armazenamento vetorial utilizando pgvector no PostgreSQL, busca semântica, categorização automática, controle de documentos ativos e geração de respostas fundamentadas em contexto.

A solução foi construída com foco em escalabilidade, organização e facilidade de manutenção, permitindo que novas funcionalidades sejam adicionadas sem comprometer a arquitetura existente.

Além de servir como base para a evolução da INNA, este projeto demonstra na prática a aplicação de conceitos modernos de Engenharia de IA, RAG (Retrieval-Augmented Generation), bancos vetoriais, processamento de linguagem natural e desenvolvimento de software.

---

# Autores

**Rogério Augusto Sabino**
**Ronaldo Augusto Sabino**

Projeto desenvolvido como parte da evolução da plataforma **INNA Financial Coach AI**, com foco em Inteligência Artificial Generativa, Engenharia de Software, RAG, Bancos Vetoriais e Sistemas Inteligentes.