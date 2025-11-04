from _typeshed import Incomplete

from . import utils as utils
from .data import YfData as YfData

class Search:
    session: Incomplete
    query: Incomplete
    max_results: Incomplete
    enable_fuzzy_query: Incomplete
    news_count: Incomplete
    timeout: Incomplete
    raise_errors: Incomplete
    lists_count: Incomplete
    include_cb: Incomplete
    nav_links: Incomplete
    enable_research: Incomplete
    enable_cultural_assets: Incomplete
    recommended: Incomplete
    def __init__(
        self,
        query,
        max_results: int = 8,
        news_count: int = 8,
        lists_count: int = 8,
        include_cb: bool = True,
        include_nav_links: bool = False,
        include_research: bool = False,
        include_cultural_assets: bool = False,
        enable_fuzzy_query: bool = False,
        recommended: int = 8,
        session: Incomplete | None = None,
        proxy=...,
        timeout: int = 30,
        raise_errors: bool = True,
    ) -> None: ...
    def search(self) -> Search: ...
    @property
    def quotes(self) -> list: ...
    @property
    def news(self) -> list: ...
    @property
    def lists(self) -> list: ...
    @property
    def research(self) -> list: ...
    @property
    def nav(self) -> list: ...
    @property
    def all(self) -> dict[str, list]: ...
    @property
    def response(self) -> dict: ...
