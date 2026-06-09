"""Network Scanner — LAN discovery of Shogun instances.

Scans the local network for hosts running Shogun (port 8000) and
cross-references them against enrolled members to detect rogue agents.
"""

from __future__ import annotations

import asyncio
import logging
import platform
import socket
import time
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from gensui.db.models.shogun_member import ShogunMember

log = logging.getLogger("gensui.network_scanner")

# Default Shogun port
SHOGUN_PORT = 8000

# Timeouts (seconds)
TCP_CONNECT_TIMEOUT = 0.5
HTTP_IDENTIFY_TIMEOUT = 2.0

# Max concurrent probes
MAX_CONCURRENT = 60


def _get_local_subnets() -> list[str]:
    """Discover /24 subnets from the machine's own network interfaces.

    Returns a list of subnet prefixes like ["192.168.1.", "10.0.0."].
    """
    subnets: set[str] = set()
    try:
        hostname = socket.gethostname()
        # getaddrinfo returns all addresses for this host
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127."):
                continue
            # Extract /24 prefix
            parts = ip.split(".")
            if len(parts) == 4:
                prefix = ".".join(parts[:3]) + "."
                subnets.add(prefix)
    except Exception as exc:
        log.warning("Failed to discover local subnets via hostname: %s", exc)

    # Fallback: try netifaces-style approach via socket connections
    if not subnets:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split(".")
            if len(parts) == 4 and not local_ip.startswith("127."):
                subnets.add(".".join(parts[:3]) + ".")
        except Exception:
            pass

    return list(subnets)


async def _probe_tcp(ip: str, port: int, timeout: float = TCP_CONNECT_TIMEOUT) -> bool:
    """Check if a TCP port is open on a given IP. Returns True if connectable."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, OSError, ConnectionRefusedError):
        return False


async def _identify_shogun(ip: str, port: int) -> dict[str, Any] | None:
    """Try to identify a Shogun instance by hitting its health endpoint.

    Returns instance info dict or None if not a Shogun.
    """
    url = f"http://{ip}:{port}/api/v1/health"
    try:
        async with httpx.AsyncClient(timeout=HTTP_IDENTIFY_TIMEOUT) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("service") == "shogun":
                    return {
                        "version": data.get("version"),
                        "instance_name": data.get("instance_name"),
                        "shogun_id": data.get("shogun_id"),
                    }
    except Exception:
        pass

    # Fallback: try the root API endpoint
    try:
        url_root = f"http://{ip}:{port}/api/v1/version"
        async with httpx.AsyncClient(timeout=HTTP_IDENTIFY_TIMEOUT) as client:
            resp = await client.get(url_root)
            if resp.status_code == 200:
                data = resp.json()
                if "version" in data:
                    return {
                        "version": data.get("version"),
                        "instance_name": data.get("name", "Unknown"),
                        "shogun_id": data.get("shogun_id"),
                    }
    except Exception:
        pass

    return None


async def _scan_host(
    ip: str,
    port: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any] | None:
    """Scan a single host: TCP probe → HTTP identify."""
    async with semaphore:
        if not await _probe_tcp(ip, port):
            return None

        # Port is open — try to identify
        info = await _identify_shogun(ip, port)

        # Resolve hostname
        hostname = None
        try:
            hostname = socket.getfqdn(ip)
            if hostname == ip:
                hostname = None
        except Exception:
            pass

        return {
            "ip": ip,
            "port": port,
            "hostname": hostname,
            "is_shogun": info is not None,
            "version": info.get("version") if info else None,
            "instance_name": info.get("instance_name") if info else None,
            "shogun_id": info.get("shogun_id") if info else None,
        }


async def scan_network(
    session: AsyncSession,
    subnets: list[str] | None = None,
    port: int = SHOGUN_PORT,
) -> dict[str, Any]:
    """Scan the local network for Shogun instances.

    Args:
        session: Database session for cross-referencing enrolled members.
        subnets: Optional list of /24 subnet prefixes. Auto-detected if None.
        port: Port to scan (default 8000).

    Returns a dict with discovered hosts, scan metadata, and classification.
    """
    start = time.monotonic()

    # Discover subnets
    if not subnets:
        subnets = _get_local_subnets()

    if not subnets:
        return {
            "hosts": [],
            "enrolled": [],
            "unenrolled": [],
            "unknown": [],
            "subnets_scanned": [],
            "scan_duration_ms": 0,
            "error": "Could not detect local network subnets",
        }

    log.info("[NetworkScanner] Scanning subnets: %s (port %d)", subnets, port)

    # Build IP list
    ips = []
    for subnet in subnets:
        for i in range(1, 255):
            ips.append(f"{subnet}{i}")

    # Scan all IPs concurrently (with semaphore)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = [_scan_host(ip, port, semaphore) for ip in ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect discovered hosts (filter None and exceptions)
    discovered: list[dict[str, Any]] = []
    for r in results:
        if isinstance(r, dict):
            discovered.append(r)

    # Load all enrolled members for cross-reference
    result = await session.execute(
        select(ShogunMember).where(ShogunMember.enrollment_status.in_(["active", "pending"]))
    )
    members = list(result.scalars().all())

    # Build lookup sets
    enrolled_hostnames = {m.hostname for m in members if m.hostname}
    enrolled_ids = {str(m.id) for m in members}
    enrolled_names = {m.instance_name for m in members if m.instance_name}

    # Classify discovered hosts
    enrolled_hosts = []
    unenrolled_hosts = []
    unknown_hosts = []

    for host in discovered:
        if not host["is_shogun"]:
            host["classification"] = "unknown"
            unknown_hosts.append(host)
            continue

        # Check if this Shogun is enrolled
        is_enrolled = False

        # Match by shogun_id
        if host.get("shogun_id") and host["shogun_id"] in enrolled_ids:
            is_enrolled = True
            host["matched_by"] = "shogun_id"

        # Match by hostname
        elif host.get("hostname") and host["hostname"] in enrolled_hostnames:
            is_enrolled = True
            host["matched_by"] = "hostname"

        # Match by instance_name
        elif host.get("instance_name") and host["instance_name"] in enrolled_names:
            is_enrolled = True
            host["matched_by"] = "instance_name"

        # Match by IP as hostname
        elif host["ip"] in enrolled_hostnames:
            is_enrolled = True
            host["matched_by"] = "ip"

        if is_enrolled:
            host["classification"] = "enrolled"
            enrolled_hosts.append(host)
        else:
            host["classification"] = "unenrolled"
            unenrolled_hosts.append(host)

    duration_ms = int((time.monotonic() - start) * 1000)
    log.info(
        "[NetworkScanner] Scan complete: %d hosts found (%d enrolled, %d unenrolled, %d unknown) in %dms",
        len(discovered), len(enrolled_hosts), len(unenrolled_hosts), len(unknown_hosts), duration_ms,
    )

    return {
        "hosts": discovered,
        "enrolled": enrolled_hosts,
        "unenrolled": unenrolled_hosts,
        "unknown": unknown_hosts,
        "subnets_scanned": subnets,
        "total_ips_probed": len(ips),
        "scan_duration_ms": duration_ms,
        "timestamp": time.time(),
    }
