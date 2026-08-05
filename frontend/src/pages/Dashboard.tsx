import { useEffect, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { DashboardResponse } from "../api/types";

export function Dashboard() {
  const [dados, setDados] = useState<DashboardResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<DashboardResponse>("/dashboard/")
      .then((res) => setDados(res.data))
      .catch(() => setErro("Não foi possível carregar o dashboard"));
  }, []);

  if (erro) return <p style={{ color: "#dc2626" }}>{erro}</p>;
  if (!dados) return <p>Carregando...</p>;

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Dashboard</h1>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={cardStyle}>
          <p style={{ fontSize: 28, fontWeight: 700 }}>{dados.total_pedidos_pendentes}</p>
          <p>Pedidos pendentes de etiqueta</p>
        </div>
        <div style={cardStyle}>
          <p style={{ fontSize: 28, fontWeight: 700, color: "#dc2626" }}>
            {dados.total_produtos_estoque_baixo}
          </p>
          <p>Produtos com estoque baixo</p>
        </div>
      </div>

      <h2 style={{ marginBottom: 8 }}>Pedidos pendentes</h2>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th>Pedido ML</th>
            <th>Qtd</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {dados.pedidos_pendentes.map((pedido) => (
            <tr key={pedido.id}>
              <td>{pedido.pedido_id_externo}</td>
              <td>{pedido.quantidade}</td>
              <td>{pedido.status}</td>
            </tr>
          ))}
          {dados.pedidos_pendentes.length === 0 && (
            <tr>
              <td colSpan={3}>Nenhum pedido pendente</td>
            </tr>
          )}
        </tbody>
      </table>
      <p style={{ marginTop: 8 }}>
        <Link to="/pedidos">Ver todos os pedidos →</Link>
      </p>

      <h2 style={{ margin: "24px 0 8px" }}>Estoque abaixo do mínimo</h2>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Produto</th>
            <th>Estoque atual</th>
            <th>Mínimo</th>
          </tr>
        </thead>
        <tbody>
          {dados.produtos_estoque_baixo.map((produto) => (
            <tr key={produto.id} style={{ color: "#dc2626" }}>
              <td>{produto.sku}</td>
              <td>{produto.nome}</td>
              <td>{produto.estoque_atual}</td>
              <td>{produto.estoque_minimo}</td>
            </tr>
          ))}
          {dados.produtos_estoque_baixo.length === 0 && (
            <tr>
              <td colSpan={4}>Nenhum produto abaixo do mínimo</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

const cardStyle: CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 8,
  padding: 16,
  minWidth: 200,
};

const tableStyle: CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
};
