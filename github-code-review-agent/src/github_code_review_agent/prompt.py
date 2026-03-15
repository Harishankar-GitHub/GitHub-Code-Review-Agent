"""Builds the review prompt sent to Kiro CLI."""

from .fetcher import PRInfo


def build_prompt(pr: PRInfo, focus: list[str], severity_threshold: str) -> str:
    """Construct a structured prompt for Kiro CLI code review."""

    focus_str = ", ".join(focus).replace("_", " ")

    files_section = ""
    for f in pr.files:
        files_section += f"\n### `{f.filename}` ({f.status}, +{f.additions}/-{f.deletions})\n"
        if f.patch:
            files_section += f"```diff\n{f.patch}\n```\n"
        else:
            files_section += "_Binary or empty file — no patch available._\n"

    return f"""You are an expert code reviewer. Review the following GitHub Pull Request and provide detailed, actionable feedback.

## Pull Request Details
- **Title:** {pr.title}
- **Author:** {pr.author}
- **Branch:** `{pr.head_branch}` → `{pr.base_branch}`
- **Description:** {pr.description or "_(no description provided)_"}

## Review Focus Areas
{focus_str}

## Severity Threshold
Report issues at **{severity_threshold}** severity and above.

## Changed Files
{files_section}

## Instructions
- Do NOT repeat the full diff in your response
- Organise feedback by file, then by issue
- For each issue: state the file, line reference (if applicable), severity (🔴 High / 🟡 Medium / 🟢 Low), and a clear explanation with a suggested fix
- Use emojis to improve readability
- End with an overall summary and a verdict: ✅ Approved / ⚠️ Needs Changes / ❌ Request Changes
"""
