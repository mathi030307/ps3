import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple

class SecurityException(Exception):
    """Custom exception for security violations with safe messages."""
    pass

FORBIDDEN_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "metadata.google.internal",
    "instance-data",
}

def is_ip_private_or_restricted(ip_str: str) -> bool:
    """
    Checks if an IP address string is private, loopback, link-local,
    reserved, multicast, carrier-grade NAT, IPv4-mapped IPv6, or cloud metadata.
    """
    try:
        # Strip brackets if IPv6
        clean_ip = ip_str.strip("[]")
        ip = ipaddress.ip_address(clean_ip)

        # Check IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            return is_ip_private_or_restricted(str(ip.ipv4_mapped))

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return True

        # Check AWS / GCP / Azure metadata endpoint explicitly (169.254.169.254)
        if str(ip) == "169.254.169.254":
            return True

        # Carrier Grade NAT: 100.64.0.0/10
        if isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network("100.64.0.0/10"):
            return True

        return False
    except ValueError:
        return True

def validate_url_for_ssrf(url: str) -> Tuple[bool, str]:
    """
    Validates a URL against SSRF vulnerabilities:
    - Scheme must be HTTP or HTTPS
    - Hostname must resolve to a valid, public, non-restricted IP address
    Returns (is_valid, error_reason_if_invalid)
    """
    if not url or not isinstance(url, str):
        return False, "Invalid URL provided."

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return False, "Only HTTP and HTTPS URLs are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL lacks a valid hostname."

    hostname_clean = hostname.strip().lower().rstrip(".")

    if hostname_clean in FORBIDDEN_HOSTNAMES:
        return False, "Access to internal or local hostnames is prohibited."

    # Direct IP literal check
    try:
        ip = ipaddress.ip_address(hostname_clean.strip("[]"))
        if is_ip_private_or_restricted(str(ip)):
            return False, "Target IP address is in a restricted or private network."
    except ValueError:
        # Not a raw IP literal, proceed to DNS resolution
        pass

    # Resolve hostname via DNS and check all returned IPs
    try:
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        addr_info = socket.getaddrinfo(hostname_clean, port, proto=socket.IPPROTO_TCP)
        if not addr_info:
            return False, "Hostname could not be resolved."

        for item in addr_info:
            sockaddr = item[4]
            ip_str = sockaddr[0]
            if is_ip_private_or_restricted(ip_str):
                return False, "Resolved IP address is in a restricted or private network."
    except socket.gaierror:
        return False, "Failed to resolve domain name."
    except Exception:
        return False, "Network security verification failed."

    return True, ""
