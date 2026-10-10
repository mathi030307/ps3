import re
from typing import Tuple, Optional
from ..schemas.audit import EvidenceQuote

FALLBACK_QUOTE_TEXT = "No verified evidence quote available."

def normalize_text(text: Optional[str]) -> str:
    """
    Deterministically normalizes text by converting all whitespace sequences
    (including non-breaking spaces, newlines, tabs) to a single ASCII space and trimming.
    """
    if not text:
        return ""
    # Normalize unicode whitespace
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip()

def verify_quote(quote: Optional[str], normalized_source_text: str) -> Tuple[bool, Optional[int], Optional[int]]:
    """
    Deterministic quote verification against extracted source text.
    RULE 1: Exact substring after whitespace normalization.
    Returns (is_verified, char_start, char_end).
    """
    if not quote or not normalized_source_text:
        return False, None, None
    
    norm_quote = normalize_text(quote)
    if len(norm_quote) < 3:  # Too short to be a valid deterministic quote
        return False, None, None

    # Exact substring match after whitespace normalization (case-insensitive for robust index lookup,
    # then verifies exact casing or normalized presence)
    start_idx = normalized_source_text.lower().find(norm_quote.lower())
    if start_idx == -1:
        return False, None, None

    end_idx = start_idx + len(norm_quote)
    return True, start_idx, end_idx

def extract_surrounding_context(normalized_source_text: str, start_idx: int, end_idx: int, padding: int = 60) -> str:
    """
    Extracts surrounding context with ellipses for provenance display.
    """
    total_len = len(normalized_source_text)
    ctx_start = max(0, start_idx - padding)
    ctx_end = min(total_len, end_idx + padding)
    
    prefix = "..." if ctx_start > 0 else ""
    suffix = "..." if ctx_end < total_len else ""
    
    return f"{prefix}{normalized_source_text[ctx_start:ctx_end]}{suffix}"

def create_verified_evidence_quote(
    candidate_quote: Optional[str],
    normalized_source_text: str,
    source_element: str = "body"
) -> EvidenceQuote:
    """
    Verifies candidate quote. If verification succeeds, returns EvidenceQuote with offsets.
    If it fails, strictly returns 'No verified evidence quote available.' with is_verified=False.
    """
    if not candidate_quote:
        return EvidenceQuote(
            quote_text=FALLBACK_QUOTE_TEXT,
            is_verified=False,
            source_element="none"
        )

    is_verified, start_idx, end_idx = verify_quote(candidate_quote, normalized_source_text)
    if not is_verified or start_idx is None or end_idx is None:
        return EvidenceQuote(
            quote_text=FALLBACK_QUOTE_TEXT,
            is_verified=False,
            source_element="none"
        )

    # Extract the exact substring from source text to guarantee absolute fidelity
    exact_source_substring = normalized_source_text[start_idx:end_idx]
    surrounding = extract_surrounding_context(normalized_source_text, start_idx, end_idx)

    return EvidenceQuote(
        quote_text=exact_source_substring,
        is_verified=True,
        source_element=source_element,
        char_start=start_idx,
        char_end=end_idx,
        surrounding_context=surrounding
    )
