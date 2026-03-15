"""GitHub PR fetcher — retrieves PR metadata and per-file diff patches."""

import re
from dataclasses import dataclass

from github import Github, Auth
from github.PullRequest import PullRequest


@dataclass
class FileChange:
    """Represents a single changed file in a Pull Request."""

    filename: str
    status: str          # added | modified | removed | renamed
    additions: int
    deletions: int
    patch: str | None    # unified diff patch (None for binary files)


@dataclass
class PRInfo:
    """Holds all metadata and changed files for a Pull Request."""

    url: str
    number: int
    title: str
    description: str
    author: str
    base_branch: str
    head_branch: str
    files: list[FileChange]


def parse_pr_url(url: str) -> tuple[str, int]:
    """Parse 'https://github.com/owner/repo/pull/123' → ('owner/repo', 123)."""
    match = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", url.strip())
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}")
    return match.group(1), int(match.group(2))


def fetch_pr(pr_url: str, token: str | None, max_files: int = 50) -> PRInfo:
    """Fetch PR metadata and changed files from GitHub."""
    repo_name, pr_number = parse_pr_url(pr_url)

    auth = Auth.Token(token) if token else None
    gh = Github(auth=auth)

    repo = gh.get_repo(repo_name)
    pr: PullRequest = repo.get_pull(pr_number)

    files = []
    for f in pr.get_files():
        if len(files) >= max_files:
            break
        files.append(FileChange(
            filename=f.filename,
            status=f.status,
            additions=f.additions,
            deletions=f.deletions,
            patch=getattr(f, "patch", None),
        ))

    return PRInfo(
        url=pr_url,
        number=pr_number,
        title=pr.title,
        description=pr.body or "",
        author=pr.user.login,
        base_branch=pr.base.ref,
        head_branch=pr.head.ref,
        files=files,
    )
