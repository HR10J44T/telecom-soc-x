from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import hashlib
import re
from backend.app.models import Alert, Incident
from backend.app.store import ALERTS, INCIDENTS, SUMMARY, read_json, write_json
from response_engine.firewall import block_ip

FAILED_RE = re.compile(r"FAILED_LOGIN src=(?P<ip>\S+) user=(?P<user>\S+)")
PORT_RE = re.compile(r"PORT_SCAN src=(?P<ip>\S+) ports=(?P<ports>[\d,]+)")
SENSITIVE_RE = re.compile(r"SENSITIVE_ACCESS src=(?P<ip>\S+) file=(?P<file>\S+)")
ANOMALY_RE = re.compile(r"ANOMALY src=(?P<ip>\S+) metric=(?P<metric>\S+) value=(?P<value>\S+)")


def _id(prefix: str, raw: str) -> str:
    return f"{prefix}_{hashlib.sha1(raw.encode()).hexdigest()[:10]}"


def ai_explain(event_type: str, ip: str, signals: int) -> tuple[str, str, str]:
    mapping = {
        "brute_force": (
            "high",
            f"Multiple failed SSH authentication attempts from {ip} suggest credential guessing or password spraying.",
            "Block the source IP, rotate exposed credentials, and enable MFA or rate limiting.",
        ),
        "port_scan": (
            "medium",
            f"Sequential probing from {ip} indicates reconnaissance activity against exposed services.",
            "Block or tarpitted the source IP and review exposed services and firewall rules.",
        ),
        "sensitive_access": (
            "critical",
            f"Access to a protected path from {ip} may indicate privilege misuse or post-compromise discovery.",
            "Isolate the host, preserve logs, and validate file integrity immediately.",
        ),
        "anomaly": (
            "medium",
            f"Traffic or behavior anomaly from {ip} crossed the defined operational baseline.",
            "Correlate with recent deployments and inspect upstream/downstream network behavior.",
        ),
    }
    sev, desc, rec = mapping[event_type]
    return sev, desc + f" Signals observed: {signals}.", rec


def process_log_file(log_path: str) -> dict:
    path = Path(log_path)
    if not path.exists():
        return {"processed": 0, "alerts_created": 0, "incidents_created": 0}

    lines = path.read_text().splitlines()
    summary = read_json(SUMMARY)
    start = summary.get("processed_lines", 0)
    new_lines = lines[start:]
    if not new_lines:
        return {"processed": 0, "alerts_created": 0, "incidents_created": 0}

    failed = Counter()
    port_scans = defaultdict(set)
    incidents = read_json(INCIDENTS)
    alerts = read_json(ALERTS)
    created_alerts = 0
    created_incidents = 0

    for line in new_lines:
        ts = datetime.utcnow().isoformat() + "Z"
        if m := FAILED_RE.search(line):
            ip = m.group("ip")
            failed[ip] += 1
        elif m := PORT_RE.search(line):
            ip = m.group("ip")
            for p in m.group("ports").split(','):
                port_scans[ip].add(p)
        elif m := SENSITIVE_RE.search(line):
            ip = m.group("ip")
            sev, desc, rec = ai_explain("sensitive_access", ip, 1)
            alert = Alert(
                id=_id("alert", line), timestamp=ts, source_ip=ip, event_type="sensitive_access",
                severity=sev, confidence=97, description=desc, recommendation=rec, auto_action="host_isolation_recommended"
            ).model_dump()
            alerts.append(alert); created_alerts += 1
            incidents.append(Incident(
                id=_id("inc", line), title="Sensitive File Access", source_ip=ip, severity=sev, status="investigating",
                duration_minutes=1, signals=1, ai_explanation=desc,
                timeline=[{"time": ts, "event": "Sensitive access detected", "status": "investigating"}]
            ).model_dump()); created_incidents += 1
        elif m := ANOMALY_RE.search(line):
            ip = m.group("ip")
            sev, desc, rec = ai_explain("anomaly", ip, 1)
            alerts.append(Alert(
                id=_id("alert", line), timestamp=ts, source_ip=ip, event_type="anomaly",
                severity=sev, confidence=75, description=desc, recommendation=rec
            ).model_dump()); created_alerts += 1

    for ip, count in failed.items():
        if count >= 8:
            sev, desc, rec = ai_explain("brute_force", ip, count)
            block = block_ip(ip, "brute_force_detected")
            raw = f"bruteforce:{ip}:{count}"
            alerts.append(Alert(
                id=_id("alert", raw), timestamp=datetime.utcnow().isoformat() + "Z", source_ip=ip,
                event_type="brute_force", severity=sev, confidence=95, description=desc,
                recommendation=rec, auto_action=block["status"]
            ).model_dump()); created_alerts += 1
            incidents.append(Incident(
                id=_id("inc", raw), title="SSH Brute Force", source_ip=ip, severity=sev, status="contained",
                duration_minutes=5, signals=count, ai_explanation=desc,
                timeline=[
                    {"time": datetime.utcnow().isoformat() + "Z", "event": f"{count} failed logins detected", "status": "new"},
                    {"time": datetime.utcnow().isoformat() + "Z", "event": f"IP {ip} auto-blocked", "status": "contained"},
                ]
            ).model_dump()); created_incidents += 1

    for ip, ports in port_scans.items():
        if len(ports) >= 10:
            sev, desc, rec = ai_explain("port_scan", ip, len(ports))
            raw = f"portscan:{ip}:{len(ports)}"
            alerts.append(Alert(
                id=_id("alert", raw), timestamp=datetime.utcnow().isoformat() + "Z", source_ip=ip,
                event_type="port_scan", severity=sev, confidence=88, description=desc,
                recommendation=rec
            ).model_dump()); created_alerts += 1
            incidents.append(Incident(
                id=_id("inc", raw), title="Port Scan Reconnaissance", source_ip=ip, severity=sev, status="new",
                duration_minutes=3, signals=len(ports), ai_explanation=desc,
                timeline=[{"time": datetime.utcnow().isoformat() + "Z", "event": f"{len(ports)} probed ports observed", "status": "new"}]
            ).model_dump()); created_incidents += 1

    write_json(ALERTS, alerts)
    write_json(INCIDENTS, incidents)
    summary["processed_lines"] = len(lines)
    write_json(SUMMARY, summary)
    return {"processed": len(new_lines), "alerts_created": created_alerts, "incidents_created": created_incidents}
