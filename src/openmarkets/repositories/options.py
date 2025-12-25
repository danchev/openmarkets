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
    @abstractmethod
    def get_option_expiration_dates(self, ticker: str, session: Session | None = None) -> list[OptionExpirationDate]:
        pass

    @abstractmethod
    def get_option_chain(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> OptionContractChain:
        pass

    @abstractmethod
    def get_call_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[CallOption] | None:
        pass

    @abstractmethod
    def get_put_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[PutOption] | None:
        pass

    @abstractmethod
    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> dict:
        pass

    @abstractmethod
    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> dict:
        pass

    @abstractmethod
    def get_options_skew(self, ticker: str, expiration_date: str | None = None, session: Session | None = None) -> dict:
        pass


class YFinanceOptionsRepository(IOptionsRepository):
    def get_option_expiration_dates(self, ticker: str, session: Session | None = None) -> list[OptionExpirationDate]:
        options = yf.Ticker(ticker, session=session).options
        return [OptionExpirationDate(date=dt) for dt in options]

    def get_option_chain(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> OptionContractChain:
        option_chain = yf.Ticker(ticker, session=session).option_chain(date=str(expiration) if expiration else None)
        calls = option_chain.calls
        puts = option_chain.puts
        call_objs = [CallOption(**row.to_dict()) for _, row in calls.iterrows()] if not calls.empty else None
        put_objs = [PutOption(**row.to_dict()) for _, row in puts.iterrows()] if not puts.empty else None
        underlying = OptionUnderlying(**getattr(option_chain, "underlying", {}))
        return OptionContractChain(calls=call_objs, puts=put_objs, underlying=underlying)

    def get_call_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[CallOption] | None:
        option_chain = yf.Ticker(ticker, session=session).option_chain(str(expiration) if expiration else None)
        calls = option_chain.calls
        if calls.empty:
            return None
        return [CallOption(**row.to_dict()) for _, row in calls.iterrows()]

    def get_put_options(
        self, ticker: str, expiration: date | None = None, session: Session | None = None
    ) -> list[PutOption] | None:
        option_chain = yf.Ticker(ticker, session=session).option_chain(str(expiration) if expiration else None)
        puts = option_chain.puts
        if puts.empty:
            return None
        return [PutOption(**row.to_dict()) for _, row in puts.iterrows()]

    def get_options_volume_analysis(
        self, ticker: str, expiration_date: str | None = None, session: Session | None = None
    ) -> dict:
        stock = yf.Ticker(ticker, session=session)
        if expiration_date:
            option_chain = stock.option_chain(expiration_date)
        else:
            expirations = stock.options
            if not expirations:
                return {"error": "No options data available"}
            option_chain = stock.option_chain(expirations[0])
        calls = option_chain.calls
        puts = option_chain.puts
        analysis = {
            "total_call_volume": calls["volume"].sum() if "volume" in calls.columns else 0,
            "total_put_volume": puts["volume"].sum() if "volume" in puts.columns else 0,
            "total_call_open_interest": calls["openInterest"].sum() if "openInterest" in calls.columns else 0,
            "total_put_open_interest": puts["openInterest"].sum() if "openInterest" in puts.columns else 0,
            "put_call_ratio_volume": (puts["volume"].sum() / calls["volume"].sum())
            if "volume" in calls.columns and calls["volume"].sum() > 0
            else None,
            "put_call_ratio_oi": (puts["openInterest"].sum() / calls["openInterest"].sum())
            if "openInterest" in calls.columns and calls["openInterest"].sum() > 0
            else None,
        }
        return analysis

    def get_options_by_moneyness(
        self,
        ticker: str,
        expiration_date: str | None = None,
        moneyness_range: float = 0.1,
        session: Session | None = None,
    ) -> dict:
        stock = yf.Ticker(ticker, session=session)
        current_price = stock.info.get("currentPrice")
        if not current_price:
            return {"error": "Could not get current stock price"}
        if expiration_date:
            option_chain = stock.option_chain(expiration_date)
        else:
            expirations = stock.options
            if not expirations:
                return {"error": "No options data available"}
            option_chain = stock.option_chain(expirations[0])
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
        stock = yf.Ticker(ticker, session=session)
        if not expiration_date:
            expirations = stock.options
            if not expirations:
                return {"error": "No options data available for this ticker."}
            expiration_date = expirations[0]
        option_chain = stock.option_chain(expiration_date)
        if not option_chain or (option_chain.calls.empty and option_chain.puts.empty):
            return {"error": f"No options data available for {ticker} on {expiration_date}."}
        call_skew = []
        if not option_chain.calls.empty:
            if "strike" not in option_chain.calls.columns or "impliedVolatility" not in option_chain.calls.columns:
                return {"error": "Missing 'strike' or 'impliedVolatility' in call options data."}
            call_skew = option_chain.calls[["strike", "impliedVolatility"]].to_dict("records")
        put_skew = []
        if not option_chain.puts.empty:
            if "strike" not in option_chain.puts.columns or "impliedVolatility" not in option_chain.puts.columns:
                return {"error": "Missing 'strike' or 'impliedVolatility' in put options data."}
            put_skew = option_chain.puts[["strike", "impliedVolatility"]].to_dict("records")
        result = {
            "call_skew": call_skew,
            "put_skew": put_skew,
        }
        return result
