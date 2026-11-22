'use client';

import { apiFetch } from "@/lib/api";

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { Plus, TrendingUp } from 'lucide-react';

interface DividendRecord {
  id: number;
  stock_symbol: string;
  stock_name: string | null;
  amount: number;
  currency_code: string;
  date: string;
  value_inr: number;
}

type Period = 'lifetime' | 'current' | 'last' | 'last3';

const PERIOD_LABELS: Record<Period, string> = {
  lifetime: 'Lifetime',
  current: 'Current year',
  last: 'Last year',
  last3: 'Last 3 years',
};

const formatCurrency = (value: number): string => {
  if (!Number.isFinite(value)) return '₹ 0';
  const abs = Math.abs(value);
  if (abs >= 10000000) return `₹ ${(value / 10000000).toFixed(2)} Cr`;
  if (abs >= 100000) return `₹ ${(value / 100000).toFixed(2)} L`;
  if (abs >= 1000) return `₹ ${(value / 1000).toFixed(1)} K`;
  return `₹ ${value.toFixed(0)}`;
};

export default function DividendsPage() {
  const [records, setRecords] = useState<DividendRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<Period>('lifetime');

  useEffect(() => {
    let active = true;
    apiFetch('/api/dividends/analytics')
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        return res.json();
      })
      .then((data: DividendRecord[]) => {
        if (active) setRecords(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (active) setError(err?.message || 'Could not load dividends');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const currentYear = new Date().getFullYear();

  const filtered = useMemo(
    () =>
      records.filter((row) => {
        const year = Number(row.date.slice(0, 4));
        if (period === 'lifetime') return true;
        if (period === 'current') return year === currentYear;
        if (period === 'last') return year === currentYear - 1;
        return year >= currentYear - 2;
      }),
    [records, period, currentYear]
  );

  const summary = useMemo(() => {
    const byStock = new Map<string, { symbol: string; name: string; total: number; count: number }>();
    const byYear = new Map<string, number>();
    let total = 0;

    for (const row of filtered) {
      const value = Number(row.value_inr) || 0;
      total += value;
      const symbol = row.stock_symbol || 'Unknown';
      const stock = byStock.get(symbol) || {
        symbol,
        name: row.stock_name || symbol,
        total: 0,
        count: 0,
      };
      stock.total += value;
      stock.count += 1;
      byStock.set(symbol, stock);

      const year = row.date.slice(0, 4);
      byYear.set(year, (byYear.get(year) || 0) + value);
    }

    const stocks = Array.from(byStock.values()).sort((a, b) => b.total - a.total);
    const years = Array.from(byYear.entries())
      .map(([year, amount]) => ({ year, amount }))
      .sort((a, b) => a.year.localeCompare(b.year));

    return { total, stocks, years, payments: filtered.length };
  }, [filtered]);

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <h1 className="page-title">Dividend income</h1>
          <p className="page-sub">
            Dividends received from your holdings, summed by stock and by year.
          </p>
        </div>
        <Link href="/transactions?tab=dividend" className="btn btn-primary">
          <Plus size={15} aria-hidden="true" />
          Add dividend
        </Link>
      </div>

      <div className="seg" role="tablist" aria-label="Dividend period">
        {(Object.keys(PERIOD_LABELS) as Period[]).map((key) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={period === key}
            onClick={() => setPeriod(key)}
            className={`seg-item ${period === key ? 'is-active' : ''}`}
          >
            {PERIOD_LABELS[key]}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4" aria-busy="true" aria-label="Loading dividends">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="skeleton h-28" />
            ))}
          </div>
          <div className="skeleton h-80 w-full" />
        </div>
      ) : error ? (
        <div className="card p-8 text-center">
          <h2 className="section-title">Dividends unavailable</h2>
          <p className="page-sub mx-auto">{error}</p>
        </div>
      ) : records.length === 0 ? (
        <div className="card empty-state">
          <p className="state-title">No dividends recorded yet</p>
          <p className="text-[length:var(--text-sm)]">Add a dividend and it will appear in this view.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="card kpi-card card-mint p-5">
              <div className="label">Total received</div>
              <div className="stat-value mt-2">{formatCurrency(summary.total)}</div>
              <p className="mt-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                {PERIOD_LABELS[period]}
              </p>
            </div>
            <div className="card kpi-card card-violet p-5">
              <div className="label">Stocks paying</div>
              <div className="stat-value mt-2">{summary.stocks.length}</div>
              <p className="mt-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                Distinct symbols in this period
              </p>
            </div>
            <div className="card kpi-card card-sky p-5">
              <div className="label">Payments</div>
              <div className="stat-value mt-2">{summary.payments}</div>
              <p className="mt-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                Individual credit entries
              </p>
            </div>
            <div className="card kpi-card card-amber p-5">
              <div className="label">Largest payer</div>
              <div className="mt-2 truncate text-[var(--text-lg)] font-extrabold text-[var(--color-ink)]">
                {summary.stocks[0]?.symbol || 'None'}
              </div>
              <p className="mt-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                {summary.stocks[0] ? formatCurrency(summary.stocks[0].total) : 'No dividends'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">
            <section className="card flex flex-col">
              <div className="card-head">
                <div>
                  <h2 className="card-title">Dividend by stock</h2>
                  <p className="card-note">Largest contributors in the selected period</p>
                </div>
              </div>
              <div className="flex-1 p-5">
                {summary.stocks.length === 0 ? (
                  <div className="empty-state">
                    <p className="state-title">Nothing in this period</p>
                    <p className="text-[length:var(--text-sm)]">Try a wider range.</p>
                  </div>
                ) : (
                  <div className="h-[340px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        layout="vertical"
                        data={summary.stocks.slice(0, 8)}
                        margin={{ top: 8, right: 24, left: 8, bottom: 8 }}
                      >
                        <CartesianGrid stroke="var(--color-rule)" strokeDasharray="3 3" horizontal={false} />
                        <XAxis
                          type="number"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: 'var(--color-muted)', fontSize: 11 }}
                          tickFormatter={(value) => formatCurrency(value)}
                        />
                        <YAxis
                          type="category"
                          dataKey="symbol"
                          width={90}
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: 'var(--color-ink-2)', fontSize: 11 }}
                        />
                        <Tooltip
                          cursor={{ fill: 'var(--color-well)' }}
                          content={({ active, payload }) =>
                            active && payload?.length ? (
                              <div className="rounded-[var(--radius-panel)] border border-[var(--color-edge)] bg-[var(--color-surface)] p-2.5 text-[length:var(--text-xs)] shadow-[var(--shadow-pop)]">
                                <span className="font-bold text-[var(--color-ink)]">{payload[0].payload.name}</span>
                                <span className="ml-2 tabular-nums text-[var(--color-ink-2)]">
                                  {formatCurrency(Number(payload[0].value ?? 0))}
                                </span>
                              </div>
                            ) : null
                          }
                        />
                        <Bar dataKey="total" fill="var(--chart-5)" radius={[0, 4, 4, 0]} barSize={16} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </section>

            <section className="card flex flex-col">
              <div className="card-head">
                <div>
                  <h2 className="card-title">By year</h2>
                  <p className="card-note">Totals in the selected range</p>
                </div>
              </div>
              <div className="flex-1 space-y-3 p-5">
                {summary.years.length === 0 ? (
                  <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">No years to show.</p>
                ) : (
                  summary.years.map((entry) => (
                    <div key={entry.year}>
                      <div className="flex items-center justify-between text-[length:var(--text-sm)]">
                        <span className="font-medium text-[var(--color-ink-2)]">{entry.year}</span>
                        <span className="font-semibold tabular-nums text-[var(--color-ink)]">
                          {formatCurrency(entry.amount)}
                        </span>
                      </div>
                      <div className="meter mt-1.5">
                        <span
                          style={
                            {
                              '--value':
                                summary.total > 0 ? Math.min(entry.amount / summary.total, 1) : 0,
                            } as React.CSSProperties
                          }
                          aria-hidden="true"
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>

          <section className="card overflow-hidden">
            <div className="card-head">
              <div>
                <h2 className="card-title">Stock-wise details</h2>
                <p className="card-note">Every paying stock in the selected period</p>
              </div>
              <span className="badge badge-neutral">{summary.stocks.length} stocks</span>
            </div>
            <div className="overflow-x-auto px-2 sm:px-3">
              <table className="table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Company</th>
                    <th className="num">Payments</th>
                    <th className="num">Total received</th>
                    <th className="num">Share</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.stocks.map((stock) => (
                    <tr key={stock.symbol}>
                      <td className="font-semibold text-[var(--color-ink)]">{stock.symbol}</td>
                      <td className="text-[var(--color-ink-2)]">{stock.name}</td>
                      <td className="num">{stock.count}</td>
                      <td className="num font-semibold text-[var(--color-ink)]">
                        {formatCurrency(stock.total)}
                      </td>
                      <td className="num text-[var(--color-muted)]">
                        {summary.total > 0 ? ((stock.total / summary.total) * 100).toFixed(1) : '0.0'}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="border-t border-[var(--color-rule)] px-5 py-3 text-[length:var(--text-xs)] text-[var(--color-muted)]">
              <TrendingUp size={13} aria-hidden="true" className="mr-1 inline" />
              Amounts are stored in the currency received and converted to INR at current rates.
            </div>
          </section>
        </>
      )}
    </div>
  );
}
