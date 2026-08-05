# Base profissional da INNA — versão 2.0.0

Este pacote contém arquivos reais em Markdown, não um script PowerShell.

## Conteúdo

- `EDUCADORA_FINANCEIRA_PROFISSIONAL.md`: arquivo completo e consolidado da Educadora Financeira.
- `SEGURANCA_FINANCEIRA_PROFISSIONAL.md`: arquivo completo e consolidado de Segurança Financeira.
- `educadora_financeira/`: 8 documentos temáticos prontos para chunking.
- `seguranca_financeira/`: 8 documentos temáticos prontos para chunking.
- `prompts/`: prompts profissionais dos dois agentes.
- `manifest.json`: catálogo dos documentos.
- `governanca/source_registry.json`: fontes oficiais usadas.

## Melhorias aplicadas

- separação clara entre Educação Financeira e Segurança Financeira;
- respostas diretas para as cinco perguntas oficiais;
- cobertura de priorização de dívidas, phishing e fraude com cartão;
- metadados para RAG, versionamento e rastreabilidade;
- regras de abstenção, privacidade e encaminhamento;
- deduplicação por tópico e propósito;
- referências oficiais do Banco Central, CVM, ANPD e CERT.br.

## Próximo uso no projeto

Revise os arquivos localmente antes de ingestão. Depois, execute chunking, deduplicação, geração de embeddings e cadastro no Neon em uma etapa controlada. Os arquivos antigos duplicados não devem ser removidos antes de backup e validação.
