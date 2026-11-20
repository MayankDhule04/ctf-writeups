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

# We know: flag = ????w3_aRe_g0Nn@????_MY_FuncKee_????ey_!!}
# Positions 0-3, 16-19, 32-35 are encrypted with keystream words 0, 4, 8
# These words depend only on the COUNTER value
# The secret counter was NOT among the 32 sampled counter values

# Strategy: reverse engineer how the counter affects w0, w4, w8
# and extrapolate to find the secret counter

# Collect all (counter_idx, w0, w4, w8, w12) from n0 samples
n0_samples = sorted([s for s in samples if s['sample_id'].startswith('sample_n0_')],
                    key=lambda s: int(s['sample_id'].split('_c')[1]))

data_pts = []
for s in n0_samples:
    pt = bytes.fromhex(s['plaintext_hex'])
    ct = bytes.fromhex(s['ciphertext_hex'])
    ks = bytes(a ^ b for a, b in zip(pt, ct))
    ctr_idx = int(s['sample_id'].split('_c')[1])
    w0 = struct.unpack_from('<I', ks, 0)[0]
    w4 = struct.unpack_from('<I', ks, 16)[0]
    w8 = struct.unpack_from('<I', ks, 32)[0]
    w12 = struct.unpack_from('<I', ks, 48)[0]
    data_pts.append((ctr_idx, w0, w4, w8, w12))

print('Counter data (idx, w0, w4, w8, w12):')
for d in data_pts:
    print(f'  c{d[0]:2d}: w0={d[1]:08x} w4={d[2]:08x} w8={d[3]:08x} w12={d[4]:08x}')

# KEY: the actual counter value in the cipher state might be different from the index
# The KNOWN counter values (from dataset) are specific numeric values chosen by the challenge
# The SECRET counter is a different value
# The keystream function is: ks = f(key, nonce, counter)
# We know f for 32 counter values; we need to find the counter that gives us the flag keystream

# The flag's word 0 keystream bytes: flag_ct[0:4] XOR flag_plaintext[0:4]
# If the flag starts with "CTF{": ks_w0_flag = flag_ct[0:4] XOR b'CTF{'
# = 692f09e6 XOR 43544366 = 2a7b4a80 = 0x2a7b4a80

flag_prefix = b'CTF{'
ks_w0_flag = bytes(a ^ b for a, b in zip(flag_ct[0:4], flag_prefix))
w0_flag_target = struct.unpack('<I', ks_w0_flag)[0]
print()
print(f'Flag w0 target (if starts with CTF{{): {w0_flag_target:08x}')

# Now I need to understand the mathematical relationship between actual counter value and w0
# Looking at the dataset: the 32 counter values are specifically chosen
# The init.sh says NUM_COUNTER_VARS=32 and SECRET_TARGET_COUNTER_INT
# The 32 counter values are VARIATIONS AROUND the secret target
# The patterns in w12 might encode the actual counter used

# Let me analyze the actual counter embedding
# w12 for n0_c0 = 4e73493e = 0x4e73493e = 1316178238 in decimal
# This might be the counter value used in the cipher

# Check if the n0_c0 counter encodes something specific
# The variations: from n0_c0 to n0_c1, w12 changes from 4e73493e to 4d73494f
# The counter index 0 → 1 changes w12, so w12 IS the counter in the cipher state

# If w12 IS the actual counter used in the cipher, then:
# For the flag, we need to find a counter value where w0 matches our target
# The function w0 = F(counter) is complex (involves mixing with other state)

# But we can look at patterns...
# From data: w0 changes with counter in a complex way
# The key insight: if the cipher is a LINEAR or simple function, we can model it

# Let me check if there is a linear relationship between w12 (counter) and w0
# Looking at pairs:
print()
print('Analysis of counter vs w0:')
for d in data_pts:
    ctr = d[4]  # w12 = counter value
    w0 = d[1]
    print(f'  ctr={ctr:08x} w0={w0:08x}  XOR={ctr^w0:08x}  ADD={(ctr+w0)&0xFFFFFFFF:08x}')

# The plaintext word 0 (as LE int):
pt_w0 = struct.unpack_from('<I', common_pt, 0)[0]
print()
print(f'Plaintext word 0: {pt_w0:08x}')
print()
print('ctr vs (w0 XOR pt_w0):')
for d in data_pts:
    ctr = d[4]
    w0 = d[1]
    print(f'  ctr={ctr:08x} w0^pt_w0={w0^pt_w0:08x}  ctr+w0^pt_w0={(ctr+(w0^pt_w0))&0xFFFFFFFF:08x}')

