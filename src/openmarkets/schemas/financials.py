"""
Ticker Financial Schemas:
    income_stmt
    quarterly_income_stmt
    ttm_income_stmt
    balance_sheet
    cashflow
    quarterly_cashflow
    ttm_cashflow
    earnings
    calendar
    earnings_dates
    sec_filings
"""

from datetime import date, datetime

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class FinancialCalendar(BaseModel):
    """Earnings and dividend calendar for a ticker."""

    Dividend_Date: date | None = Field(None, alias="Dividend Date", description="Dividend payment date.")
    Ex_Dividend_Date: date | None = Field(None, alias="Ex-Dividend Date", description="Ex-dividend date.")
    Earnings_Date: list[date] | None = Field(None, alias="Earnings Date", description="List of earnings dates.")
    Earnings_High: float | None = Field(None, alias="Earnings High", description="High estimate for earnings.")
    Earnings_Low: float | None = Field(None, alias="Earnings Low", description="Low estimate for earnings.")
    Earnings_Average: float | None = Field(None, alias="Earnings Average", description="Average earnings estimate.")
    Revenue_High: int | None = Field(None, alias="Revenue High", description="High estimate for revenue.")
    Revenue_Low: int | None = Field(None, alias="Revenue Low", description="Low estimate for revenue.")
    Revenue_Average: int | None = Field(None, alias="Revenue Average", description="Average revenue estimate.")

    @field_validator("Dividend_Date", "Ex_Dividend_Date", mode="before")
    @classmethod
    def coerce_date_to_timestamp(cls, v):
        """Coerce date fields to pd.Timestamp."""
        if not isinstance(v, date):
            return datetime.fromisoformat(v)
        return v

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}


class SecFilingRecord(BaseModel):
    """Schema for ticker SEC filings data."""

    date: datetime | None = Field(None, description="Filing date")
    epochDate: int | None = Field(None, description="Filing date in epoch time")
    type: str | None = Field(None, description="Filing type")
    title: str | None = Field(None, description="Filing title")
    edgarUrl: str | None = Field(None, description="URL to the filing on EDGAR")
    exhibits: dict[str, str] | None = Field(None, description="Dictionary of exhibit names to URLs")
    maxAge: int | None = Field(None, description="Maximum age of the filing data")


