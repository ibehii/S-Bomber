# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Public proxy scraper, live async validator, and proxy.txt updater."""

import asyncio
from pathlib import Path
import re
from typing import Final, Optional

import requests

from lib.proxy_manager import (
    ProxyHealthResult,
    check_proxies_health,
    load_proxies_from_file,
    normalize_proxy_address,
)

DEFAULT_PUBLIC_PROXY_SOURCES: Final[list[str]] = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
]

PROXY_REGEX: Final[re.Pattern] = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b"
)


def fetch_raw_proxies_from_source(source_url: str, timeout_seconds: float = 10.0) -> list[str]:
    """Fetch raw proxy list text from a remote URL."""
    try:
        response = requests.get(source_url, timeout=timeout_seconds)
        response.raise_for_status()
        found_matches: list[str] = PROXY_REGEX.findall(response.text)
        return found_matches
    except Exception:
        return []


def fetch_all_public_proxies(
    sources: Optional[list[str]] = None,
    max_candidates: int = 150,
) -> list[str]:
    """Fetch and deduplicate raw candidate proxies from public repositories."""
    sources_to_scrape = sources if sources else DEFAULT_PUBLIC_PROXY_SOURCES
    candidate_proxies: list[str] = []
    seen: set[str] = set()

    for source_url in sources_to_scrape:
        found_proxies = fetch_raw_proxies_from_source(source_url)
        for proxy_str in found_proxies:
            norm = normalize_proxy_address(proxy_str)
            if norm and norm not in seen:
                seen.add(norm)
                candidate_proxies.append(norm)
                if len(candidate_proxies) >= max_candidates:
                    break
        if len(candidate_proxies) >= max_candidates:
            break

    return candidate_proxies


def update_proxy_file_with_live_proxies(
    destination_file: Path | str,
    max_working_proxies: int = 25,
    timeout_seconds: float = 3.0,
    sources: Optional[list[str]] = None,
) -> list[ProxyHealthResult]:
    """Scrape public proxies, concurrently verify latency, and save alive nodes to file.

    Parameters
    ----------
    destination_file : Path | str
        Target file path (e.g. proxy.txt).
    max_working_proxies : int, optional
        Maximum number of verified working proxies to retain, by default 25.
    timeout_seconds : float, optional
        Health check connection timeout in seconds, by default 3.0.
    sources : Optional[list[str]], optional
        Custom list of source URLs to scrape, by default None.

    Returns
    -------
    list[ProxyHealthResult]
        Verified alive proxies sorted by latency.
    """
    candidates = fetch_all_public_proxies(sources=sources)
    if not candidates:
        return []

    # Run concurrent health check
    health_results: list[ProxyHealthResult] = asyncio.run(
        check_proxies_health(candidates, timeout_seconds=timeout_seconds, max_concurrency=30)
    )

    alive_proxies = [res for res in health_results if res.is_alive]
    # Sort alive proxies by lowest latency
    alive_proxies.sort(key=lambda r: r.latency_ms)

    best_proxies = alive_proxies[:max_working_proxies]

    dest_path = Path(destination_file).resolve()
    # Write cleanly to file
    file_content_lines = [
        "# S-Bomber Verified Proxy List",
        f"# Auto-updated with top {len(best_proxies)} operational nodes (sorted by latency)",
        "#",
    ]
    for p in best_proxies:
        file_content_lines.append(p.proxy_address)

    file_content_lines.append("")
    dest_path.write_text("\n".join(file_content_lines), encoding="utf-8")

    return best_proxies


__all__ = [
    "DEFAULT_PUBLIC_PROXY_SOURCES",
    "fetch_all_public_proxies",
    "fetch_raw_proxies_from_source",
    "update_proxy_file_with_live_proxies",
]
