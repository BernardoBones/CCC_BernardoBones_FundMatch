export default function FundList({ funds }) {
  if (!funds.length) return <p>Nenhum fundo encontrado.</p>;

  return (
    <table border="1" cellPadding="8" style={{ width: "100%" }}>
      <thead>
        <tr>
          <th>Nome</th>
          <th>CNPJ</th>
          <th>Classe</th>
          <th>Rentabilidade</th>
          <th>Risco</th>
          <th>Sharpe</th>
        </tr>
      </thead>
      <tbody>
        {funds.map((f) => (
          <tr key={f.id}>
            <td>{f.name}</td>
            <td>{f.cnpj}</td>
            <td>{f.class_name}</td>
            <td>{f.rentabilidade?.toFixed(2)}</td>
            <td>{f.risco?.toFixed(2)}</td>
            <td>{f.sharpe?.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
