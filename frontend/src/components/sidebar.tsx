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
      {/* Header / Logo */}
      <div className="mb-10 px-2">
        <div className="flex items-center gap-3 group">
          <div className="bg-[var(--color-accent)] p-2.5 rounded-xl text-black shadow-lg transform group-hover:scale-110 transition-transform duration-300">
            <TrendingUp size={24} strokeWidth={2.5} />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight text-[var(--color-text-secondary)] leading-none">
              MERA
            </h1>
            <h1 className="text-xl font-light tracking-[0.2em] text-[var(--color-accent)] leading-none mt-1">
              PAISA
            </h1>
          </div>
        </div>
        <div className="h-[2px] w-full bg-gradient-to-r from-[var(--color-accent)] to-transparent mt-6 opacity-20"></div>
      </div>

      {/* Navigation */}
      <nav className="space-y-1 flex-1 text-sm overflow-y-auto pr-2 custom-scrollbar">
        {navItems.map((item) => (
          <SidebarItem key={item.name} item={item} depth={0} pathname={pathname} openMenus={openMenus} toggleMenu={toggleMenu} />
        ))}
      </nav>
    </aside>
  );
}

// Recursive Sidebar Item Component
function SidebarItem({ item, depth, pathname, openMenus, toggleMenu }: any) {
  const isOpen = openMenus[item.name];
  const hasChildren = Array.isArray(item.children) && item.children.length > 0;
  const isActive = pathname === item.path;

  // Indentation calculation
  const paddingLeft = `${depth * 12 + 16}px`;

  return (
    <div className="mb-1">
      {hasChildren ? (
        <>
          <button
            onClick={() => toggleMenu(item.name)}
            className={`flex items-center justify-between w-full py-2 rounded-lg font-medium transition-all duration-200 group ${
              isOpen ? "text-white" : "text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] hover:bg-[var(--color-card)]"
            }`}
             style={{ paddingLeft, paddingRight: '12px' }}
          >
            <span className="flex items-center gap-3">
              {item.icon && <span className={`${isOpen ? 'text-[var(--color-accent)]' : 'text-gray-500 group-hover:text-[var(--color-accent)]'}`}>{item.icon}</span>}
              <span className="tracking-wide">{item.name}</span>
            </span>
            <ChevronRight
              size={16}
              className={`transition-transform duration-300 ${isOpen ? "rotate-90 text-[var(--color-accent)]" : "text-gray-600"}`}
            />
          </button>

          <div
            className={`overflow-hidden transition-all duration-300 ease-in-out pl-2 border-l border-[var(--color-border)] ml-${depth * 2 + 4}`}
            style={{
              maxHeight: isOpen ? "1000px" : "0px",
              opacity: isOpen ? 1 : 0,
            }}
          >
            <div className="pt-1 pb-2 space-y-1">
              {item.children.map((child: any) => (
                <SidebarItem
                  key={child.name}
                  item={child}
                  depth={depth + 1}
                  pathname={pathname}
                  openMenus={openMenus}
                  toggleMenu={toggleMenu}
                />
              ))}
            </div>
          </div>
        </>
      ) : (
        <Link
          href={item.path ?? "#"}
          className={`flex items-center gap-3 py-2 rounded-lg font-medium transition-all duration-150 relative overflow-hidden ${
            isActive
              ? "bg-gradient-to-r from-[var(--color-accent)]/10 to-transparent text-[var(--color-accent)]"
              : "text-[var(--color-text-secondary)] hover:text-white hover:bg-[var(--color-card)]"
          }`}
          style={{ paddingLeft, paddingRight: '12px' }}
        >
          {isActive && (
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[var(--color-accent)] rounded-r-full" />
          )}
          {item.icon && <span className={isActive ? "text-[var(--color-accent)]" : "text-gray-500"}>{item.icon}</span>}
          <span>{item.name}</span>
        </Link>
      )}
    </div>
  );
}
