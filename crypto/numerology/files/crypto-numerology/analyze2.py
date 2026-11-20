import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

# All samples have same PT with different (nonce, counter)
# The keystream = PT XOR CT for each sample
# We have 32 nonces x 32 counters = 1024 samples
# The key is "given" -- it's the known material

# The challenge says the name is "crypto-numerology"
# The init.sh references: KNOWN_KEY_ACTIVE_MATERIAL_HEX and KNOWN_KEY_STRUCTURE
# The key 000000005c5470020000000031f4727bf7d4923400000000e7bbb1c900000000
# Has 4 active words out of 8 -- this suggests the cipher uses the key differently

# Let's look at the keystreams more carefully
# Looking at first sample keystream:
# 49734f3d 00000000 00000000 00000000 dfbe3624 b8a8e004 00000000 62e8e5f6 
# 2bf399b7 00000000 ce776393 00000000 3e49734e 02000000 00000000 00000000
# Lots of zero words!

# For n0_c0:
s0 = samples[0]
pt = bytes.fromhex(s0['plaintext_hex'])
ct = bytes.fromhex(s0['ciphertext_hex'])
ks = bytes(a ^ b for a, b in zip(pt, ct))

print('Keystream n0_c0 as 4-byte LE words:')
ks_words = [struct.unpack_from('<I', ks, i)[0] for i in range(0, 64, 4)]
for i, w in enumerate(ks_words):
    print(f'  Word {i:2d}: {w:08x} ({w})')

print()
# Look for a pattern like ChaCha20 state
# ChaCha20 initial state:
# "expa" "nd 3" "2-by" "te k"
# key[0..3] key[4..7] key[8..11] key[12..15]
# key[16..19] key[20..23] key[24..27] key[28..31]
# counter   nonce[0]  nonce[1]  nonce[2]  <- for 96-bit nonce
# OR
# counter_lo counter_hi nonce[0] nonce[1] <- for 64-bit nonce (IETF)

# ChaCha20 constants
print('ChaCha20 sigma constants:')
sigma = b'expand 32-byte k'
sigma_words = [struct.unpack_from('<I', sigma, i)[0] for i in range(0, 16, 4)]
for i, w in enumerate(sigma_words):
    print(f'  Word {i}: {w:08x} ({sigma[i*4:i*4+4]})')

# Let's check if the keystream words match the output of a Salsa20/ChaCha20-like cipher
# The key has 4 non-zero words: w1, w3, w4, w6
key_words_int = [struct.unpack_from('<I', key, i)[0] for i in range(0, 32, 4)]
print()
print('Key words (LE):', [f'{w:08x}' for w in key_words_int])

# If the cipher uses a subset of key words...
# Active words are at positions 1, 3, 4, 6 = 4 words = 16 bytes = 128-bit key
# Maybe this is actually ChaCha20 with a 128-bit key using expanded key
# ChaCha20 with 128-bit key doubles it: key = k0 || k0 (or k0 || k1)

# Let's see if the active words at positions 1,3,4,6 form the actual 128-bit key
active_key = bytes(key[4:8] + key[12:16] + key[16:20] + key[24:28])  # words 1,3,4,6
print('Active key material:', active_key.hex())
# = 5c547002 31f4727b f7d49234 e7bbb1c9

# Perhaps the encryption is XOR with just the known key material?
# Or perhaps this is a custom "numerology" cipher

# Let's study differences between consecutive counter values
n0_xors = []
for s in [s for s in samples if s['sample_id'].startswith('sample_n0_')][:10]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    n0_xors.append(ks)
    
print()
print('Keystreams for n0 as 4-byte LE words (first 16 words):')
for i, ks in enumerate(n0_xors[:5]):
    words = [struct.unpack_from('<I', ks, j)[0] for j in range(0, 64, 4)]
    print(f'n0_c{i}:', [f'{w:08x}' for w in words])

# Check which words are zero across all samples for a given nonce
print()
print('Word positions that are always 0 for n0:')
always_zero_n0 = [True] * 16
for ks in n0_xors:
    words = [struct.unpack_from('<I', ks, j)[0] for j in range(0, 64, 4)]
    for p, w in enumerate(words):
        if w != 0:
            always_zero_n0[p] = False
print([i for i, z in enumerate(always_zero_n0) if z])

# Check across all nonces
print()
print('Checking zero patterns across all nonces...')
all_zero = [True] * 16
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    words = [struct.unpack_from('<I', ks, j)[0] for j in range(0, 64, 4)]
    for p, w in enumerate(words):
        if w != 0:
            all_zero[p] = False
print('Globally zero words:', [i for i, z in enumerate(all_zero) if z])
