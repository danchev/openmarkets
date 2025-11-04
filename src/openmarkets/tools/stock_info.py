"""Stock information tools."""

import json
from datetime import datetime
from typing import List

import yfinance as yf


async def get_stock_info(ticker: str) -> str:
    """Fetches basic company and price information for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL').

    Returns:
        str: JSON string containing company profile, sector, price, volume, and other key fields. Example keys: symbol, shortName, sector, currentPrice, marketCap, etc.
    """

    def convert_unix_to_date(timestamp):
        """Helper function to convert Unix timestamp to ISO 8601 date."""
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None

    stock = yf.Ticker(ticker)
    info = stock.info
    relevant_info = {
        "symbol": info.get("symbol"),
        "shortName": info.get("shortName"),
        "longName": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "currentPrice": info.get("currentPrice"),
        "previousClose": info.get("previousClose"),
        "open": info.get("open"),
        "dayLow": info.get("dayLow"),
        "dayHigh": info.get("dayHigh"),
        "volume": info.get("volume"),
        "averageVolume": info.get("averageVolume"),
        "beta": info.get("beta"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "dividendYield": info.get("dividendYield"),
        "payoutRatio": info.get("payoutRatio"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
        "priceToBook": info.get("priceToBook"),
        "debtToEquity": info.get("debtToEquity"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        "website": info.get("website"),
        "country": info.get("country"),
        "city": info.get("city"),
        "phone": info.get("phone"),
        "fullTimeEmployees": info.get("fullTimeEmployees"),
        "longBusinessSummary": info.get("longBusinessSummary"),
        "exDividendDate": convert_unix_to_date(info.get("exDividendDate")),
    }
    return json.dumps(relevant_info, indent=2)


async def get_risk_metrics(ticker: str) -> str:
    """Fetches risk metrics for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string with audit, board, compensation, shareholder rights, and overall risk scores. Example keys: auditRisk, boardRisk, overallRisk, etc.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    risk_metrics = {
        "auditRisk": info.get("auditRisk"),
        "boardRisk": info.get("boardRisk"),
        "compensationRisk": info.get("compensationRisk"),
        "shareHolderRightsRisk": info.get("shareHolderRightsRisk"),
        "overallRisk": info.get("overallRisk"),
    }
    return json.dumps(risk_metrics, indent=2)


async def get_dividend_info(ticker: str) -> str:
    """Fetches dividend information for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string with dividend rate, yield, payout ratio, ex-dividend date, and related fields. Example keys: dividendRate, dividendYield, exDividendDate, etc.
    """

    def convert_unix_to_date(timestamp):
        """Helper function to convert Unix timestamp to ISO 8601 date."""
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None

    stock = yf.Ticker(ticker)
    info = stock.info
    dividend_info = {
        "dividendRate": info.get("dividendRate"),
        "dividendYield": info.get("dividendYield"),
        "exDividendDate": convert_unix_to_date(info.get("exDividendDate")),
        "payoutRatio": info.get("payoutRatio"),
        "fiveYearAvgDividendYield": info.get("fiveYearAvgDividendYield"),
        "trailingAnnualDividendRate": info.get("trailingAnnualDividendRate"),
        "trailingAnnualDividendYield": info.get("trailingAnnualDividendYield"),
        "lastDividendValue": info.get("lastDividendValue"),
        "lastDividendDate": convert_unix_to_date(info.get("lastDividendDate")),
    }
    return json.dumps(dividend_info, indent=2)


async def get_price_targets(ticker: str) -> str:
    """Fetches analyst price targets for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string with analyst high, low, mean, and median price targets, plus number of analyst opinions. Example keys: targetHighPrice, targetMeanPrice, numberOfAnalystOpinions, etc.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    price_targets = {
        "targetHighPrice": info.get("targetHighPrice"),
        "targetLowPrice": info.get("targetLowPrice"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "targetMedianPrice": info.get("targetMedianPrice"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
    }
    return json.dumps(price_targets, indent=2)


async def get_analyst_recommendation(ticker: str) -> str:
    """Fetches analyst recommendation and rating for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string with recommendation mean, key, and average analyst rating. Example keys: recommendationMean, recommendationKey, averageAnalystRating.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    recommendation = {
        "recommendationMean": info.get("recommendationMean"),
        "recommendationKey": info.get("recommendationKey"),
        "averageAnalystRating": info.get("averageAnalystRating"),
    }
    return json.dumps(recommendation, indent=2)


async def get_financial_summary(ticker: str) -> str:
    """Fetches key financial summary metrics for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string with market cap, margins, cash flow, revenue, and other financial metrics. Example keys: marketCap, totalRevenue, grossMargins, operatingCashflow, etc.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    summary = {
        "marketCap": info.get("marketCap"),
        "enterpriseValue": info.get("enterpriseValue"),
        "profitMargins": info.get("profitMargins"),
        "floatShares": info.get("floatShares"),
        "sharesOutstanding": info.get("sharesOutstanding"),
        "bookValue": info.get("bookValue"),
        "priceToBook": info.get("priceToBook"),
        "totalCash": info.get("totalCash"),
        "totalDebt": info.get("totalDebt"),
        "totalRevenue": info.get("totalRevenue"),
        "grossProfits": info.get("grossProfits"),
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        "earningsGrowth": info.get("earningsGrowth"),
        "revenueGrowth": info.get("revenueGrowth"),
        "grossMargins": info.get("grossMargins"),
        "ebitdaMargins": info.get("ebitdaMargins"),
        "operatingMargins": info.get("operatingMargins"),
    }
    return json.dumps(summary, indent=2)


async def get_multiple_tickers(tickers: List[str], period: str = "1d") -> str:
    """Fetches current price and volume data for multiple stock tickers over a specified period.

    Args:
        tickers: List of stock ticker symbols (e.g. ['AAPL', 'GOOGL']).
        period: Data period (e.g. '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max').

    Returns:
        str: JSON string containing time series data for all requested tickers. Keys include price, volume, and date-indexed values. Returns error message if no data is available.
    """
    tickers_str = " ".join(tickers)
    data = yf.download(
        tickers_str,
        period=period,
        group_by="ticker",
        auto_adjust=True,
    )
    if data is None or data.empty:
        return json.dumps({"error": "No data available for the given tickers"})
    return data.to_json(date_format="iso")


async def get_company_officers(ticker: str) -> str:
    """Fetches company officers and key personnel information.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string containing a list of officer dictionaries, each with name, title, and other details. Returns empty list if unavailable.
    """
    stock = yf.Ticker(ticker)
    officers = stock.get_info().get("companyOfficers", [])
    return json.dumps(officers, indent=2)


async def get_institutional_holders(ticker: str) -> str:
    """Fetches institutional holders information for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string containing institutional holders data as a table (JSON), or error message if unavailable.
    """
    stock = yf.Ticker(ticker)
    holders = stock.institutional_holders
    if holders is not None:
        return holders.to_json(date_format="iso")
    return json.dumps({"error": "No institutional holders data available"})


async def get_major_holders(ticker: str) -> str:
    """Fetches major holders breakdown for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string containing major holders breakdown as a table (JSON), or error message if unavailable.
    """
    stock = yf.Ticker(ticker)
    holders = stock.major_holders
    if holders is not None:
        return holders.to_json()
    return json.dumps({"error": "No major holders data available"})


async def get_mutualfund_holders(ticker: str) -> str:
    """Fetches mutual fund holders information for a company.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        str: JSON string containing mutual fund holders data as a table (JSON), or error message if unavailable.
    """
    stock = yf.Ticker(ticker)
    holders = stock.mutualfund_holders
    if holders is not None:
        return holders.to_json(date_format="iso")
    return json.dumps({"error": "No mutual fund holders data available"})
