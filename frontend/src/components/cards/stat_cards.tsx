// components/StatCard.tsx
interface StatCardProps {
  title: string;
  value: number | string;
  percentage?: string;
  change?: string;
}

export default function StatCard({ title, value, percentage, change }: StatCardProps) {
  return (
    <div className="card bg-[var(--color-card)] p-6 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl"></span>
        {percentage && (
          <span className="text-xs text-[var(--color-text-secondary)] mt-2">{percentage}</span>
        )}
      </div>
      <p className="text-[var(--color-text-secondary)] text-sm mb-2">{title}</p>
      <p className="text-2xl font-bold text-[var(--color-accent)]">{value}</p>
      {change && (
        <p className="text-xs text-[var(--color-text-secondary)] mt-2">{change}</p>
      )}
    </div>
  );
}
