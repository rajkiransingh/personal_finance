"use client";

import AdminOnly from "@/components/admin-only";
import StockPickStrategyConfigPage from "@/components/configurations/stock-pick-strategy-config";

export default function Page() {
  return (
    <AdminOnly>
      <div className="mb-6">
        <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">Scoring defaults</h1>
        <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
          Administrator configuration. Changes apply to everyone.
        </p>
      </div>
      <StockPickStrategyConfigPage />
    </AdminOnly>
  );
}
