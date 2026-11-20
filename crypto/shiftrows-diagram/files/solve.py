from hashlib import md5
from itertools import product
import string

BLOCK_SIZE = 16

# Known data
kp_pt = bytes.fromhex('c91ca824783e91dc41a856162bcfaebc')
kp_ct = bytes.fromhex('25c4ceee22c0529b19c2b51886fed24c')
flag_ct = bytes.fromhex('adee3839c59e972f2b2e96440f0002d0')

def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def fun(key, pt, rounds, sbox, perm):
    key = md5(key).digest()
    state = bytearray(pt)
    for r in range(rounds):
        state = bytearray(xor(state, key))
        for i in range(BLOCK_SIZE):
            state[i] = sbox[state[i]]
        new = bytearray(BLOCK_SIZE)
        for i in range(BLOCK_SIZE):
            new[i] = state[perm[i]]
        state = new
    return bytes(state)

def encrypt(key, pt, rounds, sbox, perm):
    k1 = key[:3]
    k2 = key[3:]
    return fun(k2, fun(k1, pt, rounds, sbox, perm), rounds, sbox, perm)

# Try ROUNDS = 0 first (trivial - no encryption)
print("Testing ROUNDS=0...")
if kp_pt == kp_ct:
    print("ROUNDS=0 works (identity)")
else:
    print("ROUNDS=0 doesn't match known pair (expected)")

# With ROUNDS=1 and identity SBOX/PERM, fun(key, pt) = XOR(pt, md5(key))
# This is a meet-in-the-middle attack
# fun(k1, pt) = intermediate
# fun(k2, intermediate) = ct
# So we compute fun(k1, pt) for all k1, and fun_inv(k2, ct) for all k2
# For identity SBOX/PERM with 1 round: fun(k, x) = XOR(x, md5(k))
# fun_inv is the same as fun (XOR is its own inverse)

print("\nTesting ROUNDS=1, identity SBOX, identity PERM (meet-in-the-middle)...")

identity_sbox = list(range(256))
identity_perm = list(range(16))

# Precompute all md5(k) for 3-byte keys
# 2^24 = 16,777,216 keys - this might take a while
# Let's first try smaller key spaces

# Actually, the key is described as key[:3] and key[3:]
# Maybe the key is a short ASCII string?
# Let's try printable ASCII keys first

print("Trying printable ASCII keys (meet-in-the-middle with identity SBOX/PERM, ROUNDS=1)...")

# Build forward table: k1 -> fun(k1, kp_pt)
forward = {}
# Try all 3-byte combinations of printable ASCII
chars = string.printable.encode()

print(f"Key space per half: {len(chars)}^3 = {len(chars)**3}")

for c1 in chars:
    for c2 in chars:
        for c3 in chars:
            k = bytes([c1, c2, c3])
            h = md5(k).digest()
            intermediate = xor(kp_pt, h)
            forward[intermediate] = k

print(f"Built forward table: {len(forward)} entries")

# Check backward: for each k2, compute fun_inv(k2, kp_ct) = xor(kp_ct, md5(k2))
found = False
for c1 in chars:
    for c2 in chars:
        for c3 in chars:
            k2 = bytes([c1, c2, c3])
            h = md5(k2).digest()
            intermediate = xor(kp_ct, h)
            if intermediate in forward:
                k1 = forward[intermediate]
                key = k1 + k2
                # Verify
                test = encrypt(key, kp_pt, 1, identity_sbox, identity_perm)
                if test == kp_ct:
                    print(f"\nFOUND KEY: k1={k1}, k2={k2}, full_key={key}")
                    # Decrypt flag
                    # fun_inv for identity SBOX/PERM with 1 round is the same as fun
                    # Actually no, fun(k, x) = permute(sbox(xor(x, md5(k))))
                    # With identity sbox and perm: fun(k, x) = xor(x, md5(k))
                    # fun is its own inverse
                    
                    # To decrypt: flag_pt = fun_inv(k1, fun_inv(k2, flag_ct))
                    # = xor(xor(flag_ct, md5(k2)), md5(k1))
                    inter = xor(flag_ct, md5(k2).digest())
                    flag_pt = xor(inter, md5(k1).digest())
                    print(f"Flag bytes: {flag_pt.hex()}")
                    try:
                        print(f"Flag ASCII: {flag_pt.decode()}")
                    except:
                        print(f"Flag (raw): {flag_pt}")
                    found = True

if not found:
    print("No key found with printable ASCII + identity SBOX/PERM + ROUNDS=1")
    
    # Try all 256^3 byte combinations
    print("\nTrying full byte space (meet-in-the-middle with identity SBOX/PERM, ROUNDS=1)...")
    forward = {}
    for i in range(256**3):
        k = bytes([i >> 16, (i >> 8) & 0xFF, i & 0xFF])
        h = md5(k).digest()
        intermediate = xor(kp_pt, h)
        forward[intermediate] = k
    
    print(f"Built forward table: {len(forward)} entries")
    
    for i in range(256**3):
        k2 = bytes([i >> 16, (i >> 8) & 0xFF, i & 0xFF])
        h = md5(k2).digest()
        intermediate = xor(kp_ct, h)
        if intermediate in forward:
            k1 = forward[intermediate]
            key = k1 + k2
            test = encrypt(key, kp_pt, 1, identity_sbox, identity_perm)
            if test == kp_ct:
                print(f"\nFOUND KEY: k1={k1.hex()}, k2={k2.hex()}")
                inter = xor(flag_ct, md5(k2).digest())
                flag_pt = xor(inter, md5(k1).digest())
                print(f"Flag bytes: {flag_pt.hex()}")
                try:
                    print(f"Flag ASCII: {flag_pt.decode()}")
                except:
                    print(f"Flag (raw): {flag_pt}")
                found = True
                break
    
    if not found:
        print("No key found with full byte space either")
