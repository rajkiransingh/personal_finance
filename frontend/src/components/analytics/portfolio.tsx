'use client';

import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ComposedChart,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Treemap
} from 'recharts';

import { PortfolioResponse } from './types/portfolio';
import CustomTooltip from "../charts/chart_tooltip"

export default function PortfolioPage() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeChart, setActiveChart] = useState<'allocation'|'Sub Allocations'|'drift'|'rebalance'|'comparison'|'radar'>('allocation');

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/api/portfolio', { method: 'GET' });

        if (!response.ok) {
          const txt = await response.text().catch(() => '');
          throw new Error(`Failed to fetch data: ${response.status} ${response.statusText} ${txt}`);
        }
        const portfolioData: PortfolioResponse = await response.json();
        setData(portfolioData);
      } catch (err: any) {
        console.error('Error fetching portfolio data:', err);
        setError(`Failed to load portfolio data. ${err?.message ?? err}`);
      } finally {
        setLoading(false);
      }
    };
    fetchPortfolioData();
  }, []);

  if (loading) {
    return <div className="text-center py-8 text-[var(--color-text-secondary)]">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-400">{error}</div>;
  }

  if (!data) {
    return <div className="text-center py-8 text-[var(--color-text-secondary)]">No data available</div>;
  }

  const COLORS: Record<string, string> = {
    ETFs: '#3b82f6',
    MutualFunds: '#10b981',
    Stocks: '#f59e0b',
    Metals: '#fbbf24',
    Crypto: '#8b5cf6',
    RealEstate: '#ec4899'
  };

  const STATUS_COLORS: Record<string, string> = {
    'OK': '#10b981',
    'Drifted': '#f59e0b',
    'Significant drift': '#ef4444'
  };

  // Transform data for charts
  const allocationData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    current: value.current_value,
    target: value.ideal_value,
    currentPct: value.current_pct,
    targetPct: value.target_pct
  }));

  const pieCurrentData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    value: value.current_value
  }));

  const pieTargetData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    value: value.target_pct
  }));

  const driftData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    drift: +(value.current_pct - value.target_pct).toFixed(2),
    status: value.status
  }));

  const rebalancePlanData = Object.entries(data.rebalance_plan).map(([key, value]) => ({
    name: key,
    amount: value
  }));

  const radarData = Object.entries(data.categories).map(([key, value]) => ({
    category: key,
    Current: value.current_pct,
    Target: value.target_pct
  }));

  const formatCurrency = (value: number): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '₹0.00';

  const absValue = Math.abs(value);

  if (absValue >= 10000000) {
    return `₹${(value / 10000000).toFixed(2)}Cr`;
  } else if (absValue >= 100000) {
    return `₹${(value / 100000).toFixed(2)}L`;
  } else if (absValue >= 1000) {
    return `₹${(value / 1000).toFixed(2)}K`;
  } else {
    return `₹${value.toFixed(2)}`;
  }
};

  const formatPercent = (value: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) return '0.0%';
    return `${value.toFixed(1)}%`;
  };

  return (
    <div className="space-y-6 bg-[var(--color-bg)]">
      <div>
        {/* Header with Title and Data Refresh Button */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-semibold"> Portfolio Rebalancing </h1>
          <div className="flex gap-6 text-lg">
            <div>Total Value: <span className="font-semibold text-blue-400">{formatCurrency(data.total_value)}</span></div>
            <div>Next SIP: <span className="font-semibold text-green-400">{formatCurrency(data.next_monthly_sip)}</span></div>
          </div>
        </div>

        {/* Chart Selector */}
        <div className="flex gap-2 mb-4 flex-wrap bg-[var(--color-card)] p-4 rounded-lg">
          {['allocation', 'Sub Allocations', 'drift', 'rebalance', 'comparison', 'radar'].map((chart) => (
            <button
              key={chart}
              onClick={() => setActiveChart(chart as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeChart === chart
                  ? 'bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-2 px-4 rounded-md text-sm font-semibold transition'
                  : 'bg-[var(--color-bg-lighter)] hover:bg-[var(--color-accent-hover)] hover:text-black'
              }`}
            >
              {chart.charAt(0).toUpperCase() + chart.slice(1)}
            </button>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="card grid grid-cols-1 lg:grid-cols-2 bg-[var(--color-card)] p-4 rounded-lg h-[550px] mb-4">

          {/* Current vs Target Allocation */}
          {activeChart === 'allocation' && (
            <>
              {/* Current Allocation */}
                <ResponsiveContainer width="100%" height={530}>
                  <PieChart>
                    <Pie
                      data={pieCurrentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(1)}%`}
                      outerRadius={220}
                      innerRadius={150}   // <-- makes it a doughnut
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieCurrentData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[entry.name as keyof typeof COLORS] ?? '#8884d8'}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                  </PieChart>
                </ResponsiveContainer>

                {/* Target Allocation */}
                <ResponsiveContainer width="100%" height={530}>
                  <PieChart>
                    <Pie
                      data={pieTargetData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name} ${value}%`}
                      outerRadius={220}
                      innerRadius={150}       // <-- makes it a doughnut
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieTargetData.map((entry, index) => (
                        <Cell
                          key={`cell-target-${index}`}
                          fill={COLORS[entry.name as keyof typeof COLORS] ?? '#8884d8'}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                  </PieChart>
                </ResponsiveContainer>
            </>
          )}

          {/* Sub Allocations */}
          {activeChart === 'Sub Allocations' && (
            <div className="col-span-2">
                <h2 className="text-xl font-semibold text-white mb-4">Subcategories: Current vs Target</h2>
                <ResponsiveContainer width="100%" height={Object.keys(data.categories).length * 80}>
                  <ComposedChart
                    layout="vertical"
                    data={Object.entries(data.categories).flatMap(([catKey, catValue]) =>
                      Object.entries(catValue.sub_allocations || {}).map(([subKey, subValue]: [string, any]) => ({
                        name: `${catKey} - ${subKey}`,
                        current: subValue.current_value,
                        target: subValue.ideal_value,
                      }))
                    )}
                    margin={{ top: 10, right: 10, left: 100, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9ca3af" tickFormatter={(v) => formatCurrency(v)} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={100}
                      stroke="#9ca3af"
                      tick={{ fontSize: 10, dy: 2 }}
                    />
                    <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                    <Legend />
                    <Bar dataKey="current" fill="#3b82f6" name="Current" barSize={14} radius={[0, 8, 8, 0]} />
                    <Bar dataKey="target" fill="#10b981" name="Target" barSize={14} radius={[0, 8, 8, 0]} />
                  </ComposedChart>
                </ResponsiveContainer>
            </div>
          )}

          {/* Drift Analysis */}
          {activeChart === 'drift' && (
            <div>
              <h2 className="text-xl font-semibold text-white">Allocation Drift</h2>
              <ResponsiveContainer width={1400} height={400}>
                <BarChart data={driftData} layout="vertical" >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9ca3af" />
                  <YAxis dataKey="name" type="category" stroke="#9ca3af" width={140} />
                  <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                  <Bar dataKey="drift" radius={[0, 8, 8, 0]}>
                    {driftData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.drift > 0 ? '#10b981' : '#ef4444'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Rebalance Plan */}
          {activeChart === 'rebalance' && (
            <div>
              <h2 className="text-xl font-semibold text-white">Next Month's Rebalance Plan</h2>
              <ResponsiveContainer width={1400} height={400}>
                <BarChart data={rebalancePlanData} margin={{ top: 20, right: 30, left: 60, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                  <Bar dataKey="amount" fill="#3b82f6" radius={[8, 8, 0, 0]}>
                    {rebalancePlanData.map((entry, index) => (
                      <Cell key={`cell-reb-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] ?? '#3b82f6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Current vs Target Comparison */}
          {activeChart === 'comparison' && (
            <div>
              <h2 className="text-xl font-semibold text-white">Current vs Target Values</h2>
              <ResponsiveContainer width={1400} height={400}>
                <ComposedChart data={allocationData} margin={{ top: 20, right: 30, left: 60, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" tickFormatter={(value) => formatCurrency(value)}/>
                  <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                  <Legend />
                  <Bar dataKey="current" fill="#3b82f6" name="Current" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="target" fill="#10b981" name="Target" radius={[8, 8, 0, 0]} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Radar Chart */}
          {activeChart === 'radar' && (
            <div>
              <h2 className="text-xl font-semibold text-white">Allocation Radar</h2>
              <ResponsiveContainer width={1400} height={400}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#08306F" />
                  <PolarAngleAxis dataKey="category" stroke="#9ca3af" />
                  <PolarRadiusAxis stroke="#9ca3af" />
                  <Radar name="Current" dataKey="Current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Radar name="Target" dataKey="Target" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                  <Legend />
                  <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-4">
          {Object.entries(data.categories).map(([key, value]) => (
            <div key={key} className="card bg-[var(--color-card)] rounded-xl p-4 shadow-xl">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-white">{key}</h3>
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: STATUS_COLORS[value.status] || '#6b7280' }}
                />
              </div>
              <div className="text-2xl font-bold text-white mb-1">
                {formatPercent(value.current_pct)}
              </div>
              <div className="text-sm text-slate-400">
                Target: {formatPercent(value.target_pct)}
              </div>
              <div className={`text-sm font-medium mt-2 ${
                value.gap > 0 ? 'text-red-400' : 'text-green-400'
              }`}>
                {value.gap > 0 ? '+' : ''}{formatCurrency(value.gap)}
              </div>
            </div>
          ))}
        </div>
    </div>
  );
}
