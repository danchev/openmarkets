"""Options repository interfaces and implementations.

Provides access to option chains, contracts, and analytics using yfinance.
"""

from abc import ABC, abstractmethod
from datetime import date

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.options import (
    CallOption,
    OptionContractChain,
    OptionExpirationDate,
    OptionUnderlying,
    PutOption,
)


class IOptionsRepository(ABC):
    """Abstract interface for options data repositories."""

    @abstractmethod
    def get_option_expiration_dates(self, ticker: str, session: Session | None = None) -> list[OptionExpirationDate]:
        """Retrieve all available option expiration dates for a ticker.

        Args:
            ticker: Stock ticker symbol.
            session: Optional HTTP session for request handling.

        Returns:
            List of option expiration dates.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> dict:
        """Analyze option volumes and open interest for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration_date: Option expiration date string. Uses nearest if None.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing volume analysis metrics.
        """
        pass

    @abstractmethod
    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> dict:
        """Retrieve options filtered by moneyness for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration_date: Option expiration date string. Uses nearest if None.
            moneyness_range: Percentage range around current price (default 0.1 = 10%).
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing filtered options by moneyness.
        """
        pass

    @abstractmethod
    def get_options_skew(self, ticker: str, expiration_date: str | None = None, session: Session | None = None) -> dict:
        """Retrieve options skew (implied volatility by strike) for a ticker and expiration date.

        Args:
            ticker: Stock ticker symbol.
            expiration_date: Option expiration date string. Uses nearest if None.
            session: Optional HTTP session for request handling.

        Returns:
            Dictionary containing options skew data.
        """
        pass


class YFinanceOptionsRepository(IOptionsRepository):
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
            call_objs = [CallOption(**row.to_dict()) for _, row in calls.iterrows()]

        put_objs = None
        if not puts.empty:
            put_objs = [PutOption(**row.to_dict()) for _, row in puts.iterrows()]

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
        return [CallOption(**row.to_dict()) for _, row in calls.iterrows()]

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
        return [PutOption(**row.to_dict()) for _, row in puts.iterrows()]

    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> dict:
        """Analyze option volumes and open interest for a ticker and expiration date.

        Returns total call/put volume, open interest, and put/call ratios.
        """
        stock = yf.Ticker(ticker, session=session)
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)
        if option_chain is None:
            return {"error": "No options data available"}
        calls = option_chain.calls
        puts = option_chain.puts
        analysis = {
            "total_call_volume": self._get_column_sum(calls, "volume"),
            "total_put_volume": self._get_column_sum(puts, "volume"),
            "total_call_open_interest": self._get_column_sum(calls, "openInterest"),
            "total_put_open_interest": self._get_column_sum(puts, "openInterest"),
            "put_call_ratio_volume": self._safe_ratio(
                self._get_column_sum(puts, "volume"),
                self._get_column_sum(calls, "volume"),
            ),
            "put_call_ratio_oi": self._safe_ratio(
                self._get_column_sum(puts, "openInterest"),
                self._get_column_sum(calls, "openInterest"),
            ),
        }
        return analysis

    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> dict:
        """Get options filtered by moneyness for a ticker and expiration date."""
        stock = yf.Ticker(ticker, session=session)
        current_price = stock.info.get("currentPrice")
        if not current_price:
            return {"error": "Could not get current stock price"}
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)
        if option_chain is None:
            return {"error": "No options data available"}
        price_min = current_price * (1 - moneyness_range)
        price_max = current_price * (1 + moneyness_range)
        calls = option_chain.calls
        puts = option_chain.puts
        filtered_calls = calls[(calls["strike"] >= price_min) & (calls["strike"] <= price_max)]
        filtered_puts = puts[(puts["strike"] >= price_min) & (puts["strike"] <= price_max)]
        result = {
            "current_price": current_price,
            "price_range": {"min": price_min, "max": price_max},
            "calls": filtered_calls.to_dict("records"),
            "puts": filtered_puts.to_dict("records"),
        }
        return result

    def get_options_skew(self, ticker: str, expiration_date: str | None = None, session: Session | None = None) -> dict:
        """Get options skew (implied volatility by strike) for a ticker and expiration date."""
        stock = yf.Ticker(ticker, session=session)
        option_chain = self._get_option_chain_for_expiration(stock, expiration_date)

        if option_chain is None:
            return {"error": f"No options data available for {ticker} on {expiration_date}."}

        if option_chain.calls.empty and option_chain.puts.empty:
            return {"error": f"No options data available for {ticker} on {expiration_date}."}

        call_skew = self._extract_call_skew(option_chain.calls)
        if isinstance(call_skew, dict):
            return call_skew

        put_skew = self._extract_put_skew(option_chain.puts)
        if isinstance(put_skew, dict):
            return put_skew

        return {"call_skew": call_skew, "put_skew": put_skew}

    def _extract_call_skew(self, calls):
        """Extract call options skew data."""
        if calls.empty:
            return []
        if "strike" not in calls.columns:
            return {"error": "Missing 'strike' or 'impliedVolatility' in call options data."}
        if "impliedVolatility" not in calls.columns:
            return {"error": "Missing 'strike' or 'impliedVolatility' in call options data."}
        return calls[["strike", "impliedVolatility"]].to_dict("records")

    def _extract_put_skew(self, puts):
        """Extract put options skew data."""
        if puts.empty:
            return []
        if "strike" not in puts.columns:
            return {"error": "Missing 'strike' or 'impliedVolatility' in put options data."}
        if "impliedVolatility" not in puts.columns:
            return {"error": "Missing 'strike' or 'impliedVolatility' in put options data."}
        return puts[["strike", "impliedVolatility"]].to_dict("records")

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
