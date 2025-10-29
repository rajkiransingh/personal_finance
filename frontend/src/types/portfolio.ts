export interface SubAllocation {
  current_value: number;
  ideal_value: number;
  gap: number;
  target_pct_of_total: number;
}

export interface Category {
  current_value: number;
  ideal_value: number;
  gap: number;
  current_pct: number;
  target_pct: number;
  status: string;
  sub_allocations: Record<string, SubAllocation>;
}

export interface Summary {
  positive_gap_total: number;
  negative_gap_total: number;
  inflow_sufficient: boolean;
}

export interface RebalancePlan {
  ETFs: number;
  MutualFunds: number;
  Stocks: number;
  Metals: number;
  RealEstate: number;
  Crypto: number;
}

export interface PortfolioResponse {
  total_value: number;
  categories: Record<string, Category>;
  summary: Summary;
  next_monthly_sip: number;
  rebalance_plan: RebalancePlan;
}
