from pathlib import Path
from datetime import datetime

LOG = Path("data/logs/telecom.log")
attacker = "203.0.113.66"
user = "root"
LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a") as f:
    for _ in range(12):
        f.write(f"{datetime.utcnow().isoformat()}Z INFO FAILED_LOGIN src={attacker} user={user}\n")
print("Brute force simulation complete for", attacker)
