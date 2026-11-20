import urllib.request, urllib.error, ssl, json, time

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def req(method, path, body=None, token=None):
    url=f"{BASE}{path}"
    data=json.dumps(body).encode() if body is not None else None
    h={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Content-Type":"application/json","Accept":"application/json"}
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=25,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

email=f"hunter_{int(time.time())}@proton.me"
s,o=req("POST","/auth/v1/signup",{"email":email,"password":"L@ntern-bypass-2026!"})
tok=json.loads(o).get("access_token") if s==200 else None
print("signup:", s, "token?", bool(tok), "email:", email)

tables=["chapters","chapter_content","chapter_access","whitelisted_emails","user_roles"]
for t in tables:
    s,o=req("GET",f"/rest/v1/{t}?select=*", token=tok)
    print(f"\n===== {t} -> {s} =====")
    print(o[:3000])
