from __future__ import annotations
from datetime import datetime
from backend.app.store import BLOCKED, read_json, write_json
from backend.app.config import settings


def block_ip(ip: str, reason: str) -> dict:
    blocked = read_json(BLOCKED)
    if any(row["ip"] == ip for row in blocked):
        return {"status": "already_blocked", "ip": ip}

    action = {
        "ip": ip,
        "blocked_at": datetime.utcnow().isoformat() + "Z",
        "reason": reason,
        "mode": "live_iptables" if settings.auto_block else "simulation_only",
        "command": f"sudo iptables -A INPUT -s {ip} -j DROP",
    }
    blocked.append(action)
    write_json(BLOCKED, blocked)
    return {"status": "blocked", **action}
