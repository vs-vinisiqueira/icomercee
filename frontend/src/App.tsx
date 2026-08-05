import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { AdminRoute, ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Products } from "./pages/Products";
import { Suppliers } from "./pages/Suppliers";
import { Orders } from "./pages/Orders";
import { ProductMapping } from "./pages/ProductMapping";
import { MLIntegration } from "./pages/MLIntegration";
import { Users } from "./pages/Users";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/pedidos" element={<Orders />} />
              <Route path="/produtos" element={<Products />} />
              <Route path="/fornecedores" element={<Suppliers />} />
              <Route path="/vinculos" element={<ProductMapping />} />

              <Route element={<AdminRoute />}>
                <Route path="/integracao-ml" element={<MLIntegration />} />
                <Route path="/usuarios" element={<Users />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
