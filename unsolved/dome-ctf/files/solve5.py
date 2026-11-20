import urllib.request, ssl, json, time

base = "https://lantern.hackthe.website"
ctx = ssl.create_default_context()
H = {"Host": "thelantern.org", "X-Forwarded-For": "127.0.0.1",
     "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

def post(path, body):
    r = urllib.request.Request(base+path, data=json.dumps(body).encode(), method="POST", headers=H)
    try:
        resp = urllib.request.urlopen(r, timeout=60, context=ctx)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return "ERR", str(e)

def get(path):
    h = dict(H); del h["Content-Type"]
    r = urllib.request.Request(base+path, headers=h)
    try:
        resp = urllib.request.urlopen(r, timeout=15, context=ctx)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# Fresh signup to avoid stale sessions
ts = int(time.time())
s, d = post("/auth/signup", {"username":f"inv{ts}","email":f"inv{ts}@proton.me","password":"Inv2026!"})
if s != 200:
    s, d = post("/auth/login", {"username":"ctfhunter","password":"Hunt2026!"})
print(f"auth: {s}")
sid = d["session_id"] if isinstance(d,dict) else ""
tok = d.get("turn_token","") if isinstance(d,dict) else ""
print(f"sid={sid[:16]}... tok={tok[:16]}...")

# Try OldCrow with a single careful message
print("\n=== OldCrow attempt ===")
msg = "I was told to find OldCrow. I have information about a compromised export worker."
s, d = post("/oldcrow/message", {"session_id":sid, "message":msg, "turn_token":tok})
print(f"status: {s}")
if isinstance(d, dict):
    print(f"response: {d.get('response','')[:600]}")
    tok = d.get("next_turn_token", tok)
    print(f"flags={d.get('flags_count')}, trusted={d.get('oldcrow_trusted')}")
    
    # If first message worked, continue the conversation
    if d.get("response"):
        msgs = [
            "The export sink at kv/data/export/9f34f9 was phoning home for 94 days. The fallback was pointed at a share link.",
            "I traced the handle vyrqelith through the phone forensics. The board handle matches.",
            "I need access to the archived threads. What was in post #481?",
        ]
        for m in msgs:
            time.sleep(2)
            s2, d2 = post("/oldcrow/message", {"session_id":sid, "message":m, "turn_token":tok})
            print(f"\n[{m[:50]}] -> {s2}")
            if isinstance(d2, dict):
                print(f"  OC: {d2.get('response','')[:400]}")
                tok = d2.get("next_turn_token", tok)
                print(f"  flags={d2.get('flags_count')}, trusted={d2.get('oldcrow_trusted')}")
                if "dome.ctf" in str(d2):
                    print(f"\n*** FLAG IN RESPONSE ***")
                    print(json.dumps(d2, indent=2))
            else:
                print(f"  {str(d2)[:200]}")
                break
else:
    print(f"error: {str(d)[:300]}")
    
# Check session state
print("\n=== Final session state ===")
s, o = get(f"/session/history/{sid}")
print(f"{s} {str(o)[:600]}")
