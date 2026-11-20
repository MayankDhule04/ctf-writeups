import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

key_words_LE = [struct.unpack_from('<I', key, i)[0] for i in range(0, 32, 4)]
k1 = key_words_LE[1]
k3 = key_words_LE[3]
k4 = key_words_LE[4]
k6 = key_words_LE[6]

# The cipher is a custom stream cipher that generates keystream blocks
# Structure: keystream has fixed-zero words at positions 1,2,3,6,9,11,14,15
# Position 5, 7, 10 are constant (depend only on key)
# Positions 0, 4, 8, 12, 13 vary with nonce/counter

# The flag cipher has 42-byte ciphertext covering keystream words 0-10 (plus 2 bytes of 10)
# Word 13 (nonce info) is at byte 52-55, beyond the 42-byte scope

# Since w0, w4, w8 don't depend on nonce (shown by the analysis), 
# they only depend on the COUNTER value (which is SECRET)

# Let's look at this problem differently:
# The flag is nearly readable: ????w3_aRe_g0Nn@????_MY_FuncKee_????ey_!!}
# The structure suggests it's: CTF{w3_aRe_g0Nn@[??]_MY_FuncKee_[??]ey_!!}
# This is a 42-character flag: CTF{...38 chars...}

# Looking at the pattern:
# "w3_aRe_g0Nn@" = "we are gonna" leet speak
# "_MY_FuncKee_" = "_MY_FunKey_" or "_MY_Funky_"... wait
# "Kee_" + "ey_!!}" = "Key_!!}" -- so "FuncKey" -> FuncKey or "FunckKey"?
# Actually: "FuncKee_????ey_" -- Kee_ + ????ey_ = potentially "Key" + something

# Let me be more systematic about what the unknown 4-byte chunks could be
# pos 16-19: 4 bytes between "g0Nn@" and "_MY_"
# pos 32-35: 4 bytes between "FuncKee_" and "ey_!!"

# The ciphertext bytes at these positions
print('Flag CT bytes 16-19:', flag_ct[16:20].hex())
print('Flag CT bytes 32-35:', flag_ct[32:36].hex())

# Since we know the constant and variable keystream structure, 
# and we have 1024 (nonce,counter) pairs with known keystreams,
# we need to find the ACTUAL (nonce, counter) used for the flag

# The keystream for the flag must produce valid flag text
# The flag likely starts with "CTF{" and ends with "}"
# We've confirmed it ends with "!}" (bytes 40-41)

# For bytes 16-19 (word 4 position):
# flag_plain[16:20] = flag_ct[16:20] XOR ks_word4
# If word 4 for the flag's counter maps to some value from our samples...

# Let's collect ALL word4 values from the dataset and try each on flag_ct[16:20]
print()
print('Trying all word4 values from dataset on flag_ct[16:20]:')
seen_w4 = set()
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w4 = ks[16:20]
    if w4 in seen_w4:
        continue
    seen_w4.add(w4)
    decoded = bytes(a ^ b for a, b in zip(flag_ct[16:20], w4))
    if all(32 <= b <= 126 for b in decoded):
        print(f'  w4={w4.hex()} -> flag[16:20] = {decoded.decode()}')

print()
print('Trying all word8 values from dataset on flag_ct[32:36]:')
seen_w8 = set()
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w8 = ks[32:36]
    if w8 in seen_w8:
        continue
    seen_w8.add(w8)
    decoded = bytes(a ^ b for a, b in zip(flag_ct[32:36], w8))
    if all(32 <= b <= 126 for b in decoded):
        print(f'  w8={w8.hex()} -> flag[32:36] = {decoded.decode()}')

# Also try word0 for flag_ct[0:4]
print()
print('Trying all word0 values from dataset on flag_ct[0:4]:')
seen_w0 = set()
candidates = []
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w0 = ks[0:4]
    if w0 in seen_w0:
        continue
    seen_w0.add(w0)
    decoded = bytes(a ^ b for a, b in zip(flag_ct[0:4], w0))
    if all(32 <= b <= 126 for b in decoded):
        candidates.append((s['sample_id'], w0, decoded))
        print(f'  w0={w0.hex()} -> flag[0:4] = {decoded.decode()} (from {s["sample_id"]})')

# Combine results -- find samples where ALL three positions decode to printable chars
print()
print('=== BRUTE FORCE: Try all 1024 samples as candidate keystream ===')
partial_ks = bytearray(42)
w5_bytes = struct.pack('<I', (2*k1) & 0xFFFFFFFF)
w7_bytes = struct.pack('<I', (2*k3) & 0xFFFFFFFF)
w10_bytes = struct.pack('<I', (2*k6) & 0xFFFFFFFF)
partial_ks[20:24] = w5_bytes
partial_ks[28:32] = w7_bytes
partial_ks[40:42] = w10_bytes[:2]

seen_combos = set()
found_flags = []
for s in samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks_sample = bytes(a ^ b for a, b in zip(pt, ct))
    
    # word 0, 4, 8 from this sample's keystream
    combo = (ks_sample[0:4], ks_sample[16:20], ks_sample[32:36])
    if combo in seen_combos:
        continue
    seen_combos.add(combo)
    
    # Build full 42-byte keystream
    full_ks = bytearray(partial_ks)
    full_ks[0:4] = ks_sample[0:4]
    full_ks[16:20] = ks_sample[16:20]
    full_ks[32:36] = ks_sample[32:36]
    
    # Decrypt
    plain = bytes(a ^ b for a, b in zip(flag_ct, bytes(full_ks)))
    
    # Check validity: all printable ASCII, starts with CTF{, ends with }
    if all(32 <= b <= 126 for b in plain) and plain.endswith(b'}'):
        print(f'  CANDIDATE ({s["sample_id"]}): {plain.decode()}')
        found_flags.append((s['sample_id'], plain.decode()))

if not found_flags:
    print('No valid flags found from direct sample keystreams.')
    print()
    print('This means the secret counter was NOT one of the 32 sampled values.')
    print('Need to reverse-engineer or search for the secret counter.')

# The 32 counter variations and 32 nonce variations in the dataset 
# were DIFFERENT nonce/counter values from the flag's nonce/counter
# We need to figure out the pattern to extrapolate

# From w12 patterns observed:
# n0_c0: w12=4e73493e
# n0_c1: w12=4d73494f  
# The difference: 4e73493e - 4d73494f = 00ffff ef? Let me check
c0_w12 = 0x4e73493e
c1_w12 = 0x4d73494f
print()
print(f'w12 difference c0→c1: {(c1_w12 - c0_w12) & 0xFFFFFFFF:08x}')

# collect all w12 values for n0
n0_samples = sorted([s for s in samples if s['sample_id'].startswith('sample_n0_')],
                    key=lambda s: int(s['sample_id'].split('_c')[1]))
w12_values = []
w0_values = []
for s in n0_samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w12_values.append(struct.unpack_from('<I', ks, 48)[0])
    w0_values.append(struct.unpack_from('<I', ks, 0)[0])

print()
print('w12 sequence for n0 (first 10):')
for i, w in enumerate(w12_values[:10]):
    print(f'  c{i}: {w:08x}')
print()
print('Differences in w12 sequence:')
for i in range(1, min(10, len(w12_values))):
    diff = (w12_values[i] - w12_values[i-1]) & 0xFFFFFFFF
    print(f'  c{i-1}→c{i}: {diff:08x} = {diff}')
