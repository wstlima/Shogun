"""SSRF guard — validates user-supplied URLs before outbound HTTP requests.

Resolves the hostname and rejects targets that land in private, loopback,
link-local, or cloud metadata address space. This blocks the common SSRF
vector (reaching internal services or the cloud metadata endpoint via a
user-controlled URL) but is not a complete defense against sophisticated
bypasses such as DNS rebinding after the check or HTTP redirects to a
blocked target — callers that need that level of assurance should also
disable redirect following and re-validate the final URL.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFValidationError(ValueError):
    """Raised when a URL fails SSRF validation."""


_METADATA_ADDRESSES = {
    "169.254.169.254",  # AWS/GCP/Azure/DigitalOcean cloud metadata
    "fd00:ec2::254",    # AWS IMDSv2 IPv6
}


def _is_blocked_ip(ip_str: str, *, allow_private: bool) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # unparsable — fail closed

    if ip_str in _METADATA_ADDRESSES:
        return True
    if ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    if allow_private:
        # Still block link-local (covers the metadata range 169.254.0.0/16
        # generically, beyond the well-known single address above).
        return ip.is_link_local
    return ip.is_private or ip.is_loopback or ip.is_link_local


def assert_safe_url(url: str, *, allow_private: bool = False) -> None:
    """Raise SSRFValidationError if `url` resolves to a disallowed target.

    Checks scheme (http/https only) and resolves the hostname.

    By default rejects any address in private/loopback/link-local/reserved
    ranges (RFC 1918, 127.0.0.0/8, 169.254.0.0/16, ::1, fc00::/7, etc) —
    appropriate for URLs that should only ever point to the public
    internet (e.g. remote peers contacted over A2A).

    Pass allow_private=True for callers that legitimately connect to
    services on the operator's own LAN (e.g. a self-hosted Gensui
    instance) — this still blocks cloud metadata endpoints and link-local
    addresses, but allows RFC 1918 private ranges and loopback.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SSRFValidationError(f"Unsupported URL scheme: {parsed.scheme!r}")
    if not parsed.hostname:
        raise SSRFValidationError("URL has no hostname")

    try:
        addr_infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise SSRFValidationError(f"Could not resolve host {parsed.hostname!r}: {exc}") from exc

    for family, _, _, _, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str, allow_private=allow_private):
            raise SSRFValidationError(
                f"URL host {parsed.hostname!r} resolves to disallowed address {ip_str}"
            )
