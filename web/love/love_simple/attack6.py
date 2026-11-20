import requests
import hashlib
import hmac
import time
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# WHAT WE KNOW:
# - Server is Python Flask (Werkzeug/3.1.6 Python/3.11.15)
# - POST /api/confess needs 4 headers: x-love-time, x-love-token, x-love-proof, x-love-signature
# - Meta keywords hint at "2pm IST" time window
# - Hint 3 says:
#   1. Time - the foundation of all truth = timestamp
#   2. Token - four layers deep, four salts wide, five rounds of fire
#   3. Proof - your identity woven with time and salt
#   4. Signature - the seal that binds all three

# The server always returns 403 regardless - maybe we need the EXACT right headers.
# Let's think about this as a Flask/Python developer would implement it.

# Common Python pattern for this kind of CTF:
# SALTS could be ["love", "is", "simple", "!"] (from challenge name "Love Is Simple")
# or valentine/love themed
# "five rounds of fire" = 5 iterations of MD5

# Let me try the most literal interpretation:
# 1. x-love-time = current unix timestamp (must be within window around 2pm IST)
# 2. x-love-token = md5^5(timestamp + salt1 + salt2 + salt3 + salt4) 
#    OR  md5(md5(md5(md5(timestamp+s1)+s2)+s3)+s4) done 5 times
# 3. x-love-proof = md5(identity + timestamp + salt)
# 4. x-love-signature = md5(timestamp + token + proof)

ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist)

# Generate timestamps around 2pm IST
today_2pm = now_ist.replace(hour=14, minute=0, second=0, microsecond=0)
ts_2pm = int(today_2pm.timestamp())

# Try current time too
ts_now = int(time.time())

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def attempt(ts_val, salts, identity, hash_fn=md5, method="A"):
    ts = str(ts_val)
    
    if method == "A":
        # Token: hash(hash(hash(hash(ts+s1)+s2)+s3)+s4), repeat 5 times
        token = ts
        for _ in range(5):
            for s in salts:
                token = hash_fn(token + s)
    elif method == "B":
        # Token: apply 4 salts once, then hash 5 times
        token = ts
        for s in salts:
            token = hash_fn(token + s)
        for _ in range(5):
            token = hash_fn(token)
    elif method == "C":
        # Token: concatenate all salts with ts, hash 5 times
        token = ts + "".join(salts)
        for _ in range(5):
            token = hash_fn(token)
    elif method == "D":
        # Token: for each salt, hash 5 times
        token = ts
        for s in salts:
            for _ in range(5):
                token = hash_fn(token + s)
    elif method == "E":
        # Token: HMAC chain
        token = ts
        for s in salts:
            token = hmac.new(s.encode(), token.encode(), hashlib.md5).hexdigest()
        for _ in range(5):
            token = hash_fn(token)
    elif method == "F":
        # Token: hash(ts:salt1:salt2:salt3:salt4) x5
        token = ":".join([ts] + salts)
        for _ in range(5):
            token = hash_fn(token)
    elif method == "G":
        # five rounds, four layers per round with concatenated salts
        token = ts
        for _ in range(5):
            combined = token
            for s in salts:
                combined += s
            token = hash_fn(combined)
    
    # Proof variations
    if method in ["A", "B", "C", "D", "E", "G"]:
        proof = hash_fn(identity + ts + salts[0])
    elif method == "F":
        proof = hash_fn(identity + ":" + ts + ":" + salts[0])
    
    # Signature
    if method == "F":
        signature = hash_fn(ts + ":" + token + ":" + proof)
    else:
        signature = hash_fn(ts + token + proof)
    
    headers = {
        "x-love-time": ts,
        "x-love-token": token,
        "x-love-proof": proof,
        "x-love-signature": signature,
    }
    
    r = requests.post(f"{BASE_URL}/api/confess", headers=headers, json={"message": "I love you"}, timeout=10)
    return r.status_code, r.text.strip()

