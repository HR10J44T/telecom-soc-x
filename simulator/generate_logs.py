from pathlib import Path
from random import choice, randint
from datetime import datetime

LOG = Path("data/logs/telecom.log")
LOG.parent.mkdir(parents=True, exist_ok=True)
ips = ["10.10.2.14", "172.16.0.23", "185.22.9.41", "45.77.10.9"]
users = ["root", "admin", "ubuntu", "ops"]

entries = []
for _ in range(20):
    entries.append(f"{datetime.utcnow().isoformat()}Z INFO FAILED_LOGIN src={choice(ips)} user={choice(users)}")
for _ in range(5):
    base = randint(20, 80)
    ports = ",".join(str(base + i) for i in range(12))
    entries.append(f"{datetime.utcnow().isoformat()}Z WARN PORT_SCAN src={choice(ips)} ports={ports}")
entries.append(f"{datetime.utcnow().isoformat()}Z ALERT SENSITIVE_ACCESS src=45.77.10.9 file=/etc/shadow")
entries.append(f"{datetime.utcnow().isoformat()}Z WARN ANOMALY src=10.10.2.14 metric=bps value=9900000")

with LOG.open("a") as f:
    f.write("\n".join(entries) + "\n")

print(f"Wrote {len(entries)} demo log entries to {LOG}")
