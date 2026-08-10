"""Pydantic schemas for SEC EDGAR corporate filings and XBRL financial disclosures."""

from pydantic import BaseModel, ConfigDict, Field


class SECCIKLookupResult(BaseModel):
    """Result of an SEC company CIK search query."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="10-digit zero-padded SEC Central Index Key (CIK)")
    title: str = Field(..., description="Official SEC registrant corporate name")


class SECAddress(BaseModel):
    """Mailing or business address of an SEC registered entity."""

    model_config = ConfigDict(populate_by_name=True)

    street1: str | None = Field(None, description="Primary street line")
    street2: str | None = Field(None, description="Secondary street line")
    city: str | None = Field(None, description="City name")
    state_or_country: str | None = Field(None, description="State or Country code")
    zip_code: str | None = Field(None, description="Postal / ZIP code")


class SECCompanyProfile(BaseModel):
    """Comprehensive corporate metadata filed with the SEC."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="10-digit zero-padded SEC CIK")
    name: str = Field(..., description="Official registrant corporate name")
    sic: str | None = Field(None, description="Standard Industrial Classification (SIC) code")
    sic_description: str | None = Field(None, description="SIC industry title")
    fiscal_year_end: str | None = Field(None, description="Month/Day of fiscal year end (e.g. '0930')")
    state_of_incorporation: str | None = Field(None, description="State or country of legal incorporation")
    business_address: SECAddress | None = Field(None, description="Primary corporate headquarters address")
    mailing_address: SECAddress | None = Field(None, description="Mailing address")
    phone: str | None = Field(None, description="Primary corporate telephone number")
    website: str | None = Field(None, description="Corporate website URL")
    investor_website: str | None = Field(None, description="Investor relations website URL")


class SECFilingItem(BaseModel):
    """A single regulatory filing submitted to the SEC EDGAR system."""

    model_config = ConfigDict(populate_by_name=True)

    form: str = Field(..., description="SEC Form type (e.g. '10-K', '10-Q', '8-K', '4', '13F-HR')")
    filing_date: str = Field(..., description="Date accepted and posted by the SEC (YYYY-MM-DD)")
    report_date: str | None = Field(None, description="Period of report / fiscal end date (YYYY-MM-DD)")
    accession_number: str = Field(..., description="Unique 20-character SEC accession number")
    primary_document: str = Field(..., description="Primary document filename (e.g. 'aapl-20260627.htm')")
    primary_doc_description: str | None = Field(None, description="Description or title of the primary document")
    is_xbrl: bool = Field(False, description="Whether the filing includes structured interactive XBRL data")
    document_url: str = Field(..., description="Direct HTTPS link to read the primary document on SEC EDGAR")


class SECXBRLFactObservation(BaseModel):
    """A single reported financial fact point in an XBRL disclosure."""

    model_config = ConfigDict(populate_by_name=True)

    end: str = Field(..., description="Accounting period end date (YYYY-MM-DD)")
    val: float | int = Field(..., description="Reported financial value in currency or shares")
    fy: int | None = Field(None, description="Fiscal year (e.g. 2026)")
    fp: str | None = Field(None, description="Fiscal period (e.g. 'Q1', 'Q2', 'Q3', 'FY')")
    form: str | None = Field(None, description="SEC Form containing this fact (e.g. '10-K', '10-Q')")
    filed: str | None = Field(None, description="Date filed with the SEC")
    frame: str | None = Field(None, description="Standardized CY/CQ reporting frame (e.g. 'CY2026Q2')")
    accn: str | None = Field(None, description="Accession number of filing")


class SECXBRLConceptTimeseries(BaseModel):
    """Standardized timeseries for a specific US-GAAP or DEI accounting concept."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="10-digit zero-padded SEC CIK")
    concept: str = Field(..., description="Standardized XBRL tag name (e.g. 'Revenues', 'Assets')")
    label: str | None = Field(None, description="Human-readable concept title")
    description: str | None = Field(None, description="US-GAAP accounting definition")
    unit: str = Field("USD", description="Measurement unit (e.g. 'USD', 'shares')")
    latest_value: float | int | None = Field(None, description="Most recent reported value")
    latest_period: str | None = Field(None, description="Period end date for latest value")
    observations: list[SECXBRLFactObservation] = Field(default_factory=list, description="Historical observations")


class SECXBRLCompanyFactsSummary(BaseModel):
    """Summary of available interactive XBRL financial statements for a registrant."""

    model_config = ConfigDict(populate_by_name=True)

    ticker: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="10-digit zero-padded SEC CIK")
    entity_name: str = Field(..., description="Official registrant corporate name")
    available_gaap_concepts_count: int = Field(..., description="Total US-GAAP concepts filed")
    available_concepts_sample: list[str] = Field(default_factory=list, description="Sample of concept tag names")
    key_metrics_available: list[str] = Field(default_factory=list, description="Identified standard financial metrics")
