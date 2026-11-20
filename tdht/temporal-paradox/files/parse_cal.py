c0 = bytes.fromhex("43395452000404060301030200040301000205010003020a020300010b030200010f030102004792")
c1 = bytes.fromhex("43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9")

for name,c in [("lane0",c0),("lane1",c1)]:
    print(f"== {name} len={len(c)} ==")
    print("magic:", c[:4], c[:4].decode('latin1'))
    print("byte4 (version/lane):", c[4])
    print("bytes5..:", " ".join(f"{b:02x}" for b in c[5:]))
    print("trailer (last2):", c[-2:].hex())
    print()
