"""Screener and search tools for yfinance MCP server."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def screen_stocks_by_criteria(
    min_market_cap: float | None = None,
    max_market_cap: float | None = None,
    min_pe_ratio: float | None = None,
    max_pe_ratio: float | None = None,
    min_dividend_yield: float | None = None,
    sector: str | None = None,
    tickers: list[str] | None = None,
) -> str:
    """Screen stocks based on financial criteria.

    Args:
        min_market_cap: Minimum market cap in dollars
        max_market_cap: Maximum market cap in dollars
        min_pe_ratio: Minimum P/E ratio
        max_pe_ratio: Maximum P/E ratio
        min_dividend_yield: Minimum dividend yield (as decimal, e.g., 0.02 for 2%)
        sector: Filter by sector
        tickers: List of specific tickers to screen (if None, uses popular stocks)

    Returns:
        JSON string containing filtered stocks
    """
    try:
        # If no specific tickers provided, use a list of popular stocks
        if tickers is None:
            tickers = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA",
                "NVDA",
                "META",
                "NFLX",
                "AMD",
                "CRM",
                "ORCL",
                "ADBE",
                "INTC",
                "CSCO",
                "PEP",
                "KO",
                "WMT",
                "DIS",
                "V",
                "MA",
                "JPM",
                "BAC",
                "JNJ",
                "PG",
                "UNH",
                "HD",
                "VZ",
                "T",
                "XOM",
                "CVX",
                "PFE",
                "MRK",
                "ABBV",
                "LLY",
            ]

        screened_stocks = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Apply filters
                market_cap = info.get("marketCap")
                pe_ratio = info.get("trailingPE")
                dividend_yield = info.get("dividendYield")
                stock_sector = info.get("sector")

                # Check market cap filters
                if min_market_cap and (not market_cap or market_cap < min_market_cap):
                    continue
                if max_market_cap and (not market_cap or market_cap > max_market_cap):
                    continue

                # Check P/E ratio filters
                if min_pe_ratio and (not pe_ratio or pe_ratio < min_pe_ratio):
                    continue
                if max_pe_ratio and (not pe_ratio or pe_ratio > max_pe_ratio):
                    continue

                # Check dividend yield filter
                if min_dividend_yield and (not dividend_yield or dividend_yield < min_dividend_yield):
                    continue

                # Check sector filter
                if sector and stock_sector != sector:
                    continue

                # If stock passes all filters, add to results
                screened_stocks.append(
                    {
                        "symbol": ticker,
                        "name": info.get("shortName"),
                        "sector": stock_sector,
                        "marketCap": market_cap,
                        "trailingPE": pe_ratio,
                        "dividendYield": dividend_yield,
                        "currentPrice": info.get("currentPrice"),
                        "beta": info.get("beta"),
                    }
                )

            except Exception:
                # Skip stocks that cause errors
                continue

        return json.dumps(
            {
                "criteria": {
                    "min_market_cap": min_market_cap,
                    "max_market_cap": max_market_cap,
                    "min_pe_ratio": min_pe_ratio,
                    "max_pe_ratio": max_pe_ratio,
                    "min_dividend_yield": min_dividend_yield,
                    "sector": sector,
                },
                "results_count": len(screened_stocks),
                "stocks": screened_stocks,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Failed to screen stocks: {str(e)}"})


async def get_similar_stocks(ticker: str, count: int = 5) -> str:
    """Find stocks similar to the given ticker based on sector and market cap.

    Args:
        ticker: Reference stock ticker symbol
        count: Number of similar stocks to return

    Returns:
        JSON string containing similar stocks
    """
    try:
        reference_stock = yf.Ticker(ticker)
        ref_info = reference_stock.info

        ref_sector = ref_info.get("sector")
        ref_market_cap = ref_info.get("marketCap")

        if not ref_sector:
            return json.dumps({"error": "Could not determine sector for reference stock"})

        # List of stocks to search through
        search_tickers = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "NFLX",
            "AMD",
            "CRM",
            "ORCL",
            "ADBE",
            "INTC",
            "CSCO",
            "PEP",
            "KO",
            "WMT",
            "DIS",
            "V",
            "MA",
            "JPM",
            "BAC",
            "JNJ",
            "PG",
            "UNH",
            "HD",
            "VZ",
            "T",
            "XOM",
            "CVX",
            "PFE",
            "MRK",
            "ABBV",
            "LLY",
            "COST",
            "TMO",
            "ACN",
            "AVGO",
            "TXN",
            "DHR",
            "NEE",
            "NKE",
        ]

        similar_stocks = []

        for search_ticker in search_tickers:
            if search_ticker == ticker:
                continue

            try:
                stock = yf.Ticker(search_ticker)
                info = stock.info

                # Check if same sector
                if info.get("sector") == ref_sector:
                    market_cap = info.get("marketCap")

                    # Calculate market cap similarity (within 50% to 200% of reference)
                    if ref_market_cap and market_cap:
                        ratio = market_cap / ref_market_cap
                        if 0.5 <= ratio <= 2.0:
                            similar_stocks.append(
                                {
                                    "symbol": search_ticker,
                                    "name": info.get("shortName"),
                                    "sector": info.get("sector"),
                                    "marketCap": market_cap,
                                    "marketCapRatio": ratio,
                                    "currentPrice": info.get("currentPrice"),
                                    "trailingPE": info.get("trailingPE"),
                                    "beta": info.get("beta"),
                                }
                            )
                    else:
                        # Include stocks in same sector even if market cap unknown
                        similar_stocks.append(
                            {
                                "symbol": search_ticker,
                                "name": info.get("shortName"),
                                "sector": info.get("sector"),
                                "marketCap": market_cap,
                                "currentPrice": info.get("currentPrice"),
                                "trailingPE": info.get("trailingPE"),
                                "beta": info.get("beta"),
                            }
                        )

            except Exception:
                continue

        # Sort by market cap ratio (closest to 1.0 first)
        if ref_market_cap:
            similar_stocks.sort(key=lambda x: abs((x.get("marketCapRatio", 1.0)) - 1.0))

        # Limit results
        limited_results = similar_stocks[:count]

        return json.dumps(
            {
                "reference_stock": {
                    "symbol": ticker,
                    "name": ref_info.get("shortName"),
                    "sector": ref_sector,
                    "marketCap": ref_market_cap,
                },
                "similar_stocks": limited_results,
                "count": len(limited_results),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Failed to find similar stocks: {str(e)}"})


async def get_top_performers(period: str = "1mo", sector: str | None = None, count: int = 10) -> str:
    """Get top performing stocks over a specified period.

    Args:
        period: Time period for performance calculation (1d, 5d, 1mo, 3mo, 6mo, 1y)
        sector: Filter by specific sector (optional)
        count: Number of top performers to return

    Returns:
        JSON string containing top performing stocks
    """
    try:
        # Sample of stocks to analyze
        tickers = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "NFLX",
            "AMD",
            "CRM",
            "ORCL",
            "ADBE",
            "INTC",
            "CSCO",
            "PEP",
            "KO",
            "WMT",
            "DIS",
            "V",
            "MA",
            "JPM",
            "BAC",
            "JNJ",
            "PG",
            "UNH",
            "HD",
            "VZ",
            "T",
            "XOM",
            "CVX",
            "PFE",
            "MRK",
            "ABBV",
            "LLY",
        ]

        performance_data = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period=period)

                # Apply sector filter if specified
                if sector and info.get("sector") != sector:
                    continue

                if len(hist) >= 2:
                    start_price = hist.iloc[0]["Close"]
                    end_price = hist.iloc[-1]["Close"]
                    performance = ((end_price - start_price) / start_price) * 100

                    performance_data.append(
                        {
                            "symbol": ticker,
                            "name": info.get("shortName"),
                            "sector": info.get("sector"),
                            "performance_percent": performance,
                            "start_price": start_price,
                            "end_price": end_price,
                            "marketCap": info.get("marketCap"),
                            "volume": info.get("volume"),
                        }
                    )

            except Exception:
                continue

        # Sort by performance (best first)
        performance_data.sort(key=lambda x: x["performance_percent"], reverse=True)

        # Limit results
        top_performers = performance_data[:count]

        return json.dumps(
            {
                "period": period,
                "sector_filter": sector,
                "top_performers": top_performers,
                "count": len(top_performers),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Failed to get top performers: {str(e)}"})


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
