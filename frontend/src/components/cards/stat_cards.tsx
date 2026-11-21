import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number | string;
  average?: number | string;
  comparison?: string;
  metric?: string;
  metricValue?: number;
  metricTone?: "positive" | "negative" | "neutral";
  noteBadge?: string;
  footnote?: string;
  icon?: React.ReactNode;
  tone?: "mint" | "coral" | "violet" | "sky" | "amber";
}

export default function StatCard({
  title,
  value,
  average,
  comparison,
  metric,
  metricValue,
  metricTone,
  noteBadge,
  footnote,
  icon,
  tone = "violet",
}: StatCardProps) {
  const isPositive = metricValue !== undefined && metricValue > 0;
  const isNegative = metricValue !== undefined && metricValue < 0;
  const isNeutral = metricValue === 0 || metricValue === undefined;
  const badgeTone = metricTone ?? (isPositive ? "positive" : isNegative ? "negative" : "neutral");

  return (
    <div className={`card kpi-card card-${tone} flex flex-col justify-between p-5`}>
      <div>
        <div className="flex items-start justify-between gap-2">
          <span className="icon-chip" aria-hidden="true">{icon ?? <TrendingUp size={16} />}</span>
          <span className="flex flex-wrap items-center justify-end gap-1.5">
            {noteBadge && <span className="badge badge-neutral">{noteBadge}</span>}
            {metric && (
              <span className={`badge shrink-0 badge-${badgeTone}`}>
                {isPositive && <TrendingUp size={12} aria-hidden="true" />}
                {isNegative && <TrendingDown size={12} aria-hidden="true" />}
                {isNeutral && <Minus size={12} aria-hidden="true" />}
                {metric}
              </span>
            )}
          </span>
        </div>

        <div className="label mt-3 leading-snug">{title}</div>
        <div className="stat-value mt-1">{value}</div>
        {footnote && (
          <p className="mt-1.5 truncate text-[length:var(--text-xs)] text-[var(--color-muted)]" title={footnote}>
            {footnote}
          </p>
        )}
      </div>

      <div className="mt-4 flex flex-col gap-1 border-t border-[var(--color-rule)] pt-3 text-[12px] text-[var(--color-muted)] sm:flex-row sm:items-center sm:justify-between">
        {comparison && (
          <span className="truncate" title={comparison}>
            {comparison}
          </span>
        )}
        {average && <span className="shrink-0 font-bold text-[var(--color-ink-2)]">{average}</span>}
      </div>
    </div>
  );
}
