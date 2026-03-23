from collections import Counter
from backend.app.store import ALERTS, INCIDENTS, BLOCKED, read_json


def get_dashboard_summary() -> dict:
    alerts = read_json(ALERTS)
    incidents = read_json(INCIDENTS)
    blocked = read_json(BLOCKED)
    sev = Counter(a["severity"] for a in alerts)
    status = Counter(i["status"] for i in incidents)
    top_ips = Counter(a["source_ip"] for a in alerts).most_common(5)
    return {
        "alerts_total": len(alerts),
        "incidents_total": len(incidents),
        "blocked_total": len(blocked),
        "severity": {k: sev.get(k, 0) for k in ["critical", "high", "medium", "low"]},
        "status": dict(status),
        "top_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
    }
