import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

print("=== all http(s) URLs ===")
urls = sorted(set(re.findall(r'https?://[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]{4,120}', js)))
for u in urls:
    print("  ", u)

print("\n=== fetch( / axios / XMLHttpRequest contexts ===")
for m in re.finditer(r'(fetch\(|axios|XMLHttpRequest|\.open\(|FormData|formspree|supabase|firebase|googleapis|netlify|method:\s*["\']POST)', js, re.I):
    i = m.start()
    print("  ...", js[max(0,i-60):i+100].replace("\n"," "), "...")

print("\n=== relative api/endpoint strings ===")
eps = sorted(set(re.findall(r'["\'](/[a-zA-Z0-9_\-/]{2,40})["\']', js)))
for e in eps:
    print("  ", e)
