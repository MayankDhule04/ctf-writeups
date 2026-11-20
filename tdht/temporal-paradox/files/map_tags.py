import struct
d=open(r'extracted/usr/local/sbin/r9sampler','rb').read()

# file offset == vaddr for this PIE's text (load bias 0). Verify: .rodata at 0x2000.
# jump table 1 base referenced at 0x16e1: lea rcx,[rip+0x91c]; rip after instr = 0x16e8 -> 0x16e8+0x91c=0x2004
# entries: movsxd rax,[rcx + rdi*4] where rdi = tag-0x22, for tag-0x22 in 0..0x4b (76 entries)
base1 = 0x2004
def tgt(base, i):
    off = struct.unpack('<i', d[base+i*4:base+i*4+4])[0]
    return base + off

# The jump lands on one of the case stubs at 0x171f.. each does mov edi, <IDX>; call 0x1656
# Map stub addr -> idx by reading the 'mov edi, imm' 
def stub_idx(addr):
    # addr points to 'mov edi, imm32' = B8 imm? Actually 'mov edi,0' = BF xx xx xx xx
    b=d[addr]
    if b==0xbf:
        return struct.unpack('<I', d[addr+1:addr+5])[0]
    return None

MODS = ["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]

print("=== table1 (tags 0x22..0x6d) ===")
tag_to_mod={}
for i in range(0x4c):
    a=tgt(base1,i)
    idx=stub_idx(a)
    tag=0x22+i
    if idx is not None and idx<20:
        tag_to_mod[tag]=MODS[idx]
        # print(f"tag {tag:#04x} -> idx {idx} {MODS[idx]}")

# table2 at 0x170e: lea rcx,[rip+0xa1f]; rip after=0x1715 ->0x1715+0xa1f=0x2134
base2=0x2134
for i in range(0x46):
    a=tgt(base2,i)
    idx=stub_idx(a)
    tag=(i-0x70)&0xff  # rdi+0x70 index; tag = i-0x70 mod 256
    tag=(0x100 + (i-0x70))&0xff if i<0x70 else i-0x70
    # actually dispatch: edi2=tag+0x70; index=edi2; so tag = i-0x70 (with wrap for high tags)
    realtag=(i-0x70)%256
    if idx is not None and idx<20:
        tag_to_mod[realtag]=MODS[idx]

for t in sorted(tag_to_mod):
    print(f"tag {t:#04x} -> {tag_to_mod[t]}")
print("total mapped", len(tag_to_mod))

import json
open('tag_map.json','w').write(json.dumps({str(k):v for k,v in tag_to_mod.items()}))
