interface IncomeYTD {
    income: number
    income_last_year_to_date: number
    change: number
}

interface ExpenseYTD {
    expense: number
    average_expense: number
    change: number
}

interface InvestmentYTD {
    investment: number
    investment_last_year_to_date: number
    change: number
}

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
  income_ytd: IncomeYTD,
  expense_avg: ExpenseYTD,
  investment_avg: InvestmentYTD,
  total_returns: number;
  average_roi: number;
  earning: Record<string, unknown>;
  spending: Record<string, unknown>;
  investment_returns: InvestmentReturns;
  assets: Assets;
}
