# INNA Security and Compliance Pipeline

## Objetivo

O pipeline `INNA Security and Compliance Validation` implementa
controles automatizados de segurança, governança e produção de
evidências para os workflows e dependências da INNA.

## Controles implementados

### GitHub Actions

- validação sintática com actionlint;
- verificação de permissões mínimas;
- exigência de timeout;
- exigência de política de concorrência;
- bloqueio de `pull_request_target`;
- allowlist de Actions externas;
- identificação de Actions ainda não fixadas por SHA;
- detecção básica de credenciais em arquivos YAML.

### Dependências Python

- auditoria contra vulnerabilidades conhecidas;
- saída JSON estruturada;
- geração de SBOM CycloneDX;
- bloqueio do pipeline quando vulnerabilidades são encontradas.

### Secrets

- varredura do repositório e do histórico Git;
- mascaramento dos valores encontrados;
- produção de relatório JSON;
- bloqueio em caso de credencial versionada.

## Evidências

Os artefatos são mantidos por 30 dias:

- `actionlint.jsonl`;
- `workflow-policy-report.json`;
- `pip-audit.json`;
- `python-sbom.cdx.json`;
- `gitleaks-report.json`.

## Limites

Este pipeline apoia controles técnicos e auditoria, mas não constitui
certificação ISO. Certificação exige escopo formal, políticas,
responsabilidades, gestão de riscos, auditoria e avaliação por
organismo competente.

## Próxima evolução

- fixar todas as Actions por SHA completo;
- ativar Dependabot para Actions e pip;
- adicionar CodeQL;
- adicionar política de exceções para vulnerabilidades;
- proteger a branch `main` com checks obrigatórios;
- configurar revisão obrigatória dos environments reais.
