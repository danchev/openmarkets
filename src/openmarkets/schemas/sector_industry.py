from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SectorEnum(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial-services"
    INDUSTRIALS = "industrials"
    ENERGY = "energy"
    UTILITIES = "utilities"
    REAL_ESTATE = "real-estate"
    COMMUNICATION_SERVICES = "communication-services"
    CONSUMER_DEFENSIVE = "consumer-defensive"
    CONSUMER_CYCLICAL = "consumer-cyclical"
    BASIC_MATERIALS = "basic-materials"


SECTOR_INDUSTRY_MAPPING: dict[str, list[str]] = {
    "basic-materials": [
        "agricultural-inputs",
        "aluminum",
        "building-materials",
        "chemicals",
        "coking-coal",
        "copper",
        "gold",
        "lumber-wood-production",
        "other-industrial-metals-mining",
        "other-precious-metals-mining",
        "paper-paper-products",
        "silver",
        "specialty-chemicals",
        "steel",
    ],
    "communication-services": [
        "advertising-agencies",
        "broadcasting",
        "electronic-gaming-multimedia",
        "entertainment",
        "internet-content-information",
        "publishing",
        "telecom-services",
    ],
    "consumer-cyclical": [
        "apparel-manufacturing",
        "apparel-retail",
        "auto-manufacturers",
        "auto-parts",
        "auto-truck-dealerships",
        "department-stores",
        "footwear-accessories",
        "furnishings-fixtures-appliances",
        "gambling",
        "home-improvement-retail",
        "internet-retail",
        "leisure",
        "lodging",
        "luxury-goods",
        "packaging-containers",
        "personal-services",
        "recreational-vehicles",
        "residential-construction",
        "resorts-casinos",
        "restaurants",
        "specialty-retail",
        "textile-manufacturing",
        "travel-services",
    ],
    "consumer-defensive": [
        "beverages-brewers",
        "beverages-non-alcoholic",
        "beverages-wineries-distilleries",
        "confectioners",
        "discount-stores",
        "education-training-services",
        "farm-products",
        "food-distribution",
        "grocery-stores",
        "household-personal-products",
        "packaged-foods",
        "tobacco",
    ],
    "energy": [
        "oil-gas-drilling",
        "oil-gas-e-p",
        "oil-gas-equipment-services",
        "oil-gas-integrated",
        "oil-gas-midstream",
        "oil-gas-refining-marketing",
        "thermal-coal",
        "uranium",
    ],
    "financial-services": [
        "asset-management",
        "banks-diversified",
        "banks-regional",
        "capital-markets",
        "credit-services",
        "financial-conglomerates",
        "financial-data-stock-exchanges",
        "insurance-brokers",
        "insurance-diversified",
        "insurance-life",
        "insurance-property-casualty",
        "insurance-reinsurance",
        "insurance-specialty",
        "mortgage-finance",
        "shell-companies",
    ],
    "healthcare": [
        "biotechnology",
        "diagnostics-research",
        "drug-manufacturers-general",
        "drug-manufacturers-specialty-generic",
        "health-information-services",
        "healthcare-plans",
        "medical-care-facilities",
        "medical-devices",
        "medical-distribution",
        "medical-instruments-supplies",
        "pharmaceutical-retailers",
    ],
    "industrials": [
        "aerospace-defense",
        "airlines",
        "airports-air-services",
        "building-products-equipment",
        "business-equipment-supplies",
        "conglomerates",
        "consulting-services",
        "electrical-equipment-parts",
        "engineering-construction",
        "farm-heavy-construction-machinery",
        "industrial-distribution",
        "infrastructure-operations",
        "integrated-freight-logistics",
        "marine-shipping",
        "metal-fabrication",
        "pollution-treatment-controls",
        "railroads",
        "rental-leasing-services",
        "security-protection-services",
        "specialty-business-services",
        "specialty-industrial-machinery",
        "staffing-employment-services",
        "tools-accessories",
        "trucking",
        "waste-management",
    ],
    "real-estate": [
        "real-estate-development",
        "real-estate-diversified",
        "real-estate-services",
        "reit-diversified",
        "reit-healthcare-facilities",
        "reit-hotel-motel",
        "reit-industrial",
        "reit-mortgage",
        "reit-office",
        "reit-residential",
        "reit-retail",
        "reit-specialty",
    ],
    "technology": [
        "communication-equipment",
        "computer-hardware",
        "consumer-electronics",
        "electronic-components",
        "electronics-computer-distribution",
        "information-technology-services",
        "scientific-technical-instruments",
        "semiconductor-equipment-materials",
        "semiconductors",
        "software-application",
        "software-infrastructure",
        "solar",
    ],
    "utilities": [
        "utilities-diversified",
        "utilities-independent-power-producers",
        "utilities-regulated-electric",
        "utilities-regulated-gas",
        "utilities-regulated-water",
        "utilities-renewable",
    ],
}


class SectorOverview(BaseModel):
    """
    Sector Overview Schema
    """

    companies_count: int = Field(..., alias="companies_count")
    market_cap: int = Field(..., alias="market_cap")
    message_board_id: str = Field(..., alias="message_board_id")
    description: str = Field(..., alias="description")
    industries_count: int = Field(..., alias="industries_count")
    market_weight: float = Field(..., alias="market_weight")
    employee_count: int = Field(..., alias="employee_count")


class SectorTopCompaniesEntry(BaseModel):
    """
    Sector Top Companies Entry Schema
    """

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    rating: str = Field(..., description="Company rating")
    market_weight: float = Field(..., description="Market weight", alias="market weight")


class SectorTopETFsEntry(BaseModel):
    """
    Sector Top ETFs Entry Schema
    """

    symbol: str = Field(..., description="ETF ticker symbol")
    name: str = Field(..., description="ETF name")


class SectorTopMutualFundsEntry(BaseModel):
    """
    Sector Top Mutual Funds Entry Schema
    """

    symbol: str = Field(..., description="Mutual Fund ticker symbol")
    name: str = Field(..., description="Mutual Fund name")


class IndustryOverview(BaseModel):
    """
    Industry Overview Schema
    """

    # {'companies_count': 4, 'market_cap': 17122720768, 'message_board_id': 'INDEXYH10150010', 'description': 'Companies that produce, refine, market, and distribute aluminum and related aluminum-based products.', 'industries_count': None, 'market_weight': 0.0087670535, 'employee_count': 19101}
    companies_count: int = Field(..., alias="companies_count")
    market_cap: int = Field(..., alias="market_cap")
    message_board_id: str = Field(..., alias="message_board_id")
    description: str = Field(..., alias="description")
    industries_count: int | None = Field(None, alias="industries_count")
    market_weight: float = Field(..., alias="market_weight")
    employee_count: int = Field(..., alias="employee_count")


class IndustryTopCompaniesEntry(BaseModel):
    """
    Industry Top Companies Entry Schema
    """

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    rating: str | None = Field(None, description="Company rating")
    market_weight: float = Field(..., description="Market weight", alias="market weight")


class IndustryResearchReportEntry(BaseModel):
    """
    Industry Research Report Entry Schema
    """

    id: str = Field(..., description="Research report ID")
    head_html: str = Field(..., description="Research report headline", alias="headHtml")
    provider: str = Field(..., description="Research report provider")
    target_price: float | str | None = Field(None, description="Target price", alias="targetPrice")
    target_price_status: str | None = Field(None, description="Target price status", alias="targetPriceStatus")
    investment_rating: str | None = Field(None, description="Investment rating", alias="investmentRating")
    report_date: str | None = Field(None, description="Report date", alias="reportDate")
    report_title: str = Field(..., description="Report title", alias="reportTitle")
    report_type: str = Field(..., description="Report type", alias="reportType")

    @field_validator("target_price", mode="before")
    def validate_target_price(cls, v):
        if v is None:
            return v
        try:
            return float(v)
        except Exception:
            return None


class IndustryTopGrowthCompaniesEntry(BaseModel):
    """
    Industry Top Growth Companies Entry Schema
    """

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    ytd_return: float = Field(..., description="Year-to-date return", alias="ytd return")
    growth_estimate: float = Field(..., description="Growth Estimate", alias="growth estimate")


class IndustryTopPerformingCompaniesEntry(BaseModel):
    """
    Industry Top Growth Companies Entry Schema
    """

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    ytd_return: float = Field(..., description="Year-to-date return", alias="ytd return")
    last_price: float = Field(..., description="Last Price", alias="last price")
    target_price: float = Field(..., description="Target Price", alias="target price")
