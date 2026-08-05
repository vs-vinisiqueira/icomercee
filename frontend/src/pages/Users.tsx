import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { UserResponse } from "../api/types";

export function Users() {
  const [usuarios, setUsuarios] = useState<UserResponse[]>([]);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [role, setRole] = useState<"admin" | "operador">("operador");
  const [erro, setErro] = useState<string | null>(null);

  const carregar = () => {
    api.get<UserResponse[]>("/users/").then((res) => setUsuarios(res.data));
  };

  useEffect(carregar, []);

  const criar = async (event: FormEvent) => {
    event.preventDefault();
    setErro(null);
    try {
      await api.post("/users/", { nome, email, senha, role });
      setNome("");
      setEmail("");
      setSenha("");
      setRole("operador");
      carregar();
    } catch {
      setErro("Não foi possível criar o usuário (email já cadastrado?)");
    }
  };

  const desativar = async (id: number) => {
    await api.delete(`/users/${id}`);
    carregar();
  };

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Usuários</h1>

      <form onSubmit={criar} style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        <input placeholder="Nome" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <input
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          placeholder="Senha (mín. 8)"
          type="password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />
        <select value={role} onChange={(e) => setRole(e.target.value as "admin" | "operador")}>
          <option value="operador">Operador</option>
          <option value="admin">Admin</option>
        </select>
        <button type="submit">Adicionar</button>
      </form>
      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Role</th>
            <th>Ativo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              <td>{u.nome}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>{u.ativo ? "Sim" : "Não"}</td>
              <td>
                {u.ativo && <button onClick={() => desativar(u.id)}>Desativar</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
