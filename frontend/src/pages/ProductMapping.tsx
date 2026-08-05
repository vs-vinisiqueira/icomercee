import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { ProductMappingResponse, ProductResponse } from "../api/types";

export function ProductMapping() {
  const [vinculos, setVinculos] = useState<ProductMappingResponse[]>([]);
  const [produtos, setProdutos] = useState<ProductResponse[]>([]);
  const [itemIdExterno, setItemIdExterno] = useState("");
  const [productId, setProductId] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  const carregar = () => {
    api.get<ProductMappingResponse[]>("/product-mappings/").then((res) => setVinculos(res.data));
  };

  useEffect(carregar, []);
  useEffect(() => {
    api.get<ProductResponse[]>("/products/").then((res) => setProdutos(res.data));
  }, []);

  const criar = async (event: FormEvent) => {
    event.preventDefault();
    setErro(null);
    try {
      await api.post("/product-mappings/", {
        canal: "mercado_livre",
        item_id_externo: itemIdExterno,
        product_id: Number(productId),
      });
      setItemIdExterno("");
      setProductId("");
      carregar();
    } catch {
      setErro("Este anúncio já está vinculado a um produto");
    }
  };

  const nomeProduto = (id: number) => produtos.find((p) => p.id === id)?.nome ?? id;

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Vínculos anúncio ↔ produto (Mercado Livre)</h1>
      <p style={{ color: "#666", marginBottom: 16, maxWidth: 640 }}>
        Um anúncio do Mercado Livre pode não corresponder 1:1 a um SKU interno. Vincule manualmente
        aqui para que a baixa automática de estoque funcione ao gerar a etiqueta.
      </p>

      <form onSubmit={criar} style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input
          placeholder="item_id do anúncio no ML"
          value={itemIdExterno}
          onChange={(e) => setItemIdExterno(e.target.value)}
          required
        />
        <select value={productId} onChange={(e) => setProductId(e.target.value)} required>
          <option value="">Selecione o produto</option>
          {produtos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.sku} — {p.nome}
            </option>
          ))}
        </select>
        <button type="submit">Vincular</button>
      </form>
      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Item ML</th>
            <th>Produto</th>
          </tr>
        </thead>
        <tbody>
          {vinculos.map((v) => (
            <tr key={v.id}>
              <td>{v.item_id_externo}</td>
              <td>{nomeProduto(v.product_id)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
