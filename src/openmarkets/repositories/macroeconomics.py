"""Repository layer for macroeconomic data and Federal Reserve economic telemetry."""

from datetime import date
from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError, ProviderContractError
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

    @staticmethod
    def _points(raw_points: list[dict], series_id: str) -> list[MacroeconomicPoint]:
        """Validate, de-duplicate, and chronologically order FRED observations."""
        points = [MacroeconomicPoint(date=p["date"], value=p["value"]) for p in raw_points]
        if not points:
            raise DataUnavailableError(f"No observations available for FRED series {series_id}.")
        points.sort(key=lambda point: point.date)
        dates = [point.date for point in points]
        if len(dates) != len(set(dates)):
            raise ProviderContractError(f"FRED series {series_id} contains duplicate observation dates.")
        return points

    @staticmethod
    def _history(points: list[MacroeconomicPoint], limit: int) -> list[MacroeconomicPoint]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        return points[-limit:]

    @staticmethod
    def _year_over_year(points: list[MacroeconomicPoint]) -> float | None:
        """Calculate an exact calendar-year change, never a positional approximation."""
        latest = points[-1]
        latest_date = date.fromisoformat(latest.date)
        try:
            prior_date = latest_date.replace(year=latest_date.year - 1)
        except ValueError:  # February 29 maps to the final day of prior February.
            prior_date = latest_date.replace(year=latest_date.year - 1, day=28)
        prior = next((point for point in points if point.date == prior_date.isoformat()), None)
        if prior is None or prior.value == 0:
            return None
        return round(((latest.value / prior.value) - 1.0) * 100, 2)

    def get_series(self, series_id: str, limit: int = 50, session: Session | None = None) -> MacroeconomicSeries:
        """Fetch timeseries observations for any arbitrary FRED series identifier."""
        norm_id = series_id.strip().upper()
        raw_pts = fetch_fred_timeseries(norm_id, session=session)
        meta = FRED_SERIES_CATALOG.get(
            norm_id,
            {"title": norm_id, "units": "Value", "frequency": "Unknown"},
        )

        pts = self._points(raw_pts, norm_id)
        truncated = self._history(pts, limit)

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

        cpi_pts = self._points(raw_headline, "CPIAUCSL")
        core_pts = self._points(raw_core, "CPILFESL")

        cpi_yoy = self._year_over_year(cpi_pts)
        core_yoy = self._year_over_year(core_pts)

        return InflationSummary(
            headline_cpi_latest=cpi_pts[-1].value,
            headline_cpi_date=cpi_pts[-1].date,
            core_cpi_latest=core_pts[-1].value,
            core_cpi_date=core_pts[-1].date,
            cpi_yoy_percent=cpi_yoy,
            core_cpi_yoy_percent=core_yoy,
            headline_cpi_history=self._history(cpi_pts, limit),
            core_cpi_history=self._history(core_pts, limit),
        )

    def get_pce(self, limit: int = 24, session: Session | None = None) -> PCESummary:
        """Retrieve Core PCE Inflation Price Index (the Fed's primary inflation gauge)."""
        raw_pce = fetch_fred_timeseries("PCEPILFE", session=session)
        pce_pts = self._points(raw_pce, "PCEPILFE")

        pce_yoy = self._year_over_year(pce_pts)

        return PCESummary(
            core_pce_latest=pce_pts[-1].value,
            core_pce_date=pce_pts[-1].date,
            core_pce_yoy_percent=pce_yoy,
            fed_target_percent=2.0,
            history=self._history(pce_pts, limit),
        )

    def get_employment(self, limit: int = 24, session: Session | None = None) -> EmploymentSummary:
        """Retrieve Unemployment Rate and Nonfarm Payrolls labor market telemetry."""
        raw_unrate = fetch_fred_timeseries("UNRATE", session=session)
        raw_payems = fetch_fred_timeseries("PAYEMS", session=session)

        un_pts = self._points(raw_unrate, "UNRATE")
        pay_pts = self._points(raw_payems, "PAYEMS")

        job_growth = None
        if len(pay_pts) >= 2:
            job_growth = round(pay_pts[-1].value - pay_pts[-2].value, 1)

        return EmploymentSummary(
            unemployment_rate_percent=un_pts[-1].value,
            unemployment_date=un_pts[-1].date,
            nonfarm_payrolls_thousands=pay_pts[-1].value,
            nonfarm_payrolls_date=pay_pts[-1].date,
            monthly_job_growth_thousands=job_growth,
            unemployment_history=self._history(un_pts, limit),
            payrolls_history=self._history(pay_pts, limit),
        )

    def get_interest_rates(self, limit: int = 30, session: Session | None = None) -> InterestRatesSummary:
        """Retrieve Effective Federal Funds Rate (EFFR) and SOFR benchmark interest rates."""
        raw_dff = fetch_fred_timeseries("DFF", session=session)
        raw_sofr = fetch_fred_timeseries("SOFR", session=session)

        dff_pts = self._points(raw_dff, "DFF")
        sofr_pts = self._points(raw_sofr, "SOFR")

        return InterestRatesSummary(
            effective_fed_funds_rate=dff_pts[-1].value,
            fed_funds_date=dff_pts[-1].date,
            sofr_rate=sofr_pts[-1].value,
            sofr_date=sofr_pts[-1].date,
            fed_funds_history=self._history(dff_pts, limit),
            sofr_history=self._history(sofr_pts, limit),
        )

    def get_gdp(self, limit: int = 20, session: Session | None = None) -> GDPSummary:
        """Retrieve Real and Nominal Gross Domestic Product (GDP) timeseries."""
        raw_real = fetch_fred_timeseries("GDPC1", session=session)
        raw_nom = fetch_fred_timeseries("GDP", session=session)

        real_pts = self._points(raw_real, "GDPC1")
        nom_pts = self._points(raw_nom, "GDP")

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
            real_gdp_history=self._history(real_pts, limit),
            nominal_gdp_history=self._history(nom_pts, limit),
        )

    def get_liquidity(self, limit: int = 24, session: Session | None = None) -> LiquiditySummary:
        """Retrieve M2 Money Supply and Federal Reserve balance sheet total assets."""
        raw_m2 = fetch_fred_timeseries("M2SL", session=session)
        raw_walcl = fetch_fred_timeseries("WALCL", session=session)

        m2_pts = self._points(raw_m2, "M2SL")
        walcl_pts = self._points(raw_walcl, "WALCL")

        m2_yoy = self._year_over_year(m2_pts)

        return LiquiditySummary(
            m2_money_supply_billions=m2_pts[-1].value,
            m2_date=m2_pts[-1].date,
            m2_yoy_growth_percent=m2_yoy,
            fed_total_assets_millions=walcl_pts[-1].value,
            fed_assets_date=walcl_pts[-1].date,
            m2_history=self._history(m2_pts, limit),
            fed_assets_history=self._history(walcl_pts, limit),
        )

    def get_inflation_expectations(
        self, limit: int = 30, session: Session | None = None
    ) -> InflationExpectationsSummary:
        """Retrieve 5-Year and 10-Year market-implied Breakeven Inflation Rates from TIPS."""
        raw_5y = fetch_fred_timeseries("T5YIE", session=session)
        raw_10y = fetch_fred_timeseries("T10YIE", session=session)

        pts_5y = self._points(raw_5y, "T5YIE")
        pts_10y = self._points(raw_10y, "T10YIE")

        return InflationExpectationsSummary(
            breakeven_5y_percent=pts_5y[-1].value,
            breakeven_5y_date=pts_5y[-1].date,
            breakeven_10y_percent=pts_10y[-1].value,
            breakeven_10y_date=pts_10y[-1].date,
            history_5y=self._history(pts_5y, limit),
            history_10y=self._history(pts_10y, limit),
        )

    def get_financial_stress(self, limit: int = 30, session: Session | None = None) -> FinancialStressSummary:
        """Retrieve St. Louis Fed Financial Stress Index and High-Yield credit spreads."""
        raw_stress = fetch_fred_timeseries("STLFSI4", session=session)
        raw_oas = fetch_fred_timeseries("BAMLH0A0HYM2", session=session)

        stress_pts = self._points(raw_stress, "STLFSI4")
        oas_pts = self._points(raw_oas, "BAMLH0A0HYM2")

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
            stress_history=self._history(stress_pts, limit),
            oas_history=self._history(oas_pts, limit),
        )
