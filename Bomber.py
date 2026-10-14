# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Main command-line interface entry point for S-Bomber."""

import io
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import time
from typing import Any, Final, Optional
import zipfile

import click

# Graceful terminal color handling
try:
    from colorama import Fore, Style
except ImportError:
    class Fore:  # type: ignore[no-redef]
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        RESET = "\033[39m"

    class Style:  # type: ignore[no-redef]
        RESET_ALL = "\033[0m"
        BRIGHT = "\033[1m"

try:
    import pyfiglet
except ImportError:
    pyfiglet = None  # type: ignore[assignment]

try:
    from Rcolor import standard_fg
except ImportError:
    def standard_fg(display_text: str) -> str:
        return display_text

try:
    import requests
    from requests import Response
except ImportError:
    requests = None  # type: ignore[assignment]
    Response = None  # type: ignore[assignment, misc]

from lib import IranianSMS, IranianWebSMS, bomb_exceptions
from lib.config_loader import load_configuration
from lib.dashboard import DispatchDashboard
from lib.proxy_manager import (
    ProxyHealthResult,
    ProxyPool,
    check_proxies_health,
    load_proxies_from_file,
    prune_dead_proxies_from_file,
)
from lib.proxy_updater import update_proxy_file_with_live_proxies
from lib.reporter import export_benchmark_report
from lib.service_checker import ServiceHealthResult, check_all_services
from lib.service_tags import get_available_tags, get_services_by_tags

PERSIAN_AND_ARABIC_DIGIT_TRANSLATION_TABLE: Final[dict[int, int]] = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def clear_terminal_screen() -> None:
    """Clear the terminal screen safely across POSIX and Windows systems when attached to a TTY."""
    if not sys.stdout.isatty():
        return
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def normalize_iranian_phone_number(raw_phone_input: str) -> str:
    """Validate and normalize Iranian mobile phone numbers to standard 11-digit format.

    Supported input formats:
    - '09123456789' (standard domestic format, 11 digits)
    - '989123456789' (international format without plus, 12 digits)
    - '+989123456789' (international format with plus, 13 characters)
    - '9123456789' (trunk-less format, 10 digits)
    - '۰۹۱۲۳۴۵۶۷۸۹' or '٠٩١٢٣٤٥٦٧٨٩' (Persian / Arabic numerals)

    Parameters
    ----------
    raw_phone_input : str
        The raw phone number entered by the user.

    Returns
    -------
    str
        Normalized 11-digit mobile number beginning with '09'.

    Raises
    ------
    ValueError
        If the input is empty, non-numeric, or does not match an Iranian mobile pattern.
    """
    cleaned_phone_number: str = (
        raw_phone_input.strip()
        .translate(PERSIAN_AND_ARABIC_DIGIT_TRANSLATION_TABLE)
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
    )

    if not cleaned_phone_number:
        raise ValueError("Phone number cannot be empty.")

    if not cleaned_phone_number.isnumeric():
        raise ValueError("Phone number must contain digits only.")

    # Format: +989... or 989... (12 digits)
    if cleaned_phone_number.startswith("98"):
        if not cleaned_phone_number.startswith("989"):
            raise ValueError(
                "Invalid Iranian mobile prefix. Iranian mobile numbers begin with 989."
            )
        if len(cleaned_phone_number) != 12:
            raise ValueError(
                f"Expected 12 digits for international format (98...), got {len(cleaned_phone_number)}."
            )
        return "0" + cleaned_phone_number[2:]

    # Format: 09... (11 digits)
    if cleaned_phone_number.startswith("09"):
        if len(cleaned_phone_number) != 11:
            raise ValueError(
                f"Expected 11 digits for domestic format (09...), got {len(cleaned_phone_number)}."
            )
        return cleaned_phone_number

    # Format: 9... (10 digits)
    if cleaned_phone_number.startswith("9"):
        if len(cleaned_phone_number) != 10:
            raise ValueError(
                f"Expected 10 digits without trunk zero, got {len(cleaned_phone_number)}."
            )
        return "0" + cleaned_phone_number

    raise ValueError(
        "Invalid phone number. Iranian mobile numbers must start with 09, 989, or +989."
    )


