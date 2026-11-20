import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"

# find all 'boardreader' occurrences and dump wide context, looking for URLs/hosts/config keys
needle = b"boardreader"
CHUNK = 16*1024*1024
overlap = 64
offs = []
with open(f,"rb") as fh:
    off=0; prev=b""
    while True:
        d=fh.read(CHUNK)
        if not d: break
        buf=prev+d
        s=0
        while True:
            i=buf.find(needle,s)
            if i<0: break
            offs.append(off-len(prev)+i); s=i+1
        prev=buf[-overlap:]; off+=len(d)
print("boardreader offsets:", offs)

# also search for config-ish keys and any non-example host near board data
keys = [b"base_url", b"baseUrl", b"server", b"host", b"endpoint", b"api_url",
        b"apiBase", b"board_url", b"instance", b"https://board", b"board.",
        b".board", b"forum", b"community"]
with open(f,"rb") as fh:
    data_regions = []
    for o in offs:
        fh.seek(max(0,o-800)); chunk=fh.read(1800)
        txt="".join(chr(c) if 32<=c<127 else "." for c in chunk)
        txt=re.sub(r'\.{4,}',' ... ',txt)
        # only print if there's a url/host/config hint
        if re.search(r'https?://|base_url|server|host|endpoint|\.(in|com|net|io|xyz|onion|app)\b', txt, re.I):
            data_regions.append((o,txt))
    print("\n=== boardreader regions with host/url/config hints ===")
    for o,txt in data_regions:
        print(f"--- offset {o} ---")
        print(txt[:900])
        print()
