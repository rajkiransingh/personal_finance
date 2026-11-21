export default function Skeleton({ height = 200 }: { height?: number }) {
  return <div className="skeleton w-full" style={{ height }} aria-hidden="true" />;
}
