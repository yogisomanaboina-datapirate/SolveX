from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class PolicyInfo(BaseModel):
    """Insurance policy details supplied by Backend/User."""
    policy_id: str = Field(description="Insurance policy identification number", examples=["POL-99281"])
    provider_name: str = Field(description="Insurance provider name", examples=["Star Health Insurance"])
    policy_type: str = Field(default="COMPREHENSIVE_HEALTH", description="Policy category")
    coverage_limit_inr: float = Field(default=500000.0, description="Total policy coverage limit in INR")
    copay_percentage: float = Field(default=10.0, description="Co-pay percentage required from patient")
    network_hospitals: List[str] = Field(
        default_factory=lambda: ["Apollo Emergency Hospital Jubilee Hills", "KIMS Secunderabad"],
        description="Cashless network hospital names"
    )
    pre_authorization_required: bool = Field(default=True, description="Whether pre-authorization is required for emergency admission")


class ExistingClaimData(BaseModel):
    """Claim record retrieved from Backend database (Source of Truth)."""
    claim_id: str = Field(description="Claim reference ID", examples=["CLM-4401"])
    policy_id: str = Field(description="Associated policy ID", examples=["POL-99281"])
    hospital_name: str = Field(description="Hospital where treatment was provided")
    treatment_type: str = Field(description="Medical treatment or emergency category")
    claim_amount_inr: float = Field(description="Requested claim amount in INR")
    status: str = Field(
        description="Claim current status: SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED",
        examples=["UNDER_REVIEW"]
    )
    submission_date: str = Field(description="Date claim was submitted")
    approved_amount_inr: Optional[float] = Field(default=None, description="Approved reimbursement amount if processed")


class ClaimAnalysisRequest(BaseModel):
    """Insurance claim request payload received from Backend."""
    user_request: str = Field(
        description="User query or request regarding insurance claim or coverage",
        examples=["I admitted my mother to Apollo Hospital for cardiac treatment under policy POL-99281. Has a claim been filed and what coverage applies?"]
    )
    policy_info: Optional[PolicyInfo] = Field(default=None, description="Policy details if available")
    existing_claims: List[ExistingClaimData] = Field(
        default_factory=list,
        description="Backend-supplied list of user's existing claims (Source of Truth)"
    )
    document_details: Optional[Dict[str, Any]] = Field(default=None, description="Associated document details (e.g. estimated bill amount)")


class ClaimMatchResult(BaseModel):
    """Deterministic tool output for claim matching."""
    claim_exists: bool
    matched_claim_id: Optional[str] = None
    matched_claim_status: Optional[str] = None
    matched_claim_data: Optional[ExistingClaimData] = None
    match_confidence: float = 0.0
    match_explanation: str = ""


class ClaimAnalysisResponse(BaseDecisionResponse):
    """Structured Insurance & Claims AI Decision Output."""
    claim_exists: bool = Field(default=False, description="Flag indicating whether a matching claim exists in Backend source of truth")
    matched_claim_id: Optional[str] = Field(default=None, description="Matched claim ID if found")
    matched_claim_status: Optional[str] = Field(default=None, description="Status of matched claim")
    assistance_type: str = Field(
        default="NEW_CLAIM_FILING_GUIDANCE",
        description="Assistance category: EXISTING_CLAIM_STATUS, NEW_CLAIM_FILING_GUIDANCE, COVERAGE_VERIFICATION, PRE_AUTH_ASSISTANCE",
        examples=["EXISTING_CLAIM_STATUS"]
    )
    coverage_estimation: Optional[Dict[str, Any]] = Field(default=None, description="Coverage estimation calculation")
    recommended_next_step: str = Field(
        default="Consult insurance provider desk for claim submission.",
        validation_alias=AliasChoices("recommended_next_step", "next_step", "next_action"),
        description="Recommended next step for user or backend execution"
    )
    disclaimer: str = Field(
        default="Insurance analysis is provided for coordination assistance. Official claim settlement is executed by the insurance provider.",
        description="Insurance legal disclaimer"
    )