# Let's try many salt combos
salt_combos = [
    ["love", "is", "simple", "!"],
    ["love", "is", "simple", "."],
    ["love", "simple", "pagal", "hai"],
    ["love", "time", "moment", "heart"],
    ["love", "pagal", "hai", "simple"],
    ["L", "O", "V", "E"],
    ["l", "o", "v", "e"],
    ["love", "Love", "LOVE", "LoVe"],
    ["true", "love", "is", "simple"],
    ["trace", "ctf", "love", "simple"],
    ["salt1", "salt2", "salt3", "salt4"],
    ["s1", "s2", "s3", "s4"],
    ["1", "2", "3", "4"],
    ["the", "right", "moment", "love"],
    ["confess", "love", "heart", "time"],
    ["14", "00", "IST", "love"],
    ["2", "pm", "ist", "love"],
]

identities = ["love", "admin", "user", "lover", "confess", "pagal", "heart", "anonymous", "guest"]
methods = ["A", "B", "C", "D", "E", "F", "G"]

# Use 2pm timestamp
count = 0
found = False

# First, let's do a focused round with the most likely combos
print("=== Focused attack round ===")
for ts_val in [ts_2pm, ts_now]:
    for salts in salt_combos:
        for identity in identities:
            for method in methods:
                for hash_fn in [md5, sha256]:
                    status, text = attempt(ts_val, salts, identity, hash_fn, method)
                    count += 1
                    if status != 403:
                        print(f"\n!! STATUS {status}: method={method}, hash={'md5' if hash_fn==md5 else 'sha256'}")
                        print(f"   ts={ts_val}, salts={salts}, id={identity}")
                        print(f"   Response: {text}")
                        if status == 200:
                            print("\n*** FLAG FOUND ***")
                            found = True
                            break
                    if count % 200 == 0:
                        print(f"  Tried {count}...")
                if found: break
            if found: break
        if found: break
    if found: break

if not found:
    print(f"\nTried {count} combos. No success.")
    
    # Maybe the ENTIRE approach is wrong. Let's try:
    # 1. Checking if the /api/flag response IS the flag (just encoded weirdly)
    # 2. The flag might be hidden differently
    
    print("\n=== Analyzing /api/flag response ===")
    import base64
    
    r = requests.get(f"{BASE_URL}/api/flag", timeout=15)
    flag_data = r.json()["flag"]
    
    # Each part between || might be a base32-encoded chunk
    parts = flag_data.split("||")
    print(f"Number of parts: {len(parts)}")
    
    # Try to extract just one character from each part
    decoded_chars = []
    for i, part in enumerate(parts):
        try:
            # Pad to multiple of 8
            padded = part + "=" * ((8 - len(part) % 8) % 8)
            decoded = base64.b32decode(padded)
            decoded_chars.append(decoded)
        except Exception as e:
            decoded_chars.append(f"ERR:{e}")
    
    # Print first few
    for i, d in enumerate(decoded_chars[:20]):
        if isinstance(d, bytes):
            print(f"  Part {i}: {d.hex()} = {d}")
    
    # Try getting first byte of each
    first_bytes = []
    for d in decoded_chars:
        if isinstance(d, bytes) and len(d) > 0:
            first_bytes.append(chr(d[0]) if d[0] < 128 else '?')
    print(f"\nFirst bytes: {''.join(first_bytes)}")
    
    # Try last byte
    last_bytes = []
    for d in decoded_chars:
        if isinstance(d, bytes) and len(d) > 0:
            last_bytes.append(chr(d[-1]) if d[-1] < 128 else '?')
    print(f"Last bytes: {''.join(last_bytes)}")
    
    # Try removing || and decoding as one base32 string
    try:
        full = flag_data.replace("||", "")
        padded = full + "=" * ((8 - len(full) % 8) % 8)
        decoded_full = base64.b32decode(padded)
        print(f"\nFull decode (hex): {decoded_full[:100].hex()}")
        print(f"Full decode (text): {decoded_full[:200].decode('utf-8', errors='replace')}")
    except Exception as e:
        print(f"Full decode error: {e}")

print(f"\nTotal: {count} attempts")