class TTMCashFlowStatementEntry(BaseModel):
    """Schema for trailing twelve months (TTM) cash flow statement data.

    Each field corresponds to a cash flow statement item, typically reported for the trailing twelve months.
    All values are optional floats except for the index (date).
    """

    Date: datetime = Field(..., alias="index", description="Date of the TTM cash flow statement entry")
    Free_Cash_Flow: float | None = Field(None, alias="Free Cash Flow", description="Free cash flow")
    Repurchase_Of_Capital_Stock: float | None = Field(
        None, alias="Repurchase Of Capital Stock", description="Repurchase of capital stock"
    )
    Repayment_Of_Debt: float | None = Field(None, alias="Repayment Of Debt", description="Repayment of debt")
    Issuance_Of_Debt: float | None = Field(None, alias="Issuance Of Debt", description="Issuance of debt")
    Issuance_Of_Capital_Stock: float | None = Field(
        None, alias="Issuance Of Capital Stock", description="Issuance of capital stock"
    )
    Capital_Expenditure: float | None = Field(None, alias="Capital Expenditure", description="Capital expenditure")
    End_Cash_Position: float | None = Field(None, alias="End Cash Position", description="End cash position")
    Beginning_Cash_Position: float | None = Field(
        None, alias="Beginning Cash Position", description="Beginning cash position"
    )
    Effect_Of_Exchange_Rate_Changes: float | None = Field(
        None, alias="Effect Of Exchange Rate Changes", description="Effect of exchange rate changes"
    )
    Changes_In_Cash: float | None = Field(None, alias="Changes In Cash", description="Changes in cash")
    Financing_Cash_Flow: float | None = Field(None, alias="Financing Cash Flow", description="Financing cash flow")
    Cash_Flow_From_Continuing_Financing_Activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Financing Activities",
        description="Cash flow from continuing financing activities",
    )
    Net_Other_Financing_Charges: float | None = Field(
        None, alias="Net Other Financing Charges", description="Net other financing charges"
    )
    Cash_Dividends_Paid: float | None = Field(None, alias="Cash Dividends Paid", description="Cash dividends paid")
    Common_Stock_Dividend_Paid: float | None = Field(
        None, alias="Common Stock Dividend Paid", description="Common stock dividend paid"
    )
    Net_Common_Stock_Issuance: float | None = Field(
        None, alias="Net Common Stock Issuance", description="Net common stock issuance"
    )
    Common_Stock_Payments: float | None = Field(
        None, alias="Common Stock Payments", description="Common stock payments"
    )
    Common_Stock_Issuance: float | None = Field(
        None, alias="Common Stock Issuance", description="Common stock issuance"
    )
    Net_Issuance_Payments_Of_Debt: float | None = Field(
        None, alias="Net Issuance Payments Of Debt", description="Net issuance payments of debt"
    )
    Net_Short_Term_Debt_Issuance: float | None = Field(
        None, alias="Net Short Term Debt Issuance", description="Net short term debt issuance"
    )
    Net_Long_Term_Debt_Issuance: float | None = Field(
        None, alias="Net Long Term Debt Issuance", description="Net long term debt issuance"
    )
    Long_Term_Debt_Payments: float | None = Field(
        None, alias="Long Term Debt Payments", description="Long term debt payments"
    )
    Long_Term_Debt_Issuance: float | None = Field(
        None, alias="Long Term Debt Issuance", description="Long term debt issuance"
    )
    Investing_Cash_Flow: float | None = Field(None, alias="Investing Cash Flow", description="Investing cash flow")
    Cash_Flow_From_Continuing_Investing_Activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Investing Activities",
        description="Cash flow from continuing investing activities",
    )
    Net_Other_Investing_Changes: float | None = Field(
        None, alias="Net Other Investing Changes", description="Net other investing changes"
    )
    Net_Investment_Purchase_And_Sale: float | None = Field(
        None, alias="Net Investment Purchase And Sale", description="Net investment purchase and sale"
    )
    Sale_Of_Investment: float | None = Field(None, alias="Sale Of Investment", description="Sale of investment")
    Purchase_Of_Investment: float | None = Field(
        None, alias="Purchase Of Investment", description="Purchase of investment"
    )
    Net_Business_Purchase_And_Sale: float | None = Field(
        None, alias="Net Business Purchase And Sale", description="Net business purchase and sale"
    )
    Purchase_Of_Business: float | None = Field(None, alias="Purchase Of Business", description="Purchase of business")
    Net_PPE_Purchase_And_Sale: float | None = Field(
        None, alias="Net PPE Purchase And Sale", description="Net PPE purchase and sale"
    )
    Purchase_Of_PPE: float | None = Field(None, alias="Purchase Of PPE", description="Purchase of PPE")
    Operating_Cash_Flow: float | None = Field(None, alias="Operating Cash Flow", description="Operating cash flow")
    Cash_Flow_From_Continuing_Operating_Activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Operating Activities",
        description="Cash flow from continuing operating activities",
    )
    Change_In_Working_Capital: float | None = Field(
        None, alias="Change In Working Capital", description="Change in working capital"
    )
    Change_In_Other_Working_Capital: float | None = Field(
        None, alias="Change In Other Working Capital", description="Change in other working capital"
    )
    Change_In_Other_Current_Liabilities: float | None = Field(
        None, alias="Change In Other Current Liabilities", description="Change in other current liabilities"
    )
    Change_In_Other_Current_Assets: float | None = Field(
        None, alias="Change In Other Current Assets", description="Change in other current assets"
    )
    Change_In_Payables_And_Accrued_Expense: float | None = Field(
        None, alias="Change In Payables And Accrued Expense", description="Change in payables and accrued expense"
    )
    Change_In_Payable: float | None = Field(None, alias="Change In Payable", description="Change in payable")
    Change_In_Account_Payable: float | None = Field(
        None, alias="Change In Account Payable", description="Change in account payable"
    )
    Change_In_Inventory: float | None = Field(None, alias="Change In Inventory", description="Change in inventory")
    Change_In_Receivables: float | None = Field(
        None, alias="Change In Receivables", description="Change in receivables"
    )
    Changes_In_Account_Receivables: float | None = Field(
        None, alias="Changes In Account Receivables", description="Changes in account receivables"
    )
    Stock_Based_Compensation: float | None = Field(
        None, alias="Stock Based Compensation", description="Stock based compensation"
    )
    Unrealized_Gain_Loss_On_Investment_Securities: float | None = Field(
        None,
        alias="Unrealized Gain Loss On Investment Securities",
        description="Unrealized gain/loss on investment securities",
    )
    Asset_Impairment_Charge: float | None = Field(
        None, alias="Asset Impairment Charge", description="Asset impairment charge"
    )
    Deferred_Tax: float | None = Field(None, alias="Deferred Tax", description="Deferred tax")
    Deferred_Income_Tax: float | None = Field(None, alias="Deferred Income Tax", description="Deferred income tax")
    Depreciation_Amortization_Depletion: float | None = Field(
        None, alias="Depreciation Amortization Depletion", description="Depreciation, amortization, and depletion"
    )
    Depreciation_And_Amortization: float | None = Field(
        None, alias="Depreciation And Amortization", description="Depreciation and amortization"
    )
    Depreciation: float | None = Field(None, alias="Depreciation", description="Depreciation")
    Operating_Gains_Losses: float | None = Field(
        None, alias="Operating Gains Losses", description="Operating gains/losses"
    )
    Gain_Loss_On_Investment_Securities: float | None = Field(
        None, alias="Gain Loss On Investment Securities", description="Gain/loss on investment securities"
    )
    Net_Income_From_Continuing_Operations: float | None = Field(
        None, alias="Net Income From Continuing Operations", description="Net income from continuing operations"
    )


