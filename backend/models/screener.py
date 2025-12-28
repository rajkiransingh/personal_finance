from typing import Dict, Union

from pydantic import BaseModel, field_validator


class StockData(BaseModel):
    # Basic price and market info
    currentPrice: Union[int, float, str, None]
    website: Union[int, float, str, None]
    industry: Union[int, float, str, None]
    sector: Union[int, float, str, None]
    priceHint: Union[int, float, str, None]
    previousClose: Union[int, float, str, None]
    open: Union[int, float, str, None]
    dayLow: Union[int, float, str, None]
    dayHigh: Union[int, float, str, None]
    regularMarketPreviousClose: Union[int, float, str, None]
    regularMarketOpen: Union[int, float, str, None]
    regularMarketDayLow: Union[int, float, str, None]
    regularMarketDayHigh: Union[int, float, str, None]

    # Dividends
    dividendRate: Union[int, float, str, None] = None
    dividendYield: Union[int, float, str, None]
    exDividendDate: Union[int, float, str, None]
    payoutRatio: Union[int, float, str, None]
    fiveYearAvgDividendYield: Union[int, float, str, None]

    # Valuation and ratios
    beta: Union[int, float, str, None]
    trailingPE: Union[int, float, str, None]
    forwardPE: Union[int, float, str, None]
    volume: Union[int, float, str, None]
    regularMarketVolume: Union[int, float, str, None]
    averageVolume: Union[int, float, str, None]
    averageVolume10days: Union[int, float, str, None]
    averageDailyVolume10Day: Union[int, float, str, None]
    bid: Union[int, float, str, None]
    ask: Union[int, float, str, None]
    bidSize: Union[int, float, str, None]
    askSize: Union[int, float, str, None]
    marketCap: Union[int, float, str, None]
    fiftyTwoWeekLow: Union[int, float, str, None]
    fiftyTwoWeekHigh: Union[int, float, str, None]
    priceToSalesTrailing12Months: Union[int, float, str, None]
    fiftyDayAverage: Union[int, float, str, None]
    twoHundredDayAverage: Union[int, float, str, None]
    trailingAnnualDividendRate: Union[int, float, str, None]
    trailingAnnualDividendYield: Union[int, float, str, None]
    currency: Union[int, float, str, None]
    tradeable: Union[int, float, str, None]
    enterpriseValue: Union[int, float, str, None]
    profitMargins: Union[int, float, str, None]
    floatShares: Union[int, float, str, None]
    sharesOutstanding: Union[int, float, str, None]
    heldPercentInsiders: Union[int, float, str, None]  # Promoter holding
    heldPercentInstitutions: Union[int, float, str, None]
    impliedSharesOutstanding: Union[int, float, str, None]
    bookValue: Union[int, float, str, None]
    priceToBook: Union[int, float, str, None]
    lastFiscalYearEnd: Union[int, float, str, None]
    nextFiscalYearEnd: Union[int, float, str, None]
    mostRecentQuarter: Union[int, float, str, None]
    earningsQuarterlyGrowth: Union[int, float, str, None]
    netIncomeToCommon: Union[int, float, str, None]
    trailingEps: Union[int, float, str, None]
    forwardEps: Union[int, float, str, None]  # Sometimes "N/A"
    lastSplitFactor: Union[int, float, str, None]
    lastSplitDate: Union[int, float, str, None]
    enterpriseToRevenue: Union[int, float, str, None]
    enterpriseToEbitda: Union[int, float, str, None]
    fiftyTwoWeekChange: int | float | str | None = None
    SandP52WeekChange: Union[int, float, str, None]
    lastDividendValue: Union[int, float, str, None]
    lastDividendDate: Union[int, float, str, None]
    quoteType: Union[int, float, str, None]
    recommendationKey: Union[int, float, str, None]
    totalCash: Union[int, float, str, None]
    totalCashPerShare: Union[int, float, str, None]
    ebitda: Union[int, float, str, None]
    totalDebt: Union[int, float, str, None]
    totalRevenue: Union[int, float, str, None]
    debtToEquity: Union[int, float, str, None]
    revenuePerShare: Union[int, float, str, None]
    grossProfits: Union[int, float, str, None]
    earningsGrowth: Union[int, float, str, None]
    revenueGrowth: Union[int, float, str, None]
    grossMargins: Union[int, float, str, None]
    ebitdaMargins: Union[int, float, str, None]
    operatingMargins: Union[int, float, str, None]
    financialCurrency: Union[int, float, str, None]
    symbol: Union[int, float, str, None]
    customPriceAlertConfidence: Union[int, float, str, None]
    shortName: Union[int, float, str, None]
    longName: Union[int, float, str, None]
    regularMarketTime: Union[int, float, str, None]
    marketState: Union[int, float, str, None]
    regularMarketChangePercent: Union[int, float, str, None]
    regularMarketPrice: Union[int, float, str, None]
    exchange: Union[int, float, str, None]
    messageBoardId: Union[int, float, str, None]
    averageDailyVolume3Month: Union[int, float, str, None]
    fiftyTwoWeekLowChange: Union[int, float, str, None]
    fiftyTwoWeekLowChangePercent: Union[int, float, str, None]
    fiftyTwoWeekRange: Union[int, float, str, None]
    fiftyTwoWeekHighChange: Union[int, float, str, None]
    fiftyTwoWeekHighChangePercent: Union[int, float, str, None]
    fiftyTwoWeekChangePercent: Union[int, float, str, None]
    earningsTimestamp: Union[int, float, str, None]
    earningsTimestampStart: Union[int, float, str, None]
    earningsTimestampEnd: Union[int, float, str, None]
    isEarningsDateEstimate: Union[int, float, str, None]
    epsTrailingTwelveMonths: Union[int, float, str, None]
    epsForward: Union[int, float, str, None]
    fiftyDayAverageChange: Union[int, float, str, None]
    fiftyDayAverageChangePercent: Union[int, float, str, None]
    twoHundredDayAverageChange: Union[int, float, str, None]
    twoHundredDayAverageChangePercent: Union[int, float, str, None]
    sourceInterval: Union[int, float, str, None]
    exchangeDataDelayedBy: Union[int, float, str, None]
    cryptoTradeable: Union[int, float, str, None]
    hasPrePostMarketData: Union[int, float, str, None]
    firstTradeDateMilliseconds: Union[int, float, str, None]
    regularMarketChange: Union[int, float, str, None]
    regularMarketDayRange: Union[int, float, str, None]
    fullExchangeName: Union[int, float, str, None]
    trailingPegRatio: Union[int, float, str, None]

    @field_validator(
        "currentPrice",
        "website",
        "industry",
        "sector",
        "priceHint",
        "previousClose",
        "open",
        "dayLow",
        "dayHigh",
        "regularMarketPreviousClose",
        "regularMarketOpen",
        "regularMarketDayLow",
        "regularMarketDayHigh",
        "dividendRate",
        "dividendYield",
        "exDividendDate",
        "payoutRatio",
        "fiveYearAvgDividendYield",
        "beta",
        "trailingPE",
        "forwardPE",
        "volume",
        "regularMarketVolume",
        "averageVolume",
        "averageVolume10days",
        "averageDailyVolume10Day",
        "bid",
        "ask",
        "bidSize",
        "askSize",
        "marketCap",
        "fiftyTwoWeekLow",
        "fiftyTwoWeekHigh",
        "priceToSalesTrailing12Months",
        "fiftyDayAverage",
        "twoHundredDayAverage",
        "trailingAnnualDividendRate",
        "trailingAnnualDividendYield",
        "currency",
        "tradeable",
        "enterpriseValue",
        "profitMargins",
        "floatShares",
        "sharesOutstanding",
        "heldPercentInsiders",
        "heldPercentInstitutions",
        "impliedSharesOutstanding",
        "bookValue",
        "priceToBook",
        "lastFiscalYearEnd",
        "nextFiscalYearEnd",
        "mostRecentQuarter",
        "earningsQuarterlyGrowth",
        "netIncomeToCommon",
        "trailingEps",
        "forwardEps",
        "lastSplitFactor",
        "lastSplitDate",
        "enterpriseToRevenue",
        "enterpriseToEbitda",
        "fiftyTwoWeekChange",
        "SandP52WeekChange",
        "lastDividendValue",
        "lastDividendDate",
        "quoteType",
        "recommendationKey",
        "totalCash",
        "totalCashPerShare",
        "ebitda",
        "totalDebt",
        "totalRevenue",
        "debtToEquity",
        "revenuePerShare",
        "grossProfits",
        "earningsGrowth",
        "revenueGrowth",
        "grossMargins",
        "ebitdaMargins",
        "operatingMargins",
        "financialCurrency",
        "symbol",
        "customPriceAlertConfidence",
        "shortName",
        "longName",
        "regularMarketTime",
        "marketState",
        "regularMarketChangePercent",
        "regularMarketPrice",
        "exchange",
        "messageBoardId",
        "averageDailyVolume3Month",
        "fiftyTwoWeekLowChange",
        "fiftyTwoWeekLowChangePercent",
        "fiftyTwoWeekRange",
        "fiftyTwoWeekHighChange",
        "fiftyTwoWeekHighChangePercent",
        "fiftyTwoWeekChangePercent",
        "earningsTimestamp",
        "earningsTimestampStart",
        "earningsTimestampEnd",
        "isEarningsDateEstimate",
        "epsTrailingTwelveMonths",
        "epsForward",
        "fiftyDayAverageChange",
        "fiftyDayAverageChangePercent",
        "twoHundredDayAverageChange",
        "twoHundredDayAverageChangePercent",
        "sourceInterval",
        "exchangeDataDelayedBy",
        "cryptoTradeable",
        "hasPrePostMarketData",
        "firstTradeDateMilliseconds",
        "regularMarketChange",
        "regularMarketDayRange",
        "fullExchangeName",
        "trailingPegRatio",
        mode="before",
    )
    def clean_ex_dividend_date(cls, v):
        if v == "N/A":
            return None
        return v


class RedisDataResponse(BaseModel):
    stocks: Dict[str, StockData]
