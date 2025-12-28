"use client";

import { User } from "lucide-react";

export default function Topbar() {
  return (
    <header className="flex justify-between items-center bg-[var(--color-bg-lighter)] shadow-sm px-6 py-4 border-b border-[var(--color-card)]">
      <h2 className="text-lg font-medium text-[var(--color-text-primary)] opacity-80">Financial Dashboard</h2>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--color-card)] border border-[var(--color-accent)] border-opacity-20">
          <User size={16} className="text-[var(--color-accent)]" />
          <span className="text-sm font-medium text-[var(--color-text-primary)]">Hello, user</span>
        </div>
        <button className="text-xs font-semibold tracking-wider text-[var(--color-text-primary)] opacity-60 hover:opacity-100 transition-opacity uppercase">
          Logout
        </button>
      </div>
    </header>
  );
}