def display_startup_banner() -> None:
    """Render startup banner and author attribution to stdout."""
    current_script_directory: Path = Path(__file__).parent.resolve()
    banner_text: str = ""

    if pyfiglet is not None:
        local_bundled_font: Path = current_script_directory / "ANSI Shadow.flf"
        pyfiglet_fonts_directory: Path = (
            Path(pyfiglet.__file__).parent.resolve() / "fonts"
        )
        custom_font_file: Path = pyfiglet_fonts_directory / "ANSI Shadow.flf"

        if not custom_font_file.exists() and local_bundled_font.exists():
            try:
                shutil.copy(local_bundled_font, custom_font_file)
            except (OSError, PermissionError):
                pass

        try:
            if custom_font_file.exists():
                banner_text = pyfiglet.figlet_format("S-Bomber", font="ANSI Shadow")
            else:
                banner_text = pyfiglet.figlet_format("S-Bomber", font="standard")
        except Exception:
            banner_text = ""

    if not banner_text:
        banner_text = (
            "  ____      ____                  _               \n"
            " / ___|    | __ )  ___  _ __ ___ | |__   ___ _ __ \n"
            " \\___ \\ ___|  _ \\ / _ \\| '_ ` _ \\| '_ \\ / _ \\ '__|\n"
            "  ___) |___| |_) | (_) | | | | | | |_) |  __/ |   \n"
            " |____/    |____/ \\___/|_| |_| |_|_.__/ \\___|_|   \n"
        )

    print(standard_fg(banner_text))
    print(
        Fore.MAGENTA
        + "- My telegram : t.me/dr_xz -\n"
        + "- My github   : https://github.com/ibehii -\n\n"
        + Fore.YELLOW
        + "------------ # v1.2.0 # ------------  \n"
        + Fore.RESET
    )


def resolve_and_download_geckodriver(destination_directory: Path) -> Optional[Path]:
    """Identify host platform and download matching geckodriver binary.

    Parameters
    ----------
    destination_directory : Path
        Directory where geckodriver binary will be placed.

    Returns
    -------
    Optional[Path]
        Path to extracted executable if successful, None otherwise.
    """
    if requests is None:
        print(Fore.RED + "The requests package is required to download geckodriver." + Fore.RESET)
        return None

    current_operating_system: str = platform.system()
    current_architecture: str = platform.machine().lower()

    platform_download_urls: dict[tuple[str, str], str] = {
        ("Linux", "x86_64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
        ),
        ("Linux", "arm64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux-aarch64.tar.gz"
        ),
        ("Linux", "aarch64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux-aarch64.tar.gz"
        ),
        ("Darwin", "x86_64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-macos.tar.gz"
        ),
        ("Darwin", "arm64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-macos-aarch64.tar.gz"
        ),
        ("Windows", "x86_64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-win64.zip"
        ),
        ("Windows", "x86"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-win32.zip"
        ),
        ("Windows", "arm64"): (
            "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-win-aarch64.zip"
        ),
    }

    # Normalize architecture key
    if current_architecture in ("x86_64", "amd64"):
        normalized_architecture: str = "x86_64"
    elif current_architecture in ("aarch64", "arm64"):
        normalized_architecture = "arm64"
    elif current_architecture in ("x86", "i386", "i686"):
        normalized_architecture = "x86"
    else:
        normalized_architecture = current_architecture

    target_platform_key: tuple[str, str] = (
        current_operating_system,
        normalized_architecture,
    )
    download_url: Optional[str] = platform_download_urls.get(target_platform_key)

    if download_url is None:
        print(
            Fore.RED
            + f"Unsupported platform: {current_operating_system} {current_architecture}. "
            + "Please install geckodriver manually."
            + Fore.RESET
        )
        return None

    executable_name: str = "geckodriver.exe" if current_operating_system == "Windows" else "geckodriver"
    final_executable_path: Path = destination_directory / executable_name

    try:
        print(Fore.YELLOW + f"Downloading geckodriver from {download_url}..." + Fore.RESET)
        network_response: Response = requests.get(download_url, timeout=45.0)
        network_response.raise_for_status()
        archive_bytes: io.BytesIO = io.BytesIO(network_response.content)

        if download_url.endswith(".tar.gz"):
            with tarfile.open(fileobj=archive_bytes, mode="r:gz") as tar_archive:
                for member_entry in tar_archive.getmembers():
                    if member_entry.name.endswith("geckodriver"):
                        extracted_file = tar_archive.extractfile(member_entry)
                        if extracted_file is not None:
                            with open(final_executable_path, "wb") as target_binary:
                                shutil.copyfileobj(extracted_file, target_binary)
                        break
        elif download_url.endswith(".zip"):
            with zipfile.ZipFile(archive_bytes) as zip_archive:
                for zip_entry in zip_archive.namelist():
                    if zip_entry.endswith("geckodriver.exe"):
                        with zip_archive.open(zip_entry) as source_binary, open(
                            final_executable_path, "wb"
                        ) as target_binary:
                            shutil.copyfileobj(source_binary, target_binary)
                        break

        if final_executable_path.exists():
            final_executable_path.chmod(0o755)
            print(Fore.GREEN + f"Successfully installed geckodriver at {final_executable_path}" + Fore.RESET)
            return final_executable_path

    except Exception as download_failure:
        print(Fore.RED + f"Failed to download geckodriver: {download_failure}" + Fore.RESET)

    return None


