from datetime import date, datetime

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class FinancialCalendar(BaseModel):
    """Earnings and dividend calendar for a ticker."""

    dividend_date: date | None = Field(None, alias="Dividend Date", description="Dividend payment date.")
    ex_dividend_date: date | None = Field(None, alias="Ex-Dividend Date", description="Ex-dividend date.")
    earnings_date: list[date] | None = Field(None, alias="Earnings Date", description="List of earnings dates.")
    earnings_high: float | None = Field(None, alias="Earnings High", description="High estimate for earnings.")
    earnings_low: float | None = Field(None, alias="Earnings Low", description="Low estimate for earnings.")
    earnings_average: float | None = Field(None, alias="Earnings Average", description="Average earnings estimate.")
    revenue_high: int | None = Field(None, alias="Revenue High", description="High estimate for revenue.")
    revenue_low: int | None = Field(None, alias="Revenue Low", description="Low estimate for revenue.")
    revenue_average: int | None = Field(None, alias="Revenue Average", description="Average revenue estimate.")

    @field_validator("dividend_date", "ex_dividend_date", mode="before")
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
    epoch_date: int | None = Field(None, alias="epochDate", description="Filing date in epoch time")
    type: str | None = Field(None, description="Filing type")
    title: str | None = Field(None, description="Filing title")
    edgar_url: str | None = Field(None, alias="edgarUrl", description="URL to the filing on EDGAR")
    exhibits: dict[str, str] | None = Field(None, description="Dictionary of exhibit names to URLs")
    max_age: int | None = Field(None, alias="maxAge", description="Maximum age of the filing data")


