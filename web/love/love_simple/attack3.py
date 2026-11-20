import requests
import hashlib
import hmac
import time
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# From HTML: Required: x-love-time, x-love-token, x-love-proof, x-love-signature
# Meta keywords: love,time,moment,heart,2pm,IST,confess

ist = timezone(timedelta(hours=5, minutes=30))
today_2pm_ist = datetime.now(ist).replace(hour=14, minute=0, second=0, microsecond=0)
timestamp_2pm = str(int(today_2pm_ist.timestamp()))
timestamp_now = str(int(time.time()))

print(f"2pm IST today: {timestamp_2pm}")
print(f"Now: {timestamp_now}")

# Step 1: Check what error messages we get with progressive headers
print("\n=== Error message analysis ===")

# No headers
r = requests.post(f"{BASE_URL}/api/confess", json={"message": "I love you"}, timeout=10)
print(f"No headers: {r.status_code} -> {r.text}")

# Only x-love-time
r = requests.post(f"{BASE_URL}/api/confess", 
    headers={"x-love-time": timestamp_now}, 
    json={"message": "I love you"}, timeout=10)
print(f"Only x-love-time (now): {r.status_code} -> {r.text}")

r = requests.post(f"{BASE_URL}/api/confess", 
    headers={"x-love-time": timestamp_2pm}, 
    json={"message": "I love you"}, timeout=10)
print(f"Only x-love-time (2pm): {r.status_code} -> {r.text}")

# x-love-time + x-love-token
r = requests.post(f"{BASE_URL}/api/confess", 
    headers={"x-love-time": timestamp_2pm, "x-love-token": "test"}, 
    json={"message": "I love you"}, timeout=10)
print(f"time+token (2pm, dummy): {r.status_code} -> {r.text}")

# All 4 with dummy
r = requests.post(f"{BASE_URL}/api/confess", 
    headers={
        "x-love-time": timestamp_2pm, 
        "x-love-token": "test",
        "x-love-proof": "test", 
        "x-love-signature": "test"
    }, 
    json={"message": "I love you"}, timeout=10)
print(f"All 4 (2pm, dummy): {r.status_code} -> {r.text}")

# All 4 with dummy but NOW time
r = requests.post(f"{BASE_URL}/api/confess", 
    headers={
        "x-love-time": timestamp_now, 
        "x-love-token": "test",
        "x-love-proof": "test", 
        "x-love-signature": "test"
    }, 
    json={"message": "I love you"}, timeout=10)
print(f"All 4 (now, dummy): {r.status_code} -> {r.text}")

# Try different error messages - maybe integer vs string timestamp matters
r = requests.post(f"{BASE_URL}/api/confess", 
    headers={
        "x-love-time": "1774513800",  # 2pm IST
        "x-love-token": hashlib.md5(b"test").hexdigest(),
        "x-love-proof": hashlib.md5(b"test").hexdigest(), 
        "x-love-signature": hashlib.md5(b"test").hexdigest()
    }, 
    json={"message": "I love you"}, timeout=10)
print(f"All 4 (2pm, md5): {r.status_code} -> {r.text}")

print("\n=== Now trying the actual solve ===")

# Hint 3 interpretation:  
# "Four headers guard the gate, each built upon the last"
# 1. Time - unix timestamp (the foundation)
# 2. Token - "four layers deep, four salts wide, five rounds of fire"
#    = md5 hash, 4 layers of nesting with 4 salts, iterated 5 times
# 3. Proof - "your identity woven with time and salt"  
#    = md5(identity + time + salt)
# 4. Signature - "the seal that binds all three"
#    = md5(time + token + proof)

# The salts are likely: love, pagal, hai, simple (from URL) 
# OR love, time, moment, heart (from meta keywords)

def solve(timestamp, salts, identity):
    # TIME
    x_time = timestamp
    
    # TOKEN: "four layers deep, four salts wide, five rounds of fire"
    # Interpretation: start with time, hash it with salt[0], then hash result with salt[1], etc. (4 layers, 4 salts)
    # Then do this process 5 times (5 rounds)
    
    # Version A: 4 layers = 4 hashes with 4 salts, repeated 5 rounds
    token = x_time
    for round_i in range(5):  # five rounds
        for salt in salts:  # four salts
            token = hashlib.md5((token + salt).encode()).hexdigest()
    
    # PROOF: "your identity woven with time and salt"
    proof = hashlib.md5((identity + x_time + salts[0]).encode()).hexdigest()
    
    # SIGNATURE: "the seal that binds all three"  
    signature = hashlib.md5((x_time + token + proof).encode()).hexdigest()
    
    return x_time, token, proof, signature