def run_http_sms_bomber(
    target_phone_number: str,
    request_interval_seconds: float = 1.6,
    request_timeout_seconds: float = 10.0,
    selected_services: Optional[list[str]] = None,
    proxy_pool: Optional[ProxyPool] = None,
    dashboard: Optional[DispatchDashboard] = None,
) -> int:
    """Execute verification requests through direct HTTP API endpoints with proxy failover.

    Parameters
    ----------
    target_phone_number : str
        Normalized 11-digit Iranian mobile number.
    request_interval_seconds : float, optional
        Delay in seconds between requests, by default 1.6.
    request_timeout_seconds : float, optional
        HTTP request timeout in seconds, by default 10.0.
    selected_services : Optional[list[str]], optional
        List of specific service names to filter, by default None.
    proxy_pool : Optional[ProxyPool], optional
        Proxy pool for round-robin rotation and failover, by default None.
    dashboard : Optional[DispatchDashboard], optional
        Live telemetry dashboard instance, by default None.

    Returns
    -------
    int
        Total number of successfully initiated requests.
    """
    successful_requests_count: int = 0
    current_proxy: Optional[str] = proxy_pool.get_next_proxy() if proxy_pool and proxy_pool.has_proxies else None

    with IranianSMS(
        phone_number=target_phone_number,
        request_timeout=request_timeout_seconds,
        proxy_url=current_proxy,
    ) as iranian_sms_sender:
        provider_service_names: list[str] = iranian_sms_sender.filter_service_methods(selected_services)

        for provider_service_name in provider_service_names:
            # Rotate proxy per request if pool is active
            if proxy_pool and proxy_pool.has_proxies:
                current_proxy = proxy_pool.get_next_proxy()
                iranian_sms_sender.set_proxy(current_proxy)

            provider_service_callable = getattr(iranian_sms_sender, provider_service_name)
            request_start_time: float = time.perf_counter()
            is_success: bool = False
            status_label: str = "Success"

            try:
                provider_service_callable()
                is_success = True
            except ConnectionError:
                if current_proxy and proxy_pool:
                    proxy_pool.record_dead_proxy(current_proxy)
                    if dashboard is not None:
                        dashboard.record_dead_proxy()
                status_label = "Connection Error"
            except bomb_exceptions.BombClientError as client_err:
                code_suffix = f" ({client_err.status_code})" if getattr(client_err, "status_code", None) else ""
                status_label = f"Client Error{code_suffix}"
            except bomb_exceptions.BombServerError as server_err:
                code_suffix = f" ({server_err.status_code})" if getattr(server_err, "status_code", None) else ""
                status_label = f"Server Error{code_suffix}"
            except Exception as general_err:
                status_label = str(general_err)[:25]

            elapsed_latency_ms: float = (time.perf_counter() - request_start_time) * 1000.0

            if is_success:
                successful_requests_count += 1

            if dashboard is not None:
                dashboard.record_result(
                    service_name=provider_service_name,
                    engine="HTTP",
                    is_success=is_success,
                    latency_ms=elapsed_latency_ms,
                    status_label=status_label,
                    proxy=current_proxy,
                )
            else:
                if is_success:
                    print(
                        Fore.YELLOW
                        + "[+]"
                        + Fore.MAGENTA
                        + " - "
                        + Fore.GREEN
                        + f"Verification code sent through {provider_service_name} Successfully"
                        + Fore.RESET
                    )
                else:
                    print(
                        Fore.RED
                        + "[-] - "
                        + f"Couldn't send Verification code through {provider_service_name}! {status_label}"
                        + Fore.RESET
                    )

            time.sleep(request_interval_seconds)

    return successful_requests_count


