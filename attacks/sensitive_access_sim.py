from pathlib import Path
from datetime import datetime

LOG = Path("data/logs/telecom.log")
attacker = "192.0.2.55"
LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a") as f:
    f.write(f"{datetime.utcnow().isoformat()}Z ALERT SENSITIVE_ACCESS src={attacker} file=/etc/passwd\n")
print("Sensitive file access simulation complete for", attacker)
