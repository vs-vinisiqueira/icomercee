# Sistema DRI — Etiquetas Mercado Livre + Controle de Estoque

Sistema para uma vendedora do Mercado Livre: gera etiquetas de envio dos pedidos e controla
entrada/saída de estoque dos produtos revendidos, com baixa automática de estoque quando uma
etiqueta é gerada.

Stack: FastAPI + SQLAlchemy + Alembic + PostgreSQL no backend, React (Vite + TS) no frontend, JWT
para autenticação.

## Estrutura

```
backend/    API FastAPI (app/, alembic/, tests/, scripts/)
frontend/   SPA React (Vite + TypeScript)
docker-compose.yml   Postgres + API para desenvolvimento local
```

## Setup local (sem Docker)

### 1. Banco de dados

Suba um PostgreSQL local (ou use o `docker-compose.yml` só para o serviço `db`):

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate        # Windows (PowerShell: venv\Scripts\Activate.ps1)
pip install -r requirements.txt

cp .env.example .env
# edite backend/.env com os valores reais (ou copie o .env.example da raiz)
```

Gere uma chave de criptografia para os tokens do Mercado Livre e cole em `ML_TOKEN_ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Rode as migrations e crie o tenant + usuário admin inicial:

```bash
alembic upgrade head
python scripts/seed_admin.py --tenant "Nome da Loja" --nome "Fulana" --email fulana@exemplo.com --senha "senha-forte-123"
```

Suba a API:

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` (docs interativas em `/docs`).

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env    # VITE_API_URL=http://localhost:8000
npm run dev
```

Acesse `http://localhost:5173` e faça login com o usuário criado no seed.

## Setup via Docker Compose (backend + banco)

Na raiz do projeto:

```bash
cp .env.example .env    # edite os valores
docker compose up --build
```

Depois rode as migrations e o seed dentro do container (ou do host, se tiver Python local apontando
pro Postgres do compose):

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_admin.py --tenant "Nome da Loja" --nome "Fulana" --email fulana@exemplo.com --senha "senha-forte-123"
```

O frontend roda separado (`cd frontend && npm run dev`), apontando `VITE_API_URL` para
`http://localhost:8000`.

## Integração com o Mercado Livre

1. Crie uma aplicação em [developers.mercadolivre.com.br](https://developers.mercadolivre.com.br/).
2. Preencha no `.env`: `ML_CLIENT_ID`, `ML_CLIENT_SECRET`.
3. Para testar o fluxo OAuth e o webhook **localmente**, exponha a API via [ngrok](https://ngrok.com/):

   ```bash
   ngrok http 8000
   ```

   Use a URL pública gerada (`https://xxxx.ngrok-free.app`) como:
   - `ML_REDIRECT_URI=https://xxxx.ngrok-free.app/integrations/ml/callback` (no `.env`, reinicie a API)
   - URL de callback OAuth cadastrada na aplicação do ML Developers
   - URL de notificações (webhook) cadastrada na aplicação, apontando para `/webhooks/mercadolivre`

4. No frontend, como usuário admin, vá em **Integração ML** e clique em "Conectar Mercado Livre".
5. Em produção, a URL pública precisa ser estável (domínio real do deploy) — não dá para depender do
   ngrok fora de desenvolvimento.

### Fluxo de uso após conectar

1. **Produtos**: cadastre os produtos com SKU, estoque mínimo, etc.
2. **Vínculos ML**: associe manualmente cada anúncio do Mercado Livre (`item_id`) ao produto interno
   correspondente — só assim a baixa automática de estoque funciona.
3. Pedidos novos chegam via webhook e aparecem em **Pedidos** com status "pendente_etiqueta".
4. Selecione um ou mais pedidos (já vinculados a produto) e gere a etiqueta — individual ou em lote.
   A geração baixa o estoque automaticamente na mesma operação.
5. **Dashboard** mostra o resumo de pedidos pendentes e produtos com estoque abaixo do mínimo.

## Rodando os testes (backend)

```bash
cd backend
./venv/Scripts/python.exe -m pytest -v
```

Os testes cobrem as regras críticas do sistema: estoque nunca fica negativo, movimentação de
estoque é atômica (rollback completo em falha), idempotência de notificações de webhook do ML,
renovação automática/segura de token do ML, isolamento de dados por tenant e permissões
admin/operador. Rodam contra SQLite local — não precisam do Postgres do compose.

## Escopo do MVP e decisões de arquitetura

Ver [`docs/decisoes-arquitetura.md`](docs/decisoes-arquitetura.md) para o racional completo (por que
webhook em vez de polling, por que `BackgroundTasks` em vez de Celery/Redis no MVP, o que ficou
fora do escopo e por quê).
