# Decisões de arquitetura

Resumo das decisões fechadas na fase de planejamento com a cliente/dev, para consulta rápida sem
precisar reconstruir o raciocínio a cada mudança.

## Canais de venda
Só Mercado Livre implementado no MVP. O schema já é genérico (`orders.canal`,
`product_channel_mapping.canal`) para permitir outros canais (Shopee, site próprio) no futuro sem
migração destrutiva — mas nenhuma lógica de integração além de ML existe hoje.

## Multiusuário
A cliente pode ter funcionário operando o sistema desde o MVP. Roles `admin`/`operador` são reais
(não só um campo preparado): only admin cria/gerencia usuários e conecta a conta do ML.

## Sincronização de pedidos: webhook, não polling
O Mercado Livre envia notificações via webhook (`POST /webhooks/mercadolivre`). O endpoint responde
200 imediatamente (requisito do ML — ele desativa o webhook após falhas repetidas) e delega o
processamento pesado para uma `BackgroundTask` do FastAPI. Idempotência é garantida por
`webhook_events` com `UNIQUE(tenant_id, ml_notification_id)` — reentregas do ML não duplicam efeito.

## Fila assíncrona: adiada
Decisão deliberada de **não** usar Celery/Redis no MVP. Volume esperado (20-100 pedidos/dia) não
justifica a complexidade operacional extra dentro do prazo de 1-2 meses com um único dev.
`BackgroundTasks` nativo cobre o caso de uso; o risco de perda em crash do processo é mitigado por
`webhook_events` permanecer com status `recebido`/`erro` até ser processado, permitindo
reprocessamento manual via `POST /admin/webhooks/reprocess`.

**Gatilho para migrar**: multi-tenant real (múltiplos vendedores) ou volume > 500-1000 eventos/dia.
A lógica já está isolada em `app/services/mercadolivre/webhook.py::processar_evento(webhook_event_id)`
— trocar por `celery_task.delay(webhook_event_id)` é uma mudança pequena e localizada.

## Geração de etiqueta + baixa de estoque
Ordem deliberada: (1) validar pré-condições (produto vinculado, shipment existe), (2) chamar a API
do ML para baixar a etiqueta — rede, **fora** de qualquer transação de banco —, (3) só então abrir
uma transação curta e local para gravar a baixa de estoque e atualizar o pedido. Se a chamada ao ML
falhar, nada é persistido. Ver `app/services/mercadolivre/labels.py`.

## Estoque nunca fica negativo
Toda alteração de estoque passa por `app/services/stock/movements.py`, que trava a linha do produto
(`SELECT ... FOR UPDATE`) durante a operação e grava o movimento + atualiza o cache
`products.estoque_atual` na mesma transação. O `CHECK (estoque_atual >= 0)` no banco é a rede de
segurança adicional.

## Tokens do Mercado Livre
Criptografados em repouso (`cryptography.fernet`, chave em `ML_TOKEN_ENCRYPTION_KEY`). Renovação
automática usa lock de linha (`SELECT ... FOR UPDATE` em `ml_credentials`) para que duas requisições
concorrentes não tentem renovar o mesmo `refresh_token` (o ML invalida o antigo ao emitir um novo).

## Explicitamente fora do MVP
- Impressora térmica (driver/protocolo direto) — MVP só gera/baixa PDF, impressão é manual.
- Nota fiscal eletrônica (NF-e).
- Canais de venda além do Mercado Livre (schema preparado, lógica não implementada).
- Multi-tenant self-service (tabelas já carregam `tenant_id`, mas hoje há 1 tenant fixo via seed).
- Cobrança/assinatura (Stripe ou similar).
- App mobile.
