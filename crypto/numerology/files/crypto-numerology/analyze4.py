import json
import struct

CHALLENGE_DIR = r'c:\Users\mayan\OneDrive\Desktop\ctf\5b0d78bf17f82eca5d41baa852ea1abdf8d81a63c16f5c42c3de6b164b5428b6aeefc0bc83ac1ac3d4967946362c40bfdb346e61b45c09a3f259031feb0e6365\crypto-numerology'

data = json.load(open(CHALLENGE_DIR + r'\ctf_challenge_package.json'))

samples = data['learning_dataset_for_player']
key = bytes.fromhex(data['cipher_parameters']['key'])
common_pt = bytes.fromhex(data['cipher_parameters']['common_plaintext'])
flag_ct = bytes.fromhex(data['flag_ciphertext'])

key_words_LE = [struct.unpack_from('<I', key, i)[0] for i in range(0, 32, 4)]
print('Key words (LE):', [f'{w:08x}' for w in key_words_LE])
# [00000000, 0270545c, 00000000, 7b72f431, 3492d4f7, 00000000, c9b1bbe7, 00000000]

# From analysis:
# Keystream word 5 is ALWAYS 04e0a8b8 for nonce 0
# diff = w5 - key[1] = 04e0a8b8 - 0270545c = 0270545c!
# So w5 = key[1] + key[1] = 2 * key[1]  (mod 2^32)
print()
print('2 * key[1]:', hex((2 * key_words_LE[1]) & 0xFFFFFFFF))
print('Observed w5:', hex(0x04e0a8b8))

# Similarly, diff w10 = c9b1bbe7 = key[6]
# So w10 = key[6] + key[6] = 2 * key[6]
print()
print('2 * key[6]:', hex((2 * key_words_LE[6]) & 0xFFFFFFFF))
print('Observed w10:', hex(0x936377ce))
# 2 * c9b1bbe7 = 193637bce... mod 2^32 = 93637bce... hmm

# Wait, let me recalculate
k6 = key_words_LE[6]  # c9b1bbe7
print(f'k6 = {k6:08x}')
print(f'2*k6 mod 2^32 = {(2*k6) & 0xFFFFFFFF:08x}')
print(f'Observed w10 = 936377ce')
# 2 * c9b1bbe7 = 193637bce mod 2^32 = 936377ce ??? let me check
print(f'hex(2 * 0xc9b1bbe7) = {hex(2 * 0xc9b1bbe7)}')
print(f'hex(2 * 0xc9b1bbe7 & 0xFFFFFFFF) = {hex(2 * 0xc9b1bbe7 & 0xFFFFFFFF)}')

# Interesting! 2 * 0xc9b1bbe7 = 0x193637bce 
# mod 2^32 = 0x936377ce -- YES! That matches!

# So this IS indeed addition-based output
# w5_keystream = final_state_w5 XOR XOR PT = ... wait no
# keystream = PT XOR CT, so keystream_w5 = PT_w5 XOR CT_w5
# For n0_c0: keystream_w5 = 04e0a8b8

# If keystream_w5 = 2*key[1] = output of some cipher...
# Actually in ChaCha20/Salsa20, the output is: initial_state + scrambled_state
# Where the key occupies positions 4-11 in the state
# For position 5 (key[1] = 0270545c):
# output[5] = key[1] + f(state) = key[1] + something
# We observe output[5] = 04e0a8b8 = 2 * key[1]
# So f(state) that mixes into position 5 = key[1] since output = key[1] + key[1]
# This makes sense if ROUNDS=1 and the quarter round operations cause key[1] to feed into itself

# Let's verify the insight: in Salsa20's quarterround:
# The SALSA20 quarter round: (a,b,c,d) are mixed
# In ChaCha20 column QR: (0,4,8,12), (1,5,9,13), (2,6,10,14), (3,7,11,15)
# Then diagonal: (0,5,10,15), (1,6,11,12), (2,7,8,13), (3,4,9,14)
# With ROUNDS=1, that's only 2 quarter rounds

