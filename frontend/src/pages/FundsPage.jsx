import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/styles.css";

export default function FundsPage() {
  const [funds, setFunds] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        const [fundsRes, favsRes] = await Promise.all([
          api.get("/funds/"),
          api.get("/favorites/"),
        ]);
        setFunds(fundsRes.data);
        setFavorites(favsRes.data.map(f => f.id)); // lista de ids favoritos
      } catch (err) {
        console.error("Erro ao buscar dados:", err);
        setError("Não foi possível carregar os fundos. Tente novamente.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  async function toggleFavorite(fundId) {
    try {
      if (favorites.includes(fundId)) {
        await api.delete(`/favorites/${fundId}`);
        setFavorites(favorites.filter(id => id !== fundId));
      } else {
        await api.post(`/favorites/${fundId}`);
        setFavorites([...favorites, fundId]);
      }
    } catch (err) {
      console.error("Erro ao favoritar:", err);
      alert("Não foi possível atualizar favorito. Tente novamente.");
    }
  }

  if (loading) return <p className="p-4">Carregando fundos...</p>;
  if (error) return <p className="p-4 text-red-500">{error}</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Fundos de Investimento</h2>
      {funds.length === 0 ? (
        <p>Nenhum fundo disponível.</p>
      ) : (
        <ul className="space-y-2">
          {funds.map(fund => (
            <li
              key={fund.id}
              className="flex items-center justify-between bg-gray-100 p-3 rounded-lg"
            >
              <div>
                <p className="font-semibold">{fund.name}</p>
                <p className="text-sm text-gray-600">{fund.cnpj}</p>
              </div>
              <button
                onClick={() => toggleFavorite(fund.id)}
                className={`text-lg ${favorites.includes(fund.id) ? "text-yellow-500" : "text-gray-400"}`}
              >
                {favorites.includes(fund.id) ? "★" : "☆"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
