import re
b=open(r"Temporal Paradox/gateway_snapshot.img","rb").read()

# The historian DB lives around 0xa22000. retired_lane_profiles CREATE at 0xa22bbb.
# It was DROPPed from the working copy but pages persist. Dump the DB region raw and
# look for its row payloads. Rows would contain label text + blobs.
# First: find any 'lane' / profile labels near the retired table region.
region_start=0xa22000
region=b[region_start:region_start+0x400000]  # 4MB after db header start

print("=== candidate profile labels / interesting text in DB region ===")
for kw in [b'lane', b'profile', b'residue', b'current', b'newest', b'generation',
           b'gen', b'effective', b'HTF', b'key', b'seed', b'xor', b'keystream']:
    for m in re.finditer(re.escape(kw), region):
        off=region_start+m.start()
        ctx=b[off-8:off+40]
        print(f"{hex(off)} {kw} :: {ctx}")