class TTMIncomeStatementEntry(BaseModel):
    """Schema for ticker trailing twelve months (TTM) income statement data."""

    Date: datetime = Field(..., alias="index", description="Date of the TTM income statement entry")
    Tax_Effect_Of_Unusual_Items: float | None = Field(
        None, alias="Tax Effect Of Unusual Items", description="Tax effect of unusual items"
    )
    Tax_Rate_For_Calcs: float | None = Field(None, alias="Tax Rate For Calcs", description="Tax rate for calculations")
    Normalized_EBITDA: float | None = Field(None, alias="Normalized EBITDA", description="Normalized EBITDA")
    Total_Unusual_Items: float | None = Field(None, alias="Total Unusual Items", description="Total unusual items")
    Total_Unusual_Items_Excluding_Goodwill: float | None = Field(
        None, alias="Total Unusual Items Excluding Goodwill", description="Total unusual items excluding goodwill"
    )
    Net_Income_From_Continuing_Operation_Net_Minority_Interest: float | None = Field(
        None,
        alias="Net Income From Continuing Operation Net Minority Interest",
        description="Net income from continuing operation net minority interest",
    )
    Reconciled_Depreciation: float | None = Field(
        None, alias="Reconciled Depreciation", description="Reconciled depreciation"
    )
    Reconciled_Cost_Of_Revenue: float | None = Field(
        None, alias="Reconciled Cost Of Revenue", description="Reconciled cost of revenue"
    )
    EBITDA: float | None = Field(None, alias="EBITDA", description="EBITDA")
    EBIT: float | None = Field(None, alias="EBIT", description="EBIT")
    Net_Interest_Income: float | None = Field(None, alias="Net Interest Income", description="Net interest income")
    Interest_Expense: float | None = Field(None, alias="Interest Expense", description="Interest expense")
    Interest_Income: float | None = Field(None, alias="Interest Income", description="Interest income")
    Normalized_Income: float | None = Field(None, alias="Normalized Income", description="Normalized income")
    Net_Income_From_Continuing_And_Discontinued_Operation: float | None = Field(
        None,
        alias="Net Income From Continuing And Discontinued Operation",
        description="Net income from continuing and discontinued operation",
    )
    Total_Expenses: float | None = Field(None, alias="Total Expenses", description="Total expenses")
    Total_Operating_Income_As_Reported: float | None = Field(
        None, alias="Total Operating Income As Reported", description="Total operating income as reported"
    )
    Diluted_Average_Shares: float | None = Field(
        None, alias="Diluted Average Shares", description="Diluted average shares"
    )
    Basic_Average_Shares: float | None = Field(None, alias="Basic Average Shares", description="Basic average shares")
    Diluted_EPS: float | None = Field(None, alias="Diluted EPS", description="Diluted earnings per share")
    Basic_EPS: float | None = Field(None, alias="Basic EPS", description="Basic earnings per share")
    Diluted_NI_Availto_Com_Stockholders: float | None = Field(
        None,
        alias="Diluted NI Availto Com Stockholders",
        description="Diluted net income available to common stockholders",
    )
    Net_Income_Common_Stockholders: float | None = Field(
        None, alias="Net Income Common Stockholders", description="Net income common stockholders"
    )
    Net_Income: float | None = Field(None, alias="Net Income", description="Net income")
    Net_Income_Including_Noncontrolling_Interests: float | None = Field(
        None,
        alias="Net Income Including Noncontrolling Interests",
        description="Net income including noncontrolling interests",
    )
    Net_Income_Continuous_Operations: float | None = Field(
        None, alias="Net Income Continuous Operations", description="Net income continuous operations"
    )
    Tax_Provision: float | None = Field(None, alias="Tax Provision", description="Tax provision")
    Pretax_Income: float | None = Field(None, alias="Pretax Income", description="Pretax income")
    Other_Income_Expense: float | None = Field(None, alias="Other Income Expense", description="Other income expense")
    Other_Non_Operating_Income_Expenses: float | None = Field(
        None, alias="Other Non Operating Income Expenses", description="Other non operating income expenses"
    )
    Special_Income_Charges: float | None = Field(
        None, alias="Special Income Charges", description="Special income charges"
    )
    Write_Off: float | None = Field(None, alias="Write Off", description="Write off")
    Gain_On_Sale_Of_Security: float | None = Field(
        None, alias="Gain On Sale Of Security", description="Gain on sale of security"
    )
    Net_Non_Operating_Interest_Income_Expense: float | None = Field(
        None, alias="Net Non Operating Interest Income Expense", description="Net non operating interest income expense"
    )
    Interest_Expense_Non_Operating: float | None = Field(
        None, alias="Interest Expense Non Operating", description="Interest expense non operating"
    )
    Interest_Income_Non_Operating: float | None = Field(
        None, alias="Interest Income Non Operating", description="Interest income non operating"
    )
    Operating_Income: float | None = Field(None, alias="Operating Income", description="Operating income")
    Operating_Expense: float | None = Field(None, alias="Operating Expense", description="Operating expense")
    Research_And_Development: float | None = Field(
        None, alias="Research And Development", description="Research and development"
    )
    Selling_General_And_Administration: float | None = Field(
        None, alias="Selling General And Administration", description="Selling general and administration"
    )
    Selling_And_Marketing_Expense: float | None = Field(
        None, alias="Selling And Marketing Expense", description="Selling and marketing expense"
    )
    General_And_Administrative_Expense: float | None = Field(
        None, alias="General And Administrative Expense", description="General and administrative expense"
    )
    Other_GandA: float | None = Field(None, alias="Other Gand A", description="Other G&A")
    Gross_Profit: float | None = Field(None, alias="Gross Profit", description="Gross profit")
    Cost_Of_Revenue: float | None = Field(None, alias="Cost Of Revenue", description="Cost of revenue")
    Total_Revenue: float | None = Field(None, alias="Total Revenue", description="Total revenue")
    Operating_Revenue: float | None = Field(None, alias="Operating Revenue", description="Operating revenue")


