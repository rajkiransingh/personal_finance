'use client';

import React, { useState, useEffect } from "react";

export default function PortfolioConfigPage() {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/config/portfolio-config")
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
      const res = await fetch("http://localhost:8000/config/portfolio-config", {
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

  if (!config) return <div>Loading configuration...</div>;

  return (
    <div className="bg-[var(--color-card)] p-6 rounded-xl shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-[var(--color-accent)]">
          Portfolio Configuration
        </h2>
        <button
          onClick={handleAddAllocation}
          className="bg-[var(--color-accent)] text-black px-3 py-1 rounded hover:bg-[var(--color-accent-hover)]"
        >
          + Add Allocation
        </button>
      </div>

      {Object.entries(config.targets).map(([target, data]: any) => (
        <div
          key={target}
          className="mb-6 border border-[var(--color-bg-lighter)] rounded-lg p-4 bg-[var(--color-bg-lighter)/30]"
        >
          {/* Main allocation header */}
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-[var(--color-text-secondary)]">
              {target}
            </h3>
            <div className="flex gap-2">
              <input
                type="number"
                step="0.01"
                value={data.weight ?? 0}
                onChange={(e) =>
                  handleTargetChange(target, Number(e.target.value))
                }
                className="w-28 text-right border border-[var(--color-card)] bg-[var(--color-bg)] p-2 rounded text-[var(--color-text-primary)]"
              />
              <button
                onClick={() => handleRemoveAllocation(target)}
                className="bg-red-400 px-3 py-1 rounded text-white"
              >
                ✕ Delete
              </button>
            </div>
          </div>

          {/* Sub-allocations */}
          {data.sub_allocations && (
            <div className="ml-4">
              <h4 className="text-sm mb-3 text-[var(--color-accent-hover)]">
                Sub-Allocations
              </h4>
              <div className="space-y-2 ">
                {Object.entries(data.sub_allocations).map(([sub, val]: any) => (
                  <div
                    key={sub}
                    className="flex justify-between items-center border border-[var(--color-bg)] ml-4 rounded-md p-2"
                  >
                    <span>{sub}</span>
                    <div className="flex gap-2 items-center ">
                      <input
                        type="number"
                        step="0.01"
                        value={val}
                        onChange={(e) =>
                          handleSubChange(target, sub, Number(e.target.value))
                        }
                        className="w-20 bg-[var(--color-bg)] p-1 rounded text-right text-[var(--color-text-primary)] border border-[var(--color-bg-lighter)] "
                      />
                      <button
                        onClick={() => handleRemoveSub(target, sub)}
                        className="bg-red-400 px-3 py-1 rounded text-white"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleAddSub(target)}
                className="text-sm text-[var(--color-accent)] hover:underline mt-3 block"
              >
                + Add Sub-Allocation
              </button>
            </div>
          )}
        </div>
      ))}

      <button
        onClick={saveConfig}
        disabled={saving}
        className="mt-4 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-black px-4 py-2 rounded"
      >
        {saving ? "Saving..." : "💾 Save Configuration"}
      </button>
    </div>
  );
}
