import requests
import hashlib
import hmac
import time
import json
import sys

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

with open("output.txt", "w", encoding="utf-8") as f:
    def log(msg):
        print(msg)
        f.write(msg + "\n")
        f.flush()

    log("=== STEP 1: Reconnaissance ===")

    r = requests.get(BASE_URL, timeout=15)
    log(f"\n--- Main page HTML (status {r.status_code}) ---")
    log(r.text)
    log(f"\n--- Response Headers ---")
    for k, v in r.headers.items():
        log(f"  {k}: {v}")

    r = requests.get(f"{BASE_URL}/api/hint", timeout=15)
    log(f"\n--- /api/hint (status {r.status_code}) ---")
    log(r.text)

    r = requests.get(f"{BASE_URL}/api/secret", timeout=15)
    log(f"\n--- /api/secret GET (status {r.status_code}) ---")
    log(r.text)

    r = requests.get(f"{BASE_URL}/api/admin", timeout=15)
    log(f"\n--- /api/admin GET (status {r.status_code}) ---")
    log(r.text)

    r = requests.post(f"{BASE_URL}/api/confess", json={"message": "I love you"}, timeout=15)
    log(f"\n--- /api/confess POST json (status {r.status_code}) ---")
    log(r.text)

    r = requests.get(f"{BASE_URL}/api/confess", timeout=15)
    log(f"\n--- /api/confess GET (status {r.status_code}) ---")
    log(r.text)

    # Try common endpoints
    for path in ["/api/validate", "/api/auth", "/api/login", "/api/time", "/api/token", 
                 "/api/verify", "/api/headers", "/api/help", "/api/status", "/api/health",
                 "/api/config", "/api/info", "/api/docs", "/api/swagger"]:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=10)
            if r.status_code != 404:
                log(f"\n--- {path} GET (status {r.status_code}) ---")
                log(r.text[:500])
        except Exception as e:
            pass

    log("\n\n=== STEP 2: Header-Based Auth ===")
    timestamp = str(int(time.time()))
    log(f"Current timestamp: {timestamp}")

    # Try all header combinations on /api/secret
    for time_header in ["X-Time", "X-Timestamp", "X-Auth-Time", "Time", "X-Request-Time", "X-Date"]:
        headers_attempt = {time_header: timestamp}
        r = requests.get(f"{BASE_URL}/api/secret", headers=headers_attempt, timeout=10)
        log(f"  /api/secret with {time_header}: {r.status_code} -> {r.text[:200]}")

    # Try POST confess with headers
    for time_header in ["X-Time", "X-Timestamp", "X-Auth-Time", "Time"]:
        headers_attempt = {time_header: timestamp}
        r = requests.post(f"{BASE_URL}/api/confess", headers=headers_attempt, json={"message":"I love you"}, timeout=10)
        log(f"  POST /api/confess with {time_header}: {r.status_code} -> {r.text[:300]}")

    # Try admin with headers
    for time_header in ["X-Time", "X-Timestamp", "X-Auth-Time", "Time"]:
        headers_attempt = {time_header: timestamp}
        r = requests.get(f"{BASE_URL}/api/admin", headers=headers_attempt, timeout=10)
        log(f"  /api/admin with {time_header}: {r.status_code} -> {r.text[:300]}")

    log("\n\n=== STEP 3: /api/flag analysis ===")
    r = requests.get(f"{BASE_URL}/api/flag", timeout=15)
    log(f"/api/flag status: {r.status_code}")
    log(f"Response headers:")
    for k, v in r.headers.items():
        log(f"  {k}: {v}")
    flag_json = r.json()
    log(f"Keys: {list(flag_json.keys())}")
    flag_value = flag_json.get("flag", "")
    log(f"Flag length: {len(flag_value)}")

    # Try POST to /api/flag
    r = requests.post(f"{BASE_URL}/api/flag", json={"auth": True}, timeout=10)
    log(f"\nPOST /api/flag: {r.status_code} -> {r.text[:500]}")

    log("\n\n=== STEP 4: Full header auth attempt ===")
    # Based on hints:
    # Header 1: X-Time = unix timestamp
    # Header 2: X-Token = md5(md5(md5(md5(timestamp + salt1) + salt2) + salt3) + salt4) x5 rounds
    # Header 3: X-Proof = hash(identity + time + salt) 
    # Header 4: X-Signature = hash(time + token + proof)
    
    # Try different salt values - "love", "simple", "pagal", "hai"
    salts = ["love", "simple", "pagal", "hai"]
    
    def multi_hash(data, rounds=5):
        result = data
        for _ in range(rounds):
            result = hashlib.md5(result.encode()).hexdigest()
        return result
    
    # Token: four layers deep (4 nested hashes), four salts wide (using 4 salts), five rounds
    token_base = timestamp
    for salt in salts:
        token_base = hashlib.md5((token_base + salt).encode()).hexdigest()
    # Apply 5 rounds
    token = token_base
    for _ in range(5):
        token = hashlib.md5(token.encode()).hexdigest()
    
    # Proof: identity + time + salt
    proof = hashlib.md5(("admin" + timestamp + "love").encode()).hexdigest()
    
    # Signature: binds all three
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    
    headers_full = {
        "X-Time": timestamp,
        "X-Token": token,
        "X-Proof": proof,
        "X-Signature": signature
    }
    
    log(f"Headers: {json.dumps(headers_full, indent=2)}")
    
    for endpoint in ["/api/secret", "/api/admin", "/api/confess", "/api/flag"]:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=headers_full, timeout=10)
        log(f"\nGET {endpoint} with full headers: {r.status_code}")
        log(r.text[:500])
        
        if endpoint == "/api/confess":
            r = requests.post(f"{BASE_URL}{endpoint}", headers=headers_full, json={"message": "I love you"}, timeout=10)
            log(f"POST {endpoint} with full headers: {r.status_code}")
            log(r.text[:500])

    log("\nDone!")