class TTMCashFlowStatementEntry(BaseModel):
    """Schema for trailing twelve months (TTM) cash flow statement data."""

    date: datetime = Field(..., alias="index", description="Date of the TTM cash flow statement entry")
    free_cash_flow: float | None = Field(None, alias="Free Cash Flow", description="Free cash flow")
    repurchase_of_capital_stock: float | None = Field(
        None, alias="Repurchase Of Capital Stock", description="Repurchase of capital stock"
    )
    repayment_of_debt: float | None = Field(None, alias="Repayment Of Debt", description="Repayment of debt")
    issuance_of_debt: float | None = Field(None, alias="Issuance Of Debt", description="Issuance of debt")
    issuance_of_capital_stock: float | None = Field(
        None, alias="Issuance Of Capital Stock", description="Issuance of capital stock"
    )
    capital_expenditure: float | None = Field(None, alias="Capital Expenditure", description="Capital expenditure")
    end_cash_position: float | None = Field(None, alias="End Cash Position", description="End cash position")
    beginning_cash_position: float | None = Field(
        None, alias="Beginning Cash Position", description="Beginning cash position"
    )
    effect_of_exchange_rate_changes: float | None = Field(
        None, alias="Effect Of Exchange Rate Changes", description="Effect of exchange rate changes"
    )
    changes_in_cash: float | None = Field(None, alias="Changes In Cash", description="Changes in cash")
    financing_cash_flow: float | None = Field(None, alias="Financing Cash Flow", description="Financing cash flow")
    cash_flow_from_continuing_financing_activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Financing Activities",
        description="Cash flow from continuing financing activities",
    )
    net_other_financing_charges: float | None = Field(
        None, alias="Net Other Financing Charges", description="Net other financing charges"
    )
    cash_dividends_paid: float | None = Field(None, alias="Cash Dividends Paid", description="Cash dividends paid")
    common_stock_dividend_paid: float | None = Field(
        None, alias="Common Stock Dividend Paid", description="Common stock dividend paid"
    )
    net_common_stock_issuance: float | None = Field(
        None, alias="Net Common Stock Issuance", description="Net common stock issuance"
    )
    common_stock_payments: float | None = Field(
        None, alias="Common Stock Payments", description="Common stock payments"
    )
    common_stock_issuance: float | None = Field(
        None, alias="Common Stock Issuance", description="Common stock issuance"
    )
    net_issuance_payments_of_debt: float | None = Field(
        None, alias="Net Issuance Payments Of Debt", description="Net issuance payments of debt"
    )
    net_short_term_debt_issuance: float | None = Field(
        None, alias="Net Short Term Debt Issuance", description="Net short term debt issuance"
    )
    net_long_term_debt_issuance: float | None = Field(
        None, alias="Net Long Term Debt Issuance", description="Net long term debt issuance"
    )
    long_term_debt_payments: float | None = Field(
        None, alias="Long Term Debt Payments", description="Long term debt payments"
    )
    long_term_debt_issuance: float | None = Field(
        None, alias="Long Term Debt Issuance", description="Long term debt issuance"
    )
    investing_cash_flow: float | None = Field(None, alias="Investing Cash Flow", description="Investing cash flow")
    cash_flow_from_continuing_investing_activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Investing Activities",
        description="Cash flow from continuing investing activities",
    )
    net_other_investing_changes: float | None = Field(
        None, alias="Net Other Investing Changes", description="Net other investing changes"
    )
    net_investment_purchase_and_sale: float | None = Field(
        None, alias="Net Investment Purchase And Sale", description="Net investment purchase and sale"
    )
    sale_of_investment: float | None = Field(None, alias="Sale Of Investment", description="Sale of investment")
    purchase_of_investment: float | None = Field(
        None, alias="Purchase Of Investment", description="Purchase of investment"
    )
    net_business_purchase_and_sale: float | None = Field(
        None, alias="Net Business Purchase And Sale", description="Net business purchase and sale"
    )
    purchase_of_business: float | None = Field(None, alias="Purchase Of Business", description="Purchase of business")
    net_ppe_purchase_and_sale: float | None = Field(
        None, alias="Net PPE Purchase And Sale", description="Net PPE purchase and sale"
    )
    purchase_of_ppe: float | None = Field(None, alias="Purchase Of PPE", description="Purchase of PPE")
    operating_cash_flow: float | None = Field(None, alias="Operating Cash Flow", description="Operating cash flow")
    cash_flow_from_continuing_operating_activities: float | None = Field(
        None,
        alias="Cash Flow From Continuing Operating Activities",
        description="Cash flow from continuing operating activities",
    )
    change_in_working_capital: float | None = Field(
        None, alias="Change In Working Capital", description="Change in working capital"
    )
    change_in_other_working_capital: float | None = Field(
        None, alias="Change In Other Working Capital", description="Change in other working capital"
    )
    change_in_other_current_liabilities: float | None = Field(
        None, alias="Change In Other Current Liabilities", description="Change in other current liabilities"
    )
    change_in_other_current_assets: float | None = Field(
        None, alias="Change In Other Current Assets", description="Change in other current assets"
    )
    change_in_payables_and_accrued_expense: float | None = Field(
        None, alias="Change In Payables And Accrued Expense", description="Change in payables and accrued expense"
    )
    change_in_payable: float | None = Field(None, alias="Change In Payable", description="Change in payable")
    change_in_account_payable: float | None = Field(
        None, alias="Change In Account Payable", description="Change in account payable"
    )
    change_in_inventory: float | None = Field(None, alias="Change In Inventory", description="Change in inventory")
    change_in_receivables: float | None = Field(
        None, alias="Change In Receivables", description="Change in receivables"
    )
    changes_in_account_receivables: float | None = Field(
        None, alias="Changes In Account Receivables", description="Changes in account receivables"
    )
    stock_based_compensation: float | None = Field(
        None, alias="Stock Based Compensation", description="Stock based compensation"
    )
    unrealized_gain_loss_on_investment_securities: float | None = Field(
        None,
        alias="Unrealized Gain Loss On Investment Securities",
        description="Unrealized gain/loss on investment securities",
    )
    asset_impairment_charge: float | None = Field(
        None, alias="Asset Impairment Charge", description="Asset impairment charge"
    )
    deferred_tax: float | None = Field(None, alias="Deferred Tax", description="Deferred tax")
    deferred_income_tax: float | None = Field(None, alias="Deferred Income Tax", description="Deferred income tax")
    depreciation_amortization_depletion: float | None = Field(
        None, alias="Depreciation Amortization Depletion", description="Depreciation, amortization, and depletion"
    )
    depreciation_and_amortization: float | None = Field(
        None, alias="Depreciation And Amortization", description="Depreciation and amortization"
    )
    depreciation: float | None = Field(None, alias="Depreciation", description="Depreciation")
    operating_gains_losses: float | None = Field(
        None, alias="Operating Gains Losses", description="Operating gains/losses"
    )
    gain_loss_on_investment_securities: float | None = Field(
        None, alias="Gain Loss On Investment Securities", description="Gain/loss on investment securities"
    )
    net_income_from_continuing_operations: float | None = Field(
        None, alias="Net Income From Continuing Operations", description="Net income from continuing operations"
    )


