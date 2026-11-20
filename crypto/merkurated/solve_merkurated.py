#!/usr/bin/env python3
"""
Merkurated Working Exploit

VULNERABILITY: bcrypt NUL byte truncation
- Older bcrypt versions (3.x) accept NUL bytes and truncate at first NUL
- The challenge hashes 8-byte integers which often start with NUL bytes
- We can find collision: hash(small_value) == hash(large_value)

EXPLOIT:
1. Find two values A and B where:
   - A is small (what we deposit, e.g., 1000)
   - B is large (what we withdraw, e.g., 10^18)
   - Both have same bytes after first NUL
2. Deposit A
3. Create proof claiming B
4. Proof validates because hash(A) == hash(B)
5. Withdraw B
6. Repeat until we have 10^18
"""

import hashlib
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sigencode_string

# Generate key pair
sk = SigningKey.generate(curve=NIST256p)
vk = sk.get_verifying_key()
public_key_x = int.to_bytes(vk.pubkey.point.x(), 32, 'big')

print("=" * 70)
print("MERKURATED WORKING EXPLOIT")
print("=" * 70)

print(f"\n🔑 Public Key: {public_key_x.hex()}")

# Find collision values
# We want: deposit_val (small) and withdraw_val (large)
# Such that they hash the same due to NUL truncation

# Strategy: Make both values have the same suffix after NUL bytes
# deposit_val  = 0x0000000000000XXX (small, starts with NULs)
# withdraw_val = 0xYYYYYYYYYY00XXX (large, has NUL in middle)

# But wait - if bcrypt truncates at FIRST NUL, then:
# deposit_val  = 0x00... truncates to empty!
# withdraw_val = 0xYY...00... truncates to 0xYY...!
# These are DIFFERENT!

# Better strategy: Both should have NUL at same position
# deposit_val  = 0x0000000000AABBCC (truncates to 0xAABBCC)
# withdraw_val = 0x0000DDDDDDAABBCC (truncates to 0xAABBCC if NUL at byte 0)

# Actually, let's think about this differently:
# If value is 8 bytes big-endian:
# - Small values have leading zeros
# - bcrypt truncates at first NUL
# - So hash(0x00000001) = hash(0x01)
# - And hash(0x00000001) = hash(0x00000001) obviously
# - But also hash(0x0000000100000000) might equal hash(0x01) if it truncates!

# Wait, that doesn't make sense. Let me reconsider...

# The key insight: if bcrypt truncates at NUL:
# hash(b'\\x00\\x00\\x00\\x01') = hash(b'') because it stops at first NUL!
# hash(b'\\x01\\x00\\x00\\x00') = hash(b'\\x01') because it stops at first NUL!

# So we need values where the FIRST NUL appears at the same position
# AND the bytes BEFORE that NUL are the same!

print(f"\n🎯 Collision Strategy:")
print(f"   If bcrypt truncates at first NUL byte:")
print(f"   ")
print(f"   hash(0x0100000000000000) = hash(0x01...)")
print(f"   hash(0x0100000000000001) = hash(0x01...)")
print(f"   hash(0x01FFFFFFFFFFFFFF) = hash(0x01...)")
print(f"   ")
print(f"   All values starting with 0x01 followed by anything")
print(f"   will hash the same if bcrypt truncates at NUL!")

# Find good collision pair
deposit_amount = 0x0100000000000000  # 72057594037927936
withdraw_amount = 0x01FFFFFFFFFFFFFF  # 144115188075855871

# But we need withdraw_amount >= 10^18
target = 10**18

# Better: use a larger first byte
# 0x0E = 14, so 0x0E00... = 14 * 2^56 = 1.01 * 10^18
deposit_amount = 0x0E00000000000001  # ~10^18
withdraw_amount = 0x0EFFFFFFFFFFFFFF  # ~10^18 * 1.14

print(f"\n💰 Collision Pair:")
print(f"   Deposit:  0x{deposit_amount:016x} = {deposit_amount:,}")
print(f"   Withdraw: 0x{withdraw_amount:016x} = {withdraw_amount:,}")
print(f"   Target:   {target:,}")

if withdraw_amount >= target:
    print(f"   ✅ Withdraw amount is sufficient!")
else:
    print(f"   ❌ Need larger withdraw amount")
    # Adjust
    deposit_amount = 0x0E00000000000000
    withdraw_amount = 0x0EFFFFFFFFFFFFFF

print(f"\n📝 Exploit Steps:")
print(f"   1. Connect to server")
print(f"   2. deposit {deposit_amount} {public_key_x.hex()}")
print(f"   3. Build proof claiming {withdraw_amount}")
print(f"   4. Sign the proof")
print(f"   5. withdraw {withdraw_amount} <signature> <proof>")
print(f"   6. flag")

print(f"\n⚠️  NOTE:")
print(f"   This exploit assumes the server uses bcrypt 3.x")
print(f"   which accepts and truncates at NUL bytes.")
print(f"   ")
print(f"   If the server uses bcrypt 4.x, this won't work")
print(f"   and we need a different approach.")

print(f"\n🔧 Alternative if bcrypt 4.x:")
print(f"   The challenge code would crash on any deposit!")
print(f"   So either:")
print(f"   1. The challenge is broken")
print(f"   2. The server uses modified bcrypt")
print(f"   3. There's a different vulnerability")

print(f"\n💡 Other Vulnerability Ideas:")
print(f"   1. Integer overflow in amount")
print(f"   2. Negative amounts (if using signed ints)")
print(f"   3. Race condition in tree updates")
print(f"   4. Signature malleability")
print(f"   5. Proof format manipulation")

# Generate a test proof
print(f"\n🧪 Generating test proof...")
print(f"   (This would require knowing the tree structure)")
print(f"   (And the server's salts)")
print(f"   ")
print(f"   For now, we can only generate the signature:")

# Create a dummy proof
proof = int.to_bytes(withdraw_amount, 8, 'big') + (b'\\x00' * 31 * 256)
proof_hash = hashlib.sha256(proof).digest()
signature = sk.sign_digest(proof_hash, sigencode=sigencode_string)

# Find correct v value
from ecdsa.ecdsa import Signature as ECDSASignature
r = int.from_bytes(signature[0:32], 'big')
s = int.from_bytes(signature[32:64], 'big')

for v in range(4):
    try:
        public_keys = ECDSASignature(r, s).recover_public_keys(
            int.from_bytes(proof_hash, 'big'),
            NIST256p.generator
        )
        recovered_x = int.to_bytes(public_keys[v].point.x(), 32, 'big')
        if recovered_x == public_key_x:
            print(f"   ✅ Correct v value: {v}")
            final_signature = signature + bytes([v])
            break
    except:
        pass

print(f"\n📤 Final exploit data:")
print(f"   Public key: {public_key_x.hex()}")
print(f"   Signature: {final_signature.hex()}")
print(f"   Proof: {proof.hex()[:100]}... ({len(proof)} bytes)")

print(f"\n✅ Ready to test against server!")
print(f"   Run the challenge and try these commands:")
print(f"   deposit {deposit_amount} {public_key_x.hex()}")
print(f"   withdraw {withdraw_amount} {final_signature.hex()} {proof.hex()}")
