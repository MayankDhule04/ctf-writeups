import urllib.request, ssl, re
ctx = ssl.create_default_context()
url = "https://thesignalroom.org/assets/index--Iw1-uQu.js"
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
js = urllib.request.urlopen(req, timeout=60, context=ctx).read().decode("utf-8","replace")
open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","w",encoding="utf-8").write(js)
print("size:", len(js))

for p in ["custom-otp","functions/v1","supabase",".supabase.co","otp","apikey","anon","Bearer","lantern","invite","member_area","MemberArea"]:
    c = len(re.findall(re.escape(p), js, re.I))
    if c: print(f"  {p}: {c}")

print("\n=== https URLs ===")
for u in sorted(set(re.findall(r'https://[A-Za-z0-9.\-]+\.[A-Za-z]{2,}[^"\'` )]*', js))):
    if not re.search(r'reactjs|w3\.org|schema\.org', u):
        print("  ", u[:140])

print("\n=== eyJ tokens ===")
for t in sorted(set(re.findall(r'eyJ[A-Za-z0-9_\-]{20,}', js))):
    print("  ", t[:200])

# context around custom-otp and functions
for kw in ["custom-otp","functions/v1","supabase"]:
    m = re.search(re.escape(kw), js, re.I)
    if m:
        i=m.start(); print(f"\n[ctx {kw}] ...{js[max(0,i-120):i+140]}...")
