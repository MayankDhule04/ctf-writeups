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
k6 = key_words_LE[6]

# CRITICAL INSIGHT: w0_c0 = w0_c0 for ALL nonces (same counter index = same w0!)
# This means word 0 depends ONLY on the counter, not the nonce
# Similarly w12_c0 is the same for all nonces

# We have 32 different counter values (c0..c31) in the dataset
# For each counter index, we know what w0 and w12 values are (from n0 samples)

# The flag was encrypted with a SECRET nonce and SECRET counter
# We need to find the keystream for that (nonce, counter)
# For the constant words: already computed
# For w0: we know it equals the w0 at the same counter index
# For w4: we know it equals the w4 at the same counter index
# For w8: we know it equals the w8 at the same counter index
# For w12: we know it equals the w12 at the same counter index
# For w13: this depends on nonce only!

# Strategy: 
# From the known plaintext at byte positions 0-3, we can determine the keystream word 0
# The flag starts with CTF{ (standard CTF flag format)
# flag[0:4] = CT{F or CTF{ 

# Let's try to brute-force word 0 by checking if the decrypted bytes make sense
# flag[0:4] should be "CTF{"
expected_prefix = b'CTF{'

# What is flag_ct[0:4] XOR expected_prefix?
ks_w0_from_prefix = bytes(a ^ b for a, b in zip(flag_ct[0:4], expected_prefix))
w0_from_prefix = struct.unpack('<I', ks_w0_from_prefix)[0]
print(f'If flag starts with "CTF{{": w0 should be {w0_from_prefix:08x}')

# Check which counter index has this w0 value
n0_samples = [s for s in samples if s['sample_id'].startswith('sample_n0_')]
print()
print('Searching for matching w0 across all counter values:')
for s in n0_samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    w0 = struct.unpack_from('<I', ks, 0)[0]
    if w0 == w0_from_prefix:
        print(f'  MATCH! {s["sample_id"]}: w0={w0:08x}')
        
        # Now decrypt the full flag using this sample's keystream
        # (the keystream only differs at w13 for different nonces)
        full_ks = bytes(a ^ b for a, b in zip(pt, ct))
        
        # For the flag, we need up to 42 bytes of keystream
        # The flag keystream differs from sample keystream only at word 13 (if secret nonce != n0)
        # But bytes 52-55 (word 13) are beyond the 42 bytes of flag ct, so it doesn't matter!
        # The flag is only 42 bytes, so we only need keystream[0:42]
        # Keystream[0:42] doesn't include word 13 (which is at bytes 52-55)!
        
        print()
        print('Flag keystream (first 42 bytes from matching sample):')
        print(full_ks[:42].hex())
        
        flag_plain = bytes(a ^ b for a, b in zip(flag_ct, full_ks[:42]))
        print()
        print('Decrypted flag:')
        print(flag_plain.hex())
        print(flag_plain.decode('utf-8', errors='replace'))
        break

# Also try: what if flag doesn't start with "CTF{" but something else?
# Let's also check "ctf{" 
expected_prefix2 = b'ctf{'
ks_w0_2 = bytes(a ^ b for a, b in zip(flag_ct[0:4], expected_prefix2))
w0_2 = struct.unpack('<I', ks_w0_2)[0]
print()
print(f'If flag starts with "ctf{{": w0 should be {w0_2:08x}')
for s in n0_samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct_s = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct_s))
    w0 = struct.unpack_from('<I', ks, 0)[0]
    if w0 == w0_2:
        print(f'  MATCH! {s["sample_id"]}')
        flag_plain = bytes(a ^ b for a, b in zip(flag_ct, ks[:42]))
        print('Decrypted flag:', flag_plain.decode('utf-8', errors='replace'))
        break

# Now let's also verify by checking the FULL partial flag we already know
# We know: ????w3_aRe_g0Nn@????_MY_FuncKee_????ey_!!}
# Expected CTF flag format: CTF{w3_aRe_g0Nn@????_MY_FuncKee_????ey_!!}
# The unknown positions are at bytes 0-3, 16-19, 32-35
# bytes 0-3: likely "CTF{" 
# bytes 16-19: likely part of flag content
# bytes 32-35: likely part of flag content

print()
print("=== Summary of known decrypted bytes ===")
partial_text = list('?' * 42)
# bytes 4-15 (words 1-3) direct
for i in range(4, 16):
    c = flag_ct[i]
    partial_text[i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'
# bytes 20-23 (word 5)
w5_bytes = struct.pack('<I', (2*k1) & 0xFFFFFFFF)
for i in range(4):
    c = flag_ct[20+i] ^ w5_bytes[i]
    partial_text[20+i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'
# bytes 24-27 (word 6=0) direct
for i in range(24, 28):
    c = flag_ct[i]
    partial_text[i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'
# bytes 28-31 (word 7)
w7_bytes = struct.pack('<I', (2*k3) & 0xFFFFFFFF)
for i in range(4):
    c = flag_ct[28+i] ^ w7_bytes[i]
    partial_text[28+i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'
# bytes 36-39 (word 9=0) direct
for i in range(36, 40):
    c = flag_ct[i]
    partial_text[i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'
# bytes 40-41 (first 2 of word 10)
w10_bytes = struct.pack('<I', (2*k6) & 0xFFFFFFFF)
for i in range(2):
    c = flag_ct[40+i] ^ w10_bytes[i]
    partial_text[40+i] = chr(c) if 32 <= c <= 126 else f'\\x{c:02x}'

print(''.join(str(x) for x in partial_text))
print()
print('The flag ends with: ...}')
print('If bytes 0-3 = "CTF{", then bytes 16-19 and 32-35 should be guessable from context:')
print('CTF{w3_aRe_g0Nn@[b16-19]_MY_FuncKee_[b32-35]ey_!!}')
