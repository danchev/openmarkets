"""Repository layer for SEC EDGAR regulatory filings and XBRL disclosures."""

from typing import Any, Protocol

from curl_cffi.requests import Session

from openmarkets.core.sec import (
    build_sec_doc_url,
    fetch_sec_company_facts,
    fetch_sec_concept,
    fetch_sec_submissions,
    resolve_cik,
    search_sec_entities,
)
from openmarkets.schemas.sec import (
    SECAddress,
    SECCIKLookupResult,
    SECCompanyProfile,
    SECFilingItem,
    SECXBRLCompanyFactsSummary,
    SECXBRLConceptTimeseries,
    SECXBRLFactObservation,
)

# Common GAAP concept aliases to support intuitive financial analysis queries
GAAP_CONCEPT_ALIASES: dict[str, list[str]] = {
    "REVENUES": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "InterestAndDividendIncomeOperating",
    ],
    "NET_INCOME": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "GROSS_PROFIT": [
        "GrossProfit",
    ],
    "OPERATING_INCOME": [
        "OperatingIncomeLoss",
    ],
    "ASSETS": [
        "Assets",
    ],
    "LIABILITIES": [
        "Liabilities",
    ],
    "STOCKHOLDERS_EQUITY": [
        "StockholdersEquity",
        "CommonStockValue",
    ],
    "CASH": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "EPS": [
        "EarningsPerShareDiluted",
        "EarningsPerShareBasic",
    ],
}


class SECRepository(Protocol):
    """Protocol defining the SEC EDGAR repository interface."""

    def get_company_profile(self, ticker: str, session: Session | None = None) -> SECCompanyProfile: ...

    def get_recent_filings(
        self,
        ticker: str,
        form_type: str | None = None,
        limit: int = 20,
        session: Session | None = None,
    ) -> list[SECFilingItem]: ...

    def get_10k_annual_filings(
        self, ticker: str, limit: int = 5, session: Session | None = None
    ) -> list[SECFilingItem]: ...

    def get_10q_quarterly_filings(
        self, ticker: str, limit: int = 8, session: Session | None = None
    ) -> list[SECFilingItem]: ...

    def get_8k_material_events(
        self, ticker: str, limit: int = 10, session: Session | None = None
    ) -> list[SECFilingItem]: ...

    def get_insider_form4_filings(
        self, ticker: str, limit: int = 15, session: Session | None = None
    ) -> list[SECFilingItem]: ...

    def get_xbrl_facts_summary(self, ticker: str, session: Session | None = None) -> SECXBRLCompanyFactsSummary: ...

    def get_xbrl_concept_timeseries(
        self,
        ticker: str,
        concept: str = "Revenues",
        limit: int = 20,
        session: Session | None = None,
    ) -> SECXBRLConceptTimeseries: ...

    def search_cik(self, query: str, limit: int = 10, session: Session | None = None) -> list[SECCIKLookupResult]: ...


