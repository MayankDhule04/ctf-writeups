import urllib.request, ssl, json, http.cookiejar, time

base = "https://lantern.hackthe.website"
ctx = ssl.create_default_context()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))

def get(path, extra=None):
    h = {"User-Agent": "Mozilla/5.0"}
    if extra: h.update(extra)
    r = opener.open(urllib.request.Request(base+path, headers=h), timeout=15)
    return r.status, r.read(8000).decode("utf-8","replace")

def post(path, body, csrf, extra=None):
    data = json.dumps(body).encode()
    h = {"User-Agent":"Mozilla/5.0","Content-Type":"application/json","X-CSRF-Token":csrf}
    if extra: h.update(extra)
    req = urllib.request.Request(base+path, data=data, method="POST", headers=h)
    try:
        r = opener.open(req, timeout=15)
        return r.status, r.read(4000).decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000).decode("utf-8","replace")

# Fresh session
s, o = get("/api/auth/csrf-token")
csrf = json.loads(o).get("token","")
print("CSRF:", csrf[:20], "...")

# Register
ts = int(time.time())
s, o = post("/api/auth/register", {"username":f"hunter{ts}","email":f"h{ts}@test.com","password":"Solve2026!"}, csrf)
print(f"register: {s} {o[:300]}")

if s == 200 or s == 201:
    # Try login with new account
    s, o = post("/api/auth/login", {"username":f"hunter{ts}","password":"Solve2026!"}, csrf)
    print(f"login: {s} {o[:300]}")

    # Check session
    try:
        s, o = get("/api/auth/session")
        print(f"session: {s} {o[:300]}")
    except Exception as e:
        print(f"session: ERR")

    # Try restricted pages as logged-in user
    for p in ["/c/underground", "/data/", "/internal/mod-logs/", "/c/announcements"]:
        try:
            s, o = get(p)
            print(f"{p}: {s} {o[:200]}")
        except Exception as e:
            print(f"{p}: ERR {e}")
