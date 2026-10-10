import pytest
from backend.app.schemas.audit import ClaimAudit, MatchStatus, ClaimCategory, CtaComparison
from backend.app.services.extraction import ExtractedPageData
from backend.app.services.scoring import calculate_score, STATUS_BASE_VALUES, FORMULA_TEXT

def test_null_score_when_analysis_cannot_complete():
    """Rule 4: Score is null (unavailable) when analysis can't complete; this is different from 0."""
    score, grade, verdict, breakdown = calculate_score([], None)
    assert score is None
    assert grade is None
    assert breakdown is None
    assert "incomplete" in verdict.lower()

    dummy_claim = ClaimAudit(
        claim_id="C01",
        source_part="headline",
        category=ClaimCategory.FEATURE_BENEFIT,
        claim_text="Fast Cloud Storage",
        status=MatchStatus.NOT_FOUND,
        similarity_score=0.0,
        evidence_quote="No verified evidence quote available.",
        is_quote_verified=False,
        status_reason="Not found",
        suggested_action="Add to page"
    )
    score, grade, verdict, breakdown = calculate_score([dummy_claim], None)
    assert score is None
    assert grade is None

def test_documented_scoring_formula_and_material_weights():
    """Requirement 3: Test status values, material weight 2.0x, contribution table, and formula text."""
    page_data = ExtractedPageData(
        raw_html="<html><body><h1>Enterprise CRM Platform</h1><p>Streamline deal flow.</p><button>Start Free Trial</button></body></html>",
        normalized_text="Enterprise CRM Platform Streamline deal flow. Start Free Trial",
        headings_h1=["Enterprise CRM Platform"],
        headings_h2_h3=[],
        hero_text="Enterprise CRM Platform",
        detected_ctas=["Start Free Trial"],
        text_segments=[{"type": "h1", "text": "Enterprise CRM Platform"}]
    )

    claims = [
        # Material claim 1 (Headline, weight=2.0, Supported=1.0 -> 2.0 points)
        ClaimAudit(
            claim_id="C01",
            source_part="headline",
            category=ClaimCategory.FEATURE_BENEFIT,
            claim_text="Enterprise CRM Platform",
            status=MatchStatus.SUPPORTED,
            similarity_score=100.0,
            evidence_quote="Enterprise CRM Platform",
            is_quote_verified=True,
            status_reason="Matched",
            suggested_action="Maintain"
        ),
        # Material claim 2 (Offer/Pricing, weight=2.0, Partial Match=0.5 -> 1.0 points)
        ClaimAudit(
            claim_id="C02",
            source_part="description",
            category=ClaimCategory.OFFER_PRICING,
            claim_text="Save 50% on all plans",
            status=MatchStatus.PARTIAL_MATCH,
            similarity_score=65.0,
            evidence_quote="Streamline deal flow.",
            is_quote_verified=True,
            status_reason="Partial",
            suggested_action="Align pricing"
        ),
        # Standard claim 3 (Description, weight=1.0, Not Found=0.0 -> 0.0 points)
        ClaimAudit(
            claim_id="C03",
            source_part="description",
            category=ClaimCategory.FEATURE_BENEFIT,
            claim_text="Integrates with 500 apps",
            status=MatchStatus.NOT_FOUND,
            similarity_score=10.0,
            evidence_quote="No verified evidence quote available.",
            is_quote_verified=False,
            status_reason="Not found",
            suggested_action="Add to page"
        )
    ]

    cta_comp = CtaComparison(
        ad_cta="Start Free Trial",
        page_primary_cta="Start Free Trial",
        all_page_ctas=["Start Free Trial"],
        match_status=MatchStatus.SUPPORTED,
        similarity_score=100.0,
        friction_detected=False,
        friction_notes="Exact match"
    )

    score, grade, verdict, breakdown = calculate_score(claims, page_data, cta_comp)
    assert score is not None
    # Calculation check:
    # C01: 1.0 * 2.0 = 2.0 pts (max 2.0)
    # C02: 0.5 * 2.0 = 1.0 pts (max 2.0)
    # C03: 0.0 * 1.0 = 0.0 pts (max 1.0)
    # Total weighted: 3.0 pts, Total max: 5.0 pts -> Base Score = 3.0 / 5.0 * 100 = 60.0%
    assert score == 60.0

    # Verify per-claim contribution table
    assert len(breakdown.claim_contributions) == 3
    c01_contrib = next(c for c in breakdown.claim_contributions if c.claim_id == "C01")
    assert c01_contrib.weight == 2.0
    assert c01_contrib.base_value == 1.0
    assert c01_contrib.weighted_points == 2.0
    assert c01_contrib.contribution_percent == 40.0  # 2.0 / 5.0 = 40%

    c02_contrib = next(c for c in breakdown.claim_contributions if c.claim_id == "C02")
    assert c02_contrib.weight == 2.0
    assert c02_contrib.base_value == 0.5
    assert c02_contrib.weighted_points == 1.0
    assert c02_contrib.contribution_percent == 20.0  # 1.0 / 5.0 = 20%

    # Verify formula text and presentation aid label
    assert breakdown.formula_text == FORMULA_TEXT
    assert "Presentation aid" in breakdown.presentation_aid_label

def test_contradiction_triggers_cap_at_40():
    """Requirement 3: If any claim is Contradicted, overall score is strictly capped at 40."""
    page_data = ExtractedPageData(
        raw_html="<html><body><h1>Accounting Software</h1><p>Credit card required at signup.</p></body></html>",
        normalized_text="Accounting Software Credit card required at signup.",
        headings_h1=["Accounting Software"],
        headings_h2_h3=[],
        hero_text="Accounting Software",
        detected_ctas=["Sign Up"],
        text_segments=[]
    )

    claims = [
        # Strongly supported claim
        ClaimAudit(
            claim_id="C01",
            source_part="headline",
            category=ClaimCategory.FEATURE_BENEFIT,
            claim_text="Accounting Software",
            status=MatchStatus.SUPPORTED,
            similarity_score=100.0,
            evidence_quote="Accounting Software",
            is_quote_verified=True,
            status_reason="Match",
            suggested_action="Keep"
        ),
        # Contradicted offer claim
        ClaimAudit(
            claim_id="C02",
            source_part="description",
            category=ClaimCategory.OFFER_PRICING,
            claim_text="No credit card required",
            status=MatchStatus.CONTRADICTED,
            similarity_score=40.0,
            evidence_quote="Credit card required at signup.",
            is_quote_verified=True,
            status_reason="Contradiction",
            suggested_action="Fix terms"
        )
    ]

    score, grade, verdict, breakdown = calculate_score(claims, page_data)
    assert score is not None
    # Score MUST be capped at 40.0 or lower
    assert score <= 40.0
    assert breakdown.is_capped_at_40 is True
    assert grade in ("D", "F")
