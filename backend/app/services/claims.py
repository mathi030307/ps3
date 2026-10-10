import re
from typing import List, Dict, Any, Optional
from ..schemas.audit import AdInput, ClaimCategory

class AtomicClaim:
    def __init__(
        self,
        claim_id: str,
        source_part: str,
        category: ClaimCategory,
        text: str,
        extracted_entities: Dict[str, Any]
    ):
        self.claim_id = claim_id
        self.source_part = source_part  # "headline", "description", or "cta"
        self.category = category
        self.text = text
        self.extracted_entities = extracted_entities

# Regex patterns for categorization
PRICE_OFFER_PATTERN = re.compile(
    r"(\$|€|£|₹|\b\d+%\b|\bfree\b|\bdiscount\b|\boff\b|\bprice\b|\bpricing\b|\bcost\b|\bfee\b|\bfees\b|\bmonthly\b|\bannually\b|\btrial\b|\bguarantee\b|\bmoney-back\b|\bstarting at\b|\bsave\b|\bdeal\b|\bcredit card\b|\bcard required\b|\bno cc\b)",
    re.I
)

CTA_ACTION_PATTERN = re.compile(
    r"\b(start|try|get|claim|download|sign up|join|book|schedule|buy|order|register|subscribe|explore|see|request|contact)\b",
    re.I
)

TRUST_PROOF_PATTERN = re.compile(
    r"(\b(rated|stars|reviews|trusted by|customers|users|award|proven|certified|#1|no\. 1|fortune 500|verified|leader)\b|\b\d+[kKmM\+]+\b|\b\d+(\.\d+)?\s*/\s*5\b)",
    re.I
)

AUDIENCE_SCOPE_PATTERN = re.compile(
    r"\b(for teams|for enterprise|for businesses|for small business|for developers|for creators|for agencies|for beginners|b2b|b2c)\b",
    re.I
)

def extract_entities_from_claim(text: str) -> Dict[str, Any]:
    """
    Extracts numerical figures, percentages, currencies, and timeframes
    to enable deterministic contradiction and offer mismatch checks.
    """
    entities: Dict[str, Any] = {
        "percentages": re.findall(r"\b\d+%\b", text, re.I),
        "currencies": re.findall(r"[\$€£₹]\s*\d+(?:\.\d{2})?", text),
        "numbers": re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", text),
        "has_free": bool(re.search(r"\bfree\b", text, re.I)),
        "has_trial": bool(re.search(r"\btrial\b", text, re.I)),
        "timeframes": re.findall(r"\b\d+\s*(?:day|days|hour|hours|min|minutes|month|months|year|years)\b", text, re.I)
    }
    return entities

def categorize_claim(text: str, source_part: str) -> ClaimCategory:
    """
    Deterministically determines the claim category based on source part and lexical features.
    """
    if source_part == "cta":
        return ClaimCategory.CTA_ACTION

    if PRICE_OFFER_PATTERN.search(text):
        return ClaimCategory.OFFER_PRICING

    if TRUST_PROOF_PATTERN.search(text):
        return ClaimCategory.TRUST_PROOF

    if AUDIENCE_SCOPE_PATTERN.search(text):
        return ClaimCategory.AUDIENCE_SCOPE

    if source_part == "headline" and CTA_ACTION_PATTERN.search(text) and len(text.split()) <= 4:
        return ClaimCategory.CTA_ACTION

    return ClaimCategory.FEATURE_BENEFIT

def split_text_into_claim_units(text: str) -> List[str]:
    """
    Splits text on punctuation (., !, ?, ;, newline, pipes, em-dash, bullets).
    Preserves meaningful clauses while avoiding empty fragments.
    """
    if not text:
        return []

    # Replace common bullet separators and pipes with periods
    cleaned = re.sub(r"[\r\n]+", ". ", text)
    cleaned = re.sub(r"[\t|•–—]+", ". ", cleaned)

    # Split on sentence terminals
    raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    
    claims: List[str] = []
    for s in raw_sentences:
        s_clean = s.strip().rstrip(".!? \t")
        if not s_clean:
            continue
        
        # If sentence contains coordinate clauses joined by " - " or " – "
        sub_clauses = re.split(r"\s+[-]\s+", s_clean)
        for clause in sub_clauses:
            clause = clause.strip()
            # Must have at least 2 words or 5 characters
            if len(clause.split()) >= 2 or len(clause) >= 5:
                claims.append(clause)

    return claims

def extract_claims_from_ad(ad: AdInput) -> List[AtomicClaim]:
    """
    Extracts structured atomic claims from headline, description, and CTA.
    """
    claims: List[AtomicClaim] = []
    claim_counter = 1

    # 1. Headline claims
    headline_units = split_text_into_claim_units(ad.headline)
    if not headline_units and ad.headline.strip():
        headline_units = [ad.headline.strip()]
    
    for unit in headline_units:
        cat = categorize_claim(unit, "headline")
        entities = extract_entities_from_claim(unit)
        claims.append(AtomicClaim(
            claim_id=f"C{claim_counter:02d}",
            source_part="headline",
            category=cat,
            text=unit,
            extracted_entities=entities
        ))
        claim_counter += 1

    # 2. Description claims
    desc_units = split_text_into_claim_units(ad.description)
    if not desc_units and ad.description.strip():
        desc_units = [ad.description.strip()]

    for unit in desc_units:
        cat = categorize_claim(unit, "description")
        entities = extract_entities_from_claim(unit)
        claims.append(AtomicClaim(
            claim_id=f"C{claim_counter:02d}",
            source_part="description",
            category=cat,
            text=unit,
            extracted_entities=entities
        ))
        claim_counter += 1

    # 3. CTA claim (if provided)
    if ad.cta and ad.cta.strip():
        cta_text = ad.cta.strip()
        entities = extract_entities_from_claim(cta_text)
        claims.append(AtomicClaim(
            claim_id=f"C{claim_counter:02d}",
            source_part="cta",
            category=ClaimCategory.CTA_ACTION,
            text=cta_text,
            extracted_entities=entities
        ))
        claim_counter += 1

    return claims
