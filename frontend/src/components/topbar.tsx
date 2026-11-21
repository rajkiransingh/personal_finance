"use client";

import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";
import ThemeToggle from "./theme-toggle";

export default function Topbar() {
  const pathname = usePathname();

  const getPageTitle = () => {
    if (pathname === "/") return "Overview";
    if (pathname === "/transactions") return "Transactions";
    if (pathname.includes("/portfolio-rebalancing")) return "Portfolio rebalancing";
    if (pathname.includes("/investment-breakdown")) return "Investment breakdown";
    if (pathname.includes("/screen&discover")) return "Stock screener";
    if (pathname.includes("/configurations")) return "Configurations";
    if (pathname.includes("/settings")) return "Settings";
    return "Personal finance";
  };

  return (
    <header className="topbar relative z-[250] flex h-16 items-center justify-between gap-4 py-0 pl-16 pr-5 md:px-8">
      <div className="flex min-w-0 items-center gap-2 text-[length:var(--text-sm)]">
        <span className="truncate font-medium text-[var(--color-muted)]">Personal finance</span>
        <span className="text-[var(--color-rule-strong)]" aria-hidden="true">/</span>
        <span className="truncate font-bold text-[var(--color-ink)]">{getPageTitle()}</span>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <span className="hidden items-center gap-1.5 rounded-full bg-[var(--color-well)] px-2.5 py-1.5 text-[11px] font-bold text-[var(--color-success-text)] sm:inline-flex">
          <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-success)]" aria-hidden="true" />
          LIVE
        </span>

        <span className="hidden items-center gap-2 rounded-full border border-[var(--color-rule)] bg-[var(--color-surface)] px-2 py-1.5 shadow-[var(--shadow-chip)] sm:inline-flex">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-[var(--color-warning)] to-[var(--color-danger)] text-[11px] font-extrabold text-white">
            RS
          </span>
          <span className="text-[12px] font-bold text-[var(--color-ink)]">Rajkiran</span>
        </span>

        <ThemeToggle />

        <button type="button" className="btn btn-ghost btn-icon" aria-label="Sign out" title="Sign out">
          <LogOut size={16} aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
