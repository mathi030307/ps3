import re
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import fuzz

from ..schemas.audit import MatchStatus, ClaimAudit, ClaimCategory, CtaComparison
from ..core.config import settings
from .claims import AtomicClaim
from .evidence import create_verified_evidence_quote, normalize_text
from .extraction import ExtractedPageData

CONTRADICTION_PATTERNS = [
    # Free vs Paid / Credit Card
    (re.compile(r"\b(no credit card|free trial|100% free|\$0 free|free forever)\b", re.I),
     re.compile(r"\b(credit card required|paid plan required|paid subscription required|no free trial|starts at \$|credit card needed|no free tier)\b", re.I),
     "Ad claims free / no credit card, but landing page explicitly requires payment or credit card."),
    
    # Refund / Guarantee vs No refund
    (re.compile(r"\b(money[- ]back|guarantee|full refund|free cancellation)\b", re.I),
     re.compile(r"\b(no refunds|non[- ]refundable|all sales final|all sales are strictly final|strict cancellation)\b", re.I),
     "Ad promises guarantee or refund, but landing page specifies strict non-refundable terms."),
    
    # Instant vs Sales Call / Gated
    (re.compile(r"\b(instant access|start immediately|get started now|self[- ]serve)\b", re.I),
     re.compile(r"\b(speak to sales|sales consultation|request a demo|request an invite|by invitation only|trials are strictly unavailable)\b", re.I),
     "Ad promises self-serve or instant access, but page requires a gated sales consultation.")
]

def find_best_candidate_evidence(
    claim_text: str,
    page_data: ExtractedPageData
) -> Tuple[Optional[str], str, float]:
    """
    Finds the best candidate quote and element source across page segments.
    Returns (candidate_quote, source_element, similarity_score).
    """
    best_candidate: Optional[str] = None
    best_element = "body"
    best_sim = 0.0

    # 1. Check against H1 headings
    for h1 in page_data.headings_h1:
        sim = max(
            fuzz.token_set_ratio(claim_text, h1),
            fuzz.token_sort_ratio(claim_text, h1)
        )
        if sim > best_sim:
            best_sim = sim
            best_candidate = h1
            best_element = "h1"

    # 2. Check against Hero text
    if page_data.hero_text:
        sim = max(
            fuzz.token_set_ratio(claim_text, page_data.hero_text),
            fuzz.token_sort_ratio(claim_text, page_data.hero_text)
        )
        if sim > best_sim:
            best_sim = sim
            hero_sentences = page_data.hero_text.split(".")
            best_h_sent = page_data.hero_text
            best_h_score = 0
            for hs in hero_sentences:
                hs_clean = normalize_text(hs)
                if hs_clean:
                    hs_score = fuzz.token_set_ratio(claim_text, hs_clean)
                    if hs_score > best_h_score:
                        best_h_score = hs_score
                        best_h_sent = hs_clean
            best_candidate = best_h_sent
            best_element = "hero"

    # 3. Check against CTAs
    for cta in page_data.detected_ctas:
        sim = max(
            fuzz.token_set_ratio(claim_text, cta),
            fuzz.token_sort_ratio(claim_text, cta)
        )
        if sim > best_sim:
            best_sim = sim
            best_candidate = cta
            best_element = "cta_button"

    # 4. Check against H2/H3s
    for h2 in page_data.headings_h2_h3:
        sim = max(
            fuzz.token_set_ratio(claim_text, h2),
            fuzz.token_sort_ratio(claim_text, h2)
        )
        if sim > best_sim:
            best_sim = sim
            best_candidate = h2
            best_element = "h2_h3"

    # 5. Check against general text segments
    for seg in page_data.text_segments:
        seg_text = seg["text"]
        if len(seg_text) > 300:
            continue
        sim = max(
            fuzz.token_set_ratio(claim_text, seg_text),
            fuzz.token_sort_ratio(claim_text, seg_text)
        )
        if sim > best_sim:
            best_sim = sim
            best_candidate = seg_text
            best_element = seg.get("type", "body_paragraph")

    return best_candidate, best_element, round(best_sim, 1)