def run_browser_sms_bomber(
    target_phone_number: str,
    request_interval_seconds: float = 1.6,
    browser_type: str = "chrome",
    is_headless: bool = True,
    fast_mode: bool = True,
    selected_services: Optional[list[str]] = None,
    proxy_url: Optional[str] = None,
    dashboard: Optional[DispatchDashboard] = None,
) -> int:
    """Execute browser-dependent verification code requests using Selenium.

    Parameters
    ----------
    target_phone_number : str
        Normalized 11-digit Iranian mobile number.
    request_interval_seconds : float, optional
        Delay in seconds between browser actions, by default 1.6.
    browser_type : str, optional
        Browser engine to automate ('chrome' or 'firefox'), by default 'chrome'.
    is_headless : bool, optional
        Run browser headless, by default True.
    fast_mode : bool, optional
        Enable performance optimizations (eager DOM, disable images), by default True.
    selected_services : Optional[list[str]], optional
        List of specific service names to filter, by default None.
    proxy_url : Optional[str], optional
        Proxy URI for browser traffic, by default None.
    dashboard : Optional[DispatchDashboard], optional
        Live telemetry dashboard instance, by default None.

    Returns
    -------
    int
        Total number of successfully initiated browser requests.
    """
    successful_browser_requests_count: int = 0
    current_workspace_directory: Path = Path(__file__).parent.resolve()

    try:
        from selenium.common.exceptions import WebDriverException
    except ImportError:
        print(
            Fore.RED
            + 'Selenium is missing. Run "pip install -r requirements.txt" to enable browser automation.'
            + Fore.RESET
        )
        return 0

    try:
        with IranianWebSMS(
            phone_number=target_phone_number,
            browser_type=browser_type,
            is_headless=is_headless,
            fast_mode=fast_mode,
            proxy_url=proxy_url,
        ) as web_sms_sender:
            browser_service_names: list[str] = web_sms_sender.filter_service_methods(selected_services)

            for browser_service_name in browser_service_names:
                browser_service_callable = getattr(web_sms_sender, browser_service_name)
                browser_start_time: float = time.perf_counter()
                is_operation_successful: bool = False

                try:
                    is_operation_successful = bool(browser_service_callable())
                except Exception:
                    is_operation_successful = False

                elapsed_browser_latency_ms: float = (time.perf_counter() - browser_start_time) * 1000.0

                if is_operation_successful:
                    successful_browser_requests_count += 1

                if dashboard is not None:
                    dashboard.record_result(
                        service_name=browser_service_name,
                        engine="Browser",
                        is_success=is_operation_successful,
                        latency_ms=elapsed_browser_latency_ms,
                        status_label="Success" if is_operation_successful else "Browser Failed",
                        proxy=proxy_url,
                    )
                else:
                    if is_operation_successful:
                        print(
                            Fore.YELLOW
                            + "[+]"
                            + Fore.MAGENTA
                            + " - "
                            + Fore.GREEN
                            + f"Browser verification code sent through {browser_service_name} Successfully"
                            + Fore.RESET
                        )
                    else:
                        print(
                            Fore.RED
                            + "[-] - "
                            + f"Couldn't send browser verification code through {browser_service_name}!"
                            + Fore.RESET
                        )

                time.sleep(request_interval_seconds)

    except ImportError as import_error:
        print(Fore.RED + f"Browser component unavailable: {import_error}" + Fore.RESET)
    except WebDriverException as webdriver_error:
        print(
            Fore.RED
            + f"Browser webdriver error: {webdriver_error}.\n"
            + "Ensure Chrome or Firefox is installed and matching driver is present."
            + Fore.RESET
        )
        try:
            user_permission_input: str = input(
                Fore.GREEN + "Would you like to install geckodriver automatically? [Y/n] " + Fore.RESET
            )
        except (KeyboardInterrupt, EOFError):
            print(Fore.YELLOW + "\nGeckodriver installation skipped." + Fore.RESET)
            return 0

        if user_permission_input.strip().lower() in ("y", "yes", ""):
            downloaded_driver_path = resolve_and_download_geckodriver(current_workspace_directory)
            if downloaded_driver_path is not None:
                print(
                    Fore.GREEN
                    + "Driver installed. Re-running browser services..."
                    + Fore.RESET
                )
                return run_browser_sms_bomber(
                    target_phone_number=target_phone_number,
                    request_interval_seconds=request_interval_seconds,
                    browser_type="firefox",
                    is_headless=is_headless,
                    fast_mode=fast_mode,
                    selected_services=selected_services,
                    proxy_url=proxy_url,
                )

    return successful_browser_requests_count


