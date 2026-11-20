import urllib.request, urllib.error, ssl

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()

def get(path, token=None):
    url=f"{BASE}/rest/v1/{path}"
    h={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Accept":"application/json"}
    r=urllib.request.Request(url, headers=h)
    try:
        resp=urllib.request.urlopen(r,timeout=15,context=ctx)
        return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

# OpenAPI root lists all tables the anon role can see
print("=== OpenAPI root (/) ===")
s,o=get("")
import re, json
try:
    doc=json.loads(o)
    paths=[p for p in doc.get("paths",{}).keys() if p!="/"]
    print("tables/paths exposed:", paths)
except Exception as e:
    print(s, o[:500])

cands=["otps","otp_codes","codes","login_codes","email_otps","magic_codes","otp","verification_codes",
       "profiles","users","members","leads","posts","invites","invitations","messages","notes",
       "chapters","chapter_content","chapter_access","whitelisted_emails","user_roles","settings","flags","secrets"]
print("\n=== table existence (anon) ===")
for t in cands:
    s,o=get(f"{t}?select=*&limit=1")
    exists = not (s==404 and "PGRST205" in o)
    print(f"{t:22} {s} {'EXISTS' if exists else 'missing'} {o[:120] if exists and o.strip() not in ('[]',) else ''}")
