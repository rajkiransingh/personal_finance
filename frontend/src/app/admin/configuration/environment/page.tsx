"use client";

import AdminOnly from "@/components/admin-only";
import EnvironmentConfigPage from "@/app/configurations/environment/page";

export default function Page() {
  return (
    <AdminOnly>
      <div className="mb-6">
        <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">Environment</h1>
        <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
          Administrator configuration. Changes apply to everyone.
        </p>
      </div>
      <EnvironmentConfigPage />
    </AdminOnly>
  );
}
