import urllib.request, urllib.error, ssl, json

BASE = "https://iuqrarlmvuydxhiygkro.supabase.co"
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx = ssl.create_default_context()
tables = ["whitelisted_emails","chapters","chapter_content","chapter_access","chapter-files","user_roles"]

def get(path):
    url = f"{BASE}/rest/v1/{path}"
    req = urllib.request.Request(url, headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Accept":"application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=20, context=ctx)
        return r.status, r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", str(e)

for t in tables:
    enc = urllib.parse.quote(t)
    s, body = get(f"{enc}?select=*")
    print(f"\n===== {t} -> {s} =====")
    print(body[:2500])
