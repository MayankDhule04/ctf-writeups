#!/usr/bin/env python3
"""
The key values might tell us the COUNTER VALUE to use!
Let me try interpreting the key as the actual counter in different ways
"""
import json

print("[*] NUMEROLOGY FINAL SOLVER")
print("="*70)

# Load data
with open('5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365/crypto-numerology/ctf_challenge_package.json', 'r') as f:
    data = json.load(f)

common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])
key = bytes.fromhex(data['cipher_parameters']['key'])

# Get all keystreams
samples = data['learning_dataset_for_player']
keystreams = {}

for sample in samples:
    nonce = sample['nonce_hex']
    counter = sample['counter_int']
    pt = bytes.fromhex(sample['plaintext_hex'])
    ct = bytes.fromhex(sample['ciphertext_hex'])
    ks = bytes([p ^ c for p, c in zip(pt, ct)])
    
    if nonce not in keystreams:
        keystreams[nonce] = {}
    keystreams[nonce][counter] = ks

# The key might encode: nonce + counter
# Let's try different interpretations

# Interpretation 1: Key is the nonce (first 12 bytes) + counter (last 4 bytes)
print(f"\n[Interpretation 1: Key as nonce+counter]")
key_nonce = key[:12].hex()
key_counter = int.from_bytes(key[12:16], 'little')

print(f"Nonce from key: {key_nonce}")
print(f"Counter from key: {key_counter}")

# Check if we have this combination
if key_nonce in keystreams and key_counter in keystreams[key_nonce]:
    print(f"*** Found matching sample! ***")
    ks = keystreams[key_nonce][key_counter]
    flag_pt = bytes([c ^ k for c, k in zip(flag_ct, ks)])
    
    print(f"Decrypted (hex): {flag_pt.hex()}")
    try:
        flag_text = flag_pt.decode('utf-8')
        print(f"Decrypted (text): {flag_text}")
        if 'CTF{' in flag_text:
            print(f"\n*** FLAG: {flag_text} ***")
    except:
        print("Not UTF-8")

# Interpretation 2: Different byte ordering
print(f"\n[Interpretation 2: Different orderings]")

# Try treating the whole key as a counter
key_as_counter = int.from_bytes(key, 'little')
print(f"Key as single counter: {key_as_counter}")

# Try first 4 bytes as counter
for i in range(0, len(key), 4):
    chunk_counter = int.from_bytes(key[i:i+4], 'little')
    if chunk_counter > 0:
        print(f"Bytes {i}-{i+3} as counter: {chunk_counter}")
        
        # Check all nonces
        for nonce in keystreams:
            if chunk_counter in keystreams[nonce]:
                print(f"  Found in nonce {nonce}")
                ks = keystreams[nonce][chunk_counter]
                flag_pt = bytes([c ^ k for c, k in zip(flag_ct, ks)])
                
                try:
                    flag_text = flag_pt.decode('utf-8')
                    if 'CTF{' in flag_text:
                        print(f"\n*** FLAG: {flag_text} ***")
                        exit(0)
                except:
                    pass

# Interpretation 3: The key tells us to XOR specific keystreams
# Maybe we need to XOR keystreams for counters encoded in the key

print(f"\n[Interpretation 3: XOR multiple keystreams]")

# Extract all non-zero 4-byte values from key as potential counters
potential_counters = []
for i in range(0, len(key), 4):
    val = int.from_bytes(key[i:i+4], 'little')
    if val > 0:
        potential_counters.append(val)

print(f"Potential counters from key: {potential_counters}")

# Try XORing keystreams from nonce 01
nonce_01 = "010000000000000000000000"
if nonce_01 in keystreams:
    # Start with counter=1
    combined_ks = bytearray(keystreams[nonce_01][1])
    
    for counter in potential_counters:
        if counter in keystreams[nonce_01] and counter != 1:
            print(f"XORing keystream for counter={counter}")
            ks = keystreams[nonce_01][counter]
            for i in range(len(combined_ks)):
                combined_ks[i] ^= ks[i]
    
    flag_pt = bytes([c ^ k for c, k in zip(flag_ct, combined_ks)])
    print(f"\nDecrypted (hex): {flag_pt.hex()}")
    
    try:
        flag_text = flag_pt.decode('utf-8')
        print(f"Decrypted (text): {flag_text}")
        if 'CTF{' in flag_text:
            print(f"\n*** FLAG: {flag_text} ***")
    except:
        print("Not UTF-8")

print("\n" + "="*70)
