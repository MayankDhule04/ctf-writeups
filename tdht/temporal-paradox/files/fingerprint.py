import json, hashlib
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'
ROUTE=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]
accepted=[2,3,6,8,9,10]
def parse(rec):
    ln=rec[5]|(rec[6]<<8); i=8; ents=[]
    while i<ln-2:
        mid=rec[i]; pl=rec[i+1]; ents.append((tag_to_mod.get(mid,hex(mid)),rec[i+2:i+2+pl])); i+=2+pl
    return ents
recs={i:open(f"r9cf/rec{i:02d}.bin","rb").read() for i in accepted}

def crc16(data):
    v=0xffff
    for byte in data:
        v^=(byte<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v&0xffff

# CRC of each accepted record body: recall accepted guard=0x21. Let's compute CRC over body and check tail.
print("=== verify tail CRC per record ===")
for i in accepted:
    rec=recs[i]; ln=rec[5]|(rec[6]<<8)
    body=rec[:ln-2]; tail=rec[ln-2:ln]
    print(f"rec{i:02d} crc(body)={crc16(body):04x} tail={tail.hex()} crc(from8)={crc16(rec[8:ln-2]):04x}")

# candidate: the newest complete lane1 config. Determine newest: o4 payload as u32 LE = generation?
def val(ents,m):
    d=dict(ents); return d.get(m,b'')
for i in accepted:
    e=parse(recs[i])
    o4=int.from_bytes(val(e,'o4'),'little')
    print(f"rec{i:02d} o4-gen={o4}  ml={val(e,'ml').hex()} g8={val(e,'g8').hex()} lc={val(e,'lc').hex()} cf={val(e,'cf').hex()}")
