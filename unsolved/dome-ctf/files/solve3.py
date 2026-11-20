import urllib.request, ssl, json

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

# Login
s, d = post("/auth/login", {"username":"ctfhunter","password":"Hunt2026!"})
print("login:", s, json.dumps(d)[:200] if isinstance(d,dict) else d[:200])
sid = d["session_id"] if isinstance(d,dict) else ""
tok = d.get("turn_token","") if isinstance(d,dict) else ""

# Single OldCrow message
if sid:
    s, d = post("/oldcrow/message", {"session_id":sid, "message":"Hello, I am investigating. Who are you?", "turn_token":tok})
    print("\noldcrow:", s)
    if isinstance(d,dict):
        print("response:", d.get("response","")[:500])
        print("flags:", d.get("flags_count"), "trusted:", d.get("oldcrow_trusted"))
        tok = d.get("next_turn_token", tok)
    else:
        print(d[:300])
