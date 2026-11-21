export interface IncomeYTD {
    income: number;
    income_last_year_to_date: number;
    average_income: number;
    active_months: number;
    last_month: string | null;
    change: number;
}

export interface ExpenseYTD {
    expense: number;
    expense_last_year_to_date: number;
    average_expense: number;
    active_months: number;
    last_month: string | null;
    change: number;
    expense_ratio: number;
}

export interface InvestmentYTD {
    investment: number;
    investment_last_year_to_date: number;
    average_investment: number;
    active_months: number;
    last_month: string | null;
    active_sip_count: number;
    change: number;
    investment_ratio: number;
}

export interface Assets {
  Cash: number;
  Stocks: number;
  Mutual_Fund: number;
  Gold: number;
  Silver: number;
  Land: number;
  Crypto: number;
}

export interface InvestmentReturns {
  Stocks: number;
  Mutual_Fund: number;
  Gold: number;
  Silver: number;
  Land: number;
  Crypto: number;
}

export interface DividendYear {
  year: string;
  amount: number;
}

export interface DividendStock {
  name: string;
  amount: number;
}

export interface CashFlowForecast {
  inflow: number;
  outflow: number;
  net_savings: number;
}

export interface Spending {
  category: string;
  amount: number;
}

export interface InvestmentBreakdown {
  name: string;
  total_cost: number;
  current_value: number;
  gain: number;
  xirr: number;
}

export interface DashboardData {
  cash_balance: number;
  emergency_coverage: number;
  emergency_fund_required: number;
  emergency_monthly_average: number;
  total_invested_cost: number;
  income_ytd: IncomeYTD;
  expense_avg: ExpenseYTD;
  investment_avg: InvestmentYTD;
  total_returns: number;
  total_return_pct: number;
  invested_current_value: number;
  investment_breakdown: InvestmentBreakdown[];
  average_roi: number;
  savings_ytd: number;
  savings_rate: number;
  forecast: CashFlowForecast;
  assets: Assets;
  total_assets: number;
  total_liabilities: number;
  liability_breakdown: Array<{ name: string; value: number }>;
  net_worth: number;
  spending_categories: Spending[];
  dividend_yearly: DividendYear[];
  dividend_top_stocks: DividendStock[];
  investment_returns: InvestmentReturns;
}

