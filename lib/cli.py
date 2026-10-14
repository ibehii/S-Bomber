"""Click-based command-line interface and interactive menu for S-Bomber."""

import asyncio
from pathlib import Path
import sys
from typing import Any, Optional

import click

from lib.config_loader import load_configuration
from lib.proxy_manager import (
    ProxyHealthResult,
    check_proxies_health,
    load_proxies_from_file,
    prune_dead_proxies_from_file,
)
from lib.proxy_updater import update_proxy_file_with_live_proxies
from lib.reporter import export_benchmark_report
from lib.service_checker import ServiceHealthResult, check_all_services
from lib.service_tags import get_available_tags, get_services_by_tags


def display_interactive_menu() -> int:
    """Render the ASCII interactive menu and return the selected choice.

    Returns
    -------
    int
        Selected menu item (1: Dispatch, 2: Check & Clean Proxies, 3: View Settings, 4: Exit).
    """
    click.echo("\n" + "=" * 45)
    click.echo("         S-BOMBER INTERACTIVE MENU")
    click.echo("=" * 45)
    click.echo(" [1] Start SMS Dispatch")
    click.echo(" [2] Check & Clean Proxies (Async Health Check)")
    click.echo(" [3] View Current Settings (config.toml)")
    click.echo(" [4] Exit")
    click.echo("=" * 45)
    choice = click.prompt("Select an option [1-4]", type=int, default=1)
    return choice


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
    help="Browser automation engine driver.",
)
@click.option(
    "-s",
    "--services",
    type=str,
    default=None,
    help="Comma-separated list of services to target (e.g., divar,snapp_food,digikala).",
)
@click.option(
    "-g",
    "--tags",
    type=str,
    default=None,
    help="Comma-separated category tags to target (e.g., transport,marketplace,food).",
)
@click.option(
    "--proxy-file",
    type=click.Path(),
    default=None,
    help="Path to proxy file containing one address per line.",
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
    """S-Bomber: SMS verification provider benchmarking and stress utility."""
    if ctx.invoked_subcommand is not None:
        return

    # Load persistent configuration
    cfg = load_configuration(config_path)
    bomber_cfg = cfg.get("bomber", {})

    # Apply configuration defaults if CLI options were not explicitly provided
    resolved_interval = interval if interval is not None else float(bomber_cfg.get("request_interval", 1.6))
    resolved_timeout = timeout if timeout is not None else float(bomber_cfg.get("request_timeout", 10.0))
    resolved_driver = driver if driver is not None else str(bomber_cfg.get("default_driver", "chrome"))
    resolved_proxy_file = proxy_file if proxy_file is not None else str(bomber_cfg.get("proxy_file", "proxy.txt"))
    resolved_headless = headless if headless is not None else bool(bomber_cfg.get("is_headless", True))
    resolved_use_rich = use_rich if use_rich is not None else bool(bomber_cfg.get("use_rich_dashboard", True))
    resolved_export_report = export_report if export_report is not None else bool(bomber_cfg.get("export_report", False))
    resolved_export_format = export_format.lower() if export_format is not None else str(bomber_cfg.get("export_format", "json")).lower()
    resolved_reports_dir = reports_dir if reports_dir is not None else str(bomber_cfg.get("reports_dir", "reports"))
    resolved_rounds = rounds if rounds is not None else int(bomber_cfg.get("rounds", 1))
    resolved_round_interval = round_interval if round_interval is not None else float(bomber_cfg.get("round_interval", 5.0))

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

    # If no flags and no phone given, display the interactive menu
    if phone is None and not only_browser and not no_browser and interval is None:
        choice = display_interactive_menu()
        if choice == 1:
            phone_input = click.prompt("Enter target phone number", type=str)
            click.echo(f"Starting dispatch for {phone_input} using driver={resolved_driver}...")
        elif choice == 2:
            ctx.invoke(check_proxies, proxy_file=resolved_proxy_file)
        elif choice == 3:
            click.echo("\nCurrent Configuration Settings:")
            for section, values in cfg.items():
                click.echo(f"[{section}]")
                if isinstance(values, dict):
                    for k, v in values.items():
                        click.echo(f"  {k} = {v}")
        elif choice == 4:
            click.echo("Exiting S-Bomber.")
            sys.exit(0)
        return

    click.echo(f"Target phone: {phone}")
    click.echo(f"Interval: {resolved_interval}s | Timeout: {resolved_timeout}s | Driver: {resolved_driver}")
    click.echo(f"Headless: {resolved_headless} | Proxy file: {resolved_proxy_file}")
    if tags:
        click.echo(f"Filter tags: {tags}")
    if selected_services_list:
        click.echo(f"Filtered services: {', '.join(selected_services_list)}")
    click.echo(f"Rounds: {resolved_rounds} | Round Interval: {resolved_round_interval}s")
    click.echo(f"Export report: {resolved_export_report} (format={resolved_export_format}, dir={resolved_reports_dir})")
    if only_browser:
        click.echo("Mode: Only browser automation")
    elif no_browser:
        click.echo("Mode: Only HTTP API services")



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
            except click.Abort:
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


__all__ = [
    "check_proxies",
    "check_services",
    "cli",
    "display_interactive_menu",
    "update_proxies",
]

