import urllib.request, urllib.error, ssl, json, time

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

# throwaway authed token
s,o=req("POST","/auth/v1/signup",{"email":f"t{int(time.time())}@proton.me","password":"L@ntern2026!"})
tok=json.loads(o).get("access_token"); print("authed:", bool(tok))

# generate a fresh code for the whitelisted member
s,o=req("POST","/functions/v1/custom-otp",{"email":"d.vitali@reply.it"}); print("custom-otp d.vitali ->", s, o[:120])

for label,tk in [("anon",None),("authed",tok)]:
    s,o=req("GET","/rest/v1/otp_codes?select=*&order=created_at.desc",token=tk)
    print(f"\notp_codes [{label}] -> {s} {o[:800]}")

# also authed reads of content/whitelist
for t in ["whitelisted_emails","chapters","chapter_content"]:
    s,o=req("GET",f"/rest/v1/{t}?select=*",token=tok)
    print(f"{t} [authed] -> {s} {o[:300]}")
