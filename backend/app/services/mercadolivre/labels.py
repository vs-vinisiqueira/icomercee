"""Geração de etiqueta de envio + baixa automática de estoque.

Ordem deliberada: (1) validar pré-condições, (2) chamar a API do ML — rede, fora de
qualquer transação de banco — e só then (3) abrir uma transação curta e local para
gravar o resultado (baixa de estoque + atualização do pedido). Se a chamada ao ML
falhar, nada é persistido; o pedido continua pendente_etiqueta e nenhum estoque é
descontado. Isso evita segurar uma transação de banco esperando uma chamada de rede.
"""

import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.crud.order import obter_pedido
from app.models.order import Order
from app.services.mercadolivre.client import baixar_etiqueta
from app.services.stock.movements import EstoqueInsuficienteError, registrar_saida

LABELS_DIR = Path(os.getenv("LABELS_STORAGE_DIR", "storage/labels"))


class PedidoNaoEncontradoError(Exception):
    pass


class ProdutoNaoVinculadoError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Pedido {order_id} não tem produto vinculado — faça o vínculo antes de gerar a etiqueta")


class PedidoSemShipmentError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Pedido {order_id} ainda não tem shipment_id do Mercado Livre")


def gerar_etiqueta_pedido(db: Session, tenant_id: int, order_id: int, usuario_id: int) -> Order:
    pedido = obter_pedido(db, tenant_id, order_id)
    if not pedido:
        raise PedidoNaoEncontradoError(f"Pedido {order_id} não encontrado")

    if not pedido.product_id:
        raise ProdutoNaoVinculadoError(order_id)

    if not pedido.shipment_id_externo:
        raise PedidoSemShipmentError(order_id)

    # Chamada de rede primeiro, fora de transação de banco.
    conteudo_etiqueta = baixar_etiqueta(db, tenant_id, pedido.shipment_id_externo)

    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    caminho_arquivo = LABELS_DIR / f"{tenant_id}_{order_id}.pdf"
    caminho_arquivo.write_bytes(conteudo_etiqueta)

    # Transação curta e local: baixa de estoque + atualização do pedido.
    registrar_saida(
        db,
        tenant_id=tenant_id,
        product_id=pedido.product_id,
        quantidade=pedido.quantidade,
        motivo="baixa_pedido",
        criado_por=usuario_id,
        origem="pedido",
        referencia_pedido_id=pedido.id,
        observacao=f"Baixa automática por geração de etiqueta do pedido ML {pedido.pedido_id_externo}",
    )

    pedido.etiqueta_gerada = True
    pedido.etiqueta_url = f"/orders/{order_id}/label/download"
    pedido.status = "etiqueta_gerada"
    db.commit()
    db.refresh(pedido)

    return pedido


def gerar_etiquetas_lote(
    db: Session, tenant_id: int, order_ids: list[int], usuario_id: int
) -> tuple[list[Order], list[dict]]:
    """Gera etiquetas para múltiplos pedidos. Falha de um pedido não trava os demais —
    cada pedido tem sua própria tentativa e erro reportado separadamente."""
    sucesso: list[Order] = []
    falhas: list[dict] = []

    for order_id in order_ids:
        try:
            pedido = gerar_etiqueta_pedido(db, tenant_id, order_id, usuario_id)
            sucesso.append(pedido)
        except (
            PedidoNaoEncontradoError,
            ProdutoNaoVinculadoError,
            PedidoSemShipmentError,
            EstoqueInsuficienteError,
        ) as exc:
            falhas.append({"order_id": order_id, "erro": str(exc)})
        except Exception as exc:  # noqa: BLE001 — erro de rede/ML não deve travar o lote
            falhas.append({"order_id": order_id, "erro": f"Falha ao gerar etiqueta: {exc}"})

    return sucesso, falhas
