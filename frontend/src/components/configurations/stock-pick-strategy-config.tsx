'use client';

import { useEffect, useState } from 'react';

export default function StockPickStrategyConfigPage() {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/config/stock-picking-strategy-config")
      .then((res) => res.json())
      .then((data) => setConfig(data));
  }, []);

  // ✅ Update metric value
  const handleMetricChange = (strategy: string, metric: string, value: number) => {
    setConfig((prev: any) => ({
      ...prev,
      strategy: {
        ...prev.strategy,
        [strategy]: {
          ...prev.strategy[strategy],
          metrics: {
            ...prev.strategy[strategy].metrics,
            [metric]: value,
          },
        },
      },
    }));
  };

  // ✅ Update description
  const handleDescriptionChange = (strategy: string, value: string) => {
    setConfig((prev: any) => ({
      ...prev,
      strategy: {
        ...prev.strategy,
        [strategy]: {
          ...prev.strategy[strategy],
          description: value,
        },
      },
    }));
  };

  // ✅ Add new metric
  const handleAddMetric = (strategy: string) => {
    const metricName = prompt("Enter metric name:");
    if (!metricName) return;
    setConfig((prev: any) => ({
      ...prev,
      strategy: {
        ...prev.strategy,
        [strategy]: {
          ...prev.strategy[strategy],
          metrics: {
            ...prev.strategy[strategy].metrics,
            [metricName]: 0,
          },
        },
      },
    }));
  };

  // ✅ Remove a metric
  const handleRemoveMetric = (strategy: string, metric: string) => {
    setConfig((prev: any) => {
      const newMetrics = { ...prev.strategy[strategy].metrics };
      delete newMetrics[metric];
      return {
        ...prev,
        strategy: {
          ...prev.strategy,
          [strategy]: {
            ...prev.strategy[strategy],
            metrics: newMetrics,
          },
        },
      };
    });
  };

  // ✅ Add new strategy (asks for name + description)
  const handleAddStrategy = () => {
    const name = prompt("Enter new strategy name:");
    if (!name) return;
    const description = prompt("Enter description for this strategy:") || "";
    setConfig((prev: any) => ({
      ...prev,
      strategy: {
        ...prev.strategy,
        [name]: {
          metrics: {},
          description,
        },
      },
    }));
  };

  // ✅ Remove a strategy
  const handleRemoveStrategy = (strategy: string) => {
    setConfig((prev: any) => {
      const newStrategies = { ...prev.strategy };
      delete newStrategies[strategy];
      return { ...prev, strategy: newStrategies };
    });
  };

  // ✅ Save + show success popup
  const saveConfig = async () => {
    setSaving(true);
    const res = await fetch("/api/config/stock-picking-strategy-config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config, null, 2),
    });
    setSaving(false);

    if (res.ok) {
      alert("✅ Configuration saved successfully!");
    } else {
      alert("❌ Failed to save configuration. Please check the console.");
    }
  };

  if (!config) return <div>Loading configuration...</div>;

  return (
    <div className="bg-[var(--color-card)] p-6 rounded-xl shadow-md space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-[var(--color-accent)]">
          Stock Score Configuration
        </h2>
        <button
          onClick={handleAddStrategy}
          className="bg-[var(--color-accent)] text-black px-3 py-1 rounded hover:bg-[var(--color-accent-hover)]"
        >
          + Add Strategy
        </button>
      </div>

      {Object.entries(config.strategy).map(([strategy, data]: any) => (
        <div
          key={strategy}
          className="border border-[var(--color-bg-lighter)] p-4 rounded-lg bg-[var(--color-bg-lighter)/20] space-y-4"
        >
          {/* Strategy header */}
          <div className="border border-[var(--color-card)] rounded-md p-3 bg-[var(--color-bg)] space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-[var(--color-text-secondary)]">
                {strategy}
              </h3>
              <button
                onClick={() => handleRemoveStrategy(strategy)}
                className="bg-red-400 px-3 py-1 rounded text-white"
              >
                ✕ Delete Strategy
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-medium text-[var(--color-accent-hover)]">Description:</span>
              <input
                type="text"
                value={data.description}
                onChange={(e) => handleDescriptionChange(strategy, e.target.value)}
                className="flex-1 p-1 rounded text-[var(--color-text-primary)] bg-[var(--color-bg)]"
              />
            </div>
          </div>

          {/* Metrics */}
          <h4 className="text-sm font-medium text-[var(--color-accent-hover)] ml-4">Metrics</h4>
          <div className="space-y-2 ml-6">
            {Object.entries(data.metrics).map(([metric, value]: any) => (
              <div
                key={metric}
                className="flex justify-between items-center border border-[var(--color-bg-lighter)] rounded-md p-2"
              >
                <span>{metric}</span>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    step="0.01"
                    value={value}
                    onChange={(e) =>
                      handleMetricChange(strategy, metric, Number(e.target.value))
                    }
                    className="w-24 p-1 rounded text-right border border-[var(--color-bg-lighter)] bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                  />
                  <button
                    onClick={() => handleRemoveMetric(strategy, metric)}
                    className="bg-red-400 px-3 py-1 rounded text-white"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => handleAddMetric(strategy)}
            className="text-sm text-[var(--color-accent)] hover:underline mt-2 block"
          >
            + Add Metric
          </button>
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
