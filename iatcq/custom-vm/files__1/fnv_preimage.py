import itertools, string
TARGET=0x86d03165
P=0x01000193; B=0x811c9dc5; M=0xffffffff
def fnv1a(data):
    h=B
    for b in data: h=((h^b)*P)&M
    return h
def fnv1(data):
    h=B
    for b in data: h=((h*P)&M)^b
    return h

# 1) brute all readable strings length 1..4 for either FNV variant
alpha=[chr(c) for c in range(0x20,0x7f)]
for L in range(1,4):  # length 4 = 95^4 ~ 81M, do up to 3 fast then 4 if needed
    for tup in itertools.product(range(0x20,0x7f), repeat=L):
        d=bytes(tup)
        if fnv1a(d)==TARGET: print("FNV1a preimage len",L,":",d); 
        if fnv1(d)==TARGET: print("FNV1 preimage len",L,":",d)
    print("done len",L)
