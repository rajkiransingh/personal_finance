"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { name: "Dashboard", path: "/" },
  { name: "Transactions", path: "/transactions" },
  { name: "Analytics", path: "/analytics" },
  { name: "Settings", path: "/settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="bg-[var(--color-sidebar)] text-[var(--color-text-primary)] w-72 min-h-screen p-6 flex flex-col shadow-lg border-r border-[var(--color-card)]">
      {/* Header */}
      <h1 className="font-playwrite text-2xl mb-6 text-center font-[PlaywriteDeutschlandSchulausgangschri] tracking-wide">
        <span className="inline-flex flex-col items-center gap-1">
          <span className="text-[var(--color-accent)] text-sm tracking-widest">
            ▁ ▃ ▄ ▅
          </span>
          <span className="text-[var(--color-accent)] font-semibold">
            Mera Paisa
          </span>
        </span>
      </h1>

      <div className="h-[1px] bg-[var(--color-card)] mb-8 mx-4"></div>

      {/* Navigation */}
      <nav className="space-y-2 flex-1">
        {navItems.map((item) => {
          const active = pathname === item.path;
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`block px-4 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                active
                  ? "bg-[var(--color-accent)] text-black shadow-inner"
                  : "text-[var(--color-text-secondary)] hover:bg-[var(--color-card)] hover:text-[var(--color-accent)]"
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 text-xs text-center text-[var(--color-text-secondary)] opacity-60">
        v1.0 • Personal Finance
      </div>
    </aside>
  );
}
