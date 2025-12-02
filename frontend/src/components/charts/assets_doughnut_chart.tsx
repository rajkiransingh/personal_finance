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

export default function InvestmentPieChart({ earnings }: { earnings: EarningsData }) {
  if (!earnings) return null;

  const data = Object.entries(earnings).map(([key, value]) => ({
    name: key.replace(/_/g, ' '),
    value,
  }));

  const total = Object.values(earnings).reduce((a, b) => a + b, 0);

  const colorMap: Record<string, string> = {
    Cash: '#50C878',
    Stocks: '#F28500',
    'Mutual Fund': '#99FFFF',
    Gold: '#FADA5E',
    Silver: '#E5E4E2',
    Land: '#9F8170',
    Crypto: '#FFB7C5',
  };

  return (
    <div className="w-full h-[445px] flex flex-col sm:flex-row justify-center items-center sm:items-start">

      {/* Chart Section */}
      <div className="w-full sm:w-2/3 h-[420px]">
        <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={150}
            outerRadius={200}
            paddingAngle={4}
            isAnimationActive={true}
            animationDuration={800}
          >
            {data.map((entry) => (
              <Cell key={`cell-${entry.name}`} fill={colorMap[entry.name] || '#ccc'} />
            ))}
          </Pie>

          <Tooltip contentStyle={{
                                  backgroundColor: 'var(--color-card)',
                                  border: '1px solid var(--color-bg)',
                                  color: 'var(--color-text-primary)',
                                 }}
                             content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const value = payload[0].value;
                              const percentage = ((value / total) * 100).toFixed(1);
                              return (
                                <div className="p-2">
                                  <p className="text-white">
                                    {payload[0].name}: ₹{value.toLocaleString('en-IN')} ({percentage}%)
                                  </p>
                                </div>
                              );
                            }
                            return null;
                          }}
          />

          {/* Center Text */}
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-[var(--color-text-primary)] font-semibold text-xl"
          >
            ₹{total.toLocaleString('en-IN')}
          </text>
        </PieChart>
      </ResponsiveContainer>
      </div>


      {/* Legend Section */}
      <div className="mt-2 sm:mt-4 sm:ml-2 flex flex-col justify-right gap-2 text-sm text-[var(--color-text-secondary)]">
        {data.map(({ name, value }) => (
          <div key={name} className="flex justify-between items-center min-w-[200px] gap-2"> {/* this one aligns the space between text and amount */}
            <div className="flex items-center gap-2 min-w-[100px] text-left">  {/* this one aligns the dots with text and spacing */}
              <span
                className="inline-block w-3 h-3 rounded-full"
                style={{ backgroundColor: colorMap[name] || '#ccc' }}
              ></span>
              {name}
            </div>
            <span className="text-[var(--color-accent)] font-semibold text-right min-w-[90px]">
              ₹{value.toLocaleString('en-IN')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
