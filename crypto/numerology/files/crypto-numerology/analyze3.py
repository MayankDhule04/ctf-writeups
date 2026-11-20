import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

# Keystream word positions that are ALWAYS zero: [1, 2, 3, 6, 9, 11, 14, 15]
# Keystream word positions that are NON-zero: [0, 4, 5, 7, 8, 10, 12, 13]

# This means the cipher only affects 8 out of 16 words (32 bytes out of 64)
# The other 8 words remain same as plaintext → XOR = 0

# ChaCha20 16-word state layout:
# [0]  [1]  [2]  [3]   <- constants: "expa", "nd 3", "2-by", "te k"
# [4]  [5]  [6]  [7]   <- key words 0-3
# [8]  [9]  [10] [11]  <- key words 4-7
# [12] [13] [14] [15]  <- counter, nonce0, nonce1, nonce2

# Changed words (non-zero keystream): 0, 4, 5, 7, 8, 10, 12, 13
# ZEro words: 1, 2, 3, 6, 9, 11, 14, 15

# In ChaCha20, state position → real mapping: 
# Pos 4,5,6,7 = key[0..3]
# Pos 8,9,10,11 = key[4..7]
# Key word positions (via LE): [0..3] = 00000000, 0270545c, 00000000, 7b72f431
#                              [4..7] = 3492d4f7, 00000000, c9b1bbe7, 00000000

# Key words (LE): {1: 0270545c, 3: 7b72f431, 4: 3492d4f7, 6: c9b1bbe7}
# Key zeros at positions: 0, 2, 5, 7

# If this is a Salsa20/ChaCha20 variant, positions in state that correspond to
# non-zero key words would be affected by mixing...

# But there's a simpler hypothesis: the cipher is ADDITIVE/XOR with a keystream
# generated purely from (nonce, counter, key), and the keystream itself has
# fixed zero words.

# Let's think about the structure differently:
# Keystream non-zero words at positions: [0, 4, 5, 7, 8, 10, 12, 13]
# Keystream zero words at positions:     [1, 2, 3, 6, 9, 11, 14, 15]

# The active key words (LE) are at positions 1, 3, 4, 6 in the key
# Key position 1 → 0270545c (non-zero) → state position 5 (key[1])
# Key position 3 → 7b72f431 (non-zero) → state position 7 (key[3])
# Key position 4 → 3492d4f7 (non-zero) → state position 8 (key[4])
# Key position 6 → c9b1bbe7 (non-zero) → state position 10 (key[6])

# Zero key words at positions 0, 2, 5, 7:
# Key position 0 → 00000000 → state position 4 (key[0])
# Key position 2 → 00000000 → state position 6 (key[2])
# Key position 5 → 00000000 → state position 9 (key[5])
# Key position 7 → 00000000 → state position 11 (key[7])

# WAIT: in ChaCha20 with 32-byte key:
# State words 4-11 = key words 0-7
# Key word 0 (pos4): ZERO → but keystream word 4 is NON-ZERO (has data!)
# Key word 1 (pos5): ACTIVE → keystream word 5 is NON-ZERO ✓
# Key word 2 (pos6): ZERO → keystream word 6 is ZERO ✓
# Key word 3 (pos7): ACTIVE → keystream word 7 is NON-ZERO ✓
# Key word 4 (pos8): ACTIVE → keystream word 8 is NON-ZERO ✓
# Key word 5 (pos9): ZERO → keystream word 9 is ZERO ✓
# Key word 6 (pos10): ACTIVE → keystream word 10 is NON-ZERO ✓
# Key word 7 (pos11): ZERO → keystream word 11 is ZERO ✓
# Word 12 = counter → NON-ZERO ✓
# Word 13 = nonce[0] → NON-ZERO ✓  
# Word 14 = nonce[1] → ZERO ✓ (target nonce must have zero here)
# Word 15 = nonce[2] → ZERO ✓ (target nonce must have zero here)

# KEY INSIGHT: key word 0 maps to state position 4, yet keystream position 4 IS non-zero!
# This means the cipher is NOT simply placing key material at positions 4-11
# OR the "zero key" actually influences pos 4 weakly via rotations

