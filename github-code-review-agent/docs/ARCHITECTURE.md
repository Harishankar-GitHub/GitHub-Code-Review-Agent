# 🏗️ Architecture

## 🔍 Overview

The GitHub Code Review AI Agent is a lightweight Python tool that bridges the GitHub API and Kiro CLI to produce AI-powered PR reviews in the console. It is intentionally read-only — it never writes back to GitHub.

```
PR URL
  │
  ▼
┌─────────────┐     GitHub REST API      ┌──────────────┐
│   CLI / MCP │ ──── fetch PR files ───► │   fetcher.py │
│   Entry     │                          └──────┬───────┘
└─────────────┘                                 │ PRInfo
                                                ▼
                                        ┌──────────────┐
                                        │   prompt.py  │  builds structured prompt
                                        └──────┬───────┘
                                                │ prompt string
                                                ▼
                                        ┌──────────────┐
                                        │  reviewer.py │  subprocess → kiro-cli chat
                                        └──────┬───────┘
                                                │ review text
                                                ▼
                                        ┌──────────────┐
                                        │ formatter.py │  Rich console output
                                        └──────────────┘
```

---

## 📦 Modules

| Module | Purpose | What it does |
|---|---|---|
| `__init__.py` | 📌 Public API | Exposes `PRInfo` and `FileChange` as the public API surface for programmatic use |
| `config.py` | ⚙️ Configuration loader | Reads `~/.kiro/gh-review/config.yaml` (falling back to `./config.yaml`), deep-merges with built-in defaults, then applies `GITHUB_TOKEN` and `KIRO_MODEL` env var overrides |
| `fetcher.py` | 🔍 GitHub PR fetcher | Parses the PR URL to extract owner, repo and PR number; calls the GitHub REST API via PyGithub to retrieve PR metadata (title, author, branches, description) and per-file patches; skips binary files and enforces `max_files` limit; returns a `PRInfo` dataclass |
| `prompt.py` | 📝 Review prompt builder | Takes a `PRInfo` and review settings (focus areas, severity threshold) and assembles a structured Markdown prompt that instructs Kiro to review each changed file, report issues by severity, suggest fixes, and produce a final verdict |
| `reviewer.py` | 🤖 Kiro CLI invoker | Pipes the prompt to `kiro-cli chat --no-interactive` via stdin as a subprocess; optionally passes `--model` if configured; captures stdout as the review text; raises `RuntimeError` on non-zero exit or timeout |
| `formatter.py` | 🎨 Console output renderer | Strips ANSI escape codes from Kiro CLI output, then prints a Rich header panel (PR URL, title, author, branch, file count, timestamp), the review line-by-line, and a footer rule |
| `cli.py` | 💻 Standalone CLI entry point | Click command registered as `gh-review`; accepts PR URL, optional `--config`, `--model`, `--max-files` flags; orchestrates config load → fetch → review → display and handles errors with clean exit codes |
| `mcp_server.py` | 🔌 MCP stdio server | Uses the official `mcp` Python SDK to expose a single `review_github_pull_request` tool over stdio transport; Kiro spawns this as a subprocess and calls it when asked to review a PR; returns the formatted review as a text response |

---

## 🔄 Data Flow

1. **📥 Input** — A GitHub PR URL (`https://github.com/owner/repo/pull/N`)
2. **🔍 Fetch** — `fetcher.py` calls the GitHub REST API to retrieve PR metadata and per-file patches (unified diff). Binary files and files beyond `max_files` are skipped.
3. **📝 Prompt** — `prompt.py` assembles a structured prompt containing PR context, changed file patches, and review instructions (focus areas, severity threshold).
4. **🤖 Review** — `reviewer.py` pipes the prompt to `kiro-cli chat --no-interactive` via stdin and captures stdout.
5. **🎨 Display** — `formatter.py` strips ANSI escape codes from Kiro's output, then renders a Rich header panel with PR metadata, prints each review line individually for clean per-comment formatting, and closes with a footer rule.

---

## 🛠️ Usage Modes

### 💻 Standalone CLI
`cli.py` uses Click. The `gh-review` command is registered via `pyproject.toml` entry point. All config can be overridden via CLI flags.

### 🔌 MCP Server
`mcp_server.py` uses the official `mcp` Python SDK with `stdio` transport. Kiro spawns the server as a subprocess and communicates over stdin/stdout. The server exposes a single tool: `review_github_pull_request`.

### 🔄 CI/CD
The agent is a standard CLI tool — any CI system can run `gh-review <PR_URL>` as a build step. See [CI_CD.md](CI_CD.md) for GitHub Actions and Jenkins integration instructions.

---

## 🔑 Authentication

| Method | When to use |
|---|---|
| 🔐 Fine-grained PAT (`GITHUB_TOKEN`) | Local use, CI/CD, public or private repos — needs `Contents: Read` + `Pull requests: Read` |
| 🌐 No token | Public repos only (subject to rate limits) |

The agent only requires **read** access. It never posts comments or modifies any GitHub resource.

---

## ⚙️ Configuration Precedence

> **Recommended:** Use `~/.kiro/gh-review/config.yaml` for persistent configuration. Alternatively, set `GITHUB_TOKEN` and `KIRO_MODEL` as environment variables for quick use or CI/CD.

```
CLI flags  >  Environment variables  >  ~/.kiro/gh-review/config.yaml  >  ./config.yaml  >  built-in defaults
```

---

## 🧠 Key Design Decisions

- 🔒 **Read-only** — No GitHub write permissions required or used.
- 🤖 **Kiro as the AI engine** — The agent delegates all AI reasoning to `kiro-cli`. It does not call any LLM API directly.
- 🚫 **No diff in output** — The prompt instructs Kiro not to repeat the diff; only review comments are shown.
- 📡 **stdio MCP transport** — Matches Kiro's native integration model; no network port required.
- 🎨 **Rich for output** — Provides a clean, coloured console output. ANSI escape codes from Kiro CLI are stripped and the review is printed line-by-line so each comment appears on its own line with clear separation.

---

## 📦 Libraries & Dependencies

| Library | Version | Purpose |
|---|---|---|
| [PyGithub](https://github.com/PyGithub/PyGithub) | `>=2.1.1` | GitHub REST API client — fetches PR metadata and per-file patches |
| [PyYAML](https://pyyaml.org/) | `>=6.0` | Parses `config.yaml` configuration files |
| [mcp](https://github.com/modelcontextprotocol/python-sdk) | `>=1.0.0` | Official MCP Python SDK — powers the stdio MCP server for Kiro integration |
| [click](https://click.palletsprojects.com/) | `>=8.1.0` | CLI framework — defines the `gh-review` command, arguments, and options |
| [rich](https://rich.readthedocs.io/) | `>=13.0.0` | Terminal output formatting — renders the header panel, review body, and footer |

**External tools (not pip dependencies):**

| Tool | Purpose |
|---|---|
| [Kiro CLI](https://kiro.dev/downloads/) | AI engine — receives the review prompt via stdin and returns the review text |
