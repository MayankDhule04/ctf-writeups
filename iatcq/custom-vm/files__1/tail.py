f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b = open(f,"rb").read()
ro_off=8192; ro_addr=0x2000; ro_size=635
# encrypted program region started at 0x20c0 (off 8192+0xc0=8384), length 349 -> ends 8733
enc_start = 8192 + (0x20c0-0x2000)
enc_len = 349
print("enc region file:", enc_start, "to", enc_start+enc_len, "( .rodata ends", ro_off+ro_size, ")")
# bytes between end of enc program and end of rodata:
tail = b[enc_start+enc_len : ro_off+ro_size]
print("tail after program in rodata:", tail)
# Also: is 0x86d03165 present as bytes anywhere? and reverse?
import struct
for pat,name in [(struct.pack("<I",0x86d03165),"LE"),(struct.pack(">I",0x86d03165),"BE")]:
    idx=b.find(pat); print(name, pat.hex(), "at", idx)
# dump the whole rodata region 0x21f0..0x2260 (the readable-ish strings) decoded with LCG? 
# Actually re-run LCG but keep going past 349 to see if extra structured data follows.
src_addr=0x20c0
eax=0xc0ffee42
extra=[]
srcfull=b[enc_start:ro_off+ro_size]
for i in range(len(srcfull)):
    eax=(eax*0x41c64e6d+0x3039)&0xffffffff
    ecx=(eax>>16)&0xffffffff
    extra.append((ecx^srcfull[i])&0xff)
extra=bytes(extra)
print("decrypted full rodata-from-0x20c0 len", len(extra))
print("bytes 349..end (post-program):", extra[349:])
# show ascii of full
print("ascii:", "".join(chr(c) if 32<=c<127 else '.' for c in extra))
