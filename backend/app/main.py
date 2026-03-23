from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.store import ALERTS, INCIDENTS, BLOCKED, read_json, init_state
from backend.app.services.metrics import get_dashboard_summary
from detection_engine.engine import process_log_file
from response_engine.firewall import block_ip

init_state()
app = FastAPI(title="TelecomSOC-X API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"service": "TelecomSOC-X API", "status": "ok"}

@app.post("/scan")
def scan_logs():
    return process_log_file(str(settings.log_path))

@app.get("/alerts")
def list_alerts():
    return read_json(ALERTS)

@app.get("/incidents")
def list_incidents():
    return read_json(INCIDENTS)

@app.get("/blocked")
def list_blocked():
    return read_json(BLOCKED)

@app.post("/block/{ip}")
def manual_block(ip: str):
    return block_ip(ip, "manual_block")

@app.get("/summary")
def summary():
    return get_dashboard_summary()

@app.post("/incident/{incident_id}/status/{status}")
def update_incident_status(incident_id: str, status: str):
    incidents = read_json(INCIDENTS)
    updated = False
    for inc in incidents:
        if inc["id"] == incident_id:
            inc["status"] = status
            updated = True
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    from backend.app.store import write_json
    write_json(INCIDENTS, incidents)
    return {"status": "updated", "incident_id": incident_id, "new_status": status}
