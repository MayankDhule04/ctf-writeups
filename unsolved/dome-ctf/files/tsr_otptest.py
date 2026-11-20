import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def call(fn, body):
    url=f"{BASE}/functions/v1/{fn}"
    data=json.dumps(body).encode()
    req=urllib.request.Request(url, data=data, method="POST",
        headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json","Accept":"application/json"})
    try:
        r=urllib.request.urlopen(req,timeout=25,context=ctx)
        return r.status, r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

tests = [
    ("custom-otp", {"email":"attacker@example.com"}),
    ("custom-otp", {"email":"admin@thesignalroom.org"}),
    ("custom-otp", {"email":"host@thesignalroom.org"}),
    ("verify-otp", {"email":"attacker@example.com","code":"000000"}),
]
for fn, body in tests:
    s, out = call(fn, body)
    print(f"\n===== POST {fn} {body} -> {s} =====")
    print(out[:1500])
