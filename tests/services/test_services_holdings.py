"""Tests for HoldingsService.

Verifies that the service layer correctly delegates to the repository
for all holdings data methods.
"""

from datetime import datetime

import pytest

from openmarkets.repositories.holdings import IHoldingsRepository
from openmarkets.schemas.holdings import (
    InsiderPurchase,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)
from openmarkets.services.holdings import HoldingsService


class HoldingsRepositorySpy(IHoldingsRepository):
    """Spy implementation of IHoldingsRepository for testing."""

    def __init__(self):
        self.calls = {}

    def _record(self, method_name, *args, **kwargs):
        """Record a method call."""
        self.calls[method_name] = self.calls.get(method_name, 0) + 1

    def get_major_holders(self, ticker, session=None):
        self._record("get_major_holders", ticker)
        return [
            StockMajorHolders(
                **{
                    "insidersPercentHeld": 0.05,
                    "institutionsPercentHeld": 0.65,
                    "institutionsFloatPercentHeld": 0.68,
                    "institutionsCount": 1234,
                }
            )
        ]

    def get_institutional_holdings(self, ticker, session=None):
        self._record("get_institutional_holdings", ticker)
        return [
            StockInstitutionalHoldings(
                **{
                    "Holder": "Vanguard Group Inc",
                    "Shares": 50000000,
                    "Date Report": datetime(2024, 3, 31),
                    "Value": 7500000000,
                    "Percent Out": 0.065,
                }
            ),
            StockInstitutionalHoldings(
                **{
                    "Holder": "BlackRock Inc",
                    "Shares": 40000000,
                    "Date Report": datetime(2024, 3, 31),
                    "Value": 6000000000,
                    "Percent Out": 0.052,
                }
            ),
        ]

    def get_mutual_fund_holdings(self, ticker, session=None):
        self._record("get_mutual_fund_holdings", ticker)
        return [
            StockMutualFundHoldings(
                **{
                    "Holder": "Vanguard Total Stock Market Index Fund",
                    "Shares": 30000000,
                    "Date Report": datetime(2024, 3, 31),
                    "Value": 4500000000,
                    "Percent Out": 0.039,
                }
            )
        ]

    def get_insider_purchases(self, ticker, session=None):
        self._record("get_insider_purchases", ticker)
        return [
            InsiderPurchase(
                **{
                    "Insider Purchases Last 6m": "10.71%",
                    "Shares": 10000,
                    "Trans": 5,
                }
            )
        ]

    def get_insider_roster_holders(self, ticker, session=None):
        self._record("get_insider_roster_holders", ticker)
        return [
            InsiderPurchase(
                **{
                    "Name": "John Doe",
                    "Position": "CEO",
                    "URL": "https://sec.gov/Archives/edgar/data/12345/000123450040000012/xslF345X03/wf-form4_12345678901234.xml",
                }
            )
        ]


@pytest.fixture
def spy_repository():
    """Create a spy repository for testing service delegation."""
    return HoldingsRepositorySpy()


@pytest.fixture
def service(spy_repository):
    """Create HoldingsService with spy repository."""
    return HoldingsService(repository=spy_repository)


class TestHoldingsServiceDelegatesToRepository:
    """Test that all service methods delegate to the repository."""

    def test_get_major_holders(self, service, spy_repository):
        """Test that get_major_holders delegates to repository."""
        result = service.get_major_holders("AAPL")
        assert len(result) == 1
        assert result[0].insiders_percent_held == 0.05
        assert result[0].institutions_count == 1234
        assert spy_repository.calls["get_major_holders"] == 1

    def test_get_institutional_holdings(self, service, spy_repository):
        """Test that get_institutional_holdings delegates to repository."""
        result = service.get_institutional_holdings("AAPL")
        assert len(result) == 2
        assert result[0].holder == "Vanguard Group Inc"
        assert result[0].shares == 50000000
        assert spy_repository.calls["get_institutional_holdings"] == 1

    def test_get_mutual_fund_holdings(self, service, spy_repository):
        """Test that get_mutual_fund_holdings delegates to repository."""
        result = service.get_mutual_fund_holdings("AAPL")
        assert len(result) == 1
        assert result[0].holder == "Vanguard Total Stock Market Index Fund"
        assert result[0].value == 4500000000
        assert spy_repository.calls["get_mutual_fund_holdings"] == 1

    def test_get_insider_purchases(self, service, spy_repository):
        """Test that get_insider_purchases delegates to repository."""
        result = service.get_insider_purchases("AAPL")
        assert len(result) == 1
        assert result[0].shares == 10000
        assert result[0].trans == 5
        assert spy_repository.calls["get_insider_purchases"] == 1

    def test_get_full_holdings(self, service, spy_repository):
        """Test that get_full_holdings aggregates all holdings data."""
        result = service.get_full_holdings("AAPL")
        assert "major_holders" in result
        assert "institutional_holdings" in result
        assert "mutual_fund_holdings" in result
        assert "insider_purchases" in result
        assert len(result["major_holders"]) == 1
        assert len(result["institutional_holdings"]) == 2
        assert len(result["mutual_fund_holdings"]) == 1
        assert len(result["insider_purchases"]) == 1

        # Verify all methods were called
        expected_calls = [
            "get_major_holders",
            "get_institutional_holdings",
            "get_mutual_fund_holdings",
            "get_insider_purchases",
        ]
        for call in expected_calls:
            assert spy_repository.calls.get(call) == 1, f"Expected {call} to be called once"
