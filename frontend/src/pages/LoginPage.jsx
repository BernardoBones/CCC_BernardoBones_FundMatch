import { useState } from "react";
import api from "../api/api";
import { useNavigate } from "react-router-dom";
import "../styles/styles.css";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      if (isRegister) {
        // Criar conta
        const res = await api.post("/auth/register", { name, email, password });
        setSuccess("Conta criada com sucesso! Você já pode fazer login.");
        setIsRegister(false);
        setName("");
        setPassword("");
      } else {
        // Fazer login
        const res = await api.post("/auth/login", { email, password });
        localStorage.setItem("token", res.data.access_token);
        navigate("/dashboard");
      }
    } catch (err) {
      console.error("Erro:", err);
      if (err.response?.status === 400) {
        setError("E-mail já registrado.");
      } else if (err.response?.status === 401) {
        setError("Credenciais inválidas.");
      } else {
        setError("Tente novamente em 1 minuto.");
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1 className="auth-title">{isRegister ? "Criar Conta" : "Entrar"}</h1>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <input
              type="text"
              placeholder="Nome completo"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}

          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" className="btn-primary" style={{ width: "100%", marginTop: "10px" }}>
            {isRegister ? "Cadastrar" : "Entrar"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}

        <p style={{ marginTop: "12px", textAlign: "center" }}>
          {isRegister ? (
            <>
              Já tem uma conta?{" "}
              <button
                type="button"
                onClick={() => setIsRegister(false)}
                className="link-button"
              >
                Entrar
              </button>
            </>
          ) : (
            <>
              Não tem conta?{" "}
              <button
                type="button"
                onClick={() => setIsRegister(true)}
                className="link-button"
              >
                Criar conta
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
