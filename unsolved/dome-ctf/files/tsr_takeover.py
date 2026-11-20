import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()
def req(method, path, body=None, token=None):
    r=urllib.request.Request(f"{BASE}{path}", data=(json.dumps(body).encode() if body is not None else None), method=method,
        headers={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Content-Type":"application/json","Accept":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=25,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

WL="d.vitali@reply.it"
print("signup AS whitelisted member:", WL)
s,o=req("POST","/auth/v1/signup",{"email":WL,"password":"Pwn3d-Lantern-2026!"})
print("  ->", s, o[:300])
tok=None
try: tok=json.loads(o).get("access_token")
except: pass

if not tok:
    print("  no token from signup; trying password login...")
    s,o=req("POST","/auth/v1/token?grant_type=password",{"email":WL,"password":"Pwn3d-Lantern-2026!"})
    print("  login ->", s, o[:300])
    try: tok=json.loads(o).get("access_token")
    except: pass

print("\ntoken?", bool(tok))
if tok:
    for t in ["whitelisted_emails","chapters","chapter_content","chapter_access","user_roles"]:
        s,o=req("GET",f"/rest/v1/{t}?select=*",token=tok)
        print(f"\n===== {t} -> {s} =====")
        print(o[:3000])
