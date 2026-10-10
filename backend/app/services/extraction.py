import re
from typing import List, Dict, Any, Optional, Tuple
import httpx
from bs4 import BeautifulSoup
from ..core.config import settings
from ..core.security import validate_url_for_ssrf, SecurityException
from .evidence import normalize_text

class ExtractionException(Exception):
    """Exception raised when page extraction or fetching fails."""
    pass

class ExtractedPageData:
    def __init__(
        self,
        raw_html: str,
        normalized_text: str,
        title: Optional[str] = None,
        headings_h1: Optional[List[str]] = None,
        headings_h2_h3: Optional[List[str]] = None,
        hero_text: Optional[str] = None,
        detected_ctas: Optional[List[str]] = None,
        footer_disclosures: Optional[List[str]] = None,
        text_segments: Optional[List[Dict[str, Any]]] = None,
        url: Optional[str] = None
    ):
        self.raw_html = raw_html
        self.normalized_text = normalized_text
        self.title = title
        self.headings_h1 = headings_h1 or []
        self.headings_h2_h3 = headings_h2_h3 or []
        self.hero_text = hero_text
        self.detected_ctas = detected_ctas or []
        self.footer_disclosures = footer_disclosures or []
        self.text_segments = text_segments or []
        self.url = url
        
        words = self.normalized_text.split()
        self.word_count = len(words)
        self.reading_time_minutes = round(self.word_count / 200.0, 1) if self.word_count > 0 else 0.0

