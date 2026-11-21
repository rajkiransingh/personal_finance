'use client';

import React, { useState, useEffect } from "react";
import { ChevronRight, Save } from "lucide-react";

const sections = {
  "Database Setup": [
    "MYSQL_ROOT_PASSWORD",
    "MYSQL_DATABASE",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
  ],
  "Currency Exchange": [
    "EXCHANGE_API_URL",
    "EXCHANGE_RATE_API_KEY",
  ],
  "Stock Data": [
    "ALPHA_VANTAGE_API_KEY",
    "NSE_WEBSITE_URL",
  ],
  "Mutual Funds": [
    "RAPID_API_MF_HOST",
    "RAPID_API_MF_BASE_URL",
    "RAPID_MF_API_KEY",
  ],
  "Bullion Rates": [
    "CITY",
    "RAPID_API_BULLION_HOST",
    "RAPID_API_BULLION_BASE_URL",
    "GOLD_API",
    "SILVER_API",
    "RAPID_API_KEY",
    "METAL_RATES_WEBSITE",
  ],
  "Crypto": [
    "COIN_MARKET_URL",
    "COIN_MARKET_CAP_API_KEY",
  ],
  "AWS Lambda": [
    "AWS_REGION",
    "AWS_PROFILE",
    "LAMBDA_FUNCTION_NAME",
    "LAMBDA_FUNCTION_ARN",
    "S3_BUCKET",
  ],
};

export default function EnvironmentConfigPage() {
  const [envConfig, setEnvConfig] = useState<Record<string, string> | null>(null);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/config/environment-config")
      .then((res) => res.json())
      .then((data) => setEnvConfig(data));
  }, []);

  const handleChange = (key: string, value: string) => {
    if (envConfig) {
      setEnvConfig({ ...envConfig, [key]: value });
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/config/environment-config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(envConfig),
      });
      if (res.ok) {
        alert('Environment variables saved successfully!');
      } else {
        alert('Failed to save. Check server logs.');
      }
    } catch (err) {
      console.error(err);
      alert('Error saving environment variables.');
    } finally {
      setSaving(false);
    }
  };

  if (!envConfig) {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="Loading environment configuration">
        <div className="skeleton h-9 w-1/3" />
        <div className="skeleton h-16 w-full" />
        <div className="skeleton h-16 w-full" />
        <div className="skeleton h-16 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8">
      <div className="page-head">
        <div>
          <h1 className="page-title">Environment variables</h1>
          <p className="page-sub">
            Service credentials and endpoints used by the data pipelines.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {Object.entries(sections).map(([sectionName, keys]) => {
          const isCollapsed = collapsed[sectionName] ?? false;
          const panelId = `env-panel-${sectionName.replace(/\s+/g, '-').toLowerCase()}`;

          return (
            <section key={sectionName} className="card overflow-hidden">
              {/* Header */}
              <button
                type="button"
                aria-expanded={!isCollapsed}
                aria-controls={panelId}
                className="flex w-full items-center justify-between gap-3 px-5 py-3.5 text-left transition-colors hover:bg-[var(--color-well)]"
                onClick={() =>
                  setCollapsed(prev => ({ ...prev, [sectionName]: !prev[sectionName] }))
                }
              >
                <h2 className="text-[length:var(--text-md)] font-semibold text-[var(--color-ink)]">{sectionName}</h2>
                <span className="flex items-center gap-3">
                  <span className="card-note">{keys.length} keys</span>
                  <ChevronRight
                    size={16}
                    aria-hidden="true"
                    className={`shrink-0 text-[var(--color-muted)] transition-transform duration-[var(--dur-short)] ease-[var(--ease-out)] ${
                      isCollapsed ? '' : 'rotate-90'
                    }`}
                  />
                </span>
              </button>

              {/* Content */}
              {!isCollapsed && (
                <div
                  id={panelId}
                  className="grid grid-cols-1 gap-4 border-t border-[var(--color-rule)] p-5 md:grid-cols-2"
                >
                  {keys.map(key => (
                    <div key={key} className="flex flex-col">
                      <label className="field-label" htmlFor={`env-${key}`}>{key}</label>
                      <input
                        id={`env-${key}`}
                        type="text"
                        className="field"
                        value={envConfig[key] || ""}
                        onChange={(e) => handleChange(key, e.target.value)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </section>
          );
        })}
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn btn-primary"
        >
          <Save size={15} aria-hidden="true" />
          {saving ? 'Saving' : 'Save environment'}
        </button>
      </div>
    </div>
  );
}
