import os
c0 = bytes.fromhex("43395452000404060301030200040301000205010003020a020300010b030200010f030102004792")
c1 = bytes.fromhex("43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9")

def crc16_ccitt(data):  # matches 0x1849: init 0xffff, poly 0x1021, MSB-first, no final xor (returns eax low 16)
    crc=0xffff
    for byte in data:
        crc ^= (byte<<8)
        crc &= 0xffff
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc<<1) ^ 0x1021) & 0xffff
            else:
                crc = (crc<<1) & 0xffff
    return crc & 0xffff

outdir = r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\variants"
os.makedirs(outdir, exist_ok=True)

def save(name, data):
    open(os.path.join(outdir,name),"wb").write(data)

for lane,c in [("0",c0),("1",c1)]:
    # v1: whole reverse
    save(f"rev_{lane}.cal", c[::-1])
    # v2: fix magic to R9CF, keep rest
    save(f"magic_{lane}.cal", b"R9CF"+c[4:])
    # v3: reverse then fix magic
    r=c[::-1]
    save(f"revmagic_{lane}.cal", b"R9CF"+r[4:])
    # v4: swap 16-bit words
    ws=bytearray()
    for i in range(0,len(c),2):
        ws+=bytes([c[i+1],c[i]])
    save(f"wordswap_{lane}.cal", bytes(ws))
    # v5: build proper R9CF record from the payload with recomputed CRC.
    # .cal layout guess: [magic4][lane1][len? ...]. main reads len at offset 5,6 (LE: [5]|[6]<<8) of record.
    # Let's construct: R9CF + lane byte + body, len covering whole record, CRC16 over record[0:len-2].
    body = c[5:-2]  # inner
    print(f"lane{lane} body({len(body)}):", body.hex())

# also print crc of various spans to match trailer
for lane,c in [("0",c0),("1",c1)]:
    trailer = c[-2:]
    print(f"lane{lane} trailer {trailer.hex()}  crc(c[0:-2])={crc16_ccitt(c[:-2]):04x}  crc(c[4:-2])={crc16_ccitt(c[4:-2]):04x}  crc(c[5:-2])={crc16_ccitt(c[5:-2]):04x}")
    # trailer big-endian value
    print(f"   trailer BE={trailer[0]<<8|trailer[1]:04x} LE={trailer[1]<<8|trailer[0]:04x}")
