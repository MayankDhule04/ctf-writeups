import requests
import hashlib
import hmac
import time
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist)
today_2pm_ist = now_ist.replace(hour=14, minute=0, second=0, microsecond=0)
timestamp_2pm = str(int(today_2pm_ist.timestamp()))
timestamp_now = str(int(time.time()))

results = []

def log(msg):
    results.append(msg)
    print(msg)

log(f"Current IST time: {now_ist}")
log(f"2pm IST timestamp: {timestamp_2pm}")

# Progressive header analysis
log("\n=== Progressive header analysis on /api/confess (POST) ===")
combos = [
    ({}, "No headers"),
    ({"x-love-time": timestamp_2pm}, "time only (2pm)"),
    ({"x-love-time": timestamp_now}, "time only (now)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a"}, "time+token (2pm)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a", "x-love-proof": "b"}, "time+token+proof (2pm)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a", "x-love-proof": "b", "x-love-signature": "c"}, "all 4 (2pm, dummy)"),
    ({"x-love-time": timestamp_now, "x-love-token": "a", "x-love-proof": "b", "x-love-signature": "c"}, "all 4 (now, dummy)"),
]

for hdrs, desc in combos:
    r = requests.post(f"{BASE_URL}/api/confess", headers=hdrs, json={"message": "I love you"}, timeout=10)
    log(f"  {desc}: {r.status_code} -> {r.text.strip()}")

log("\n=== Progressive header analysis on /api/admin (GET) ===")
for hdrs, desc in combos:
    r = requests.get(f"{BASE_URL}/api/admin", headers=hdrs, timeout=10)
    log(f"  {desc}: {r.status_code} -> {r.text.strip()}")

log("\n=== Progressive header analysis on /api/secret (GET) ===")
for hdrs, desc in combos:
    r = requests.get(f"{BASE_URL}/api/secret", headers=hdrs, timeout=10)
    log(f"  {desc}: {r.status_code} -> {r.text.strip()}")

# OPTIONS check
r = requests.options(f"{BASE_URL}/api/confess", timeout=10)
log(f"\nOPTIONS /api/confess: {r.status_code}")
for k, v in r.headers.items():
    log(f"  {k}: {v}")
log(f"  Body: {r.text}")

# Check API paths
log("\n=== Checking other paths ===")
for path in ["/api/status", "/api/config", "/api/version", "/api/docs", "/api/health",
             "/api/validate", "/api/requirements"]:
    r = requests.get(f"{BASE_URL}{path}", timeout=5)
    if r.status_code != 404:
        log(f"  {path}: {r.status_code} -> {r.text[:500]}")

with open("output4.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

log("\nDone!")