# For init.sh: ROUNDS=1
print()
print("=== Testing ChaCha20 with ROUNDS=1 ===")
# ChaCha20 quarter round:
def chacha_qr(a, b, c, d):
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = ((d << 16) | (d >> 16)) & 0xFFFFFFFF
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = ((b << 12) | (b >> 20)) & 0xFFFFFFFF
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = ((d << 8) | (d >> 24)) & 0xFFFFFFFF
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = ((b << 7) | (b >> 25)) & 0xFFFFFFFF
    return a, b, c, d

def chacha20_block(key32, nonce12, counter, rounds):
    # IETF ChaCha20 state
    SIGMA = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    key_words = [struct.unpack_from('<I', key32, i)[0] for i in range(0, 32, 4)]
    nonce_words = [struct.unpack_from('<I', nonce12, i)[0] for i in range(0, 12, 4)]
    
    state = list(SIGMA) + key_words + [counter % (2**32)] + list(nonce_words)
    working = list(state)
    
    for _ in range(rounds):
        # Column rounds
        working[0],working[4],working[8],working[12] = chacha_qr(working[0],working[4],working[8],working[12])
        working[1],working[5],working[9],working[13] = chacha_qr(working[1],working[5],working[9],working[13])
        working[2],working[6],working[10],working[14] = chacha_qr(working[2],working[6],working[10],working[14])
        working[3],working[7],working[11],working[15] = chacha_qr(working[3],working[7],working[11],working[15])
        # Diagonal rounds
        working[0],working[5],working[10],working[15] = chacha_qr(working[0],working[5],working[10],working[15])
        working[1],working[6],working[11],working[12] = chacha_qr(working[1],working[6],working[11],working[12])
        working[2],working[7],working[8],working[13] = chacha_qr(working[2],working[7],working[8],working[13])
        working[3],working[4],working[9],working[14] = chacha_qr(working[3],working[4],working[9],working[14])
    
    output = [(state[i] + working[i]) & 0xFFFFFFFF for i in range(16)]
    result = b''
    for w in output:
        result += struct.pack('<I', w)
    return result

# Test with nonce=0, counter=0, 1 round
nonce_zero = b'\x00' * 12
ks_generated = chacha20_block(key, nonce_zero, 0, 1)
print('Generated keystream (ChaCha20, 1 round, zero nonce, counter=0):')
gen_words = [struct.unpack_from('<I', ks_generated, i)[0] for i in range(0, 64, 4)]
print([f'{w:08x}' for w in gen_words])

# Observed keystream n0_c0:
s0 = samples[0]
pt = bytes.fromhex(s0['plaintext_hex'])
ct = bytes.fromhex(s0['ciphertext_hex'])
obs_ks = bytes(a ^ b for a, b in zip(pt, ct))
obs_words = [struct.unpack_from('<I', obs_ks, i)[0] for i in range(0, 64, 4)]
print('Observed keystream (n0_c0):')
print([f'{w:08x}' for w in obs_words])
print('Match?', ks_generated == obs_ks)

# If not matching, try different nonce values
# The challenge has 32 nonces -- need to figure out what nonce 0 is
# Let's try to brute-force or guess the nonce for sample n0_c0
# The sample ID says n0 = nonce variant 0, c0 = counter variant 0
# The init.sh says SECRET_TARGET_NONCE_HEX and target counter
print()
print('=== Testing various nonces for n0_c0 ===')
# Check various counter values
for ctr in range(10):
    ks_gen = chacha20_block(key, nonce_zero, ctr, 1)
    if ks_gen == obs_ks:
        print(f'MATCH! counter={ctr}, nonce=zero')
        break

# Try Salsa20
def salsa20_qr(a, b, c, d):
    b ^= ((a + d) & 0xFFFFFFFF)
    b = ((b << 7) | (b >> 25)) & 0xFFFFFFFF
    c ^= ((b + a) & 0xFFFFFFFF)
    c = ((c << 9) | (c >> 23)) & 0xFFFFFFFF
    d ^= ((c + b) & 0xFFFFFFFF)
    d = ((d << 13) | (d >> 19)) & 0xFFFFFFFF
    a ^= ((d + c) & 0xFFFFFFFF)
    a = ((a << 18) | (a >> 14)) & 0xFFFFFFFF
    return a, b, c, d

