# Prompt: Build a GitHub Code Review AI Agent using Kiro CLI

> **Note:** This prompt was written after building the agent and captures its full design and implementation details.
> You can use it with Kiro CLI (or any AI assistant) to recreate this agent from scratch or build a similar one.

Build a Python-based GitHub Pull Request code review agent. It takes a GitHub PR URL as input, fetches the changed files, sends them to Kiro CLI for AI-powered review, and prints the results to the console. The agent is read-only — it never writes back to GitHub.

---

## What to Build

A Python package named `github-code-review-agent` with a `gh-review` CLI entry point, supporting three usage modes:

1. **Standalone CLI** — `gh-review <PR_URL>`, globally installable via `pipx`
2. **MCP Server** — stdio server exposing a `review_github_pull_request` tool for Kiro integration
3. **CI/CD** — runs as a standard build step in GitHub Actions or Jenkins

---

## Project Structure

Use a `src` layout with the following modules inside `src/github_code_review_agent/`:

- `config.py` — loads configuration from YAML file and environment variable overrides
- `fetcher.py` — parses the PR URL and fetches PR metadata and changed files from GitHub REST API
- `prompt.py` — builds a structured review prompt from the PR data and review settings
- `reviewer.py` — invokes `kiro-cli chat --no-interactive` with the prompt piped via stdin and captures the output
- `formatter.py` — renders the review to the console using Rich (header panel, review body, footer)
- `cli.py` — Click-based CLI entry point orchestrating the full flow
- `mcp_server.py` — MCP stdio server exposing the `review_github_pull_request` tool for Kiro

Also include: `config.example.yaml`, `pyproject.toml`, `requirements.txt`, `.gitignore`

---

## Module Behaviour

### `config.py`
- Define sensible built-in defaults for all settings
- Look for config in this order: explicit path argument → `~/.kiro/gh-review/config.yaml` → `./config.yaml`
- Deep-merge the YAML file into defaults; skip `None` values (YAML empty keys parse as `None` and must not overwrite defaults)
- Apply environment variable overrides last: `GITHUB_TOKEN` and `KIRO_MODEL`

### `fetcher.py`
- Parse the PR URL with regex to extract owner, repo, and PR number; raise `ValueError` on invalid URL
- Authenticate with a token if provided, otherwise unauthenticated (for public repos)
- Fetch PR metadata (title, author, branches, description) and up to `max_files` changed files with their patches
- Handle binary files safely (patch may be absent)
- Return structured dataclasses: `FileChange` and `PRInfo`

### `prompt.py`
- Build a structured Markdown prompt containing PR metadata, per-file diffs, focus areas, and severity threshold
- Instruct Kiro to: not repeat the diff, organise feedback by file then issue, use severity emojis (🔴 High / 🟡 Medium / 🟢 Low), and end with a summary verdict (✅ Approved / ⚠️ Needs Changes / ❌ Request Changes)

### `reviewer.py`
- Build the prompt and run `kiro-cli chat --no-interactive` as a subprocess with the prompt via stdin
- Pass `--model` only if a model is explicitly configured
- Set a generous timeout; raise `RuntimeError` with details on non-zero exit

### `formatter.py`
- Print a Rich `Rule` header, a `Panel` with PR metadata (URL as hyperlink, title, author, branch, file count, UTC timestamp), a `Rule` for the review section, then the review body line-by-line, and a footer `Rule`
- Kiro outputs ANSI-formatted text — strip ANSI escape codes before printing; do not use Rich's `Markdown` renderer
- Use cyan for the header/footer, yellow for the review section rule

### `cli.py`
- Accept PR URL as a positional argument; options: `--config`, `--model`, `--max-files`
- CLI flags override config values
- Print progress messages to stderr
- Handle errors cleanly with distinct exit codes for invalid input, Kiro failures, and unexpected errors

### `mcp_server.py`
- Expose a single `review_github_pull_request` tool with `pr_url` (required) and `config_path` (optional) inputs
- Return the review as plain Markdown text — do not use the Rich formatter
- Run as a stdio server using the official `mcp` Python SDK

