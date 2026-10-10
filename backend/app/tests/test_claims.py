import pytest
from backend.app.schemas.audit import AdInput, ClaimCategory
from backend.app.services.claims import extract_claims_from_ad, split_text_into_claim_units

def test_split_text_into_claim_units():
    text = "Save 50% Today. Fast setup • Trusted by 10k users - Zero hidden fees!"
    units = split_text_into_claim_units(text)
    assert len(units) >= 3
    assert any("Save 50% Today" in u for u in units)
    assert any("Fast setup" in u for u in units)

def test_extract_claims_from_ad():
    ad = AdInput(
        headline="AI Marketing Automation - Boost ROAS by 40%",
        description="Launch high-converting campaigns in seconds. Rated 4.9/5 by 5,000+ marketers. No credit card required.",
        cta="Start Free Trial"
    )
    claims = extract_claims_from_ad(ad)
    assert len(claims) >= 3
    
    categories = [c.category for c in claims]
    assert ClaimCategory.OFFER_PRICING in categories
    assert ClaimCategory.CTA_ACTION in categories
    assert any(c.source_part == "cta" for c in claims)
