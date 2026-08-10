"""Unit tests for MacroeconomicsService."""

from unittest.mock import Mock

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


def test_macroeconomics_service_delegation():
    repo_mock = Mock()

    mock_cpi = InflationSummary(
        headline_cpi_latest=330.0,
        headline_cpi_date="2026-06-01",
        core_cpi_latest=335.0,
        core_cpi_date="2026-06-01",
    )
    mock_pce = PCESummary(core_pce_latest=130.0, core_pce_date="2026-06-01")
    mock_emp = EmploymentSummary(
        unemployment_rate_percent=4.1,
        unemployment_date="2026-07-01",
        nonfarm_payrolls_thousands=158000.0,
        nonfarm_payrolls_date="2026-07-01",
    )
    mock_rates = InterestRatesSummary(
        effective_fed_funds_rate=3.63,
        fed_funds_date="2026-08-05",
        sofr_rate=3.65,
        sofr_date="2026-08-05",
    )
    mock_gdp = GDPSummary(
        real_gdp_billions=24000.0,
        real_gdp_date="2026-04-01",
        nominal_gdp_billions=32000.0,
        nominal_gdp_date="2026-04-01",
    )
    mock_liq = LiquiditySummary(
        m2_money_supply_billions=23000.0,
        m2_date="2026-06-01",
        fed_total_assets_millions=6700000.0,
        fed_assets_date="2026-08-05",
    )
    mock_exp = InflationExpectationsSummary(
        breakeven_5y_percent=2.22,
        breakeven_5y_date="2026-08-07",
        breakeven_10y_percent=2.25,
        breakeven_10y_date="2026-08-07",
    )
    mock_stress = FinancialStressSummary(
        financial_stress_index=-0.5,
        stress_index_date="2026-07-31",
        stress_level_interpretation="Low stress",
        high_yield_oas_percent=2.7,
        high_yield_oas_date="2026-08-06",
    )
    mock_series = MacroeconomicSeries(
        series_id="CPIAUCSL",
        title="CPI",
        units="Index",
        frequency="Monthly",
        latest_date="2026-06-01",
        latest_value=330.0,
    )

    repo_mock.get_cpi.return_value = mock_cpi
    repo_mock.get_pce.return_value = mock_pce
    repo_mock.get_employment.return_value = mock_emp
    repo_mock.get_interest_rates.return_value = mock_rates
    repo_mock.get_gdp.return_value = mock_gdp
    repo_mock.get_liquidity.return_value = mock_liq
    repo_mock.get_inflation_expectations.return_value = mock_exp
    repo_mock.get_financial_stress.return_value = mock_stress
    repo_mock.get_series.return_value = mock_series

    svc = MacroeconomicsService(repository=repo_mock)

    assert svc.get_cpi_inflation(limit=24) == mock_cpi
    repo_mock.get_cpi.assert_called_with(limit=24, session=svc.session)

    assert svc.get_pce_inflation(limit=24) == mock_pce
    repo_mock.get_pce.assert_called_with(limit=24, session=svc.session)

    assert svc.get_employment_indicators(limit=24) == mock_emp
    repo_mock.get_employment.assert_called_with(limit=24, session=svc.session)

    assert svc.get_interest_rates_telemetry(limit=30) == mock_rates
    repo_mock.get_interest_rates.assert_called_with(limit=30, session=svc.session)

    assert svc.get_gdp_growth(limit=20) == mock_gdp
    repo_mock.get_gdp.assert_called_with(limit=20, session=svc.session)

    assert svc.get_money_supply_and_fed_balance_sheet(limit=24) == mock_liq
    repo_mock.get_liquidity.assert_called_with(limit=24, session=svc.session)

    assert svc.get_inflation_expectations(limit=30) == mock_exp
    repo_mock.get_inflation_expectations.assert_called_with(limit=30, session=svc.session)

    assert svc.get_financial_stress_and_credit_spreads(limit=30) == mock_stress
    repo_mock.get_financial_stress.assert_called_with(limit=30, session=svc.session)

    assert svc.get_macroeconomic_series("CPIAUCSL", limit=50) == mock_series
    repo_mock.get_series.assert_called_with(series_id="CPIAUCSL", limit=50, session=svc.session)
