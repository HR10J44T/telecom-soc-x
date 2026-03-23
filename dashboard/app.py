import os
import pandas as pd
import requests
import streamlit as st

API = os.getenv("TELECOM_SOC_API_BASE", "http://127.0.0.1:8000")
st.set_page_config(page_title="TelecomSOC-X", layout="wide")
st.title("💣 TelecomSOC-X — Real-Time Telecom SOC")
st.caption("Mini Airtel-style SIEM + Auto Response demo")

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Run Detection Scan"):
        r = requests.post(f"{API}/scan", timeout=30)
        st.success(r.json())
with col2:
    st.write("API:", API)

summary = requests.get(f"{API}/summary", timeout=30).json()
alerts = requests.get(f"{API}/alerts", timeout=30).json()
incidents = requests.get(f"{API}/incidents", timeout=30).json()
blocked = requests.get(f"{API}/blocked", timeout=30).json()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Alerts", summary["alerts_total"])
c2.metric("Incidents", summary["incidents_total"])
c3.metric("Blocked IPs", summary["blocked_total"])
c4.metric("Critical Alerts", summary["severity"]["critical"])

st.subheader("Severity Overview")
st.bar_chart(pd.DataFrame([summary["severity"]]).T.rename(columns={0:"count"}))

st.subheader("Top Attacking IPs")
if summary["top_ips"]:
    st.dataframe(pd.DataFrame(summary["top_ips"]), use_container_width=True)
else:
    st.info("No attackers detected yet. Run the demo generators first.")

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Alerts")
    st.dataframe(pd.DataFrame(alerts), use_container_width=True)
with right:
    st.subheader("Blocked IP Registry")
    st.dataframe(pd.DataFrame(blocked), use_container_width=True)

st.subheader("Incident Board")
if incidents:
    df = pd.DataFrame(incidents)[["id","title","source_ip","severity","status","signals","duration_minutes"]]
    st.dataframe(df, use_container_width=True)
else:
    st.info("No incidents yet.")
