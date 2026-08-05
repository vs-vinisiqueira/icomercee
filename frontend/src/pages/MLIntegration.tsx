import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { MLCredentialsStatus } from "../api/types";

export function MLIntegration() {
  const [status, setStatus] = useState<MLCredentialsStatus | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = () => {
    api
      .get<MLCredentialsStatus>("/integrations/ml/status")
      .then((res) => setStatus(res.data))
      .catch(() => setErro("Não foi possível carregar o status da integração"));
  };

  useEffect(carregar, []);

  const conectar = async () => {
    const { data } = await api.get<{ authorization_url: string }>("/integrations/ml/connect");
    window.location.href = data.authorization_url;
  };

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Integração Mercado Livre</h1>

      {erro && <p style={{ color: "#dc2626" }}>{erro}</p>}

      {status && (
        <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 16, maxWidth: 480 }}>
          {status.conectado ? (
            <>
              <p style={{ color: "#16a34a", fontWeight: 600 }}>Conta conectada</p>
              <p>ML user id: {status.ml_user_id}</p>
              <p>Token expira em: {status.expires_at ? new Date(status.expires_at).toLocaleString() : "—"}</p>
            </>
          ) : (
            <>
              <p style={{ marginBottom: 12 }}>Nenhuma conta do Mercado Livre conectada ainda.</p>
              <button onClick={conectar}>Conectar Mercado Livre</button>
            </>
          )}
        </div>
      )}

      <p style={{ marginTop: 16, color: "#666", fontSize: 13, maxWidth: 640 }}>
        Em desenvolvimento local, use o ngrok para expor a API e configure a URL pública tanto em
        ML_REDIRECT_URI quanto no webhook cadastrado na aplicação do Mercado Livre Developers.
      </p>
    </div>
  );
}
