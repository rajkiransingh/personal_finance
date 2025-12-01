'use client';

import { useEffect, useState } from 'react';

interface StockData {
  symbol: string;
  sector: string;
  sub_sector: string;
  core: number;
  accelerators: number;
  gem: number;
  market_cap: number;
  pe_ratio: number;
  pb_ratio: number;
  peg_ratio: number;
  roe: number;
  roce: number;
  debt_to_equity: number;
  promoter_holding: number;
  ebitda_margin: number;
  ev_ebitda: number;
}

function ScoreBox({ label, value }: { label: string; value: number }) {
  const color =
    value > 0.2 ? 'bg-green-500' : value < -0.2 ? 'bg-red-500' : 'bg-yellow-500';
  return (
    <div className={`px-3 py-1 rounded text-sm font-medium text-white ${color}`}>
      {label}: {value.toFixed(2)}
    </div>
  );
}

// 🎴 Flip Card Component
function StockCard({ stock }: { stock: StockData }) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div
      className="relative w-full h-48 cursor-pointer perspective"
      onClick={() => setFlipped(!flipped)}
    >
      <div
        className={`relative w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
          flipped ? 'rotate-y-180' : ''
        }`}
      >
        {/* Front Side */}
        <div className="absolute inset-0 bg-gray-900 rounded-lg p-4 shadow-lg backface-hidden">
          <h2 className="text-lg font-semibold mb-1">{stock.symbol}</h2>
          <p className="text-sm text-gray-400 mb-3">
            {stock.sub_sector} [{stock.sector}]
          </p>
          <div className="flex flex-wrap gap-2">
            <ScoreBox label="Core" value={stock.core} />
            <ScoreBox label="Accelerator" value={stock.accelerators} />
            <ScoreBox label="GEM" value={stock.gem} />
          </div>
          <p className="text-xs text-gray-500 mt-3">Click to view fundamentals ↩</p>
        </div>

        {/* Back Side */}
        <div className="absolute inset-0 bg-gray-800 rounded-lg p-4 shadow-lg rotate-y-180 backface-hidden">
          <h3 className="text-md font-semibold mb-2 text-blue-400">
            Fundamentals
          </h3>
          <div className="grid grid-cols-2 gap-1 text-sm">
            <span>MC: {stock.market_cap}</span>
            <span>PE: {stock.pe_ratio}</span>
            <span>PB: {stock.pb_ratio}</span>
            <span>PEG: {stock.peg_ratio}</span>
            <span>ROE: {stock.roe}</span>
            <span>ROCE: {stock.roce}</span>
            <span>D/E: {stock.debt_to_equity}</span>
            <span>Prom: {stock.promoter_holding}%</span>
            <span>EBITDA: {stock.ebitda_margin}</span>
            <span>EV/EBITDA: {stock.ev_ebitda}</span>
          </div>
          <p className="text-xs text-gray-500 mt-3">Click to flip back ↪</p>
        </div>
      </div>
    </div>
  );
}

// 🧠 Page Component
export default function ScreenNDiscover() {
  const [data, setData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sector, setSector] = useState('All');
  const [subSector, setSubSector] = useState('All');
  const [filterType, setFilterType] = useState<'All' | 'Core' | 'Accelerator' | 'GEM'>('All');

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://localhost:8000/analytics/score');
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const sectors = Array.from(new Set(data.map(d => d.sector))).sort();
  const subSectors = Array.from(
    new Set(
      data.filter(s => sector === 'All' || s.sector === sector).map(s => s.sub_sector)
    )
  ).sort();

  const filteredData = data.filter(d => {
    const matchSearch = d.symbol.toLowerCase().includes(search.toLowerCase());
    const matchSector = sector === 'All' || d.sector === sector;
    const matchSubSector = subSector === 'All' || d.sub_sector === subSector;
    let matchFilter = true;

    if (filterType === 'Core') matchFilter = d.core > 0.2;
    else if (filterType === 'Accelerator') matchFilter = d.accelerators > 0.2;
    else if (filterType === 'GEM') matchFilter = d.gem > 0.2;

    return matchSearch && matchSector && matchSubSector && matchFilter;
  });

  if (loading) return <div className="text-white p-4">Loading data...</div>;

  return (
    <div className="p-4 space-y-4 text-white">
      {/* Filters Section */}
      <div className="flex justify-between flex-wrap mb-4 items-center">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search symbol..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="p-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none"
          />

          <select
            value={sector}
            onChange={e => setSector(e.target.value)}
            className="p-2 rounded bg-gray-800 text-white border border-gray-600 w-64"
          >
            <option value="All">All Sectors</option>
            {sectors.map(sec => (
              <option key={sec} value={sec}>
                {sec}
              </option>
            ))}
          </select>

          <select
            value={subSector}
            onChange={e => setSubSector(e.target.value)}
            className="p-2 rounded bg-gray-800 text-white border border-gray-600 w-72"
          >
            <option value="All">All Sub Sectors</option>
            {subSectors.map(sec => (
              <option key={sec} value={sec}>
                {sec}
              </option>
            ))}
          </select>

          <span className="flex ml-6 text-white mt-3">Results: {filteredData.length}</span>
        </div>

        <div className="flex gap-2">
          {['All', 'Core', 'Accelerator', 'GEM'].map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type as any)}
              className={`px-3 py-1 rounded text-sm font-semibold transition ${
                filterType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Stock Cards Grid */}
      {filteredData.length === 0 ? (
        <div className="text-gray-400">No stocks found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {filteredData.map(stock => (
            <StockCard key={stock.symbol} stock={stock} />
          ))}
        </div>
      )}
    </div>
  );
}
