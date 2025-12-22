'use client';

import { useState, useRef, useEffect } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useDebounce } from 'use-debounce';

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
  const color =
    value > 0.2 ? 'bg-green-500' : value < -0.2 ? 'bg-red-500' : 'bg-yellow-500';
  return (
    <div className={`px-3 py-1 rounded text-sm font-medium text-white ${color}`}>
      {label}: {value.toFixed(2)}
    </div>
  );
}

function StockCard({ stock }: { stock: StockData }) {
  const [flipped, setFlipped] = useState(false);
  const isSell = stock.recommendation === 'Sell';

  return (
    <div
      className="relative w-full h-48 cursor-pointer perspective mb-4"
      onClick={() => setFlipped(!flipped)}
    >
      <div
        className={`relative w-full h-full transition-transform duration-500 transform-style-preserve-3d ${
          flipped ? 'rotate-y-180' : ''
        }`}
      >
        {/* Front Side */}
        <div className={`absolute inset-0 bg-gray-900 rounded-lg p-4 shadow-lg backface-hidden border ${isSell ? 'border-red-500' : 'border-gray-700 hover:border-blue-500'} transition-colors`}>
          <div className="flex justify-between items-start mb-1">
             <h2 className="text-lg font-semibold">{stock.symbol}</h2>
             {isSell && (
                 <span className="bg-red-600 text-white text-xs px-2 py-0.5 rounded animate-pulse">
                    SELL
                 </span>
             )}
          </div>
          
          <p className="text-sm text-gray-400 mb-3 truncate">
            {stock.sub_sector} [{stock.sector}]
          </p>
          
          {isSell ? (
             <div className="text-red-400 text-sm mt-2 font-medium">
                Reason: {stock.reason || "Underperforming"}
             </div>
          ) : (
             <div className="flex flex-wrap gap-2">
                <ScoreBox label="Core" value={stock.core} />
                <ScoreBox label="Acc" value={stock.accelerators} />
                <ScoreBox label="GEM" value={stock.gem} />
             </div>
          )}
          
          <p className="text-xs text-gray-500 mt-3 absolute bottom-4">Click for fundamentals ↩</p>
        </div>

        {/* Back Side */}
        <div className="absolute inset-0 bg-gray-800 rounded-lg p-4 shadow-lg rotate-y-180 backface-hidden border border-gray-600">
          <h3 className="text-md font-semibold mb-2 text-blue-400">
            Fundamentals
          </h3>
          <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs sm:text-sm">
            <span>MC: {(stock.market_cap / 1000).toFixed(1)}K Cr</span>
            <span>PE: {stock.pe_ratio.toFixed(1)}</span>
            <span>PB: {stock.pb_ratio.toFixed(1)}</span>
            <span>PEG: {stock.peg_ratio.toFixed(1)}</span>
            <span>ROE: {stock.roe.toFixed(1)}%</span>
            <span>ROCE: {stock.roce.toFixed(1)}%</span>
            <span>D/E: {stock.debt_to_equity.toFixed(1)}</span>
            <span>Prom: {stock.promoter_holding.toFixed(1)}%</span>
          </div>
          <p className="text-xs text-gray-500 mt-3 absolute bottom-4">Click to flip ↪</p>
        </div>
      </div>
    </div>
  );
}

// --- Main Page ---

