"""Real Yahoo Finance API tests for FinancialsService.

This service had zero coverage at the service layer before this file.
"""

from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    EPSHistoryEntry,
    FinancialCalendar,
    FullFinancials,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)
from openmarkets.services.financials import FinancialsService
from tests.live.conftest import STABLE_TICKER, tolerate_network_errors


def test_get_balance_sheet_against_real_api():
    result = FinancialsService().get_balance_sheet(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, BalanceSheetEntry) for entry in result)


def test_get_income_statement_against_real_api():
    result = FinancialsService().get_income_statement(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, IncomeStatementEntry) for entry in result)


def test_get_ttm_income_statement_against_real_api():
    result = FinancialsService().get_ttm_income_statement(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, TTMIncomeStatementEntry) for entry in result)


def test_get_ttm_cash_flow_statement_against_real_api():
    result = FinancialsService().get_ttm_cash_flow_statement(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, TTMCashFlowStatementEntry) for entry in result)


def test_get_financial_calendar_against_real_api():
    """Exercises the actual .get_calendar() -> FinancialCalendar(**data) path
    flagged in an earlier session as a theoretical None-unpacking risk;
    confirms it constructs cleanly against a live, real ticker."""
    result = FinancialsService().get_financial_calendar(STABLE_TICKER)

    assert isinstance(result, FinancialCalendar)


def test_get_sec_filings_against_real_api():
    result = FinancialsService().get_sec_filings(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, SecFilingRecord) for entry in result)


def test_get_eps_history_against_real_api():
    """get_earnings_dates() has been observed timing out from this
    environment independent of this project's code - reproduced calling
    yfinance directly with no session, our repository, or our service
    involved. tolerate_network_errors turns that into a skip, not a
    failure, so it isn't mistaken for a regression."""
    with tolerate_network_errors("get_earnings_dates"):
        result = FinancialsService().get_eps_history(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, EPSHistoryEntry) for entry in result)


def test_get_full_financials_against_real_api():
    """Exercises the concurrent gather() fan-out across 7 real endpoints."""
    with tolerate_network_errors("get_full_financials (includes get_earnings_dates)"):
        result = FinancialsService().get_full_financials(STABLE_TICKER)

    assert isinstance(result, FullFinancials)
    assert isinstance(result.balance_sheet, list)
    assert isinstance(result.financial_calendar, FinancialCalendar)