class TTMIncomeStatementEntry(BaseModel):
    """Schema for ticker trailing twelve months (TTM) income statement data."""

    date: datetime = Field(..., alias="index", description="Date of the TTM income statement entry")
    tax_effect_of_unusual_items: float | None = Field(
        None, alias="Tax Effect Of Unusual Items", description="Tax effect of unusual items"
    )
    tax_rate_for_calcs: float | None = Field(None, alias="Tax Rate For Calcs", description="Tax rate for calculations")
    normalized_ebitda: float | None = Field(None, alias="Normalized EBITDA", description="Normalized EBITDA")
    total_unusual_items: float | None = Field(None, alias="Total Unusual Items", description="Total unusual items")
    total_unusual_items_excluding_goodwill: float | None = Field(
        None, alias="Total Unusual Items Excluding Goodwill", description="Total unusual items excluding goodwill"
    )
    net_income_from_continuing_operation_net_minority_interest: float | None = Field(
        None,
        alias="Net Income From Continuing Operation Net Minority Interest",
        description="Net income from continuing operation net minority interest",
    )
    reconciled_depreciation: float | None = Field(
        None, alias="Reconciled Depreciation", description="Reconciled depreciation"
    )
    reconciled_cost_of_revenue: float | None = Field(
        None, alias="Reconciled Cost Of Revenue", description="Reconciled cost of revenue"
    )
    ebitda: float | None = Field(None, alias="EBITDA", description="EBITDA")
    ebit: float | None = Field(None, alias="EBIT", description="EBIT")
    net_interest_income: float | None = Field(None, alias="Net Interest Income", description="Net interest income")
    interest_expense: float | None = Field(None, alias="Interest Expense", description="Interest expense")
    interest_income: float | None = Field(None, alias="Interest Income", description="Interest income")
    normalized_income: float | None = Field(None, alias="Normalized Income", description="Normalized income")
    net_income_from_continuing_and_discontinued_operation: float | None = Field(
        None,
        alias="Net Income From Continuing And Discontinued Operation",
        description="Net income from continuing and discontinued operation",
    )
    total_expenses: float | None = Field(None, alias="Total Expenses", description="Total expenses")
    total_operating_income_as_reported: float | None = Field(
        None, alias="Total Operating Income As Reported", description="Total operating income as reported"
    )
    diluted_average_shares: float | None = Field(
        None, alias="Diluted Average Shares", description="Diluted average shares"
    )
    basic_average_shares: float | None = Field(None, alias="Basic Average Shares", description="Basic average shares")
    diluted_eps: float | None = Field(None, alias="Diluted EPS", description="Diluted earnings per share")
    basic_eps: float | None = Field(None, alias="Basic EPS", description="Basic earnings per share")
    diluted_ni_availto_com_stockholders: float | None = Field(
        None,
        alias="Diluted NI Availto Com Stockholders",
        description="Diluted net income available to common stockholders",
    )
    net_income_common_stockholders: float | None = Field(
        None, alias="Net Income Common Stockholders", description="Net income common stockholders"
    )
    net_income: float | None = Field(None, alias="Net Income", description="Net income")
    net_income_including_noncontrolling_interests: float | None = Field(
        None,
        alias="Net Income Including Noncontrolling Interests",
        description="Net income including noncontrolling interests",
    )
    net_income_continuous_operations: float | None = Field(
        None, alias="Net Income Continuous Operations", description="Net income continuous operations"
    )
    tax_provision: float | None = Field(None, alias="Tax Provision", description="Tax provision")
    pretax_income: float | None = Field(None, alias="Pretax Income", description="Pretax income")
    other_income_expense: float | None = Field(None, alias="Other Income Expense", description="Other income expense")
    other_non_operating_income_expenses: float | None = Field(
        None, alias="Other Non Operating Income Expenses", description="Other non operating income expenses"
    )
    special_income_charges: float | None = Field(
        None, alias="Special Income Charges", description="Special income charges"
    )
    write_off: float | None = Field(None, alias="Write Off", description="Write off")
    gain_on_sale_of_security: float | None = Field(
        None, alias="Gain On Sale Of Security", description="Gain on sale of security"
    )
    net_non_operating_interest_income_expense: float | None = Field(
        None, alias="Net Non Operating Interest Income Expense", description="Net non operating interest income expense"
    )
    interest_expense_non_operating: float | None = Field(
        None, alias="Interest Expense Non Operating", description="Interest expense non operating"
    )
    interest_income_non_operating: float | None = Field(
        None, alias="Interest Income Non Operating", description="Interest income non operating"
    )
    operating_income: float | None = Field(None, alias="Operating Income", description="Operating income")
    operating_expense: float | None = Field(None, alias="Operating Expense", description="Operating expense")
    research_and_development: float | None = Field(
        None, alias="Research And Development", description="Research and development"
    )
    selling_general_and_administration: float | None = Field(
        None, alias="Selling General And Administration", description="Selling general and administration"
    )
    selling_and_marketing_expense: float | None = Field(
        None, alias="Selling And Marketing Expense", description="Selling and marketing expense"
    )
    general_and_administrative_expense: float | None = Field(
        None, alias="General And Administrative Expense", description="General and administrative expense"
    )
    other_gand_a: float | None = Field(None, alias="Other Gand A", description="Other G&A")
    gross_profit: float | None = Field(None, alias="Gross Profit", description="Gross profit")
    cost_of_revenue: float | None = Field(None, alias="Cost Of Revenue", description="Cost of revenue")
    total_revenue: float | None = Field(None, alias="Total Revenue", description="Total revenue")
    operating_revenue: float | None = Field(None, alias="Operating Revenue", description="Operating revenue")


