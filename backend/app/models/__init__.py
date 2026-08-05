"""Importa todos os módulos de modelo para garantir que o registry de mappers do
SQLAlchemy conheça todas as tabelas assim que `app.models` é importado — sem isso,
resolver uma ForeignKey (ex: "tenants.id") falha em runtime se o módulo dono da tabela
nunca foi importado por nenhuma rota (ex: Tenant só era referenciado via string nas
FKs, nunca importado diretamente pelas rotas)."""

from app.models import (  # noqa: F401
    ml_credentials,
    order,
    product,
    product_channel_mapping,
    stock_movement,
    supplier,
    tenant,
    user,
    webhook_event,
)
