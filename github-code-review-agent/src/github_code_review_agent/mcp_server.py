"""MCP Server — exposes review_github_pull_request as an MCP tool for Kiro integration."""

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import load_config
from .fetcher import fetch_pr
from .reviewer import run_kiro_review

app = Server("github-code-review-agent")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of tools exposed by this MCP server."""
    return [
        Tool(
            name="review_github_pull_request",
            description="Fetch a GitHub Pull Request and generate an AI-powered code review using Kiro CLI. Returns formatted review comments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pr_url": {
                        "type": "string",
                        "description": "Full GitHub PR URL, e.g. https://github.com/owner/repo/pull/42",
                    },
                    "config_path": {
                        "type": "string",
                        "description": "Optional path to config.yaml",
                    },
                },
                "required": ["pr_url"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle a tool call from Kiro — delegates to review_github_pull_request."""
    if name != "review_github_pull_request":
        raise ValueError(f"Unknown tool: {name}")

    pr_url: str = arguments["pr_url"]
    config_path: str | None = arguments.get("config_path")

    cfg = load_config(config_path)
    token = cfg["github"].get("token") or None

    pr = fetch_pr(pr_url, token=token, max_files=cfg["review"]["max_files"])
    review = run_kiro_review(pr, cfg)

    # Build plain-text output for MCP response
    output = (
        f"# 🤖 GitHub AI Code Review\n\n"
        f"**PR:** {pr.url}\n"
        f"**Title:** {pr.title}\n"
        f"**Author:** {pr.author}\n"
        f"**Branch:** `{pr.head_branch}` → `{pr.base_branch}`\n"
        f"**Files changed:** {len(pr.files)}\n\n"
        f"---\n\n"
        f"{review}\n\n"
        f"---\n"
        f"*⚡ Powered by Kiro CLI • GitHub Code Review Agent*"
    )

    return [TextContent(type="text", text=output)]


def serve() -> None:
    """Start the MCP stdio server."""
    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    serve()