def display_interactive_main_menu() -> int:
    """Render the 4-choice interactive ASCII main menu.

    Returns
    -------
    int
        Selected menu item (1: Start, 2: Check & Clean Proxies, 3: View Settings, 4: Exit).
    """
    print(Fore.CYAN + "\n=============================================" + Fore.RESET)
    print(Fore.YELLOW + "           S-BOMBER MAIN MENU                " + Fore.RESET)
    print(Fore.CYAN + "=============================================" + Fore.RESET)
    print(Fore.GREEN + " [1]" + Fore.WHITE + " Start SMS Dispatch")
    print(Fore.GREEN + " [2]" + Fore.WHITE + " Check & Clean Proxies (Async Health Check)")
    print(Fore.GREEN + " [3]" + Fore.WHITE + " View Current Settings (config.toml)")
    print(Fore.GREEN + " [4]" + Fore.WHITE + " Exit")
    print(Fore.CYAN + "=============================================" + Fore.RESET)
    try:
        user_choice = click.prompt(
            Fore.GREEN + "Select an option [1-4]" + Fore.RESET,
            type=int,
            default=1,
        )
        return user_choice
    except (KeyboardInterrupt, EOFError):
        print(Fore.YELLOW + "\nOperation aborted by user." + Fore.RESET)
        sys.exit(0)


# ==================== Click Command-Line Interface ==================== #

