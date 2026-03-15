"""Configuration loader — merges config.yaml with environment variable overrides."""

import os
from pathlib import Path
from typing import Any

import yaml

_DEFAULTS: dict[str, Any] = {
    "github": {"token": ""},
    "kiro": {},
    "review": {
        "focus": ["code_quality", "security", "best_practices", "performance", "test_coverage"],
        "severity_threshold": "low",
        "max_files": 50,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, skipping None values from YAML empty keys."""
    result = base.copy()
    for k, v in override.items():
        if v is None:
            continue  # YAML empty key (e.g. `kiro:`) — keep default
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load config from YAML file then apply env var overrides."""
    cfg = _deep_merge({}, _DEFAULTS)

    if config_path:
        path = Path(config_path)
    elif (kiro_cfg := Path.home() / ".kiro" / "gh-review" / "config.yaml").exists():
        path = kiro_cfg
    else:
        path = Path("config.yaml")
    if path.exists():
        with path.open() as f:
            file_cfg = yaml.safe_load(f) or {}
        cfg = _deep_merge(cfg, file_cfg)

    # Environment variable overrides
    if token := os.getenv("GITHUB_TOKEN"):
        cfg["github"]["token"] = token
    if model := os.getenv("KIRO_MODEL"):
        cfg["kiro"]["model"] = model

    return cfg
