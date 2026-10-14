# GitHub: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Asynchronous proxy health checker, rotation pool, and pruning manager."""

import asyncio
from dataclasses import dataclass
from itertools import cycle
from pathlib import Path
import time
from typing import Any, Iterator, Optional
from urllib.parse import urlparse


@dataclass
class ProxyHealthResult:
    """Represents the operational health status and ping response of a proxy."""

    proxy_address: str
    is_alive: bool
    latency_ms: float
    error_message: Optional[str] = None


def normalize_proxy_address(raw_proxy_entry: str) -> str:
    """Normalize raw proxy string into a standard scheme URI.

    Parameters
    ----------
    raw_proxy_entry : str
        Proxy input string, e.g. '1.2.3.4:8080' or 'http://1.2.3.4:8080'.

    Returns
    -------
    str
        Standardized proxy URI.
    """
    cleaned_proxy_string: str = raw_proxy_entry.strip()
    if not cleaned_proxy_string:
        return ""

    if "://" not in cleaned_proxy_string:
        return f"http://{cleaned_proxy_string}"

    return cleaned_proxy_string


def load_proxies_from_file(proxy_file_path: Path | str) -> list[str]:
    """Read and sanitize proxy addresses from a file.

    Parameters
    ----------
    proxy_file_path : Path | str
        Path to the text file containing proxy addresses.

    Returns
    -------
    list[str]
        Cleaned, normalized list of unique proxy URI strings.
    """
    target_path = Path(proxy_file_path).resolve()
    if not target_path.exists() or not target_path.is_file():
        return []

    collected_proxies: list[str] = []
    seen_proxy_addresses: set[str] = set()

    try:
        with open(target_path, "r", encoding="utf-8") as proxy_file_handle:
            for raw_file_line in proxy_file_handle:
                stripped_line: str = raw_file_line.strip()
                if not stripped_line or stripped_line.startswith("#"):
                    continue

                normalized_proxy_uri: str = normalize_proxy_address(stripped_line)
                if normalized_proxy_uri and normalized_proxy_uri not in seen_proxy_addresses:
                    seen_proxy_addresses.add(normalized_proxy_uri)
                    collected_proxies.append(normalized_proxy_uri)

    except OSError:
        return []

    return collected_proxies


async def test_single_proxy(
    proxy_address: str,
    timeout_seconds: float = 3.5,
) -> ProxyHealthResult:
    """Asynchronously evaluate whether a proxy is responsive via TCP handshake.

    Parameters
    ----------
    proxy_address : str
        The proxy URI to test.
    timeout_seconds : float, optional
        Maximum duration to wait for connection in seconds, by default 3.5.

    Returns
    -------
    ProxyHealthResult
        Verification result including latency and connection status.
    """
    parsed_proxy_url = urlparse(proxy_address)
    target_host: Optional[str] = parsed_proxy_url.hostname
    target_port: int = parsed_proxy_url.port or 80

    if not target_host:
        return ProxyHealthResult(
            proxy_address=proxy_address,
            is_alive=False,
            latency_ms=0.0,
            error_message="Invalid proxy hostname",
        )

    start_timestamp: float = time.perf_counter()
    try:
        connection_coroutine = asyncio.open_connection(
            host=target_host,
            port=target_port,
        )
        stream_reader, stream_writer = await asyncio.wait_for(
            connection_coroutine,
            timeout=timeout_seconds,
        )
        elapsed_latency_ms: float = (time.perf_counter() - start_timestamp) * 1000.0

        stream_writer.close()
        await stream_writer.wait_closed()

        return ProxyHealthResult(
            proxy_address=proxy_address,
            is_alive=True,
            latency_ms=round(elapsed_latency_ms, 1),
            error_message=None,
        )

    except asyncio.TimeoutError:
        return ProxyHealthResult(
            proxy_address=proxy_address,
            is_alive=False,
            latency_ms=0.0,
            error_message="Connection timed out",
        )
    except Exception as connection_exception:
        return ProxyHealthResult(
            proxy_address=proxy_address,
            is_alive=False,
            latency_ms=0.0,
            error_message=str(connection_exception),
        )


