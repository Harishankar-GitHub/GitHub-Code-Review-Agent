# ⚡ Quickstart Guide

---

## 🤖 What's Been Created

The GitHub Code Review AI Agent is a Python-based CLI tool that:

- 🔍 Fetches changed files from any GitHub Pull Request
- 🧠 Sends the code to **Kiro CLI** for AI-powered review
- 🎨 Prints clean, emoji-rich review comments to your console — organised by file and severity
- 🔒 Never writes back to GitHub (read-only)

It supports three usage modes: standalone CLI, MCP server (Kiro integration), and CI/CD pipelines.

---

## 📁 Project Structure

```
github-code-review-agent/
├── src/
│   └── github_code_review_agent/
│       ├── __init__.py         # Public API — exposes PRInfo, FileChange
│       ├── cli.py              # CLI entry point — parses args, orchestrates fetch → review → display
│       ├── mcp_server.py       # MCP stdio server — exposes review_github_pull_request tool for Kiro integration
│       ├── config.py           # Config loader — merges ~/.kiro/gh-review/config.yaml with env vars
│       ├── fetcher.py          # GitHub fetcher — parses PR URL, calls GitHub REST API, returns PRInfo
│       ├── prompt.py           # Prompt builder — constructs the structured review prompt for Kiro CLI
│       ├── reviewer.py         # Kiro invoker — pipes prompt to kiro-cli chat, captures review text
│       └── formatter.py        # Output formatter — renders header, review comments, footer via Rich
├── docs/
│   ├── ARCHITECTURE.md         # Detailed design overview
│   ├── QUICKSTART.md           # Setup steps and usage examples
│   ├── CI_CD.md                # GitHub Actions and Jenkins integration
│   ├── IMPROVEMENTS.md         # Potential enhancements and ideas
│   └── PROMPT.md               # Original prompt used to generate this agent
├── config.example.yaml         # Annotated example config — copy to ~/.kiro/gh-review/config.yaml
├── pyproject.toml              # Package metadata and gh-review entry point
├── README.md
└── .gitignore
```

---

## 🛠️ Prerequisites

