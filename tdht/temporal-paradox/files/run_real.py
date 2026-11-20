import os

# Build files to feed r9sampler:
# 1) All 6 accepted records concatenated
# 2) Just rec08 alone
# 3) The full R9CF region from the image (all 12 + the lane0 tail)
# 4) Both .cal files converted to R9CF

accepted=[2,3,6,8,9,10]
allrecs=b''
for i in accepted:
    allrecs+=open(f"r9cf/rec{i:02d}.bin","rb").read()
open("feed_accepted.bin","wb").write(allrecs)

# all 12
allrecs12=b''
for i in range(12):
    allrecs12+=open(f"r9cf/rec{i:02d}.bin","rb").read()
open("feed_all12.bin","wb").write(allrecs12)

# just rec08
open("feed_rec08.bin","wb").write(open("r9cf/rec08.bin","rb").read())

# The raw region from 0x15cf30a covering all R9CF + the lane0 record at 0x15dd29a
img=open(r"Temporal Paradox/gateway_snapshot.img","rb").read()
region=img[0x15cf30a:0x15df000]
open("feed_region.bin","wb").write(region)

print("feed_accepted.bin", len(allrecs))
print("feed_all12.bin", len(allrecs12))
print("feed_rec08.bin", os.path.getsize("feed_rec08.bin"))
print("feed_region.bin", len(region))
