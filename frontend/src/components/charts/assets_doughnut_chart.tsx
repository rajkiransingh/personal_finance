'use client';

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

interface EarningsData {
  Cash: number;
  Stocks: number;
  Mutual_Fund: number;
  Gold: number;
  Silver: number;
  Land: number;
  Crypto: number;
}

const colorMap: Record<string, string> = {
  Cash: 'var(--chart-2)',
  Stocks: 'var(--chart-3)',
  'Mutual Fund': 'var(--chart-5)',
  Gold: 'var(--chart-1)',
  Silver: 'var(--chart-7)',
  Land: 'var(--chart-6)',
  Crypto: 'var(--chart-4)',
};

const formatCurrency = (value: number): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '₹ 0';
  const absValue = Math.abs(value);
  if (absValue >= 10000000) {
    return `₹ ${(value / 10000000).toFixed(2)} Cr`;
  } else if (absValue >= 100000) {
    return `₹ ${(value / 100000).toFixed(2)} L`;
  } else if (absValue >= 1000) {
    return `₹ ${(value / 1000).toFixed(1)} K`;
  } else {
    return `₹ ${value.toLocaleString('en-IN')}`;
  }
};

export default function InvestmentPieChart({ earnings }: { earnings: EarningsData }) {
  if (!earnings) return null;

  const data = Object.entries(earnings)
    .map(([key, value]) => ({
      name: key.replace(/_/g, ' '),
      value: Number(value) || 0,
    }))
    .filter((d) => d.value > 0);

  const total = Object.values(earnings).reduce((a, b) => a + (Number(b) || 0), 0);

  return (
    <div className="flex w-full flex-col items-center justify-center gap-4 py-2">
      <div
        className="relative h-[300px] w-full md:h-[380px]"
        role="img"
        aria-label={`Asset distribution: ${data
          .map((entry) => `${entry.name} ${total > 0 ? ((entry.value / total) * 100).toFixed(1) : '0.0'} percent`)
          .join(', ')}`}
      >
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius="52%"
              outerRadius="82%"
              paddingAngle={2}
              isAnimationActive={false}
            >
              {data.map((entry) => (
                <Cell
                  key={`cell-${entry.name}`}
                  fill={colorMap[entry.name] || 'var(--color-muted)'}
                  stroke="var(--color-surface)"
                  strokeWidth={2}
                />
              ))}
            </Pie>

            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const entry = payload[0];
                  const value = Number(entry.value) || 0;
                  const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
                  return (
                    <div className="rounded-[var(--radius-panel)] border border-[var(--color-edge)] bg-[var(--color-surface)] p-3 text-xs shadow-[var(--shadow-pop)]">
                      <div className="mb-1 flex items-center gap-2">
                        <span
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: colorMap[entry.name as string] || 'var(--color-muted)' }}
                        />
                        <span className="font-semibold text-[var(--color-ink)]">{entry.name}</span>
                      </div>
                      <div className="flex justify-between gap-4 text-[var(--color-ink-2)]">
                        <span>Amount</span>
                        <span className="font-semibold tabular-nums text-[var(--color-ink)]">
                          ₹{value.toLocaleString('en-IN')}
                        </span>
                      </div>
                      <div className="mt-0.5 flex justify-between gap-4 text-[var(--color-muted)]">
                        <span>Share</span>
                        <span className="font-medium tabular-nums text-[var(--color-accent)]">{pct}%</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            <text
              x="50%"
              y="46%"
              textAnchor="middle"
              dominantBaseline="middle"
              fill="var(--color-muted)"
              fontSize={12}
              fontWeight={600}
            >
              Assets before liabilities
            </text>
            <text
              x="50%"
              y="56%"
              textAnchor="middle"
              dominantBaseline="middle"
              fill="var(--color-ink)"
              fontSize={26}
              fontWeight={700}
            >
              {formatCurrency(total)}
            </text>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid w-full grid-cols-2 gap-x-4 gap-y-1.5 sm:grid-cols-3 lg:grid-cols-4">
        {data.map(({ name, value }) => {
          const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
          return (
            <div
              key={name}
              className="flex flex-col items-center gap-0.5 rounded-[8px] px-1 py-1.5 text-[12px] transition-colors duration-[var(--dur-micro)] hover:bg-[var(--color-well)]"
            >
              <span className="flex max-w-full items-center gap-1.5">
                <span
                  className="h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ backgroundColor: colorMap[name] || 'var(--color-muted)' }}
                />
                <span className="truncate font-medium text-[var(--color-ink-2)]">{name}</span>
                <span className="text-[11px] text-[var(--color-muted)]">{pct}%</span>
              </span>
              <span className="font-semibold tabular-nums text-[var(--color-ink)]">
                {formatCurrency(value)}
              </span>
            </div>
          );
        })}
      </div>
      <p className="w-full text-center text-[length:var(--text-xs)] text-[var(--color-muted)]">
        Land is carried at a manually recorded local value, not a live market price.
      </p>
    </div>
  );
}
