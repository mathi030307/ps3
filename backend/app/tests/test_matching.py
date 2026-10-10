import pytest
from backend.app.schemas.audit import MatchStatus, ClaimCategory
from backend.app.services.claims import AtomicClaim
from backend.app.services.extraction import ExtractedPageData
from backend.app.services.matching import evaluate_claim_match

def test_absence_of_evidence_is_not_found_never_contradicted():
    """Rule 3: Absence of evidence = Not Found, never Contradicted."""
    claim = AtomicClaim(
        claim_id="C01",
        source_part="description",
        category=ClaimCategory.FEATURE_BENEFIT,
        text="Includes quantum encrypted military grade backups",
        extracted_entities={}
    )
    # Landing page is completely silent on this subject
    page_data = ExtractedPageData(
        raw_html="<html><body><p>Simple note taking app for shopping lists.</p></body></html>",
        normalized_text="Simple note taking app for shopping lists.",
        headings_h1=["Simple Notes"],
        headings_h2_h3=[],
        hero_text="Simple note taking app",
        detected_ctas=["Download"],
        text_segments=[{"type": "body_text", "text": "Simple note taking app for shopping lists."}]
    )

    result = evaluate_claim_match(claim, page_data)
    assert result.status == MatchStatus.NOT_FOUND
    assert result.status != MatchStatus.CONTRADICTED
    assert result.evidence_quote == "No verified evidence quote available."
    assert result.is_quote_verified is False

def test_contradiction_detected_when_page_conflicts():
    """Rule 3: Status is Contradicted when explicit contradiction exists."""
    claim = AtomicClaim(
        claim_id="C02",
        source_part="description",
        category=ClaimCategory.OFFER_PRICING,
        text="100% free trial with no credit card required",
        extracted_entities={"has_free": True}
    )
    page_data = ExtractedPageData(
        raw_html="<html><body><p>Paid plan required with credit card required at kickoff.</p></body></html>",
        normalized_text="Paid plan required with credit card required at kickoff.",
        headings_h1=["Enterprise CRM"],
        headings_h2_h3=[],
        hero_text="Enterprise CRM",
        detected_ctas=["Contact Sales"],
        text_segments=[{"type": "body_text", "text": "Paid plan required with credit card required at kickoff."}]
    )

    result = evaluate_claim_match(claim, page_data)
    assert result.status == MatchStatus.CONTRADICTED

def test_similarity_alone_never_supported_if_entities_missing():
    """Rule 3: Similarity alone never = Supported if entities (e.g. 50% discount) disagree."""
    claim = AtomicClaim(
        claim_id="C03",
        source_part="headline",
        category=ClaimCategory.OFFER_PRICING,
        text="Get 50% off all annual cloud plans today",
        extracted_entities={"percentages": ["50%"]}
    )
    # Page text talks about cloud plans and discounts, but does NOT contain 50%
    page_data = ExtractedPageData(
        raw_html="<html><body><h1>Get special cloud plans today</h1><p>Save 15% on team licenses.</p></body></html>",
        normalized_text="Get special cloud plans today Save 15% on team licenses.",
        headings_h1=["Get special cloud plans today"],
        headings_h2_h3=[],
        hero_text="Get special cloud plans today",
        detected_ctas=["Sign Up"],
        text_segments=[
            {"type": "h1", "text": "Get special cloud plans today"},
            {"type": "body_text", "text": "Save 15% on team licenses."}
        ]
    )

    result = evaluate_claim_match(claim, page_data)
    # Must NOT be Supported because 50% is unconfirmed
    assert result.status != MatchStatus.SUPPORTED

def test_supported_claim_has_verified_quote():
    """Rule 1 & 3: Supported requires verified exact quote and high similarity."""
    claim = AtomicClaim(
        claim_id="C04",
        source_part="headline",
        category=ClaimCategory.FEATURE_BENEFIT,
        text="Automated testing pipeline for fast deploys",
        extracted_entities={}
    )
    page_data = ExtractedPageData(
        raw_html="<html><body><h1>Automated testing pipeline for fast deploys</h1></body></html>",
        normalized_text="Automated testing pipeline for fast deploys",
        headings_h1=["Automated testing pipeline for fast deploys"],
        headings_h2_h3=[],
        hero_text="Automated testing pipeline for fast deploys",
        detected_ctas=[],
        text_segments=[{"type": "h1", "text": "Automated testing pipeline for fast deploys"}]
    )

    result = evaluate_claim_match(claim, page_data)
    assert result.status == MatchStatus.SUPPORTED
    assert result.is_quote_verified is True
    assert result.evidence_quote == "Automated testing pipeline for fast deploys"