async def check_proxies_health(
    proxy_addresses: list[str],
    max_concurrency: int = 25,
    timeout_seconds: float = 3.5,
) -> list[ProxyHealthResult]:
    """Test a list of proxies concurrently with bounded parallelism.

    Parameters
    ----------
    proxy_addresses : list[str]
        List of proxy addresses to verify.
    max_concurrency : int, optional
        Maximum concurrent asynchronous tasks, by default 25.
    timeout_seconds : float, optional
        Connection timeout per proxy, by default 3.5.

    Returns
    -------
    list[ProxyHealthResult]
        Health results for all tested proxies.
    """
    concurrency_semaphore = asyncio.Semaphore(max_concurrency)

    async def bounded_proxy_check(target_proxy: str) -> ProxyHealthResult:
        async with concurrency_semaphore:
            return await test_single_proxy(
                proxy_address=target_proxy,
                timeout_seconds=timeout_seconds,
            )

    proxy_verification_tasks = [
        bounded_proxy_check(single_proxy) for single_proxy in proxy_addresses
    ]
    return await asyncio.gather(*proxy_verification_tasks)


def prune_dead_proxies_from_file(
    proxy_file_path: Path | str,
    dead_proxy_addresses: set[str],
) -> int:
    """Remove confirmed dead proxies from proxy.txt and save the updated file.

    Parameters
    ----------
    proxy_file_path : Path | str
        Path to the proxies file.
    dead_proxy_addresses : set[str]
        Set of dead proxy addresses to remove.

    Returns
    -------
    int
        Count of dead proxies purged.
    """
    target_path = Path(proxy_file_path).resolve()
    if not target_path.exists() or not target_path.is_file():
        return 0

    normalized_dead_set: set[str] = {
        normalize_proxy_address(dead_proxy) for dead_proxy in dead_proxy_addresses
    }

    surviving_lines: list[str] = []
    removed_count: int = 0

    with open(target_path, "r", encoding="utf-8") as file_read_handle:
        for file_line in file_read_handle:
            stripped_line: str = file_line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                surviving_lines.append(file_line)
                continue

            normalized_line_uri: str = normalize_proxy_address(stripped_line)
            if normalized_line_uri in normalized_dead_set or stripped_line in normalized_dead_set:
                removed_count += 1
            else:
                surviving_lines.append(file_line)

    with open(target_path, "w", encoding="utf-8") as file_write_handle:
        file_write_handle.writelines(surviving_lines)

    return removed_count


class ProxyPool:
    """Manages round-robin rotation, failover, and health state for operational proxies."""

    def __init__(self, available_proxies: list[str]) -> None:
        self.available_proxies: list[str] = list(available_proxies)
        self.dead_proxies: set[str] = set()
        self._proxy_iterator: Iterator[str] = cycle(self.available_proxies) if self.available_proxies else iter([])

    @property
    def total_count(self) -> int:
        """Return total count of initial proxies."""
        return len(self.available_proxies)

    @property
    def has_proxies(self) -> bool:
        """Return True if proxies are available."""
        return len(self.available_proxies) > 0

    def get_next_proxy(self) -> Optional[str]:
        """Obtain the next proxy in the round-robin cycle."""
        if not self.available_proxies:
            return None
        return next(self._proxy_iterator)

    def record_dead_proxy(self, failed_proxy_address: str) -> None:
        """Record that a proxy failed during execution."""
        self.dead_proxies.add(failed_proxy_address)

    @staticmethod
    def format_requests_proxy_dictionary(proxy_uri: str) -> dict[str, str]:
        """Format proxy URI into requests dictionary format."""
        return {
            "http": proxy_uri,
            "https": proxy_uri,
        }


__all__ = [
    "ProxyHealthResult",
    "ProxyPool",
    "check_proxies_health",
    "load_proxies_from_file",
    "normalize_proxy_address",
    "prune_dead_proxies_from_file",
    "test_single_proxy",
]
