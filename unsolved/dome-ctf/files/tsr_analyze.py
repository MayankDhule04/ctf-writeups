import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()
print("len:", len(js))

print("\n=== routes (path:'...') ===")
for p in sorted(set(re.findall(r'path:\s*["\']([^"\']{1,50})["\']', js))):
    print("  ", repr(p))

print("\n=== api / fetch endpoints ===")
for m in re.finditer(r'(fetch\(|axios|\.(?:get|post|put)\(|/api/|/~api/|supabase|createClient)', js):
    i=m.start(); seg=js[max(0,i-40):i+120].replace("\n"," ")
    print("  ...", seg, "...")

print("\n=== url strings ===")
for u in sorted(set(re.findall(r'https?://[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=%-]{4,100}', js)))[:40]:
    print("  ", u)

print("\n=== auth / login / token / password / member strings ===")
for kw in ["password","login","signin","sign in","token","session","isAuth","authenticated","role","admin","member","invite","access_code","passcode","localStorage","sessionStorage","Bearer","jwt","supabase","anon","apikey","api_key","gate","verify","otp","magic"]:
    hits=[m.start() for m in re.finditer(re.escape(kw), js, re.I)]
    if hits:
        print(f"\n[{kw}] {len(hits)}")
        for i in hits[:3]:
            print("   ...", js[max(0,i-70):i+90].replace("\n"," "), "...")
