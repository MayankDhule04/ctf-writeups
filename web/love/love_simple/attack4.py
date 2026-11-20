import requests
import hashlib
import hmac
import time
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# Let's try a completely different approach:
# Maybe the site checks if time is EXACTLY 2pm IST
# And the token generation follows very specific rules

# Let's first check the error messages more carefully with the CORRECT header names
ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist)
today_2pm_ist = now_ist.replace(hour=14, minute=0, second=0, microsecond=0)
timestamp_2pm = str(int(today_2pm_ist.timestamp()))
timestamp_now = str(int(time.time()))

print(f"Current IST time: {now_ist}")
print(f"2pm IST timestamp: {timestamp_2pm}")
print(f"Current timestamp: {timestamp_now}")

# Test 1: Different error for different endpoints with progressive headers
print("\n=== Test: Progressive header analysis ===")

combos = [
    ({}, "No headers"),
    ({"x-love-time": timestamp_2pm}, "x-love-time only (2pm)"),
    ({"x-love-time": timestamp_now}, "x-love-time only (now)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a"}, "time+token (2pm)"),
    ({"x-love-time": timestamp_now, "x-love-token": "a"}, "time+token (now)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a", "x-love-proof": "b"}, "time+token+proof (2pm)"),
    ({"x-love-time": timestamp_2pm, "x-love-token": "a", "x-love-proof": "b", "x-love-signature": "c"}, "all 4 (2pm)"),
]

for hdrs, desc in combos:
    r = requests.post(f"{BASE_URL}/api/confess", headers=hdrs, json={"message": "I love you"}, timeout=10)
    print(f"  {desc}: {r.status_code} -> {r.text.strip()}")

# Test 2: Maybe it's not /api/confess but another endpoint that needs these headers?
print("\n=== Test: Trying headers on /api/secret ===")
for hdrs, desc in combos:
    r = requests.get(f"{BASE_URL}/api/secret", headers=hdrs, timeout=10)
    print(f"  {desc}: {r.status_code} -> {r.text.strip()}")

print("\n=== Test: Trying headers on /api/admin ===")
for hdrs, desc in combos:
    r = requests.get(f"{BASE_URL}/api/admin", headers=hdrs, timeout=10)
    print(f"  {desc}: {r.status_code} -> {r.text.strip()}")

# Test 3: Maybe the 2pm needs to be exactly right - different time formats
print("\n=== Test: Different time formats ===")
time_formats = [
    timestamp_2pm,  # unix timestamp
    "14:00",  # time
    "2:00 PM",  # 12h format
    "14:00:00",  # full time
    str(today_2pm_ist),  # ISO format
    today_2pm_ist.isoformat(),  # ISO format
    "2pm",  # simple
    "1400",  # military
    str(int(today_2pm_ist.timestamp() * 1000)),  # millisecond timestamp
]

for tf in time_formats:
    hdrs = {"x-love-time": tf, "x-love-token": "a", "x-love-proof": "b", "x-love-signature": "c"}
    r = requests.post(f"{BASE_URL}/api/confess", headers=hdrs, json={"message": "I love you"}, timeout=10)
    print(f"  time='{tf}': {r.status_code} -> {r.text.strip()}")

# Test 4: Maybe these are NOT custom headers but something else entirely
# Maybe I need to check source code more carefully
print("\n=== Test: Checking if JS fetches more content ===")
for path in ["/static/js/app.js", "/static/js/main.js", "/js/app.js", "/script.js",
             "/app.js", "/main.js", "/confess.js", "/love.js", "/api/config",
             "/api/requirements", "/api/docs", "/api/spec", "/api/openapi",
             "/api/swagger.json", "/api/schema", "/api/version"]:
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=5)
        if r.status_code != 404:
            print(f"  {path}: {r.status_code} -> {r.text[:300]}")
    except:
        pass

# Test 5: Try PUT, PATCH, DELETE on /api/confess
for method in ["PUT", "PATCH", "DELETE", "OPTIONS"]:
    r = requests.request(method, f"{BASE_URL}/api/confess", timeout=10,
                         headers={"x-love-time": timestamp_2pm, "x-love-token": "a", 
                                  "x-love-proof": "b", "x-love-signature": "c"})
    print(f"\n{method} /api/confess: {r.status_code} -> {r.text[:300]}")
    if method == "OPTIONS":
        print(f"  Headers: {dict(r.headers)}")
