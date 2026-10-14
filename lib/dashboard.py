# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Live interactive terminal dashboard and telemetry rendering for S-Bomber."""

from dataclasses import dataclass, field
import sys
import time
from typing import Any, Optional

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
    from rich.console import Console, Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskID,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE: bool = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore[assignment, misc]
    Live = None  # type: ignore[assignment, misc]
    Panel = None  # type: ignore[assignment, misc]
    Progress = None  # type: ignore[assignment, misc]
    SpinnerColumn = None  # type: ignore[assignment, misc]
    BarColumn = None  # type: ignore[assignment, misc]
    TextColumn = None  # type: ignore[assignment, misc]
    TimeElapsedColumn = None  # type: ignore[assignment, misc]
    TimeRemainingColumn = None  # type: ignore[assignment, misc]
    Table = None  # type: ignore[assignment, misc]
    Text = None  # type: ignore[assignment, misc]
    Group = None  # type: ignore[assignment, misc]
    TaskID = int  # type: ignore[assignment, misc]


@dataclass
class ServiceExecutionResult:
    """Represents a single service dispatch execution result."""

    index: int
    service_name: str
    engine: str
    is_success: bool
    latency_ms: float
    status_label: str
    proxy_address: Optional[str] = None


@dataclass
class DashboardStats:
    """Aggregates execution metrics across all dispatched services."""

    total_tasks: int = 0
    completed_tasks: int = 0
    successful_count: int = 0
    failed_count: int = 0
    total_latency_ms: float = 0.0
    dead_proxies_count: int = 0
    results: list[ServiceExecutionResult] = field(default_factory=list)

    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency across completed tasks."""
        if not self.completed_tasks:
            return 0.0
        return self.total_latency_ms / self.completed_tasks

    @property
    def success_percentage(self) -> float:
        """Calculate success rate percentage."""
        if not self.completed_tasks:
            return 0.0
        return (self.successful_count / self.completed_tasks) * 100.0


class DispatchDashboard:
    """Real-time terminal dashboard with progress bar, live metrics table, and telemetry.

    Parameters
    ----------
    total_tasks : int
        Total number of verification tasks to be executed.
    use_rich : bool, optional
        Whether to enable Rich interactive UI, by default True.
    task_description : str, optional
        Label for the active progress bar task, by default 'Dispatching verification codes'.
    """

    def __init__(
        self,
        total_tasks: int,
        use_rich: bool = True,
        task_description: str = "Dispatching requests",
    ) -> None:
        self.stats = DashboardStats(total_tasks=total_tasks)
        self.task_description = task_description
        self.is_rich_active = bool(RICH_AVAILABLE and use_rich and sys.stdout.isatty())
        self.start_timestamp: float = time.perf_counter()

        self.console: Any = Console() if (RICH_AVAILABLE and self.is_rich_active) else None
        self.live: Any = None
        self.progress: Any = None
        self.task_id: Optional[TaskID] = None

        if self.is_rich_active:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}"),
                BarColumn(bar_width=None),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console,
            )
            self.task_id = self.progress.add_task(
                self.task_description,
                total=total_tasks,
            )

    def __enter__(self) -> "DispatchDashboard":
        if self.is_rich_active and self.progress is not None:
            self.live = Live(
                self._render_renderable_group(),
                console=self.console,
                refresh_per_second=8,
                transient=False,
            )
            self.live.__enter__()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: Any,
    ) -> None:
        if self.live is not None:
            self.live.__exit__(exception_type, exception_value, traceback)
            self.live = None

    def _render_renderable_group(self) -> Any:
        """Assemble the composite Live layout (Progress + Status Table + Telemetry)."""
        table = Table(
            title="[bold yellow]Service Dispatch Activity[/bold yellow]",
            expand=True,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("#", justify="right", width=4)
        table.add_column("Service", style="cyan", width=22)
        table.add_column("Engine", width=10)
        table.add_column("Status", width=14)
        table.add_column("Latency", justify="right", width=12)
        table.add_column("Active Proxy", style="dim", width=25)

        # Show the most recent 10 results to maintain clean terminal view
        recent_results = self.stats.results[-10:] if self.stats.results else []
        for res in recent_results:
            status_text = (
                "[bold green]✓ SUCCESS[/bold green]"
                if res.is_success
                else "[bold red]✗ FAILED[/bold red]"
            )
            engine_text = (
                "[blue]HTTP[/blue]"
                if res.engine.upper() == "HTTP"
                else "[purple]Browser[/purple]"
            )
            table.add_row(
                str(res.index),
                res.service_name,
                engine_text,
                status_text,
                f"{res.latency_ms:.1f}ms",
                res.proxy_address or "Direct (No Proxy)",
            )

        telemetry_content = Text()
        telemetry_content.append("Progress: ", style="bold")
        telemetry_content.append(f"{self.stats.completed_tasks}/{self.stats.total_tasks} | ")
        telemetry_content.append("Successful: ", style="bold green")
        telemetry_content.append(f"{self.stats.successful_count} | ", style="green")
        telemetry_content.append("Failed: ", style="bold red")
        telemetry_content.append(f"{self.stats.failed_count} | ", style="red")
        telemetry_content.append("Avg Latency: ", style="bold cyan")
        telemetry_content.append(f"{self.stats.average_latency_ms:.1f}ms | ", style="cyan")
        telemetry_content.append("Dead Proxies: ", style="bold yellow")
        telemetry_content.append(f"{self.stats.dead_proxies_count}", style="yellow")

        telemetry_panel = Panel(
            telemetry_content,
            title="[bold blue]Telemetry Metrics[/bold blue]",
            border_style="blue",
        )

        return Group(self.progress, table, telemetry_panel)

    def record_result(
        self,
        service_name: str,
        engine: str,
        is_success: bool,
        latency_ms: float,
        status_label: str = "",
        proxy: Optional[str] = None,
    ) -> None:
        """Record a completed dispatch event and update the active display."""
        self.stats.completed_tasks += 1
        if is_success:
            self.stats.successful_count += 1
        else:
            self.stats.failed_count += 1
        self.stats.total_latency_ms += latency_ms

        execution_record = ServiceExecutionResult(
            index=self.stats.completed_tasks,
            service_name=service_name,
            engine=engine,
            is_success=is_success,
            latency_ms=latency_ms,
            status_label=status_label,
            proxy_address=proxy,
        )
        self.stats.results.append(execution_record)

        if self.is_rich_active and self.progress is not None and self.task_id is not None:
            self.progress.update(self.task_id, advance=1)
            if self.live is not None:
                self.live.update(self._render_renderable_group())
        else:
            # Fallback stdout output
            if is_success:
                print(
                    Fore.YELLOW
                    + "[+]"
                    + Fore.MAGENTA
                    + " - "
                    + Fore.GREEN
                    + f"Verification code sent through {service_name} Successfully ({latency_ms:.1f}ms)"
                    + Fore.RESET
                )
            else:
                reason = f" ({status_label})" if status_label else ""
                print(
                    Fore.RED
                    + "[-] - "
                    + f"Couldn't send Verification code through {service_name}!{reason}"
                    + Fore.RESET
                )

    def record_dead_proxy(self) -> None:
        """Increment count of observed dead proxies."""
        self.stats.dead_proxies_count += 1

    def render_summary(self) -> None:
        """Display the final execution summary card upon completion."""
        total_time_seconds = time.perf_counter() - self.start_timestamp

        if self.is_rich_active and Console is not None:
            summary_console = Console()
            summary_text = Text()
            summary_text.append(f"• Total Requests Dispatched: ", style="bold")
            summary_text.append(f"{self.stats.completed_tasks}\n")
            summary_text.append(f"• Successful: ", style="bold green")
            summary_text.append(f"{self.stats.successful_count} ({self.stats.success_percentage:.1f}%)\n", style="green")
            summary_text.append(f"• Failed / Rejected: ", style="bold red")
            summary_text.append(f"{self.stats.failed_count}\n", style="red")
            summary_text.append(f"• Average Latency: ", style="bold cyan")
            summary_text.append(f"{self.stats.average_latency_ms:.1f} ms\n", style="cyan")
            summary_text.append(f"• Dead Proxies Detected: ", style="bold yellow")
            summary_text.append(f"{self.stats.dead_proxies_count}\n", style="yellow")
            summary_text.append(f"• Total Elapsed Time: ", style="bold magenta")
            summary_text.append(f"{total_time_seconds:.2f} s\n", style="magenta")

            panel = Panel(
                summary_text,
                title="[bold green]Dispatch Operation Completed[/bold green]",
                border_style="green",
                expand=False,
            )
            summary_console.print("\n", panel)
        else:
            print(Fore.CYAN + "\n=============================================" + Fore.RESET)
            print(Fore.GREEN + "       DISPATCH OPERATION SUMMARY" + Fore.RESET)
            print(Fore.CYAN + "=============================================" + Fore.RESET)
            print(f"Total Requests Dispatched: {self.stats.completed_tasks}")
            print(f"Successful: {self.stats.successful_count} ({self.stats.success_percentage:.1f}%)")
            print(f"Failed: {self.stats.failed_count}")
            print(f"Average Latency: {self.stats.average_latency_ms:.1f} ms")
            print(f"Total Elapsed Time: {total_time_seconds:.2f} s")
            print(Fore.CYAN + "=============================================\n" + Fore.RESET)


__all__ = [
    "DashboardStats",
    "DispatchDashboard",
    "RICH_AVAILABLE",
    "ServiceExecutionResult",
]
