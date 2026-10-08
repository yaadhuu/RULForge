"""Load YAML settings from configs/. A run is reproducible from (config contents, seed)."""
from __future__ import annotations

from pathlib import Path

import yaml

# src/rulforge/config.py -> project root is two levels above the package folder
ROOT = Path(__file__).resolve().parents[2]


def load_config(name: str) -> dict:
    """load_config("data") reads configs/data.yaml."""
    path = ROOT / "configs" / f"{name}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)
