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
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Busca inicial de dados
  useEffect(() => {
    async function fetchData() {
      try {
        const [fundRes, favRes, recRes] = await Promise.all([
          api.get("/funds/"),
          api.get("/favorites/"),
          api.get("/recommendations/"),
        ]);

        setFunds(fundRes.data);
        setFavorites(favRes.data.map((f) => f.id));
        setRecommendations(recRes.data);
      } catch (err) {
        console.error("Erro ao buscar dados:", err);
      }
    }
    fetchData();
  }, []);

  // Função de favoritar/desfavoritar
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
    }
  }

  // Renderização dos cards
  function renderFundCards(list) {
    if (!list.length)
      return <p style={{ marginTop: "12px" }}>Nenhum fundo encontrado.</p>;

    return (
      <div className="funds-grid">
        {list.map((fund) => (
          <div key={fund.id} className="fund-card">
            <div className="fund-header">
              <h3>{fund.nome}</h3>
              <button
                className={
                  favorites.includes(fund.id)
                    ? "favorite"
                    : "not-favorite"
                }
                onClick={() => toggleFavorite(fund.id)}
              >
                {favorites.includes(fund.id) ? "★" : "☆"}
              </button>
            </div>
            <p><strong>CNPJ:</strong> {fund.cnpj}</p>
            <p><strong>Classe:</strong> {fund.classe || "N/A"}</p>
            <p><strong>Rentabilidade:</strong> {fund.rentabilidade?.toFixed(2) ?? 0}%</p>
            <p><strong>Risco:</strong> {fund.risco?.toFixed(2) ?? 0}</p>
            <p><strong>Sharpe:</strong> {fund.sharpe?.toFixed(2) ?? 0}</p>
          </div>
        ))}
      </div>
    );
  }

  // Alterna entre abas
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
      <h1>Fundos de Investimento</h1>

      {/* Abas de navegação */}
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

      {/* Exibição de cards */}
      {renderFundCards(getActiveList())}
    </div>
  );
}