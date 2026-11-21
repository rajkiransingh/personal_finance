import React from "react";
import { ShieldCheck, AlertCircle } from "lucide-react";

interface CorpusProps {
  percentage: number;
  required?: number;
  available?: number;
  monthlyAverage?: number;
}

const compactCurrency = (value: number) => {
  if (!Number.isFinite(value)) return "₹0";
  const abs = Math.abs(value);
  if (abs >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`;
  if (abs >= 100000) return `₹${(value / 100000).toFixed(2)} L`;
  if (abs >= 1000) return `₹${(value / 1000).toFixed(1)} K`;
  return `₹${value.toFixed(0)}`;
};

export default function Corpus({ percentage, required, available, monthlyAverage }: CorpusProps) {
  const safePercentage = Math.min(Math.max(percentage, 0), 100);
  const circumference = 2 * Math.PI * 42;
  const dash = (safePercentage / 100) * circumference;

  const monthsCovered =
    monthlyAverage && monthlyAverage > 0 && available !== undefined
      ? available / monthlyAverage
      : (safePercentage / 100) * 6;
  const monthsShort = Math.max(0, 6 - monthsCovered);
  const isHealthy = safePercentage >= 100;

  return (
    <section className="card flex items-center gap-4 p-5">
      <div className="relative h-20 w-20 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full" aria-hidden="true">
          <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-well)" strokeWidth="11" />
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke={isHealthy ? "var(--color-success)" : "var(--color-warning)"}
            strokeWidth="11"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference}`}
            transform="rotate(-90 50 50)"
          />
        </svg>
        <span className="absolute inset-0 grid place-items-center text-[length:var(--text-md)] font-extrabold tabular-nums text-[var(--color-ink)]">
          {safePercentage}%
        </span>
      </div>

      <div className="min-w-0 flex-1">
        <h2 className="card-title">Emergency fund</h2>
        <p className="card-note mt-0.5">
          {monthsCovered.toFixed(1)} of 6 months of expenses covered
        </p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <span className={`badge ${isHealthy ? "badge-positive" : "badge-warning"}`}>
            {isHealthy ? <ShieldCheck size={12} aria-hidden="true" /> : <AlertCircle size={12} aria-hidden="true" />}
            {isHealthy ? "Fully funded" : `${monthsShort.toFixed(1)} months short`}
          </span>
          {required !== undefined && available !== undefined && (
            <span className="text-[length:var(--text-xs)] font-medium tabular-nums text-[var(--color-muted)]">
              {compactCurrency(available)} of {compactCurrency(required)}
            </span>
          )}
        </div>
      </div>
    </section>
  );
}
