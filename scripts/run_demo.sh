#!/usr/bin/env bash
set -e
python simulator/generate_logs.py
python attacks/bruteforce_sim.py
python attacks/port_scan_sim.py
python attacks/sensitive_access_sim.py
curl -s -X POST http://127.0.0.1:8000/scan
