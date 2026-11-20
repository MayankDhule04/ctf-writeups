import re
db=open("carved.db","rb").read()
PGSZ=4096
# retired_lane_profiles(slot INT PK, label TEXT, blob BLOB, residue BLOB)
# rows stored as table-btree leaf cells. After DROP, pages are on freelist but data persists.
# A leaf cell: varint payloadlen, varint rowid, record(header: varint hdrlen, serial types...), body.
# We look for records whose header decodes to: [type_int_or_null, text, blob, blob].
# Heuristic: scan for label strings then parse backwards. First find plausible labels.
# Labels probably like 'gen0','gen1','current','stale', etc. Let's dump all short printable
# tokens that are NOT the injection/decoy text, across the whole db, that look like profile labels.

# Simpler: scan every page for a 4-column record with 2 blobs. Walk all byte offsets, try parse.
def rd_varint(b,o):
    v=0
    for k in range(9):
        c=b[o+k]; 
        if k==8:
            v=(v<<8)|c; return v,o+9
        v=(v<<7)|(c&0x7f)
        if not (c&0x80): return v,o+k+1
    return v,o+9

def serial_len(t):
    if t==0: return 0
    if t<=4: return t
    if t==5: return 6
    if t==6 or t==7: return 8
    if t==8 or t==9: return 0
    if t>=12:
        return (t-12)//2 if t%2==0 else (t-13)//2
    return 0

found=[]
for o in range(len(db)-4):
    # try: hdrlen varint small (<=12), then 4 serial types
    try:
        hdrlen,p=rd_varint(db,o)
        if hdrlen<4 or hdrlen>16: continue
        types=[]
        pp=p
        while pp < o+hdrlen:
            t,pp=rd_varint(db,pp)
            types.append(t)
        if len(types)!=4: continue
        # col0 int (1..6 or 8/9), col1 text(>=13 odd), col2 blob(>=12 even), col3 blob(>=12 even)
        t0,t1,t2,t3=types
        if not (t0 in (1,2,8,9)): continue
        if not (t1>=13 and t1%2==1): continue
        if not (t2>=12 and t2%2==0 and t2>12): continue
        if not (t3>=12 and t3%2==0 and t3>12): continue
        body=o+hdrlen
        l1=serial_len(t1); l2=serial_len(t2); l3=serial_len(t3)
        l0=serial_len(t0)
        label=db[body+l0:body+l0+l1]
        if not all(32<=c<127 for c in label): continue
        blob=db[body+l0+l1:body+l0+l1+l2]
        residue=db[body+l0+l1+l2:body+l0+l1+l2+l3]
        found.append((o,label,blob,residue))
    except: pass

print("candidates:",len(found))
for o,label,blob,residue in found[:40]:
    print(f"@{hex(o)} label={label!r} blob({len(blob)})={blob.hex()} residue({len(residue)})={residue.hex()}")
