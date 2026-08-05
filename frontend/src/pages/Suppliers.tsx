import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { SupplierResponse } from "../api/types";

export function Suppliers() {
  const [fornecedores, setFornecedores] = useState<SupplierResponse[]>([]);
  const [nome, setNome] = useState("");
  const [contato, setContato] = useState("");

  const carregar = () => {
    api.get<SupplierResponse[]>("/suppliers/").then((res) => setFornecedores(res.data));
  };

  useEffect(carregar, []);

  const criar = async (event: FormEvent) => {
    event.preventDefault();
    await api.post("/suppliers/", { nome, contato: contato || null });
    setNome("");
    setContato("");
    carregar();
  };

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Fornecedores</h1>

      <form onSubmit={criar} style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input placeholder="Nome" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <input placeholder="Contato (opcional)" value={contato} onChange={(e) => setContato(e.target.value)} />
        <button type="submit">Adicionar</button>
      </form>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Contato</th>
          </tr>
        </thead>
        <tbody>
          {fornecedores.map((f) => (
            <tr key={f.id}>
              <td>{f.nome}</td>
              <td>{f.contato ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
