#!/usr/bin/env python3
import sys, zlib, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
raw = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\flashback.swf","rb").read()
body = zlib.decompress(raw[8:]) if raw[:3]==b"CWS" else raw[8:]

# skip rect in header of body
def read_rect(b, p):
    nbits = b[p] >> 3
    total = 5 + nbits*4
    nbytes = (total + 7)//8
    return p + nbytes
p = read_rect(body, 0)
p += 4  # framerate(2) + framecount(2)
print("tag section starts at", p, "body len", len(body))

TAGS = {0:"End",1:"ShowFrame",9:"SetBackgroundColor",39:"DefineSprite",56:"ExportAssets",
        59:"DoInitAction",12:"DoAction",26:"PlaceObject2",2:"DefineShape",
        76:"SymbolClass",82:"DoABC",87:"DefineBinaryData",88:"DefineFontName"}
action_blocks=[]
while p < len(body):
    hdr = struct.unpack("<H", body[p:p+2])[0]; p+=2
    code = hdr >> 6; length = hdr & 0x3f
    if length == 0x3f:
        length = struct.unpack("<I", body[p:p+4])[0]; p+=4
    tagname = TAGS.get(code, f"Tag{code}")
    extra=""
    tagbody = body[p:p+length]
    if code == 59:  # DoInitAction: sprite id (2) then actions
        spid = struct.unpack("<H", tagbody[:2])[0]
        extra = f" spriteId={spid} actionlen={length-2}"
        action_blocks.append(("DoInitAction", spid, tagbody[2:]))
    if code == 12:  # DoAction
        extra = f" actionlen={length}"
        action_blocks.append(("DoAction", None, tagbody))
    if code == 56:  # ExportAssets
        extra = f" {tagbody[:40]!r}"
    if code == 87:
        extra = f" BINARYDATA len={length}"
    print(f"@{p-2:6d} {tagname:18s} code={code} len={length}{extra}")
    p += length
    if code == 0: break

# dump action blocks to files
import os
for i,(kind,spid,ab) in enumerate(action_blocks):
    fn = rf"c:\Users\mayan\OneDrive\Desktop\ctf\flashback_action_{i}_{kind}.bin"
    open(fn,"wb").write(ab)
    print(f"wrote {fn} ({len(ab)} bytes)")
