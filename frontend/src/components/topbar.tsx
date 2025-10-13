"use client";

export default function Topbar() {
  return (
    <header className="flex justify-between items-center bg-[var(--color-bg-lighter)] shadow px-6 py-3">
      <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">Financial Tracker</h2>
      <div className="flex items-center gap-4">
        <span className="text-[var(--color-text-primary)]">Hello, Raj 👋</span>
        <button className="text-[var(--color-text-primary)] px-3 py-1 rounded hover:bg-[var(--color-card)] hover:text-[var(--color-accent)]">
          Logout
        </button>
      </div>
    </header>
  );
}
