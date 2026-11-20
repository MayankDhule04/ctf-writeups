import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

key_words_LE = [struct.unpack_from('<I', key, i)[0] for i in range(0, 32, 4)]
k1 = key_words_LE[1]  # 0270545c
k3 = key_words_LE[3]  # 7b72f431
k6 = key_words_LE[6]  # c9b1bbe7

# Summary of keystream structure:
# word 0: varies (nonce + counter dependent)
# word 1: 0 (always)
# word 2: 0 (always)
# word 3: 0 (always)
# word 4: varies (nonce + counter dependent)
# word 5: 2*k1 = 04e0a8b8 (constant!)
# word 6: 0 (always)
# word 7: 2*k3 = f6e5e862 (constant!)
# word 8: varies (nonce + counter dependent)
# word 9: 0 (always)
# word 10: 2*k6 = 936377ce (constant!)
# word 11: 0 (always)
# word 12: varies (nonce + counter dependent)
# word 13: varies (nonce dependent, constant per nonce)
# word 14: 0 (always)
# word 15: 0 (always)

# The flag ciphertext is 42 bytes -- that only covers the first 42 bytes
# of the keystream = the first ~10.5 words
# So the flag keystream bytes involved are:
# bytes 0-3: word 0 (varies)
# bytes 4-7: word 1 = 00000000 (constant zero)
# bytes 8-11: word 2 = 00000000 (constant zero)
# bytes 12-15: word 3 = 00000000 (constant zero)
# bytes 16-19: word 4 (varies)
# bytes 20-23: word 5 = 04e0a8b8 (constant!)
# bytes 24-27: word 6 = 00000000 (constant zero)
# bytes 28-31: word 7 = f6e5e862 (constant!)
# bytes 32-35: word 8 (varies)
# bytes 36-39: word 9 = 00000000 (constant zero)
# bytes 40-41: first 2 bytes of word 10 = ce, 77 (from 936377ce LE = ce, 77, 63, 93)

# For the flag, we know bytes 4-15 of keystream are all 0x00
# And bytes 20-23 = c8 a8 b8 04 (04e0a8b8 in LE = b8 a8 e0 04)
# Wait: 04e0a8b8 in LE means word stored as b8 a8 e0 04? No:
# struct.pack('<I', 0x04e0a8b8) = b'\xb8\xa8\xe0\x04'
# So bytes 20-23 of keystream = b8 a8 e0 04

# And bytes 28-31 (word 7) = 62 e8 e5 f6 (from f6e5e862 LE)
# And bytes 36-39 (word 9) = 00 00 00 00
# And bytes 40-41 (first 2 of word 10) = ce 77 (from 936377ce LE = ce 77 63 93)

# To find the flag, we need word0, word4, word8 for the secret (nonce, counter)
# These are the only varying words in the first 42 bytes of keystream

# Let's look at the complete 64-byte keystream to understand the structure
# For the flag, the 42-byte CT encrypts 42 bytes of the flag plaintext
# Without knowing (nonce, counter) we can't decrypt word0, word4, word8 positions

# BUT: the challenge says "I gave you the key to decrypt the flag, is that enough?"
# The key includes info about the secret nonce AND counter!
# Look at init.sh: the key = KNOWN_KEY_ACTIVE_MATERIAL_HEX + formatting
# The init.sh passes --secret_target_nonce_hex and --secret_target_counter_int
# These are the SECRET nonce/counter used to encrypt the flag!

# The flag ct is 42 bytes. The constant parts of the keystream allow us to decrypt
# bytes 4-15 (words 1-3 = 0), bytes 20-23 (word 5), bytes 24-27 (word 6 = 0)
# bytes 28-31 (word 7), bytes 36-39 (word 9 = 0), bytes 40-41 (first 2 of word 10)

# The flag is CTF{...} format with 42 bytes total
# Let's decrypt the constant parts first

w5_bytes = struct.pack('<I', (2*k1) & 0xFFFFFFFF)  # bytes 20-23
w7_bytes = struct.pack('<I', (2*k3) & 0xFFFFFFFF)  # bytes 28-31
w10_bytes = struct.pack('<I', (2*k6) & 0xFFFFFFFF)  # bytes 40-43 (only 40-41 needed)

print('w5 bytes:', w5_bytes.hex())  # = b8 a8 e0 04
print('w7 bytes:', w7_bytes.hex())  # = 62 e8 e5 f6
print('w10 bytes:', w10_bytes.hex())  # = ce 77 63 93

# Build partial keystream (42 bytes)
partial_ks = bytearray(42)
# Bytes 4-15: word 1,2,3 = 0 (already zero)
# Bytes 20-23: word 5
partial_ks[20:24] = w5_bytes
# Bytes 24-27: word 6 = 0 (already zero)
# Bytes 28-31: word 7
partial_ks[28:32] = w7_bytes
# Bytes 36-39: word 9 = 0 (already zero)
# Bytes 40-41: first 2 bytes of word 10
partial_ks[40:42] = w10_bytes[:2]

