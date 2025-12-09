from pydantic import BaseModel
from typing import List, Optional


# ---------- Arbeitsverträge ----------

class Party(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None  # "employer" | "employee"


class ExtractedEmploymentFields(BaseModel):
    parties: List[Party] = []
    start_date: Optional[str] = None  # YYYY-MM-DD
    fixed_term: bool = False
    end_date: Optional[str] = None
    probation_period_months: Optional[float] = None
    weekly_hours: Optional[float] = None
    base_salary_eur: Optional[float] = None
    vacation_days_per_year: Optional[float] = None
    notice_period_employee: Optional[str] = None
    notice_period_employer: Optional[str] = None
    non_compete_during_term: bool = False
    post_contract_non_compete: bool = False


class RiskFlag(BaseModel):
    severity: str  # "low" | "medium" | "high"
    title: str
    description: str
    clause_snippet: Optional[str] = None
    policy_reference: Optional[str] = None


class ContractAnalysisResult(BaseModel):
    contract_id: str
    contract_type: str
    language: str
    summary: str
    extracted_fields: ExtractedEmploymentFields
    risk_flags: List[RiskFlag]


# ---------- SaaS- / Dienstleistungsverträge ----------

class SaaSCoreFields(BaseModel):
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None
    contract_start_date: Optional[str] = None  # ISO-Format
    contract_end_date: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_notice_days: Optional[int] = None
    annual_contract_value_eur: Optional[float] = None
    billing_interval: Optional[str] = None  # "monthly" | "quarterly" | "annual" | None
    min_term_months: Optional[int] = None
    termination_for_convenience: Optional[bool] = None
    data_location: Optional[str] = None
    dp_addendum_included: Optional[bool] = None
    liability_cap_multiple_acv: Optional[float] = None
    uptime_sla_percent: Optional[float] = None


class SaaSContractAnalysisResult(BaseModel):
    contract_id: str
    contract_type: str
    language: str
    summary: str
    extracted_fields: SaaSCoreFields
    risk_flags: List[RiskFlag]

