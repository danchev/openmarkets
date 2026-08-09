"""Options repository.

Provides access to option chains, contracts, and analytics using yfinance.
"""

from datetime import date
from typing import Protocol

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError
from openmarkets.schemas.options import (
    CallOption,
    OptionContractChain,
    OptionExpirationDate,
    OptionsByMoneyness,
    OptionsSkew,
    OptionsVolumeAnalysis,
    OptionUnderlying,
    PriceRange,
    PutOption,
    SkewPoint,
)


class OptionsRepository(Protocol):
    """Structural type for options data access.

    See ``StockRepository`` in ``repositories.stock`` for why a Protocol is
    used here rather than the ``IOptionsRepository`` ABC that was removed.
    """

    def get_option_expiration_dates(
        self, ticker: str, session: Session | None = None
    ) -> list[OptionExpirationDate]: ...

    def get_option_chain(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> OptionContractChain: ...

    def get_call_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[CallOption] | None: ...

    def get_put_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[PutOption] | None: ...

    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> OptionsVolumeAnalysis: ...

    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> OptionsByMoneyness: ...

    def get_options_skew(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> OptionsSkew: ...


class YFinanceOptionsRepository:
    """YFinance-based implementation of options repository."""

    def get_option_expiration_dates(self, ticker: str, session: Session | None = None) -> list[OptionExpirationDate]:
        """Retrieve all available option expiration dates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of option expiration dates.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        options = ticker_obj.options
        return [OptionExpirationDate(date=dt) for dt in options]

    def get_option_chain(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> OptionContractChain:
        """Retrieve the full option contract chain for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration: Option expiration date. Uses nearest if None.
            session: Optional HTTP session for request handling.

        Returns:
            Option contract chain containing calls and puts.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        expiration_str = str(expiration) if expiration else None
        option_chain = ticker_obj.option_chain(date=expiration_str)
        calls = option_chain.calls
        puts = option_chain.puts

        call_objs = None
        if not calls.empty:
            call_objs = [CallOption(**row) for row in calls.to_dict(orient="records")]

        put_objs = None
        if not puts.empty:
            put_objs = [PutOption(**row) for row in puts.to_dict(orient="records")]

        underlying = OptionUnderlying(**getattr(option_chain, "underlying", {}))
        return OptionContractChain(calls=call_objs, puts=put_objs, underlying=underlying)

    def get_call_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[CallOption] | None:
        """Retrieve all call options for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration: Option expiration date. Uses nearest if None.
            session: Optional HTTP session for request handling.

        Returns:
            List of call options or None if unavailable.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        expiration_str = str(expiration) if expiration else None
        option_chain = ticker_obj.option_chain(expiration_str)
        calls = option_chain.calls
        if calls.empty:
            return None
        return [CallOption(**row) for row in calls.to_dict(orient="records")]

    def get_put_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[PutOption] | None:
        """Retrieve all put options for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration: Option expiration date. Uses nearest if None.
            session: Optional HTTP session for request handling.

        Returns:
            List of put options or None if unavailable.
        """
        ticker_obj = yf.Ticker(ticker, session=session)
        expiration_str = str(expiration) if expiration else None
        option_chain = ticker_obj.option_chain(expiration_str)
        puts = option_chain.puts
        if puts.empty:
            return None
        return [PutOption(**row) for row in puts.to_dict(orient="records")]

    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> OptionsVolumeAnalysis:
        """Analyze option volumes and open interest for a ticker and expiration date.

        Returns total call/put volume, open interest, and put/call ratios.
        """
        stock = yf.Ticker(ticker, session=session)
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)
        if option_chain is None:
            raise DataUnavailableError(f"No options data available for {ticker}.")
        calls = option_chain.calls
        puts = option_chain.puts
        return OptionsVolumeAnalysis(
            total_call_volume=self._get_column_sum(calls, "volume"),
            total_put_volume=self._get_column_sum(puts, "volume"),
            total_call_open_interest=self._get_column_sum(calls, "openInterest"),
            total_put_open_interest=self._get_column_sum(puts, "openInterest"),
            put_call_ratio_volume=self._safe_ratio(
                self._get_column_sum(puts, "volume"),
                self._get_column_sum(calls, "volume"),
            ),
            put_call_ratio_oi=self._safe_ratio(
                self._get_column_sum(puts, "openInterest"),
                self._get_column_sum(calls, "openInterest"),
            ),
        )

    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> OptionsByMoneyness:
        """Get options filtered by moneyness for a ticker and expiration date."""
        stock = yf.Ticker(ticker, session=session)
        current_price = stock.info.get("currentPrice")
        if not current_price:
            raise DataUnavailableError(f"Could not get current stock price for {ticker}.")
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)
        if option_chain is None:
            raise DataUnavailableError(f"No options data available for {ticker}.")
        price_min = current_price * (1 - moneyness_range)
        price_max = current_price * (1 + moneyness_range)
        calls = option_chain.calls
        puts = option_chain.puts
        filtered_calls = calls[(calls["strike"] >= price_min) & (calls["strike"] <= price_max)]
        filtered_puts = puts[(puts["strike"] >= price_min) & (puts["strike"] <= price_max)]
        return OptionsByMoneyness(
            current_price=current_price,
            price_range=PriceRange(min=price_min, max=price_max),
            calls=filtered_calls.to_dict("records"),
            puts=filtered_puts.to_dict("records"),
        )

    def get_options_skew(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> OptionsSkew:
        """Get options skew (implied volatility by strike) for a ticker and expiration date."""
        stock = yf.Ticker(ticker, session=session)
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)

        if option_chain is None or (option_chain.calls.empty and option_chain.puts.empty):
            raise DataUnavailableError(f"No options data available for {ticker} on {expiration_date}.")

        call_skew = self._extract_skew(option_chain.calls)
        put_skew = self._extract_skew(option_chain.puts)

        if call_skew is None and put_skew is None:
            raise DataUnavailableError(f"Missing 'strike' or 'impliedVolatility' in options data for {ticker}.")

        # Report a malformed side without discarding the side that is usable.
        unavailable = [side for side, skew in (("calls", call_skew), ("puts", put_skew)) if skew is None]
        warning = (
            f"Missing 'strike' or 'impliedVolatility' in {' and '.join(unavailable)} options data."
            if unavailable
            else None
        )
        return OptionsSkew(
            call_skew=[SkewPoint(**point) for point in (call_skew or [])],
            put_skew=[SkewPoint(**point) for point in (put_skew or [])],
            warning=warning,
        )

    def _extract_skew(self, contracts) -> list[dict] | None:
        """Extract skew (implied volatility by strike) from an option side.

        Args:
            contracts: DataFrame of either call or put contracts.

        Returns:
            A list of strike/impliedVolatility records, an empty list when
            there are no contracts, or None when the required columns are
            absent.
        """
        if contracts.empty:
            return []
        if "strike" not in contracts.columns or "impliedVolatility" not in contracts.columns:
            return None
        return contracts[["strike", "impliedVolatility"]].to_dict("records")

    def _get_option_chain_for_expiration(self, stock, expiration_date: str | None):
        """Helper to get option chain for a given expiration date or first available."""
        if expiration_date:
            try:
                return stock.option_chain(expiration_date)
            except Exception:
                return None
        expirations = getattr(stock, "options", None)
        if not expirations:
            return None
        try:
            return stock.option_chain(expirations[0])
        except Exception:
            return None

    def _safe_ratio(self, numerator: float, denominator: float) -> float | None:
        """Safely compute ratio, returning None if denominator is zero."""
        if denominator == 0:
            return None
        return numerator / denominator

    def _get_column_sum(self, dataframe, column_name: str) -> float:
        """Get sum of column if it exists, otherwise return 0."""
        if column_name not in dataframe.columns:
            return 0
        return dataframe[column_name].sum()
