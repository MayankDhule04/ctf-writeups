p = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421.jpg"
with open(p, "rb") as f:
    data = f.read()

i = 2  # skip SOI
assert data[0:2] == b"\xff\xd8"
while i < len(data) - 1:
    if data[i] != 0xFF:
        print("desync at", i)
        break
    marker = data[i+1]
    if marker in (0xD8, 0xD9):  # SOI, EOI
        print(f"@{i} marker=FF{marker:02X}")
        i += 2
        if marker == 0xD9:
            break
        continue
    if marker == 0x01 or (0xD0 <= marker <= 0xD7):
        i += 2
        continue
    length = (data[i+2] << 8) | data[i+3]
    seg = data[i+4:i+2+length]
    print(f"@{i} marker=FF{marker:02X} length={length} data_preview={seg[:40]!r}")
    if marker == 0xDA:  # SOS - start of scan, rest is entropy-coded data
        print("  SOS reached, scanning for next marker not in entropy data...")
        break
    i += 2 + length
