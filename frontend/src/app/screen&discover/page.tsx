'use client';

import { useState, useRef, useEffect } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useDebounce } from 'use-debounce';
import { Search, ChevronRight, Eye, EyeOff } from 'lucide-react';

// --- Types ---
interface StockData {
  symbol: string;
  sector: string;
  sub_sector: string;
  core: number;
  accelerators: number;
  gem: number;
  market_cap: number;
  pe_ratio: number;
  pb_ratio: number;
  peg_ratio: number;
  roe: number;
  roce: number;
  debt_to_equity: number;
  promoter_holding: number;
  ebitda_margin: number;
  ev_ebitda: number;
  recommendation?: string;
  reason?: string;
}

interface ApiResponse {
  data: StockData[];
  page: number;
  limit: number;
  total: number;
  pages: number;
  has_more: boolean;
}

// --- Components ---

function ScoreBox({ label, value }: { label: string; value: number }) {
  const isHigh = value > 0.2;
  const isLow = value < -0.2;

  const colorClass = isHigh
    ? 'border-[color-mix(in_oklab,var(--color-success)_30%,transparent)] bg-[color-mix(in_oklab,var(--color-success)_10%,transparent)] text-[var(--color-success-text)]'
    : isLow
    ? 'border-[color-mix(in_oklab,var(--color-danger)_28%,transparent)] bg-[color-mix(in_oklab,var(--color-danger)_10%,transparent)] text-[var(--color-danger-text)]'
    : 'border-[color-mix(in_oklab,var(--color-warning)_32%,transparent)] bg-[color-mix(in_oklab,var(--color-warning)_12%,transparent)] text-[color-mix(in_oklab,var(--color-warning)_70%,var(--color-ink))]';

  return (
    <span className={`rounded-[6px] border px-2 py-0.5 text-[length:var(--text-xs)] font-semibold tabular-nums ${colorClass}`}>
      {label}: {value.toFixed(2)}
    </span>
  );
}

function StockCard({ stock }: { stock: StockData }) {
  const [showFundamentals, setShowFundamentals] = useState(false);
  const isSell = stock.recommendation === 'Sell';

  return (
    <article
      className={`card card-interactive flex h-48 flex-col justify-between p-4 ${
        isSell ? 'border-[color-mix(in_oklab,var(--color-danger)_45%,var(--color-edge))]' : ''
      }`}
    >
      <div className="min-w-0">
        <div className="mb-1 flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h2 className="truncate font-body text-[length:var(--text-lg)] font-semibold leading-tight text-[var(--color-ink)]">
              {stock.symbol}
            </h2>
            <p className="max-w-[180px] truncate text-[length:var(--text-xs)] text-[var(--color-muted)]">
              {stock.sub_sector || stock.sector}
            </p>
          </div>
          {isSell ? (
            <span className="badge badge-negative">Sell</span>
          ) : (
            <span className="badge badge-neutral">{stock.sector}</span>
          )}
        </div>

        {!showFundamentals ? (
          <div className="mt-3">
            {isSell ? (
              <p className="rounded-[var(--radius-panel)] border border-[color-mix(in_oklab,var(--color-danger)_25%,transparent)] bg-[color-mix(in_oklab,var(--color-danger)_8%,transparent)] p-2 text-[length:var(--text-xs)] text-[var(--color-danger-text)]">
                {stock.reason || "Flagged for risk / underperformance"}
              </p>
            ) : (
              <div className="mt-2 flex flex-wrap gap-1.5">
                <ScoreBox label="Core" value={stock.core} />
                <ScoreBox label="Acc" value={stock.accelerators} />
                <ScoreBox label="GEM" value={stock.gem} />
              </div>
            )}
          </div>
        ) : (
          <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-[length:var(--text-xs)] text-[var(--color-ink-2)]">
            <div><dt className="inline">MC: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{(stock.market_cap / 1000).toFixed(1)}K Cr</dd></div>
            <div><dt className="inline">PE: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{stock.pe_ratio.toFixed(1)}</dd></div>
            <div><dt className="inline">PB: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{stock.pb_ratio.toFixed(1)}</dd></div>
            <div><dt className="inline">ROE: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{stock.roe.toFixed(1)}%</dd></div>
            <div><dt className="inline">D/E: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{stock.debt_to_equity.toFixed(1)}</dd></div>
            <div><dt className="inline">Prom: </dt><dd className="inline font-semibold tabular-nums text-[var(--color-ink)]">{stock.promoter_holding.toFixed(1)}%</dd></div>
          </dl>
        )}
      </div>

      <div className="flex items-center justify-between gap-2 border-t border-[var(--color-rule)] pt-2 text-[length:var(--text-xs)]">
        <button
          type="button"
          onClick={() => setShowFundamentals(!showFundamentals)}
          className="link inline-flex items-center gap-1"
        >
          {showFundamentals ? <EyeOff size={13} aria-hidden="true" /> : <Eye size={13} aria-hidden="true" />}
          {showFundamentals ? 'Show scores' : 'Fundamentals'}
        </button>
        <span className="font-medium tabular-nums text-[var(--color-muted)]">
          ROCE: {stock.roce.toFixed(1)}%
        </span>
      </div>
    </article>
  );
}

