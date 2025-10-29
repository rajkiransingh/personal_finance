interface Assets {
  Cash: number;
  Stocks: number;
  Mutual_Fund: number;
  Gold: number;
  Silver: number;
  Land: number;
  Crypto: number;
}

interface InvestmentReturns {
  Stocks: number;
  Mutual_Fund: number;
  Gold: number;
  Silver: number;
  Land: number;
  Crypto: number;
}

interface DashboardData {
  emergency_coverage: number;
  total_returns: number;
  average_roi: number;
  earning: Record<string, unknown>;
  spending: Record<string, unknown>;
  investment_returns: InvestmentReturns;
  assets: Assets;
}
