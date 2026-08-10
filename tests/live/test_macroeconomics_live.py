"""Real Federal Reserve Economic Data (FRED) API tests for MacroeconomicsService."""

from openmarkets.schemas.macroeconomics import (
    EmploymentSummary,
    FinancialStressSummary,
    GDPSummary,
    InflationExpectationsSummary,
    InflationSummary,
    InterestRatesSummary,
    LiquiditySummary,
    MacroeconomicSeries,
    PCESummary,
)
from openmarkets.services.macroeconomics import MacroeconomicsService
from tests.live.conftest import tolerate_network_errors


def test_get_cpi_inflation_live():
    with tolerate_network_errors("FRED CPI"):
        svc = MacroeconomicsService()
        res = svc.get_cpi_inflation(limit=12)

        assert isinstance(res, InflationSummary)
        assert res.headline_cpi_latest > 200.0
        assert res.core_cpi_latest > 200.0
        assert len(res.headline_cpi_history) == 12


def test_get_pce_inflation_live():
    with tolerate_network_errors("FRED PCE"):
        svc = MacroeconomicsService()
        res = svc.get_pce_inflation(limit=12)

        assert isinstance(res, PCESummary)
        assert res.core_pce_latest > 50.0
        assert res.fed_target_percent == 2.0
        assert len(res.history) == 12


def test_get_employment_indicators_live():
    with tolerate_network_errors("FRED Employment"):
        svc = MacroeconomicsService()
        res = svc.get_employment_indicators(limit=12)

        assert isinstance(res, EmploymentSummary)
        assert 1.0 <= res.unemployment_rate_percent <= 25.0
        assert res.nonfarm_payrolls_thousands > 100000.0
        assert len(res.payrolls_history) == 12


def test_get_interest_rates_telemetry_live():
    with tolerate_network_errors("FRED Interest Rates"):
        svc = MacroeconomicsService()
        res = svc.get_interest_rates_telemetry(limit=15)

        assert isinstance(res, InterestRatesSummary)
        assert res.effective_fed_funds_rate >= 0.0
        assert res.sofr_rate >= 0.0
        assert len(res.sofr_history) == 15


def test_get_gdp_growth_live():
    with tolerate_network_errors("FRED GDP"):
        svc = MacroeconomicsService()
        res = svc.get_gdp_growth(limit=8)

        assert isinstance(res, GDPSummary)
        assert res.real_gdp_billions > 15000.0
        assert res.nominal_gdp_billions > 15000.0
        assert len(res.real_gdp_history) == 8


def test_get_money_supply_and_fed_balance_sheet_live():
    with tolerate_network_errors("FRED Liquidity"):
        svc = MacroeconomicsService()
        res = svc.get_money_supply_and_fed_balance_sheet(limit=12)

        assert isinstance(res, LiquiditySummary)
        assert res.m2_money_supply_billions > 10000.0
        assert res.fed_total_assets_millions > 1000000.0
        assert len(res.m2_history) == 12


def test_get_inflation_expectations_live():
    with tolerate_network_errors("FRED Inflation Expectations"):
        svc = MacroeconomicsService()
        res = svc.get_inflation_expectations(limit=15)

        assert isinstance(res, InflationExpectationsSummary)
        assert res.breakeven_5y_percent > 0.0
        assert res.breakeven_10y_percent > 0.0
        assert len(res.history_10y) == 15


def test_get_financial_stress_and_credit_spreads_live():
    with tolerate_network_errors("FRED Financial Stress"):
        svc = MacroeconomicsService()
        res = svc.get_financial_stress_and_credit_spreads(limit=15)

        assert isinstance(res, FinancialStressSummary)
        assert isinstance(res.financial_stress_index, float)
        assert res.high_yield_oas_percent > 0.0
        assert len(res.oas_history) == 15


def test_get_macroeconomic_series_live():
    with tolerate_network_errors("FRED Universal Series"):
        svc = MacroeconomicsService()
        res = svc.get_macroeconomic_series("MORTGAGE30US", limit=10)

        assert isinstance(res, MacroeconomicSeries)
        assert res.series_id == "MORTGAGE30US"
        assert len(res.data_points) == 10
        assert res.latest_value > 0.0
