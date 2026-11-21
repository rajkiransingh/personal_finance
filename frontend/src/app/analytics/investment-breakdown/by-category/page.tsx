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
  Stocks: 'var(--chart-3)',
  'Mutual funds': 'var(--chart-5)',
  Gold: 'var(--chart-1)',
  Silver: 'var(--chart-7)',
  'Real estate': 'var(--chart-6)',
  Crypto: 'var(--chart-4)',
  Others: 'var(--chart-2)'
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

const normalizeCategory = (cat: string) =>
  cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

const axisTick = { fill: 'var(--color-muted)', fontSize: 11 };

export default function InvestmentBreakdown() {
  const [data, setData] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/summary/portfolio');
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

  if (loading) {
    return (
      <div className="space-y-6 py-4" aria-busy="true" aria-label="Loading investment breakdown">
        <div className="skeleton h-9 w-1/3" />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-28" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="skeleton h-96" />
          <div className="skeleton h-96" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card mx-auto my-12 max-w-lg p-8 text-center">
        <h3 className="section-title">Breakdown unavailable</h3>
        <p className="page-sub mx-auto">{error}</p>
      </div>
    );
  }

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
    <div className="space-y-6 pb-8">
      {/* Page Title */}
      <div className="page-head">
        <div>
          <h1 className="page-title">Investment breakdown by category</h1>
          <p className="page-sub">
            Comprehensive cost basis, market valuation, and annualized XIRR yields.
          </p>
        </div>
        <span className="badge badge-neutral">{categories.length} categories</span>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
        {[
          { label: 'Total invested capital', value: formatCurrency(totalInvested), color: 'text-[var(--color-ink)]' },
          { label: 'Current valuation', value: formatCurrency(totalCurrent), color: 'text-[var(--color-ink)]' },
          {
            label: 'Total net gain / loss',
            value: formatCurrency(totalGain),
            color: totalGain >= 0 ? 'text-[var(--color-success-text)]' : 'text-[var(--color-danger-text)]',
            badge: totalGain >= 0 ? `+${((totalGain/totalInvested)*100).toFixed(1)}%` : `${((totalGain/totalInvested)*100).toFixed(1)}%`
          },
          {
            label: 'Weighted XIRR',
            value: `${overallXIRR.toFixed(2)}%`,
            color: overallXIRR >= 0 ? 'text-[var(--color-success-text)]' : 'text-[var(--color-danger-text)]',
            badge: 'Annualized'
          }
        ].map((card, idx) => (
          <div key={idx} className="card flex flex-col justify-between p-5">
            <div className="mb-2 flex items-start justify-between gap-2">
              <span className="label">{card.label}</span>
              {card.badge && (
                <span className="badge badge-neutral">{card.badge}</span>
              )}
            </div>
            <p className={`stat-value stat-value-sm ${card.color}`}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

        {/* Allocation Pie Chart */}
        <section className="card flex h-[480px] flex-col p-5 sm:p-6">
          <div className="card-head-plain border-b border-[var(--color-rule)] pb-3">
            <h2 className="card-title">Portfolio allocation</h2>
            <span className="card-note">By asset class</span>
          </div>
          <div className="mt-4 min-h-0 flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(0)}%`}
                  outerRadius={125}
                  innerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="var(--color-surface)"
                  strokeWidth={2}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} stroke="var(--color-surface)" strokeWidth={2} />
                  ))}
                </Pie>
                <RechartsTooltip content={<CustomTooltip formatter={(value: number) => formatCurrency(value)} />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Invested vs Current Bar Chart */}
        <section className="card flex h-[480px] flex-col p-5 sm:p-6">
          <div className="card-head-plain border-b border-[var(--color-rule)] pb-3">
            <h2 className="card-title">Invested vs current market value</h2>
            <span className="card-note">Capital performance</span>
          </div>
          <div className="mt-4 min-h-0 flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 20, right: 20, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-rule)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--color-muted)" angle={-30} textAnchor="end" height={50} tick={{ ...axisTick, fill: 'var(--color-ink-2)' }} />
                <YAxis stroke="var(--color-muted)" tick={axisTick} tickFormatter={(val) => `₹${(val/100000).toFixed(0)}L`} />
                <Tooltip
                   content={<CustomTooltip formatter={(value: number) => formatCurrency(value)} />}
                />
                <Legend wrapperStyle={{ paddingTop: '10px', fontSize: 12, color: 'var(--color-ink-2)' }} />
                <Bar dataKey="Invested" fill="var(--chart-7)" name="Invested amount" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Current" fill="var(--chart-2)" name="Current value" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      {/* Detailed Breakdown Table */}
      <section className="card overflow-hidden">
        <div className="card-head">
          <h2 className="card-title">Detailed asset breakdown</h2>
          <span className="card-note">{categories.length} tracked categories</span>
        </div>
        <div className="overflow-x-auto px-2 sm:px-3">
          <table className="table">
            <thead>
              <tr>
                <th>Category</th>
                <th className="num">Invested capital</th>
                <th className="num">Current value</th>
                <th className="num">Absolute return</th>
                <th className="num">Annualized XIRR</th>
                <th className="num">Portfolio share</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => {
                 const row = data[cat];
                 const name = normalizeCategory(cat);
                 const gain = row.current_value - row.total_cost;
                 const allocation = totalCurrent > 0 ? (row.current_value / totalCurrent) * 100 : 0;
                 return (
                   <tr key={cat}>
                     <td>
                       <span className="flex items-center gap-2.5">
                         <span
                           className="h-2.5 w-2.5 shrink-0 rounded-full"
                           style={{ backgroundColor: COLORS[name] || COLORS.Others }}
                           aria-hidden="true"
                         />
                         <span className="font-semibold text-[var(--color-ink)]">{name}</span>
                       </span>
                     </td>
                     <td className="num text-[var(--color-ink-2)]">{formatCurrency(row.total_cost)}</td>
                     <td className="num font-semibold text-[var(--color-ink)]">{formatCurrency(row.current_value)}</td>
                     <td className={`num font-semibold ${gain >= 0 ? 'text-[var(--color-success-text)]' : 'text-[var(--color-danger-text)]'}`}>
                       {gain >= 0 ? `+${formatCurrency(gain)}` : formatCurrency(gain)}
                     </td>
                     <td className="num">
                       <span className={`badge ${row.xirr >= 0 ? 'badge-positive' : 'badge-negative'}`}>
                         {row.xirr >= 0 ? `+${row.xirr.toFixed(1)}%` : `${row.xirr.toFixed(1)}%`}
                       </span>
                     </td>
                     <td className="num text-[var(--color-muted)]">
                       {allocation.toFixed(1)}%
                     </td>
                   </tr>
                 );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
