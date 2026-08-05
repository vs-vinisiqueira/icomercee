import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { ProductResponse, StockMovementResponse, SupplierResponse } from "../api/types";

export function Products() {
  const [produtos, setProdutos] = useState<ProductResponse[]>([]);
  const [fornecedores, setFornecedores] = useState<SupplierResponse[]>([]);
  const [apenasEstoqueBaixo, setApenasEstoqueBaixo] = useState(false);

  const [sku, setSku] = useState("");
  const [nome, setNome] = useState("");
  const [categoria, setCategoria] = useState("");
  const [supplierId, setSupplierId] = useState("");
  const [custoCompra, setCustoCompra] = useState("0");
  const [precoVenda, setPrecoVenda] = useState("0");
  const [estoqueMinimo, setEstoqueMinimo] = useState("0");
  const [erro, setErro] = useState<string | null>(null);

  const [produtoSelecionado, setProdutoSelecionado] = useState<ProductResponse | null>(null);

  const carregarProdutos = () => {
    api
      .get<ProductResponse[]>("/products/", { params: { apenas_estoque_baixo: apenasEstoqueBaixo } })
      .then((res) => setProdutos(res.data));
  };

  useEffect(carregarProdutos, [apenasEstoqueBaixo]);
  useEffect(() => {
    api.get<SupplierResponse[]>("/suppliers/").then((res) => setFornecedores(res.data));
  }, []);

  const criar = async (event: FormEvent) => {
    event.preventDefault();
    setErro(null);
    try {
      await api.post("/products/", {
        sku,
        nome,
        categoria: categoria || null,
        supplier_id: supplierId ? Number(supplierId) : null,
        custo_compra: custoCompra,
        preco_venda: precoVenda,
        estoque_minimo: Number(estoqueMinimo),
      });
      setSku("");
      setNome("");
      setCategoria("");
      setSupplierId("");
      setCustoCompra("0");
      setPrecoVenda("0");
      setEstoqueMinimo("0");
      carregarProdutos();
    } catch {
      setErro("Não foi possível criar o produto (SKU já cadastrado?)");
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Produtos</h1>

      <form onSubmit={criar} style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <input placeholder="SKU" value={sku} onChange={(e) => setSku(e.target.value)} required />
        <input placeholder="Nome" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <input placeholder="Categoria" value={categoria} onChange={(e) => setCategoria(e.target.value)} />
        <select value={supplierId} onChange={(e) => setSupplierId(e.target.value)}>
          <option value="">Sem fornecedor</option>
          {fornecedores.map((f) => (
            <option key={f.id} value={f.id}>
              {f.nome}
            </option>
          ))}
        </select>
        <input
          placeholder="Custo"
          type="number"
          step="0.01"
          value={custoCompra}
          onChange={(e) => setCustoCompra(e.target.value)}
        />
        <input
          placeholder="Preço venda"
          type="number"
          step="0.01"
          value={precoVenda}
          onChange={(e) => setPrecoVenda(e.target.value)}
        />
        <input
          placeholder="Estoque mínimo"
          type="number"
          value={estoqueMinimo}
          onChange={(e) => setEstoqueMinimo(e.target.value)}
        />
        <button type="submit">Adicionar</button>
      </form>
      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      <label style={{ display: "block", marginBottom: 12 }}>
        <input
          type="checkbox"
          checked={apenasEstoqueBaixo}
          onChange={(e) => setApenasEstoqueBaixo(e.target.checked)}
        />{" "}
        Mostrar apenas estoque abaixo do mínimo
      </label>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nome</th>
            <th>Estoque</th>
            <th>Mínimo</th>
            <th>Preço venda</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {produtos.map((p) => (
            <tr key={p.id} style={p.estoque_atual <= p.estoque_minimo ? { color: "#dc2626" } : undefined}>
              <td>{p.sku}</td>
              <td>{p.nome}</td>
              <td>{p.estoque_atual}</td>
              <td>{p.estoque_minimo}</td>
              <td>{p.preco_venda}</td>
              <td>
                <button onClick={() => setProdutoSelecionado(p)}>Movimentar estoque</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {produtoSelecionado && (
        <MovimentacaoPanel
          produto={produtoSelecionado}
          onFechar={() => setProdutoSelecionado(null)}
          onAtualizado={carregarProdutos}
        />
      )}
    </div>
  );
}

function MovimentacaoPanel({
  produto,
  onFechar,
  onAtualizado,
}: {
  produto: ProductResponse;
  onFechar: () => void;
  onAtualizado: () => void;
}) {
  const [quantidade, setQuantidade] = useState("1");
  const [motivoEntrada, setMotivoEntrada] = useState("compra_fornecedor");
  const [motivoSaida, setMotivoSaida] = useState("ajuste_manual");
  const [observacao, setObservacao] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [historico, setHistorico] = useState<StockMovementResponse[]>([]);

  const carregarHistorico = () => {
    api
      .get<StockMovementResponse[]>(`/stock/produtos/${produto.id}/historico`)
      .then((res) => setHistorico(res.data));
  };

  useEffect(carregarHistorico, [produto.id]);

  const registrarEntrada = async () => {
    setErro(null);
    try {
      await api.post("/stock/entrada", {
        product_id: produto.id,
        quantidade: Number(quantidade),
        motivo: motivoEntrada,
        observacao: observacao || null,
      });
      onAtualizado();
      carregarHistorico();
    } catch {
      setErro("Falha ao registrar entrada");
    }
  };

  const registrarSaida = async () => {
    setErro(null);
    try {
      await api.post("/stock/saida", {
        product_id: produto.id,
        quantidade: Number(quantidade),
        motivo: motivoSaida,
        observacao: observacao || null,
      });
      onAtualizado();
      carregarHistorico();
    } catch (err: any) {
      setErro(err.response?.data?.detail || "Falha ao registrar saída (estoque insuficiente?)");
    }
  };

  return (
    <div style={{ marginTop: 24, border: "1px solid #e5e7eb", borderRadius: 8, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <h2>
          Movimentar: {produto.sku} — {produto.nome} (estoque atual: {produto.estoque_atual})
        </h2>
        <button onClick={onFechar}>Fechar</button>
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
        <input
          type="number"
          min={1}
          value={quantidade}
          onChange={(e) => setQuantidade(e.target.value)}
          style={{ width: 80 }}
        />
        <select value={motivoEntrada} onChange={(e) => setMotivoEntrada(e.target.value)}>
          <option value="compra_fornecedor">Compra de fornecedor</option>
          <option value="ajuste_manual">Ajuste manual</option>
        </select>
        <button onClick={registrarEntrada}>Registrar entrada</button>

        <select value={motivoSaida} onChange={(e) => setMotivoSaida(e.target.value)}>
          <option value="ajuste_manual">Ajuste manual</option>
          <option value="perda">Perda</option>
        </select>
        <button onClick={registrarSaida}>Registrar saída</button>

        <input
          placeholder="Observação (opcional)"
          value={observacao}
          onChange={(e) => setObservacao(e.target.value)}
          style={{ flex: 1, minWidth: 160 }}
        />
      </div>
      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      <h3 style={{ marginBottom: 8 }}>Histórico</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Data</th>
            <th>Tipo</th>
            <th>Qtd</th>
            <th>Motivo</th>
            <th>Origem</th>
            <th>Observação</th>
          </tr>
        </thead>
        <tbody>
          {historico.map((m) => (
            <tr key={m.id}>
              <td>{new Date(m.criado_em).toLocaleString()}</td>
              <td>{m.tipo}</td>
              <td>{m.quantidade}</td>
              <td>{m.motivo}</td>
              <td>{m.origem}</td>
              <td>{m.observacao ?? "—"}</td>
            </tr>
          ))}
          {historico.length === 0 && (
            <tr>
              <td colSpan={6}>Nenhuma movimentação ainda</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
