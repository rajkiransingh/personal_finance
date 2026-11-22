"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface Strategy {
  description?: string;
  metrics?: Record<string, number>;
}
interface StrategyConfig {
  strategy?: Record<string, Strategy>;
}

export default function StockPickingStrategyPage() {
  const { preferences, savePreferences } = useAuth();
  const [config, setConfig] = useState<StrategyConfig | null>(null);
  const [active, setActive] = useState<string>("");
  const [overrides, setOverrides] = useState<Record<string, number>>({});
  const [message, setMessage] = useState("");

  useEffect(() => {
    void apiFetch("/api/config/stock-picking-strategy-config")
      .then((res) => res.json())
      .then(setConfig)
      .catch(() => setConfig(null));
    const saved = preferences.strategies || {};
    setActive(typeof saved.active === "string" ? saved.active : "");
    setOverrides(
      saved.overrides && typeof saved.overrides === "object"
        ? (saved.overrides as Record<string, number>)
        : {}
    );
  }, [preferences.strategies]);

  const names = Object.keys(config?.strategy || {});
  const metrics = active ? config?.strategy?.[active]?.metrics || {} : {};
  const effective = (name: string, base: number) => overrides[name] ?? base;

  const save = async () => {
    await savePreferences({
      strategies: { active, overrides },
    });
    setMessage("Your strategy choice is saved to your account.");
  };

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">
          Stock-picking strategy
        </h1>
        <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
          The administrator sets the default weights. Your choice and tweaks are saved to your account.
        </p>
      </div>

      <section className="card">
        <div className="card-head">
          <div>
            <h2 className="card-title">Choose a strategy</h2>
            <span className="card-note">Applies to your screener view only</span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 p-5">
          {names.length === 0 && (
            <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
              No strategies are configured yet.
            </p>
          )}
          {names.map((name) => (
            <button
              key={name}
              type="button"
              className={active === name ? "btn btn-primary" : "btn btn-secondary"}
              onClick={() => {
                setActive(name);
                setOverrides({});
              }}
            >
              {name}
            </button>
          ))}
        </div>
      </section>

      {active && (
        <section className="card">
          <div className="card-head">
            <div>
              <h2 className="card-title">{active} weights</h2>
              <span className="card-note">Blank means the administrator default</span>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-3 p-5 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(metrics).map(([metric, base]) => (
              <div key={metric}>
                <label className="field-label" htmlFor={`metric-${metric}`}>
                  {metric} <span className="text-[var(--color-muted)]">· default {base}</span>
                </label>
                <input
                  id={`metric-${metric}`}
                  className="field field-num"
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder={String(base)}
                  value={overrides[metric] ?? ""}
                  onChange={(event) =>
                    setOverrides((current) => {
                      const next = { ...current };
                      if (event.target.value === "") delete next[metric];
                      else next[metric] = Number(event.target.value);
                      return next;
                    })
                  }
                />
                <p className="field-help">Effective weight: {effective(metric, Number(base))}</p>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-3 border-t border-[var(--color-rule)] px-5 py-4">
            <button className="btn btn-primary" type="button" onClick={() => void save()}>
              Save my strategy
            </button>
            {message && <span className="text-[length:var(--text-sm)] font-semibold text-[var(--color-success-text)]">{message}</span>}
          </div>
        </section>
      )}
    </div>
  );
}
