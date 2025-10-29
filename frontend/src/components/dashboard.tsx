'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

import MonthDropdown from "./helpers/month_helper"
import StatCard from "./cards/stat_cards"
import Skeleton from "./charts/chart_skeleton";
import CustomTooltip from "./charts/chart_tooltip"
import InvestmentPieChart from "./charts/assets_doughnut_chart"
import Corpus from "./cards/corpus_fund"
import TransactionTable from "./cards/transactions"
import { DashboardData } from './types/dashboard';

const mockCategoryData = [
  { category: "Food", amount: 450 },
  { category: "Bills", amount: 320 },
  { category: "Travel", amount: 180 },
  { category: "Shopping", amount: 250 },
];

const mockTransactions = [
  { "date": "2025-10-12", "category": "Groceries", "amount": 235.60, "paymentMode": "Credit Card", "merchant": "Lidl", "status": "Completed" },
  { "date": "2025-10-11", "category": "Utilities", "amount": 89.99, "paymentMode": "Bank Transfer", "merchant": "Energa", "status": "Completed" },
  { "date": "2025-10-09", "category": "Transportation", "amount": 15.20, "paymentMode": "Cash", "merchant": "ZTM Gdańsk", "status": "Completed" },
  { "date": "2025-10-08", "category": "Dining", "amount": 72.50, "paymentMode": "Credit Card", "merchant": "Pizza Hut", "status": "Completed" },
  { "date": "2025-10-06", "category": "Subscription", "amount": 49.00, "paymentMode": "Auto Debit", "merchant": "Netflix", "status": "Completed" },
  { "date": "2025-10-04", "category": "Healthcare", "amount": 130.00, "paymentMode": "Credit Card", "merchant": "Medicover", "status": "Completed" },
  { "date": "2025-10-02", "category": "Shopping", "amount": 260.75, "paymentMode": "Credit Card", "merchant": "Decathlon", "status": "Completed" },
  { "date": "2025-09-30", "category": "Rent", "amount": 2300.00, "paymentMode": "Bank Transfer", "merchant": "Landlord", "status": "Completed" },
  { "date": "2025-09-28", "category": "Insurance", "amount": 540.00, "paymentMode": "Bank Transfer", "merchant": "PZU", "status": "Completed" },
  { "date": "2025-09-25", "category": "Fuel", "amount": 210.30, "paymentMode": "Credit Card", "merchant": "BP", "status": "Completed" },
]

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

