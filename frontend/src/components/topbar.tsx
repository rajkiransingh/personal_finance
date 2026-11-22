"use client";

import { usePathname, useRouter } from "next/navigation";
import { LogOut, Users2, User2 } from "lucide-react";
import ThemeToggle from "./theme-toggle";
import { useAuth } from "@/lib/auth";

export default function Topbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, setView } = useAuth();

  const getPageTitle = () => {
    if (pathname === "/" || pathname === "/admin") return "Overview";
    if (pathname === "/transactions") return "Transactions";
    if (pathname.includes("/portfolio-rebalancing")) return "Portfolio rebalancing";
    if (pathname.includes("/investment-breakdown")) return "Investment breakdown";
    if (pathname.includes("/screen&discover")) return "Stock screener";
    if (pathname.startsWith("/strategies")) return "Strategies";
    if (pathname.startsWith("/admin")) return "Administration";
    if (pathname.startsWith("/configurations")) return "Configurations";
    if (pathname.startsWith("/settings")) return "Settings";
    return "Personal finance";
  };

  const initials = (user?.name || "")
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

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

        {user?.can_household_view && (
          <div className="seg hidden sm:flex" role="group" aria-label="Data view">
            <button
              type="button"
              className="seg-item"
              aria-selected={user.view === "personal"}
              onClick={() => void setView("personal")}
            >
              <User2 size={13} aria-hidden="true" /> Me
            </button>
            <button
              type="button"
              className="seg-item"
              aria-selected={user.view === "household"}
              onClick={() => void setView("household")}
            >
              <Users2 size={13} aria-hidden="true" /> Household
            </button>
          </div>
        )}

        <span className="hidden items-center gap-2 rounded-full border border-[var(--color-rule)] bg-[var(--color-surface)] px-2 py-1.5 shadow-[var(--shadow-chip)] sm:inline-flex">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-[var(--color-warning)] to-[var(--color-danger)] text-[11px] font-extrabold text-white">
            {initials || "?"}
          </span>
          <span className="text-[12px] font-bold text-[var(--color-ink)]">{user?.name || "Account"}</span>
          {user?.role === "admin" && <span className="badge badge-warning">Admin</span>}
        </span>

        <ThemeToggle />

        <button
          type="button"
          className="btn btn-ghost btn-icon"
          aria-label="Sign out"
          title="Sign out"
          onClick={async () => {
            await logout();
            router.replace("/login");
          }}
        >
          <LogOut size={16} aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
