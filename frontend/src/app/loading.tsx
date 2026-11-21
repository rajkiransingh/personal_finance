export default function Loading() {
  return (
    <div className="space-y-6 py-4" aria-busy="true" aria-label="Loading page">
      {/* Title skeleton */}
      <div className="flex items-center justify-between gap-4">
        <div className="skeleton h-9 w-1/3" />
        <div className="skeleton h-9 w-28" />
      </div>

      {/* Hero progress skeleton */}
      <div className="skeleton h-24 w-full" />

      {/* KPI Cards skeleton */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <div className="skeleton h-32" />
        <div className="skeleton h-32" />
        <div className="skeleton h-32" />
      </div>

      {/* Main Grid skeleton */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="skeleton h-[420px] lg:col-span-2" />
        <div className="skeleton h-[420px]" />
      </div>
    </div>
  );
}