# Let's look: ciphertext word 0 = w0 (keystream) XOR pt word 0
# And the cipher state: word 12 (counter) goes through the ChaCha-like mixing → output
# After 1 ROUND, the counter mixes primarily with the constant (sigma) word at position 12

# Actually: the init state INCLUDES the counter at position 12
# After 1 round of ChaCha20, positions 0 and 12 interact via:
# Column QR (0,4,8,12) and diagonal QR (0,5,10,15)
# Then final output[0] = initial_state[0] + working[0]
# initial_state[0] = sigma[0] = 0x61707865
# working[0] = result of two quarter rounds involving sigma[0], key[0]=0, key[4]=k4, counter

# Let me just try to model this: if it's ChaCha20 with 1 round,
# I can compute w0 for any counter value

def chacha_qr(a, b, c, d):
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = ((d << 16) | (d >> 16)) & 0xFFFFFFFF
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = ((b << 12) | (b >> 20)) & 0xFFFFFFFF
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = ((d << 8) | (d >> 24)) & 0xFFFFFFFF
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = ((b << 7) | (b >> 25)) & 0xFFFFFFFF
    return a, b, c, d

def chacha20_1round_state(key32, counter_val, nonce12=None):
    SIGMA = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    kw = [struct.unpack_from('<I', key32, i)[0] for i in range(0, 32, 4)]
    if nonce12 is None:
        nw = [0, 0, 0]
    else:
        nw = [struct.unpack_from('<I', nonce12, i)[0] for i in range(0, 12, 4)]
    
    state = list(SIGMA) + kw + [counter_val & 0xFFFFFFFF] + list(nw)
    working = list(state)
    
    # 1 round = 1 column + 1 diagonal
    working[0],working[4],working[8],working[12] = chacha_qr(working[0],working[4],working[8],working[12])
    working[1],working[5],working[9],working[13] = chacha_qr(working[1],working[5],working[9],working[13])
    working[2],working[6],working[10],working[14] = chacha_qr(working[2],working[6],working[10],working[14])
    working[3],working[7],working[11],working[15] = chacha_qr(working[3],working[7],working[11],working[15])
    working[0],working[5],working[10],working[15] = chacha_qr(working[0],working[5],working[10],working[15])
    working[1],working[6],working[11],working[12] = chacha_qr(working[1],working[6],working[11],working[12])
    working[2],working[7],working[8],working[13] = chacha_qr(working[2],working[7],working[8],working[13])
    working[3],working[4],working[9],working[14] = chacha_qr(working[3],working[4],working[9],working[14])
    
    output = [(state[i] + working[i]) & 0xFFFFFFFF for i in range(16)]
    return output

# Test: use w12 values as the actual counter, check if chacha20_1round produces matching w0
print()
print('Testing ChaCha20 1-round with w12 as counter:')
for d in data_pts[:5]:
    ctr = d[4]  # w12
    output = chacha20_1round_state(key, ctr)
    w0_pred = output[0]
    w0_obs = d[1]
    print(f'  ctr={ctr:08x}: predicted w0={w0_pred:08x}, observed w0={w0_obs:08x}, match={w0_pred==w0_obs}')
    
# Also test with different nonces for w13 check
print()
print('What if we use the w12 directly (counter)? Let me check what sigma[0] XOR output[0] gives...')
# Actually if the cipher is linear in the counter bits, maybe we can find the target counter
# by looking at the pattern

# Let's try: find the counter value that gives w0 = w0_flag_target
# w0_flag_target = flag_ct[0:4] XOR b'CTF{'
print()
print(f'Searching for counter value giving w0={w0_flag_target:08x}...')
found = False
for test_ctr in range(0, 2**32, 1):
    output = chacha20_1round_state(key, test_ctr)
    if output[0] == w0_flag_target:
        print(f'  FOUND! counter={test_ctr} ({test_ctr:#010x})')
        # Verify with w4 and w8
        # Get w4 from flag_ct
        # Need to know what the flag bytes 16-19 are to verify
        found = True
        break
    if test_ctr > 0 and test_ctr % 100000 == 0:
        print(f'  Checked {test_ctr} counters...')
        break  # Too slow, let's be smarter
