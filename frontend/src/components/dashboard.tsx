'use client';

import Link from 'next/link';
import { useEffect, useState, useCallback } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { RotateCcw, TrendingUp, ShieldCheck, Calendar, ArrowDownLeft, ArrowUpRight, Landmark, Plus } from 'lucide-react';

import StatCard from "./cards/stat_cards";
import InvestmentPieChart from "./charts/assets_doughnut_chart";
import Corpus from "./cards/corpus_fund";
import InfoTooltip from "./info-tooltip";
import { DashboardData } from '@/types/dashboard';

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

const XIRR_NOTE =
  "Cost-weighted average of each asset class's XIRR. It is an estimate, not a true portfolio internal rate of return.";

const signedCurrency = (value: number) =>
  `${value >= 0 ? '+' : '-'}${formatCurrency(Math.abs(value))}`;

const signedPercent = (value: number) =>
  `${value > 0 ? '+' : value < 0 ? '-' : ''}${Math.abs(value).toFixed(2)}%`;

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/dashboard', { method: 'GET' });

      if (!response.ok) throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      const dashboardData: DashboardData = await response.json();
      setData(dashboardData);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Ensure the backend service is running.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="space-y-6 py-2" aria-busy="true" aria-label="Loading dashboard">
        <div className="skeleton h-10 w-1/3" />
        <div className="skeleton h-24 w-full" />
        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          <div className="skeleton h-32" />
          <div className="skeleton h-32" />
          <div className="skeleton h-32" />
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="skeleton h-96 lg:col-span-2" />
          <div className="skeleton h-96" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card mx-auto my-12 max-w-lg p-8 text-center">
        <h2 className="section-title">Service unreachable</h2>
        <p className="page-sub mx-auto">{error}</p>
        <button type="button" onClick={fetchDashboardData} className="btn btn-primary mt-6">
          <RotateCcw size={15} aria-hidden="true" />
          Retry connection
        </button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card empty-state">
        <p className="state-title">No financial data yet</p>
        <p>Add a first transaction and the dashboard fills itself from the ledger.</p>
        <Link href="/transactions" className="btn btn-primary mt-2">Open transactions</Link>
      </div>
    );
  }

  /* Base Data from the API call */
  const corpus = data.emergency_coverage;
  const income_data = data.income_ytd;
  const expense_data = data.expense_avg;
  const investment_data = data.investment_avg;
  const totalReturns = data.total_returns;
  const averageRoi = data.average_roi;
  const assets = data.assets;
  const breakdown = data.investment_breakdown ?? [];

  /* Computed metrics */
  const incomeChange = income_data?.change ?? 0;
  const incomeMetric = `${Math.abs(incomeChange).toFixed(1)}% vs last year`;

  const expenseChange = expense_data?.change ?? 0;
  const expenseMetric = `${Math.abs(expenseChange).toFixed(1)}% vs last year`;
  const expenseRatio = expense_data?.expense_ratio ?? 0;

  const investmentChange = investment_data?.change ?? 0;
  const investmentMetric = `${Math.abs(investmentChange).toFixed(1)}% vs last year`;
  const investmentRatio = investment_data?.investment_ratio ?? 0;

  const topCategory = (data.spending_categories?.[0]?.category ?? "None").replace(/_/g, " ");

  const formatMonth = (value: string | null) => {
    if (!value) return "No entries yet";
    const [year, month] = value.split("-").map(Number);
    return new Date(Date.UTC(year, month - 1, 1)).toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    });
  };

  const topContributor = breakdown[0];
  const returnRows = breakdown.filter(
    (row) => Number.isFinite(row.xirr) && row.xirr !== 0
  );
  const topSpending = (data.spending_categories ?? []).slice(0, 3);
  const totalExpense = expense_data?.expense ?? 0;

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <p className="greeting">Welcome back, Rajkiran 👋</p>
          <h1 className="page-title">Financial dashboard</h1>
          <p className="page-sub">
            Here’s how your money is doing today, straight from the live ledger.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={fetchDashboardData}
            disabled={refreshing}
            className="btn btn-secondary"
          >
            <RotateCcw
              size={14}
              aria-hidden="true"
              className={refreshing ? 'animate-spin text-[var(--color-primary)]' : ''}
            />
            {refreshing ? 'Syncing' : 'Refresh data'}
          </button>
          <Link href="/transactions" className="btn btn-primary">
            <Plus size={15} aria-hidden="true" />
            Add transaction
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.9fr_1fr]">
        <section className="hero-balance">
          <div className="flex min-h-[136px] flex-wrap items-center justify-between gap-6">
            <div>
              <div className="hero-balance-label">Net worth</div>
              <div className="hero-balance-value">{formatCurrency(data.net_worth ?? 0)}</div>
              <p className="mt-2 text-[length:var(--text-xs)] text-[color-mix(in_oklab,var(--color-primary-ink)_84%,transparent)]">
                Cash {formatCurrency(data.cash_balance ?? 0)} · Investments {formatCurrency(data.invested_current_value ?? 0)}
              </p>
            </div>

            <div className="hero-balance-sheet">
              <div className="hero-balance-sheet-row">
                <span>Assets</span>
                <b>{formatCurrency(data.total_assets ?? 0)}</b>
              </div>
              <div className="hero-balance-sheet-row">
                <span>Liabilities</span>
                <b>
                  {data.total_liabilities > 0
                    ? `-${formatCurrency(data.total_liabilities)}`
                    : formatCurrency(data.total_liabilities ?? 0)}
                </b>
              </div>
            </div>
          </div>
        </section>

        <Corpus
          percentage={corpus}
          required={data.emergency_fund_required}
          available={data.cash_balance}
          monthlyAverage={data.emergency_monthly_average}
        />
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <StatCard
          icon={<ArrowDownLeft size={16} aria-hidden="true" />}
          tone="mint"
          title="Income (YTD)"
          value={formatCurrency(income_data?.income ?? 0)}
          average={`Avg per month: ${formatCurrency(income_data?.average_income ?? 0)}`}
          comparison={`Prior year: ${formatCurrency(income_data?.income_last_year_to_date ?? 0)}`}
          metric={incomeMetric}
          metricValue={incomeChange}
          footnote={`Last entry ${formatMonth(income_data?.last_month ?? null)}`}
        />
        <StatCard
          icon={<ArrowUpRight size={16} aria-hidden="true" />}
          tone="coral"
          title="Expenses (YTD)"
          value={formatCurrency(expense_data?.expense ?? 0)}
          average={`Avg per month: ${formatCurrency(expense_data?.average_expense ?? 0)}`}
          comparison={`Prior year: ${formatCurrency(expense_data?.expense_last_year_to_date ?? 0)}`}
          metric={expenseMetric}
          metricValue={expenseChange}
          metricTone={expenseChange <= 0 ? "positive" : "negative"}
          noteBadge={`${expenseRatio.toFixed(1)}% of income`}
          footnote={`Top spend: ${topCategory} · ${formatMonth(expense_data?.last_month ?? null)}`}
        />
        <StatCard
          icon={<Landmark size={16} aria-hidden="true" />}
          tone="violet"
          title="Capital invested (YTD)"
          value={formatCurrency(investment_data?.investment ?? 0)}
          average={`Avg per month: ${formatCurrency(investment_data?.average_investment ?? 0)}`}
          comparison={`Prior year: ${formatCurrency(investment_data?.investment_last_year_to_date ?? 0)}`}
          metric={investmentMetric}
          metricValue={investmentChange}
          noteBadge={`${investmentRatio.toFixed(1)}% of income`}
          footnote={`Portfolio cost ${formatCurrency(data.total_invested_cost ?? 0)} · ${investment_data?.active_sip_count ?? 0} active SIPs`}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="card flex flex-col lg:col-span-2">
          <div className="card-head">
            <div>
              <h2 className="card-title">Asset and net worth distribution</h2>
              <p className="card-note">Liquid cash reserves and market investments, combined</p>
            </div>
            <span className="badge badge-neutral">Active allocations</span>
          </div>

          <div className="flex flex-1 items-center p-5">
            <InvestmentPieChart earnings={assets} />
          </div>
        </section>

        <section className="card flex flex-col justify-between">
          <div className="card-head">
            <div>
              <h2 className="card-title">Investment returns</h2>
              <p className="card-note">Since purchase, marked to current value</p>
            </div>
          </div>

          <div className="p-5">
            <div className="rounded-[var(--radius-panel)] bg-[var(--color-primary-hover)] p-4 text-[var(--color-primary-ink)] shadow-[var(--shadow-glow)]">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="block text-[12px] font-medium text-[color-mix(in_oklab,var(--color-primary-ink)_92%,transparent)]">Total gain</span>
                  <span className="mt-1 block text-[22px] font-semibold tabular-nums">
                    {typeof totalReturns === 'number' ? formatCurrency(totalReturns) : totalReturns}
                  </span>
                  <span className="mt-1 block text-[11px] text-[color-mix(in_oklab,var(--color-primary-ink)_82%,transparent)]">
                    on {formatCurrency(data.total_invested_cost ?? 0)} invested
                  </span>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center gap-1 text-[12px] font-medium text-[color-mix(in_oklab,var(--color-primary-ink)_92%,transparent)]">
                    Weighted XIRR (est.)
                    <InfoTooltip text={XIRR_NOTE} label="About weighted XIRR" align="right" />
                  </span>
                  <span className="mt-1 block text-[22px] font-semibold tabular-nums">
                    {typeof averageRoi === 'number' ? signedPercent(averageRoi) : averageRoi}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[length:var(--text-xs)]">
              <span className="text-[var(--color-muted)]">
                Investments now{" "}
                <b className="font-bold tabular-nums text-[var(--color-ink)]">
                  {formatCurrency(data.invested_current_value ?? 0)}
                </b>
              </span>
              <span className="badge badge-positive">{signedPercent(data.total_return_pct ?? 0)} on cost</span>
            </div>

            <div className="mt-5 space-y-3">
              <span className="label">Annualized return by class (XIRR)</span>

              {topContributor && (
                <div className="flex items-center justify-between rounded-[var(--radius-panel)] border border-[color-mix(in_oklab,var(--color-success)_30%,var(--color-surface))] bg-[color-mix(in_oklab,var(--color-success)_10%,var(--color-surface))] px-3 py-2.5">
                  <span className="flex items-center gap-2 text-[12px] font-semibold text-[var(--color-success-text)]">
                    <ShieldCheck size={14} aria-hidden="true" />
                    Top contributor: {topContributor.name}
                  </span>
                  <span className="text-[12px] font-semibold tabular-nums text-[var(--color-success-text)]">
                    {signedCurrency(topContributor.gain)}
                  </span>
                </div>
              )}

              <div className="space-y-2 pt-1">
                {returnRows.map((row) => (
                  <div key={row.name} className="flex items-center justify-between gap-2 px-1 py-1 text-[12px]">
                    <span className="font-medium text-[var(--color-ink-2)]">{row.name}</span>
                    <span className="flex items-center gap-3 tabular-nums">
                      <span className="font-medium text-[var(--color-muted)]">{signedCurrency(row.gain)}</span>
                      <span className={`w-14 text-right font-semibold ${
                        row.xirr >= 0 ? 'text-[var(--color-ink)]' : 'text-[var(--color-danger-text)]'
                      }`}>
                        {signedPercent(row.xirr)}
                      </span>
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <p className="mt-4 border-t border-[var(--color-rule)] pt-3 text-[length:var(--text-xs)] text-[var(--color-muted)]">
              Unrealized gains, marked to current values.
            </p>
          </div>

          <div className="mt-auto border-t border-[var(--color-rule)] p-5">
            <Link
              href="/analytics/investment-breakdown/by-category"
              className="btn btn-secondary w-full"
            >
              Explore category breakdown
            </Link>
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <section className="card flex flex-col justify-between">
          <div className="flex flex-1 flex-col justify-center p-5">
            <div className="card-head-plain">
              <h2 className="section-title flex items-center gap-2">
                <Calendar size={17} aria-hidden="true" className="text-[var(--color-primary)]" />
                Next month estimate
              </h2>
              <span className="card-note">Based on monthly averages</span>
            </div>

            <div className="space-y-2.5">
              {[
                { label: "Expected inflow", value: data.forecast?.inflow ?? 0, badge: "badge-positive", tag: "Income" },
                { label: "Expected outflow", value: data.forecast?.outflow ?? 0, badge: "badge-negative", tag: "Expenses" },
                { label: "Projected net savings", value: data.forecast?.net_savings ?? 0, badge: "badge-neutral", tag: "Savings" },
              ].map(({ label, value, badge, tag }) => (
                <div key={label} className="well flex items-center justify-between gap-3">
                  <span className="text-[12px] font-medium text-[var(--color-ink-2)]">{label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[12px] font-semibold tabular-nums text-[var(--color-ink)]">
                      {formatCurrency(value)}
                    </span>
                    <span className={`badge ${badge}`}>{tag}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <p className="border-t border-[var(--color-rule)] px-5 py-4 text-[12px] text-[var(--color-muted)]">
            Averaged from the months that have entries. An estimate, not a bill schedule.
          </p>
        </section>

        <section className="card flex flex-col justify-between">
          <div className="p-5">
            <div className="card-head-plain">
              <h2 className="section-title flex items-center gap-2">
                <Landmark size={17} aria-hidden="true" className="text-[var(--color-primary)]" />
                Top spending categories
              </h2>
              <span className="card-note">Year to date</span>
            </div>

            {topSpending.length === 0 ? (
              <div className="empty-state">
                <p className="state-title">No spending recorded</p>
                <p className="text-[length:var(--text-sm)]">Categorized expenses appear here as they are added.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {topSpending.map((item) => {
                  const share = totalExpense > 0 ? (item.amount / totalExpense) * 100 : 0;
                  return (
                    <div key={item.category}>
                      <div className="flex items-center justify-between gap-3 text-[12px]">
                        <span className="truncate font-medium text-[var(--color-ink-2)]">
                          {item.category.replace(/_/g, ' ')}
                        </span>
                        <span className="shrink-0 font-semibold tabular-nums text-[var(--color-ink)]">
                          {formatCurrency(item.amount)}
                        </span>
                      </div>
                      <div className="meter mt-1.5">
                        <span style={{ '--value': Math.min(share / 100, 1) } as React.CSSProperties} aria-hidden="true" />
                      </div>
                      <div className="mt-1 text-right text-[11px] text-[var(--color-muted)]">
                        {share.toFixed(1)}% of spend
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <p className="border-t border-[var(--color-rule)] px-5 py-4 text-[12px] text-[var(--color-muted)]">
            From the categorized transaction ledger.
          </p>
        </section>

        <section className="card flex flex-col justify-between">
          <div className="p-5">
            <div className="card-head-plain">
              <h2 className="section-title flex items-center gap-2">
                <TrendingUp size={17} aria-hidden="true" className="text-[var(--color-primary)]" />
                Dividend growth
              </h2>
              <span className="card-note">Yearly total received</span>
            </div>

            <div className="h-[210px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={data.dividend_yearly ?? []}
                  margin={{ top: 12, right: 8, left: 0, bottom: 4 }}
                >
                  <CartesianGrid stroke="var(--color-rule)" strokeDasharray="3 3" vertical={false} />
                  <XAxis
                    dataKey="year"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: 'var(--color-muted)', fontSize: 11 }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    width={58}
                    tick={{ fill: 'var(--color-muted)', fontSize: 11 }}
                    tickFormatter={(value) => formatCurrency(value)}
                  />
                  <Tooltip
                    content={({ active, payload }) =>
                      active && payload?.length ? (
                        <div className="rounded-[var(--radius-panel)] border border-[var(--color-edge)] bg-[var(--color-surface)] p-2.5 text-[var(--text-xs)] shadow-[var(--shadow-pop)]">
                          <span className="font-bold text-[var(--color-ink)]">{payload[0].payload.year}</span>
                          <span className="ml-2 tabular-nums text-[var(--color-ink-2)]">
                            {formatCurrency(Number(payload[0].value ?? 0))}
                          </span>
                        </div>
                      ) : null
                    }
                  />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke="var(--color-brand-2)"
                    strokeWidth={2}
                    dot={{ r: 3, fill: 'var(--color-brand-2)' }}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {data.dividend_top_stocks?.[0] && (
              <p className="mt-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                Top stock: <span className="font-bold text-[var(--color-ink-2)]">{data.dividend_top_stocks[0].name}</span>
                {' '}· {formatCurrency(data.dividend_top_stocks[0].amount)} all time
              </p>
            )}
          </div>

          <div className="border-t border-[var(--color-rule)] p-5">
            <Link href="/analytics/income-timeline/dividends" className="btn btn-secondary w-full">
              View dividend details
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
