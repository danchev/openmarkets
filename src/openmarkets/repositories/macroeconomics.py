"""Repository layer for macroeconomic data and Federal Reserve economic telemetry."""

from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.fred import FRED_SERIES_CATALOG, fetch_fred_timeseries
from openmarkets.schemas.macroeconomics import (
    EmploymentSummary,
    FinancialStressSummary,
    GDPSummary,
    InflationExpectationsSummary,
    InflationSummary,
    InterestRatesSummary,
    LiquiditySummary,
    MacroeconomicPoint,
    MacroeconomicSeries,
    PCESummary,
)


class MacroeconomicsRepository(Protocol):
    """Structural protocol for macroeconomic telemetry data access."""

    def get_series(self, series_id: str, limit: int = 50, session: Session | None = None) -> MacroeconomicSeries: ...

    def get_cpi(self, limit: int = 24, session: Session | None = None) -> InflationSummary: ...

    def get_pce(self, limit: int = 24, session: Session | None = None) -> PCESummary: ...

    def get_employment(self, limit: int = 24, session: Session | None = None) -> EmploymentSummary: ...

    def get_interest_rates(self, limit: int = 30, session: Session | None = None) -> InterestRatesSummary: ...

    def get_gdp(self, limit: int = 20, session: Session | None = None) -> GDPSummary: ...

    def get_liquidity(self, limit: int = 24, session: Session | None = None) -> LiquiditySummary: ...

    def get_inflation_expectations(
        self, limit: int = 30, session: Session | None = None
    ) -> InflationExpectationsSummary: ...

    def get_financial_stress(self, limit: int = 30, session: Session | None = None) -> FinancialStressSummary: ...


