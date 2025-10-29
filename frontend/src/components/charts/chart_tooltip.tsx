interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  formatter?: (value: number, name?: string) => string;
}

const CustomTooltip = ({ active, payload, label, formatter }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div
        className="p-3 rounded-md border border-[var(--color-bg)] shadow-md"
        style={{
          backgroundColor: "var(--color-card)",
          color: "var(--color-text-primary)",
          fontSize: "0.875rem",
        }}
      >
        <p className="font-semibold mb-1 text-[var(--color-accent)]">{label}</p>
        {payload.map((entry, index) => (
          <p key={`item-${index}`}>
            {entry.name}:{" "}
            <span className="text-[var(--color-accent)]">
              {formatter ? formatter(Number(entry.value), entry.name) : entry.value}
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default CustomTooltip;