class IncomeStatementEntry(BaseModel):
    """Schema for a single income statement entry for a ticker."""

    date: datetime = Field(..., description="Date of the income statement entry", alias="index")
    total_revenue: float | None = Field(None, description="Total revenue", alias="TotalRevenue")
    cost_of_revenue: float | None = Field(None, description="Cost of revenue", alias="CostOfRevenue")
    gross_profit: float | None = Field(None, description="Gross profit", alias="GrossProfit")
    research_development: float | None = Field(
        None, description="Research and development expenses", alias="ResearchDevelopment"
    )
    selling_general_administrative: float | None = Field(
        None, description="Selling, general and administrative expenses", alias="SellingGeneralAdministrative"
    )
    non_recurring: float | None = Field(None, description="Non-recurring items", alias="NonRecurring")
    other_operating_expenses: float | None = Field(
        None, description="Other operating expenses", alias="OtherOperatingExpenses"
    )
    total_operating_expenses: float | None = Field(
        None, description="Total operating expenses", alias="TotalOperatingExpenses"
    )
    operating_income_or_loss: float | None = Field(
        None, description="Operating income or loss", alias="OperatingIncomeOrLoss"
    )
    total_other_income_expense_net: float | None = Field(
        None, description="Total other income/expense net", alias="TotalOtherIncomeExpenseNet"
    )
    earnings_before_interest_and_taxes: float | None = Field(
        None, description="Earnings before interest and taxes (EBIT)", alias="EarningsBeforeInterestAndTaxes"
    )
    interest_expense: float | None = Field(None, description="Interest expense", alias="InterestExpense")
    income_before_tax: float | None = Field(None, description="Income before tax", alias="IncomeBeforeTax")
    income_tax_expense: float | None = Field(None, description="Income tax expense", alias="IncomeTaxExpense")
    net_income_from_continuing_ops: float | None = Field(
        None, description="Net income from continuing operations", alias="NetIncomeFromContinuingOps"
    )
    net_income_applicable_to_common_shares: float | None = Field(
        None, description="Net income applicable to common shares", alias="NetIncomeApplicableToCommonShares"
    )


