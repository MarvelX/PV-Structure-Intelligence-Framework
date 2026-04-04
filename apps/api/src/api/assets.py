from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class AssetCatalog:
    waterbase_rules: List[Dict[str, Any]]
    overseas_rules: List[Dict[str, Any]]
    waterbase_template: str
    overseas_template: str


def load_catalog(assets_dir: Path) -> AssetCatalog:
    rules_dir = assets_dir / "rules"
    templates_dir = assets_dir / "templates"
    return AssetCatalog(
        waterbase_rules=_load_json(rules_dir / "waterbase_rules.json"),
        overseas_rules=_load_json(rules_dir / "overseas_rules.json"),
        waterbase_template=(templates_dir / "waterbase_summary_template.md").read_text(encoding="utf-8"),
        overseas_template=(templates_dir / "overseas_summary_template.md").read_text(encoding="utf-8"),
    )


def _load_json(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))
