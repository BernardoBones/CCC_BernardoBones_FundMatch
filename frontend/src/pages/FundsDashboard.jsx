import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/styles.css";

export default function FundsDashboard() {
  const [funds, setFunds] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [activeTab, setActiveTab] = useState("funds");
  const [metrics, setMetrics] = useState({});

  const token = localStorage.getItem("token");

  const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: { Authorization: `Bearer ${token}` },
  });

  // ============================================================
  // 1. Carregar fundos, favoritos e recomendações
  // ============================================================
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

  // ============================================================
  // 2. computeMetrics (igual ao botão)
  // ============================================================
  async function computeMetrics(cnpj) {
    try {
      const res = await api.get(`/funds/${cnpj}/metrics`);

      setMetrics((prev) => ({
        ...prev,
        [cnpj]: res.data,
      }));
    } catch (err) {
      console.error("Erro ao obter métricas:", err);
    }
  }

  // ============================================================
  // 3. Carregar métricas para FUNDS
  // ============================================================
  useEffect(() => {
    funds.forEach((fund) => {
      if (!metrics[fund.cnpj]) computeMetrics(fund.cnpj);
    });
  }, [funds]);

  // ============================================================
  // 4. Carregar métricas para RECOMMENDATIONS
  // ============================================================
  useEffect(() => {
    recommendations.forEach((fund) => {
      if (!metrics[fund.cnpj]) computeMetrics(fund.cnpj);
    });
  }, [recommendations]);

  // ============================================================
  // 5. Favoritar / desfavoritar
  // ============================================================
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
      alert("Erro ao favoritar.");
    }
  }

  // ============================================================
  // 6. PDF
  // ============================================================
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
      alert("Erro ao gerar relatório PDF.");
    }
  }

  // ============================================================
  // 7. Render de cards
  // ============================================================
  function renderFundCards(list) {
    if (!list.length)
      return <p style={{ marginTop: "12px" }}>Nenhum fundo encontrado.</p>;

    return (
      <div className="funds-grid">
        {list.map((fund) => {
          const m = metrics[fund.cnpj];

          return (
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
              <p><strong>Classe:</strong> {fund.class_name}</p>

              {!m && <p>Carregando métricas...</p>}

              {m && (
                <>
                  <p><strong>Rentabilidade:</strong> {m.rentability.toFixed(4)}</p>
                  <p><strong>Volatilidade:</strong> {m.volatility.toFixed(4)}</p>
                  <p><strong>Sharpe:</strong> {m.sharpe.toFixed(4)}</p>
                </>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // ============================================================
  // 8. Abas
  // ============================================================
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
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Fundos de Investimento</h1>
        <button className="btn-primary" onClick={generateReport}>
          📄 Gerar Relatório PDF
        </button>
      </div>

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

      {renderFundCards(getActiveList())}
    </div>
  );
}
