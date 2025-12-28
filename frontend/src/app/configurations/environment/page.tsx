'use client';

import React, { useState, useEffect } from "react";

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

  if (!envConfig) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 text-[var(--color-accent)]">Environment Variables</h1>

      {Object.entries(sections).map(([sectionName, keys]) => {
        const isCollapsed = collapsed[sectionName] ?? false;

        return (
          <div key={sectionName} className="mb-4 shadow-lg">
            {/* Header */}
            <div
              className={`
                card cursor-pointer flex justify-between items-center p-3
                bg-[var(--color-card)]
                ${isCollapsed ? 'rounded-2xl' : 'rounded-t-2xl'}
                transition-all duration-200 ease-in-out
              `}
              onClick={() =>
                setCollapsed(prev => ({ ...prev, [sectionName]: !prev[sectionName] }))
              }
            >
              <h2 className="font-semibold text-[var(--color-accent)]">{sectionName}</h2>
              <span className="text-xl font-bold">{isCollapsed ? "+" : "-"}</span>
            </div>

            {/* Content */}
            {!isCollapsed && (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 rounded-b-2xl bg-[var(--color-card)]">
                {keys.map(key => (
                  <div key={key} className="flex flex-col">
                    <label className="font-medium mb-1">{key}</label>
                    <input
                      type="text"
                      className="p-2 border rounded"
                      value={envConfig[key] || ""}
                      onChange={(e) => handleChange(key, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-all"
      >
        {saving ? 'Saving...' : 'Save'}
      </button>
    </div>
  );
}
