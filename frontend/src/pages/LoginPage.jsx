import { useState } from "react";
import api from "../api/api";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
  e.preventDefault();
  try {
    const formData = { email, password };
    console.log("🔍 formData:", formData);

    // Axios envia JSON por padrão
    const res = await api.post("/auth/login", formData);

    localStorage.setItem("token", res.data.access_token);
    navigate("/dashboard");
  } catch (err) {
    console.error("Erro ao fazer login:", err);
    setError("Falha no login. Verifique email e senha.");
  }
};

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <h1>FundMatch</h1>
      <form onSubmit={handleLogin}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Senha" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Entrar</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
