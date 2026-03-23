from pathlib import Path
from datetime import datetime

LOG = Path("data/logs/telecom.log")
attacker = "198.51.100.77"
ports = ",".join(str(p) for p in range(20, 37))
LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a") as f:
    f.write(f"{datetime.utcnow().isoformat()}Z WARN PORT_SCAN src={attacker} ports={ports}\n")
print("Port scan simulation complete for", attacker)
