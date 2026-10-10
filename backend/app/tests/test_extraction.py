import pytest
from backend.app.services.extraction import (
    parse_html_content,
    validate_snapshot_file,
    ExtractionException
)

SCRIPT_STYLE_HEAVY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Cloud Analytics</title>
    <style>
        .hero { color: red; margin: 0; padding: 20px; }
        @media (max-width: 600px) { body { font-size: 14px; } }
    </style>
    <script>
        var trackingData = { id: 12345, event: "pageview", token: "secret_xyz" };
        function trackEvent() { window.dataLayer.push(trackingData); }
    </script>
</head>
<body>
    <header class="hero">
        <h1>Enterprise Cloud Analytics Dashboard</h1>
        <p>Monitor real-time infrastructure performance across global clusters.</p>
        <button class="btn btn-primary">Start Free Trial</button>
    </header>
    <script src="https://cdn.example.com/analytics.js"></script>
    <noscript><iframe src="https://example.com/ns.html"></iframe></noscript>
</body>
</html>
"""

HIDDEN_TEXT_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Store</title></head>
<body>
    <h1>Visible Title For Customers</h1>
    <p>This is standard visible product description text.</p>
    <p style="display: none;">Secret discount code 99% OFF hidden from view</p>
    <div style="visibility: hidden;">Hidden competitor price match promise</div>
    <span aria-hidden="true">Hidden decorative metric 10x faster</span>
    <input type="hidden" name="csrf" value="hidden_value_token" />
    <button class="btn">Buy Now</button>
</body>
</html>
"""

FOOTER_DISCLOSURE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Low Cost Loans</title></head>
<body>
    <header class="hero">
        <h1>Instant Personal Loans at 0% APR</h1>
        <p>Borrow up to $5,000 with zero upfront fees.</p>
        <button class="btn">Apply Online</button>
    </header>
    <main>
        <p>Fast approval process within 24 hours.</p>
    </main>
    <footer class="legal-disclaimer">
        <p>Mandatory Disclosure: 0% APR applies only for the first 30 days. Standard variable APR of 29.9% applies thereafter. Origination fee of $150 deducted upon disbursement.</p>
    </footer>
</body>
</html>
"""

JS_EMPTY_SHELL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Single Page App</title>
    <script src="/static/bundle.js"></script>
</head>
<body>
    <div id="root"></div>
    <noscript>Please enable JavaScript to view this application.</noscript>
</body>
</html>
"""

def test_script_style_heavy_page():
    """Requirement 5: Scripts and styles must be cleanly decomposed and excluded from text."""
    data = parse_html_content(SCRIPT_STYLE_HEAVY_HTML)
    assert data.title == "Enterprise Cloud Analytics"
    assert "Enterprise Cloud Analytics Dashboard" in data.headings_h1
    assert "trackingData" not in data.normalized_text
    assert "dataLayer" not in data.normalized_text
    assert "font-size" not in data.normalized_text
    assert "Start Free Trial" in data.detected_ctas

def test_hidden_text_removal():
    """Requirement 5: Hidden text (display:none, visibility:hidden, aria-hidden) must be excluded."""
    data = parse_html_content(HIDDEN_TEXT_HTML)
    assert "Visible Title For Customers" in data.normalized_text
    assert "Secret discount code" not in data.normalized_text
    assert "Hidden competitor price" not in data.normalized_text
    assert "Hidden decorative metric" not in data.normalized_text
    assert "hidden_value_token" not in data.normalized_text

def test_footer_fee_disclosure():
    """Requirement 5: Footer fee disclosures must be extracted accurately."""
    data = parse_html_content(FOOTER_DISCLOSURE_HTML)
    assert len(data.footer_disclosures) >= 1
    assert any("Origination fee of $150" in f for f in data.footer_disclosures)
    assert any("29.9% applies thereafter" in f for f in data.footer_disclosures)

def test_js_empty_shell_raises_insufficient_content():
    """Requirement 5: JS-only empty shell must raise insufficient_content ExtractionException."""
    with pytest.raises(ExtractionException) as exc_info:
        parse_html_content(JS_EMPTY_SHELL_HTML)
    assert "insufficient_content" in str(exc_info.value)

def test_snapshot_file_validation():
    """Requirement 5: Snapshot validation for extension, size, and binary data."""
    # 1. Valid snapshot
    is_valid, msg = validate_snapshot_file("page.html", b"<html><body>Hello world</body></html>")
    assert is_valid is True

    # 2. Wrong extension
    is_valid, msg = validate_snapshot_file("page.pdf", b"Some content")
    assert is_valid is False
    assert "Invalid file extension" in msg

    is_valid, msg = validate_snapshot_file("script.exe", b"Some content")
    assert is_valid is False

    # 3. Oversized file (>5MB)
    big_bytes = b"A" * (6 * 1024 * 1024)
    is_valid, msg = validate_snapshot_file("big.html", big_bytes)
    assert is_valid is False
    assert "exceeds the 5MB limit" in msg

    # 4. Binary file containing null bytes
    binary_bytes = b"<html>\x00\x01\x02<body>Malicious Binary</body></html>"
    is_valid, msg = validate_snapshot_file("binary.html", binary_bytes)
    assert is_valid is False
    assert "binary data" in msg
