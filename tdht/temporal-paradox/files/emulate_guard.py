import struct, json

# Emulate the guard computation from main (0x1b80-0x1c30) after loading rec08
# This follows the disasm exactly.

tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'
MODS=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]

rec=open("r9cf/rec08.bin","rb").read()
ln=rec[5]|(rec[6]<<8)

# Parse modules and store into tables (emulating func_1656)
presence = [0]*20   # byte per module idx
payloads = [bytearray(12) for _ in range(20)]  # up to 12 bytes per slot

i=8
while i < ln-2:
    tag=rec[i]; plen=rec[i+1]; pdata=rec[i+2:i+2+plen]
    # map tag to idx via dispatch
    name=tag_to_mod.get(tag)
    if name:
        idx=MODS.index(name)
        presence[idx]=plen
        for k in range(min(plen,12)):
            payloads[idx][k]=pdata[k]
    i+=2+plen

print("=== loaded module state ===")
for idx in range(20):
    if presence[idx]:
        print(f"  [{idx:2d}] {MODS[idx]} len={presence[idx]} data={bytes(payloads[idx][:presence[idx]]).hex()}")

# The guard computation (0x1b80 onwards):
# 1) func_1273(edi=2, esi=0x19, edx=0x37, ecx=0x51, r8d=0)
def func_1273(edi, esi, edx, ecx, r8d):
    if edi == 1:
        eax = (ecx >> 8) & 0xffffffff
        eax ^= edx; eax ^= r8d; eax ^= esi
        eax &= 0xff
        if eax == 0: eax = 0xa7
        return eax
    else:
        edx2 = edx ^ ecx ^ esi
        eax = edx2 ^ r8d
        eax &= 0xffffffff
        if edx2 == r8d: eax = 0x6d2b79f5
        return eax

guard_mix = func_1273(2, 0x19, 0x37, 0x51, 0)
print(f"\nfunc_1273(2,0x19,0x37,0x51,0) = {guard_mix:#x}")
# stored in [rbp-0x48]

# 2) [rbp-0x40] = 0 (qword)
state_qword = 0

# 3) func_1362(rdi=9, esi=8, rdx=&[rbp-0x40])
# This writes 8 bytes to [rbp-0x40] based on input=9, size=8
def func_1362(val, size, out):
    # bit decomposition + xor parity
    b = [(val >> k) & 1 for k in range(4)]  # bits 0-3 of val
    bit0, bit1, bit2, bit3 = b[0], b[1], b[2], b[3]
    out[0] = bit0 ^ bit2 ^ bit3
    out[1] = bit1 ^ bit2 ^ bit3  # was: bit1 ^ bit3 ^ bit0? let me re-read asm
    # Actually: 0x1362 does:
    # ecx = (edi>>3)&1, edx=(edi>>2)&1, esi=edi&1, edi=(edi>>1)&1
    # for val=9=0b1001: bit0=1,bit1=0,bit2=0,bit3=1
    ecx_v = (val>>3)&1  # bit3
    edx_v = (val>>2)&1  # bit2
    esi_v = val&1        # bit0
    edi_v = (val>>1)&1   # bit1
    r8 = edx_v ^ ecx_v ^ esi_v
    out[0] = r8
    r8_2 = edi_v ^ ecx_v ^ esi_v
    out[1] = r8_2
    out[2] = ecx_v
    out[3] = edi_v ^ edx_v ^ esi_v
    out[4] = edx_v
    out[5] = edi_v
    out[6] = esi_v
    if size == 8:
        # xor parity of bytes 0-6
        p = 0
        for k in range(7):
            p ^= out[k]
        out[7] = p
    return out

buf = bytearray(8)
func_1362(9, 8, buf)
print(f"func_1362(9,8) = {list(buf)}")

# 4) Read byte at 0x4078 = payloads[8][0] (idx 8 = cf)
cf_byte = payloads[8][0]  # cf = idx 8
print(f"cf payload[0] (byte@0x4078) = {cf_byte:#x}")

