'use client';

import React, { useState, useEffect } from "react";
import { Plus, Trash2, Save } from "lucide-react";

export default function PortfolioConfigPage() {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/config/portfolio-config")
      .then((res) => res.json())
      .then((data) => setConfig(data));
  }, []);

  // Main allocation weight change
  const handleTargetChange = (target: string, value: any) => {
    setConfig((prev: any) => ({
      ...prev,
      targets: {
        ...prev.targets,
        [target]: { ...prev.targets[target], weight: value },
      },
    }));
  };

  // Sub-allocation change
  const handleSubChange = (target: string, sub: string, value: any) => {
    setConfig((prev: any) => ({
      ...prev,
      targets: {
        ...prev.targets,
        [target]: {
          ...prev.targets[target],
          sub_allocations: {
            ...prev.targets[target].sub_allocations,
            [sub]: value,
          },
        },
      },
    }));
  };

  // Add sub-allocation
  const handleAddSub = (target: string) => {
    const newSub = prompt("Enter new sub-allocation name:");
    if (!newSub) return;
    setConfig((prev: any) => ({
      ...prev,
      targets: {
        ...prev.targets,
        [target]: {
          ...prev.targets[target],
          sub_allocations: {
            ...prev.targets[target].sub_allocations,
            [newSub]: 0,
          },
        },
      },
    }));
  };

  // Remove sub-allocation
  const handleRemoveSub = (target: string, sub: string) => {
    setConfig((prev: any) => {
      const newTargets = { ...prev.targets };
      delete newTargets[target].sub_allocations[sub];
      return { ...prev, targets: newTargets };
    });
  };

  // Add main allocation
  const handleAddAllocation = () => {
    const newAlloc = prompt("Enter new allocation name:");
    if (!newAlloc) return;
    setConfig((prev: any) => ({
      ...prev,
      targets: {
        ...prev.targets,
        [newAlloc]: {
          weight: 0,
          sub_allocations: {},
        },
      },
    }));
  };

  // Remove main allocation
  const handleRemoveAllocation = (target: string) => {
    setConfig((prev: any) => {
      const newTargets = { ...prev.targets };
      delete newTargets[target];
      return { ...prev, targets: newTargets };
    });
  };

  // Save config via POST
  const saveConfig = async () => {
    setSaving(true);
    try {
      const res = await fetch("/api/config/portfolio-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config, null, 2),
      });
      if (!res.ok) throw new Error("Save failed");
      alert("Configuration saved successfully!");
    } catch (err) {
      console.error(err);
      alert("Error saving configuration");
    } finally {
      setSaving(false);
    }
  };

  if (!config) {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="Loading configuration">
        <div className="skeleton h-9 w-1/3" />
        <div className="skeleton h-40 w-full" />
        <div className="skeleton h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <h1 className="page-title">Portfolio configuration</h1>
          <p className="page-sub">
            Target weights and sub-allocations saved to the rebalancing policy.
          </p>
        </div>
        <button
          onClick={handleAddAllocation}
          className="btn btn-secondary"
        >
          <Plus size={15} aria-hidden="true" />
          Add allocation
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(config.targets).map(([target, data]: any) => (
          <section key={target} className="card">
            {/* Main allocation header */}
            <div className="card-head flex-wrap">
              <h2 className="card-title">{target}</h2>
              <div className="flex flex-wrap items-center gap-2">
                <label className="field-label mb-0" htmlFor={`weight-${target}`}>
                  Weight %
                </label>
                <input
                  id={`weight-${target}`}
                  type="number"
                  step="0.01"
                  value={data.weight ?? 0}
                  onChange={(e) =>
                    handleTargetChange(target, Number(e.target.value))
                  }
                  className="field field-num"
                />
                <button
                  onClick={() => handleRemoveAllocation(target)}
                  className="btn btn-danger btn-sm"
                  aria-label={`Delete ${target} allocation`}
                >
                  <Trash2 size={13} aria-hidden="true" />
                  Delete
                </button>
              </div>
            </div>

            {/* Sub-allocations */}
            {data.sub_allocations && (
              <div className="p-5">
                <h3 className="label mb-3">Sub-allocations</h3>
                <div className="space-y-2">
                  {Object.entries(data.sub_allocations).map(([sub, val]: any) => (
                    <div
                      key={sub}
                      className="well flex flex-wrap items-center justify-between gap-2"
                    >
                      <span className="text-[length:var(--text-sm)] font-medium text-[var(--color-ink)]">{sub}</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          step="0.01"
                          value={val}
                          onChange={(e) =>
                            handleSubChange(target, sub, Number(e.target.value))
                          }
                          className="field field-num"
                          aria-label={`${sub} weight`}
                        />
                        <button
                          onClick={() => handleRemoveSub(target, sub)}
                          className="btn btn-danger btn-sm btn-icon"
                          aria-label={`Remove ${sub}`}
                        >
                          <Trash2 size={13} aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => handleAddSub(target)}
                  className="link mt-4 inline-flex items-center gap-1 text-[length:var(--text-sm)]"
                >
                  <Plus size={13} aria-hidden="true" />
                  Add sub-allocation
                </button>
              </div>
            )}
          </section>
        ))}
      </div>

      <div className="flex justify-end">
        <button
          onClick={saveConfig}
          disabled={saving}
          className="btn btn-primary"
        >
          <Save size={15} aria-hidden="true" />
          {saving ? "Saving" : "Save configuration"}
        </button>
      </div>
    </div>
  );
}
