from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MatchStatus(str, Enum):
    SUPPORTED = "Supported"
    PARTIAL_MATCH = "Partial Match"
    NOT_FOUND = "Not Found"
    CONTRADICTED = "Contradicted"
    UNCERTAIN = "Uncertain"

class ClaimCategory(str, Enum):
    OFFER_PRICING = "Offer / Pricing"
    FEATURE_BENEFIT = "Feature / Benefit"
    CTA_ACTION = "Call to Action"
    TRUST_PROOF = "Social Proof / Trust"
    AUDIENCE_SCOPE = "Audience / Scope"

class PriorityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AdInput(BaseModel):
    headline: str = Field(..., min_length=2, max_length=500, description="Ad Headline")
    description: str = Field(..., min_length=2, max_length=2000, description="Ad Body / Description")
    cta: Optional[str] = Field(None, max_length=200, description="Optional Ad Call to Action")

class AuditRequest(BaseModel):
    ad: AdInput
    url: Optional[str] = Field(None, description="Landing page live URL")
    html_content: Optional[str] = Field(None, description="Direct HTML snapshot content")
    is_synthetic_demo: bool = Field(False, description="Whether this request is a preset demo run")

class ClaimContribution(BaseModel):
    claim_id: str
    claim_text: str
    source_part: str
    category: ClaimCategory
    status: MatchStatus
    base_value: float  # Supported=1.0, Partial=0.5, Uncertain=0.25, NotFound=0.0, Contradicted=-0.5
    weight: float      # Material=2.0, Standard=1.0
    weighted_points: float
    max_possible_points: float
    contribution_percent: float

class CtaComparison(BaseModel):
    ad_cta: Optional[str] = None
    page_primary_cta: Optional[str] = None
    all_page_ctas: List[str] = []
    match_status: MatchStatus
    similarity_score: float
    friction_detected: bool
    friction_notes: str

class ScoreBreakdown(BaseModel):
    headline_hero_alignment: float  # 0 to 100
    cta_alignment: float            # 0 to 100
    claim_coverage_rate: float      # 0 to 100
    offer_consistency: float        # 0 to 100
    contradiction_penalty: float    # points deducted
    is_capped_at_40: bool = False
    formula_text: str
    presentation_aid_label: str = "Presentation aid derived from score"
    claim_contributions: List[ClaimContribution] = []

class EvidenceQuote(BaseModel):
    quote_text: str
    is_verified: bool
    source_element: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    surrounding_context: Optional[str] = None

class ClaimAudit(BaseModel):
    claim_id: str
    source_part: str  # "headline", "description", or "cta"
    category: ClaimCategory
    claim_text: str
    status: MatchStatus
    similarity_score: float  # 0.0 to 100.0
    evidence_quote: Optional[str] = None
    is_quote_verified: bool = False
    quote_source_element: Optional[str] = None
    status_reason: str
    suggested_action: str

class Recommendation(BaseModel):
    id: str
    priority: PriorityLevel
    category: str
    issue: str
    impact: str
    recommended_fix: str
    suggested_ad_copy: Optional[str] = None
    suggested_page_copy: Optional[str] = None

class PageExtractionSummary(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    headings_h1: List[str] = []
    headings_h2_h3: List[str] = []
    hero_text: Optional[str] = None
    detected_ctas: List[str] = []
    footer_disclosures: List[str] = []
    word_count: int = 0
    reading_time_minutes: float = 0.0
    text_length: int = 0

class AuditResponse(BaseModel):
    success: bool
    is_synthetic_demo: bool = False
    demo_badge: Optional[str] = None  # Always "Synthetic example" if synthetic
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: str = ""
    source_description: str = ""
    
    # Core results (null when analysis cannot complete - Rule 4)
    overall_score: Optional[float] = None
    grade: Optional[str] = None
    presentation_aid_note: Optional[str] = None
    summary_verdict: Optional[str] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    cta_analysis: Optional[CtaComparison] = None
    
    # Counts
    total_claims: int = 0
    supported_count: int = 0
    partial_count: int = 0
    not_found_count: int = 0
    contradicted_count: int = 0
    uncertain_count: int = 0
    
    # Detailed data
    claims: List[ClaimAudit] = []
    recommendations: List[Recommendation] = []
    page_summary: Optional[PageExtractionSummary] = None

class SyntheticScenario(BaseModel):
    id: str
    name: str
    label: str = "Synthetic example"
    category: str
    mismatch_description: str
    ad: AdInput
    html_file_path: Optional[str] = None
    simulated_error: Optional[str] = None
