from __future__ import annotations
from pathlib import Path
import json
from typing import Any
from backend.app.config import settings

ALERTS = settings.state_path / "alerts.json"
INCIDENTS = settings.state_path / "incidents.json"
BLOCKED = settings.state_path / "blocked_ips.json"
SUMMARY = settings.state_path / "summary.json"


def _ensure(path: Path, default: Any):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2))


def init_state() -> None:
    _ensure(ALERTS, [])
    _ensure(INCIDENTS, [])
    _ensure(BLOCKED, [])
    _ensure(SUMMARY, {"processed_lines": 0})


def read_json(path: Path):
    init_state()
    return json.loads(path.read_text())


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))
