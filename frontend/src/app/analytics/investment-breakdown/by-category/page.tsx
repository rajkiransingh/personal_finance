'use client';

import { useEffect, useState } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip 
} from 'recharts';
import CustomTooltip from '@/components/charts/chart_tooltip';

interface CategoryData {
  total_cost: number;
  current_value: number;
  xirr: number;
}

interface PortfolioSummary {
  [key: string]: CategoryData;
}

const COLORS: Record<string, string> = {
  Stocks: '#f59e0b',
  Mutual_funds: '#10b981',
  Gold: '#fbbf24',
  Silver: '#94a3b8',
  Real_estate: '#ec4899',
  Crypto: '#8b5cf6',
  Others: '#3b82f6'
};

const formatCurrency = (value: number) => 
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

const normalizeCategory = (cat: string) => cat.charAt(0).toUpperCase() + cat.slice(1);

export default function InvestmentBreakdown() {
  const [data, setData] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://localhost:8000/summary/portfolio');
        if (!res.ok) throw new Error('Failed to fetch data');
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError('Failed to load investment data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div className="p-8 text-center text-[var(--color-text-secondary)]">Loading breakdown...</div>;
  if (error) return <div className="p-8 text-center text-red-400">{error}</div>;
  if (!data) return null;

  // Process Data for Visualization
  const categories = Object.keys(data);
  
  // 1. Totals
  const totalInvested = categories.reduce((sum, cat) => sum + data[cat].total_cost, 0);
  const totalCurrent = categories.reduce((sum, cat) => sum + data[cat].current_value, 0);
  const totalGain = totalCurrent - totalInvested;
  const overallXIRR = categories.reduce((sum, cat) => sum + (data[cat].xirr * data[cat].total_cost), 0) / (totalInvested || 1);

  // 2. Chart Data
  const pieData = categories.map(cat => {
    const name = normalizeCategory(cat);
    return {
      name: name,
      value: data[cat].current_value,
      fill: COLORS[name] || COLORS.Others
    };
  }).filter(d => d.value > 0);

  const barData = categories.map(cat => {
    const name = normalizeCategory(cat);
    return {
      name: name,
      Invested: data[cat].total_cost,
      Current: data[cat].current_value
    };
  }).filter(d => d.Invested > 0);

  return (
    <div className="space-y-6 text-[var(--color-text-primary)] p-6 bg-[var(--color-bg)] min-h-screen">
      <h1 className="text-3xl font-semibold mb-6">Investment Breakdown by Category</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Invested', value: formatCurrency(totalInvested), color: 'text-white' },
          { label: 'Current Value', value: formatCurrency(totalCurrent), color: 'text-green-400' },
          { label: 'Total Gain', value: formatCurrency(totalGain), color: totalGain >= 0 ? 'text-green-400' : 'text-red-400' },
          { label: 'Weighted XIRR', value: `${overallXIRR.toFixed(2)}%`, color: overallXIRR >= 0 ? 'text-green-400' : 'text-red-400' }
        ].map((card, idx) => (
          <div key={idx} className="bg-[var(--color-card)] p-6 rounded-lg shadow-lg">
            <h3 className="text-sm text-[var(--color-text-secondary)] uppercase tracking-wide mb-2">{card.label}</h3>
            <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Allocation Pie Chart */}
        <div className="bg-[var(--color-card)] p-6 rounded-lg shadow-lg h-[500px]">
          <h2 className="text-xl font-semibold mb-6 border-b border-gray-700 pb-2">Portfolio Allocation</h2>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={150}
                innerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} stroke="rgba(0,0,0,0)" />
                ))}
              </Pie>
              <RechartsTooltip content={<CustomTooltip formatter={(value: number) => formatCurrency(value)} />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Invested vs Current Bar Chart */}
        <div className="bg-[var(--color-card)] p-6 rounded-lg shadow-lg h-[500px]">
          <h2 className="text-xl font-semibold mb-6 border-b border-gray-700 pb-2">Invested vs Current Value</h2>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="name" stroke="#9ca3af" angle={-45} textAnchor="end" height={60} />
              <YAxis stroke="#9ca3af" tickFormatter={(val) => `₹${(val/100000).toFixed(0)}L`} />
              <Tooltip 
                 cursor={{fill: 'rgba(255,255,255,0.05)'}}
                 content={<CustomTooltip formatter={(value: number) => formatCurrency(value)} />}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="Invested" fill="#3b82f6" name="Invested Amount" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Current" fill="#10b981" name="Current Value" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-[var(--color-card)] p-6 rounded-lg shadow-lg overflow-x-auto">
      <h2 className="text-xl font-semibold mb-6 border-b border-gray-700 pb-2">Detailed Breakdown</h2>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-700 text-[var(--color-text-secondary)] text-sm uppercase tracking-wider">
              <th className="py-4 px-2">Category</th>
              <th className="py-4 px-2 text-right">Invested</th>
              <th className="py-4 px-2 text-right">Current Value</th>
              <th className="py-4 px-2 text-right">Abs. Return</th>
              <th className="py-4 px-2 text-center">XIRR</th>
              <th className="py-4 px-2 text-center">Allocation</th>
            </tr>
          </thead>
          <tbody className="text-sm font-medium">
            {categories.map((cat, idx) => {
               const row = data[cat];
               const name = normalizeCategory(cat);
               const gain = row.current_value - row.total_cost;
               const allocation = (row.current_value / totalCurrent) * 100;
               return (
                 <tr key={cat} className={`border-b border-gray-800 hover:bg-white/5 transition-colors ${idx === categories.length - 1 ? 'border-none' : ''}`}>
                   <td className="py-4 px-2 flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[name] || COLORS.Others }}></div>
                      {name}
                   </td>
                   <td className="py-4 px-2 text-right font-mono">{formatCurrency(row.total_cost)}</td>
                   <td className="py-4 px-2 text-right font-mono text-[var(--color-text-primary)]">{formatCurrency(row.current_value)}</td>
                   <td className={`py-4 px-2 text-right font-mono ${gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                     {formatCurrency(gain)}
                   </td>
                   <td className={`py-4 px-2 text-center font-mono ${row.xirr >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                     {row.xirr.toFixed(1)}%
                   </td>
                   <td className="py-4 px-2 text-center text-[var(--color-text-secondary)]">
                     {allocation.toFixed(1)}%
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
