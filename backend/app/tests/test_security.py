import pytest
import httpx
from unittest.mock import patch, MagicMock
from backend.app.core.security import is_ip_private_or_restricted, validate_url_for_ssrf
from backend.app.services.extraction import fetch_html_from_url, ExtractionException
from backend.app.core.security import SecurityException

def test_private_and_restricted_ip_detection():
    # Loopbacks
    assert is_ip_private_or_restricted("127.0.0.1") is True
    assert is_ip_private_or_restricted("127.0.1.1") is True
    assert is_ip_private_or_restricted("::1") is True

    # Private subnets
    assert is_ip_private_or_restricted("10.0.0.1") is True
    assert is_ip_private_or_restricted("192.168.1.1") is True
    assert is_ip_private_or_restricted("172.16.0.5") is True

    # Cloud metadata endpoint
    assert is_ip_private_or_restricted("169.254.169.254") is True

    # Carrier-grade NAT (100.64.0.0/10)
    assert is_ip_private_or_restricted("100.64.0.1") is True
    assert is_ip_private_or_restricted("100.127.255.255") is True

    # Public IPs
    assert is_ip_private_or_restricted("8.8.8.8") is False
    assert is_ip_private_or_restricted("1.1.1.1") is False

def test_ipv4_mapped_ipv6():
    """Requirement 4: Tests for IPv4-mapped IPv6 addresses."""
    assert is_ip_private_or_restricted("::ffff:127.0.0.1") is True
    assert is_ip_private_or_restricted("::ffff:10.0.0.1") is True
    assert is_ip_private_or_restricted("::ffff:169.254.169.254") is True
    assert is_ip_private_or_restricted("::ffff:192.168.0.1") is True
    assert is_ip_private_or_restricted("::ffff:8.8.8.8") is False

def test_dns_resolving_to_private_ip():
    """Requirement 4: Tests DNS resolving to a private IP is blocked."""
    with patch("socket.getaddrinfo") as mock_dns:
        mock_dns.return_value = [
            (2, 1, 6, "", ("10.0.0.5", 80))
        ]
        is_valid, err = validate_url_for_ssrf("http://internal-domain.com/page")
        assert is_valid is False
        assert "restricted or private" in err

def test_forbidden_schemes():
    assert validate_url_for_ssrf("ftp://example.com")[0] is False
    assert validate_url_for_ssrf("file:///etc/passwd")[0] is False
    assert validate_url_for_ssrf("gopher://example.com")[0] is False
    assert validate_url_for_ssrf("javascript:alert(1)")[0] is False

@pytest.mark.asyncio
async def test_redirect_to_private_ip_is_blocked():
    """Requirement 4: Tests redirection to a private IP is blocked."""
    # First hop is public, but redirects to 127.0.0.1
    with patch("backend.app.services.extraction.validate_url_for_ssrf") as mock_val:
        # Step 1 passes (public), Step 2 fails on redirect
        mock_val.side_effect = [(True, ""), (False, "Target IP is in a restricted network")]
        
        # Mock client to return redirect response
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.is_redirect = True
            mock_resp.headers = {"location": "http://127.0.0.1/admin"}
            mock_resp.url = httpx.URL("https://example.com")
            mock_get.return_value = mock_resp

            with pytest.raises(SecurityException) as exc_info:
                await fetch_html_from_url("https://example.com")
            assert "SSRF Protection" in str(exc_info.value)

@pytest.mark.asyncio
async def test_non_html_content_type_rejected():
    """Requirement 4: Tests rejection of non-HTML content types."""
    with patch("backend.app.services.extraction.validate_url_for_ssrf", return_value=(True, "")):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.is_redirect = False
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/pdf"}
            mock_resp.content = b"%PDF-1.4 binary content"
            mock_get.return_value = mock_resp

            with pytest.raises(ExtractionException) as exc_info:
                await fetch_html_from_url("https://example.com/document.pdf")
            assert "non-HTML" in str(exc_info.value)

@pytest.mark.asyncio
async def test_fetch_timeout_handling():
    """Requirement 4: Tests handling of fetch timeouts."""
    with patch("backend.app.services.extraction.validate_url_for_ssrf", return_value=(True, "")):
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Read timed out")):
            with pytest.raises(ExtractionException) as exc_info:
                await fetch_html_from_url("https://slow-website.com")
            assert "timed out" in str(exc_info.value)

@pytest.mark.asyncio
async def test_response_size_cap_exceeded():
    """Requirement 4: Tests rejection when response exceeds 5MB."""
    with patch("backend.app.services.extraction.validate_url_for_ssrf", return_value=(True, "")):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.is_redirect = False
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "text/html"}
            mock_resp.content = b"A" * (6 * 1024 * 1024)  # 6MB
            mock_get.return_value = mock_resp

            with pytest.raises(ExtractionException) as exc_info:
                await fetch_html_from_url("https://example.com/oversized")
            assert "exceeds maximum allowed size" in str(exc_info.value)
