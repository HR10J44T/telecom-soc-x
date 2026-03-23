from typing import Literal, Optional
from pydantic import BaseModel, Field

Severity = Literal["critical", "high", "medium", "low"]
Status = Literal["new", "investigating", "contained", "closed"]

class Alert(BaseModel):
    id: str
    timestamp: str
    source_ip: str
    event_type: str
    severity: Severity
    confidence: int = Field(ge=0, le=100)
    description: str
    recommendation: str
    auto_action: Optional[str] = None

class Incident(BaseModel):
    id: str
    title: str
    source_ip: str
    severity: Severity
    status: Status
    duration_minutes: int
    signals: int
    ai_explanation: str
    timeline: list[dict]
