from pathlib import Path
import json
base = Path("data/state")
base.mkdir(parents=True, exist_ok=True)
for name, default in {
    "alerts.json": [],
    "incidents.json": [],
    "blocked_ips.json": [],
    "summary.json": {"processed_lines": 0},
}.items():
    (base / name).write_text(json.dumps(default, indent=2))
Path("data/logs/telecom.log").write_text("")
print("State reset complete.")
