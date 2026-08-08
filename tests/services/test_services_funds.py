"""Tests for FundsService.

Verifies that the service layer correctly delegates to the repository
for all fund data methods.
"""

import pytest

from openmarkets.repositories.funds import IFundsRepository
from openmarkets.schemas.funds import (
    FundAssetClassHolding,
    FundBondHolding,
    FundEquityHolding,
    FundInfo,
    FundOperations,
    FundOverview,
    FundSectorWeighting,
    FundTopHolding,
)
from openmarkets.services.funds import FundsService


class FundsRepositorySpy(IFundsRepository):
    """Spy implementation of IFundsRepository for testing."""

    def __init__(self):
        self.calls = {}

    def _record(self, method_name, *args, **kwargs):
        """Record a method call."""
        self.calls[method_name] = self.calls.get(method_name, 0) + 1

    def get_fund_info(self, ticker, session=None):
        self._record("get_fund_info", ticker)
        return FundInfo(
            **{
                "longBusinessSummary": "Test Fund",
                "maxAge": 1,
                "previousClose": 100.0,
                "open": 100.5,
                "dayLow": 99.5,
                "dayHigh": 101.5,
                "regularMarketPreviousClose": 100.0,
                "regularMarketOpen": 100.5,
                "regularMarketDayLow": 99.5,
                "regularMarketDayHigh": 101.5,
                "dividendRate": 2.0,
                "dividendYield": 0.02,
                "payoutRatio": 0.5,
                "fiveYearAvgDividendYield": 2.0,
                "beta": 1.0,
                "trailingPE": 15.0,
                "forwardPE": 14.0,
                "volume": 1000000,
                "regularMarketVolume": 1000000,
                "averageVolume": 1000000,
                "averageVolume10days": 1000000,
                "averageDailyVolume10Day": 1000000,
                "bid": 100.0,
                "ask": 100.1,
                "bidSize": 100,
                "askSize": 100,
                "fullExchangeName": "TestExchange",
                "financialCurrency": "USD",
                "regularMarketOpen": 100.5,
                "averageAnnualReturn": None,
                "threeYearAverageReturn": None,
                "fiveYearAverageReturn": None,
                "marketCap": 1000000000,
                "preMarketPremium": None,
                "preMarketPrice": None,
                "preMarketChange": None,
                "preMarketChangePercent": None,
                "preMarketTime": None,
                "postMarketChange": None,
                "postMarketChangePercent": None,
                "postMarketPrice": None,
                "postMarketTime": None,
                "symbol": ticker,
                "shortName": "Test Fund",
                "longName": "Test Fund Long Name",
                "quoteType": "ETF",
                "exchange": "TEST",
                "exchangeTimezoneName": "America/New_York",
                "exchangeTimezoneShortName": "EST",
                "isEsgPopulated": False,
                "messageBoardId": "finmb_TEST",
                "market": "us_market",
                "annualReportExpenseRatio": None,
                "totalAssets": None,
                "yield": None,
                "ytdReturn": None,
                "beta3Year": None,
                "threeYearAverageReturn": None,
                "fiveYearAverageReturn": None,
            }
        )

    def get_fund_sector_weighting(self, ticker, session=None):
        self._record("get_fund_sector_weighting", ticker)
        return FundSectorWeighting(
            **{
                "realestate": 0.05,
                "customer_ciclical": 0.15,
                "basic_materials": 0.10,
                "consumer_defensive": 0.10,
                "utilities": 0.05,
                "energy": 0.05,
                "communication_services": 0.10,
                "financial_services": 0.15,
                "industrials": 0.10,
                "technology": 0.10,
                "healthcare": 0.05,
            }
        )

    def get_fund_operations(self, ticker, session=None):
        self._record("get_fund_operations", ticker)
        return FundOperations(
            **{
                "index": "SP500",
                "Annual Report Expense Ratio": 0.0012,
                "Annual Holdings Turnover": 0.15,
                "Total Net Assets": 1000000000,
            }
        )

    def get_fund_overview(self, ticker, session=None):
        self._record("get_fund_overview", ticker)
        return FundOverview(
            **{
                "categoryName": "Large Blend",
                "family": "Test Family",
                "legalType": "Exchange Traded Fund",
            }
        )

    def get_fund_top_holdings(self, ticker, session=None):
        self._record("get_fund_top_holdings", ticker)
        return [
            FundTopHolding(
                **{
                    "Symbol": "AAPL",
                    "Name": "Apple Inc",
                    "Holding Percent": 0.07,
                }
            ),
            FundTopHolding(
                **{
                    "Symbol": "MSFT",
                    "Name": "Microsoft Corp",
                    "Holding Percent": 0.06,
                }
            ),
        ]

    def get_fund_bond_holdings(self, ticker, session=None):
        self._record("get_fund_bond_holdings", ticker)
        return [
            FundBondHolding(
                **{
                    "index": "BOND1",
                    "Duration": 5.5,
                    "Maturity": 10.0,
                    "Credit Quality": 0.85,
                }
            )
        ]

    def get_fund_equity_holdings(self, ticker, session=None):
        self._record("get_fund_equity_holdings", ticker)
        return [
            FundEquityHolding(
                **{
                    "index": "EQUITY1",
                    "Price/Earnings": 15.0,
                    "Price/Book": 2.5,
                    "Price/Sales": 1.8,
                    "Price/Cashflow": 12.0,
                    "Median Market Cap": 50000000000,
                    "Three Year Earnings Growth": 0.12,
                    "Price/Earnings Ratio Category": None,
                    "Price/Book Ratio Category": None,
                    "Price/Sales Ratio Category": None,
                    "Price/Cashflow Ratio Category": None,
                    "Median Market Cap Category": None,
                    "Three Year Earnings Growth Category": None,
                }
            )
        ]

    def get_fund_asset_class_holdings(self, ticker, session=None):
        self._record("get_fund_asset_class_holdings", ticker)
        return FundAssetClassHolding(
            **{
                "cashPosition": 0.05,
                "stockPosition": 0.80,
                "bondPosition": 0.10,
                "preferredPosition": 0.02,
                "convertiblePosition": 0.01,
                "otherPosition": 0.02,
            }
        )


