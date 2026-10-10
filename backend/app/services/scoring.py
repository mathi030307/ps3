from typing import List, Optional, Tuple, Dict
from ..schemas.audit import (
    ClaimAudit,
    MatchStatus,
    ClaimCategory,
    ScoreBreakdown,
    ClaimContribution,
    CtaComparison
)
from .extraction import ExtractedPageData

STATUS_BASE_VALUES: Dict[MatchStatus, float] = {
    MatchStatus.SUPPORTED: 1.0,
    MatchStatus.PARTIAL_MATCH: 0.5,
    MatchStatus.UNCERTAIN: 0.25,
    MatchStatus.NOT_FOUND: 0.0,
    MatchStatus.CONTRADICTED: -0.5,
}

FORMULA_TEXT = (
    "Score = [max(0, Sum(Status_Value_i * Weight_i)) / Sum(Max_Points_i)] * 100 - Penalties. "
    "Material claims (Offer / Pricing, Headline) are weighted at 2.0x, others 1.0x. "
    "Status values: Supported=1.0, Partial=0.5, Uncertain=0.25, Not Found=0.0, Contradicted=-0.5. "
    "Hard Cap: Overall score is strictly capped at 40.0 if any claim is Contradicted."
)

def calculate_score(
    claims: List[ClaimAudit],
    page_data: Optional[ExtractedPageData],
    cta_analysis: Optional[CtaComparison] = None
) -> Tuple[Optional[float], Optional[str], Optional[str], Optional[ScoreBreakdown]]:
    """
    Computes an explainable 0–100 score strictly according to the documented formula:
    - Status values: Supported=1.0, Partial=0.5, Uncertain=0.25, Not Found=0.0, Contradicted=-0.5
    - Material claims weight = 2.0 (Offer/Pricing or Headline), Standard = 1.0
    - Contradiction penalty: -15 pts per contradicted claim
    - CTA friction penalty: -10 pts if CTA friction detected
    - Hard Cap 40: Score cannot exceed 40 if any claim is Contradicted.
    - Rule 4: Score is null (unavailable) when analysis cannot complete; distinct from 0.0.
    """
    if not claims or page_data is None or not page_data.normalized_text:
        return None, None, "Analysis incomplete. Unable to compute score.", None

    total_weighted_points = 0.0
    total_max_points = 0.0
    claim_contributions: List[ClaimContribution] = []

    contradicted_count = 0

    for c in claims:
        # Determine weight: Material (Offer/Pricing or Headline) = 2.0, others = 1.0
        is_material = (c.category == ClaimCategory.OFFER_PRICING or c.source_part == "headline")
        weight = 2.0 if is_material else 1.0

        base_val = STATUS_BASE_VALUES.get(c.status, 0.0)
        if c.status == MatchStatus.CONTRADICTED:
            contradicted_count += 1

        weighted_pts = base_val * weight
        max_pts = 1.0 * weight

        total_weighted_points += weighted_pts
        total_max_points += max_pts

        claim_contributions.append(ClaimContribution(
            claim_id=c.claim_id,
            claim_text=c.claim_text,
            source_part=c.source_part,
            category=c.category,
            status=c.status,
            base_value=base_val,
            weight=weight,
            weighted_points=round(weighted_pts, 2),
            max_possible_points=round(max_pts, 2),
            contribution_percent=0.0  # calculated after total_max_points
        ))

    # Calculate contribution percentage relative to total potential points
    if total_max_points > 0:
        for contrib in claim_contributions:
            contrib.contribution_percent = round((contrib.weighted_points / total_max_points) * 100, 1)

    # Base score percentage (clamped at 0 minimum before penalties)
    base_score = (max(0.0, total_weighted_points) / total_max_points) * 100 if total_max_points > 0 else 0.0

    # Penalties
    contradiction_penalty = contradicted_count * 15.0
    cta_penalty = 10.0 if (cta_analysis and cta_analysis.friction_detected) else 0.0
    total_penalties = contradiction_penalty + cta_penalty

    raw_score = base_score - total_penalties

    # Hard Cap 40: if any contradicted claim exists, score is capped at 40
    is_capped = (contradicted_count > 0)
    if is_capped:
        final_score = min(40.0, max(0.0, raw_score))
    else:
        final_score = max(0.0, min(100.0, raw_score))

    final_score = round(final_score, 1)

    # Dimensional Alignment sub-metrics for breakdown
    headline_claims = [c for c in claims if c.source_part == "headline"]
    headline_score = sum(c.similarity_score for c in headline_claims) / len(headline_claims) if headline_claims else 50.0

    cta_score = cta_analysis.similarity_score if cta_analysis else (
        70.0 if len(page_data.detected_ctas) > 0 else 30.0
    )

    supported_or_partial = sum(1 for c in claims if c.status in (MatchStatus.SUPPORTED, MatchStatus.PARTIAL_MATCH))
    claim_coverage_rate = (supported_or_partial / len(claims)) * 100 if claims else 0.0

    offer_claims = [c for c in claims if c.category == ClaimCategory.OFFER_PRICING]
    if offer_claims:
        offer_score = sum(100.0 if oc.status == MatchStatus.SUPPORTED else (50.0 if oc.status == MatchStatus.PARTIAL_MATCH else 0.0) for oc in offer_claims) / len(offer_claims)
    else:
        offer_score = (headline_score + claim_coverage_rate) / 2.0

    # Grade (Presentation Aid derived from score)
    if final_score >= 90.0:
        grade = "A"
        verdict = "Excellent Message Match: Strong, verified alignment across headline, offer, and CTA."
    elif final_score >= 80.0:
        grade = "B"
        verdict = "Good Message Match: Core promises verified with minor phrasing or nuance differences."
    elif final_score >= 65.0:
        grade = "C"
        verdict = "Moderate Alignment: Noticeable message gaps or missing secondary claims."
    elif final_score >= 45.0:
        grade = "D"
        verdict = "Weak Message Match: High bounce risk; material offers or CTAs are unconfirmed."
    else:
        grade = "F"
        verdict = "Critical Mismatch: Page explicitly contradicts ad promises or lacks key claims."

    breakdown = ScoreBreakdown(
        headline_hero_alignment=round(headline_score, 1),
        cta_alignment=round(cta_score, 1),
        claim_coverage_rate=round(claim_coverage_rate, 1),
        offer_consistency=round(offer_score, 1),
        contradiction_penalty=round(total_penalties, 1),
        is_capped_at_40=is_capped,
        formula_text=FORMULA_TEXT,
        presentation_aid_label="Presentation aid derived from score",
        claim_contributions=claim_contributions
    )

    return final_score, grade, verdict, breakdown
