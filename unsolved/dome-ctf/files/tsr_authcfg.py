import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def req(method, path, body=None, extra=None):
    url=f"{BASE}{path}"
    data=json.dumps(body).encode() if body is not None else None
    h={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json","Accept":"application/json"}
    if extra: h.update(extra)
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=25,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

print("=== GET /auth/v1/settings ===")
s,o=req("GET","/auth/v1/settings"); print(s, o[:800])

print("\n=== POST /auth/v1/signup ===")
s,o=req("POST","/auth/v1/signup",{"email":"ctfhunter_9f34@proton.me","password":"L@ntern-bypass-2026"})
print(s, o[:1200])

print("\n=== POST /auth/v1/signup (anonymous?) ===")
s,o=req("POST","/auth/v1/signup",{}); print(s, o[:400])
