import json

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

print('Key (hex):', key.hex())
print('Key len:', len(key))
print('Common PT len:', len(common_pt))
print('Flag CT len:', len(flag_ct))
print()

key_words = [key[i:i+4].hex() for i in range(0, 32, 4)]
print('Key as 4-byte words:', key_words)
print()

# XOR of PT and CT for first few samples
n0_samples = [s for s in samples if s['sample_id'].startswith('sample_n0_')]
print('n0 sample count:', len(n0_samples))
for s in n0_samples[:5]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    xored = bytes(a ^ b for a, b in zip(pt, ct))
    print(f"  {s['sample_id']}: XOR = {xored.hex()}")

print()
# Check all nonce groups
nonce_groups = {}
for s in samples:
    parts = s['sample_id'].split('_')
    n = parts[1]  # n0, n1, etc.
    c = parts[2]  # c0, c1, etc.
    nonce_groups.setdefault(n, []).append(s)

print('Nonce groups:', sorted(nonce_groups.keys()))
print('Samples per nonce:', {k: len(v) for k, v in nonce_groups.items()})

# For the same nonce but different counter, XOR(PT, CT) should differ
print()
print('XOR values for n0 (same plaintext, different counter in key):')
all_xors = []
for s in nonce_groups.get('n0', [])[:5]:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    xored = bytes(a ^ b for a, b in zip(pt, ct))
    all_xors.append(xored)
    print(f"  {s['sample_id']}: XOR = {xored.hex()}")

# Check where XOR differs between samples
print()
print('Byte positions where XOR changes between c0 and c1:')
if len(all_xors) >= 2:
    for i in range(min(len(all_xors[0]), len(all_xors[1]))):
        if all_xors[0][i] != all_xors[1][i]:
            print(f'  byte {i}: {all_xors[0][i]:02x} vs {all_xors[1][i]:02x}')

# Try: this might be a stream cipher (like ChaCha20 or similar)
# The key is given, the nonce and counter vary
# Let's check what the XOR represents -- it should be the keystream

# Key has a specific structure -- let's look at it:
# 000000005c5470020000000031f4727bf7d4923400000000e7bbb1c900000000
# Bytes 0-3: 00000000
# Bytes 4-7: 5c547002  (non-zero)
# Bytes 8-11: 00000000
# Bytes 12-15: 31f4727b (non-zero)
# Bytes 16-19: f7d49234 (non-zero)
# Bytes 20-23: 00000000
# Bytes 24-27: e7bbb1c9 (non-zero)
# Bytes 28-31: 00000000

# This looks like an active material key where only some 32-bit words are non-zero
print()
print('Key structure analysis:')
for i, w in enumerate(key_words):
    val = int(w, 16)
    print(f'  Word {i}: {w} = {val} ({"ACTIVE" if val != 0 else "zero"})')

# Try ChaCha20
print()
print('Attempting ChaCha20 decryption...')
try:
    from Crypto.Cipher import ChaCha20
    # ChaCha20 key is 32 bytes, nonce is 8 or 12 bytes
    # In the challenge, the nonce and counter are separate parameters
    # Let's try with a zero nonce first
    nonce_zero = b'\x00' * 8
    cipher = ChaCha20.new(key=key, nonce=nonce_zero)
    # Decrypt flag_ct
    flag_pt = cipher.decrypt(flag_ct)
    print('ChaCha20 (8-byte zero nonce) flag decryption:', flag_pt)
    print('As hex:', flag_pt.hex())
except Exception as e:
    print('ChaCha20 error:', e)

# Verify with known PT/CT pair using ChaCha20
try:
    from Crypto.Cipher import ChaCha20
    # Try with common_pt and first ciphertext
    first_sample = samples[0]
    pt = bytes.fromhex(first_sample['plaintext_hex'])
    ct = bytes.fromhex(first_sample['ciphertext_hex'])
    # The keystream = PT XOR CT
    keystream = bytes(a ^ b for a, b in zip(pt, ct))
    print()
    print('Keystream for sample_n0_c0:', keystream.hex())
    
    # Try ChaCha20 with zero nonce, counter=0 to generate keystream
    nonce_zero = b'\x00' * 8
    cipher = ChaCha20.new(key=key, nonce=nonce_zero)
    gen_ks = cipher.encrypt(b'\x00' * 64)
    print('ChaCha20 keystream (zero nonce, counter=0):', gen_ks.hex())
    print('Match?', gen_ks == keystream)
except Exception as e:
    print('Verification error:', e)
