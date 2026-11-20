import requests
import hashlib
import hmac
import time
import json
import calendar
from datetime import datetime, timezone, timedelta

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# From HTML source:
# Required headers: x-love-time, x-love-token, x-love-proof, x-love-signature
# Endpoint: POST /api/confess
# Time hint: 2pm IST (from meta keywords: love,time,moment,heart,2pm,IST,confess)

# From Hint 3:
# 1. Time – the foundation of all truth -> x-love-time = unix timestamp
# 2. Token – four layers deep, four salts wide, five rounds of fire
#    -> 4 layers of hashing, 4 different salts, 5 rounds each or 5 total rounds
# 3. Proof – your identity woven with time and salt
# 4. Signature – the seal that binds all three (time + token + proof)

# The salts could be: love, simple, pagal, hai (from challenge name/URL)
# Or they could be: love, time, moment, heart (from meta keywords)

# Time: 2pm IST = 14:00 IST = 08:30 UTC
# Let's use today's 2pm IST as the timestamp
ist = timezone(timedelta(hours=5, minutes=30))
today_2pm_ist = datetime.now(ist).replace(hour=14, minute=0, second=0, microsecond=0)
timestamp_2pm = str(int(today_2pm_ist.timestamp()))

# Also try current time
timestamp_now = str(int(time.time()))

print(f"2pm IST timestamp: {timestamp_2pm}")
print(f"Current timestamp: {timestamp_now}")
print(f"2pm IST datetime: {today_2pm_ist}")

def try_auth(timestamp, salts, identity, hash_func, label=""):
    """Try different authentication strategies"""
    print(f"\n{'='*60}")
    print(f"Attempt: {label}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Salts: {salts}")
    print(f"  Identity: {identity}")
    print(f"  Hash: {hash_func.__name__ if hasattr(hash_func, '__name__') else hash_func}")
    
    # Strategy 1: Token = hash(hash(hash(hash(time+salt1)+salt2)+salt3)+salt4)
    # "four layers deep, four salts wide"
    token = timestamp
    for salt in salts:
        token = hashlib.md5((token + salt).encode()).hexdigest()
    
    # "five rounds of fire" - apply 5 more rounds?
    for _ in range(5):
        token = hashlib.md5(token.encode()).hexdigest()
    
    # Proof: identity + time + salt  
    proof = hashlib.md5((identity + timestamp + salts[0]).encode()).hexdigest()
    
    # Signature: binds all three
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    
    headers = {
        "x-love-time": timestamp,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=15)
    print(f"  Result: {r.status_code} -> {r.text[:500]}")
    
    if r.status_code == 200:
        print(f"\n!!! SUCCESS !!!")
        return True
    return False

def try_auth_v2(timestamp, salts, identity, label=""):
    """Token: each round uses all 4 salts"""
    print(f"\n{'='*60}")
    print(f"Attempt v2: {label}")
    
    # Token: 5 rounds, each round hashes with all 4 salts
    token = timestamp
    for round_num in range(5):
        for salt in salts:
            token = hashlib.md5((token + salt).encode()).hexdigest()
    
    # Proof
    proof = hashlib.md5((identity + timestamp + salts[0]).encode()).hexdigest()
    
    # Signature
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    
    headers = {
        "x-love-time": timestamp,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=15)
    print(f"  Result: {r.status_code} -> {r.text[:500]}")
    if r.status_code == 200:
        print(f"\n!!! SUCCESS !!!")
        return True
    return False

def try_auth_v3(timestamp, salts, identity, label=""):
    """Token: 4 layers with salts, each layer has 5 rounds"""
    print(f"\n{'='*60}")
    print(f"Attempt v3: {label}")
    
    token = timestamp
    for salt in salts:  # 4 layers
        temp = token + salt
        for _ in range(5):  # 5 rounds per layer
            temp = hashlib.md5(temp.encode()).hexdigest()
        token = temp
    
    proof = hashlib.md5((identity + timestamp + salts[0]).encode()).hexdigest()
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    
    headers = {
        "x-love-time": timestamp,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=15)
    print(f"  Result: {r.status_code} -> {r.text[:500]}")
    if r.status_code == 200:
        print(f"\n!!! SUCCESS !!!")
        return True
    return False

