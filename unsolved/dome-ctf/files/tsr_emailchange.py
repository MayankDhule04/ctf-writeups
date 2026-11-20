import urllib.request, urllib.error, ssl, json, time, base64

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
def jwtemail(t):
    try: return json.loads(base64.urlsafe_b64decode(t.split('.')[1]+'==')).get('email')
    except: return '?'

s,o=req("POST","/auth/v1/signup",{"email":f"t{int(time.time())}@proton.me","password":"L@ntern2026!"})
tok=json.loads(o).get("access_token"); print("signup email in jwt:", jwtemail(tok))

print("\n[A] change email to UNREGISTERED random:")
s,o=req("PUT","/auth/v1/user",{"email":f"rand{int(time.time())}@proton.me"},token=tok); print("  ->",s,o[:260])
s,o=req("GET","/auth/v1/user",token=tok); 
try: print("  current email now:", json.loads(o).get("email"), "| new_email:", json.loads(o).get("new_email"))
except: print("  ",o[:200])

print("\n[B] change email to WHITELISTED d.vitali@reply.it:")
s,o=req("PUT","/auth/v1/user",{"email":"d.vitali@reply.it"},token=tok); print("  ->",s,o[:260])
