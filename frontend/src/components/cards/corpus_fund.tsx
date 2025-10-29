interface CorpusProps {
  percentage: number;
}

export default function Corpus({ percentage }: CorpusProps) {
  return (
    <div className="card col-span-3 bg-[var(--color-card)] p-6 rounded-lg">
      {/* Corpus Fund Progress Bar */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Corpus Fund</h2>
        <span className="text-2xl font-bold text-[var(--color-accent)]">{percentage}%</span>
      </div>

      <div className="w-full bg-[var(--color-bg)] rounded-full h-3 overflow-hidden">
        <div
          className="bg-[var(--color-accent)] h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>

      <p className="text-xs text-[var(--color-text-secondary)] mt-3">
        {percentage}% of Emergency fund available
      </p>
    </div>
  );
}
