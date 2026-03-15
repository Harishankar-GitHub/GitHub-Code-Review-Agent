"""Sends prompt to Kiro CLI and returns the review text."""

import subprocess
from .prompt import build_prompt
from .fetcher import PRInfo


def run_kiro_review(pr: PRInfo, cfg: dict) -> str:
    """Pipe the review prompt to `kiro-cli chat` and capture output."""
    review_cfg = cfg.get("review", {})
    prompt = build_prompt(
        pr=pr,
        focus=review_cfg.get("focus", []),
        severity_threshold=review_cfg.get("severity_threshold", "low"),
    )

    cmd = ["kiro-cli", "chat", "--no-interactive"]
    if model := cfg.get("kiro", {}).get("model"):
        cmd += ["--model", model]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("kiro-cli timed out after 300 seconds.")

    if result.returncode != 0:
        raise RuntimeError(
            f"kiro-cli exited with code {result.returncode}:\n{result.stderr.strip()}"
        )

    return result.stdout.strip()
