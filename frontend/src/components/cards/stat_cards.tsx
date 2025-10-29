interface StatCardProps {
  title: string;
  value: number | string;
  comparison?: string;
  metric?: string;
  metricValue?: number;
}

export default function StatCard({ title, value, comparison, metric, metricValue }: StatCardProps) {
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
      <p className="text-[var(--color-text-secondary)] text-sm mb-2">{title}</p>
      <p className="text-2xl font-bold text-[var(--color-accent)]">{value}</p>
      <div className="flex items-center justify-between mb-3">
        {comparison && (
        <p className="text-xs text-[var(--color-text-secondary)] mt-2">{comparison}</p>
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
