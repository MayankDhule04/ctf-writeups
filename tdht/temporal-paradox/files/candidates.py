import json, hashlib
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'
ROUTE=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]
def parse(rec):
    ln=rec[5]|(rec[6]<<8); i=8; ents={}
    while i<ln-2:
        mid=rec[i]; pl=rec[i+1]; ents[tag_to_mod.get(mid,hex(mid))]=rec[i+2:i+2+pl]; i+=2+pl
    return ents

rec=open("r9cf/rec08.bin","rb").read()
ln=rec[5]|(rec[6]<<8)
e=parse(rec)
canon=b''.join(e.get(m,b'') for m in ROUTE)
body=rec[:ln-2]
fullrec=rec[:ln]
print("canon:",canon.hex(),len(canon))

def show(name,bs):
    h=bs.hex()
    print(f"{name}: HTF{{r9_{h[:28]}}}  (full {h})")

# lane1 xor-cumulative keystream of canon, take distinctive middle
def lane1(data):
    s=0;o=bytearray()
    for x in data:
        s^=x;o.append(s)
    return bytes(o)
def lane0(data):
    s=0;o=bytearray()
    for x in data:
        s=(s+x)&0xff;o.append(s)
    return bytes(o)

show("sha256(canon)[:14]", hashlib.sha256(canon).digest()[:14])
show("sha1(canon)[:14]", hashlib.sha1(canon).digest()[:14])
show("md5(canon)[:14]", hashlib.md5(canon).digest()[:14])
show("sha256(body)[:14]", hashlib.sha256(body).digest()[:14])
show("sha256(fullrec)[:14]", hashlib.sha256(fullrec).digest()[:14])
show("lane1(canon)[:14]", lane1(canon)[:14])
show("lane0(canon)[:14]", lane0(canon)[:14])

# secret-bearing fields concatenated (the high-entropy per-config payloads)
secret = e['o3']+e['cf']+e['g8']+e['ml']+e['lc']  # 4+4+4+4+4=20 -> too long, take 14? 
print("\nsecret fields o3|cf|g8|ml|lc:", secret.hex(), len(secret))
show("secretfields[:14]", secret)
# cr constant (8) + something
show("cr|o3|xz..", (e['cr']+e['o3']+e['c7']+e['dx']))

# newest 7 active lane1 module payloads concatenated: o4,dx,c7,cf,g8,ml,lc
act=b''.join(e[m] for m in ["o4","dx","c7","cf","g8","ml","lc"])
print("\nactive concat:",act.hex(),len(act))
show("active[:14]",act)