---

## Configuration

- **Recommended:** Copy `config.example.yaml` to `~/.kiro/gh-review/config.yaml` and fill in your GitHub token — this works from any directory regardless of where the command is run
- **Alternative:** `GITHUB_TOKEN` and `KIRO_MODEL` environment variables
- **Precedence:** CLI flags > env vars > `~/.kiro/gh-review/config.yaml` > `./config.yaml` > built-in defaults
- GitHub token must have **Contents: Read** and **Pull requests: Read** permissions
- Kiro model should default to Kiro's `auto` — do not hardcode a model; make it optional in config
- `config.example.yaml` must include setup instructions as comments at the top

---

## Key Design Constraints

- **Read-only** — never post comments or modify any GitHub resource
- **No diff in output** — the prompt must instruct Kiro not to repeat the diff
- **Kiro as AI engine** — pipe the prompt to `kiro-cli`; do not call any LLM API directly
- **stdio MCP transport** — no host/port; Kiro spawns the server as a subprocess
- **ANSI stripping** — strip Kiro's ANSI escape codes before printing; print each review comment on its own line
- **Config safety** — YAML empty keys produce `None`; the deep merge must skip them to preserve defaults
- **Token safety** — treat an empty string token the same as no token (unauthenticated)

---

## Known Limitations

Be aware of these constraints when building or using the agent:

- **Binary files** — files without a text patch (images, compiled assets) are noted in the prompt but receive no diff-based review
- **Large PRs** — files beyond `max_files` are silently skipped; the agent does not warn which files were excluded
- **No codebase context** — the agent reviews only the changed files in isolation; it has no visibility into the broader codebase, which can limit the depth of architectural feedback
- **No review history** — each run is stateless; the agent has no memory of previous reviews on the same PR
- **Kiro must be authenticated separately** — the agent does not manage Kiro CLI authentication; `kiro-cli` must already be logged in before running
- **Kiro timeout** — very large prompts or slow responses may hit the subprocess timeout; no automatic retry is implemented
- **No monorepo path filtering** — all changed files up to `max_files` are reviewed regardless of which sub-package they belong to

---

## Documents to Generate

Generate the following documents with emojis and clean formatting throughout:

- **`README.md`** — features, how it works (fetch → prompt → review → display), installation (pipx global + pip local), configuration (recommended YAML + env vars table), usage modes (CLI / MCP / CI/CD), customization settings table, project structure with one-line file descriptions; link to ARCHITECTURE.md and QUICKSTART.md
- **`QUICKSTART.md`** — what's been created, project structure, prerequisites, install & configure, quick test commands, how to share with your team (push to git + team install + reinstall after updates), usage examples for all three modes, what a good review looks like (sample output), configuration reference table, troubleshooting table
- **`ARCHITECTURE.md`** — overview with ASCII data flow diagram, modules table with purpose and description, data flow steps, usage modes, authentication table, configuration precedence, key design decisions
- **`IMPROVEMENTS.md`** — potential enhancements grouped by category: review quality, output, reliability, usability, and security

---

## Using a Different AI Agent

The agent is designed around Kiro CLI but can be adapted to use any CLI-based AI tool by modifying only `reviewer.py`.

**What to change in `reviewer.py`:**
- Replace the `kiro-cli chat --no-interactive` command with the equivalent command for your chosen tool
- Adjust how the prompt is passed (stdin, a flag, or a temp file — depending on what the tool supports)
- Adjust how the model is selected (flag name, env var, or config key may differ)
- Keep the same interface: accept a prompt string, return the AI's response as a string

**Examples of drop-in replacements:**
- `claude` CLI — via stdin
- `ollama` — `ollama run <model>` with prompt via stdin
- Any tool that accepts a prompt via stdin and returns text to stdout

**Nothing else needs to change** — `config.py`, `fetcher.py`, `prompt.py`, `formatter.py`, `cli.py`, and `mcp_server.py` are all AI-tool-agnostic. Only the subprocess invocation in `reviewer.py` is Kiro-specific.
