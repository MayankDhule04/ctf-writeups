import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def call(fn, method="POST", body=None):
    url=f"{BASE}/functions/v1/{fn}"
    data=json.dumps(body).encode() if body is not None else (b"{}" if method=="POST" else None)
    h={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"}
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=20,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

names=["lantern","lanterns","the-lantern","lantern-otp","lantern-auth","lantern-login",
       "signal","chapters","get-chapters","get-content","content","chapter-content",
       "members","join","request-access","grant-access","debug","dev","test","seed"]
for n in names:
    s,o=call(n,"POST",{})
    # 404 means function doesn't exist; anything else = exists
    tag = "MISSING" if (s==404 and "NOT_FOUND" in o.upper() or (s==404)) else "EXISTS"
    print(f"{n:16} {s} {o[:120]}")