def solve_b(timestamp, salts, identity):
    # TOKEN version B: 4 salts concatenated, hashed 5 times
    token = timestamp + "".join(salts)
    for _ in range(5):
        token = hashlib.md5(token.encode()).hexdigest()
    
    proof = hashlib.md5((identity + timestamp + salts[0]).encode()).hexdigest()
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    return timestamp, token, proof, signature

def solve_c(timestamp, salts, identity):
    # TOKEN version C: hash(time), then hash with each salt = 4 layers, done 5 times
    token = hashlib.md5(timestamp.encode()).hexdigest()
    for _ in range(5):
        for salt in salts:
            token = hashlib.md5((token + salt).encode()).hexdigest()
    
    proof = hashlib.md5((identity + timestamp + salts[0]).encode()).hexdigest()
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    return timestamp, token, proof, signature

def solve_d(timestamp, salts, identity):
    # SHA256 instead of MD5
    token = timestamp
    for _ in range(5):
        for salt in salts:
            token = hashlib.sha256((token + salt).encode()).hexdigest()
    
    proof = hashlib.sha256((identity + timestamp + salts[0]).encode()).hexdigest()
    signature = hashlib.sha256((timestamp + token + proof).encode()).hexdigest()
    return timestamp, token, proof, signature

def solve_e(timestamp, salts, identity):
    # "four layers deep" = 4 hash layers, each with different salt
    # "five rounds of fire" = each layer is hashed 5 times
    token = timestamp
    for i, salt in enumerate(salts):  # 4 layers, 4 salts
        for _ in range(5):  # 5 rounds per layer
            token = hashlib.md5((token + salt).encode()).hexdigest()
    
    # Proof: identity + time + all salts combined?
    proof = hashlib.md5((identity + timestamp + "".join(salts)).encode()).hexdigest()
    signature = hashlib.md5((timestamp + token + proof).encode()).hexdigest()
    return timestamp, token, proof, signature

def solve_f(timestamp, salts, identity):
    # HMAC approach - "seal" suggests HMAC
    token = timestamp
    for salt in salts:
        token = hmac.new(salt.encode(), token.encode(), hashlib.md5).hexdigest()
    for _ in range(5):
        token = hashlib.md5(token.encode()).hexdigest()
    
    proof = hmac.new(salts[0].encode(), (identity + timestamp).encode(), hashlib.md5).hexdigest()
    signature = hmac.new(token.encode(), (timestamp + proof).encode(), hashlib.md5).hexdigest()
    return timestamp, token, proof, signature

def solve_g(timestamp, salts, identity):
    # "four layers deep, four salts wide" = different in each layer
    # Maybe: md5(md5(md5(md5(time) + salt0) + salt1) + salt2) + salt3) 5 times
    token = timestamp
    for _ in range(5):
        h = hashlib.md5(token.encode()).hexdigest()
        for salt in salts:
            h = hashlib.md5((h + salt).encode()).hexdigest()
        token = h
    
    proof = hashlib.md5((identity + ":" + timestamp + ":" + salts[0]).encode()).hexdigest()
    signature = hashlib.md5((timestamp + ":" + token + ":" + proof).encode()).hexdigest()
    return timestamp, token, proof, signature

salt_combos = [
    ["love", "simple", "pagal", "hai"],
    ["love", "time", "moment", "heart"],
    ["pagal", "hai", "love", "simple"],
    ["love", "pagal", "hai", "iii"],
    ["love", "is", "simple", "ctf"],
    ["TRACECTF", "love", "simple", "pagal"],
]

identities = ["love", "admin", "user", "lover", "confess", "pagal", "heart"]

solvers = [
    ("A", solve), ("B", solve_b), ("C", solve_c), ("D", solve_d),
    ("E", solve_e), ("F", solve_f), ("G", solve_g)
]

timestamps = [timestamp_2pm, timestamp_now]

count = 0
for ts in timestamps:
    for salt_combo in salt_combos:
        for identity in identities:
            for solver_name, solver_func in solvers:
                x_time, token, proof, signature = solver_func(ts, salt_combo, identity)
                headers = {
                    "x-love-time": x_time,
                    "x-love-token": token,
                    "x-love-proof": proof,
                    "x-love-signature": signature
                }
                try:
                    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, 
                                     json={"message": "I love you"}, timeout=10)
                    count += 1
                    if r.status_code != 403:
                        print(f"\n!!! DIFFERENT STATUS: {r.status_code}")
                        print(f"  Solver: {solver_name}, ts={ts}, salts={salt_combo}, id={identity}")
                        print(f"  Response: {r.text}")
                        if r.status_code == 200:
                            print("\n*** FLAG FOUND ***")
                            print(r.text)
                            exit()
                    if count % 50 == 0:
                        print(f"  Tried {count} combinations...")
                except Exception as e:
                    print(f"Error: {e}")

print(f"\nTotal attempts: {count}")
print("No success. Need to reconsider approach.")
