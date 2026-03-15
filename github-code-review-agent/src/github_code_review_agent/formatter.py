"""Console output formatter using Rich."""

import re
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from .fetcher import PRInfo

console = Console()

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from Kiro CLI output."""
    return _ANSI_ESCAPE.sub("", text)


def print_review(pr: PRInfo, review_text: str) -> None:
    """Print a clean, professional review report to the console."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Header ──────────────────────────────────────────────────────────────
    console.print()
    console.print(Rule("🤖  GitHub AI Code Review", style="bold cyan"))
    console.print()

    header_info = (
        f"[bold]📌 PR:[/bold]     [link={pr.url}]{pr.url}[/link]\n"
        f"[bold]📝 Title:[/bold]  {pr.title}\n"
        f"[bold]👤 Author:[/bold] {pr.author}\n"
        f"[bold]🌿 Branch:[/bold] [cyan]{pr.head_branch}[/cyan] → [cyan]{pr.base_branch}[/cyan]\n"
        f"[bold]📂 Files:[/bold]  {len(pr.files)} changed\n"
        f"[bold]🕐 Time:[/bold]   {now}"
    )
    console.print(Panel(header_info, title="Pull Request", border_style="cyan", expand=False))
    console.print()

    # ── Review Body ─────────────────────────────────────────────────────────
    console.print(Rule("📋  Review Comments", style="bold yellow"))
    console.print()

    for line in _strip_ansi(review_text).splitlines():
        console.print(line)

    console.print()

    # ── Footer ───────────────────────────────────────────────────────────────
    console.print(Rule(style="bold cyan"))
    footer = Text("⚡ Powered by Kiro CLI  •  GitHub Code Review Agent", style="dim cyan", justify="center")
    console.print(footer)
    console.print()