- 🐍 Python 3.10+
- 📦 [pipx](https://pipx.pypa.io/) (`sudo apt install pipx` / `brew install pipx`)
- 🤖 [Kiro CLI](https://kiro.dev/downloads/) installed and authenticated (`kiro-cli --version`)
- 🔑 A GitHub fine-grained PAT with **Contents: Read** and **Pull requests: Read** permissions

---

## 🚀 Install & Configure

**1. Clone and install globally:**

```bash
git clone https://github.com/your-org/github-code-review-agent
cd github-code-review-agent
pipx install .
```

**2. Set up config:**

> **Recommended:** Use `~/.kiro/gh-review/config.yaml` for persistent configuration. Alternatively, set credentials via environment variables for quick use or CI/CD.

```bash
mkdir -p ~/.kiro/gh-review
cp config.example.yaml ~/.kiro/gh-review/config.yaml
```

Edit `~/.kiro/gh-review/config.yaml` and add your GitHub token:

```yaml
github:
  token: "ghp_your_fine_grained_pat"
```

Or use environment variables instead (no config file needed):

```bash
export GITHUB_TOKEN="ghp_your_fine_grained_pat"
export KIRO_MODEL="claude-sonnet-4-5"   # optional
```

---

## 🧪 Quick Test

Run a review on any public PR to verify everything works:

```bash
# 🌐 Public repo — no token needed
gh-review https://github.com/f/prompts.chat/pull/1075

# 🔒 Private repo — token required
GITHUB_TOKEN=ghp_your_token gh-review https://github.com/your-org/your-repo/pull/1

# ⚡ Limit to 5 files for a quick test
gh-review https://github.com/owner/repo/pull/42 --max-files 5
```

You should see a formatted review with a header panel, per-file comments, and a verdict.

---

## 🤝 How to Share With Your Team

### 📤 Push to Git

```bash
git init
git add .
git commit -m "feat: GitHub Code Review AI Agent"
git remote add origin https://github.com/your-org/github-code-review-agent.git
git push -u origin main
```

### 📥 Team members install it

```bash
# Global install from Git
pipx install git+https://github.com/your-org/github-code-review-agent.git

# Or clone and install locally
git clone https://github.com/your-org/github-code-review-agent
cd github-code-review-agent
pipx install .
```

Each team member sets up their own `~/.kiro/gh-review/config.yaml` with their own GitHub token.

> **🔄 After any code update**, reinstall to pick up the changes:
> ```bash
> cd github-code-review-agent
> git pull
> pipx reinstall github-code-review-agent
> ```

---

## 💡 Usage Examples

### 💻 CLI Tool

```bash
# Basic review
gh-review https://github.com/owner/repo/pull/42

# Override model
gh-review https://github.com/owner/repo/pull/42 --model claude-sonnet-4-5

# Limit files reviewed
gh-review https://github.com/owner/repo/pull/42 --max-files 20

# Use a custom config file
gh-review https://github.com/owner/repo/pull/42 --config /path/to/config.yaml
```

### 🔌 MCP Server — Kiro Integration

Register the agent so Kiro can call it as a tool directly from chat.

**Option A — Command line:**

```bash
kiro-cli mcp add \
  --name "github-code-review" \
  --scope global \
  --command "/home/your-user/.local/share/pipx/venvs/github-code-review-agent/bin/python3" \
  --args "-m" \
  --args "github_code_review_agent.mcp_server"
```

> Replace `/home/your-user/` with your actual home directory path. Find it with:
> ```bash
> echo /home/$(whoami)/.local/share/pipx/venvs/github-code-review-agent/bin/python3
> ```

**Option B — Edit `~/.kiro/settings/mcp.json` manually:**

```json
{
  "mcpServers": {
    "github-code-review": {
      "command": "/home/your-user/.local/share/pipx/venvs/github-code-review-agent/bin/python3",
      "args": ["-m", "github_code_review_agent.mcp_server"],
      "disabled": false
    }
  }
}
```

> Replace `/home/your-user/` with your actual home directory (`echo $HOME`).
> Use `<project-root>/.kiro/settings/mcp.json` instead for project-scoped registration.

> **💡 Note:** No need to set `GITHUB_TOKEN` in `mcp.json` — the agent reads it from `~/.kiro/gh-review/config.yaml` or your shell environment automatically. You can optionally add it to `mcp.json` as a fallback if Kiro spawns the server in a clean environment that doesn't inherit your shell's env vars.

**✅ Verify it loaded** — inside a Kiro chat session:
```
/mcp
```
You should see `github-code-review` listed with the `review_github_pull_request` tool.

**💬 Use from Kiro chat:**
```
> Review this PR: https://github.com/owner/repo/pull/42
```

Kiro calls the `review_github_pull_request` tool automatically and prints the review in chat.

### 🔄 CI/CD Integration

See [CI_CD.md](CI_CD.md) for GitHub Actions and Jenkins setup instructions.

---

## ⚙️ Configuration Reference

> **Recommended:** Use `~/.kiro/gh-review/config.yaml` for persistent configuration. Alternatively, set credentials via environment variables for quick use or CI/CD.

Config is loaded from `~/.kiro/gh-review/config.yaml` by default. All values can be overridden by environment variables.

| Setting | Env var | Default | Description |
|---|---|---|---|
| `github.token` | `GITHUB_TOKEN` | `""` | GitHub fine-grained PAT |
| `kiro.model` | `KIRO_MODEL` | _(Kiro default: auto)_ | Kiro model to use |
| `review.severity_threshold` | — | `low` | Minimum severity to report (`low`/`medium`/`high`) |
| `review.max_files` | — | `50` | Max files reviewed per PR |
| `review.focus` | — | all areas | Focus areas: `code_quality`, `security`, `best_practices`, `performance`, `test_coverage`, `commit_message`, `pull_request_title` |

**Config precedence:**
```
--config flag  >  env vars  >  ~/.kiro/gh-review/config.yaml  >  ./config.yaml  >  built-in defaults
```

## 👀 What a Good Review Looks Like

When the agent is working correctly, you should see output structured like this:

```
──────────────────────── 🤖  GitHub AI Code Review ────────────────────────

╭─ Pull Request ────────────────────────────────────────────────────────╮
│ 📌 PR:     https://github.com/owner/repo/pull/42                      │
│ 📝 Title:  Fix null pointer in user auth flow                         │
│ 👤 Author: octocat                                                    │
│ 🌿 Branch: fix/auth-null → main                                       │
│ 📂 Files:  3 changed                                                  │
│ 🕐 Time:   2026-03-15 14:30 UTC                                       │
╰───────────────────────────────────────────────────────────────────────╯

──────────────────────── 📋  Review Comments ───────────────────────────

> ## Code Review: "Fix null pointer in user auth flow"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📄 src/auth/login.py

🔴 High — Line 42: Potential null dereference on `user.token`
The token is accessed without a null check. If the auth provider returns
an empty response, this will raise an AttributeError.
Fix: add `if not user or not user.token: raise AuthError(...)`

🟢 Low — Line 78: Magic number should be a named constant
Extract `30` to a constant for clarity and maintainability.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📄 tests/test_login.py

🟡 Medium — Missing test case for expired token scenario
The null pointer fix has no corresponding test coverage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary

| Area | Finding |
|---|---|
| Code Quality | Null dereference on user.token |
| Test Coverage | Missing test for expired token |
| Security | ✅ Clean |

## Verdict: ⚠️ Needs Changes

────────────────────────────────────────────────────────────────────────
          ⚡ Powered by Kiro CLI  •  GitHub Code Review Agent
```

If the output looks like this — formatted header panel, per-file comments with severity emojis, a summary table, and a verdict — the agent is working correctly.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `kiro-cli: command not found` | Install Kiro CLI from [kiro.dev/downloads](https://kiro.dev/downloads/) and ensure it's on your PATH |
| `401 Unauthorized` from GitHub | Check your `GITHUB_TOKEN` is valid and has `Contents: Read` + `Pull requests: Read` permissions |
| `kiro-cli exited with code 1` | Run `kiro-cli --version` to confirm it's authenticated |
| Review output is empty | The PR may have no reviewable files (binary-only or exceeds `max_files`) |
| MCP tool not showing in Kiro | Run `/mcp` in Kiro chat to check; verify `mcp.json` syntax is valid JSON |
| Code changes not taking effect | pipx installs into an isolated venv — run `pipx reinstall github-code-review-agent` after any code update |
