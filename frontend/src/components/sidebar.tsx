"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  ChevronRight,
  BarChart3,
  PieChart,
  Wallet,
  LineChart,
  Target,
  TrendingUp,
  Coins,
  Settings,
  Home,
  FileText,
} from "lucide-react";

// 🔹 Menu Structure — scalable & nested
const navItems = [
  { name: "Dashboard", path: "/", icon: <Home size={16} /> },
  { name: "Transactions", path: "/transactions", icon: <FileText size={16} /> },
  {
    name: "Analytics",
    icon: <BarChart3 size={16} />,
    children: [
      {
        name: "Portfolio Rebalancing",
        icon: <PieChart size={16} />,
        children: [
          { name: "Overview", path: "/analytics/portfolio-rebalancing/overview" },
          { name: "Sub Allocations", path: "/analytics/portfolio-rebalancing/sub-allocations" },
          { name: "Step-up Strategy", path: "/analytics/portfolio-rebalancing/step-up-strategy" },
        ],
      },
      {
        name: "Investment Breakdown",
        icon: <Wallet size={16} />,
        children: [
          { name: "By Category", path: "/analytics/investment-breakdown/by-category" },
          { name: "Individual Holdings", path: "/analytics/investment-breakdown/individual-holdings" },
        ],
      },
      {
        name: "Screen & Discover", path: "/screen&discover", icon: <TrendingUp size={16} /> },
      {
        name: "Trends & Risks",
        icon: <LineChart size={16} />,
        children: [
          { name: "Performance Vs Benchmark", path: "/analytics/trends-risks/performance-vs-benchmark" },
          { name: "Risk Heatmap", path: "/analytics/trends-risks/risk-heatmap" },
        ],
      },
      {
        name: "Goals",
        icon: <Target size={16} />,
        children: [{ name: "Goal Tracker", path: "/analytics/goals/goal-tracker" }],
      },
      {
        name: "Income & Timeline",
        icon: <Coins size={16} />,
        children: [
          { name: "Dividends", path: "/analytics/income-timeline/dividends" },
          { name: "Allocation History", path: "/analytics/income-timeline/allocation-history" },
        ],
      },
    ],
  },
  {
    name: "Configurations", icon: <FileText size={16} />,
    children: [
      { name: "Portfolio Config", path: "/configurations/portfolio-config" },
      { name: "Stock Strategy", path: "/configurations/stock-picking-strategy" },
      { name: "Environment Configuration", path: "/configurations/environment" }
    ],
  },
  {
      name: "Settings", icon: <Settings size={16} />,
      children: [
      { name: "Supporting Data", path: "/settings/supporting-data" }
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({});

  // ✅ Restore menu state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("sidebarOpenMenus");
    if (saved) {
      try {
        setOpenMenus(JSON.parse(saved));
      } catch {
        localStorage.removeItem("sidebarOpenMenus");
      }
    }
  }, []);

  // ✅ Save menu state whenever it changes
  useEffect(() => {
    localStorage.setItem("sidebarOpenMenus", JSON.stringify(openMenus));
  }, [openMenus]);

  const toggleMenu = (menuName: string) => {
    setOpenMenus((prev) => {
      const updated = { ...prev, [menuName]: !prev[menuName] };
      localStorage.setItem("sidebarOpenMenus", JSON.stringify(updated)); // immediate persist
      return updated;
    });
  };

  return (
    <aside className="bg-[var(--color-sidebar)] text-[var(--color-text-primary)] w-72 min-h-screen p-6 flex flex-col shadow-lg border-r border-[var(--color-card)]">
      {/* Header */}
      <h1 className="font-playwrite text-2xl mb-6 text-center tracking-wide">
        <span className="inline-flex flex-col items-center gap-1">
          <span className="text-[var(--color-accent)] text-sm tracking-widest">▁ ▃ ▄ ▅</span>
          <span className="text-[var(--color-accent)] font-semibold">Mera Paisa</span>
        </span>
      </h1>

      <div className="h-[1px] bg-[var(--color-card)] mb-8 mx-4"></div>

      {/* Navigation */}
      <nav className="space-y-2 flex-1 text-sm">
        {navItems.map((item) => {
          const active = pathname === item.path;
          const hasChildren = Array.isArray(item.children);

          if (!hasChildren) {
            return (
              <Link
                key={item.name}
                href={item.path ?? "#"}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-all duration-150 ${
                  active
                    ? "bg-[var(--color-accent)] text-black shadow-inner"
                    : "text-[var(--color-text-secondary)] hover:bg-[var(--color-card)] hover:text-[var(--color-accent)]"
                }`}
              >
                {item.icon} {item.name}
              </Link>
            );
          }

          return (
            <div key={item.name}>
              <button
                onClick={() => toggleMenu(item.name)}
                className="flex items-center justify-between w-full px-4 py-2 rounded-md font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-card)] hover:text-[var(--color-accent)]"
              >
                <span className="flex items-center gap-2">
                  {item.icon} {item.name}
                </span>
                {openMenus[item.name] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>

              {openMenus[item.name] && (
                <div className="ml-4 mt-1 space-y-1">
                  {item.children.map((child: any) => (
                    <div key={child.name}>
                      {child.children ? (
                        <>
                          <button
                            onClick={() => toggleMenu(child.name)}
                            className="flex items-center justify-between w-full px-3 py-1.5 rounded-md text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]"
                          >
                            <span className="flex items-center gap-2">
                              {child.icon} {child.name}
                            </span>
                            {openMenus[child.name] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                          </button>

                          {openMenus[child.name] && (
                            <div className="ml-4 mt-1 space-y-1">
                              {child.children.map((sub: any) => {
                                const subActive = pathname === sub.path;
                                return (
                                  <Link
                                    key={sub.name}
                                    href={sub.path}
                                    className={`block px-3 py-1.5 rounded-md transition-all duration-150 ${
                                      subActive
                                        ? "bg-[var(--color-accent)] text-black"
                                        : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-lighter)] hover:text-[var(--color-accent)]"
                                    }`}
                                  >
                                    {sub.name}
                                  </Link>
                                );
                              })}
                            </div>
                          )}
                        </>
                      ) : (
                        <Link
                          href={child.path}
                          className={`block px-3 py-1.5 rounded-md ${
                            pathname === child.path
                              ? "bg-[var(--color-accent)] text-black"
                              : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-lighter)] hover:text-[var(--color-accent)]"
                          }`}
                        >
                          {child.name}
                        </Link>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 text-xs text-center text-[var(--color-text-secondary)] opacity-60">
         Mera Paisa ••• Personal Finance Tracker ••• v1.0
      </div>
    </aside>
  );
}
