import re
b=open(r"Temporal Paradox/gateway_snapshot.img","rb").read()

# ext4 dir entries around 0xa16000-0xa2c000: printable filename fragments
region=b[0xa16000:0xa2c000]
print("=== printable strings in filename region ===")
for m in re.finditer(rb'[ -~]{3,}', region):
    s=m.group().decode('latin1')
    # filter to filename-ish
    print(hex(0xa16000+m.start()), repr(s))