@pytest.fixture
def spy_repository():
    """Create a spy repository for testing service delegation."""
    return FundsRepositorySpy()


@pytest.fixture
def service(spy_repository):
    """Create FundsService with spy repository."""
    return FundsService(repository=spy_repository)


class TestFundsServiceDelegatesToRepository:
    """Test that all service methods delegate to the repository."""

    def test_get_fund_info(self, service, spy_repository):
        """Test that get_fund_info delegates to repository."""
        result = service.get_fund_info("SPY")
        assert result.long_business_summary == "Test Fund"
        assert spy_repository.calls["get_fund_info"] == 1

    def test_get_fund_sector_weighting(self, service, spy_repository):
        """Test that get_fund_sector_weighting delegates to repository."""
        result = service.get_fund_sector_weighting("SPY")
        assert result is not None
        assert result.technology == 0.10
        assert spy_repository.calls["get_fund_sector_weighting"] == 1

    def test_get_fund_operations(self, service, spy_repository):
        """Test that get_fund_operations delegates to repository."""
        result = service.get_fund_operations("SPY")
        assert result is not None
        assert result.annual_report_expense_ratio == 0.0012
        assert spy_repository.calls["get_fund_operations"] == 1

    def test_get_fund_overview(self, service, spy_repository):
        """Test that get_fund_overview delegates to repository."""
        result = service.get_fund_overview("SPY")
        assert result is not None
        assert result.category_name == "Large Blend"
        assert spy_repository.calls["get_fund_overview"] == 1

    def test_get_fund_top_holdings(self, service, spy_repository):
        """Test that get_fund_top_holdings delegates to repository."""
        result = service.get_fund_top_holdings("SPY")
        assert len(result) == 2
        assert result[0].symbol == "AAPL"
        assert result[0].holding_percent == 0.07
        assert spy_repository.calls["get_fund_top_holdings"] == 1

    def test_get_fund_bond_holdings(self, service, spy_repository):
        """Test that get_fund_bond_holdings delegates to repository."""
        result = service.get_fund_bond_holdings("SPY")
        assert len(result) == 1
        assert result[0].duration == 5.5
        assert spy_repository.calls["get_fund_bond_holdings"] == 1

    def test_get_fund_equity_holdings(self, service, spy_repository):
        """Test that get_fund_equity_holdings delegates to repository."""
        result = service.get_fund_equity_holdings("SPY")
        assert len(result) == 1
        assert result[0].price_to_earnings == 15.0
        assert spy_repository.calls["get_fund_equity_holdings"] == 1

    def test_get_fund_asset_class_holdings(self, service, spy_repository):
        """Test that get_fund_asset_class_holdings delegates to repository."""
        result = service.get_fund_asset_class_holdings("SPY")
        assert result is not None
        assert result.stock_position == 0.80
        assert result.bond_position == 0.10
        assert spy_repository.calls["get_fund_asset_class_holdings"] == 1