class IncomeStatementEntry(BaseModel):
    """Schema for a single income statement entry for a ticker.

    Each field corresponds to an income statement item, typically reported annually or quarterly.
    All values are optional floats except for the index (date).
    """

    Date: datetime = Field(..., description="Date of the income statement entry", alias="index")
    TotalRevenue: float | None = Field(None, description="Total revenue")
    CostOfRevenue: float | None = Field(None, description="Cost of revenue")
    GrossProfit: float | None = Field(None, description="Gross profit")
    ResearchDevelopment: float | None = Field(None, description="Research and development expenses")
    SellingGeneralAdministrative: float | None = Field(None, description="Selling, general and administrative expenses")
    NonRecurring: float | None = Field(None, description="Non-recurring items")
    OtherOperatingExpenses: float | None = Field(None, description="Other operating expenses")
    TotalOperatingExpenses: float | None = Field(None, description="Total operating expenses")
    OperatingIncomeOrLoss: float | None = Field(None, description="Operating income or loss")
    TotalOtherIncomeExpenseNet: float | None = Field(None, description="Total other income/expense net")
    EarningsBeforeInterestAndTaxes: float | None = Field(None, description="Earnings before interest and taxes (EBIT)")
    InterestExpense: float | None = Field(None, description="Interest expense")
    IncomeBeforeTax: float | None = Field(None, description="Income before tax")
    IncomeTaxExpense: float | None = Field(None, description="Income tax expense")
    NetIncomeFromContinuingOps: float | None = Field(None, description="Net income from continuing operations")
    NetIncomeApplicableToCommonShares: float | None = Field(None, description="Net income applicable to common shares")