@click.group(invoke_without_command=True)
@click.option(
    "-p",
    "--phone",
    type=str,
    default=None,
    help="Target Iranian phone number (e.g., 09123456789, +989123456789).",
)
@click.option(
    "-i",
    "--interval",
    type=float,
    default=None,
    help="Delay in seconds between consecutive requests.",
)
@click.option(
    "-t",
    "--timeout",
    type=float,
    default=None,
    help="HTTP request timeout in seconds.",
)
@click.option(
    "-d",
    "--driver",
    type=click.Choice(["chrome", "firefox"], case_sensitive=False),
    default=None,
    help="Browser automation engine driver ('chrome' or 'firefox').",
)
@click.option(
    "-s",
    "--services",
    type=str,
    default=None,
    help="Comma-separated list of services to target (e.g. divar,snapp_food).",
)
@click.option(
    "-g",
    "--tags",
    type=str,
    default=None,
    help="Comma-separated category tags to target (e.g. transport,marketplace,food).",
)
@click.option(
    "--proxy-file",
    type=click.Path(),
    default=None,
    help="Path to proxy file containing one proxy per line.",
)
@click.option(
    "--only-browser",
    is_flag=True,
    default=False,
    help="Run only browser automation phase and skip HTTP API services.",
)
@click.option(
    "--no-browser",
    is_flag=True,
    default=False,
    help="Skip browser automation phase and run only HTTP API services.",
)
@click.option(
    "--headless/--no-headless",
    default=None,
    help="Run browser in headless mode or display GUI window.",
)
@click.option(
    "--rich/--no-rich",
    "use_rich",
    default=None,
    help="Enable or disable live Rich terminal dashboard.",
)
@click.option(
    "--export/--no-export",
    "export_report",
    default=None,
    help="Export benchmark telemetry report after execution.",
)
@click.option(
    "--export-format",
    type=click.Choice(["json", "csv", "md"], case_sensitive=False),
    default=None,
    help="Benchmark report export format (json, csv, md).",
)
@click.option(
    "--reports-dir",
    type=click.Path(),
    default=None,
    help="Directory to save benchmark reports.",
)
@click.option(
    "-r",
    "--rounds",
    type=int,
    default=None,
    help="Number of benchmark rounds to execute.",
)
@click.option(
    "--round-interval",
    type=float,
    default=None,
    help="Interval delay in seconds between consecutive rounds.",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(),
    default=None,
    help="Path to custom config.toml configuration file.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    phone: Optional[str],
    interval: Optional[float],
    timeout: Optional[float],
    driver: Optional[str],
    services: Optional[str],
    tags: Optional[str],
    proxy_file: Optional[str],
    only_browser: bool,
    no_browser: bool,
    headless: Optional[bool],
    use_rich: Optional[bool],
    export_report: Optional[bool],
    export_format: Optional[str],
    reports_dir: Optional[str],
    rounds: Optional[int],
    round_interval: Optional[float],
    config_path: Optional[str],
) -> None:
    """S-Bomber: SMS provider verification benchmark and stress testing utility."""
    if ctx.invoked_subcommand is not None:
        return

    # Load persistent configuration
    cfg = load_configuration(config_path)
    bomber_cfg = cfg.get("bomber", {})

    # Merge configuration defaults with CLI overrides
    resolved_interval: float = interval if interval is not None else float(bomber_cfg.get("request_interval", 1.6))
    resolved_timeout: float = timeout if timeout is not None else float(bomber_cfg.get("request_timeout", 10.0))
    resolved_driver: str = driver.lower() if driver is not None else str(bomber_cfg.get("default_driver", "chrome")).lower()
    resolved_proxy_file: str = proxy_file if proxy_file is not None else str(bomber_cfg.get("proxy_file", "proxy.txt"))
    resolved_headless: bool = headless if headless is not None else bool(bomber_cfg.get("is_headless", True))
    resolved_use_rich: bool = use_rich if use_rich is not None else bool(bomber_cfg.get("use_rich_dashboard", True))
    resolved_export_report: bool = export_report if export_report is not None else bool(bomber_cfg.get("export_report", False))
    resolved_export_format: str = export_format.lower() if export_format is not None else str(bomber_cfg.get("export_format", "json")).lower()
    resolved_reports_dir: str = reports_dir if reports_dir is not None else str(bomber_cfg.get("reports_dir", "reports"))
    resolved_rounds: int = rounds if rounds is not None else int(bomber_cfg.get("rounds", 1))
    resolved_round_interval: float = round_interval if round_interval is not None else float(bomber_cfg.get("round_interval", 5.0))
    fast_mode: bool = bool(bomber_cfg.get("fast_browser_mode", True))

    selected_services_list: list[str] = []
    if services:
        selected_services_list = [s.strip() for s in services.split(",") if s.strip()]
    elif bomber_cfg.get("selected_services"):
        selected_services_list = list(bomber_cfg.get("selected_services", []))

    if tags:
        tag_services = get_services_by_tags(tags)
        if selected_services_list:
            selected_services_list = sorted(list(set(selected_services_list).intersection(set(tag_services))))
        else:
            selected_services_list = tag_services

    clear_terminal_screen()
    display_startup_banner()

    target_phone_number: str = ""


    # Check if executed without arguments (interactive dual-mode)
    if phone is None and not only_browser and not no_browser and interval is None:
        menu_selection = display_interactive_main_menu()
        if menu_selection == 1:
            try:
                user_raw_phone = click.prompt(
                    Fore.GREEN + "- Enter your target phone number (e.g: 09126543210)" + Fore.RESET,
                    type=str,
                )
                target_phone_number = normalize_iranian_phone_number(user_raw_phone)
            except ValueError as val_err:
                sys.exit(Fore.RED + f"Validation error: {val_err}" + Fore.RESET)
            except (KeyboardInterrupt, EOFError):
                sys.exit(Fore.YELLOW + "\nOperation aborted by user." + Fore.RESET)
        elif menu_selection == 2:
            ctx.invoke(check_proxies, proxy_file=resolved_proxy_file)
            return
        elif menu_selection == 3:
            print(Fore.CYAN + "\nCurrent Configuration Settings (config.toml):" + Fore.RESET)
            for section_name, section_values in cfg.items():
                print(Fore.YELLOW + f"[{section_name}]" + Fore.RESET)
                if isinstance(section_values, dict):
                    for k, v in section_values.items():
                        print(f"  {k} = {v}")
            return
        elif menu_selection == 4:
            print(Fore.GREEN + "Goodbye!" + Fore.RESET)
            sys.exit(0)
    else:
        # Non-interactive CLI flag mode
        if phone:
            try:
                target_phone_number = normalize_iranian_phone_number(phone)
            except ValueError as val_err:
                sys.exit(Fore.RED + f"Validation error: {val_err}" + Fore.RESET)
        else:
            try:
                user_raw_phone = input(
                    Fore.GREEN + "- Enter your target phone number (e.g: 09126543210)-> " + Fore.RESET
                )
                target_phone_number = normalize_iranian_phone_number(user_raw_phone)
            except ValueError as val_err:
                sys.exit(Fore.RED + f"Validation error: {val_err}" + Fore.RESET)
            except (KeyboardInterrupt, EOFError):
                sys.exit(Fore.YELLOW + "\nOperation aborted by user." + Fore.RESET)

    print(Fore.RED + "Note: For best results check README.md file" + Fore.RESET)
    print(Fore.BLUE + f"STARTING THE OPERATION FOR {target_phone_number} ..." + Fore.RESET)

    # Initialize proxy pool
    loaded_proxies = load_proxies_from_file(resolved_proxy_file)
    proxy_pool = ProxyPool(loaded_proxies) if loaded_proxies else None
    if proxy_pool and proxy_pool.has_proxies:
        print(Fore.CYAN + f"Proxy pool loaded: {proxy_pool.total_count} proxies active." + Fore.RESET)

    total_http_tasks: int = len(IranianSMS.filter_service_methods(selected_services_list or None)) if not only_browser else 0
    total_browser_tasks: int = len(IranianWebSMS.filter_service_methods(selected_services_list or None)) if not no_browser else 0
    total_tasks_per_round: int = total_http_tasks + total_browser_tasks
    total_tasks_count: int = total_tasks_per_round * resolved_rounds

    try:
        with DispatchDashboard(total_tasks=total_tasks_count, use_rich=resolved_use_rich) as dashboard:
            for current_round_idx in range(1, resolved_rounds + 1):
                if resolved_rounds > 1 and not dashboard.is_rich_active:
                    print(Fore.CYAN + f"\n=== Starting Round {current_round_idx}/{resolved_rounds} ===" + Fore.RESET)

                if not only_browser:
                    # Phase 1: HTTP API SMS Dispatching
                    http_count = run_http_sms_bomber(
                        target_phone_number=target_phone_number,
                        request_interval_seconds=resolved_interval,
                        request_timeout_seconds=resolved_timeout,
                        selected_services=selected_services_list or None,
                        proxy_pool=proxy_pool,
                        dashboard=dashboard,
                    )
                    if not dashboard.is_rich_active and resolved_rounds == 1:
                        print(Fore.CYAN + f"HTTP dispatching completed. Dispatched: {http_count} requests." + Fore.RESET)

                if not no_browser:
                    # Phase 2: Browser-dependent SMS Dispatching
                    browser_proxy = proxy_pool.get_next_proxy() if proxy_pool and proxy_pool.has_proxies else None
                    browser_count = run_browser_sms_bomber(
                        target_phone_number=target_phone_number,
                        request_interval_seconds=resolved_interval,
                        browser_type=resolved_driver,
                        is_headless=resolved_headless,
                        fast_mode=fast_mode,
                        selected_services=selected_services_list or None,
                        proxy_url=browser_proxy,
                        dashboard=dashboard,
                    )
                    if not dashboard.is_rich_active and resolved_rounds == 1:
                        print(Fore.CYAN + f"Browser dispatching completed. Dispatched: {browser_count} requests." + Fore.RESET)

                if current_round_idx < resolved_rounds and resolved_round_interval > 0:
                    if not dashboard.is_rich_active:
                        print(Fore.YELLOW + f"Waiting {resolved_round_interval}s before round {current_round_idx + 1}..." + Fore.RESET)
                    time.sleep(resolved_round_interval)

            dashboard.render_summary()

            if resolved_export_report and dashboard.stats.completed_tasks > 0:
                exported_filepath = export_benchmark_report(
                    stats=dashboard.stats,
                    target_phone=target_phone_number,
                    format_type=resolved_export_format,
                    output_directory=resolved_reports_dir,
                    rounds_executed=resolved_rounds,
                )
                print(Fore.GREEN + f"\n[✓] Benchmark telemetry exported to: {exported_filepath}" + Fore.RESET)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation stopped by user." + Fore.RESET)

    # Offer to prune dead proxies if any were recorded during execution
    if proxy_pool and proxy_pool.dead_proxies:
        print(Fore.YELLOW + f"\n{len(proxy_pool.dead_proxies)} proxies failed during this run." + Fore.RESET)
        try:
            should_prune = click.confirm(
                Fore.GREEN + f"Would you like to remove dead proxies from {resolved_proxy_file}? [Y/n]" + Fore.RESET,
                default=True,
            )
            if should_prune:
                pruned_count = prune_dead_proxies_from_file(resolved_proxy_file, proxy_pool.dead_proxies)
                print(Fore.GREEN + f"Pruned {pruned_count} dead proxies from {resolved_proxy_file}." + Fore.RESET)
        except (click.Abort, KeyboardInterrupt):
            pass


