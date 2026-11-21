"use client";

import Link from "next/link";
import { useState, useEffect, Fragment } from "react";
import { usePathname } from "next/navigation";
import {
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
  Menu,
  X,
} from "lucide-react";

interface NavChild {
  name: string;
  path?: string;
  available?: boolean;
  icon?: React.ReactNode;
  children?: NavChild[];
}

interface NavItem {
  name: string;
  path?: string;
  available?: boolean;
  icon: React.ReactNode;
  children?: NavChild[];
}

const navItems: NavItem[] = [
  { name: "Dashboard", path: "/", icon: <Home size={17} /> },
  { name: "Transactions", path: "/transactions", icon: <FileText size={17} /> },
  {
    name: "Analytics",
    icon: <BarChart3 size={17} />,
    children: [
      {
        name: "Portfolio Rebalancing",
        icon: <PieChart size={15} />,
        children: [
          { name: "Overview", path: "/analytics/portfolio-rebalancing/overview" },
          { name: "Sub Allocations", path: "/analytics/portfolio-rebalancing/sub-allocations", available: false },
          { name: "Step-up Strategy", path: "/analytics/portfolio-rebalancing/step-up-strategy", available: false },
        ],
      },
      {
        name: "Investment Breakdown",
        icon: <Wallet size={15} />,
        children: [
          { name: "By Category", path: "/analytics/investment-breakdown/by-category" },
          { name: "Individual Holdings", path: "/analytics/investment-breakdown/individual-holdings", available: false },
        ],
      },
      {
        name: "Screen & Discover",
        path: "/screen&discover",
        icon: <TrendingUp size={15} />,
      },
      {
        name: "Trends & Risks",
        icon: <LineChart size={15} />,
        children: [
          { name: "Performance Vs Benchmark", path: "/analytics/trends-risks/performance-vs-benchmark", available: false },
          { name: "Risk Heatmap", path: "/analytics/trends-risks/risk-heatmap", available: false },
        ],
      },
      {
        name: "Goals",
        icon: <Target size={15} />,
        children: [{ name: "Goal Tracker", path: "/analytics/goals/goal-tracker", available: false }],
      },
      {
        name: "Income & Timeline",
        icon: <Coins size={15} />,
        children: [
          { name: "Dividends", path: "/analytics/income-timeline/dividends" },
          { name: "Allocation History", path: "/analytics/income-timeline/allocation-history", available: false },
        ],
      },
    ],
  },
  {
    name: "Configurations",
    icon: <Settings size={17} />,
    children: [
      { name: "Portfolio Config", path: "/configurations/portfolio-config" },
      { name: "Stock Strategy", path: "/configurations/stock-picking-strategy" },
      { name: "Environment Configuration", path: "/configurations/environment" },
    ],
  },
  {
    name: "Settings",
    icon: <Settings size={17} />,
    children: [
      { name: "Supporting Data", path: "/settings/supporting-data" },
    ],
  },
];

// Routes marked available: false stay in this file for later tasks but are
// hidden in the sidebar. Flip the flag when the route becomes real.
function isVisible(item: any): boolean {
  if (item.available === false) return false;
  if (Array.isArray(item.children) && item.children.length) {
    return item.children.some(isVisible);
  }
  return true;
}