// --- Main Page ---

export default function ScreenNDiscover() {
  // State
  const [activeTab, setActiveTab] = useState<'Candidates' | 'Invested'>('Candidates');
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounce(search, 400);
  const [sector, setSector] = useState('All');
  const [subSector, setSubSector] = useState('All');
  const [filterType, setFilterType] = useState<'All' | 'Core' | 'Accelerator' | 'GEM'>('All');

  // Dynamic Filters State
  const [filters, setFilters] = useState<{ sectors: Record<string, string[]> }>({ sectors: {} });
  const [availableSubSectors, setAvailableSubSectors] = useState<string[]>([]);

  // Invested Data State
  const [investedStocks, setInvestedStocks] = useState<StockData[]>([]);
  const [investedLoading, setInvestedLoading] = useState(false);

  const parentRef = useRef<HTMLDivElement>(null);

  // Fetch Filters on Mount
  useEffect(() => {
    async function fetchFilters() {
      try {
        const res = await fetch('/api/analytics/filters');
        if (res.ok) {
          const data = await res.json();
          setFilters(data);
        }
      } catch (err) {
        console.error("Failed to fetch filters", err);
      }
    }
    fetchFilters();
  }, []);

  // Fetch Invested Stocks on Tab Switch
  useEffect(() => {
      if (activeTab === 'Invested') {
          setInvestedLoading(true);
          fetch('/api/analytics/invested_scores')
             .then(res => res.json())
             .then(data => {
                 setInvestedStocks(data);
                 setInvestedLoading(false);
             })
             .catch(err => {
                 console.error("Failed to fetch invested stocks", err);
                 setInvestedLoading(false);
             });
      }
  }, [activeTab]);

  // Update Available Sub-Sectors when Sector Changes
  useEffect(() => {
    if (sector === 'All') {
      const allSubs = new Set<string>();
      Object.values(filters.sectors).forEach(subs => subs.forEach(s => allSubs.add(s)));
      setAvailableSubSectors(Array.from(allSubs).sort());
    } else {
      setAvailableSubSectors(filters.sectors[sector] || []);
    }
    setSubSector('All');
  }, [sector, filters]);

  // React Query for Infinite Scroll (Candidates)
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: isCandidatesLoading,
    isError,
  } = useInfiniteQuery<ApiResponse>({
    queryKey: ['stocks', debouncedSearch, sector, subSector, filterType],
    queryFn: async ({ pageParam = 1 }) => {
      const params = new URLSearchParams({
        page: String(pageParam),
        limit: '20',
      });

      if (debouncedSearch) params.append('search', debouncedSearch);
      if (sector !== 'All') params.append('sector', sector);
      if (subSector !== 'All') params.append('sub_sector', subSector);
      if (filterType !== 'All') params.append('filter_type', filterType);

      const res = await fetch(`/api/analytics/score?${params.toString()}`);
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    },
    getNextPageParam: (lastPage) => (lastPage.has_more ? lastPage.page + 1 : undefined),
    initialPageParam: 1,
  });

  const stocksToShow = activeTab === 'Candidates'
      ? (data ? data.pages.flatMap((page) => page.data) : [])
      : investedStocks;

  const isLoading = activeTab === 'Candidates' ? isCandidatesLoading : investedLoading;

  const COLUMNS = 3;
  const rowCount = Math.ceil(stocksToShow.length / COLUMNS);

  const virtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 210,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  useEffect(() => {
    if (activeTab !== 'Candidates') return;
    const [lastItem] = [...virtualItems].reverse();
    if (!lastItem) return;

    if (
      lastItem.index >= rowCount - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage();
    }
  }, [activeTab, hasNextPage, fetchNextPage, isFetchingNextPage, rowCount, virtualItems]);

  const sectorsList = Object.keys(filters.sectors).sort();

  return (
    <div className="flex h-[calc(100vh-140px)] flex-col gap-4">
      <h1 className="sr-only">Stock screener</h1>
      {/* Title and filter surface */}
      <div className="card space-y-3 p-4">
        {/* Tab Switcher */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--color-rule)] pb-3">
          <div className="seg" role="tablist" aria-label="Stock universe">
            {(['Candidates', 'Invested'] as const).map(tab => (
              <button
                key={tab}
                role="tab"
                aria-selected={activeTab === tab}
                onClick={() => setActiveTab(tab)}
                className={`seg-item ${activeTab === tab ? 'is-active' : ''}`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="text-[length:var(--text-xs)] font-medium text-[var(--color-muted)]">
            {activeTab === 'Candidates' && (
              <span>Matching universe: <b className="tabular-nums text-[var(--color-ink)]">{data?.pages[0]?.total || 0}</b> symbols</span>
            )}
            {activeTab === 'Invested' && (
              <span>Invested portfolio: <b className="tabular-nums text-[var(--color-ink)]">{investedStocks.length}</b> symbols</span>
            )}
          </div>
        </div>

        {/* Filter Controls */}
        {activeTab === 'Candidates' && (
          <div className="flex flex-col items-center justify-between gap-3 pt-1 md:flex-row">
            <div className="flex w-full flex-1 flex-wrap items-center gap-2.5">
              <div className="relative min-w-[200px] max-w-sm flex-1">
                <Search size={15} aria-hidden="true" className="pointer-events-none absolute left-3 top-3 text-[var(--color-muted)]" />
                <input
                  type="text"
                  placeholder="Search symbol (for example RELIANCE)"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="field field-search"
                  aria-label="Search stock symbol"
                />
              </div>

              <select
                value={sector}
                onChange={e => setSector(e.target.value)}
                className="field field-auto"
                aria-label="Sector"
              >
                <option value="All">All sectors</option>
                {sectorsList.map(sec => (
                  <option key={sec} value={sec}>{sec}</option>
                ))}
              </select>

              <select
                value={subSector}
                onChange={e => setSubSector(e.target.value)}
                className="field field-auto"
                aria-label="Sub-sector"
              >
                <option value="All">All sub-sectors</option>
                {availableSubSectors.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>

            {/* Score Category Filter */}
            <div className="seg shrink-0" role="group" aria-label="Score category">
              {(['All', 'Core', 'Accelerator', 'GEM'] as const).map(type => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  aria-pressed={filterType === type}
                  className={`seg-item ${filterType === type ? 'is-active' : ''}`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Grid Content Area */}
      {isLoading ? (
        <div className="empty-state flex-1 rounded-[var(--radius-card)] border border-[var(--color-rule)] bg-[var(--color-surface)]">
          <p className="state-title">Loading {activeTab} stocks</p>
          <p className="text-[length:var(--text-sm)]">Reading the latest scores from the analytics service.</p>
        </div>
      ) : isError ? (
        <div className="card border-[color-mix(in_oklab,var(--color-danger)_40%,var(--color-edge))] p-8 text-center">
          <p className="state-title text-[var(--color-danger-text)]">Stock data unavailable</p>
          <p className="page-sub mx-auto">Verify the Python analytics backend is running, then reload this screen.</p>
        </div>
      ) : stocksToShow.length === 0 ? (
        <div className="empty-state flex-1 rounded-[var(--radius-card)] border border-[var(--color-rule)] bg-[var(--color-surface)]">
          <p className="state-title">No stocks matched</p>
          <p className="max-w-[46ch] text-[length:var(--text-sm)]">Try broadening the search or clearing the sector filters.</p>
        </div>
      ) : (
        /* Virtualized Grid */
        <div
          ref={parentRef}
          className="custom-scrollbar flex-1 overflow-y-auto pr-1"
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {virtualItems.map((virtualRow) => {
              const startIndex = virtualRow.index * COLUMNS;
              const rowStocks = stocksToShow.slice(startIndex, startIndex + COLUMNS);

              return (
                <div
                  key={virtualRow.key}
                  className="absolute left-0 top-0 grid w-full grid-cols-1 gap-4 md:grid-cols-3"
                  style={{
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  {rowStocks.map((stock) => (
                    <div key={stock.symbol} className="h-full">
                      <StockCard stock={stock} />
                    </div>
                  ))}
                </div>
              );
            })}
          </div>

          {/* Pagination status */}
          {activeTab === 'Candidates' && isFetchingNextPage && (
            <div className="flex items-center justify-center gap-2 py-4 text-[length:var(--text-xs)] text-[var(--color-muted)]">
              <ChevronRight size={13} aria-hidden="true" className="animate-pulse" />
              Loading more stocks
            </div>
          )}
        </div>
      )}
    </div>
  );
}
