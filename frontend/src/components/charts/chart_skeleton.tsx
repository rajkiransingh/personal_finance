export default function Skeleton({ height = 200 }: { height?: number }) {
  return (
    <div
      className="animate-pulse bg-[var(--color-card)] rounded-lg"
      style={{ height }}
    ></div>
  );
}
