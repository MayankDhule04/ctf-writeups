import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

# Observations so far:
# 1. All samples use the SAME plaintext, only (nonce, counter) vary
# 2. Keystream = PT XOR CT
# 3. Keystream has 8 globally zero words at positions 1,2,3,6,9,11,14,15
# 4. The non-zero words at 5 and 10 relate to key_words[1] and key_words[6]:
#    w5_ks = 2 * key_word[1] (mod 2^32) — constant across all samples
#    w10_ks = 2 * key_word[6] (mod 2^32) — constant across all samples
# 5. Word 13 = 2 (always for n0) — this might be 2 * nonce_word
# 6. Words 0, 4, 7, 8, 12 vary between samples

# This matches a CUSTOM stream cipher that is NOT standard ChaCha20/Salsa20
# The cipher uses (nonce, counter) to influence words 0, 4, 7, 8, 12

# Looking at key structure more carefully:
# Key words (LE): [0, k1, 0, k3, k4, 0, k6, 0]
# Non-zero: k1=0270545c, k3=7b72f431, k4=3492d4f7, k6=c9b1bbe7

# Keystream active words (non-zero): 0, 4, 5, 7, 8, 10, 12, 13
# Constant words (across all samples): 5(=2*k1), 10(=2*k6), 13(varies by nonce)
# Varying words (across samples): 0, 4, 7, 8, 12

# Let's map key words to keystream words that are constants:
# k1 (position 1 in key) → w5 in keystream = 2*k1
# k6 (position 6 in key) → w10 in keystream = 2*k6
# k3 (position 3 in key) → w7 in keystream? Let's check...
# k4 (position 4 in key) → w8 in keystream? Let's check...

# Observe w7 for n0:
s0 = samples[0]
pt = bytes.fromhex(s0['plaintext_hex'])
ct = bytes.fromhex(s0['ciphertext_hex'])
obs_ks_n0c0 = bytes(a ^ b for a, b in zip(pt, ct))
obs_words = [struct.unpack_from('<I', obs_ks_n0c0, i)[0] for i in range(0, 64, 4)]

key_words_LE = [struct.unpack_from('<I', key, i)[0] for i in range(0, 32, 4)]
k1 = key_words_LE[1]
k3 = key_words_LE[3]
k4 = key_words_LE[4]
k6 = key_words_LE[6]

print('Key words: k1=%08x k3=%08x k4=%08x k6=%08x' % (k1, k3, k4, k6))
print()
print('Non-zero keystream words for n0_c0:')
for i, w in enumerate(obs_words):
    if w != 0:
        # Check relationship to key words
        print(f'  w{i:2d}={w:08x}: 2*k1={2*k1 & 0xFFFFFFFF:08x} 2*k3={2*k3 & 0xFFFFFFFF:08x} 2*k4={2*k4 & 0xFFFFFFFF:08x} 2*k6={2*k6 & 0xFFFFFFFF:08x}')

# Check if w7 = k3 + something, w8 = k4 + something
# For n0_c0: w7 = f6e5e862, w8 = b799f32b
print()
print(f'w7 = {obs_words[7]:08x}')
print(f'k3 = {k3:08x}')
print(f'w7 - k3 = {(obs_words[7] - k3) & 0xFFFFFFFF:08x}')
print(f'w7 - 2*k3 = {(obs_words[7] - 2*k3) & 0xFFFFFFFF:08x}')
print(f'2*k3 - w7 = {(2*k3 - obs_words[7]) & 0xFFFFFFFF:08x}')
print()
print(f'w8 = {obs_words[8]:08x}')
print(f'k4 = {k4:08x}')
print(f'w8 - k4 = {(obs_words[8] - k4) & 0xFFFFFFFF:08x}')
print(f'w8 - 2*k4 = {(obs_words[8] - 2*k4) & 0xFFFFFFFF:08x}')

# Check w7 consistency across nonces for n0
n0_samples = [s for s in samples if s['sample_id'].startswith('sample_n0_')]
print()
print('w7 consistency across n0 counters:')
for s in n0_samples[:5]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w7 = struct.unpack_from('<I', ks, 28)[0]
    print(f'  {s["sample_id"]}: w7={w7:08x}')

# Does w7 change between nonces?
print()
print('w7 for n0 vs n1:')
n1_samples = [s for s in samples if s['sample_id'].startswith('sample_n1_')]
for s in n0_samples[:3]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w7 = struct.unpack_from('<I', ks, 28)[0]
    print(f'  n0_{s["sample_id"].split("_")[2]}: w7={w7:08x}')
for s in n1_samples[:3]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w7 = struct.unpack_from('<I', ks, 28)[0]
    print(f'  n1_{s["sample_id"].split("_")[2]}: w7={w7:08x}')

# Is w7 constant across ALL 1024 samples?
all_w7 = set()
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w7 = struct.unpack_from('<I', ks, 28)[0]
    all_w7.add(w7)
print()
print('All unique w7 values:', [f'{w:08x}' for w in all_w7])
print('Count:', len(all_w7))

# Also check w0, w4, w12 patterns 
print()
print('Looking for counter in w12:')
for s in n0_samples[:8]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w12 = struct.unpack_from('<I', ks, 48)[0]
    w0 = struct.unpack_from('<I', ks, 0)[0]
    w4 = struct.unpack_from('<I', ks, 16)[0]
    w8 = struct.unpack_from('<I', ks, 32)[0]
    # Counter might be encoded differently
    ctr_idx = int(s['sample_id'].split('_c')[1])
    print(f'  {s["sample_id"]} (ctr_idx={ctr_idx:2d}): w0={w0:08x} w4={w4:08x} w8={w8:08x} w12={w12:08x}')
