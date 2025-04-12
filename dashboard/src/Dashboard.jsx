import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [positions, setPositions] = useState([]);
  const [logData, setLogData] = useState([]);
  const [marketOpen, setMarketOpen] = useState(null);
  const [livePnl, setLivePnl] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const [posRes, logRes, marketRes, pnlRes] = await Promise.all([
        fetch('http://localhost:8000/api/positions'),
        fetch('http://localhost:8000/api/logs'),
        fetch('http://localhost:8000/api/market'),
        fetch('http://localhost:8000/api/pnl')
      ]);
      const pnlData = await pnlRes.json();
      setPositions(await posRes.json());
      setLogData(await logRes.json());
      setMarketOpen(await marketRes.json());
      setLivePnl(pnlData);
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const getPnlForSymbol = (symbol) => {
    const match = livePnl.find(p => p.symbol === symbol);
    return match ? match.live_pnl : null;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-xl font-bold mb-2">Equity Curve</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={logData}>
            <XAxis dataKey="timestamp" hide />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip />
            <Line type="monotone" dataKey="balance" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-xl font-bold mb-2">Market Status</h2>
        <p>Status: <span className={`font-semibold ${marketOpen?.is_open ? 'text-green-600' : 'text-red-600'}`}>
          {marketOpen?.is_open ? 'Open' : 'Closed'}</span></p>
        <p>Time: {marketOpen?.timestamp}</p>
      </div>

      <div className="bg-white shadow rounded-xl p-4 col-span-1 md:col-span-2">
        <h2 className="text-xl font-bold mb-2">Open Positions</h2>
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left">Symbol</th>
              <th>Qty</th>
              <th>Entry</th>
              <th>SL</th>
              <th>TP</th>
              <th>Time</th>
              <th>Live PNL</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos, i) => {
              const livePnlValue = getPnlForSymbol(pos.symbol);
              const rowClass = livePnlValue > 0 ? 'bg-green-50' : livePnlValue < 0 ? 'bg-red-50' : '';
              return (
                <tr key={i} className={`border-t ${rowClass}`}>
                  <td>{pos.symbol}</td>
                  <td className="text-center">{pos.qty}</td>
                  <td className="text-center">{pos.entry_price}</td>
                  <td className="text-center">{pos.sl}</td>
                  <td className="text-center">{pos.tp}</td>
                  <td className="text-center">{pos.time}</td>
                  <td className={`text-center font-semibold ${livePnlValue > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {livePnlValue !== null ? livePnlValue.toFixed(2) : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
