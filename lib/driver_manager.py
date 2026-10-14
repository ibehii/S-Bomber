# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Automated WebDriver resolution via webdriver-manager and system paths."""

from pathlib import Path
import shutil
from typing import Optional

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager

    WEBDRIVER_MANAGER_AVAILABLE: bool = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    ChromeDriverManager = None  # type: ignore[assignment, misc]
    GeckoDriverManager = None  # type: ignore[assignment, misc]


def resolve_chromedriver_executable(custom_path: Path | str | None = None) -> Optional[str]:
    """Find or automatically install Google Chrome driver binary.

    Parameters
    ----------
    custom_path : Path | str | None, optional
        User-provided path to chromedriver, by default None.

    Returns
    -------
    Optional[str]
        Path string to chromedriver executable if found or installed, else None.
    """
    if custom_path is not None and Path(custom_path).exists():
        return str(Path(custom_path).resolve())

    # 1. Check system PATH
    system_chromedriver = shutil.which("chromedriver")
    if system_chromedriver is not None:
        return system_chromedriver

    # 2. Try automated webdriver-manager if installed
    if WEBDRIVER_MANAGER_AVAILABLE and ChromeDriverManager is not None:
        try:
            installed_path = ChromeDriverManager().install()
            if installed_path and Path(installed_path).exists():
                return installed_path
        except Exception:
            pass

    return None


def resolve_geckodriver_executable(
    custom_path: Path | str | None = None,
    workspace_root: Path | str | None = None,
) -> Optional[str]:
    """Find or automatically install Mozilla Firefox geckodriver binary.

    Parameters
    ----------
    custom_path : Path | str | None, optional
        User-provided path to geckodriver, by default None.
    workspace_root : Path | str | None, optional
        Root directory where local geckodriver might reside, by default project root.

    Returns
    -------
    Optional[str]
        Path string to geckodriver executable if found or installed, else None.
    """
    if custom_path is not None and Path(custom_path).exists():
        return str(Path(custom_path).resolve())

    # 1. Check project root directory for bundled binary
    root_path = Path(workspace_root).resolve() if workspace_root else Path(__file__).parent.parent.resolve()
    local_binary = root_path / "geckodriver"
    if local_binary.exists() and local_binary.is_file():
        return str(local_binary)

    # 2. Check system PATH
    system_geckodriver = shutil.which("geckodriver")
    if system_geckodriver is not None:
        return system_geckodriver

    # 3. Try automated webdriver-manager if installed
    if WEBDRIVER_MANAGER_AVAILABLE and GeckoDriverManager is not None:
        try:
            installed_path = GeckoDriverManager().install()
            if installed_path and Path(installed_path).exists():
                return installed_path
        except Exception:
            pass

    return None


__all__ = [
    "WEBDRIVER_MANAGER_AVAILABLE",
    "resolve_chromedriver_executable",
    "resolve_geckodriver_executable",
]
