"""
ZERO-INBOX: Security, SSRF Prevention & Content Sanitization
"""

import socket
import ipaddress
import re
from urllib.parse import urlparse
from typing import Tuple
from bs4 import BeautifulSoup


# Private and reserved IP networks for SSRF defense
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),   # CGNAT, incl. Tailscale tailnet addresses
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),   # AWS/GCP cloud metadata & link-local
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),     # Multicast
    ipaddress.ip_network("240.0.0.0/4"),     # Reserved
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),        # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
]

DANGEROUS_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal",
    "169.254.169.254", "instance-data"
}


def validate_url_safe(url: str) -> Tuple[bool, str]:
    """
    Validates that a URL is safe to fetch and protects against SSRF attacks.
    Returns (is_safe, error_message).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, f"Unsupported URL scheme: {parsed.scheme}. Only http/https permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL."

        hostname_lower = hostname.lower().rstrip(".")
        if hostname_lower in DANGEROUS_HOSTS or hostname_lower.endswith((".local", ".internal", ".ts.net", ".localhost")):
            return False, f"Target host '{hostname}' is forbidden (SSRF protection)."

        # Resolve hostname to IP to verify against private subnets
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str.split("%")[0])
                # Unwrap IPv4-mapped IPv6 (::ffff:10.0.0.1) so it is checked as IPv4
                if getattr(ip_obj, "ipv4_mapped", None):
                    ip_obj = ip_obj.ipv4_mapped
                if not ip_obj.is_global:
                    return False, f"Target host resolves to non-public address: {ip_str}"
                for net in BLOCKED_NETWORKS:
                    if ip_obj in net:
                        return False, f"Target host resolves to blocked internal network: {ip_str}"
        except socket.gaierror:
            # Domain cannot be resolved; still return false for safety
            return False, f"Failed to resolve hostname: {hostname}"

        return True, ""
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"


def sanitize_html_content(raw_html: str, max_chars: int = 50000) -> str:
    """
    Strips scripts, iframes, styles, and untrusted execution tags from HTML,
    returning clean plain text or sanitized markup.
    """
    if not raw_html:
        return ""

    if len(raw_html) > max_chars * 2:
        raw_html = raw_html[:max_chars * 2]

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove dangerous elements
    for element in soup(["script", "style", "iframe", "embed", "object", "form", "svg", "button", "nav"]):
        element.decompose()

    # Extract clean text with spaced paragraphs
    text = soup.get_text(separator="\n\n")

    # Collapse multiple blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # Collapse extra horizontal spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()[:max_chars]


def sanitize_user_input(text: str, max_len: int = 500) -> str:
    """Sanitizes user input fields (e.g. search queries, topic keywords)."""
    if not text:
        return ""
    # Strip dangerous characters
    cleaned = re.sub(r"[<>\"\'`;]", "", text)
    return cleaned.strip()[:max_len]

