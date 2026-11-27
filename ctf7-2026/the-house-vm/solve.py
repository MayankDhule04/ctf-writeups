#!/usr/bin/env python3
"""housevm solver: decrypt bytecode (splitmix64 xor), invert the CBC-like VM cipher."""
import struct,sys
d=open('housevm','rb').read(); B=0x400000
M=(1<<64)-1
def rd(a,n): return d[a-B:a-B+n]
def decrypt(key):
    enc=rd(0x47f7e8,0xc00); out=bytearray(); s=key
    while len(out)<len(enc):
        s=(s+0x9e3779b97f4a7c15)&M
        z=((s^(s>>30))*0xbf58476d1ce4e5b9)&M
        z=((z^(z>>27))*0x94d049bb133111eb)&M
        z^=z>>31
        for i in range(8):
            if len(out)<len(enc): out.append(enc[len(out)]^((z>>(8*i))&0xff))
    return bytes(out)
rol=lambda x,n:((x<<(n&7))|(x>>(8-(n&7))))&0xff if n&7 else x
ror=lambda x,n:rol(x,8-(n&7))
INV=lambda m:pow(m,-1,256)
COND={12,13,14,15}
def fwd(op,s,a,b):
    # returns True if applied
    p,dd=a>>4,a&15
    if op in COND and not s[p]&1: return
    k={12:1,13:2,14:5,15:3}.get(op,op)
    if k==1:s[dd]=(s[dd]+b)&255
    elif k==2:s[dd]^=b
    elif k==3:s[dd]=rol(s[dd],b)
    elif k==4:s[dd]=(s[dd]-b)&255
    elif k==5:e=b&15;s[dd],s[e]=s[e],s[dd]
    elif k==6:s[dd]=(s[dd]+s[b&15])&255
    elif k==7:s[dd]^=s[b&15]
    elif k==8:s[dd]=(s[dd]*(b|1))&255
    elif k==9:s[dd]=ror(s[dd],b)
    elif k==11:s[dd]=rol(s[dd],s[b&15])
def unapply(op,s,a,b):
    p,dd=a>>4,a&15
    k={12:1,13:2,14:5,15:3}.get(op,op)
    if k==1:s[dd]=(s[dd]-b)&255
    elif k==2:s[dd]^=b
    elif k==3:s[dd]=ror(s[dd],b)
    elif k==4:s[dd]=(s[dd]+b)&255
    elif k==5:e=b&15;s[dd],s[e]=s[e],s[dd]
    elif k==6:s[dd]=(s[dd]-s[b&15])&255
    elif k==7:s[dd]^=s[b&15]
    elif k==8:s[dd]=(s[dd]*INV(b|1))&255
    elif k==9:s[dd]=rol(s[dd],b)
    elif k==11:
        # s[dd] rotated by s[b&15]; if same reg ambiguous
        assert dd!=b&15; s[dd]=ror(s[dd],s[b&15])
def run_round(prog,s):
    for i in range(0,len(prog),3): fwd(prog[i],s,prog[i+1],prog[i+2])
def inv_round(prog,s):
    for i in range(len(prog)-3,-1,-3):
        op,a,b=prog[i:i+3]
        if op in COND:
            p=a>>4
            # not applied?
            pre=list(s); unapply(op,pre,a,b)
            ok_app=bool(pre[p]&1)
            ok_not=not s[p]&1
            assert ok_app!=ok_not or (ok_app and ok_not) is False or True
            if ok_app and not ok_not: s[:]=pre
            elif ok_not and not ok_app: pass
            elif ok_app and ok_not: raise Exception("ambiguous at %d"%(i//3))
            else: raise Exception("inconsistent at %d"%(i//3))
        else: unapply(op,s,a,b)
def main(key=0x5b1f2e3d4c6a7988):
    prog=decrypt(key)
    iv=list(rd(0x47f7d4,16)); tgt=rd(0x4803ee,64)
    # self test fwd/inv
    t=list(range(16)); u=t[:]; run_round(prog,u); inv_round(prog,u); assert u==t,"roundtrip"
    pt=b''; prev=iv
    for blk in range(4):
        c=list(tgt[16*blk:16*blk+16]); s=c[:]
        for _ in range(16): inv_round(prog,s)
        pt+=bytes(x^y for x,y in zip(s,prev)); prev=c
    return pt
if __name__=='__main__':
    pt=main(); print(pt)
    word=pt.rstrip(b'\0'); print('ctf7{'+word.decode()+'}')
