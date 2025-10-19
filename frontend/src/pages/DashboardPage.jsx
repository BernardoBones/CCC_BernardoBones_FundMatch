import { useEffect, useState } from "react";
import api from "../api/api";
import FundList from "../components/FundList";

export default function DashboardPage() {
  const [funds, setFunds] = useState([]);

  useEffect(() => {
    const fetchFunds = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await api.get("/funds/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setFunds(res.data);
      } catch (err) {
        console.error("Erro ao carregar fundos", err);
      }
    };
    fetchFunds();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Fundos de Investimento</h2>
      <FundList funds={funds} />
    </div>
  );
}
