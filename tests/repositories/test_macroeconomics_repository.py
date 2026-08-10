"""Unit tests for FREDMacroeconomicsRepository."""

from unittest.mock import patch

from openmarkets.repositories.macroeconomics import FREDMacroeconomicsRepository
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


def test_get_series_known_and_unknown():
    repo = FREDMacroeconomicsRepository()
    mock_data = [{"date": "2026-06-01", "value": 332.5}, {"date": "2026-07-01", "value": 333.0}]

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", return_value=mock_data):
        series = repo.get_series("CPIAUCSL", limit=10)
        assert isinstance(series, MacroeconomicSeries)
        assert series.series_id == "CPIAUCSL"
        assert series.title == "Consumer Price Index for All Urban Consumers: All Items"
        assert series.latest_value == 333.0
        assert len(series.data_points) == 2

        # Unknown series fallback
        unknown = repo.get_series("CUSTOM123", limit=10)
        assert unknown.series_id == "CUSTOM123"
        assert unknown.title == "CUSTOM123"


def test_get_cpi():
    repo = FREDMacroeconomicsRepository()
    # 13 points to test YoY calculation
    mock_headline = [{"date": f"2025-{i:02d}-01", "value": 300.0 + i} for i in range(1, 13)]
    mock_headline.append({"date": "2026-01-01", "value": 315.0})  # 315 / 301 - 1 = ~4.65%

    mock_core = [{"date": f"2025-{i:02d}-01", "value": 290.0 + i} for i in range(1, 13)]
    mock_core.append({"date": "2026-01-01", "value": 302.0})

    def mock_fetch(series_id, session=None):
        if series_id == "CPIAUCSL":
            return mock_headline
        return mock_core

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        summary = repo.get_cpi(limit=5)
        assert isinstance(summary, InflationSummary)
        assert summary.headline_cpi_latest == 315.0
        assert summary.core_cpi_latest == 302.0
        assert summary.cpi_yoy_percent == 4.65
        assert len(summary.headline_cpi_history) == 5


def test_get_pce():
    repo = FREDMacroeconomicsRepository()
    mock_pce = [{"date": f"2025-{i:02d}-01", "value": 120.0 + i} for i in range(1, 13)]
    mock_pce.append({"date": "2026-01-01", "value": 135.0})

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", return_value=mock_pce):
        pce = repo.get_pce(limit=6)
        assert isinstance(pce, PCESummary)
        assert pce.core_pce_latest == 135.0
        assert pce.fed_target_percent == 2.0
        assert pce.core_pce_yoy_percent is not None
        assert len(pce.history) == 6


def test_get_employment():
    repo = FREDMacroeconomicsRepository()
    mock_unrate = [{"date": "2026-06-01", "value": 4.0}, {"date": "2026-07-01", "value": 4.1}]
    mock_payems = [{"date": "2026-06-01", "value": 158700.0}, {"date": "2026-07-01", "value": 158850.0}]

    def mock_fetch(series_id, session=None):
        if series_id == "UNRATE":
            return mock_unrate
        return mock_payems

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        emp = repo.get_employment(limit=10)
        assert isinstance(emp, EmploymentSummary)
        assert emp.unemployment_rate_percent == 4.1
        assert emp.nonfarm_payrolls_thousands == 158850.0
        assert emp.monthly_job_growth_thousands == 150.0


def test_get_interest_rates():
    repo = FREDMacroeconomicsRepository()
    mock_dff = [{"date": "2026-08-05", "value": 3.63}]
    mock_sofr = [{"date": "2026-08-05", "value": 3.65}]

    def mock_fetch(series_id, session=None):
        if series_id == "DFF":
            return mock_dff
        return mock_sofr

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        rates = repo.get_interest_rates()
        assert isinstance(rates, InterestRatesSummary)
        assert rates.effective_fed_funds_rate == 3.63
        assert rates.sofr_rate == 3.65


def test_get_gdp():
    repo = FREDMacroeconomicsRepository()
    mock_real = [{"date": "2026-01-01", "value": 24000.0}, {"date": "2026-04-01", "value": 24200.0}]
    mock_nom = [{"date": "2026-01-01", "value": 32000.0}, {"date": "2026-04-01", "value": 32475.0}]

    def mock_fetch(series_id, session=None):
        if series_id == "GDPC1":
            return mock_real
        return mock_nom

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        gdp = repo.get_gdp()
        assert isinstance(gdp, GDPSummary)
        assert gdp.real_gdp_billions == 24200.0
        assert gdp.nominal_gdp_billions == 32475.0
        assert gdp.real_gdp_annualized_growth_percent is not None


def test_get_liquidity():
    repo = FREDMacroeconomicsRepository()
    mock_m2 = [{"date": f"2025-{i:02d}-01", "value": 21000.0 + (i * 100)} for i in range(1, 13)]
    mock_m2.append({"date": "2026-01-01", "value": 23000.0})
    mock_walcl = [{"date": "2026-08-05", "value": 6748000.0}]

    def mock_fetch(series_id, session=None):
        if series_id == "M2SL":
            return mock_m2
        return mock_walcl

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        liq = repo.get_liquidity()
        assert isinstance(liq, LiquiditySummary)
        assert liq.m2_money_supply_billions == 23000.0
        assert liq.fed_total_assets_millions == 6748000.0
        assert liq.m2_yoy_growth_percent is not None


def test_get_inflation_expectations():
    repo = FREDMacroeconomicsRepository()
    mock_5y = [{"date": "2026-08-07", "value": 2.22}]
    mock_10y = [{"date": "2026-08-07", "value": 2.25}]

    def mock_fetch(series_id, session=None):
        if series_id == "T5YIE":
            return mock_5y
        return mock_10y

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        exp = repo.get_inflation_expectations()
        assert isinstance(exp, InflationExpectationsSummary)
        assert exp.breakeven_5y_percent == 2.22
        assert exp.breakeven_10y_percent == 2.25


def test_get_financial_stress():
    repo = FREDMacroeconomicsRepository()
    mock_stress = [{"date": "2026-07-31", "value": -0.52}]
    mock_oas = [{"date": "2026-08-06", "value": 2.71}]

    def mock_fetch(series_id, session=None):
        if series_id == "STLFSI4":
            return mock_stress
        return mock_oas

    with patch("openmarkets.repositories.macroeconomics.fetch_fred_timeseries", side_effect=mock_fetch):
        stress = repo.get_financial_stress()
        assert isinstance(stress, FinancialStressSummary)
        assert stress.financial_stress_index == -0.52
        assert "tranquil" in stress.stress_level_interpretation.lower()
        assert stress.high_yield_oas_percent == 2.71
