import re, glob, os

files = {
 "pastebin": max(glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True), key=os.path.getsize),
 "bundle": r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js",
}
terms = ["T-484","484","archive","internal","x-forwarded","x-real","x-client","client-ip",
         "forwarded","real-ip","trust","boundary","header","x-signal","x-origin","x-internal",
         "cf-connecting","true-client","via","x-"]
for name, path in files.items():
    try:
        txt = open(path,"r",encoding="utf-8",errors="replace").read()
    except Exception as e:
        print(name,"ERR",e); continue
    print(f"\n########## {name} ({len(txt)} bytes) ##########")
    for t in terms:
        hits=[m.start() for m in re.finditer(re.escape(t), txt, re.I)]
        if hits:
            print(f"\n[{t}] {len(hits)} hits")
            for i in hits[:3]:
                seg=txt[max(0,i-90):i+90].replace("\n"," ")
                print("   ...",seg,"...")
    # all distinct X-* header-looking tokens
    hdrs=sorted(set(re.findall(r'[Xx]-[A-Za-z][A-Za-z0-9-]{2,30}', txt)))
    if hdrs:
        print("\n   X-* tokens:", hdrs[:40])
