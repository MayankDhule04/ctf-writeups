import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

print("=== supabase / backend hosts ===")
for m in sorted(set(re.findall(r'[a-z0-9-]+\.supabase\.(?:co|in)', js))): print("  ", m)
for m in sorted(set(re.findall(r'https?://[a-z0-9.-]+\.(?:co|dev|io|com|net|workers\.dev|r2\.dev)[^\s"\'`]*', js)))[:40]: print("  ", m)

print("\n=== JWT-like (eyJ...) ===")
for m in sorted(set(re.findall(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.?[A-Za-z0-9_-]*', js)))[:10]:
    print("  ", m[:120])

print("\n=== relative endpoints / query paths ===")
for m in sorted(set(re.findall(r'["\'`](/(?:api|~api|rest|auth|functions|v1)[A-Za-z0-9_/.-]*)["\'`]', js))):
    print("  ", m)

print("\n=== other asset chunks ===")
for m in sorted(set(re.findall(r'[\w./-]*assets/[\w.-]+\.(?:js|css)', js))): print("  ", m)
for m in sorted(set(re.findall(r'["\`]([\w-]+-[A-Za-z0-9_]{8}\.js)["\`]', js))): print("  chunk:", m)

print("\n=== interesting keywords in context ===")
for kw in ["supabase","createClient","anonKey","apikey","VITE_","import.meta.env","from(","rpc(","/rest/v1","/auth/v1",".functions.","signInWith","getSession","access_token","is_admin","approved","invite","member","chapter","salon","dossier","lead"]:
    hits=[m.start() for m in re.finditer(re.escape(kw), js)]
    if hits:
        print(f"\n[{kw}] {len(hits)}")
        for i in hits[:2]:
            print("   ...", js[max(0,i-60):i+90].replace("\n"," "), "...")
