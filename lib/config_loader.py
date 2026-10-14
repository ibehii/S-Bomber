# GitHub: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Configuration loader and schema validator for S-Bomber using TOML."""

from pathlib import Path
import sys
from typing import Any, Final

# Python 3.11+ includes tomllib in standard library
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


DEFAULT_CONFIGURATION: Final[dict[str, Any]] = {
    "general": {
        "telegram": "https://t.me/dr_xz",
        "github": "https://github.com/ibehii",
        "version": "1.2.0",
    },
    "bomber": {
        "default_driver": "chrome",
        "use_browser": True,
        "request_interval": 1.6,
        "request_timeout": 10.0,
        "is_headless": True,
        "fast_browser_mode": True,
        "proxy_file": "proxy.txt",
        "selected_services": [],
        "use_rich_dashboard": True,
        "export_report": False,
        "export_format": "json",
        "reports_dir": "reports",
        "rounds": 1,
        "round_interval": 5.0,
    },
}


def get_default_config_path() -> Path:
    """Return default Path to config.toml in project root."""
    return Path(__file__).parent.parent.resolve() / "config.toml"


def load_configuration(
    custom_config_path: Path | str | None = None,
) -> dict[str, Any]:
    """Load configuration from config.toml and merge with defaults.

    Parameters
    ----------
    custom_config_path : Path | str | None, optional
        Optional path to a custom TOML config file, by default None.

    Returns
    -------
    dict[str, Any]
        Merged configuration dictionary containing 'general' and 'bomber' sections.
    """
    resolved_config_path: Path
    if custom_config_path is not None:
        resolved_config_path = Path(custom_config_path).resolve()
    else:
        resolved_config_path = get_default_config_path()

    loaded_configuration: dict[str, Any] = {
        "general": dict(DEFAULT_CONFIGURATION["general"]),
        "bomber": dict(DEFAULT_CONFIGURATION["bomber"]),
    }

    if not resolved_config_path.exists() or not resolved_config_path.is_file():
        return loaded_configuration

    if tomllib is None:
        return loaded_configuration

    try:
        with open(resolved_config_path, "rb") as configuration_file_handle:
            parsed_toml_data: dict[str, Any] = tomllib.load(configuration_file_handle)

        if "general" in parsed_toml_data and isinstance(parsed_toml_data["general"], dict):
            loaded_configuration["general"].update(parsed_toml_data["general"])

        if "bomber" in parsed_toml_data and isinstance(parsed_toml_data["bomber"], dict):
            loaded_configuration["bomber"].update(parsed_toml_data["bomber"])

    except Exception:
        # Fall back cleanly to defaults if file is malformed
        return loaded_configuration

    return loaded_configuration


__all__ = [
    "DEFAULT_CONFIGURATION",
    "get_default_config_path",
    "load_configuration",
]
