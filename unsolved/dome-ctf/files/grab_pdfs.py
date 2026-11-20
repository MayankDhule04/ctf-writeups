import urllib.request, ssl, re, os

base = "https://www.signalroom.in"
cands = ["/assets/Founder-Authority-Playbook.pdf",
         "/Founder-Authority-Playbook.pdf",
         "/assets/Expert-Guide-to-Getting-Found.pdf",
         "/Expert-Guide-to-Getting-Found.pdf"]
ctx = ssl.create_default_context()
outdir = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf"

for c in cands:
    try:
        req = urllib.request.Request(base+c, headers={"User-Agent":"Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=30, context=ctx)
        data = r.read()
        print(f"{c} -> {r.status} {r.headers.get('Content-Type')} {len(data)} bytes")
        if r.status == 200 and len(data) > 500:
            fn = os.path.join(outdir, c.split("/")[-1])
            open(fn, "wb").write(data)
            # grep ascii strings for links/creds
            txt = data.decode("latin1", "replace")
            hits = re.findall(r'(https?://[^\s<>")]{6,120}|[A-Za-z0-9_.-]+\{[^}]{3,60}\}|member[^\s]{0,30}|login[^\s]{0,20}|password[^\s]{0,20}|invite[^\s]{0,30}|\.onion)', txt, re.I)
            uniq = sorted(set(hits))
            print("   interesting strings:")
            for h in uniq[:40]:
                print("     ", h)
    except Exception as ex:
        print(f"{c} -> ERR {ex}")