@cli.command("check-proxies")
@click.option(
    "--proxy-file",
    "-f",
    type=click.Path(),
    default="proxy.txt",
    help="Path to proxy file to test.",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=3.5,
    help="Per-proxy connection timeout in seconds.",
)
@click.option(
    "--prune/--no-prune",
    default=False,
    help="Automatically remove dead proxies from file without prompting.",
)
def check_proxies(proxy_file: str, timeout: float, prune: bool) -> None:
    """Asynchronously test proxy health and prune unresponsive proxies."""
    resolved_path = Path(proxy_file).resolve()
    proxies = load_proxies_from_file(resolved_path)

    if not proxies:
        click.secho(f"No proxies found in {proxy_file}.", fg="yellow")
        return

    click.echo(f"Testing {len(proxies)} proxies asynchronously (timeout={timeout}s)...")
    import asyncio
    results: list[ProxyHealthResult] = asyncio.run(
        check_proxies_health(proxies, timeout_seconds=timeout)
    )

    alive_count = 0
    dead_proxies: set[str] = set()

    for res in results:
        if res.is_alive:
            alive_count += 1
            click.secho(f"[✓ ALIVE] {res.proxy_address:<30} ({res.latency_ms:.1f}ms)", fg="green")
        else:
            dead_proxies.add(res.proxy_address)
            err = f": {res.error_message}" if res.error_message else ""
            click.secho(f"[✗ DEAD ] {res.proxy_address:<30}{err}", fg="red")

    click.echo(f"\nHealth check complete: {alive_count}/{len(proxies)} proxies alive.")

    if dead_proxies:
        should_prune = prune
        if not prune:
            try:
                should_prune = click.confirm(
                    f"Would you like to remove {len(dead_proxies)} dead proxies from {proxy_file}?",
                    default=True,
                )
            except (click.Abort, KeyboardInterrupt):
                should_prune = False

        if should_prune:
            removed = prune_dead_proxies_from_file(resolved_path, dead_proxies)
            click.secho(f"Successfully pruned {removed} dead proxies from {proxy_file}.", fg="green")


