"""Tests for FinancialsService.

Verifies that the service layer correctly delegates to the repository
for all financial data methods.
"""

from datetime import date, datetime

import pytest

from openmarkets.repositories.financials import IFinancialsRepository
from openmarkets.schemas.financials import (
    BalanceSheetEntry,
    EPSHistoryEntry,
    FinancialCalendar,
    IncomeStatementEntry,
    SecFilingRecord,
    TTMCashFlowStatementEntry,
    TTMIncomeStatementEntry,
)
from openmarkets.services.financials import FinancialsService


class FinancialsRepositorySpy(IFinancialsRepository):
    """Spy implementation of IFinancialsRepository for testing."""

    def __init__(self):
        self.calls = {}

    def _record(self, method_name, *args, **kwargs):
        """Record a method call."""
        self.calls[method_name] = self.calls.get(method_name, 0) + 1

    def get_balance_sheet(self, ticker, session=None):
        self._record("get_balance_sheet", ticker)
        return [
            BalanceSheetEntry(
                **{
                    "index": "2023-09-30",
                    "OrdinarySharesNumber": 15000000000,
                    "TotalDebt": 100000000000,
                    "NetDebt": 95000000000,
                }
            )
        ]

    def get_income_statement(self, ticker, session=None):
        self._record("get_income_statement", ticker)
        return [
            IncomeStatementEntry(
                **{
                    "index": "2023-09-30",
                    "TotalRevenue": 383000000000,
                    "CostOfRevenue": 214000000000,
                    "GrossProfit": 169000000000,
                }
            )
        ]

    def get_ttm_income_statement(self, ticker, session=None):
        self._record("get_ttm_income_statement", ticker)
        return [
            TTMIncomeStatementEntry(
                **{
                    "index": datetime(2024, 6, 30),
                    "Total Revenue": 395000000000,
                    "Cost Of Revenue": 220000000000,
                    "Net Income": 97000000000,
                }
            )
        ]

    def get_ttm_cash_flow_statement(self, ticker, session=None):
        self._record("get_ttm_cash_flow_statement", ticker)
        return [
            TTMCashFlowStatementEntry(
                **{
                    "index": datetime(2024, 6, 30),
                    "Free Cash Flow": 100000000000,
                    "Capital Expenditure": -10000000000,
                    "End Cash Position": 120000000000,
                    "Changes In Cash": 5000000000,
                    "Financing Cash Flow": -80000000000,
                }
            )
        ]

    def get_financial_calendar(self, ticker, session=None):
        self._record("get_financial_calendar", ticker)
        return FinancialCalendar(
            **{
                "Dividend Date": date(2024, 2, 15),
                "Ex-Dividend Date": date(2024, 2, 1),
                "Earnings Date": [date(2024, 1, 25)],
                "Earnings High": 2.5,
                "Earnings Low": 2.2,
                "Earnings Average": 2.35,
                "Revenue High": 120000000000,
                "Revenue Low": 115000000000,
                "Revenue Average": 117500000000,
            }
        )

    def get_sec_filings(self, ticker, session=None):
        self._record("get_sec_filings", ticker)
        return [
            SecFilingRecord(
                **{
                    "date": "2024-01-15T10:00:00+00:00",
                    "epochDate": 1705312800,
                    "type": "10-K",
                    "title": "Annual Report",
                    "edgarUrl": "https://www.sec.gov/Archives/edgar/data/12345/000123450040000012/a10-12345_10k.htm",
                    "exhibits": {"3": "Articles of Incorporation"},
                    "maxAge": 1,
                }
            )
        ]

    def get_eps_history(self, ticker, session=None):
        self._record("get_eps_history", ticker)
        return [
            EPSHistoryEntry(
                **{
                    "Earnings Date": datetime(2024, 1, 25, 16, 30, 0),
                    "EPS Estimate": 2.3,
                    "Reported EPS": 2.4,
                    "Surprise(%)": 4.35,
                }
            )
        ]


