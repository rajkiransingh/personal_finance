'use client';

import { useEffect, useState } from 'react';
import { Plus, Trash2, Save } from 'lucide-react';

export default function StockPickStrategyConfigPage() {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/config/stock-picking-strategy-config")
      .then((res) => res.json())
      .then((data) => setConfig(data));
  }, []);

  // Update metric value
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

  // Update description
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

  // Add new metric
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

  // Remove a metric
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

  // Add new strategy (asks for name + description)
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

  // Remove a strategy
  const handleRemoveStrategy = (strategy: string) => {
    setConfig((prev: any) => {
      const newStrategies = { ...prev.strategy };
      delete newStrategies[strategy];
      return { ...prev, strategy: newStrategies };
    });
  };

  // Save and report the result
  const saveConfig = async () => {
    setSaving(true);
    const res = await fetch("/api/config/stock-picking-strategy-config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config, null, 2),
    });
    setSaving(false);

    if (res.ok) {
      alert("Configuration saved successfully.");
    } else {
      alert("Failed to save configuration. Please check the console.");
    }
  };

  if (!config) {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="Loading configuration">
        <div className="skeleton h-9 w-1/3" />
        <div className="skeleton h-48 w-full" />
        <div className="skeleton h-48 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <h1 className="page-title">Stock score configuration</h1>
          <p className="page-sub">
            Scoring strategies and the metrics each one weighs.
          </p>
        </div>
        <button
          onClick={handleAddStrategy}
          className="btn btn-secondary"
        >
          <Plus size={15} aria-hidden="true" />
          Add strategy
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(config.strategy).map(([strategy, data]: any) => (
          <section key={strategy} className="card">
            {/* Strategy header */}
            <div className="card-head flex-wrap">
              <h2 className="card-title">{strategy}</h2>
              <button
                onClick={() => handleRemoveStrategy(strategy)}
                className="btn btn-danger btn-sm"
              >
                <Trash2 size={13} aria-hidden="true" />
                Delete strategy
              </button>
            </div>

            <div className="p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <label className="field-label mb-0 shrink-0" htmlFor={`desc-${strategy}`}>
                  Description
                </label>
                <input
                  id={`desc-${strategy}`}
                  type="text"
                  value={data.description}
                  onChange={(e) => handleDescriptionChange(strategy, e.target.value)}
                  className="field flex-1"
                />
              </div>

              {/* Metrics */}
              <h3 className="label mb-3 mt-5">Metrics</h3>
              <div className="space-y-2">
                {Object.entries(data.metrics).map(([metric, value]: any) => (
                  <div
                    key={metric}
                    className="well flex flex-wrap items-center justify-between gap-2"
                  >
                    <span className="text-[length:var(--text-sm)] font-medium text-[var(--color-ink)]">{metric}</span>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        step="0.01"
                        value={value}
                        onChange={(e) =>
                          handleMetricChange(strategy, metric, Number(e.target.value))
                        }
                        className="field field-num"
                        aria-label={`${metric} value`}
                      />
                      <button
                        onClick={() => handleRemoveMetric(strategy, metric)}
                        className="btn btn-danger btn-sm btn-icon"
                        aria-label={`Remove ${metric}`}
                      >
                        <Trash2 size={13} aria-hidden="true" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleAddMetric(strategy)}
                className="link mt-4 inline-flex items-center gap-1 text-[length:var(--text-sm)]"
              >
                <Plus size={13} aria-hidden="true" />
                Add metric
              </button>
            </div>
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
