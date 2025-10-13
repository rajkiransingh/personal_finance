export default function Corpus() {
  return (
    <div className="card col-span-3 bg-[var(--color-card)] p-6 rounded-lg">
      {/* Corpus Fund Progress Bar */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Corpus Fund</h2>
        <span className="text-2xl font-bold text-[var(--color-accent)]">75%</span>
      </div>

      <div className="w-full bg-[var(--color-bg)] rounded-full h-3 overflow-hidden">
        <div
          className="bg-[var(--color-accent)] h-full rounded-full transition-all duration-500"
          style={{ width: `75%` }}
        ></div>
      </div>

      <p className="text-xs text-[var(--color-text-secondary)] mt-3">
        75% of Emergency fund available
      </p>
    </div>
  );
}
