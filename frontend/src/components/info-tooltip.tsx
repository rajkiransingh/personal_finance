"use client";

import { Info } from "lucide-react";

export default function InfoTooltip({
  text,
  label = "More information",
  align = "left",
}: {
  text: string;
  label?: string;
  align?: "left" | "right";
}) {
  const position = align === "right" ? "right-0" : "left-1/2 -translate-x-1/2";
  return (
    <span className="group relative inline-flex items-center align-middle">
      <button
        type="button"
        aria-label={`${label}: ${text}`}
        className="inline-flex h-4 w-4 items-center justify-center rounded-full text-current opacity-70 transition-opacity duration-[var(--dur-micro)] hover:opacity-100 focus-visible:opacity-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-current"
      >
        <Info size={12} aria-hidden="true" />
      </button>
      <span
        role="tooltip"
        className={`pointer-events-none absolute bottom-full z-[600] mb-2 w-64 rounded-[var(--radius-panel)] border border-[var(--color-edge)] bg-[var(--color-surface)] p-2.5 text-left text-[length:var(--text-xs)] font-normal leading-relaxed text-[var(--color-ink-2)] opacity-0 shadow-[var(--shadow-pop)] transition-opacity duration-[var(--dur-micro)] group-hover:opacity-100 group-focus-within:opacity-100 ${position}`}
      >
        {text}
      </span>
    </span>
  );
}
