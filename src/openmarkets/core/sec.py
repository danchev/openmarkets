"""SEC EDGAR client layer for direct regulatory filings and XBRL ingestion.

Communicates directly with the US Securities and Exchange Commission (SEC) EDGAR
public REST APIs (data.sec.gov and www.sec.gov) using compliant User-Agent headers
and automatic CIK resolution across 10,000+ public registrants.
"""

from typing import Any

from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError, InvalidSymbolError
from openmarkets.core.http import get_session, retry_with_backoff

DEFAULT_SEC_USER_AGENT = "OpenMarkets/1.0 (contact@openmarkets.ai)"

# In-memory ticker-to-CIK mapping cache
_CIK_CACHE: dict[str, dict[str, Any]] = {}
_CIK_INDEX_LOADED = False


def _get_sec_headers(user_agent: str = DEFAULT_SEC_USER_AGENT) -> dict[str, str]:
    """Return compliant HTTP headers required by SEC EDGAR APIs."""
    return {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
    }


@retry_with_backoff(retries=3, initial_delay=0.5)
def _load_sec_ticker_map(session: Session | None = None) -> dict[str, dict[str, Any]]:
    """Load and cache the complete SEC company tickers and CIK catalog."""
    global _CIK_CACHE, _CIK_INDEX_LOADED
    if _CIK_INDEX_LOADED and _CIK_CACHE:
        return _CIK_CACHE

    s = session if session is not None else get_session()
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = _get_sec_headers()

    resp = s.get(url, headers=headers)
    resp.raise_for_status()
    raw_data = resp.json()

    # Format of company_tickers.json: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
    cache: dict[str, dict[str, Any]] = {}
    for entry in raw_data.values():
        ticker = str(entry.get("ticker", "")).strip().upper()
        cik_int = entry.get("cik_str")
        title = str(entry.get("title", "")).strip()
        if ticker and cik_int is not None:
            cik_10 = str(cik_int).zfill(10)
            cache[ticker] = {
                "cik": cik_10,
                "cik_int": cik_int,
                "ticker": ticker,
                "title": title,
            }
    _CIK_CACHE = cache
    _CIK_INDEX_LOADED = True
    return _CIK_CACHE


def resolve_cik(ticker_or_cik: str, session: Session | None = None) -> tuple[str, str]:
    """Resolve a stock ticker or CIK string into a 10-digit zero-padded CIK and company title.

    Args:
        ticker_or_cik: Stock ticker (e.g. 'AAPL', 'MSFT', 'NVDA') or raw CIK (e.g. '320193', '0000320193').
        session: Optional HTTP session.

    Returns:
        Tuple of (10_digit_cik, company_title).

    Raises:
        InvalidSymbolError: If the ticker/CIK cannot be resolved.
    """
    cleaned = str(ticker_or_cik).strip().upper()

    # If it is purely numeric, pad to 10 digits directly
    if cleaned.isdigit():
        cik_10 = cleaned.zfill(10)
        return cik_10, f"CIK {cik_10}"

    ticker_map = _load_sec_ticker_map(session=session)
    if cleaned in ticker_map:
        info = ticker_map[cleaned]
        return info["cik"], info["title"]

    raise InvalidSymbolError(f"Security identifier '{ticker_or_cik}' could not be resolved to an SEC EDGAR CIK.")


def build_sec_doc_url(cik: str, accession_number: str, primary_document: str) -> str:
    """Construct direct URL to an official SEC EDGAR primary filing document.

    Example:
        https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm
    """
    cik_raw = str(int(cik)) if cik.isdigit() else cik
    acc_no_dashes = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_raw}/{acc_no_dashes}/{primary_document}"


@retry_with_backoff(retries=3, initial_delay=0.5)
def fetch_sec_submissions(cik: str, session: Session | None = None) -> dict[str, Any]:
    """Fetch complete corporate metadata and recent filings from SEC EDGAR submissions API.

    Args:
        cik: 10-digit zero-padded CIK.
        session: Optional HTTP session.

    Returns:
        JSON dictionary of company submissions, SIC, entity metadata, and recent filings.
    """
    s = session if session is not None else get_session()
    cik_10 = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_10}.json"
    headers = _get_sec_headers()

    resp = s.get(url, headers=headers)
    if resp.status_code == 404:
        raise DataUnavailableError(f"No SEC EDGAR submission data found for CIK {cik_10}.")
    resp.raise_for_status()
    return resp.json()


@retry_with_backoff(retries=3, initial_delay=0.5)
def fetch_sec_company_facts(cik: str, session: Session | None = None) -> dict[str, Any]:
    """Fetch structured US-GAAP XBRL disclosures and financial statement facts.

    Args:
        cik: 10-digit zero-padded CIK.
        session: Optional HTTP session.

    Returns:
        JSON dictionary containing all taxonomy concepts, units, and historical tagged values.
    """
    s = session if session is not None else get_session()
    cik_10 = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_10}.json"
    headers = _get_sec_headers()

    resp = s.get(url, headers=headers)
    if resp.status_code == 404:
        raise DataUnavailableError(f"No SEC EDGAR XBRL company facts found for CIK {cik_10}.")
    resp.raise_for_status()
    return resp.json()


@retry_with_backoff(retries=3, initial_delay=0.5)
def fetch_sec_concept(
    cik: str, concept: str, taxonomy: str = "us-gaap", session: Session | None = None
) -> dict[str, Any]:
    """Fetch specific XBRL concept timeseries for an entity.

    Args:
        cik: 10-digit zero-padded CIK.
        concept: US-GAAP concept name (e.g. 'Revenues', 'Assets', 'GrossProfit').
        taxonomy: XBRL taxonomy, defaults to 'us-gaap' (or 'dei').
        session: Optional HTTP session.

    Returns:
        JSON dictionary containing concept details and observation units.
    """
    s = session if session is not None else get_session()
    cik_10 = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik_10}/{taxonomy}/{concept}.json"
    headers = _get_sec_headers()

    resp = s.get(url, headers=headers)
    if resp.status_code == 404:
        raise DataUnavailableError(f"No XBRL concept '{concept}' found for CIK {cik_10} under taxonomy '{taxonomy}'.")
    resp.raise_for_status()
    return resp.json()


def search_sec_entities(query: str, limit: int = 10, session: Session | None = None) -> list[dict[str, Any]]:
    """Search registered SEC companies by ticker or company name.

    Args:
        query: Search term (e.g. 'Apple', 'NVDA', 'Microsoft').
        limit: Maximum results to return.
        session: Optional HTTP session.

    Returns:
        List of matching company dictionary records.
    """
    ticker_map = _load_sec_ticker_map(session=session)
    q = query.strip().upper()

    matches: list[dict[str, Any]] = []

    # Exact ticker match first
    if q in ticker_map:
        matches.append(ticker_map[q])

    # Substring matches in ticker or title
    for ticker, info in ticker_map.items():
        if len(matches) >= limit:
            break
        if info in matches:
            continue
        if q in ticker or q in info["title"].upper():
            matches.append(info)

    return matches[:limit]