def try_auth_sha256(timestamp, salts, identity, label=""):
    """Same but with SHA-256"""
    print(f"\n{'='*60}")
    print(f"Attempt sha256: {label}")
    
    # Token: 4 layers with 4 salts, then 5 rounds
    token = timestamp
    for salt in salts:
        token = hashlib.sha256((token + salt).encode()).hexdigest()
    for _ in range(5):
        token = hashlib.sha256(token.encode()).hexdigest()
    
    proof = hashlib.sha256((identity + timestamp + salts[0]).encode()).hexdigest()
    signature = hashlib.sha256((timestamp + token + proof).encode()).hexdigest()
    
    headers = {
        "x-love-time": timestamp,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=15)
    print(f"  Result: {r.status_code} -> {r.text[:500]}")
    if r.status_code == 200:
        print(f"\n!!! SUCCESS !!!")
        return True
    return False

def try_auth_hmac(timestamp, salts, identity, label=""):
    """HMAC-based approach"""
    print(f"\n{'='*60}")
    print(f"Attempt hmac: {label}")
    
    # Token: 4 layers deep with HMAC
    token = timestamp
    for salt in salts:
        token = hmac.new(salt.encode(), token.encode(), hashlib.md5).hexdigest()
    for _ in range(5):
        token = hashlib.md5(token.encode()).hexdigest()
    
    # Proof: HMAC(identity, time+salt)
    proof = hmac.new(salts[0].encode(), (identity + timestamp).encode(), hashlib.md5).hexdigest()
    
    # Signature: HMAC based on all three
    signature = hmac.new((timestamp + token + proof).encode(), b"", hashlib.md5).hexdigest()
    
    headers = {
        "x-love-time": timestamp,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=15)
    print(f"  Result: {r.status_code} -> {r.text[:500]}")
    if r.status_code == 200:
        print(f"\n!!! SUCCESS !!!")
        return True
    return False

# Try different salt combinations
salt_options = [
    ["love", "simple", "pagal", "hai"],
    ["love", "time", "moment", "heart"],
    ["love", "pagal", "hai", "simple"],
    ["l0ve", "s1mple", "p4gal", "h41"],
    ["LOVE", "SIMPLE", "PAGAL", "HAI"],
    ["Love", "Simple", "Pagal", "Hai"],
    ["love", "is", "simple", "ctf"],
    ["trace", "ctf", "love", "simple"],
]

identity_options = ["love", "admin", "user", "lover", "confess", "pagal"]

# First, try to get more info - maybe the error messages differ with correct headers
print("=== Quick test: does /api/confess give different errors? ===")
for header_name in ["x-love-time", "X-Love-Time", "x-love-timestamp"]:
    headers = {header_name: timestamp_2pm}
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=10)
    print(f"  POST /api/confess with {header_name}={timestamp_2pm}: {r.status_code} -> {r.text}")

# Try just the time header with current time  
headers = {"x-love-time": timestamp_now}
r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=10)
print(f"\n  With current time: {r.status_code} -> {r.text}")

# Try with all 4 headers but dummy values to see which error we get
headers = {
    "x-love-time": timestamp_2pm,
    "x-love-token": "dummy",
    "x-love-proof": "dummy",
    "x-love-signature": "dummy"
}
r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=10)
print(f"\n  With all 4 headers (dummy): {r.status_code} -> {r.text}")

headers = {
    "x-love-time": timestamp_now,
    "x-love-token": "dummy",
    "x-love-proof": "dummy",
    "x-love-signature": "dummy"
}
r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=10)
print(f"\n  With all 4 headers (current time, dummy): {r.status_code} -> {r.text}")

# Now brute force combinations
for ts_label, ts in [("2pm_ist", timestamp_2pm), ("now", timestamp_now)]:
    for salts in salt_options:
        for identity in identity_options[:3]:  # limit to first 3
            label = f"ts={ts_label}, salts={salts}, id={identity}"
            if try_auth(ts, salts, identity, hashlib.md5, label):
                exit()
            if try_auth_v2(ts, salts, identity, f"v2 {label}"):
                exit()
            if try_auth_v3(ts, salts, identity, f"v3 {label}"):
                exit()

print("\n\nBasic attempts failed. Trying SHA-256 and HMAC...")
for ts_label, ts in [("2pm_ist", timestamp_2pm), ("now", timestamp_now)]:
    for salts in salt_options[:4]:
        for identity in identity_options[:3]:
            label = f"ts={ts_label}, salts={salts}, id={identity}"
            if try_auth_sha256(ts, salts, identity, f"sha256 {label}"):
                exit()
            if try_auth_hmac(ts, salts, identity, f"hmac {label}"):
                exit()

print("\nAll attempts exhausted.")
