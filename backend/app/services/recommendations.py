import uuid
from typing import List, Optional
from ..schemas.audit import Recommendation, PriorityLevel, ClaimAudit, MatchStatus, ClaimCategory, ScoreBreakdown
from .extraction import ExtractedPageData

def generate_recommendations(
    claims: List[ClaimAudit],
    breakdown: Optional[ScoreBreakdown],
    page_data: ExtractedPageData
) -> List[Recommendation]:
    """
    Generates structured, actionable recommendations prioritized by business impact.
    """
    recommendations: List[Recommendation] = []
    rec_counter = 1

    # 1. Contradictions (HIGH Priority)
    for c in claims:
        if c.status == MatchStatus.CONTRADICTED:
            recommendations.append(Recommendation(
                id=f"REC-{rec_counter:02d}",
                priority=PriorityLevel.HIGH,
                category="Factual Conflict",
                issue=f"Ad claim '{c.claim_text}' is contradicted by landing page content.",
                impact="Leads to immediate user bounce, brand distrust, and lower Quality Score.",
                recommended_fix="Immediately align the landing page terms with the ad claim or remove the claim from the ad copy.",
                suggested_ad_copy=f"Update ad copy to reflect real terms: {c.evidence_quote or 'Updated offer terms'}",
                suggested_page_copy=f"If the ad claim is true, prominently state: '{c.claim_text}' on the landing page."
            ))
            rec_counter += 1

    # 2. Headline Alignment (HIGH Priority if < 70)
    headline_claims = [c for c in claims if c.source_part == "headline"]
    if breakdown and breakdown.headline_hero_alignment < 70.0:
        headline_text = headline_claims[0].claim_text if headline_claims else "Ad Headline"
        page_h1 = page_data.headings_h1[0] if page_data.headings_h1 else (page_data.title or "Landing Page Title")
        recommendations.append(Recommendation(
            id=f"REC-{rec_counter:02d}",
            priority=PriorityLevel.HIGH,
            category="Headline-to-Hero Continuity",
            issue=f"Ad headline '{headline_text}' does not match page headline '{page_h1}'.",
            impact="Users who click expect instant visual confirmation. Weak message match causes up to 40% bounce rate.",
            recommended_fix="Mirror the core promise and keywords from the ad headline into the H1 or hero subhead.",
            suggested_ad_copy=f"Align ad headline: '{page_h1[:50]}...'",
            suggested_page_copy=f"Change landing page H1 to: '{headline_text}'"
        ))
        rec_counter += 1

    # 3. CTA Misalignment (MEDIUM Priority if < 70)
    cta_claims = [c for c in claims if c.source_part == "cta" or c.category == ClaimCategory.CTA_ACTION]
    if cta_claims and any(c.status in (MatchStatus.NOT_FOUND, MatchStatus.PARTIAL_MATCH) for c in cta_claims):
        cta_claim = next(c for c in cta_claims if c.status in (MatchStatus.NOT_FOUND, MatchStatus.PARTIAL_MATCH))
        lp_ctas = ", ".join(f"'{btn}'" for btn in page_data.detected_ctas[:2]) if page_data.detected_ctas else "None found"
        recommendations.append(Recommendation(
            id=f"REC-{rec_counter:02d}",
            priority=PriorityLevel.MEDIUM,
            category="Call-to-Action Friction",
            issue=f"Ad CTA promises '{cta_claim.claim_text}', but landing page buttons feature {lp_ctas}.",
            impact="Conversion dropoff occurs when visitors must guess what action to take next.",
            recommended_fix="Ensure the primary above-the-fold button text exactly mirrors the ad CTA copy.",
            suggested_ad_copy=f"Match button action: '{page_data.detected_ctas[0]}'" if page_data.detected_ctas else None,
            suggested_page_copy=f"Rename primary button to: '{cta_claim.claim_text}'"
        ))
        rec_counter += 1

    # 4. Missing Offer / Pricing Proof (HIGH / MEDIUM Priority)
    missing_offers = [c for c in claims if c.category == ClaimCategory.OFFER_PRICING and c.status == MatchStatus.NOT_FOUND]
    for mo in missing_offers:
        recommendations.append(Recommendation(
            id=f"REC-{rec_counter:02d}",
            priority=PriorityLevel.MEDIUM,
            category="Unverified Offer",
            issue=f"Ad promotes offer '{mo.claim_text}', but it is nowhere to be found on the landing page.",
            impact="Visitors searching for this incentive feel misled and leave without converting.",
            recommended_fix="Place a banner or badge in the hero section displaying this specific promotion.",
            suggested_ad_copy=None,
            suggested_page_copy=f"Hero Banner: '{mo.claim_text} - Available for a limited time.'"
        ))
        rec_counter += 1

    # 5. Missing Social Proof or Trust Claims (LOW Priority)
    missing_trust = [c for c in claims if c.category == ClaimCategory.TRUST_PROOF and c.status == MatchStatus.NOT_FOUND]
    for mt in missing_trust:
        recommendations.append(Recommendation(
            id=f"REC-{rec_counter:02d}",
            priority=PriorityLevel.LOW,
            category="Trust Deficit",
            issue=f"Ad mentions trust credential '{mt.claim_text}', but landing page lacks corresponding proof.",
            impact="Lower credibility on first-time visitors.",
            recommended_fix="Add trust badges, star ratings, or customer logos directly under the hero CTA.",
            suggested_ad_copy=None,
            suggested_page_copy=f"Add testimonial or badge section citing: '{mt.claim_text}'"
        ))
        rec_counter += 1

    return recommendations
