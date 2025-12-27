"""
SBS Contract Intelligence - Enterprise Data Models
Version 3.0 - DACH-fokussiert mit deutscher Rechtskonformität
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class ContractType(str, Enum):
    EMPLOYMENT = "employment"
    SAAS = "saas"
    NDA = "nda"
    VENDOR = "vendor"
    LEASE_COMMERCIAL = "lease_commercial"
    LEASE_RESIDENTIAL = "lease_residential"
    LICENSE = "license"
    MSA = "msa"
    SERVICE = "service"
    AGENCY = "agency"
    FRANCHISE = "franchise"
    PARTNERSHIP = "partnership"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class LegalValidity(str, Enum):
    VALID = "valid"
    POTENTIALLY_INVALID = "potentially_invalid"
    INVALID = "invalid"
    REQUIRES_REVIEW = "requires_review"


class ClauseCategory(str, Enum):
    PROBATION = "probation"
    TERMINATION_NOTICE = "termination_notice"
    NON_COMPETE = "non_compete"
    OVERTIME = "overtime"
    SALARY = "salary"
    BONUS = "bonus"
    VACATION = "vacation"
    WORKING_HOURS = "working_hours"
    CONFIDENTIALITY = "confidentiality"
    IP_RIGHTS = "ip_rights"
    EXCLUSION_PERIOD = "exclusion_period"
    FIXED_TERM = "fixed_term"
    SLA = "sla"
    DATA_PROTECTION = "data_protection"
    LIABILITY_CAP = "liability_cap"
    TERMINATION = "termination"
    AUTO_RENEWAL = "auto_renewal"
    PRICE_ADJUSTMENT = "price_adjustment"
    VENDOR_LOCK_IN = "vendor_lock_in"
    DURATION = "duration"
    SCOPE = "scope"
    PENALTY = "penalty"
    INDEMNIFICATION = "indemnification"
    PENALTIES = "penalties"
    OTHER = "other"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class Party(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    address: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None


class Compensation(BaseModel):
    base_salary_gross: Optional[Decimal] = None
    payment_frequency: Optional[str] = None
    bonus_target: Optional[Decimal] = None
    bonus_guaranteed: bool = False
    thirteenth_salary: bool = False
    fourteenth_salary: bool = False
    christmas_bonus: Optional[Decimal] = None
    vacation_bonus: Optional[Decimal] = None
    company_car: bool = False
    company_car_private_use: bool = False
    pension_contribution: Optional[Decimal] = None
    salary_review_clause: Optional[str] = None


class WorkingConditions(BaseModel):
    weekly_hours: Optional[float] = None
    work_location: Optional[str] = None
    home_office_allowed: bool = False
    home_office_days: Optional[int] = None
    overtime_clause: Optional[str] = None
    overtime_included_in_salary: bool = False
    overtime_cap_hours: Optional[float] = None
    flextime: bool = False
    trust_based_hours: bool = False


class VacationTerms(BaseModel):
    days_per_year: Optional[int] = None
    additional_days: Optional[int] = None
    carryover_allowed: bool = True
    carryover_deadline: Optional[str] = None


class ProbationTerms(BaseModel):
    duration_months: Optional[float] = None
    notice_period_during_probation: Optional[str] = None
    exceeds_legal_maximum: bool = False


class TerminationTerms(BaseModel):
    notice_period_employee: Optional[str] = None
    notice_period_employer: Optional[str] = None
    fixed_term: bool = False
    end_date: Optional[date] = None
    fixed_term_reason: Optional[str] = None
    fixed_term_without_reason: bool = False
    severance_clause: Optional[str] = None


class NonCompeteTerms(BaseModel):
    during_employment: bool = False
    post_employment: bool = False
    duration_months: Optional[int] = None
    geographic_scope: Optional[str] = None
    activity_scope: Optional[str] = None
    compensation_clause: Optional[str] = None
    compensation_percentage: Optional[float] = None
    has_adequate_compensation: bool = False
    missing_compensation: bool = False


class ConfidentialityTerms(BaseModel):
    confidentiality_clause: bool = False
    duration: Optional[str] = None
    ip_assignment: bool = False
    invention_assignment: bool = False


class EmploymentContractData(BaseModel):
    employer: Optional[Party] = None
    employee: Optional[Party] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    department: Optional[str] = None
    reporting_to: Optional[str] = None
    start_date: Optional[date] = None
    contract_date: Optional[date] = None
    compensation: Optional[Compensation] = None
    working_conditions: Optional[WorkingConditions] = None
    vacation: Optional[VacationTerms] = None
    probation: Optional[ProbationTerms] = None
    termination: Optional[TerminationTerms] = None
    non_compete: Optional[NonCompeteTerms] = None
    confidentiality: Optional[ConfidentialityTerms] = None
    collective_agreement: Optional[str] = None
    jurisdiction: Optional[str] = None
    exclusion_period_clause: Optional[str] = None
    exclusion_period_months: Optional[int] = None
    penalty_clause: Optional[str] = None
    penalty_amount: Optional[Decimal] = None


class ClauseRisk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clause_category: ClauseCategory
    clause_text: str
    section_reference: Optional[str] = None
    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    legal_validity: LegalValidity
    issü_title: str
    issü_description: str
    legal_basis: str
    recommendation: str
    alternative_wording: Optional[str] = None
    market_comparison: Optional[str] = None


class RiskCategory(BaseModel):
    category: str
    weight: float
    score: int
    max_score: int = 100
    issues_count: int = 0
    critical_issues: int = 0


class ContractRiskAssessment(BaseModel):
    overall_risk_score: int = Field(..., ge=0, le=100)
    overall_risk_level: RiskLevel
    legal_compliance_score: int = Field(..., ge=0, le=100)
    financial_risk_score: int = Field(..., ge=0, le=100)
    operational_risk_score: int = Field(..., ge=0, le=100)
    data_protection_score: int = Field(..., ge=0, le=100)
    contract_management_score: int = Field(..., ge=0, le=100)
    risk_categories: List[RiskCategory] = []
    critical_risks: List[ClauseRisk] = []
    high_risks: List[ClauseRisk] = []
    medium_risks: List[ClauseRisk] = []
    low_risks: List[ClauseRisk] = []
    missing_clauses: List[str] = Field(default_factory=list)
    recommended_additions: List[str] = Field(default_factory=list)
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(..., ge=0, le=1)


class ContractUploadResponse(BaseModel):
    contract_id: str
    filename: str
    contract_type: ContractType
    status: str = "uploaded"
    message: str


class DashboardSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    expiring_soon: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_contract_value: Decimal
    avg_risk_score: float
    contracts_this_month: int
    risk_trend: str


# =============================================================================
# NDA CONTRACT MODELS
# =============================================================================

class NDAType(str, Enum):
    """NDA-Typen"""
    UNILATERAL = "unilateral"  # Einseitig
    MUTUAL = "mutual"  # Gegenseitig
    MULTILATERAL = "multilateral"  # Mehrparteien


class NDAContractData(BaseModel):
    """Vollständige NDA-Datenstruktur"""
    disclosing_party: Optional[Party] = None
    receiving_party: Optional[Party] = None
    nda_type: Optional[NDAType] = None
    purpose: Optional[str] = None
    definition_confidential: Optional[str] = None
    exclusions: List[str] = Field(default_factory=list)
    duration_years: Optional[int] = None
    duration_indefinite: bool = False
    permitted_disclosures: List[str] = Field(default_factory=list)
    return_of_information: bool = False
    destruction_of_information: bool = False
    injunctive_relief: bool = False
    penalty_clause: Optional[str] = None
    penalty_amount: Optional[Decimal] = None
    jurisdiction: Optional[str] = None
    governing_law: Optional[str] = None


# =============================================================================
# VENDOR CONTRACT MODELS
# =============================================================================

class VendorContractData(BaseModel):
    """Lieferantenvertrag Datenstruktur"""
    supplier: Optional[Party] = None
    buyer: Optional[Party] = None
    contract_subject: Optional[str] = None
    delivery_terms: Optional[str] = None  # z.B. "DDP Frankfurt"
    payment_terms: Optional[str] = None  # z.B. "30 Tage netto"
    warranty_months: Optional[int] = None
    liability_cap: Optional[str] = None
    quality_requirements: Optional[str] = None
    audit_rights: bool = False
    termination_notice_days: Optional[int] = None
    exclusivity: bool = False
    minimum_order_value: Optional[Decimal] = None
    price_adjustment_clause: Optional[str] = None
