# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Non-intrusive service endpoint health and reachability checker."""

import asyncio
from dataclasses import dataclass
import time
from typing import Final, Optional
from urllib.parse import urlparse

import requests

SERVICE_ENDPOINTS: Final[dict[str, str]] = {
    "divar": "https://api.divar.ir",
    "tapsi_passenger": "https://accounts-api.tapsi.ir",
    "tapsi_biker": "https://tap33.me",
    "tapsi_driver": "https://api.tapsi.ir",
    "trob": "https://api.torob.com",
    "sheypoor": "https://www.sheypoor.com",
    "sheypoor_app_link": "https://www.sheypoor.com",
    "okcs": "https://okcs.com",
    "alibaba": "https://ws.alibaba.ir",
    "oketab": "https://www.oketab.com",
    "GapFilm": "https://core.gapfilm.ir",
    "FilmNet": "https://tv.filmnet.ir",
    "DrDr": "https://drdr.ir",
    "drsaina": "https://www.drsaina.com",
    "itoll_app_link": "https://app.itoll.com",
    "anar360": "https://anar360.com",
    "azki": "https://www.azki.com",
    "Nashr_olgoo": "https://www.olgoobooks.ir",
    "banimode": "https://mobapi.banimode.com",
    "lendo": "https://api.lendoco.ir",
    "basalam": "https://auth.basalam.com",
    "see5": "https://crm.see5.net",
    "bimito": "https://bimito.com",
    "sibirani": "https://sandbox.sibirani.com",
    "hamrah_mechanic": "https://www.hamrah-mechanic.com",
    "varzesh3": "https://sso.varzesh3.com",
    "digikala": "https://api.digikala.com",
    "telewebion": "https://gateway.telewebion.com",
    "pindo": "https://api.pindo.ir",
    "classino": "https://panel.classino.com",
    "goftino": "https://my.goftino.com",
    "snapp_app_link": "https://snapp.ir",
    "snapp_login_page": "https://app.snapp.taxi",
    "snapp_worker_login_page": "https://digitalsignup.snapp.ir",
    "snapp_food": "https://snappfood.ir",
    "snapp_market": "https://snapp.market",
    "snapp_trip": "https://www.snapptrip.com",
    "itoll": "https://itoll.com",
    "buskool": "https://www.buskool.com",
    "nobat": "https://user.nobat.ir",
    "mihanpezeshk_patients": "https://www.mihanpezeshk.com",
    "mihanpezeshk_doctor": "https://www.mihanpezeshk.com",
    "filimo": "https://www.filimo.com",
    "pooleno": "https://pooleno.ir",
}


@dataclass
class ServiceHealthResult:
    """Represents endpoint reachability and latency status."""

    service_name: str
    endpoint_url: str
    is_reachable: bool
    status_code: Optional[int]
    latency_ms: float
    error_message: Optional[str] = None


def check_single_endpoint(
    service_name: str,
    endpoint_url: str,
    timeout_seconds: float = 5.0,
) -> ServiceHealthResult:
    """Perform a non-intrusive HEAD/GET request to verify service endpoint availability."""
    start_time = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) S-Bomber-HealthCheck/1.2.0",
        "Accept": "*/*",
    }
    try:
        # First attempt HEAD for minimal bandwidth; fall back to GET if 405/rejected
        response = requests.head(endpoint_url, headers=headers, timeout=timeout_seconds, allow_redirects=True)
        if response.status_code == 405:
            response = requests.get(endpoint_url, headers=headers, timeout=timeout_seconds, allow_redirects=True)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        # Anything not a connection/server failure is considered reachable
        is_reachable = response.status_code < 500

        return ServiceHealthResult(
            service_name=service_name,
            endpoint_url=endpoint_url,
            is_reachable=is_reachable,
            status_code=response.status_code,
            latency_ms=round(elapsed_ms, 1),
            error_message=None if is_reachable else f"HTTP {response.status_code}",
        )

    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return ServiceHealthResult(
            service_name=service_name,
            endpoint_url=endpoint_url,
            is_reachable=False,
            status_code=None,
            latency_ms=round(elapsed_ms, 1),
            error_message="Connection timed out",
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return ServiceHealthResult(
            service_name=service_name,
            endpoint_url=endpoint_url,
            is_reachable=False,
            status_code=None,
            latency_ms=round(elapsed_ms, 1),
            error_message=str(exc)[:40],
        )


def check_all_services(
    selected_services: Optional[list[str]] = None,
    timeout_seconds: float = 5.0,
) -> list[ServiceHealthResult]:
    """Test reachability across specified or all configured provider endpoints."""
    target_services: dict[str, str] = {}
    if selected_services:
        normalized_targets = {s.strip().lower() for s in selected_services}
        target_services = {
            s: url for s, url in SERVICE_ENDPOINTS.items() if s.lower() in normalized_targets
        }
    else:
        target_services = dict(SERVICE_ENDPOINTS)

    results: list[ServiceHealthResult] = []
    for service_name, endpoint_url in target_services.items():
        results.append(check_single_endpoint(service_name, endpoint_url, timeout_seconds=timeout_seconds))

    return results


__all__ = [
    "SERVICE_ENDPOINTS",
    "ServiceHealthResult",
    "check_all_services",
    "check_single_endpoint",
]
