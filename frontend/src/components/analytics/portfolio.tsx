'use client';

import { apiFetch } from "@/lib/api";

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
} from 'recharts';

import { PortfolioResponse } from '@/types/portfolio';
import CustomTooltip from "../charts/chart_tooltip";

const COLORS: Record<string, string> = {
  ETFs: 'var(--chart-2)',
  MutualFunds: 'var(--chart-5)',
  Stocks: 'var(--chart-3)',
  Metals: 'var(--chart-1)',
  Crypto: 'var(--chart-4)',
  RealEstate: 'var(--chart-6)',
};

const formatCurrency = (value: number): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '₹0.00';
  const absValue = Math.abs(value);
  if (absValue >= 10000000) {
    return `₹${(value / 10000000).toFixed(2)} Cr`;
  } else if (absValue >= 100000) {
    return `₹${(value / 100000).toFixed(2)} L`;
  } else if (absValue >= 1000) {
    return `₹${(value / 1000).toFixed(2)} K`;
  } else {
    return `₹${value.toFixed(2)}`;
  }
};

const formatPercent = (value: number) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0.0%';
  return `${value.toFixed(1)}%`;
};

const axisTick = { fill: 'var(--color-muted)', fontSize: 11 };
const gridStroke = 'var(--color-rule)';

type ChartTab = 'allocation' | 'drift' | 'rebalance' | 'comparison';

