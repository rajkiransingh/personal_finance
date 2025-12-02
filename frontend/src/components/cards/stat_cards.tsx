interface StatCardProps {
  title: string;
  value: number | string;
  average?: number | string;
  comparison?: string;
  metric?: string;
  metricValue?: number;
}

export default function StatCard({ title, value, average, comparison, metric, metricValue }: StatCardProps) {
  const getMetricColor = () => {
    if (metricValue === undefined) return 'text-[var(--color-accent)]';
    return metricValue >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getBorderColor = () => {
    if (metricValue === undefined) return 'border-[var(--color-accent)]';
    return metricValue >= 0 ? 'border-green-400' : 'border-red-400';
  };

  return (
    <div className={`card bg-[var(--color-card)] p-6 rounded-lg border-l-4 ${getBorderColor()}`}>
      <p className="text-[var(--color-text-secondary)] text-sm mb-3">{title}</p>
      <p className="text-2xl font-bold text-[var(--color-accent)] mb-3">{value}</p>

      {comparison && (
        <p className="text-xs text-[var(--color-text-secondary)]">{comparison}</p>
        )}

      <div className="flex items-center justify-between mb-1">
        {average && (
        <p className="text-xs text-[var(--color-text-secondary)] mt-2">{average}</p>
        )}
        {metric && (
        <p className={`text-xs mt-1 font-semibold ${getMetricColor()}`}>
          {metricValue !== undefined && (metricValue >= 0 ? '↑ ' : '↓ ')}
          {metric}
        </p>
      )}
      </div>
    </div>
  );
}
