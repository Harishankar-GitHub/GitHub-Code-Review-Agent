# 🚀 Potential Improvements

Impactful enhancements that could make this agent more powerful, reliable, and useful.

---

## 🧠 Higher Review Quality

**PR Context**
Include the linked issue description or recent base branch commits in the prompt so the AI understands *why* the change exists, not just *what* changed. Results in more relevant, less generic feedback.

**Review History**
If the same PR was reviewed before, pass the previous comments into the prompt so the AI doesn't repeat itself across re-reviews. This is especially useful for PRs that go through multiple rounds of feedback — the AI can acknowledge what was already addressed and focus only on remaining or new issues.

**Full Codebase Context + Targeted Review**
Rather than reviewing only the changed files in isolation, first give the AI a read of the broader codebase — key files like interfaces, base classes, shared utilities, and entry points — so it understands the architecture and conventions. Then present the PR diff as the thing to actually review. This two-step approach produces significantly better feedback: the AI can spot inconsistencies with existing patterns, flag violations of project conventions, and identify ripple effects of the change that wouldn't be visible from the diff alone. In practice, this means building the prompt in two parts — a codebase context section (summarised or truncated to fit) followed by the changed files section.

**Language-Aware Prompting**
Detect the primary language(s) in the PR and tailor the prompt accordingly — e.g. stricter type safety checks for TypeScript, memory safety for C++, idiomatic style for Go.

---

## 📋 More Useful Output

**Inline Line References**
For each issue raised, show the exact lines being flagged — not just the filename — so the reviewer can act immediately without cross-referencing the diff.

**Severity Summary at the Top**
Print a quick count of 🔴 High / 🟡 Medium / 🟢 Low issues before the full review body, so you can triage at a glance.

**Exit Code Based on Verdict**
Exit `1` if the verdict is ❌ Request Changes, exit `0` if ✅ Approved. Makes CI/CD quality gates trivial to set up with no extra tooling.

---

## 🔧 Reliability

**Retry on Timeout**
`reviewer.py` raises a `RuntimeError` on timeout after 300 seconds. A single retry with exponential backoff would handle transient Kiro CLI failures more gracefully.

**Large PR Warning**
When the number of changed files exceeds `max_files`, explicitly warn the user which files were skipped rather than silently dropping them.

---

## 🛠️ Usability

**`--dry-run` Flag**
Print the exact prompt that would be sent to Kiro without actually running the review. Useful for debugging and prompt tuning without consuming AI credits.

**`--output` Flag**
Save the review to a file in addition to printing it to the console. Useful in CI pipelines where you want a persistent artifact.

---

## 🔒 Security

**Token Validation on Startup**
Make a lightweight API call (e.g. `GET /user`) before fetching the PR to validate the token and its permissions. Fail fast with a clear error message rather than failing mid-review with a cryptic API error.
