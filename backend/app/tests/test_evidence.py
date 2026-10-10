import pytest
from backend.app.services.evidence import (
    normalize_text,
    verify_quote,
    create_verified_evidence_quote,
    FALLBACK_QUOTE_TEXT
)
from backend.app.services.demo_data import SYNTHETIC_SCENARIOS, load_scenario_html
from backend.app.services.extraction import parse_html_content, ExtractionException
from backend.app.services.claims import extract_claims_from_ad
from backend.app.services.matching import audit_all_claims

def test_normalize_text():
    raw = "   Save   50%    on   all \n plans\t today!   "
    assert normalize_text(raw) == "Save 50% on all plans today!"
    assert normalize_text("") == ""
    assert normalize_text(None) == ""

def test_verify_quote_exact_substring():
    source_text = "Welcome to CloudFlow. Accelerate your deployment pipeline with automated tests and 99.9% uptime."
    
    is_valid, start, end = verify_quote("Accelerate your deployment pipeline", source_text)
    assert is_valid is True
    assert source_text[start:end] == "Accelerate your deployment pipeline"

def test_fabricated_quote_is_rejected():
    """Requirement 6: Test that a fabricated quote is strictly rejected."""
    source_text = "Standard monthly pricing starting at $49/mo."
    
    # Fabricated / altered quote
    is_valid, start, end = verify_quote("Free unlimited lifetime access with no charge", source_text)
    assert is_valid is False
    assert start is None
    assert end is None

    # Substring check with extra fabricated words
    is_valid, start, end = verify_quote("Standard monthly pricing starting at $10/mo with free gifts", source_text)
    assert is_valid is False

    # Evidence quote creator should return fallback
    ev = create_verified_evidence_quote("Completely fabricated text", source_text)
    assert ev.is_verified is False
    assert ev.quote_text == FALLBACK_QUOTE_TEXT

def test_every_finding_in_all_accessible_demos_has_verified_substring_or_fallback():
    """Requirement 6: For every finding across all 7 demos, verify_quote is a substring of the normalized extracted text."""
    for scenario in SYNTHETIC_SCENARIOS:
        try:
            html = load_scenario_html(scenario)
            page_data = parse_html_content(html)
        except ExtractionException:
            # Scenario 5 (empty shell) fails extraction by design - null findings
            continue

        claims = extract_claims_from_ad(scenario.ad)
        audited_claims = audit_all_claims(claims, page_data)

        for finding in audited_claims:
            if finding.is_quote_verified:
                assert finding.evidence_quote is not None
                assert finding.evidence_quote != FALLBACK_QUOTE_TEXT
                # Must be an exact substring after whitespace normalization
                norm_quote = normalize_text(finding.evidence_quote)
                assert norm_quote.lower() in page_data.normalized_text.lower(), (
                    f"Quote '{norm_quote}' in scenario '{scenario.id}' is not in extracted text!"
                )
            else:
                assert finding.evidence_quote == FALLBACK_QUOTE_TEXT
