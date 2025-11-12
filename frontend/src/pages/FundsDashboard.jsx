import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/styles.css";

export default function FundsDashboard() {
  const [funds, setFunds] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [activeTab, setActiveTab] = useState("funds");
  const token = localStorage.getItem("token");

  const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: { Authorization: `Bearer ${token}` },
  });

  // Carrega fundos, favoritos e recomendações
  useEffect(() => {
    async function fetchData() {
      try {
        const [fundRes, favRes, recRes] = await Promise.all([
          api.get("/funds/"),
          api.get("/favorites/"),
          api.get("/recommendations/"),
        ]);

        console.log("📊 /funds/:", fundRes.data);
        console.log("⭐ /favorites/:", favRes.data);
        console.log("💡 /recommendations/:", recRes.data);

        setFunds(fundRes.data);
        setFavorites(favRes.data.map((f) => f.id));
        setRecommendations(recRes.data);
      } catch (err) {
        console.error("Erro ao buscar dados:", err);
      }
    }
    fetchData();
  }, []);

  // Favoritar / desfavoritar
  async function toggleFavorite(fundId) {
    try {
      if (favorites.includes(fundId)) {
        await api.delete(`/favorites/${fundId}`);
        setFavorites(favorites.filter((id) => id !== fundId));
      } else {
        await api.post(`/favorites/${fundId}`);
        setFavorites([...favorites, fundId]);
      }
    } catch (err) {
      console.error("Erro ao favoritar:", err);
      alert("Erro ao favoritar. Verifique se está logado.");
    }
  }

  // Gerar PDF do relatório
  async function generateReport() {
    try {
      const response = await fetch("http://127.0.0.1:8000/report/generate", {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error("Falha ao gerar relatório");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");
    } catch (err) {
      console.error("Erro ao gerar relatório:", err);
      alert("Erro ao gerar relatório PDF. Verifique sua autenticação.");
    }
  }

  // Renderiza cards
  function renderFundCards(list) {
    if (!list.length)
      return <p style={{ marginTop: "12px" }}>Nenhum fundo encontrado.</p>;

    return (
      <div className="funds-grid">
        {list.map((fund) => (
          <div key={fund.id} className="fund-card">
            <div className="fund-header">
              <h3>{fund.name}</h3>
              <button
                className={
                  favorites.includes(fund.id) ? "favorite" : "not-favorite"
                }
                onClick={() => toggleFavorite(fund.id)}
              >
                {favorites.includes(fund.id) ? "★" : "☆"}
              </button>
            </div>

            <p><strong>CNPJ:</strong> {fund.cnpj}</p>
            <p><strong>Classe:</strong> {fund.class_name || "N/A"}</p>
            <p><strong>Rentabilidade:</strong> {fund.rentability?.toFixed(2) ?? 0}%</p>
            <p><strong>Risco:</strong> {fund.risk?.toFixed(2) ?? 0}</p>
            <p><strong>Sharpe:</strong> {fund.sharpe?.toFixed(2) ?? 0}</p>
          </div>
        ))}
      </div>
    );
  }

  // Alterna abas
  function getActiveList() {
    switch (activeTab) {
      case "favorites":
        return funds.filter((f) => favorites.includes(f.id));
      case "recommendations":
        return recommendations;
      default:
        return funds;
    }
  }

  return (
    <div className="container">
      {/* Cabeçalho e botão de relatório */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>Fundos de Investimento</h1>
        <button className="btn-primary" onClick={generateReport}>
          📄 Gerar Relatório PDF
        </button>
      </div>

      {/* Abas */}
      <div className="tabs">
        <button
          className={activeTab === "funds" ? "tab active" : "tab"}
          onClick={() => setActiveTab("funds")}
        >
          Todos os Fundos
        </button>
        <button
          className={activeTab === "favorites" ? "tab active" : "tab"}
          onClick={() => setActiveTab("favorites")}
        >
          Favoritos
        </button>
        <button
          className={activeTab === "recommendations" ? "tab active" : "tab"}
          onClick={() => setActiveTab("recommendations")}
        >
          Recomendações
        </button>
      </div>

      {/* Lista dinâmica */}
      {renderFundCards(getActiveList())}
    </div>
  );
}
