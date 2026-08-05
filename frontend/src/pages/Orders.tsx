import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { OrderResponse } from "../api/types";

export function Orders() {
  const [pedidos, setPedidos] = useState<OrderResponse[]>([]);
  const [selecionados, setSelecionados] = useState<Set<number>>(new Set());
  const [mensagem, setMensagem] = useState<string | null>(null);

  const carregar = () => {
    api.get<OrderResponse[]>("/orders/pending").then((res) => setPedidos(res.data));
  };

  useEffect(carregar, []);

  const alternarSelecao = (id: number) => {
    setSelecionados((atual) => {
      const novo = new Set(atual);
      if (novo.has(id)) novo.delete(id);
      else novo.add(id);
      return novo;
    });
  };

  const gerarEtiquetaIndividual = async (id: number) => {
    setMensagem(null);
    try {
      await api.post(`/orders/${id}/label`);
      setMensagem(`Etiqueta do pedido ${id} gerada com sucesso.`);
      carregar();
    } catch (err: any) {
      setMensagem(err.response?.data?.detail || "Falha ao gerar etiqueta");
    }
  };

  const gerarEtiquetasEmLote = async () => {
    setMensagem(null);
    const { data } = await api.post("/orders/labels/batch", {
      order_ids: Array.from(selecionados),
    });
    setMensagem(
      `${data.sucesso.length} etiqueta(s) gerada(s). ${data.falhas.length} falha(s).` +
        (data.falhas.length > 0
          ? " Detalhes: " + data.falhas.map((f: any) => `#${f.order_id}: ${f.erro}`).join("; ")
          : "")
    );
    setSelecionados(new Set());
    carregar();
  };

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Pedidos pendentes de etiqueta</h1>

      <button onClick={gerarEtiquetasEmLote} disabled={selecionados.size === 0} style={{ marginBottom: 16 }}>
        Gerar etiquetas em lote ({selecionados.size} selecionado{selecionados.size !== 1 ? "s" : ""})
      </button>

      {mensagem && <p style={{ marginBottom: 12 }}>{mensagem}</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th></th>
            <th>Pedido ML</th>
            <th>Item ML</th>
            <th>Produto vinculado</th>
            <th>Qtd</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {pedidos.map((p) => (
            <tr key={p.id}>
              <td>
                <input
                  type="checkbox"
                  checked={selecionados.has(p.id)}
                  onChange={() => alternarSelecao(p.id)}
                  disabled={!p.product_id}
                />
              </td>
              <td>{p.pedido_id_externo}</td>
              <td>{p.item_id_externo ?? "—"}</td>
              <td>{p.product_id ?? "não vinculado"}</td>
              <td>{p.quantidade}</td>
              <td>{p.status}</td>
              <td>
                <button onClick={() => gerarEtiquetaIndividual(p.id)} disabled={!p.product_id}>
                  Gerar etiqueta
                </button>
                {p.etiqueta_gerada && (
                  <a
                    href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}${p.etiqueta_url}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{ marginLeft: 8 }}
                  >
                    Baixar
                  </a>
                )}
              </td>
            </tr>
          ))}
          {pedidos.length === 0 && (
            <tr>
              <td colSpan={7}>Nenhum pedido pendente</td>
            </tr>
          )}
        </tbody>
      </table>
      <p style={{ marginTop: 12, color: "#666", fontSize: 13 }}>
        Pedidos sem produto vinculado precisam ser associados na tela de Vínculos ML antes de gerar a
        etiqueta.
      </p>
    </div>
  );
}