export default function Sidebar() {
  const pathname = usePathname();
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({ Analytics: true });
  const [mobileOpen, setMobileOpen] = useState(false);

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

  useEffect(() => {
    localStorage.setItem("sidebarOpenMenus", JSON.stringify(openMenus));
  }, [openMenus]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const toggleMenu = (menuName: string) => {
    setOpenMenus((prev) => ({
      ...prev,
      [menuName]: !prev[menuName],
    }));
  };

  return (
    <>
      <div className="fixed left-4 top-3 z-[310] lg:hidden">
        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
          aria-expanded={mobileOpen}
          className="btn btn-secondary btn-icon"
        >
          {mobileOpen ? <X size={19} /> : <Menu size={19} />}
        </button>
      </div>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-[305] bg-[color-mix(in_oklab,var(--color-ink)_38%,transparent)] lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`rail fixed left-0 top-0 z-[300] flex h-screen w-[var(--rail)] flex-col border-r border-[var(--color-rule)] transition-transform duration-[var(--dur-short)] ease-[var(--ease-out)] lg:visible lg:sticky lg:translate-x-0 ${
          mobileOpen ? "visible translate-x-0" : "invisible -translate-x-full"
        }`}
      >
        <div className="flex h-16 shrink-0 items-center gap-2.5 border-b border-[var(--color-rule)] px-5">
          <Link href="/" className="flex items-center gap-2.5" aria-label="Mera Paisa, dashboard">
            <span className="brand-mark" aria-hidden="true">M</span>
            <span className="flex flex-col gap-0.5">
              <span className="wordmark text-[var(--color-sidebar-ink)]">Mera Paisa</span>
              <span className="text-[11px] font-medium text-[var(--color-sidebar-muted)]">
                money, made clear
              </span>
            </span>
          </Link>
        </div>

        <nav
          className="custom-scrollbar flex-1 space-y-0.5 overflow-y-auto px-3 py-4"
          aria-label="Primary"
        >
          <div className="rail-cap">Your space</div>
          {navItems.filter(isVisible).map((item) => (
            <Fragment key={item.name}>
              {item.name === "Configurations" && <div className="rail-cap">Manage</div>}
              <SidebarItem
                item={item}
                depth={0}
                pathname={pathname}
                openMenus={openMenus}
                toggleMenu={toggleMenu}
              />
            </Fragment>
          ))}
        </nav>

        <div className="shrink-0 border-t border-[var(--color-rule)] p-3">
          <div className="flex items-center gap-2.5 rounded-[var(--radius-panel)] bg-[var(--color-sidebar-2)] px-3 py-2.5">
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[var(--color-surface)] text-[11px] font-extrabold text-[var(--color-primary)] shadow-[var(--shadow-chip)]">
              RS
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-[12px] font-bold text-[var(--color-sidebar-ink)]">
                Rajkiran
              </span>
              <span className="block truncate text-[11px] font-medium text-[var(--color-sidebar-muted)]">
                Personal account
              </span>
            </span>
            <span className="rounded-full border border-[color-mix(in_oklab,var(--color-primary)_30%,transparent)] bg-[var(--color-surface)] px-2 py-0.5 text-[11px] font-bold text-[var(--color-primary)]">
              INR
            </span>
          </div>
        </div>
      </aside>
    </>
  );
}

function SidebarItem({
  item,
  depth,
  pathname,
  openMenus,
  toggleMenu,
}: {
  item: any;
  depth: number;
  pathname: string;
  openMenus: Record<string, boolean>;
  toggleMenu: (name: string) => void;
}) {
  const isOpen = !!openMenus[item.name];
  const hasChildren = Array.isArray(item.children) && item.children.length > 0;
  const isActive = pathname === item.path;

  const isParentOfActive =
    hasChildren &&
    item.children.some(
      (child: any) =>
        child.path === pathname ||
        (child.children && child.children.some((sub: any) => sub.path === pathname))
    );

  const paddingLeft = depth === 0 ? 10 : depth * 10 + 10;

  if (hasChildren) {
    return (
      <div className="w-full">
        <button
          type="button"
          onClick={() => toggleMenu(item.name)}
          aria-expanded={isOpen}
          aria-current={isParentOfActive ? "true" : undefined}
          className="rail-link w-full justify-between"
          style={{ paddingLeft, paddingRight: 10 }}
        >
          <span className="flex min-w-0 items-center gap-2.5">
            {item.icon && (
              <span className={isParentOfActive ? "text-[var(--color-accent)]" : "opacity-70"}>
                {item.icon}
              </span>
            )}
            <span className="truncate">{item.name}</span>
          </span>
          <ChevronRight
            size={14}
            aria-hidden="true"
            className={`shrink-0 opacity-70 transition-transform duration-[var(--dur-short)] ease-[var(--ease-out)] ${
              isOpen ? "rotate-90" : ""
            }`}
          />
        </button>

        {isOpen && (
          <div className="mt-0.5 space-y-0.5 border-l border-[var(--color-rule)] pl-1.5 ml-3">
            {item.children.filter(isVisible).map((child: any) => (
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
        )}
      </div>
    );
  }

  return (
    <Link
      href={item.path ?? "#"}
      aria-current={isActive ? "page" : undefined}
      className="rail-link"
      style={{ paddingLeft, paddingRight: 10 }}
    >
      {item.icon && (
        <span className={isActive ? "text-[var(--color-accent)]" : "opacity-70"}>{item.icon}</span>
      )}
      <span className="truncate">{item.name}</span>
    </Link>
  );
}
