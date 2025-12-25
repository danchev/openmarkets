from types import SimpleNamespace

import numpy as np
import pandas as pd

from openmarkets.repositories.funds import YFinanceFundsRepository
from openmarkets.schemas.funds import FundAssetClassHolding, FundSectorWeighting


class _RowLike:
    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return self._data


class _FakeDF:
    def __init__(self, rows):
        self._rows = rows

    def reset_index(self):
        return self

    def transpose(self):
        return self

    def iterrows(self):
        for i, row in enumerate(self._rows):
            yield i, row


def test_get_fund_info(monkeypatch):
    repo = YFinanceFundsRepository()

    info = {"symbol": "FND", "yield": 1.23}
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker", lambda ticker, session=None: SimpleNamespace(info=info)
    )

    res = repo.get_fund_info("FND")
    assert res.symbol == "FND"
    assert res.yield_ == 1.23


def test_get_fund_sector_weighting_variants(monkeypatch):
    repo = YFinanceFundsRepository()

    # None
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: None),
    )
    assert repo.get_fund_sector_weighting("F") is None

    # missing attribute
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: SimpleNamespace()),
    )
    assert repo.get_fund_sector_weighting("F") is None

    # present
    sect = {"technology": 0.5, "financial_services": 0.25}
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: SimpleNamespace(sector_weightings=sect)),
    )

    res = repo.get_fund_sector_weighting("F")
    assert isinstance(res, FundSectorWeighting)
    assert res.technology == 0.5


def test_normalize_fund_operations_handles_numpy_and_series_and_to_dict(monkeypatch):
    repo = YFinanceFundsRepository()

    ops = {
        "index": pd.Series(["X"]),
        "Annual Report Expense Ratio": np.float64(0.123),
        "Annual Holdings Turnover": np.int64(5),
        "Total Net Assets": pd.Series([100]),
    }

    normalized = repo._normalize_fund_operations(ops)
    assert normalized["index"] == "X"
    assert isinstance(normalized["Annual Report Expense Ratio"], list) or isinstance(
        normalized["Annual Report Expense Ratio"], float
    )
    assert normalized["Annual Holdings Turnover"] == 5
    assert normalized["Total Net Assets"] == 100
    # also test that passing an object with to_dict works
    obj = SimpleNamespace(to_dict=lambda: ops)
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: SimpleNamespace(fund_operations=obj)),
    )

    out = repo.get_fund_operations("F")
    assert out is not None
    assert hasattr(out, "index")


def test_get_fund_overview_and_asset_classes_and_top_holdings_and_bond_equity_holdings(monkeypatch):
    repo = YFinanceFundsRepository()

    # None funds data
    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: None),
    )
    assert repo.get_fund_overview("F") is None
    assert repo.get_fund_top_holdings("F") == []
    assert repo.get_fund_bond_holdings("F") == []
    assert repo.get_fund_equity_holdings("F") == []
    assert repo.get_fund_asset_class_holdings("F") is None

    # provide data
    top_row = _RowLike({"Symbol": "A", "Name": "Alpha", "Holding Percent": 0.1})
    bond_row = _RowLike({"index": "B", "Duration": 1.2, "Maturity": 5.0, "Credit Quality": 7})
    equity_row = _RowLike({"index": "E", "Price/Earnings": 10.0})

    df_top = _FakeDF([top_row])
    df_bond = _FakeDF([bond_row])
    df_equity = _FakeDF([equity_row])

    fund_data = SimpleNamespace(
        fund_overview={"categoryName": "cat"},
        top_holdings=df_top,
        bond_holdings=df_bond,
        equity_holdings=df_equity,
        asset_classes={"cashPosition": 1.0, "stockPosition": 2.0},
    )

    monkeypatch.setattr(
        "openmarkets.repositories.funds.yf.Ticker",
        lambda ticker, session=None: SimpleNamespace(get_funds_data=lambda: fund_data),
    )

    ov = repo.get_fund_overview("F")
    assert ov.categoryName == "cat"

    top = repo.get_fund_top_holdings("F")
    assert len(top) == 1
    assert top[0].Symbol == "A"

    bond = repo.get_fund_bond_holdings("F")
    assert len(bond) == 1
    assert bond[0].fund == "B"

    eq = repo.get_fund_equity_holdings("F")
    assert len(eq) == 1
    assert eq[0].fund == "E"

    ac = repo.get_fund_asset_class_holdings("F")
    assert isinstance(ac, FundAssetClassHolding)
    assert ac.cashPosition == 1.0