print()
print('=== Salsa20 test ===')
# Salsa20 with key and zero nonce
# Salsa20 state (with 256-bit key):
# "expa" key[0]  key[1]  key[2]
# key[3] "nd 3" nonce[0] nonce[1]
# ctr[0] ctr[1] "2-by"  key[4]
# key[5] key[6] key[7]  "te k"

def salsa20_block(key32, nonce8, counter, rounds):
    TAU = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    kw = [struct.unpack_from('<I', key32, i)[0] for i in range(0, 32, 4)]
    nw = [struct.unpack_from('<I', nonce8, i)[0] for i in range(0, 8, 4)]
    ctr_lo = counter & 0xFFFFFFFF
    ctr_hi = (counter >> 32) & 0xFFFFFFFF
    
    state = [
        TAU[0],  kw[0],   kw[1],   kw[2],
        kw[3],   TAU[1],  nw[0],   nw[1],
        ctr_lo,  ctr_hi,  TAU[2],  kw[4],
        kw[5],   kw[6],   kw[7],   TAU[3]
    ]
    working = list(state)
    
    for _ in range(rounds):
        # Column rounds (in Salsa20's terms)
        working[0],working[4],working[8],working[12] = salsa20_qr(working[0],working[4],working[8],working[12])
        working[5],working[9],working[13],working[1] = salsa20_qr(working[5],working[9],working[13],working[1])
        working[10],working[14],working[2],working[6] = salsa20_qr(working[10],working[14],working[2],working[6])
        working[15],working[3],working[7],working[11] = salsa20_qr(working[15],working[3],working[7],working[11])
        # Row rounds
        working[0],working[1],working[2],working[3] = salsa20_qr(working[0],working[1],working[2],working[3])
        working[5],working[6],working[7],working[4] = salsa20_qr(working[5],working[6],working[7],working[4])
        working[10],working[11],working[8],working[9] = salsa20_qr(working[10],working[11],working[8],working[9])
        working[15],working[12],working[13],working[14] = salsa20_qr(working[15],working[12],working[13],working[14])
    
    output = [(state[i] + working[i]) & 0xFFFFFFFF for i in range(16)]
    result = b''
    for w in output:
        result += struct.pack('<I', w)
    return result

nonce_zero8 = b'\x00' * 8
for ctr in range(10):
    ks_gen = salsa20_block(key, nonce_zero8, ctr, 1)
    if ks_gen == obs_ks:
        print(f'Salsa20 MATCH! counter={ctr}, nonce=zero8')
        break
else:
    print('No Salsa20 match found with zero nonce')

# Key insight from analysis:
# w5 (keystream) = 2 * key[1] always for n0 samples
# w10 (keystream) = 2 * key[6] always for n0 samples  
# This means: output[5] = state[5] + working[5] where initial state[5] = key_word1
# If working[5] = key_word1 (unchanged by 1 round), then output = 2*key_word1
# Let's check which state positions have: output = 2 * initial
print()
print('=== Checking if any state positions remain unchanged after 1 round ===')
# For ChaCha20 with 1 round, which positions get modified?
# After column QRs: (0,4,8,12), (1,5,9,13), (2,6,10,14), (3,7,11,15)
# After diagonal QRs: (0,5,10,15), (1,6,11,12), (2,7,8,13), (3,4,9,14)
# Position 5 is modified in BOTH column round (1,5,9,13) and diagonal (0,5,10,15)
# Position 10 is modified in column (2,6,10,14) and diagonal (0,5,10,15)
# None are totally unchanged

# But perhaps the zero input at certain positions causes the output to equal 2*input?
# Let's just simulate and see
SIGMA = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
kw = key_words_LE
# ChaCha20 state: [sigma]*4 + [key]*8 + [ctr] + [nonce]*3
# With zero nonce and ctr=0:
initial_state = list(SIGMA) + kw + [0, 0, 0, 0]
print('Initial state:')
for i, w in enumerate(initial_state):
    print(f'  [{i:2d}]: {w:08x}')
