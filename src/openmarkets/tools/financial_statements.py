"""Financial statements tools."""

import inspect
import json
import sys

import yfinance as yf
from mcp.server import FastMCP


async def get_income_statement(ticker: str, quarterly: bool = False) -> str:
    """Get income statement data.

    Args:
        ticker: Stock ticker symbol
        quarterly: If True, get quarterly data; if False, get annual data

    Returns:
        JSON string containing income statement data
    """
    stock = yf.Ticker(ticker)
    if quarterly:
        financials = stock.quarterly_income_stmt
    else:
        financials = stock.income_stmt

    if financials is not None and not financials.empty:
        return financials.to_json(date_format="iso")
    return json.dumps({"error": "No income statement data available"})


async def get_balance_sheet(ticker: str, quarterly: bool = False) -> str:
    """Get balance sheet data.

    Args:
        ticker: Stock ticker symbol
        quarterly: If True, get quarterly data; if False, get annual data

    Returns:
        JSON string containing balance sheet data
    """
    stock = yf.Ticker(ticker)
    if quarterly:
        balance_sheet = stock.quarterly_balance_sheet
    else:
        balance_sheet = stock.balance_sheet

    if balance_sheet is not None and not balance_sheet.empty:
        return balance_sheet.to_json(date_format="iso")
    return json.dumps({"error": "No balance sheet data available"})


async def get_cash_flow(ticker: str, quarterly: bool = False) -> str:
    """Get cash flow statement data.

    Args:
        ticker: Stock ticker symbol
        quarterly: If True, get quarterly data; if False, get annual data

    Returns:
        JSON string containing cash flow data
    """
    stock = yf.Ticker(ticker)
    if quarterly:
        cashflow = stock.quarterly_cashflow
    else:
        cashflow = stock.cashflow

    if cashflow is not None and not cashflow.empty:
        return cashflow.to_json(date_format="iso")
    return json.dumps({"error": "No cash flow data available"})


async def get_financials_summary(ticker: str) -> str:
    """Get key financial metrics summary.

    Args:
        ticker: Stock ticker symbol

    Returns:
        JSON string containing financial summary
    """
    stock = yf.Ticker(ticker)

    if not stock.info:
        info = stock.info
    else:
        info = stock.info

    financial_summary = {
        "totalRevenue": info.get("totalRevenue"),
        "revenueGrowth": info.get("revenueGrowth"),
        "grossProfits": info.get("grossProfits"),
        "grossMargins": info.get("grossMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "profitMargins": info.get("profitMargins"),
        "operatingCashflow": info.get("operatingCashflow"),
        "freeCashflow": info.get("freeCashflow"),
        "totalCash": info.get("totalCash"),
        "totalDebt": info.get("totalDebt"),
        "totalCashPerShare": info.get("totalCashPerShare"),
        "earningsGrowth": info.get("earningsGrowth"),
        "currentRatio": info.get("currentRatio"),
        "quickRatio": info.get("quickRatio"),
        "returnOnAssets": info.get("returnOnAssets"),
        "returnOnEquity": info.get("returnOnEquity"),
        "debtToEquity": info.get("debtToEquity"),
    }

    return json.dumps(financial_summary, indent=2)


def register(mcp: FastMCP):
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "register":
            continue
        mcp.tool()(func)
