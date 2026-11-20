import urllib.request, urllib.error, ssl, json, time

BASE="https://iuqrarlmvuydxhiygkro.supabase.co"
ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cXJhcmxtdnV5ZHhoaXlna3JvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAzODI2NzUsImV4cCI6MjA4NTk1ODY3NX0.DCWPItRMC2aekqWjFoTGoROzzmR_q2uy2NjJK-nAxLg"
ctx=ssl.create_default_context()
def req(method, path, body=None, token=None):
    r=urllib.request.Request(f"{BASE}{path}", data=(json.dumps(body).encode() if body is not None else None), method=method,
        headers={"apikey":ANON,"Authorization":f"Bearer {token or ANON}","Content-Type":"application/json","Accept":"application/json"})
    try:
        resp=urllib.request.urlopen(r,timeout=20,context=ctx); return resp.status, resp.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code, e.read().decode("utf-8","replace")
    except Exception as e: return "ERR", str(e)

s,o=req("POST","/auth/v1/signup",{"email":f"t{int(time.time())}@proton.me","password":"L@n2026!"})
tok=json.loads(o).get("access_token")

print("=== bucket list (all) ===")
for lbl,tk in [("anon",None),("authed",tok)]:
    s,o=req("GET","/storage/v1/bucket",token=tk); print(f"  [{lbl}] {s} {o[:400]}")

print("\n=== bucket info chapter-files ===")
for lbl,tk in [("anon",None),("authed",tok)]:
    s,o=req("GET","/storage/v1/bucket/chapter-files",token=tk); print(f"  [{lbl}] {s} {o[:300]}")

print("\n=== list objects in chapter-files ===")
for lbl,tk in [("anon",None),("authed",tok)]:
    s,o=req("POST","/storage/v1/object/list/chapter-files",{"prefix":"","limit":100,"offset":0,"sortBy":{"column":"name","order":"asc"}},token=tk)
    print(f"  [{lbl}] {s} {o[:1200]}")

print("\n=== rpc probes ===")
for fn in ["lantern","get_chapters","get_content","is_member","current_user_email"]:
    s,o=req("POST",f"/rest/v1/rpc/{fn}",{},token=tok); print(f"  rpc/{fn} -> {s} {o[:120]}")