# 5) func_1898(edi=0, esi=cf_byte)
# 0x1898 is a lookup: edi=0 -> case 0x18b8
def func_1898(edi, esi):
    if edi == 0:
        if esi == 4: return 1
        if esi == 5: return 2
        if esi == 3: return 0  # cmove: eax=edi=0 when esi==3
        return 0x63
    # other cases exist but edi=0 for us
    return 0x63

lookup_result = func_1898(0, cf_byte)
print(f"func_1898(0, {cf_byte:#x}) = {lookup_result:#x}")
# XOR with 0x4f
val_44 = lookup_result ^ 0x4f
print(f"XOR 0x4f = {val_44:#x}")

# 6) func_12ab(edi=2, esi=0x51, rdx=&guard_mix) 
# This is the PRNG step: edi=2 -> calls func_1263 (LCG)
def func_1263(x):
    return (x * 0x19660d + 0x3c6ef35f) & 0xffffffff

def func_1249(x):
    eax = (x << 13) & 0xffffffff
    eax ^= x
    edx = (eax >> 17) & 0xffffffff
    edx ^= eax
    eax = (edx << 5) & 0xffffffff
    eax ^= edx
    return eax

def func_12ab(edi, esi, state_ref):
    # edi=2 -> calls func_1263(state[0])
    if edi == 1:
        # xorshift
        val = state_ref[0]
        new = func_1249(val)
        state_ref[0] = new
        return new & 0xff
    else:
        val = state_ref[0]
        new = func_1263(val)
        state_ref[0] = new
        ecx = new & 1
        return ecx

gm_ref = [guard_mix]
prng_out = func_12ab(2, 0x51, gm_ref)
print(f"func_12ab(2,0x51,state) = {prng_out}, state now = {gm_ref[0]:#x}")

# 7) func_12ef(edi=2, esi=1, edx=2, ecx=0x10)
def func_12ef(edi, esi, edx, ecx):
    if edi == 1:
        return (edx ^ esi) & 0xffffffff
    elif edi == 2:
        eax = (esi + edx) & 0xffffffff
        rem = eax % ecx if ecx else 0
        return rem
    else:
        eax = (ecx - edx + esi) & 0xffffffff
        rem = eax % ecx if ecx else 0
        return rem

r12d = func_12ef(2, 1, 2, 0x10)
print(f"func_12ef(2,1,2,0x10) = {r12d}")

# 8) func_131d(rdi=&buf, esi=4, edx=1)
def func_131d(data, size, direction):
    # bit packing from array of single-bit bytes
    # size=4, direction=1
    result = 0
    for i in range(size):
        bit = data[i] & 1
        if direction == 1:
            shift = i
        else:
            shift = size - 1 - i
        result |= (bit << shift)
    return result

pack_result = func_131d(buf, 4, 1)
print(f"func_131d(buf[:4],4,1) = {pack_result}")

# 9) Final guard: ebx = prng_out ^ pack_result ^ val_44 ^ r12d ^ 0x6f
ebx = prng_out ^ pack_result ^ val_44 ^ r12d ^ 0x6f
guard = ebx & 0xff
print(f"\nFINAL guard = {guard:#x} = {guard}")

# Now: the FULL .bss state after processing = the 20 module payloads.
# Let me dump ALL of it as a flat array and compute various 14-byte derivations
flat = b''
for idx in range(20):
    flat += bytes(payloads[idx][:presence[idx]]) if presence[idx] else b''
print(f"\nflat payload concat ({len(flat)} bytes): {flat.hex()}")

# CRC16 of flat
def crc16(data):
    v=0xffff
    for byte in data:
        v^=(byte<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v

print(f"CRC16(flat) = {crc16(flat):04x}")

# What if the "egress" is the CRC16 of each of the 7 active modules concatenated?
# 7 modules × 2 bytes = 14 bytes!
active_names = ["o4","dx","c7","cf","g8","ml","lc"]
crcs = []
for name in active_names:
    idx = MODS.index(name)
    data = bytes(payloads[idx][:presence[idx]])
    c = crc16(data)
    crcs.append(c)
    print(f"  CRC16({name}={data.hex()}) = {c:04x}")

flag_body = ''.join(f'{c:04x}' for c in crcs)
print(f"\nCRC16 per active module (7×2=14 bytes): {flag_body}")
print(f"Flag candidate: HTF{{r9_{flag_body}}}")