class FREDMacroeconomicsRepository:
    """Macroeconomics repository backed by Federal Reserve Economic Data (FRED)."""

    def get_series(self, series_id: str, limit: int = 50, session: Session | None = None) -> MacroeconomicSeries:
        """Fetch timeseries observations for any arbitrary FRED series identifier."""
        norm_id = series_id.strip().upper()
        raw_pts = fetch_fred_timeseries(norm_id, session=session)
        meta = FRED_SERIES_CATALOG.get(
            norm_id,
            {"title": norm_id, "units": "Value", "frequency": "Unknown"},
        )

        pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_pts]
        truncated = pts[-limit:] if limit > 0 else pts

        return MacroeconomicSeries(
            series_id=norm_id,
            title=meta["title"],
            units=meta["units"],
            frequency=meta["frequency"],
            latest_date=pts[-1].date if pts else "",
            latest_value=pts[-1].value if pts else 0.0,
            data_points=truncated,
        )

    def get_cpi(self, limit: int = 24, session: Session | None = None) -> InflationSummary:
        """Retrieve Consumer Price Index (CPI) and Core CPI with YoY calculations."""
        raw_headline = fetch_fred_timeseries("CPIAUCSL", session=session)
        raw_core = fetch_fred_timeseries("CPILFESL", session=session)

        cpi_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_headline]
        core_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_core]

        # Calculate YoY percentage change if 12+ months of data exist
        cpi_yoy = None
        if len(cpi_pts) >= 13:
            cpi_yoy = round(((cpi_pts[-1].value / cpi_pts[-13].value) - 1.0) * 100, 2)

        core_yoy = None
        if len(core_pts) >= 13:
            core_yoy = round(((core_pts[-1].value / core_pts[-13].value) - 1.0) * 100, 2)

        return InflationSummary(
            headline_cpi_latest=cpi_pts[-1].value,
            headline_cpi_date=cpi_pts[-1].date,
            core_cpi_latest=core_pts[-1].value,
            core_cpi_date=core_pts[-1].date,
            cpi_yoy_percent=cpi_yoy,
            core_cpi_yoy_percent=core_yoy,
            headline_cpi_history=cpi_pts[-limit:] if limit > 0 else cpi_pts,
            core_cpi_history=core_pts[-limit:] if limit > 0 else core_pts,
        )

    def get_pce(self, limit: int = 24, session: Session | None = None) -> PCESummary:
        """Retrieve Core PCE Inflation Price Index (the Fed's primary inflation gauge)."""
        raw_pce = fetch_fred_timeseries("PCEPILFE", session=session)
        pce_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_pce]

        pce_yoy = None
        if len(pce_pts) >= 13:
            pce_yoy = round(((pce_pts[-1].value / pce_pts[-13].value) - 1.0) * 100, 2)

        return PCESummary(
            core_pce_latest=pce_pts[-1].value,
            core_pce_date=pce_pts[-1].date,
            core_pce_yoy_percent=pce_yoy,
            fed_target_percent=2.0,
            history=pce_pts[-limit:] if limit > 0 else pce_pts,
        )

    def get_employment(self, limit: int = 24, session: Session | None = None) -> EmploymentSummary:
        """Retrieve Unemployment Rate and Nonfarm Payrolls labor market telemetry."""
        raw_unrate = fetch_fred_timeseries("UNRATE", session=session)
        raw_payems = fetch_fred_timeseries("PAYEMS", session=session)

        un_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_unrate]
        pay_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_payems]

        job_growth = None
        if len(pay_pts) >= 2:
            job_growth = round(pay_pts[-1].value - pay_pts[-2].value, 1)

        return EmploymentSummary(
            unemployment_rate_percent=un_pts[-1].value,
            unemployment_date=un_pts[-1].date,
            nonfarm_payrolls_thousands=pay_pts[-1].value,
            nonfarm_payrolls_date=pay_pts[-1].date,
            monthly_job_growth_thousands=job_growth,
            unemployment_history=un_pts[-limit:] if limit > 0 else un_pts,
            payrolls_history=pay_pts[-limit:] if limit > 0 else pay_pts,
        )

    def get_interest_rates(self, limit: int = 30, session: Session | None = None) -> InterestRatesSummary:
        """Retrieve Effective Federal Funds Rate (EFFR) and SOFR benchmark interest rates."""
        raw_dff = fetch_fred_timeseries("DFF", session=session)
        raw_sofr = fetch_fred_timeseries("SOFR", session=session)

        dff_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_dff]
        sofr_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_sofr]

        return InterestRatesSummary(
            effective_fed_funds_rate=dff_pts[-1].value,
            fed_funds_date=dff_pts[-1].date,
            sofr_rate=sofr_pts[-1].value,
            sofr_date=sofr_pts[-1].date,
            fed_funds_history=dff_pts[-limit:] if limit > 0 else dff_pts,
            sofr_history=sofr_pts[-limit:] if limit > 0 else sofr_pts,
        )

    def get_gdp(self, limit: int = 20, session: Session | None = None) -> GDPSummary:
        """Retrieve Real and Nominal Gross Domestic Product (GDP) timeseries."""
        raw_real = fetch_fred_timeseries("GDPC1", session=session)
        raw_nom = fetch_fred_timeseries("GDP", session=session)

        real_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_real]
        nom_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_nom]

        annualized_growth = None
        if len(real_pts) >= 2:
            # Quarter-over-quarter annualized growth rate: ((Q_t / Q_{t-1})^4 - 1) * 100
            ratio = real_pts[-1].value / real_pts[-2].value
            annualized_growth = round(((ratio**4) - 1.0) * 100, 2)

        return GDPSummary(
            real_gdp_billions=real_pts[-1].value,
            real_gdp_date=real_pts[-1].date,
            nominal_gdp_billions=nom_pts[-1].value,
            nominal_gdp_date=nom_pts[-1].date,
            real_gdp_annualized_growth_percent=annualized_growth,
            real_gdp_history=real_pts[-limit:] if limit > 0 else real_pts,
            nominal_gdp_history=nom_pts[-limit:] if limit > 0 else nom_pts,
        )

    def get_liquidity(self, limit: int = 24, session: Session | None = None) -> LiquiditySummary:
        """Retrieve M2 Money Supply and Federal Reserve balance sheet total assets."""
        raw_m2 = fetch_fred_timeseries("M2SL", session=session)
        raw_walcl = fetch_fred_timeseries("WALCL", session=session)

        m2_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_m2]
        walcl_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_walcl]

        m2_yoy = None
        if len(m2_pts) >= 13:
            m2_yoy = round(((m2_pts[-1].value / m2_pts[-13].value) - 1.0) * 100, 2)

        return LiquiditySummary(
            m2_money_supply_billions=m2_pts[-1].value,
            m2_date=m2_pts[-1].date,
            m2_yoy_growth_percent=m2_yoy,
            fed_total_assets_millions=walcl_pts[-1].value,
            fed_assets_date=walcl_pts[-1].date,
            m2_history=m2_pts[-limit:] if limit > 0 else m2_pts,
            fed_assets_history=walcl_pts[-limit:] if limit > 0 else walcl_pts,
        )

    def get_inflation_expectations(
        self, limit: int = 30, session: Session | None = None
    ) -> InflationExpectationsSummary:
        """Retrieve 5-Year and 10-Year market-implied Breakeven Inflation Rates from TIPS."""
        raw_5y = fetch_fred_timeseries("T5YIE", session=session)
        raw_10y = fetch_fred_timeseries("T10YIE", session=session)

        pts_5y = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_5y]
        pts_10y = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_10y]

        return InflationExpectationsSummary(
            breakeven_5y_percent=pts_5y[-1].value,
            breakeven_5y_date=pts_5y[-1].date,
            breakeven_10y_percent=pts_10y[-1].value,
            breakeven_10y_date=pts_10y[-1].date,
            history_5y=pts_5y[-limit:] if limit > 0 else pts_5y,
            history_10y=pts_10y[-limit:] if limit > 0 else pts_10y,
        )

    def get_financial_stress(self, limit: int = 30, session: Session | None = None) -> FinancialStressSummary:
        """Retrieve St. Louis Fed Financial Stress Index and High-Yield credit spreads."""
        raw_stress = fetch_fred_timeseries("STLFSI4", session=session)
        raw_oas = fetch_fred_timeseries("BAMLH0A0HYM2", session=session)

        stress_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_stress]
        oas_pts = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_oas]

        latest_stress = stress_pts[-1].value
        if latest_stress < -0.5:
            interpretation = "Very low financial market stress (tranquil conditions)"
        elif latest_stress < 0.0:
            interpretation = "Below-average financial market stress"
        elif latest_stress < 1.0:
            interpretation = "Moderate/elevated financial market stress"
        else:
            interpretation = "High financial market distress / crisis conditions"

        return FinancialStressSummary(
            financial_stress_index=latest_stress,
            stress_index_date=stress_pts[-1].date,
            stress_level_interpretation=interpretation,
            high_yield_oas_percent=oas_pts[-1].value,
            high_yield_oas_date=oas_pts[-1].date,
            stress_history=stress_pts[-limit:] if limit > 0 else stress_pts,
            oas_history=oas_pts[-limit:] if limit > 0 else oas_pts,
        )