class SECEDGARRepository:
    """Concrete repository implementing SEC EDGAR data access."""

    def get_company_profile(self, ticker: str, session: Session | None = None) -> SECCompanyProfile:
        """Fetch official SEC corporate registrant profile."""
        cik, _ = resolve_cik(ticker, session=session)
        sub = fetch_sec_submissions(cik, session=session)

        # Parse addresses
        biz_addr_data = sub.get("addresses", {}).get("business", {})
        biz_addr = (
            SECAddress(
                street1=biz_addr_data.get("street1"),
                street2=biz_addr_data.get("street2"),
                city=biz_addr_data.get("city"),
                state_or_country=biz_addr_data.get("stateOrCountryDescription") or biz_addr_data.get("stateOrCountry"),
                zip_code=biz_addr_data.get("zipCode"),
            )
            if biz_addr_data
            else None
        )

        mail_addr_data = sub.get("addresses", {}).get("mailing", {})
        mail_addr = (
            SECAddress(
                street1=mail_addr_data.get("street1"),
                street2=mail_addr_data.get("street2"),
                city=mail_addr_data.get("city"),
                state_or_country=mail_addr_data.get("stateOrCountryDescription")
                or mail_addr_data.get("stateOrCountry"),
                zip_code=mail_addr_data.get("zipCode"),
            )
            if mail_addr_data
            else None
        )

        return SECCompanyProfile(
            ticker=ticker.upper(),
            cik=cik,
            name=sub.get("name", ticker),
            sic=sub.get("sic"),
            sic_description=sub.get("sicDescription"),
            fiscal_year_end=sub.get("fiscalYearEnd"),
            state_of_incorporation=sub.get("stateOfIncorporationDescription") or sub.get("stateOfIncorporation"),
            business_address=biz_addr,
            mailing_address=mail_addr,
            phone=sub.get("phone"),
            website=sub.get("website"),
            investor_website=sub.get("investorWebsite"),
        )

    def get_recent_filings(
        self,
        ticker: str,
        form_type: str | None = None,
        limit: int = 20,
        session: Session | None = None,
    ) -> list[SECFilingItem]:
        """Fetch recent filings submitted by a company, optionally filtered by Form type."""
        cik, _ = resolve_cik(ticker, session=session)
        sub = fetch_sec_submissions(cik, session=session)
        recent = sub.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        primary_doc_descs = recent.get("primaryDocDescription", [])
        is_xbrl_list = recent.get("isXBRL", [])

        target_form = form_type.strip().upper() if form_type else None

        filings: list[SECFilingItem] = []
        for i in range(len(forms)):
            current_form = str(forms[i]).strip().upper()
            if target_form and current_form != target_form:
                continue

            acc_num = str(accession_numbers[i])
            prim_doc = str(primary_docs[i])
            doc_url = build_sec_doc_url(cik, acc_num, prim_doc)

            is_xb = bool(is_xbrl_list[i]) if i < len(is_xbrl_list) and is_xbrl_list[i] is not None else False
            rep_date = report_dates[i] if i < len(report_dates) and report_dates[i] else None
            doc_desc = primary_doc_descs[i] if i < len(primary_doc_descs) and primary_doc_descs[i] else None

            filings.append(
                SECFilingItem(
                    form=forms[i],
                    filing_date=filing_dates[i],
                    report_date=rep_date,
                    accession_number=acc_num,
                    primary_document=prim_doc,
                    primary_doc_description=doc_desc,
                    is_xbrl=is_xb,
                    document_url=doc_url,
                )
            )
            if len(filings) >= limit:
                break

        return filings

    def get_10k_annual_filings(
        self, ticker: str, limit: int = 5, session: Session | None = None
    ) -> list[SECFilingItem]:
        """Retrieve recent Form 10-K annual report filings."""
        return self.get_recent_filings(ticker=ticker, form_type="10-K", limit=limit, session=session)

    def get_10q_quarterly_filings(
        self, ticker: str, limit: int = 8, session: Session | None = None
    ) -> list[SECFilingItem]:
        """Retrieve recent Form 10-Q quarterly report filings."""
        return self.get_recent_filings(ticker=ticker, form_type="10-Q", limit=limit, session=session)

    def get_8k_material_events(
        self, ticker: str, limit: int = 10, session: Session | None = None
    ) -> list[SECFilingItem]:
        """Retrieve recent Form 8-K current report material events."""
        return self.get_recent_filings(ticker=ticker, form_type="8-K", limit=limit, session=session)

    def get_insider_form4_filings(
        self, ticker: str, limit: int = 15, session: Session | None = None
    ) -> list[SECFilingItem]:
        """Retrieve recent Form 4 insider ownership and transaction filings."""
        return self.get_recent_filings(ticker=ticker, form_type="4", limit=limit, session=session)

    def get_xbrl_facts_summary(self, ticker: str, session: Session | None = None) -> SECXBRLCompanyFactsSummary:
        """Fetch summary of interactive XBRL financial disclosure concepts filed by an entity."""
        cik, _ = resolve_cik(ticker, session=session)
        facts = fetch_sec_company_facts(cik, session=session)

        entity_name = facts.get("entityName", ticker)
        us_gaap = facts.get("facts", {}).get("us-gaap", {})
        concept_names = list(us_gaap.keys())

        # Check which key metrics exist
        key_metrics_found = []
        for alias, concepts in GAAP_CONCEPT_ALIASES.items():
            if any(c in us_gaap for c in concepts):
                key_metrics_found.append(alias)

        return SECXBRLCompanyFactsSummary(
            ticker=ticker.upper(),
            cik=cik,
            entity_name=entity_name,
            available_gaap_concepts_count=len(concept_names),
            available_concepts_sample=concept_names[:10],
            key_metrics_available=key_metrics_found,
        )

    def get_xbrl_concept_timeseries(
        self,
        ticker: str,
        concept: str = "Revenues",
        limit: int = 20,
        session: Session | None = None,
    ) -> SECXBRLConceptTimeseries:
        """Fetch structured historical timeseries for a specific US-GAAP XBRL accounting concept."""
        cik, _ = resolve_cik(ticker, session=session)

        # Check if concept is an alias (e.g. 'REVENUES' or 'NET_INCOME')
        alias_key = concept.strip().upper().replace(" ", "_")
        candidates = GAAP_CONCEPT_ALIASES.get(alias_key, [concept.strip()])

        facts = fetch_sec_company_facts(cik, session=session)
        us_gaap = facts.get("facts", {}).get("us-gaap", {})

        selected_concept = None
        concept_data: dict[str, Any] = {}
        for c in candidates:
            if c in us_gaap:
                selected_concept = c
                concept_data = us_gaap[c]
                break

        if not selected_concept or not concept_data:
            # Fallback to direct fetch_sec_concept
            try:
                direct = fetch_sec_concept(cik, concept=concept, session=session)
                selected_concept = concept
                concept_data = direct
            except Exception:
                selected_concept = concept
                concept_data = {}

        label = concept_data.get("label", selected_concept)
        description = concept_data.get("description")
        units_map = concept_data.get("units", {})

        # Primary unit is USD or shares
        unit_key = "USD" if "USD" in units_map else (list(units_map.keys())[0] if units_map else "USD")
        raw_units = units_map.get(unit_key, [])

        observations: list[SECXBRLFactObservation] = []
        for obs in raw_units:
            val = obs.get("val")
            end = obs.get("end")
            if val is None or end is None:
                continue
            observations.append(
                SECXBRLFactObservation(
                    end=str(end),
                    val=val,
                    fy=obs.get("fy"),
                    fp=obs.get("fp"),
                    form=obs.get("form"),
                    filed=obs.get("filed"),
                    frame=obs.get("frame"),
                    accn=obs.get("accn"),
                )
            )

        # Sort observations by period end descending and slice limit
        observations.sort(key=lambda x: x.end, reverse=True)
        trimmed_obs = observations[:limit]

        latest_val = trimmed_obs[0].val if trimmed_obs else None
        latest_period = trimmed_obs[0].end if trimmed_obs else None

        return SECXBRLConceptTimeseries(
            ticker=ticker.upper(),
            cik=cik,
            concept=selected_concept,
            label=label,
            description=description,
            unit=unit_key,
            latest_value=latest_val,
            latest_period=latest_period,
            observations=trimmed_obs,
        )

    def search_cik(self, query: str, limit: int = 10, session: Session | None = None) -> list[SECCIKLookupResult]:
        """Search SEC registrant CIK directory by ticker or company name."""
        matches = search_sec_entities(query=query, limit=limit, session=session)
        return [
            SECCIKLookupResult(
                ticker=m["ticker"],
                cik=m["cik"],
                title=m["title"],
            )
            for m in matches
        ]
