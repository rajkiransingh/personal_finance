'use client';

import { useEffect, useState } from 'react';

export default function ScreenNDiscover() {
  const [strategyConfig, setStrategyConfig] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/config/stock-picking-strategy-config')
      .then(res => res.json())
      .then(data => setStrategyConfig(data.strategy))
      .catch(err => console.error(err));
  }, []);

  // Dummy stock data to illustrate
  const exampleStock = {
    ROCE: 0.3,
    OPM_5Y: 0.18,
    NPM: 0.14,
    PEG: 0.1,
    PE: 20,
    PB: 3,
    DebtToEquity: 0.5,
    InterestCoverage: 4,
    SalesGrowth_5Y: 0.2,
    ProfitGrowth_5Y: 0.25,
    PromoterHolding: 0.6,
    MarketCap: 5000
  };

  const stockScore = (stock: any, metrics: Record<string, number>) => {
    let score = 0;
    for (let key in metrics) {
      if (stock[key] !== undefined) {
        score += stock[key] * metrics[key];
      }
    }
    return score;
  };

  function ScoreCard({ name, score }: { name: string; score: number }) {
    const color = score > 0.1 ? 'bg-green-400' : score < -0.1 ? 'bg-red-400' : 'bg-yellow-400';
    return (
      <div className={`p-2 rounded text-white ${color}`}>
        {name}: {score.toFixed(2)}
      </div>
    );
  }

  if (!strategyConfig) {
    return <div className="text-white p-4">Loading strategy config...</div>;
  }

  return (
    <div className="space-y-4 p-4">
      {Object.entries(strategyConfig).map(([strategyName, strategy]: [string, any]) => {
        const score = stockScore(exampleStock, strategy.metrics);
        return (
          <div key={strategyName} className="bg-gray-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold text-white">{strategyName.toUpperCase()}</h2>
            <p className="text-gray-300 mb-2">{strategy.description}</p>
            <ScoreCard name="Example Stock Score" score={score} />
          </div>
        );
      })}
    </div>
  );
}
