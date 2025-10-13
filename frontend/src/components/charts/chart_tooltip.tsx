const CustomTooltip = ({ active, payload, label }: any) => {
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
        {payload.map((entry: any, index: number) => (
          <p key={`item-${index}`}>
            {entry.name}:{" "}
            <span className="text-[var(--color-accent)]">
              ₹{entry.value}
            </span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default CustomTooltip;