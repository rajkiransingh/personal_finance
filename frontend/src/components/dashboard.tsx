'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

import MonthDropdown from "./helpers/month_helper"
import StatCard from "./cards/stat_cards"
import Skeleton from "./charts/chart_skeleton";
import CustomTooltip from "./charts/chart_tooltip"
import Corpus from "./cards/corpus_fund"
import TransactionTable from "./cards/transactions"

const mockSpendingData = [
  { month: "Jan", spending: 400 },
  { month: "Feb", spending: 300 },
  { month: "Mar", spending: 500 },
  { month: "Apr", spending: 200 },
  { month: "May", spending: 600 },
];

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

export default function DashboardPage() {
    const [currentMonth, setCurrentMonth] = useState(new Date());

  return (
    <div className="space-y-6 bg-[var(--color-bg)]">

      {/* Header with Title and Data Refresh Button */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold">Dashboard :: Reports & Analytics </h1>
        <button className="bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black py-2 px-4 rounded-md text-sm font-semibold transition">
          Refresh Data
        </button>
      </div>

      {/* Corpus Fund Progress Bar */}
      <Corpus />

      {/* Top Stat Cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Total Earnings" value="₹982.42" percentage="+12.8%" change="+100 than last month" />
        <StatCard title="Total Spending's" value="₹982.42" percentage="+12.8%" change="+100 than last month" />
        <StatCard title="Total Investments" value="₹982.42" percentage="+12.8%" change="+100 than last month" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Balance Summary - Takes 2 Columns */}
        <div className="card col-span-2 bg-[var(--color-card)] p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Spending`s Summary</h2>
            <MonthDropdown  currentMonth={currentMonth} onChange={(monthIndex) => setCurrentMonth(new Date(currentMonth.getFullYear(), monthIndex))}/>
          </div>
          {/* Placeholder for chart */}
          {mockSpendingData ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={mockSpendingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="month" stroke="#EED4B7" />
                <YAxis stroke="#EED4B7" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="spending"
                  stroke="#EED4B7"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Skeleton height={250} />
          )}
        </div>

        {/* Card Widget */}
        <div className="card bg-[var(--color-card)] p-6 rounded-lg shadow flex flex-col">
          <div className="bg-gradient-to-r from-[var(--color-accent-hover)] to-[var(--color-accent)] rounded-lg p-6 text-[var(--color-bg)] mb-4 flex-1">
            <p className="text-sm opacity-75 mb-8">Mera Paisa Card</p>
            <p className="text-3xl font-bold mb-8">₹1,00,000</p>
            <div className="flex justify-between text-sm">
              <div>
                <p className="opacity-75">Card Holder</p>
                <p className="opacity-75">Rajkiran Singh M</p>
              </div>
              <div className="text-right">
                <p className="opacity-75">Expires</p>
                <p className="opacity-75">11/29</p>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="flex-1 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black text-xs py-2 rounded font-semibold transition">
            Send
            </button>
            <button className="flex-1 bg-[var(--color-bg)] hover:bg-[var(--color-card)] text-[var(--color-text-primary)] text-xs py-2 rounded font-semibold transition border-[var(--color-card)]">
            Request
            </button>
          </div>
        </div>
      </div>

      {/* Quick Transaction Section */}
      <div className="card bg-[var(--color-card)] p-6 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">Quick Transaction</h2>
        <div className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-[var(--color-accent)] rounded-full flex items-center justify-center text-xl mb-2">
              +
            </div>
            <p className="text-xs text-[var(--color-text-secondary)]">Add</p>
          </div>
          {["Pitaji", "Mummyji", "Dad", "Ashwini"].map((name) => (
            <div key={name} className="flex flex-col items-center">
              <div className="w-12 h-12 bg-[var(--color-bg)] rounded-full flex items-center justify-center text-sm text-[var(--color-text-primary)] mb-2">
                {name.charAt(0)}
              </div>
              <p className="text-xs text-[var(--color-text-secondary)]">{name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Cards Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Admit Snap */}
        <div className="card bg-[var(--color-card)] p-6 rounded-lg">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-semibold">Admit Snap</h2>
            <span className="text-[var(--color-text-secondary)]">•••</span>
          </div>
          <div className="mb-4">
            <div className="text-sm text-[var(--color-text-secondary)] mb-1">+30.00%</div>
            <p className="text-2xl font-bold text-[var(--color-accent)]">₹40,585</p>
            <p className="text-xs text-[var(--color-text-secondary)]">Total Amount</p>
          </div>
          <div className="h-24 bg-[var(--color-bg)] rounded flex items-center justify-center text-[var(--color-text-secondary)]">
            [Bar Chart]
          </div>
        </div>
        {/* Customer Growth */}
      <div className="card bg-[var(--color-card)] p-6 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">Customer Growth</h2>
        <div className="h-40 bg-[var(--color-bg)] rounded flex items-center justify-center text-[var(--color-text-secondary)]">
          [Pie Chart]
        </div>
      </div>
      {/* Expenses Summary */}
        <div className="card bg-[var(--color-card)] p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Expenses Summary</h2>
            <MonthDropdown  currentMonth={currentMonth} onChange={(monthIndex) => setCurrentMonth(new Date(currentMonth.getFullYear(), monthIndex))}/>
          </div>
          <div className="h-40 bg-[var(--color-bg)] rounded flex items-center justify-center text-[var(--color-text-secondary)] mb-4">
            {mockCategoryData ? (
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={mockCategoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="category" stroke="#EED4B7" />
                <YAxis stroke="#EED4B7" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="amount" fill="#EED4B7" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Skeleton height={250} />
          )}
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[var(--color-text-secondary)]">Information tech</span>
              <span className="text-[var(--color-accent)]">₹2,657.89</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--color-text-secondary)]">Various shopping</span>
              <span className="text-[var(--color-accent)]">₹2,657.89</span>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-[var(--color-bg)]">
            <p className="text-xs text-[var(--color-text-secondary)]">72% Total Expense</p>
          </div>
        </div>
      </div>
      {/* Transaction History */}
      <TransactionTable data={mockTransactions} />
    </div>
  );
}