def detect_contradiction(
    claim: AtomicClaim,
    page_data: ExtractedPageData
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Checks if the landing page directly contradicts the claim.
    Returns (is_contradicted, contradiction_reason, conflicting_snippet).
    """
    claim_text = claim.text
    page_text = page_data.normalized_text

    # 1. Pattern-based contradiction checks
    for claim_pat, page_pat, reason in CONTRADICTION_PATTERNS:
        if claim_pat.search(claim_text):
            page_match = page_pat.search(page_text)
            if page_match:
                conflicting_snippet = page_match.group(0)
                return True, reason, conflicting_snippet

    # 2. Check footer disclosures specifically for hidden fees or non-refundable terms
    for footer in page_data.footer_disclosures:
        for claim_pat, page_pat, reason in CONTRADICTION_PATTERNS:
            if claim_pat.search(claim_text) and page_pat.search(footer):
                return True, f"Footer disclosure contradiction: {reason}", page_pat.search(footer).group(0)

    # 3. Numeric / percentage mismatch in offers
    claim_percentages = claim.extracted_entities.get("percentages", [])
    if claim_percentages:
        page_percentages = re.findall(r"\b\d+%\b", page_text, re.I)
        if page_percentages and not any(p.lower() in [cp.lower() for cp in claim_percentages] for p in page_percentages):
            if any(term in page_text.lower() for term in ["discount", "off", "sale", "save"]):
                return (
                    True,
                    f"Ad claims {', '.join(claim_percentages)} off, but landing page advertises {', '.join(page_percentages[:2])}.",
                    page_percentages[0]
                )

    return False, None, None

def evaluate_claim_match(
    claim: AtomicClaim,
    page_data: ExtractedPageData
) -> ClaimAudit:
    """
    Evaluates a single claim against page data strictly adhering to:
    Rule 1: Deterministic verify_quote() check for evidence.
    Rule 3: Statuses (Supported, Partial Match, Not Found, Contradicted, Uncertain).
            Absence of evidence = Not Found, never Contradicted.
            Similarity alone never = Supported.
    """
    claim_text = claim.text
    
    # 1. Check for contradictions first
    is_contradicted, contra_reason, contra_snippet = detect_contradiction(claim, page_data)
    if is_contradicted:
        ev_quote = create_verified_evidence_quote(contra_snippet, page_data.normalized_text, "body")
        return ClaimAudit(
            claim_id=claim.claim_id,
            source_part=claim.source_part,
            category=claim.category,
            claim_text=claim_text,
            status=MatchStatus.CONTRADICTED,
            similarity_score=40.0,
            evidence_quote=ev_quote.quote_text if ev_quote.is_verified else "No verified evidence quote available.",
            is_quote_verified=ev_quote.is_verified,
            quote_source_element=ev_quote.source_element,
            status_reason=contra_reason or "Page content factually conflicts with this ad claim.",
            suggested_action="Resolve factual discrepancy immediately to prevent user distrust and ad suspension."
        )

    # 2. Find best candidate evidence
    candidate_quote, source_el, sim_score = find_best_candidate_evidence(claim_text, page_data)

    # Verify quote deterministically against page source
    ev_quote = create_verified_evidence_quote(candidate_quote, page_data.normalized_text, source_el)

    # RULE 3: Absence of evidence = Not Found
    if sim_score < settings.UNCERTAIN_SIMILARITY_THRESHOLD:
        return ClaimAudit(
            claim_id=claim.claim_id,
            source_part=claim.source_part,
            category=claim.category,
            claim_text=claim_text,
            status=MatchStatus.NOT_FOUND,
            similarity_score=sim_score,
            evidence_quote="No verified evidence quote available.",
            is_quote_verified=False,
            quote_source_element="none",
            status_reason="No corresponding mention or evidence was found on the landing page.",
            suggested_action="Add this claim to the landing page body or headline to improve relevancy."
        )

    # Check entity consistency: if claim specifies numbers, do they exist on page?
    claim_entities = claim.extracted_entities
    numbers = claim_entities.get("numbers", [])
    percentages = claim_entities.get("percentages", [])
    currencies = claim_entities.get("currencies", [])
    
    key_entities = numbers + percentages + currencies
    entities_confirmed = True
    if key_entities:
        page_norm = page_data.normalized_text.lower()
        if not any(e.lower() in page_norm for e in key_entities):
            entities_confirmed = False

    # RULE 3: Similarity alone never = Supported
    if sim_score >= settings.SUPPORTED_SIMILARITY_THRESHOLD and ev_quote.is_verified and entities_confirmed:
        status = MatchStatus.SUPPORTED
        reason = f"Strong deterministic evidence found in page {source_el} ({sim_score:.0f}% match)."
        action = "Claim is well-aligned with landing page content."
    elif sim_score >= settings.PARTIAL_MATCH_SIMILARITY_THRESHOLD:
        status = MatchStatus.PARTIAL_MATCH
        if not entities_confirmed and key_entities:
            reason = f"Related topic found, but specific figures ({', '.join(key_entities)}) are missing or unconfirmed on page."
            action = f"Explicitly mention {', '.join(key_entities)} on the landing page or adjust ad wording."
        else:
            reason = f"Partial alignment detected ({sim_score:.0f}% match), but wording or specifics diverge."
            action = "Align wording more closely between ad copy and page hero/body."
    else:
        status = MatchStatus.UNCERTAIN
        reason = f"Vague or weak thematic relation ({sim_score:.0f}% match); unclear if this claim is confirmed."
        action = "Clarify messaging on page to make this claim explicit."

    return ClaimAudit(
        claim_id=claim.claim_id,
        source_part=claim.source_part,
        category=claim.category,
        claim_text=claim_text,
        status=status,
        similarity_score=sim_score,
        evidence_quote=ev_quote.quote_text if ev_quote.is_verified else "No verified evidence quote available.",
        is_quote_verified=ev_quote.is_verified,
        quote_source_element=ev_quote.source_element if ev_quote.is_verified else "none",
        status_reason=reason,
        suggested_action=action
    )

def audit_all_claims(
    claims: List[AtomicClaim],
    page_data: ExtractedPageData
) -> List[ClaimAudit]:
    return [evaluate_claim_match(claim, page_data) for claim in claims]

def analyze_cta_continuity(
    ad_cta: Optional[str],
    page_data: ExtractedPageData
) -> CtaComparison:
    """
    Requirement 7: Dedicated CTA analysis comparing Ad CTA against landing page CTAs.
    """
    if not ad_cta or not ad_cta.strip():
        primary_page_cta = page_data.detected_ctas[0] if page_data.detected_ctas else None
        return CtaComparison(
            ad_cta=None,
            page_primary_cta=primary_page_cta,
            all_page_ctas=page_data.detected_ctas,
            match_status=MatchStatus.UNCERTAIN,
            similarity_score=50.0,
            friction_detected=False,
            friction_notes="No explicit CTA was defined in the ad creative."
        )

    clean_ad_cta = ad_cta.strip()
    page_ctas = page_data.detected_ctas
    primary_page_cta = page_ctas[0] if page_ctas else None

    if not page_ctas:
        return CtaComparison(
            ad_cta=clean_ad_cta,
            page_primary_cta=None,
            all_page_ctas=[],
            match_status=MatchStatus.NOT_FOUND,
            similarity_score=0.0,
            friction_detected=True,
            friction_notes="No call-to-action buttons or action links were detected on the landing page."
        )

    # Check for direct friction (e.g. Free trial vs Gated sales call)
    sales_barrier_patterns = re.compile(r"\b(speak to sales|schedule demo|sales consultation|request invite|waitlist)\b", re.I)
    trial_promise_patterns = re.compile(r"\b(free trial|start free|try free|sign up free|get started free)\b", re.I)

    is_friction = False
    friction_note = ""

    if trial_promise_patterns.search(clean_ad_cta) and any(sales_barrier_patterns.search(c) for c in page_ctas):
        is_friction = True
        friction_note = "High Friction: Ad promises self-serve free trial, but landing page demands a gated sales consultation."

    # Compare ad CTA against all page CTAs
    best_sim = 0.0
    for cta in page_ctas:
        sim = max(
            fuzz.token_set_ratio(clean_ad_cta, cta),
            fuzz.token_sort_ratio(clean_ad_cta, cta)
        )
        if sim > best_sim:
            best_sim = sim

    if is_friction:
        status = MatchStatus.CONTRADICTED
    elif best_sim >= 80.0:
        status = MatchStatus.SUPPORTED
        friction_note = "Strong continuity: Landing page CTA directly aligns with ad promise."
    elif best_sim >= 55.0:
        status = MatchStatus.PARTIAL_MATCH
        friction_note = "Moderate continuity: Button action is related but phrasing differs."
    else:
        status = MatchStatus.NOT_FOUND
        friction_note = f"Action gap: Landing page buttons ({', '.join(page_ctas[:2])}) do not match ad CTA '{clean_ad_cta}'."

    return CtaComparison(
        ad_cta=clean_ad_cta,
        page_primary_cta=primary_page_cta,
        all_page_ctas=page_ctas,
        match_status=status,
        similarity_score=round(best_sim, 1),
        friction_detected=is_friction or status in (MatchStatus.NOT_FOUND, MatchStatus.CONTRADICTED),
        friction_notes=friction_note
    )
