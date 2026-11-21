import React from "react";

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  formatter?: (value: number, name?: string) => string;
}

export default function CustomTooltip({
  active,
  payload,
  label,
  formatter,
}: CustomTooltipProps) {
  if (active && payload && payload.length) {
    return (
      <div className="min-w-[140px] space-y-1.5 rounded-[var(--radius-panel)] border border-[var(--color-edge)] bg-[var(--color-surface)] p-3 text-xs shadow-[var(--shadow-pop)]">
        {label && (
          <p className="border-b border-[var(--color-rule)] pb-1 font-semibold text-[var(--color-ink)]">
            {label}
          </p>
        )}
        {payload.map((entry, index) => {
          const val = Number(entry.value);
          const formatted = formatter ? formatter(val, entry.name) : entry.value;
          return (
            <div key={`item-${index}`} className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-1.5 text-[var(--color-muted)]">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ backgroundColor: entry.color || entry.fill || 'var(--chart-2)' }}
                />
                <span className="truncate">{entry.name}</span>
              </span>
              <span className="font-semibold tabular-nums text-[var(--color-ink)]">{formatted}</span>
            </div>
          );
        })}
      </div>
    );
  }
  return null;
}