def validate_snapshot_file(filename: str, content_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates uploaded HTML snapshot file:
    - Must have .html or .htm extension
    - Must be within size limit (5MB)
    - Must not be a binary file (checked via null bytes or decode errors)
    """
    if not filename:
        return False, "File must have a valid filename."

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    if ext not in ("html", "htm"):
        return False, f"Invalid file extension '.{ext}'. Only .html and .htm files are supported."

    if len(content_bytes) > settings.MAX_HTML_SIZE_BYTES:
        return False, f"File size ({len(content_bytes)} bytes) exceeds the 5MB limit."

    # Binary check: null byte detection
    if b"\x00" in content_bytes:
        return False, "File contains binary data. Please upload a plain text HTML snapshot."

    return True, ""

async def fetch_html_from_url(url: str) -> str:
    """
    Safely fetches HTML from a live URL with SSRF validation,
    strict timeouts, redirect inspection, and content-type checks.
    """
    if not url:
        raise ExtractionException("URL cannot be empty.")

    is_safe, error_msg = validate_url_for_ssrf(url)
    if not is_safe:
        raise SecurityException(f"SSRF Protection: {error_msg}")

    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(
            timeout=settings.FETCH_TIMEOUT_SECONDS,
            follow_redirects=False,  # Handle redirects manually to verify each step for SSRF
            verify=True
        ) as client:
            current_url = url
            response = None
            redirect_count = 0
            max_redirects = 4

            while redirect_count <= max_redirects:
                # SSRF check before each request
                safe_hop, hop_err = validate_url_for_ssrf(current_url)
                if not safe_hop:
                    raise SecurityException(f"SSRF Protection: Redirect target {hop_err}")

                response = await client.get(current_url, headers=headers)

                if response.is_redirect:
                    redirect_count += 1
                    location = response.headers.get("location")
                    if not location:
                        raise ExtractionException("Redirect header missing location.")
                    # Resolve relative redirect URLs
                    current_url = str(response.url.join(location))
                    continue
                else:
                    break

            if response.status_code >= 400:
                raise ExtractionException(f"Target page returned HTTP status {response.status_code} ({response.reason_phrase}).")

            content_type = response.headers.get("content-type", "").lower()
            # Non-HTML content rejection
            if not any(t in content_type for t in ("text/html", "application/xhtml+xml")):
                if any(t in content_type for t in ("application/pdf", "image/", "audio/", "video/", "application/zip", "application/octet-stream", "application/json")):
                    raise ExtractionException(f"Target URL returned non-HTML content (Content-Type: {content_type}).")

            if len(response.content) > settings.MAX_HTML_SIZE_BYTES:
                raise ExtractionException("Landing page HTML exceeds maximum allowed size (5MB).")

            return response.text

    except httpx.TimeoutException:
        raise ExtractionException("Connection timed out while fetching the landing page.")
    except httpx.ConnectError:
        raise ExtractionException("Failed to establish connection to the target server.")
    except httpx.HTTPError as e:
        raise ExtractionException(f"HTTP request failed: {str(e)}")
    except SecurityException:
        raise
    except ExtractionException:
        raise
    except Exception as e:
        raise ExtractionException(f"An unexpected error occurred while fetching the page: {str(e)}")

def parse_html_content(html: str, url: Optional[str] = None) -> ExtractedPageData:
    """
    Parses HTML content, strips scripts, styles, and hidden text,
    validates minimum content (detects JS-only empty shells),
    and extracts headings, hero text, CTAs, footer fee disclosures, and text segments.
    """
    if not html or not html.strip():
        raise ExtractionException("Provided HTML content is empty.")

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # 1. Remove non-content tags (scripts, styles, noscript, svg, canvas, iframe, template)
    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe", "template"]):
        tag.decompose()

    # 2. Remove hidden elements (display:none, visibility:hidden, aria-hidden="true", hidden attribute)
    for el in soup.find_all(True):
        style_attr = el.get("style", "").lower()
        if (
            "display:none" in style_attr.replace(" ", "") or
            "visibility:hidden" in style_attr.replace(" ", "") or
            "opacity:0" in style_attr.replace(" ", "") or
            el.get("aria-hidden") == "true" or
            el.has_attr("hidden") or
            (el.name == "input" and el.get("type") == "hidden")
        ):
            el.decompose()

    # 3. Extract footer disclosures & fee terms before general segmenting
    footer_disclosures: List[str] = []
    footer_elements = soup.find_all(
        ["footer", "div", "section", "p", "aside"],
        attrs={"class": re.compile(r"footer|disclaimer|disclosure|legal|terms|pricing-notice|pricing-terms", re.I)}
    )
    for f in footer_elements:
        f_text = normalize_text(f.get_text())
        if f_text and len(f_text) > 10 and f_text not in footer_disclosures:
            footer_disclosures.append(f_text)

    # 4. Page Title
    title_tag = soup.find("title")
    title = normalize_text(title_tag.get_text()) if title_tag else None

    # 5. Headings (H1, H2, H3)
    headings_h1: List[str] = []
    for h in soup.find_all("h1"):
        text = normalize_text(h.get_text())
        if text and text not in headings_h1:
            headings_h1.append(text)

    headings_h2_h3: List[str] = []
    for h in soup.find_all(["h2", "h3"]):
        text = normalize_text(h.get_text())
        if text and text not in headings_h2_h3:
            headings_h2_h3.append(text)

    # 6. Hero Section Detection
    hero_text: Optional[str] = None
    hero_candidates = soup.find_all(
        ["header", "section", "div"],
        attrs={"class": re.compile(r"hero|banner|intro|headline|header-main", re.I)}
    )
    if hero_candidates:
        hero_text = normalize_text(hero_candidates[0].get_text())
    elif headings_h1:
        h1_first = soup.find("h1")
        if h1_first:
            next_p = h1_first.find_next("p")
            if next_p:
                hero_text = normalize_text(f"{h1_first.get_text()} - {next_p.get_text()}")
            else:
                hero_text = headings_h1[0]

    # 7. CTA Buttons and Action Links
    detected_ctas: List[str] = []
    cta_selectors = soup.find_all(
        ["button", "a"],
        attrs={"class": re.compile(r"btn|button|cta|action|primary", re.I)}
    )
    cta_inputs = soup.find_all("input", attrs={"type": re.compile(r"submit|button", re.I)})
    
    for el in cta_selectors + cta_inputs:
        btn_text = el.get("value", "") if el.name == "input" else el.get_text()
        btn_text = normalize_text(btn_text)
        if btn_text and 2 < len(btn_text) < 70 and btn_text not in detected_ctas:
            detected_ctas.append(btn_text)

    if not detected_ctas:
        for btn in soup.find_all("button"):
            t = normalize_text(btn.get_text())
            if t and 2 < len(t) < 70 and t not in detected_ctas:
                detected_ctas.append(t)

    # 8. Full normalized visible body text
    body = soup.find("body") or soup
    raw_body_text = body.get_text(separator=" ")
    normalized_source_text = normalize_text(raw_body_text)

    # 9. Insufficient Content Check (JS-only empty shell detection)
    words = normalized_source_text.split()
    if len(words) < 10 or len(normalized_source_text) < 50:
        raise ExtractionException(
            "insufficient_content: Landing page does not contain sufficient visible text for analysis (empty or client-rendered JavaScript SPA shell)."
        )

    # 10. Structured text segments for deterministic provenance
    text_segments: List[Dict[str, Any]] = []
    for element in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "span", "button", "a"]):
        if element.find(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
            continue
        seg_text = normalize_text(element.get_text())
        if seg_text and len(seg_text) >= 3:
            tag_name = element.name
            if tag_name.startswith("h"):
                elem_type = tag_name
            elif tag_name in ("button", "a") and ("btn" in element.get("class", []) or tag_name == "button"):
                elem_type = "cta_button"
            else:
                elem_type = "body_text"

            text_segments.append({
                "type": elem_type,
                "text": seg_text
            })

    return ExtractedPageData(
        raw_html=html,
        normalized_text=normalized_source_text,
        title=title,
        headings_h1=headings_h1,
        headings_h2_h3=headings_h2_h3,
        hero_text=hero_text,
        detected_ctas=detected_ctas,
        footer_disclosures=footer_disclosures,
        text_segments=text_segments,
        url=url
    )
