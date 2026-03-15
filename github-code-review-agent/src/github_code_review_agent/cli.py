"""Standalone CLI entry point."""

import sys

import click
from rich.console import Console

from .config import load_config
from .fetcher import fetch_pr
from .reviewer import run_kiro_review
from .formatter import print_review

console = Console(stderr=True)


@click.command()
@click.argument("pr_url")
@click.option("--config", "-c", default=None, help="Path to config.yaml (default: ~/.kiro/gh-review/config.yaml)")
@click.option("--model", "-m", default=None, help="Override Kiro model (e.g. claude-sonnet-4-5)")
@click.option("--max-files", default=None, type=int, help="Max files to review")
def main(pr_url: str, config: str | None, model: str | None, max_files: int | None) -> None:
    """AI-powered GitHub PR code reviewer using Kiro CLI.

    \b
    Example:
        gh-review https://github.com/owner/repo/pull/42
    """
    try:
        cfg = load_config(config)

        # CLI flag overrides
        if model:
            cfg["kiro"]["model"] = model
        if max_files:
            cfg["review"]["max_files"] = max_files

        token = cfg["github"].get("token") or None

        console.print("[cyan]⏳ Fetching PR...[/cyan]")
        pr = fetch_pr(pr_url, token=token, max_files=cfg["review"]["max_files"])

        console.print(f"[cyan]🤖 Running Kiro review on {len(pr.files)} file(s)...[/cyan]")
        review = run_kiro_review(pr, cfg)

        print_review(pr, review)

    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(3)


if __name__ == "__main__":
    main()
