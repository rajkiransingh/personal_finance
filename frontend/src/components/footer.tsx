"use client";

import React from "react";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-[var(--color-rule)] bg-[var(--color-paper)]">
      <div className="mx-auto flex w-full max-w-[1440px] flex-col justify-between gap-3 px-5 py-5 text-[12px] text-[var(--color-muted)] sm:flex-row sm:items-center md:px-8">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="wordmark text-[var(--color-primary)]">Mera Paisa</span>
          <span className="h-3 w-px bg-[var(--color-rule)]" aria-hidden="true" />
          <span>Personal wealth and cash flow tracker</span>
        </div>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span>Version 1.2.0</span>
          <span className="h-3 w-px bg-[var(--color-rule)]" aria-hidden="true" />
          <span>Copyright {currentYear} Mera Paisa</span>
        </div>
      </div>
    </footer>
  );
}
