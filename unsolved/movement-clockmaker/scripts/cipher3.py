import pickle, time

FWD_SBOX = open("fwd_sbox.bin","rb").read()
INV_SBOX = open("inv_sbox.bin","rb").read()
WHITEN = open("whiten_const.bin","rb").read()
IV = bytes.fromhex("d013f8769104af946dd095c6b9faa1d0f84c055a344b51b2149788ddede21c58")[:32]
ROUNDS = 0xc365

with open("M_rows.pkl","rb") as f:
    M_rows_bits = pickle.load(f)
with open("Minv_rows.pkl","rb") as f:
    Minv_rows_bits = pickle.load(f)

def bytes_to_int256(b32: bytes) -> int:
    # bit j = (b32[j>>3] >> (j&7)) & 1 ; build integer where bit j is set accordingly
    # This is just little-endian bit order across the whole 32-byte buffer = int.from_bytes(b32, 'little')
    return int.from_bytes(b32, 'little')

def int256_to_bytes(x: int) -> bytes:
    return (x & ((1<<256)-1)).to_bytes(32, 'little')

# Precompute row masks as integers (bit j set if row has 1 at position j)
M_row_masks = [sum((1 << j) for j in range(256) if M_rows_bits[i][j]) for i in range(256)]
Minv_row_masks = [sum((1 << j) for j in range(256) if Minv_rows_bits[i][j]) for i in range(256)]
WHITEN_INT = bytes_to_int256(WHITEN)

def popcount(x: int) -> int:
    return bin(x).count("1")

def matvec(row_masks, state_int: int) -> int:
    out = 0
    for i, rm in enumerate(row_masks):
        if popcount(rm & state_int) & 1:
            out |= (1 << i)
    return out

def linear_layer_fast(sub1_bytes: bytes) -> bytes:
    state_int = bytes_to_int256(sub1_bytes)
    acc = matvec(M_row_masks, state_int)
    out_int = acc ^ WHITEN_INT
    return int256_to_bytes(out_int)

def linear_layer_inverse_fast(perm_bytes: bytes) -> bytes:
    perm_int = bytes_to_int256(perm_bytes)
    acc_int = perm_int ^ WHITEN_INT
    sub1_int = matvec(Minv_row_masks, acc_int)
    return int256_to_bytes(sub1_int)

def gear_round_fwd(state: bytes) -> bytes:
    sub1 = bytes(FWD_SBOX[b] for b in state)
    perm = linear_layer_fast(sub1)
    return bytes(INV_SBOX[b] for b in perm)

def gear_round_inv(state: bytes) -> bytes:
    perm = bytes(FWD_SBOX[b] for b in state)
    sub1 = linear_layer_inverse_fast(perm)
    return bytes(INV_SBOX[b] for b in sub1)

def encrypt_block(block32: bytes) -> bytes:
    state = block32
    for _ in range(ROUNDS):
        state = gear_round_fwd(state)
    return state

def decrypt_block(block32: bytes) -> bytes:
    state = block32
    for _ in range(ROUNDS):
        state = gear_round_inv(state)
    return state

def decrypt(ciphertext: bytes) -> bytes:
    assert len(ciphertext) % 32 == 0
    blocks = [ciphertext[i:i+32] for i in range(0, len(ciphertext), 32)]
    prevs = [IV] + blocks[:-1]
    out = b""
    for block, prev in zip(blocks, prevs):
        dec = decrypt_block(block)
        plain = bytes(a ^ b for a, b in zip(dec, prev))
        out += plain
    return out

if __name__ == "__main__":
    state0 = bytes.fromhex("884ba02ec95cf7cc3588cd9ee1a2f988a0145d026c1309ea4ccfd085b5ba4400")
    round1_expected = bytes.fromhex("174f7a8b1408f025fa2b5567758a61ffbcf90be89710a26943ef7aa0460b9fb2")
    t0 = time.time()
    r1 = gear_round_fwd(state0)
    print("one round fwd time:", time.time()-t0, "match:", r1 == round1_expected)
    t0 = time.time()
    r0 = gear_round_inv(r1)
    print("one round inv time:", time.time()-t0, "round-trip match:", r0 == state0)