# Let's look more carefully at word 4 values and see if they correlate with counter
print('Word 4 (non-zero) values across n0:')
n0_samples = [s for s in samples if s['sample_id'].startswith('sample_n0_')]
for s in n0_samples[:10]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w0 = struct.unpack_from('<I', ks, 0)[0]   # word 0
    w4 = struct.unpack_from('<I', ks, 16)[0]  # word 4
    w5 = struct.unpack_from('<I', ks, 20)[0]  # word 5
    w7 = struct.unpack_from('<I', ks, 28)[0]  # word 7
    w8 = struct.unpack_from('<I', ks, 32)[0]  # word 8
    w10 = struct.unpack_from('<I', ks, 40)[0] # word 10
    w12 = struct.unpack_from('<I', ks, 48)[0] # word 12
    w13 = struct.unpack_from('<I', ks, 52)[0] # word 13
    print(f'  {s["sample_id"]}: w0={w0:08x} w4={w4:08x} w5={w5:08x} w7={w7:08x} w8={w8:08x} w10={w10:08x} w12={w12:08x} w13={w13:08x}')

print()
print('Word 4 (non-zero) values across n0 with counter index:')
for idx, s in enumerate(n0_samples):
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w4 = struct.unpack_from('<I', ks, 16)[0]
    w5 = struct.unpack_from('<I', ks, 20)[0]
    w8 = struct.unpack_from('<I', ks, 32)[0]
    w10 = struct.unpack_from('<I', ks, 40)[0]
    # Are any of these related to constants (addition with counter)?
    active_key_LE = [0x0270545c, 0x7b72f431, 0x3492d4f7, 0xc9b1bbe7]
    # w5 - key[1]? 
    diff5 = (w5 - active_key_LE[0]) & 0xFFFFFFFF
    diff8 = (w8 - active_key_LE[2]) & 0xFFFFFFFF
    diff10 = (w10 - active_key_LE[3]) & 0xFFFFFFFF
    print(f'  c{idx:2d}: w4={w4:08x} w5={w5:08x}(diff={diff5:08x}) w8={w8:08x}(diff={diff8:08x}) w10={w10:08x}(diff={diff10:08x})')

# CHeck if this is just ADDITION (no rotation/mixing)
# If keystream = initial_state + initial_state (salsa/chacha final step adds initial to output)
# Then e.g.: output_word4 = key[0] + (something from mixing)
# But if key[0]=0, output_word4 = just the mixed result
# This is getting complex. Let's try a simpler hypothesis:
# Maybe this cipher is: encrypt(pt) = pt XOR keystream
# where keystream only covers 8 words and the other 8 pass through unchanged
# The 8 active positions suggest this might be a 256-bit (32-byte) stream cipher
# operating on 32-byte blocks, despite the 64-byte message
print()
print('=== IMPORTANT INSIGHT ===')
print('Active keystream at words: 0, 4, 5, 7, 8, 10, 12, 13')
print('These are 8 words = 32 bytes scattered in a 64-byte block')
print()
# Check if the active bytes in cipher correspond to specific byte ranges of the flag ct
# Flag ct is 42 bytes. The PT XOR key = cipher for 64 bytes, but flag is shorter
# How is the flag ct structured?
print('Flag CT length:', len(flag_ct))
print('Flag CT hex:', flag_ct.hex())
print()

# Different approach: the "key" is the ONLY thing we have  
# The challenge says "I gave you the key to decrypt the flag"
# Maybe it's a direct XOR? Let's try XORing keystream from sample with flag

# For the FLAG, we need to know what nonce and counter were used
# The XOR-keystream from n0_c0 shows word13 = 00000002 (counter=2 if little-endian)
# Actually word12 is the counter in ChaCha20 IETF
# Let's look at the counter progression
print('Looking for counter values in keystream word 12 and 13:')
for s in n0_samples[:10]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w12 = struct.unpack_from('<I', ks, 48)[0]
    w13 = struct.unpack_from('<I', ks, 52)[0]
    print(f'  {s["sample_id"]}: w12={w12:08x} ({w12}) w13={w13:08x} ({w13})')
