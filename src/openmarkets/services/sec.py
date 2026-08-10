"""Service layer for SEC EDGAR regulatory filings and XBRL financial disclosures."""

from typing import Annotated

from curl_cffi.requests import Session

from openmarkets.core.cache import cached
from openmarkets.core.http import get_session
from openmarkets.repositories.sec import SECEDGARRepository, SECRepository
from openmarkets.schemas.sec import (
    SECCIKLookupResult,
    SECCompanyProfile,
    SECFilingItem,
    SECXBRLCompanyFactsSummary,
    SECXBRLConceptTimeseries,
)
from openmarkets.services.utils import ToolRegistrationMixin, tool


class SECService(ToolRegistrationMixin):
    """Service layer for SEC EDGAR corporate filings and XBRL disclosures.

    Provides direct access to official US Securities and Exchange Commission (SEC)
    filings (10-K, 10-Q, 8-K, Form 4) and interactive structured XBRL financial statements.
    """

    def __init__(
        self,
        repository: SECRepository | None = None,
        session: Session | None = None,
    ) -> None:
        """Initialize SECService.

        Args:
            repository: Repository instance for data access. Defaults to SECEDGARRepository.
            session: HTTP session for requests.
        """
        self.repository: SECRepository = repository or SECEDGARRepository()
        self._session = session

    @property
    def session(self) -> Session:
        """Return the HTTP session to use for requests."""
        return self._session if self._session is not None else get_session()

    @tool
    @cached(ttl=600.0)
    def get_sec_company_profile(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'MSFT') or CIK string"],
    ) -> SECCompanyProfile:
        """Retrieve official SEC corporate registrant profile and metadata.

        Includes 10-digit CIK, Standard Industrial Classification (SIC) code, business/mailing address,
        fiscal year end, and state of incorporation directly from SEC EDGAR.

        Args:
            ticker: Stock ticker symbol or CIK.

        Returns:
            SECCompanyProfile with regulatory corporate metadata.
        """
        return self.repository.get_company_profile(ticker=ticker, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_sec_recent_filings(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA')"],
        form_type: Annotated[
            str | None, "Optional Form type filter (e.g. '10-K', '10-Q', '8-K', '4', '13F-HR', '144')"
        ] = None,
        limit: Annotated[int, "Max number of filings to return"] = 20,
    ) -> list[SECFilingItem]:
        """Retrieve recent regulatory filings submitted to the SEC by a company.

        Provides direct SEC EDGAR document URLs, acceptance dates, accession numbers, and XBRL flags.

        Args:
            ticker: Stock ticker symbol.
            form_type: Optional filter by SEC Form (e.g. '10-K', '10-Q', '8-K', '4').
            limit: Maximum number of filing records to return.

        Returns:
            List of SECFilingItem objects with direct HTTPS document URLs.
        """
        return self.repository.get_recent_filings(ticker=ticker, form_type=form_type, limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_sec_10k_annual_filings(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'AMZN', 'GOOGL')"],
        limit: Annotated[int, "Number of 10-K annual report filings to retrieve"] = 5,
    ) -> list[SECFilingItem]:
        """Retrieve annual Form 10-K regulatory filings with direct document links.

        Annual reports filed with the SEC containing audited balance sheets, income statements,
        MD&A discussion, and comprehensive risk factor disclosures.

        Args:
            ticker: Stock ticker symbol.
            limit: Number of annual 10-K filings to retrieve.

        Returns:
            List of Form 10-K filing items with direct SEC document URLs.
        """
        return self.repository.get_10k_annual_filings(ticker=ticker, limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_sec_10q_quarterly_filings(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'META')"],
        limit: Annotated[int, "Number of 10-Q quarterly report filings to retrieve"] = 8,
    ) -> list[SECFilingItem]:
        """Retrieve quarterly Form 10-Q regulatory filings with direct document links.

        Quarterly reports filed with the SEC containing unaudited financial statements
        and ongoing quarterly operations review.

        Args:
            ticker: Stock ticker symbol.
            limit: Number of quarterly 10-Q filings to retrieve.

        Returns:
            List of Form 10-Q filing items with direct SEC document URLs.
        """
        return self.repository.get_10q_quarterly_filings(ticker=ticker, limit=limit, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_sec_8k_material_events(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA')"],
        limit: Annotated[int, "Number of 8-K material event filings to retrieve"] = 10,
    ) -> list[SECFilingItem]:
        """Retrieve Form 8-K unscheduled material corporate event announcements.

        Covers major corporate events including quarterly earnings press releases, executive appointments/departures,
        M&A transactions, debt financings, and material agreements.

        Args:
            ticker: Stock ticker symbol.
            limit: Number of Form 8-K filings to retrieve.

        Returns:
            List of Form 8-K material event filings with direct SEC document URLs.
        """
        return self.repository.get_8k_material_events(ticker=ticker, limit=limit, session=self.session)

    @tool
    @cached(ttl=300.0)
    def get_sec_insider_form4_filings(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'MSFT')"],
        limit: Annotated[int, "Number of Form 4 insider filings to retrieve"] = 15,
    ) -> list[SECFilingItem]:
        """Retrieve Form 4 insider ownership changes and transaction filings.

        Filed by corporate officers, directors, and 10%+ beneficial owners reporting open-market
        stock purchases, sales, option exercises, and restricted stock grants.

        Args:
            ticker: Stock ticker symbol.
            limit: Number of Form 4 filings to retrieve.

        Returns:
            List of Form 4 insider filings with direct SEC document URLs.
        """
        return self.repository.get_insider_form4_filings(ticker=ticker, limit=limit, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_sec_xbrl_company_facts(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'NVDA', 'MSFT')"],
    ) -> SECXBRLCompanyFactsSummary:
        """Retrieve catalog summary of all interactive US-GAAP XBRL financial disclosure concepts for an entity.

        Provides a count and sample of available standard US-GAAP accounting tags filed in the registrant's XBRL facts.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            SECXBRLCompanyFactsSummary with taxonomy metrics overview.
        """
        return self.repository.get_xbrl_facts_summary(ticker=ticker, session=self.session)

    @tool
    @cached(ttl=600.0)
    def get_sec_xbrl_concept_timeseries(
        self,
        ticker: Annotated[str, "Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA')"],
        concept: Annotated[
            str,
            "US-GAAP XBRL concept or standard alias: 'REVENUES', 'NET_INCOME', 'GROSS_PROFIT', 'OPERATING_INCOME', 'ASSETS', 'LIABILITIES', 'STOCKHOLDERS_EQUITY', 'CASH', 'EPS', or exact tag name (e.g. 'Revenues', 'Assets')",
        ] = "REVENUES",
        limit: Annotated[int, "Number of historical periods to retrieve"] = 20,
    ) -> SECXBRLConceptTimeseries:
        """Retrieve historical timeseries for a specific US-GAAP XBRL accounting concept directly from SEC filings.

        Extracts exact financial values, units, fiscal years, and fiscal periods filed in official 10-K and 10-Q reports.

        Args:
            ticker: Stock ticker symbol.
            concept: US-GAAP tag or alias ('REVENUES', 'NET_INCOME', 'GROSS_PROFIT', 'ASSETS', 'CASH', 'EPS').
            limit: Maximum historical observation periods to return.

        Returns:
            SECXBRLConceptTimeseries with historical reported values.
        """
        return self.repository.get_xbrl_concept_timeseries(
            ticker=ticker, concept=concept, limit=limit, session=self.session
        )

    @tool
    @cached(ttl=3600.0)
    def get_sec_cik_lookup(
        self,
        query: Annotated[
            str, "Company name or ticker symbol to search in SEC EDGAR directory (e.g. 'Apple', 'NVIDIA', 'Berkshire')"
        ],
        limit: Annotated[int, "Maximum number of search results to return"] = 10,
    ) -> list[SECCIKLookupResult]:
        """Search the official SEC registered company directory by ticker or company name.

        Resolves ticker symbols and company titles to their official 10-digit Central Index Key (CIK).

        Args:
            query: Ticker or company title search string.
            limit: Maximum number of matches to return.

        Returns:
            List of SECCIKLookupResult matches.
        """
        return self.repository.search_cik(query=query, limit=limit, session=self.session)


sec_service = SECService()