@pytest.fixture
def spy_repository():
    """Create a spy repository for testing service delegation."""
    return FinancialsRepositorySpy()


@pytest.fixture
def service(spy_repository):
    """Create FinancialsService with spy repository."""
    return FinancialsService(repository=spy_repository)


class TestFinancialsServiceDelegatesToRepository:
    """Test that all service methods delegate to the repository."""

    def test_get_balance_sheet(self, service, spy_repository):
        """Test that get_balance_sheet delegates to repository."""
        result = service.get_balance_sheet("AAPL")
        assert len(result) == 1
        assert result[0].total_debt == 100000000000
        assert spy_repository.calls["get_balance_sheet"] == 1

    def test_get_income_statement(self, service, spy_repository):
        """Test that get_income_statement delegates to repository."""
        result = service.get_income_statement("AAPL")
        assert len(result) == 1
        assert result[0].total_revenue == 383000000000
        assert spy_repository.calls["get_income_statement"] == 1

    def test_get_ttm_income_statement(self, service, spy_repository):
        """Test that get_ttm_income_statement delegates to repository."""
        result = service.get_ttm_income_statement("AAPL")
        assert len(result) == 1
        assert result[0].total_revenue == 395000000000
        assert spy_repository.calls["get_ttm_income_statement"] == 1

    def test_get_ttm_cash_flow_statement(self, service, spy_repository):
        """Test that get_ttm_cash_flow_statement delegates to repository."""
        result = service.get_ttm_cash_flow_statement("AAPL")
        assert len(result) == 1
        assert result[0].free_cash_flow == 100000000000
        assert spy_repository.calls["get_ttm_cash_flow_statement"] == 1

    def test_get_financial_calendar(self, service, spy_repository):
        """Test that get_financial_calendar delegates to repository."""
        result = service.get_financial_calendar("AAPL")
        assert result.dividend_date == date(2024, 2, 15)
        assert result.ex_dividend_date == date(2024, 2, 1)
        assert result.earnings_date == [date(2024, 1, 25)]
        assert result.earnings_average == 2.35
        assert spy_repository.calls["get_financial_calendar"] == 1

    def test_get_sec_filings(self, service, spy_repository):
        """Test that get_sec_filings delegates to repository."""
        result = service.get_sec_filings("AAPL")
        assert len(result) == 1
        assert result[0].type == "10-K"
        assert result[0].title == "Annual Report"
        assert spy_repository.calls["get_sec_filings"] == 1

    def test_get_eps_history(self, service, spy_repository):
        """Test that get_eps_history delegates to repository."""
        result = service.get_eps_history("AAPL")
        assert len(result) == 1
        assert result[0].eps_estimate == 2.3
        assert result[0].reported_eps == 2.4
        assert result[0].surprise_pst == 4.35
        assert spy_repository.calls["get_eps_history"] == 1

    def test_get_full_financials(self, service, spy_repository):
        """Test that get_full_financials aggregates all financial data."""
        result = service.get_full_financials("AAPL")
        assert "balance_sheet" in result
        assert "income_statement" in result
        assert "ttm_income_statement" in result
        assert "ttm_cash_flow_statement" in result
        assert "financial_calendar" in result
        assert "sec_filings" in result
        assert "eps_history" in result
        assert len(result["balance_sheet"]) == 1
        assert len(result["income_statement"]) == 1
        assert len(result["ttm_income_statement"]) == 1
        assert len(result["ttm_cash_flow_statement"]) == 1
        assert len(result["sec_filings"]) == 1
        assert len(result["eps_history"]) == 1

        # Verify all methods were called
        expected_calls = [
            "get_balance_sheet",
            "get_income_statement",
            "get_ttm_income_statement",
            "get_ttm_cash_flow_statement",
            "get_financial_calendar",
            "get_sec_filings",
            "get_eps_history",
        ]
        for call in expected_calls:
            assert spy_repository.calls.get(call) == 1, f"Expected {call} to be called once"
