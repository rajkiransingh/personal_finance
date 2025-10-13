interface Transaction {
  date: string;
  category: string
  amount: string;
}

const formatCurrency = (value: number) => {
    return `₹ ${value.toFixed(2)}`;
  };

export default function TransactionTable({ data }: { data: Transaction[] }) {
  return (
    <div className="bg-[var(--color-card)] rounded-2xl shadow-sm p-4">
      <h2 className="text-lg font-semibold mb-4 text-[var(--color-text)]">
        Recent Transactions
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] text-[var(--color-text-secondary)]">
              <th className="text-left py-2 font-medium">Date</th>
              <th className="text-left py-2 font-medium">Category</th>
              <th className="text-right py-2 font-medium">Amount</th>
            </tr>
          </thead>

          <tbody>
            {data.map((tx, index) => (
              <tr
                key={index}
                className="border-b border-[var(--color-border)] hover:bg-[var(--color-bg-hover)] transition-colors">
                <td className="py-3 text-[var(--color-text-secondary)]">{tx.date}</td>
                <td className="py-3 flex items-center gap-3 text-[var(--color-text)]">{tx.category}</td>
                <td className="py-3 text-right font-semibold text-[var(--color-accent)]">{formatCurrency(tx.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
