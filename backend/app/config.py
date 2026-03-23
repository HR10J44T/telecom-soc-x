from pathlib import Path
from pydantic import BaseModel
import os

class Settings(BaseModel):
    log_path: Path = Path(os.getenv("TELECOM_SOC_LOG_PATH", "./data/logs/telecom.log"))
    state_path: Path = Path(os.getenv("TELECOM_SOC_STATE_PATH", "./data/state"))
    auto_block: bool = os.getenv("TELECOM_SOC_AUTO_BLOCK", "false").lower() == "true"

settings = Settings()
settings.state_path.mkdir(parents=True, exist_ok=True)
settings.log_path.parent.mkdir(parents=True, exist_ok=True)
