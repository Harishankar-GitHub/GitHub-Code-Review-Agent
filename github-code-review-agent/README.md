# 🤖 GitHub Code Review AI Agent using Kiro CLI

An AI-powered GitHub Pull Request code reviewer that uses **Kiro CLI** to generate detailed, professional review comments — printed directly to your console.

## ✨ Features

- 🔍 Fetches PR changes from GitHub using the REST API
- 🤖 Generates AI-powered review comments via Kiro CLI
- 🎨 Clean, emoji-rich console output with header/footer
- 🔒 Read-only — never writes back to GitHub
- ⚙️ Three usage modes: **CLI**, **MCP Server** (Kiro integration), **CI/CD**
- 📋 Configurable focus areas: code quality, security, best practices, performance, test coverage, commit message, PR title

---

## 🔍 How It Works

1. **Fetch** — the agent parses the PR URL and calls the GitHub REST API to retrieve PR metadata and the unified diff for each changed file
2. **Prompt** — it builds a structured Markdown prompt containing the PR details, diffs, and your configured focus areas and severity threshold
3. **Review** — the prompt is piped to `kiro-cli chat --no-interactive` via stdin; Kiro's AI generates the review and returns it as text
4. **Display** — the output is stripped of ANSI codes and rendered to the console via Rich, with a header panel, per-file comments, and a summary verdict

Nothing is written back to GitHub at any point.

---

## 🚀 Installation

**Requirements:** Python 3.10+, [pipx](https://pipx.pypa.io/), [Kiro CLI](https://kiro.dev/downloads/)

```bash
git clone https://github.com/your-org/github-code-review-agent
cd github-code-review-agent
```

**Global install (recommended) — available from anywhere:**
```bash
pipx install .
```

**Local install (virtualenv only):**
```bash
pip install -e .
```

---

## ⚙️ Configuration

> **Recommended:** Use `~/.kiro/gh-review/config.yaml` for persistent configuration. Alternatively, set credentials via environment variables for quick use or CI/CD.

Copy `config.example.yaml` to `~/.kiro/gh-review/config.yaml` and fill in your GitHub token:

```bash
mkdir -p ~/.kiro/gh-review
cp config.example.yaml ~/.kiro/gh-review/config.yaml
```

```yaml
github:
  token: "ghp_..."   # Fine-grained PAT with Contents: Read + Pull requests: Read

kiro:
  # model: "auto"    # optional override

review:
  focus:
    - code_quality
    - security
    - best_practices
    - performance
    - test_coverage
    # - commit_message
    # - pull_request_title
  severity_threshold: "low"
  max_files: 50
```

### 🌍 Environment Variables

Environment variables override values in `config.yaml`.

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub fine-grained PAT (overrides config) |
| `KIRO_MODEL` | Kiro model override (overrides config) |

---

## 🛠️ Usage Modes

### 1. 💻 Standalone CLI

```bash
gh-review https://github.com/owner/repo/pull/42
```

Options:
```
--config, -c    Path to config.yaml (default: ~/.kiro/gh-review/config.yaml)
--model,  -m    Override Kiro model (e.g. claude-sonnet-4-5)
--max-files     Max number of files to review
```

See [QUICKSTART.md](docs/QUICKSTART.md) for setup steps and more usage examples.

### 2. 🔌 MCP Server (Kiro Integration)

Register the agent as an MCP server in Kiro using the CLI or by editing `~/.kiro/settings/mcp.json`. See [QUICKSTART.md](docs/QUICKSTART.md) for exact setup steps.

Once registered, ask Kiro:
> "Review this PR: https://github.com/owner/repo/pull/42"

### 3. 🔄 CI/CD (GitHub Actions / Jenkins)

See [CI_CD.md](docs/CI_CD.md) for GitHub Actions and Jenkins setup instructions.

---

## 🎛️ Customization

| Setting | Default | Description |
|---|---|---|
| `review.focus` | all areas | Which aspects to review: `code_quality`, `security`, `best_practices`, `performance`, `test_coverage`, `commit_message`, `pull_request_title` |
| `review.severity_threshold` | `low` | Minimum severity to report: `low`, `medium`, `high` |
| `review.max_files` | `50` | Max files reviewed per PR |
| `kiro.model` | _(auto)_ | Kiro model to use — omit to let Kiro choose automatically |

---

## 📁 Project Structure

```
github-code-review-agent/
├── src/
│   └── github_code_review_agent/
│       ├── __init__.py     # Public API — exposes PRInfo, FileChange
│       ├── cli.py          # CLI entry point — parses arguments, orchestrates fetch → review → display
│       ├── mcp_server.py   # MCP stdio server — exposes review_github_pull_request tool for Kiro integration
│       ├── config.py       # Config loader — merges ~/.kiro/gh-review/config.yaml with env var overrides
│       ├── fetcher.py      # GitHub fetcher — parses PR URL, calls GitHub REST API, returns PRInfo dataclass
│       ├── prompt.py       # Prompt builder — constructs the structured review prompt sent to Kiro CLI
│       ├── reviewer.py     # Kiro invoker — pipes prompt to kiro-cli chat, captures and returns review text
│       └── formatter.py    # Output formatter — renders header panel, review comments, footer via Rich
├── docs/
│   ├── ARCHITECTURE.md     # Detailed design overview
│   ├── QUICKSTART.md       # Setup steps and usage examples
│   ├── CI_CD.md            # GitHub Actions and Jenkins integration
│   ├── IMPROVEMENTS.md     # Potential enhancements and ideas
│   └── PROMPT.md           # Original prompt used to generate this agent
├── config.example.yaml     # Annotated example config — copy to ~/.kiro/gh-review/config.yaml
├── pyproject.toml          # Package metadata and gh-review entry point
├── README.md
└── .gitignore
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for a detailed design overview.

---

## 🎓 Concepts Learnt

| Concept | What it is |
|---|---|
| **Prompt Engineering** | Crafting structured, instruction-rich text inputs to guide an AI model toward producing accurate, well-formatted outputs |
| **Kiro CLI** | A command-line interface for interacting with Kiro's AI — used here to pipe review prompts and capture AI-generated responses |
| **Kiro IDE** | An AI-powered development environment by AWS that integrates AI assistance directly into the coding workflow |
| **MCP (Model Context Protocol)** | An open protocol that standardises how applications expose tools and context to AI models |
| **MCP Server** | A lightweight server that implements MCP — exposes tools (like `review_github_pull_request`) that an AI can discover and call |
| **Agentic AI** | AI that autonomously takes actions (fetching data, calling tools, producing output) to complete a goal, rather than just answering questions |
| **GitHub REST API** | GitHub's HTTP API for programmatically reading repository data — used here to fetch PR metadata and file diffs |
| **Unified Diff / Patch** | A standard text format for representing code changes — the `+`/`-` line format used in `git diff` output |
| **pipx** | A tool for installing Python CLI applications in isolated virtual environments, making them globally available |
| **`src` layout** | A Python project structure convention where source code lives under `src/` to prevent accidental imports from the project root |
| **`pyproject.toml`** | The modern Python packaging standard for declaring project metadata, dependencies, and build configuration |
| **subprocess** | Python's built-in module for spawning and communicating with external processes — used to invoke `kiro-cli` |
| **Dataclasses** | Python's `@dataclass` decorator for creating lightweight, structured data containers with minimal boilerplate |
| **Rich** | A Python library for rendering formatted, coloured terminal output including panels, rules, and styled text |
| **Click** | A Python library for building CLI applications with commands, arguments, and options declaratively |
