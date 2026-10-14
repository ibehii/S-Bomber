# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Structured benchmark and execution report exporter (JSON, CSV, Markdown)."""

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Optional

from lib.dashboard import DashboardStats


def generate_report_filename(
    prefix: str = "benchmark",
    extension: str = "json",
) -> str:
    """Generate a timestamped report filename."""
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    clean_ext = extension.lstrip(".")
    return f"{prefix}_{timestamp_str}.{clean_ext}"


def mask_phone_number(phone_number: str) -> str:
    """Mask middle digits of a phone number for privacy in exports."""
    if len(phone_number) >= 7:
        return f"{phone_number[:4]}****{phone_number[-3:]}"
    return phone_number


def export_benchmark_report(
    stats: DashboardStats,
    target_phone: str,
    format_type: str = "json",
    output_directory: Path | str = "reports",
    rounds_executed: int = 1,
) -> Path:
    """Export benchmark telemetry to a structured report file.

    Parameters
    ----------
    stats : DashboardStats
        Aggregated metrics and individual service dispatch results.
    target_phone : str
        The target phone number benchmarked.
    format_type : str, optional
        Export format ('json', 'csv', 'md'), by default 'json'.
    output_directory : Path | str, optional
        Target directory for saved reports, by default 'reports'.
    rounds_executed : int, optional
        Total benchmark passes executed, by default 1.

    Returns
    -------
    Path
        Absolute path to the created report file.
    """
    reports_dir = Path(output_directory).resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    normalized_format = format_type.lower().strip()
    report_filename = generate_report_filename(extension=normalized_format)
    target_filepath = reports_dir / report_filename

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    masked_phone = mask_phone_number(target_phone)

    if normalized_format == "json":
        report_data: dict[str, Any] = {
            "metadata": {
                "timestamp": timestamp_iso,
                "target_phone": masked_phone,
                "rounds_executed": rounds_executed,
            },
            "summary": {
                "total_requests": stats.completed_tasks,
                "successful_requests": stats.successful_count,
                "failed_requests": stats.failed_count,
                "success_rate_percent": round(stats.success_percentage, 2),
                "average_latency_ms": round(stats.average_latency_ms, 2),
                "dead_proxies_detected": stats.dead_proxies_count,
            },
            "results": [
                {
                    "index": item.index,
                    "service_name": item.service_name,
                    "engine": item.engine,
                    "is_success": item.is_success,
                    "latency_ms": round(item.latency_ms, 2),
                    "status_label": item.status_label,
                    "proxy_address": item.proxy_address,
                }
                for item in stats.results
            ],
        }
        with open(target_filepath, "w", encoding="utf-8") as json_file:
            json.dump(report_data, json_file, indent=2, ensure_ascii=False)

    elif normalized_format == "csv":
        with open(target_filepath, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                "index",
                "service_name",
                "engine",
                "is_success",
                "latency_ms",
                "status_label",
                "proxy_address",
            ])
            for item in stats.results:
                csv_writer.writerow([
                    item.index,
                    item.service_name,
                    item.engine,
                    "SUCCESS" if item.is_success else "FAILED",
                    round(item.latency_ms, 2),
                    item.status_label,
                    item.proxy_address or "",
                ])

    elif normalized_format in ("md", "markdown"):
        markdown_lines = [
            f"# S-Bomber Benchmark Report",
            f"",
            f"- **Date & Time (UTC):** `{timestamp_iso}`",
            f"- **Target (Masked):** `{masked_phone}`",
            f"- **Total Rounds:** `{rounds_executed}`",
            f"",
            f"## Summary Metrics",
            f"",
            f"| Metric | Value |",
            f"| :--- | :--- |",
            f"| **Total Requests** | `{stats.completed_tasks}` |",
            f"| **Successful Requests** | `{stats.successful_count}` (`{stats.success_percentage:.1f}%`) |",
            f"| **Failed Requests** | `{stats.failed_count}` |",
            f"| **Average Latency** | `{stats.average_latency_ms:.1f} ms` |",
            f"| **Dead Proxies Observed** | `{stats.dead_proxies_count}` |",
            f"",
            f"## Detailed Service Dispatches",
            f"",
            f"| # | Service | Engine | Outcome | Latency | Status Details | Proxy |",
            f"| :---: | :--- | :---: | :---: | :---: | :--- | :--- |",
        ]
        for item in stats.results:
            outcome = "✅ SUCCESS" if item.is_success else "❌ FAILED"
            proxy_str = item.proxy_address if item.proxy_address else "Direct"
            markdown_lines.append(
                f"| {item.index} | `{item.service_name}` | `{item.engine}` | {outcome} | `{item.latency_ms:.1f}ms` | {item.status_label} | `{proxy_str}` |"
            )
        markdown_lines.append("")

        with open(target_filepath, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_lines))

    else:
        raise ValueError(f"Unsupported report export format: {format_type}. Choose json, csv, or md.")

    return target_filepath


__all__ = [
    "export_benchmark_report",
    "generate_report_filename",
    "mask_phone_number",
]
