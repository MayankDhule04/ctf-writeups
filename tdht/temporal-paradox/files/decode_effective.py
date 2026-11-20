import os, json
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}

def parse(rec):
    ln = rec[5] | (rec[6]<<8)
    i=8; entries=[]
    while i < ln-2:
        mid=rec[i]; pl=rec[i+1]; payload=rec[i+2:i+2+pl]
        entries.append((mid, tag_to_mod.get(mid,f'?{mid:02x}'), payload))
        i += 2+pl
    return entries, rec[i:]

LANE1=["o4","dx","c7","cf","g8","ml","lc"]
LANE0=["o4","da","c8","cr","x3","ml","lc"]
accepted=[2,3,6,8,9,10]

for i in range(12):
    p=f"r9cf/rec{i:02d}.bin"
    if not os.path.exists(p): continue
    rec=open(p,"rb").read()
    ents,tail=parse(rec)
    mods={name:pl for (mid,name,pl) in ents}
    unknown=[hex(mid) for (mid,name,pl) in ents if name.startswith('?')]
    acc = "ACC" if i in accepted else "rej"
    # payloads for lane1 active modules
    lane1pl = {m: mods.get(m, b'').hex() for m in LANE1}
    print(f"rec{i:02d} {acc} unknown_tags={unknown}")
    print("   lane1:", lane1pl)