export default function ScreenNDiscover() {
  // State
  const [activeTab, setActiveTab] = useState<'Candidates' | 'Invested'>('Candidates');
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounce(search, 500);
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
        const res = await fetch('http://localhost:8000/analytics/filters');
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
          fetch('http://localhost:8000/analytics/invested_scores')
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

      const res = await fetch(`http://localhost:8000/analytics/score?${params.toString()}`);
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    },
    getNextPageParam: (lastPage) => (lastPage.has_more ? lastPage.page + 1 : undefined),
    initialPageParam: 1,
  });

  // Determine stocks to show based on active tab
  const stocksToShow = activeTab === 'Candidates' 
      ? (data ? data.pages.flatMap((page) => page.data) : [])
      : investedStocks;

  const isLoading = activeTab === 'Candidates' ? isCandidatesLoading : investedLoading;

  // Virtualizer setup
  const COLUMNS = 3;
  const rowCount = Math.ceil(stocksToShow.length / COLUMNS);
  
  const virtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 210,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  // Load more on scroll (only for Candidates)
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
  }, [
    activeTab,
    hasNextPage, 
    fetchNextPage, 
    isFetchingNextPage, 
    rowCount,
    virtualItems
  ]);


  const sectorsList = Object.keys(filters.sectors).sort();

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 text-white p-2">
       {/* Filters & Tabs Header */}
      <div className="flex flex-col gap-4 p-2 bg-gray-900 rounded-lg shadow stvirtualizer.getVirtualItems()icky top-0 z-10">
          
        {/* Tabs */}
        <div className="flex border-b border-gray-700">
            {['Invested', 'Candidates'].map(tab => (
                <button
                    key={tab}
                    onClick={() => setActiveTab(tab as any)}
                    className={`px-6 py-2 font-medium text-sm focus:outline-none transition-colors ${
                        activeTab === tab 
                            ? 'text-blue-500 border-b-2 border-blue-500' 
                            : 'text-gray-400 hover:text-white'
                    }`}
                >
                    {tab}
                </button>
            ))}
        </div>

        {/* Filters (Only show for Candidates or if we want to filter Invested too - sticking to Candidates for now as per infinite scroll logic) */}
        {activeTab === 'Candidates' && (
            <div className="flex flex-col md:flex-row justify-between gap-4">
                <div className="flex flex-wrap gap-2 flex-1">
                <input
                    type="text"
                    placeholder="Search symbol..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="p-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:border-blue-500 w-100 md:w-65"
                />

                <select
                    value={sector}
                    onChange={e => setSector(e.target.value)}
                    className="p-2 rounded bg-gray-800 text-white border border-gray-600 w-full md:w-65"
                >
                    <option value="All">All Sectors</option>
                    {sectorsList.map(sec => (
                    <option key={sec} value={sec}>{sec}</option>
                    ))}
                </select>

                <select
                    value={subSector}
                    onChange={e => setSubSector(e.target.value)}
                    className="p-2 rounded bg-gray-800 text-white border border-gray-600 w-full md:w-65"
                >
                    <option value="All">All Sub-Sectors</option>
                    {availableSubSectors.map(sub => (
                    <option key={sub} value={sub}>{sub}</option>
                    ))}
                </select>
                
                <div className="flex items-center text-sm text-gray-400 px-2">
                    Results: {data?.pages[0]?.total || 0}
                </div>
                </div>

                <div className="flex gap-2 bg-gray-800 p-1 rounded h-fit self-center">
                {['All', 'Core', 'Accelerator', 'GEM'].map(type => (
                    <button
                    key={type}
                    onClick={() => setFilterType(type as any)}
                    className={`px-3 py-1 rounded text-sm font-semibold transition-colors ${
                        filterType === type
                        ? 'bg-blue-600 text-white shadow'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                    >
                    {type}
                    </button>
                ))}
                </div>
            </div>
        )}
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64 text-blue-400 animate-pulse">
           Loading {activeTab}...
        </div>
      ) : isError ? (
        <div className="text-red-500 text-center p-10">Error loading data. Please check backend connection.</div>
      ) : stocksToShow.length === 0 ? (
        <div className="text-gray-400 text-center p-10">No stocks found matching criteria.</div>
      ) : (
        /* Virtual Scroll Container */
        <div
          ref={parentRef}
          className="flex-1 overflow-y-auto pr-2 custom-scrollbar"
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {virtualizer.getVirtualItems().map((virtualRow) => {
              const startIndex = virtualRow.index * COLUMNS;
              const rowStocks = stocksToShow.slice(startIndex, startIndex + COLUMNS);

              return (
                <div
                  key={virtualRow.key}
                  className="absolute top-0 left-0 w-full grid grid-cols-1 md:grid-cols-3 gap-4"
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
          
          {/* Loading More Spinner (Candidates Only) */}
          {activeTab === 'Candidates' && isFetchingNextPage && (
            <div className="text-center py-4 text-gray-500 text-sm animate-pulse">
              Loading more stocks...
            </div>
          )}
        </div>
      )}
    </div>
  );
}