print()
print('Partial keystream (42 bytes):', partial_ks.hex())
print('Flag CT (42 bytes):', flag_ct.hex())

# Partially decrypt
partial_flag = bytes(a ^ b for a, b in zip(flag_ct, bytes(partial_ks)))
print()
print('Partial flag (XOR with known keystream parts):')
print(partial_flag.hex())
print()
print('Partial flag as text (? where unknown):')
result = []
unknown_positions = set(range(4)) | set(range(16, 20)) | set(range(32, 36))  # word0, word4, word8 positions
for i, (c, k) in enumerate(zip(flag_ct, bytes(partial_ks))):
    if i in unknown_positions:
        result.append('?')
    else:
        result.append(chr(c ^ k) if 32 <= (c ^ k) <= 126 else f'\\x{c^k:02x}')
print(''.join(result))

# Now let's see what we know:
# Bytes 0-3 (word 0): unknown - depends on secret nonce+counter
# Bytes 4-15 (words 1-3): XOR with 0 = flag bytes direct (no encryption!)
# Wait -- keystream bytes 4-15 = 0, so CT[4-15] = PT[4-15] XOR 0 = PT[4-15]
print()
print('Flag bytes 4-15 (no encryption, directly readable):')
flag_bytes_4_15 = flag_ct[4:16]
print('  hex:', flag_bytes_4_15.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_4_15))

# Bytes 20-23 (word 5): decrypt with w5_bytes
flag_bytes_20_23 = bytes(a ^ b for a, b in zip(flag_ct[20:24], w5_bytes))
print()
print('Flag bytes 20-23 (decrypted with 2*k1):')
print('  hex:', flag_bytes_20_23.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_20_23))

# Bytes 24-27 (word 6): no encryption
flag_bytes_24_27 = flag_ct[24:28]
print()
print('Flag bytes 24-27 (no encryption):')
print('  hex:', flag_bytes_24_27.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_24_27))

# Bytes 28-31 (word 7): decrypt with w7_bytes
flag_bytes_28_31 = bytes(a ^ b for a, b in zip(flag_ct[28:32], w7_bytes))
print()
print('Flag bytes 28-31 (decrypted with 2*k3):')
print('  hex:', flag_bytes_28_31.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_28_31))

# Bytes 36-39 (word 9): no encryption  
flag_bytes_36_39 = flag_ct[36:40]
print()
print('Flag bytes 36-39 (no encryption):')
print('  hex:', flag_bytes_36_39.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_36_39))

# Bytes 40-41 (first 2 of word 10): decrypt
flag_bytes_40_41 = bytes(a ^ b for a, b in zip(flag_ct[40:42], w10_bytes[:2]))
print()
print('Flag bytes 40-41 (decrypted with 2*k6 first 2 bytes):')
print('  hex:', flag_bytes_40_41.hex())
print('  text:', ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in flag_bytes_40_41))

# Now let's try to figure out word 0 by looking at the nonce structure in the dataset
# The challenge name says "crypto-numerology" and the key has 4 active, 4 zero words
# The "secret_target_nonce_hex" is embedded in some way
# The dataset has 32 nonces x 32 counters
# Let me look at w13 across different nonces to understand nonce encoding
print()
print('w13 values across nonce groups (should encode nonce):')
nonces = sorted(set(s['sample_id'].split('_')[1] for s in samples), key=lambda x: int(x[1:]))
for n in nonces[:10]:
    s = next(s for s in samples if s['sample_id'].startswith(f'sample_{n}_c0'))
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w13 = struct.unpack_from('<I', ks, 52)[0]
    print(f'  nonce {n}: w13={w13:08x} ({w13})')

# w13 for nonce 0 = 00000002 = 2 in decimal
# Check if this is just the nonce index * 2 or something else
print()
print('Looking for nonce in w0 pattern:')
for n in nonces[:5]:
    s0 = next(s for s in samples if s['sample_id'].startswith(f'sample_{n}_c0'))
    s1 = next(s for s in samples if s['sample_id'].startswith(f'sample_{n}_c1'))
    pt0 = bytes.fromhex(s0['plaintext_hex'])
    ct0 = bytes.fromhex(s0['ciphertext_hex'])
    ks0 = bytes(a ^ b for a, b in zip(pt0, ct0))
    w0_c0 = struct.unpack_from('<I', ks0, 0)[0]
    w13_c0 = struct.unpack_from('<I', ks0, 52)[0]
    pt1 = bytes.fromhex(s1['plaintext_hex'])
    ct1 = bytes.fromhex(s1['ciphertext_hex'])
    ks1 = bytes(a ^ b for a, b in zip(pt1, ct1))
    w0_c1 = struct.unpack_from('<I', ks1, 0)[0]
    w12_c0 = struct.unpack_from('<I', ks0, 48)[0]
    w12_c1 = struct.unpack_from('<I', ks1, 48)[0]
    print(f'  nonce {n}: w0_c0={w0_c0:08x} w0_c1={w0_c1:08x} w12_c0={w12_c0:08x} w12_c1={w12_c1:08x} w13={w13_c0:08x}')