@cli.command("check-services")
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=5.0,
    help="Per-endpoint probe timeout in seconds.",
)
@click.option(
    "--tag",
    "-g",
    type=str,
    default=None,
    help="Filter probed endpoints by category tag.",
)
def check_services(timeout: float, tag: Optional[str]) -> None:
    """Non-intrusively verify availability of service provider endpoints."""
    click.echo(f"Probing service endpoints reachability (timeout={timeout}s)...")
    results: list[ServiceHealthResult] = check_all_services(timeout_seconds=timeout)
    if tag:
        target_services = set(get_services_by_tags(tag))
        results = [r for r in results if r.service_name in target_services]

    reachable_count = 0
    for res in results:
        if res.is_reachable:
            reachable_count += 1
            code_label = f"HTTP {res.status_code}" if res.status_code else "ONLINE"
            click.secho(f"[✓ ONLINE ] {res.service_name:<25} {code_label:<10} ({res.latency_ms:.1f}ms)", fg="green")
        else:
            err = f": {res.error_message}" if res.error_message else ""
            click.secho(f"[✗ OFFLINE] {res.service_name:<25} {err}", fg="red")

    click.echo(f"\nEndpoint reachability check complete: {reachable_count}/{len(results)} online.")


@cli.command("update-proxies")
@click.option(
    "--proxy-file",
    "-f",
    type=click.Path(),
    default="proxy.txt",
    help="Path to output proxy file.",
)
@click.option(
    "--max-proxies",
    "-m",
    type=int,
    default=25,
    help="Maximum number of verified working proxies to retain.",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=3.0,
    help="Connection health check timeout in seconds.",
)
def update_proxies(proxy_file: str, max_proxies: int, timeout: float) -> None:
    """Scrape public proxy lists, test connectivity, and write working proxies to file."""
    click.echo(f"Scraping public proxies and validating live nodes (timeout={timeout}s, max={max_proxies})...")
    live_proxies = update_proxy_file_with_live_proxies(
        destination_file=proxy_file,
        max_working_proxies=max_proxies,
        timeout_seconds=timeout,
    )
    if live_proxies:
        click.secho(f"\nSuccessfully discovered and saved {len(live_proxies)} live proxies to {proxy_file}:", fg="green")
        for p in live_proxies:
            click.echo(f"  {p.proxy_address:<30} ({p.latency_ms:.1f}ms)")
    else:
        click.secho("No working public proxies could be reached at this time.", fg="yellow")


# Backward-compatible helper for legacy tests
def parse_command_line_arguments(command_line_args: Optional[list[str]] = None) -> Any:
    """Backward compatibility wrapper simulating argparse.Namespace from parsed options."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phone", type=str, default=None)
    parser.add_argument("-i", "--interval", type=float, default=1.6)
    parser.add_argument("-t", "--timeout", type=float, default=10.0)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--only-browser", action="store_true")
    return parser.parse_args(command_line_args)


def main() -> None:
    """Application entry point invoking Click CLI."""
    cli()


if __name__ == "__main__":
    main()