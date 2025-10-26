import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import FundsPage from "./pages/FundsPage";
import DashboardPage from "./pages/DashboardPage"; 
import FundsDashboard from "./pages/FundsDashboard";
import React from "react";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/funds" element={<FundsPage />} />
        <Route path="/dashboard" element={<FundsDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
