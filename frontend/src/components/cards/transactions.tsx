import React from "react";

interface Transaction {
  date: string;
  category: string;
  amount: string | number;
}

const formatCurrency = (value: number | string) => {
  const num = typeof value === 'number' ? value : parseFloat(value) || 0;
  return `₹ ${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export default function TransactionTable({ data }: { data: Transaction[] }) {
  return (
    <section className="card overflow-hidden">
      <div className="card-head">
        <div>
          <h2 className="card-title">Recent transactions</h2>
          <p className="card-note">Showing latest records</p>
        </div>
      </div>

      <div className="overflow-x-auto px-2 sm:px-3">
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th className="num">Amount</th>
            </tr>
          </thead>

          <tbody>
            {data.map((tx, index) => (
              <tr key={index}>
                <td className="whitespace-nowrap text-[var(--color-muted)]">{tx.date}</td>
                <td className="font-medium text-[var(--color-ink)]">{tx.category}</td>
                <td className="num font-semibold text-[var(--color-ink)]">
                  {formatCurrency(tx.amount)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