export default function PortfolioPage() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeChart, setActiveChart] = useState<ChartTab>('allocation');

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiFetch('/api/portfolio', { method: 'GET' });

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
    return (
      <div className="space-y-6 py-4" aria-busy="true" aria-label="Loading portfolio">
        <div className="skeleton h-9 w-1/3" />
        <div className="skeleton h-12 w-2/3" />
        <div className="skeleton h-[500px] w-full" />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-28" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card mx-auto my-12 max-w-lg p-8 text-center">
        <h3 className="section-title">Portfolio unavailable</h3>
        <p className="page-sub mx-auto">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="empty-state card">
        <p className="state-title">No portfolio data available</p>
        <p>Add holdings and the allocation view fills itself from the ledger.</p>
      </div>
    );
  }

  // Transform data for charts
  const allocationData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    current: value.current_value,
    target: value.ideal_value,
    currentPct: value.current_pct,
    targetPct: value.target_pct,
  }));

  const pieCurrentData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    value: value.current_value,
  }));

  const pieTargetData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    value: value.target_pct,
  }));

  const driftData = Object.entries(data.categories).map(([key, value]) => ({
    name: key,
    drift: +(value.current_pct - value.target_pct).toFixed(2),
    status: value.status,
  }));

  const rebalancePlanData = Object.entries(data.rebalance_plan).map(([key, value]) => ({
    name: key,
    amount: value,
  }));

  const tabs: { key: ChartTab; label: string }[] = [
    { key: 'allocation', label: 'Allocation overview' },
    { key: 'drift', label: 'Allocation drift' },
    { key: 'rebalance', label: 'Rebalance plan' },
    { key: 'comparison', label: 'Current vs target' },
  ];

  const chartTitle = (title: string, note: string) => (
    <div className="card-head-plain">
      <h2 className="card-title">{title}</h2>
      <span className="card-note">{note}</span>
    </div>
  );

  return (
    <div className="space-y-6 pb-8">
      {/* Page title and high-level KPIs */}
      <div className="page-head">
        <div>
          <h1 className="page-title">Portfolio rebalancing</h1>
          <p className="page-sub">
            Target asset drift detection, SIP auto-balancing, and subcategory analysis.
          </p>
        </div>

        <div className="flex flex-wrap items-stretch gap-3">
          <div className="rounded-[var(--radius-panel)] border border-[var(--color-rule)] bg-[var(--color-surface)] px-4 py-2">
            <span className="label">Total portfolio value</span>
            <span className="mt-0.5 block text-[length:var(--text-lg)] font-semibold tabular-nums text-[var(--color-ink)]">
              {formatCurrency(data.total_value)}
            </span>
          </div>

          <div className="rounded-[var(--radius-panel)] border border-[var(--color-rule)] bg-[var(--color-surface)] px-4 py-2">
            <span className="label">Next monthly SIP</span>
            <span className="mt-0.5 block text-[length:var(--text-lg)] font-semibold tabular-nums text-[var(--color-primary)]">
              {formatCurrency(data.next_monthly_sip)}
            </span>
          </div>
        </div>
      </div>

      {/* Chart Selector Segmented Control */}
      <div className="seg" role="tablist" aria-label="Portfolio chart">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            aria-selected={activeChart === tab.key}
            onClick={() => setActiveChart(tab.key)}
            className={`seg-item ${activeChart === tab.key ? 'is-active' : ''}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Chart Visual Surface */}
      <section className="card p-5 sm:p-6">
        {/* Allocation Tab (Dual Doughnuts) */}
        {activeChart === 'allocation' && (
          <div>
            <div className="card-head-plain flex-wrap">
              <h2 className="card-title">Current holdings vs target allocation</h2>
              <div className="flex items-center gap-4 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-[var(--chart-2)]" aria-hidden="true" /> Current value
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-[var(--chart-5)]" aria-hidden="true" /> Target %
                </span>
              </div>
            </div>

            <div className="grid h-[420px] grid-cols-1 gap-8 lg:grid-cols-2">
              {/* Current Allocation */}
              <div className="flex min-w-0 flex-col items-center">
                <span className="mb-2 text-[length:var(--text-xs)] font-medium text-[var(--color-muted)]">Current value distribution</span>
                <ResponsiveContainer width="100%" height={380}>
                  <PieChart>
                    <Pie
                      data={pieCurrentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: any) => `${props.name} ${(props.percent * 100).toFixed(1)}%`}
                      outerRadius={130}
                      innerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                      stroke="var(--color-surface)"
                      strokeWidth={2}
                    >
                      {pieCurrentData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[entry.name] ?? 'var(--color-muted)'}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Target Allocation */}
              <div className="flex min-w-0 flex-col items-center">
                <span className="mb-2 text-[length:var(--text-xs)] font-medium text-[var(--color-muted)]">Target policy allocation</span>
                <ResponsiveContainer width="100%" height={380}>
                  <PieChart>
                    <Pie
                      data={pieTargetData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name} ${value}%`}
                      outerRadius={130}
                      innerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                      stroke="var(--color-surface)"
                      strokeWidth={2}
                    >
                      {pieTargetData.map((entry, index) => (
                        <Cell
                          key={`cell-target-${index}`}
                          fill={COLORS[entry.name] ?? 'var(--color-muted)'}
                        />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Sub Allocations */}
        {activeChart === 'drift' && (
          <div>
            {chartTitle('Allocation drift (% variance)', 'Green is overweight, red is underweight')}
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={driftData} layout="vertical" margin={{ top: 10, right: 30, left: 100, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis
                  type="number"
                  stroke="var(--color-muted)"
                  tick={axisTick}
                  tickFormatter={(v) => `${v}%`}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="var(--color-muted)"
                  width={100}
                  tick={{ ...axisTick, fill: 'var(--color-ink-2)' }}
                />
                <Tooltip content={<CustomTooltip formatter={(v) => `${v.toFixed(1)}%`} />} />
                <Bar dataKey="drift" radius={[0, 4, 4, 0]}>
                  {driftData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.drift > 0 ? 'var(--color-success)' : 'var(--color-danger)'}
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
            {chartTitle("Next month's SIP allocation strategy", 'Recommended capital distribution')}
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={rebalancePlanData} margin={{ top: 20, right: 30, left: 60, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="name" stroke="var(--color-muted)" tick={{ ...axisTick, fill: 'var(--color-ink-2)' }} />
                <YAxis stroke="var(--color-muted)" tick={axisTick} tickFormatter={(v) => formatCurrency(v)} />
                <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                <Bar dataKey="amount" fill="var(--chart-2)" radius={[4, 4, 0, 0]}>
                  {rebalancePlanData.map((entry, index) => (
                    <Cell key={`cell-reb-${index}`} fill={COLORS[entry.name] ?? 'var(--chart-2)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Current vs Target Comparison */}
        {activeChart === 'comparison' && (
          <div>
            {chartTitle('Current vs target absolute values', 'Comparison across major asset classes')}
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={allocationData} margin={{ top: 20, right: 30, left: 60, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis dataKey="name" stroke="var(--color-muted)" tick={{ ...axisTick, fill: 'var(--color-ink-2)' }} />
                <YAxis stroke="var(--color-muted)" tick={axisTick} tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip content={<CustomTooltip formatter={(v) => formatCurrency(v)} />} />
                <Legend wrapperStyle={{ fontSize: 12, color: 'var(--color-ink-2)' }} />
                <Bar dataKey="current" fill="var(--chart-2)" name="Current value" radius={[4, 4, 0, 0]} />
                <Bar dataKey="target" fill="var(--chart-5)" name="Target value" radius={[4, 4, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}

      </section>

      {/* Asset Class Status Tiles */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(data.categories).map(([key, value]) => {
          const statusTone =
            value.status === 'OK'
              ? 'badge-positive'
              : value.status === 'Significant drift'
                ? 'badge-negative'
                : 'badge-warning';

          return (
            <div
              key={key}
              className="card flex flex-col justify-between p-4"
            >
              <div>
                <div className="mb-2 flex items-start justify-between gap-2">
                  <h3 className="text-[length:var(--text-sm)] font-semibold text-[var(--color-ink)]">{key}</h3>
                </div>
                <div className="text-[length:var(--text-xl)] font-semibold tabular-nums text-[var(--color-ink)]">
                  {formatPercent(value.current_pct)}
                </div>
                <div className="mt-0.5 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                  Target: {formatPercent(value.target_pct)}
                </div>
              </div>

              <div className="mt-3 border-t border-[var(--color-rule)] pt-2">
                <span className={`badge ${statusTone}`}>{value.status}</span>
                <div className={`mt-2 text-[length:var(--text-xs)] font-semibold tabular-nums ${
                  value.gap > 0 ? 'text-[var(--color-danger-text)]' : 'text-[var(--color-success-text)]'
                }`}>
                  {value.gap > 0 ? '+' : ''}{formatCurrency(value.gap)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
