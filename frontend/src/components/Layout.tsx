import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const linkStyle = ({ isActive }: { isActive: boolean }) => ({
  padding: "8px 12px",
  borderRadius: 6,
  textDecoration: "none",
  color: isActive ? "#fff" : "#333",
  background: isActive ? "#2563eb" : "transparent",
  fontWeight: 500,
});

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "system-ui, sans-serif" }}>
      <nav
        style={{
          width: 220,
          borderRight: "1px solid #e5e7eb",
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        <strong style={{ marginBottom: 16, fontSize: 18 }}>Sistema DRI</strong>
        <NavLink to="/" style={linkStyle} end>
          Dashboard
        </NavLink>
        <NavLink to="/pedidos" style={linkStyle}>
          Pedidos
        </NavLink>
        <NavLink to="/produtos" style={linkStyle}>
          Produtos
        </NavLink>
        <NavLink to="/fornecedores" style={linkStyle}>
          Fornecedores
        </NavLink>
        <NavLink to="/vinculos" style={linkStyle}>
          Vínculos ML
        </NavLink>
        {user?.role === "admin" && (
          <>
            <NavLink to="/integracao-ml" style={linkStyle}>
              Integração ML
            </NavLink>
            <NavLink to="/usuarios" style={linkStyle}>
              Usuários
            </NavLink>
          </>
        )}
        <div style={{ marginTop: "auto", fontSize: 13, color: "#666" }}>
          <p>{user?.nome}</p>
          <p style={{ marginBottom: 8 }}>{user?.role}</p>
          <button onClick={logout} style={{ width: "100%" }}>
            Sair
          </button>
        </div>
      </nav>
      <main style={{ flex: 1, padding: 24 }}>
        <Outlet />
      </main>
    </div>
  );
}
