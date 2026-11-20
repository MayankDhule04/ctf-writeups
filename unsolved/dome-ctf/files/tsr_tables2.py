import urllib.request, urllib.error, ssl, time, json

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()
def get(path, token=None):
    r=urllib.request.Request(f"{BASE}/rest/v1/{path}", headers={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Accept":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=12,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

# authed token
s,o=urllib.request.urlopen(urllib.request.Request(f"{BASE}/auth/v1/signup",data=json.dumps({"email":f"t{int(time.time())}@proton.me","password":"L@n2026!"}).encode(),headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"}),timeout=20,context=ctx), None
import json as J
tok=None
try:
    rr=urllib.request.urlopen(urllib.request.Request(f"{BASE}/auth/v1/signup",data=J.dumps({"email":f"u{int(time.time())}@proton.me","password":"L@n2026!"}).encode(),headers={"apikey":ANON,"Authorization":f"Bearer {ANON}","Content-Type":"application/json"}),timeout=20,context=ctx)
    tok=J.loads(rr.read().decode()).get("access_token")
except Exception as e: print("tok err",e)

cands=["research","researches","dossier","dossiers","intel","intelligence","signals","signal",
       "clues","clue","briefings","briefing","reports","report","documents","document","files","file",
       "resources","resource","nightfall","operations","operation","leads","lead","intel_reports",
       "members","member","profiles","profile","contacts","contact","events","event","content","contents",
       "chapter_files","chapterfiles","notes","note","comments","comment","messages","posts","threads"]
found=[]
for t in cands:
    s,o=get(f"{t}?select=*&limit=5", token=tok)
    if not (s==404 and "PGRST205" in o):
        found.append((t,s,o[:300]))
print("=== existing tables (not 404) ===")
for t,s,o in found:
    print(f"{t:18} {s} {o}")