class BalanceSheetEntry(BaseModel):
    """Schema for a single balance sheet entry for a ticker."""

    date: datetime = Field(..., description="Date of the balance sheet entry", alias="index")
    ordinary_shares_number: float | None = Field(
        None, description="Number of ordinary shares", alias="OrdinarySharesNumber"
    )
    share_issued: float | None = Field(None, description="Shares issued", alias="ShareIssued")
    net_debt: float | None = Field(None, description="Net debt", alias="NetDebt")
    total_debt: float | None = Field(None, description="Total debt", alias="TotalDebt")
    tangible_book_value: float | None = Field(None, description="Tangible book value", alias="TangibleBookValue")
    invested_capital: float | None = Field(None, description="Invested capital", alias="InvestedCapital")
    working_capital: float | None = Field(None, description="Working capital", alias="WorkingCapital")
    net_tangible_assets: float | None = Field(None, description="Net tangible assets", alias="NetTangibleAssets")
    capital_lease_obligations: float | None = Field(
        None, description="Capital lease obligations", alias="CapitalLeaseObligations"
    )
    common_stock_equity: float | None = Field(None, description="Common stock equity", alias="CommonStockEquity")
    total_capitalization: float | None = Field(None, description="Total capitalization", alias="TotalCapitalization")
    total_equity_gross_minority_interest: float | None = Field(
        None, description="Total equity gross minority interest", alias="TotalEquityGrossMinorityInterest"
    )
    stockholders_equity: float | None = Field(None, description="Stockholders' equity", alias="StockholdersEquity")
    gains_losses_not_affecting_retained_earnings: float | None = Field(
        None,
        description="Gains/losses not affecting retained earnings",
        alias="GainsLossesNotAffectingRetainedEarnings",
    )
    other_equity_adjustments: float | None = Field(
        None, description="Other equity adjustments", alias="OtherEquityAdjustments"
    )
    retained_earnings: float | None = Field(None, description="Retained earnings", alias="RetainedEarnings")
    capital_stock: float | None = Field(None, description="Capital stock", alias="CapitalStock")
    common_stock: float | None = Field(None, description="Common stock", alias="CommonStock")
    total_liabilities_net_minority_interest: float | None = Field(
        None, description="Total liabilities net minority interest", alias="TotalLiabilitiesNetMinorityInterest"
    )
    total_non_current_liabilities_net_minority_interest: float | None = Field(
        None,
        description="Total non-current liabilities net minority interest",
        alias="TotalNonCurrentLiabilitiesNetMinorityInterest",
    )
    other_non_current_liabilities: float | None = Field(
        None, description="Other non-current liabilities", alias="OtherNonCurrentLiabilities"
    )
    trade_and_other_payables_non_current: float | None = Field(
        None, description="Trade and other payables (non-current)", alias="TradeandOtherPayablesNonCurrent"
    )
    non_current_deferred_liabilities: float | None = Field(
        None, description="Non-current deferred liabilities", alias="NonCurrentDeferredLiabilities"
    )
    non_current_deferred_revenue: float | None = Field(
        None, description="Non-current deferred revenue", alias="NonCurrentDeferredRevenue"
    )
    non_current_deferred_taxes_liabilities: float | None = Field(
        None, description="Non-current deferred taxes liabilities", alias="NonCurrentDeferredTaxesLiabilities"
    )
    long_term_debt_and_capital_lease_obligation: float | None = Field(
        None, description="Long-term debt and capital lease obligation", alias="LongTermDebtAndCapitalLeaseObligation"
    )
    long_term_capital_lease_obligation: float | None = Field(
        None, description="Long-term capital lease obligation", alias="LongTermCapitalLeaseObligation"
    )
    long_term_debt: float | None = Field(None, description="Long-term debt", alias="LongTermDebt")
    current_liabilities: float | None = Field(None, description="Current liabilities", alias="CurrentLiabilities")
    other_current_liabilities: float | None = Field(
        None, description="Other current liabilities", alias="OtherCurrentLiabilities"
    )
    current_deferred_liabilities: float | None = Field(
        None, description="Current deferred liabilities", alias="CurrentDeferredLiabilities"
    )
    current_deferred_revenue: float | None = Field(
        None, description="Current deferred revenue", alias="CurrentDeferredRevenue"
    )
    current_debt_and_capital_lease_obligation: float | None = Field(
        None, description="Current debt and capital lease obligation", alias="CurrentDebtAndCapitalLeaseObligation"
    )
    current_debt: float | None = Field(None, description="Current debt", alias="CurrentDebt")
    other_current_borrowings: float | None = Field(
        None, description="Other current borrowings", alias="OtherCurrentBorrowings"
    )
    commercial_paper: float | None = Field(None, description="Commercial paper", alias="CommercialPaper")
    pension_and_other_post_retirement_benefit_plans_current: float | None = Field(
        None,
        description="Pension and other post-retirement benefit plans (current)",
        alias="PensionandOtherPostRetirementBenefitPlansCurrent",
    )
    payables_and_accrued_expenses: float | None = Field(
        None, description="Payables and accrued expenses", alias="PayablesAndAccruedExpenses"
    )
    payables: float | None = Field(None, description="Payables", alias="Payables")
    total_tax_payable: float | None = Field(None, description="Total tax payable", alias="TotalTaxPayable")
    income_tax_payable: float | None = Field(None, description="Income tax payable", alias="IncomeTaxPayable")
    accounts_payable: float | None = Field(None, description="Accounts payable", alias="AccountsPayable")
    total_assets: float | None = Field(None, description="Total assets", alias="TotalAssets")
    total_non_current_assets: float | None = Field(
        None, description="Total non-current assets", alias="TotalNonCurrentAssets"
    )
    other_non_current_assets: float | None = Field(
        None, description="Other non-current assets", alias="OtherNonCurrentAssets"
    )
    financial_assets: float | None = Field(None, description="Financial assets", alias="FinancialAssets")
    investments_and_advances: float | None = Field(
        None, description="Investments and advances", alias="InvestmentsAndAdvances"
    )
    investment_in_financial_assets: float | None = Field(
        None, description="Investment in financial assets", alias="InvestmentinFinancialAssets"
    )
    available_for_sale_securities: float | None = Field(
        None, description="Available-for-sale securities", alias="AvailableForSaleSecurities"
    )
    long_term_equity_investment: float | None = Field(
        None, description="Long-term equity investment", alias="LongTermEquityInvestment"
    )
    goodwill_and_other_intangible_assets: float | None = Field(
        None, description="Goodwill and other intangible assets", alias="GoodwillAndOtherIntangibleAssets"
    )
    other_intangible_assets: float | None = Field(
        None, description="Other intangible assets", alias="OtherIntangibleAssets"
    )
    goodwill: float | None = Field(None, description="Goodwill", alias="Goodwill")
    net_ppe: float | None = Field(None, description="Net property, plant, and equipment (PPE)", alias="NetPPE")
    accumulated_depreciation: float | None = Field(
        None, description="Accumulated depreciation", alias="AccumulatedDepreciation"
    )
    gross_ppe: float | None = Field(None, description="Gross property, plant, and equipment (PPE)", alias="GrossPPE")
    leases: float | None = Field(None, description="Leases", alias="Leases")
    other_properties: float | None = Field(None, description="Other properties", alias="OtherProperties")
    machinery_furniture_equipment: float | None = Field(
        None, description="Machinery, furniture, and equipment", alias="MachineryFurnitureEquipment"
    )
    buildings_and_improvements: float | None = Field(
        None, description="Buildings and improvements", alias="BuildingsAndImprovements"
    )
    land_and_improvements: float | None = Field(None, description="Land and improvements", alias="LandAndImprovements")
    properties: float | None = Field(None, description="Properties", alias="Properties")
    current_assets: float | None = Field(None, description="Current assets", alias="CurrentAssets")
    other_current_assets: float | None = Field(None, description="Other current assets", alias="OtherCurrentAssets")
    hedging_assets_current: float | None = Field(
        None, description="Hedging assets (current)", alias="HedgingAssetsCurrent"
    )
    inventory: float | None = Field(None, description="Inventory", alias="Inventory")
    finished_goods: float | None = Field(None, description="Finished goods", alias="FinishedGoods")
    work_in_process: float | None = Field(None, description="Work in process", alias="WorkInProcess")
    raw_materials: float | None = Field(None, description="Raw materials", alias="RawMaterials")
    receivables: float | None = Field(None, description="Receivables", alias="Receivables")
    accounts_receivable: float | None = Field(None, description="Accounts receivable", alias="AccountsReceivable")
    allowance_for_doubtful_accounts_receivable: float | None = Field(
        None, description="Allowance for doubtful accounts receivable", alias="AllowanceForDoubtfulAccountsReceivable"
    )
    gross_accounts_receivable: float | None = Field(
        None, description="Gross accounts receivable", alias="GrossAccountsReceivable"
    )
    cash_cash_equivalents_and_short_term_investments: float | None = Field(
        None,
        description="Cash, cash equivalents, and short-term investments",
        alias="CashCashEquivalentsAndShortTermInvestments",
    )
    other_short_term_investments: float | None = Field(
        None, description="Other short-term investments", alias="OtherShortTermInvestments"
    )
    cash_and_cash_equivalents: float | None = Field(
        None, description="Cash and cash equivalents", alias="CashAndCashEquivalents"
    )
    cash_equivalents: float | None = Field(None, description="Cash equivalents", alias="CashEquivalents")
    cash_financial: float | None = Field(None, description="Cash (financial)", alias="CashFinancial")


class EPSHistoryEntry(BaseModel):
    """Schema for ticker earnings dates data."""

    earnings_date: datetime | None = Field(None, description="Earnings date", alias="Earnings Date")
    eps_estimate: float | None = Field(None, description="Earnings per share estimate", alias="EPS Estimate")
    reported_eps: float | None = Field(None, description="Reported earnings per share", alias="Reported EPS")
    surprise_pst: float | None = Field(None, description="Earnings surprise percentage", alias="Surprise(%)")

    @field_validator("earnings_date", mode="before")
    @classmethod
    def coerce_date_to_timestamp(cls, v):
        """Coerce date fields to pd.Timestamp."""
        if isinstance(v, pd.Timestamp):
            return v.to_pydatetime()
        return v