export default function DashboardPage() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentMonth, setCurrentMonth] = useState(new Date());

    useEffect(() => {
        const fetchDashboardData = async () => {
          try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/dashboard/', { method: 'GET' });

            if (!response.ok) throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
            const dashboardData: DashboardData = await response.json();
            setData(dashboardData);
            setError(null);
          } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError(`Failed to load dashboard data. Make sure Python backend is running. ${response}`);
          } finally {
            setLoading(false);
          }
        };
        fetchDashboardData();
    },[]);

    if (loading) {
        return <div className="text-center py-8 text-[var(--color-text-secondary)]">Loading dashboard...</div>;
    }

    if (error) {
        return <div className="text-center py-8 text-red-400">{error}</div>;
    }

    if (!data) {
        return <div className="text-center py-8 text-[var(--color-text-secondary)]">No data available</div>;
    }

    const corpus = data.emergency_coverage
    const totalReturns = data.total_returns
    const averageRoi = data.average_roi
    const assets = data.assets

    // Sort investments to get best performer
    const sortedInvestments = Object.entries(data.investment_returns).sort(
    (a, b) => b[1] - a[1]
  );
  const [bestPerformer, ...restInvestments] = sortedInvestments;

  return (
    <div className="space-y-6 bg-[var(--color-bg)]">

      {/* Header with Title and Data Refresh Button */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold">Financial Information Dashboard</h1>
        <button className="bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-2 px-4 rounded-md text-sm font-semibold transition">
          Refresh Data
        </button>
      </div>

      {/* Corpus Fund Progress Bar */}
      <Corpus percentage={corpus} />

      {/* Top Stat Cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Total Income (YTD)" value="₹9,82,420" comparison="Last Year (same date): ₹8,45,000" metric="10% Increase" metricValue={10} />
        <StatCard title="Total Expenses (YTD)" value="₹4,56,789" comparison="Avg/month: ₹38,065" metric="46% of income" metricValue={-5} />
        <StatCard title="Total Invested" value="₹78,92,345" comparison="Avg/month: ₹75,065" metric="Growth: +24.5%" metricValue={24} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-4">

        {/* Net Worth Breakdown */}
        <div className="card col-span-2 bg-[var(--color-card)] p-6 rounded-lg h-[520px]">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Net Worth Breakdown</h2>
                <span className="text-sm text-[var(--color-text-secondary)]"> (Cash + Investments) </span>
            </div>
            <InvestmentPieChart earnings={assets} />
        </div>

        {/* Investment Return Card */}
        <div className="card bg-[var(--color-card)] p-6 rounded-lg shadow flex flex-col">
            {/* Header: Total Returns & ROI */}
            <div className="h-full bg-gradient-to-r from-[var(--color-accent-hover)] to-[var(--color-accent)] rounded-lg p-6 text-[var(--color-bg)] mb-4 flex flex-col">
              <div className="flex justify-between mb-4">
                <div>
                  <p className="text-sm opacity-75 mb-1">Total Returns</p>
                  <p className="text-3xl font-bold">{totalReturns}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm opacity-75 mb-1">ROI</p>
                  <p className="text-3xl font-bold">{averageRoi}%</p>
                </div>
              </div>

              <div className="h-[1px] bg-gradient-to-r from-[var(--color-text-primary)] to-[var(--color-text-secondary)] rounded mb-4"></div>

              {/* Best Performer */}
              <div className="text-sm mb-2 opacity-75">Best Performer</div>
                {bestPerformer && (
                  <div className="flex justify-between text-sm mb-6">
                    <p className="font-semibold">{`${bestPerformer[0]}`}</p>
                    <p className="font-semibold">{`${bestPerformer[1]}%`}</p>
              </div>
              )}

              {/* Other Investments */}
              <div className="text-sm mb-2 opacity-75">Other Investments</div>
                {restInvestments.map(([name, value]) => (
                  <div key={name} className="flex justify-between text-sm mb-3" >
                    <p className="font-semibold">{name}</p>
                    <p className="font-semibold">{value}%</p>
                  </div>
                ))}
              </div>

              {/* Button */}
              <button className="w-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black text-xs py-2 rounded font-semibold transition">
                View Analysis →
              </button>
            </div>
        </div>


      <div className="grid grid-cols-2 gap-4 md:grid-cols-2 sm:grid-cols-1">
  {/* Financial Forecast Card */}
  <div className="card bg-[var(--color-card)] p-6 rounded-lg flex flex-col justify-between">
    <div>
      <h2 className="text-lg font-semibold mb-4">Next Month Forecast</h2>

      <div className="flex flex-col gap-3 text-sm">
        {[
          { label: "Expected Income", value: "7 200 PLN", color: "bg-green-500/20 text-green-400" },
          { label: "Expected Expenses", value: "4 500 PLN", color: "bg-red-500/20 text-red-400" },
          { label: "Predicted Savings", value: "2 700 PLN", color: "bg-[var(--color-accent)]/20 text-[var(--color-accent)]" },
        ].map(({ label, value, color }) => (
          <div key={label} className="flex justify-between items-center">
            <span className="text-[var(--color-text-secondary)]">{label}:</span>
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full ${color} whitespace-nowrap`}
            >
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>

    <div className="mt-6 text-xs text-[var(--color-text-secondary)] italic">
      Based on the last 3 months’ trend analysis.
    </div>
  </div>

  {/* Monthly Goals Card */}
  <div className="card bg-[var(--color-card)] p-6 rounded-lg flex flex-col justify-between">
    <div>
      <h2 className="text-lg font-semibold mb-4">Monthly Goals</h2>

      <div className="flex flex-col gap-3 text-sm">
        {[
          { goal: "Investment", progress: 72 },
          { goal: "Savings", progress: 55 },
          { goal: "Emergency Fund", progress: 84 },
        ].map(({ goal, progress }) => (
          <div
            key={goal}
            className="flex justify-between items-center"
          >
            <span>{goal}</span>
            <div
              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                progress >= 75
                  ? "bg-green-500/20 text-green-400"
                  : progress >= 50
                  ? "bg-yellow-500/20 text-yellow-400"
                  : "bg-red-500/20 text-red-400"
              }`}
            >
              {progress}%
            </div>
          </div>
        ))}
      </div>
    </div>

    <div className="mt-6 text-xs text-[var(--color-text-secondary)] italic">
      Updated weekly based on your target performance.
    </div>
  </div>
</div>
</div>
);}