class BalanceSheetEntry(BaseModel):
    """Schema for a single balance sheet entry for a ticker.

    Each field corresponds to a balance sheet item, typically reported annually or quarterly.
    All values are optional floats except for the index (date).
    """

    Date: datetime = Field(..., description="Date of the balance sheet entry", alias="index")
    OrdinarySharesNumber: float | None = Field(None, description="Number of ordinary shares")
    ShareIssued: float | None = Field(None, description="Shares issued")
    NetDebt: float | None = Field(None, description="Net debt")
    TotalDebt: float | None = Field(None, description="Total debt")
    TangibleBookValue: float | None = Field(None, description="Tangible book value")
    InvestedCapital: float | None = Field(None, description="Invested capital")
    WorkingCapital: float | None = Field(None, description="Working capital")
    NetTangibleAssets: float | None = Field(None, description="Net tangible assets")
    CapitalLeaseObligations: float | None = Field(None, description="Capital lease obligations")
    CommonStockEquity: float | None = Field(None, description="Common stock equity")
    TotalCapitalization: float | None = Field(None, description="Total capitalization")
    TotalEquityGrossMinorityInterest: float | None = Field(None, description="Total equity gross minority interest")
    StockholdersEquity: float | None = Field(None, description="Stockholders' equity")
    GainsLossesNotAffectingRetainedEarnings: float | None = Field(
        None, description="Gains/losses not affecting retained earnings"
    )
    OtherEquityAdjustments: float | None = Field(None, description="Other equity adjustments")
    RetainedEarnings: float | None = Field(None, description="Retained earnings")
    CapitalStock: float | None = Field(None, description="Capital stock")
    CommonStock: float | None = Field(None, description="Common stock")
    TotalLiabilitiesNetMinorityInterest: float | None = Field(
        None, description="Total liabilities net minority interest"
    )
    TotalNonCurrentLiabilitiesNetMinorityInterest: float | None = Field(
        None, description="Total non-current liabilities net minority interest"
    )
    OtherNonCurrentLiabilities: float | None = Field(None, description="Other non-current liabilities")
    TradeandOtherPayablesNonCurrent: float | None = Field(None, description="Trade and other payables (non-current)")
    NonCurrentDeferredLiabilities: float | None = Field(None, description="Non-current deferred liabilities")
    NonCurrentDeferredRevenue: float | None = Field(None, description="Non-current deferred revenue")
    NonCurrentDeferredTaxesLiabilities: float | None = Field(None, description="Non-current deferred taxes liabilities")
    LongTermDebtAndCapitalLeaseObligation: float | None = Field(
        None, description="Long-term debt and capital lease obligation"
    )
    LongTermCapitalLeaseObligation: float | None = Field(None, description="Long-term capital lease obligation")
    LongTermDebt: float | None = Field(None, description="Long-term debt")
    CurrentLiabilities: float | None = Field(None, description="Current liabilities")
    OtherCurrentLiabilities: float | None = Field(None, description="Other current liabilities")
    CurrentDeferredLiabilities: float | None = Field(None, description="Current deferred liabilities")
    CurrentDeferredRevenue: float | None = Field(None, description="Current deferred revenue")
    CurrentDebtAndCapitalLeaseObligation: float | None = Field(
        None, description="Current debt and capital lease obligation"
    )
    CurrentDebt: float | None = Field(None, description="Current debt")
    OtherCurrentBorrowings: float | None = Field(None, description="Other current borrowings")
    CommercialPaper: float | None = Field(None, description="Commercial paper")
    PensionandOtherPostRetirementBenefitPlansCurrent: float | None = Field(
        None, description="Pension and other post-retirement benefit plans (current)"
    )
    PayablesAndAccruedExpenses: float | None = Field(None, description="Payables and accrued expenses")
    Payables: float | None = Field(None, description="Payables")
    TotalTaxPayable: float | None = Field(None, description="Total tax payable")
    IncomeTaxPayable: float | None = Field(None, description="Income tax payable")
    AccountsPayable: float | None = Field(None, description="Accounts payable")
    TotalAssets: float | None = Field(None, description="Total assets")
    TotalNonCurrentAssets: float | None = Field(None, description="Total non-current assets")
    OtherNonCurrentAssets: float | None = Field(None, description="Other non-current assets")
    FinancialAssets: float | None = Field(None, description="Financial assets")
    InvestmentsAndAdvances: float | None = Field(None, description="Investments and advances")
    InvestmentinFinancialAssets: float | None = Field(None, description="Investment in financial assets")
    AvailableForSaleSecurities: float | None = Field(None, description="Available-for-sale securities")
    LongTermEquityInvestment: float | None = Field(None, description="Long-term equity investment")
    GoodwillAndOtherIntangibleAssets: float | None = Field(None, description="Goodwill and other intangible assets")
    OtherIntangibleAssets: float | None = Field(None, description="Other intangible assets")
    Goodwill: float | None = Field(None, description="Goodwill")
    NetPPE: float | None = Field(None, description="Net property, plant, and equipment (PPE)")
    AccumulatedDepreciation: float | None = Field(None, description="Accumulated depreciation")
    GrossPPE: float | None = Field(None, description="Gross property, plant, and equipment (PPE)")
    Leases: float | None = Field(None, description="Leases")
    OtherProperties: float | None = Field(None, description="Other properties")
    MachineryFurnitureEquipment: float | None = Field(None, description="Machinery, furniture, and equipment")
    BuildingsAndImprovements: float | None = Field(None, description="Buildings and improvements")
    LandAndImprovements: float | None = Field(None, description="Land and improvements")
    Properties: float | None = Field(None, description="Properties")
    CurrentAssets: float | None = Field(None, description="Current assets")
    OtherCurrentAssets: float | None = Field(None, description="Other current assets")
    HedgingAssetsCurrent: float | None = Field(None, description="Hedging assets (current)")
    Inventory: float | None = Field(None, description="Inventory")
    FinishedGoods: float | None = Field(None, description="Finished goods")
    WorkInProcess: float | None = Field(None, description="Work in process")
    RawMaterials: float | None = Field(None, description="Raw materials")
    Receivables: float | None = Field(None, description="Receivables")
    AccountsReceivable: float | None = Field(None, description="Accounts receivable")
    AllowanceForDoubtfulAccountsReceivable: float | None = Field(
        None, description="Allowance for doubtful accounts receivable"
    )
    GrossAccountsReceivable: float | None = Field(None, description="Gross accounts receivable")
    CashCashEquivalentsAndShortTermInvestments: float | None = Field(
        None, description="Cash, cash equivalents, and short-term investments"
    )
    OtherShortTermInvestments: float | None = Field(None, description="Other short-term investments")
    CashAndCashEquivalents: float | None = Field(None, description="Cash and cash equivalents")
    CashEquivalents: float | None = Field(None, description="Cash equivalents")
    CashFinancial: float | None = Field(None, description="Cash (financial)")


class EPSHistoryEntry(BaseModel):
    """Schema for ticker earnings dates data."""

    Earnings_Date: datetime | None = Field(None, description="Earnings date", alias="Earnings Date")
    EPS_Estimate: float | None = Field(None, description="Earnings per share estimate", alias="EPS Estimate")
    Reported_EPS: float | None = Field(None, description="Reported earnings per share", alias="Reported EPS")
    Surprise_pst: float | None = Field(None, description="Earnings surprise percentage", alias="Surprise(%)")

    @field_validator("Earnings_Date", mode="before")
    @classmethod
    def coerce_date_to_timestamp(cls, v):
        """Coerce date fields to pd.Timestamp."""
        if isinstance(v, pd.Timestamp):
            return v.to_pydatetime()
        return v
