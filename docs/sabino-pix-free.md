# Publicação inicial gratuita — gateway Sabino.AI

Branch: deploy/sabino-pix-free. Esta branch adiciona a plataforma local à base atual
origin/main sem alterar os serviços antigos. O primeiro deploy é de validação,
com emissão Pix e análise paga desativadas.

Render: nome inna-sabino-plataforma-pix, Python 3, plano Free, região Virginia,
Root Directory vazio. Build: pip install -r requirements.txt -r requirements-pix.txt
Start: python -m uvicorn src.inna_platform.app:app --host 0.0.0.0 --port $PORT
Health check: /health. Desativar deploy automático durante a validação.

Variáveis: DATABASE_URL (segredo do Neon), INNA_API_BASE_URL (URL do backend),
INNA_AUTH_COOKIE_SECURE=true, INNA_CREDITS_ENABLED=false,
INNA_PAID_ANALYSIS_TIMEOUT_SECONDS=135.

Os arquivos de configuração Pix e análises desta branch estão desativados.
A chave pessoal do recebedor não foi copiada. Configurar o recebedor de forma
segura antes de ativar Pix; INNA_CREDITS_ENABLED sozinho não ativa esse arquivo.
Não enviar segredos, .env, backups ou comprovantes locais ao GitHub.

Validação: importação do gateway e 19 testes unitários de carteira/Pix passaram.
Build Linux, memória de 512 MB, conexão Neon, schemas, login HTTPS, autorização
administrativa e comunicação com /rag/ask ainda exigem validação no destino.
O /health atual somente confirma o processo, não o banco.

Antes de receber pagamentos: confirmar o banco de destino, backup recuperável,
schemas de identidade/planos e as cinco migrações de créditos/Pix/análises.
O instalador --create-admin pressupõe que inna_auth_users já exista.
Dados locais, saldos e histórico não são transferidos por este commit.
A aprovação Pix permanece manual após conferência do extrato.

Foram excluídos backups, PDF de comprovante local e cache de embeddings.
As demais páginas da plataforma incluem demonstrações preexistentes; a inclusão
não significa que todos os módulos estejam prontos para uso por clientes.

Somente recursos Free. Não criar discos, jobs ou planos pagos. Os serviços web
Free compartilham a franquia mensal do Render e podem dormir ou ser suspensos.
