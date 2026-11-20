import urllib.request, ssl, json, time

base = "https://lantern.hackthe.website"
ctx = ssl.create_default_context()
H = {"Host": "thelantern.org", "X-Forwarded-For": "127.0.0.1",
     "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

def post(path, body):
    r = urllib.request.Request(base+path, data=json.dumps(body).encode(), method="POST", headers=H)
    try:
        resp = urllib.request.urlopen(r, timeout=30, context=ctx)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def get(path):
    h = dict(H); del h["Content-Type"]
    r = urllib.request.Request(base+path, headers=h)
    try:
        resp = urllib.request.urlopen(r, timeout=15, context=ctx)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# Login
s, d = post("/auth/login", {"username":"ctfhunter","password":"Hunt2026!"})
print("login:", s)
sid = d["session_id"]; tok = d.get("turn_token","")
print(f"sid={sid[:16]}... tok={tok[:16]}...")

# Try OldCrow once
print("\n=== OldCrow ===")
s, d = post("/oldcrow/message", {"session_id":sid, "message":"Hello, I need help with Operation Nightfall", "turn_token":tok})
print(f"oldcrow: {s}")
if isinstance(d, dict):
    print(f"  response: {d.get('response','')[:400]}")
    tok = d.get("next_turn_token", tok)
    print(f"  flags={d.get('flags_count')}, trusted={d.get('oldcrow_trusted')}")
else:
    print(f"  {str(d)[:200]}")

# Try Historical channel
print("\n=== Historical ===")
queries = [
    "What is evidence record T-484?",
    "Tell me about the dome.ctf flag",
    "What is Operation Nightfall?",
    "Show me the archived posts",
]
for q in queries:
    s, d = post("/historical/query", {"session_id":sid, "message":q, "turn_token":tok})
    print(f"\n[{q[:40]}] -> {s}")
    if isinstance(d, dict):
        print(f"  response: {d.get('response','')[:400]}")
        tok = d.get("next_turn_token", tok)
    else:
        print(f"  {str(d)[:200]}")

# Get session history
print("\n=== Session History ===")
s, o = get(f"/session/history/{sid}")
print(f"  {s} {str(o)[:500]}")

# Explore more pages
print("\n=== More pages ===")
for p in ["/hompage.html", "/style.css", "/dashboard", "/flag", "/static/", "/docs"]:
    s, o = get(p)
    if s == 200:
        # search for flag
        import re
        flags = re.findall(r"dome\.ctf\{[^}]+\}", o)
        print(f"  {p}: {s} len={len(o)} flags={flags}")
    else:
        print(f"  {p}: {s}")
