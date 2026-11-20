import re, glob, os

# 1) carved DBs — dump any URL/domain-like strings
dbdir = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\carved_dbs"
url_re = re.compile(rb'(?:https?://|www\.)[A-Za-z0-9._~:/?#@!$&\'()*+,;=%-]{4,100}')
dom_re = re.compile(rb'\b[a-z0-9][a-z0-9-]{1,40}\.(?:in|com|net|org|io|xyz|onion|social|app|site|me|co)\b', re.I)

print("=== carved DBs: URLs/domains ===")
found = set()
for p in glob.glob(os.path.join(dbdir, "*.sqlite")):
    data = open(p, "rb").read()
    for m in url_re.findall(data):
        found.add(m.decode("latin1","replace"))
    for m in dom_re.findall(data):
        found.add(m.decode("latin1","replace"))
for s in sorted(found):
    print("  ", s)

# 2) full image — domain-like tokens (dedup), excluding example.com noise
img = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
CHUNK = 16*1024*1024
overlap = 128
doms = {}
with open(img, "rb") as fh:
    prev = b""
    while True:
        d = fh.read(CHUNK)
        if not d: break
        buf = prev + d
        for m in dom_re.findall(buf):
            s = m.decode("latin1","replace").lower()
            doms[s] = doms.get(s,0)+1
        prev = buf[-overlap:]
print("\n=== image: distinct domains (count) ===")
for s,c in sorted(doms.items(), key=lambda x:-x[1]):
    print(f"  {c:5d}  {s}")
