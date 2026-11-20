---
name: invert-linear-checksum
description: Algebraically invert a linear checksum (CRC32, CRC16, Adler32, or any GF(2)-linear hash) to find a preimage that produces a target output, instead of brute-forcing. Use when a binary or challenge requires input whose checksum/CRC equals a specific target value, especially "enter a password such that checksum(password) == known_string" patterns.
---

## When this applies

Many binaries (especially rev/pwn CTF challenges) implement a "password
check" that isn't really comparing your input directly — it's comparing a
checksum of your input (often CRC32, computed per fixed-size chunk) against
a hardcoded target. Brute-forcing 2^32 possibilities is slow; CRC32 and
similar checksums are **linear over GF(2) for a fixed-length input**, so the
exact preimage can be solved algebraically in milliseconds.

## How to recognize it in disassembly

Look for a loop structure matching this pattern (CRC32 specifically):
```
crc = 0xFFFFFFFF   (i.e. ~0)
for each byte b in input:
    crc = table[(crc ^ b) & 0xFF] ^ (crc >> 8)
return ~crc
```
with a 256-entry, 4-byte-per-entry lookup table nearby in `.rodata`/`.data`.
Confirm the table matches the standard CRC32 (IEEE 802.3, polynomial
`0xEDB88320` reflected) by comparing its first several entries against a
freshly generated standard table — do not assume a custom polynomial without
checking, but also don't assume standard without checking either.

## The script (adapt the target length / table / init / xorout as needed)

```python
"""
Invert a fixed-length CRC32 (or similar GF(2)-linear checksum) to find an
input X such that checksum(X) == target.

Approach: for a FIXED message length, checksum(X) is an affine function of
the input bits over GF(2): checksum(X) = M*X XOR C, where M is a bit-matrix
and C = checksum(all-zero input of the same length). Determine M by probing
each single input bit (checksum(e_i) XOR C gives column i), then solve
M*X = target XOR C via Gaussian elimination over GF(2).
"""
import zlib

MSG_LEN_BYTES = 4          # <-- set to the actual chunk size the binary uses
NUM_BITS = MSG_LEN_BYTES * 8

def checksum(b: bytes) -> int:
    return zlib.crc32(b) & 0xFFFFFFFF   # swap for a different checksum if needed

def bytes_from_bits(x: int) -> bytes:
    return x.to_bytes(MSG_LEN_BYTES, "big")   # confirm byte order matches the binary

def build_matrix():
    C = checksum(b"\x00" * MSG_LEN_BYTES)
    cols = []
    for bit in range(NUM_BITS):
        msg = bytes_from_bits(1 << bit)
        cols.append(checksum(msg) ^ C)
    return C, cols

def solve(target: int, C: int, cols):
    rhs = target ^ C
    rows = []
    for outbit in range(32):  # CRC32 output is 32 bits regardless of input length
        row = 0
        for inbit in range(NUM_BITS):
            if (cols[inbit] >> outbit) & 1:
                row |= (1 << inbit)
        rows.append((row, (rhs >> outbit) & 1))

    mat = rows[:]
    pivot_for_col = {}
    r = 0
    for col in range(NUM_BITS):
        piv = next((i for i in range(r, len(mat)) if (mat[i][0] >> col) & 1), None)
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        for i in range(len(mat)):
            if i != r and (mat[i][0] >> col) & 1:
                mat[i] = (mat[i][0] ^ mat[r][0], mat[i][1] ^ mat[r][1])
        pivot_for_col[col] = r
        r += 1

    x = 0
    for col, row_idx in pivot_for_col.items():
        x |= (mat[row_idx][1] << col)
    return x

def find_preimage(target_bytes: bytes) -> bytes:
    target = int.from_bytes(target_bytes, "big")
    C, cols = build_matrix()
    x = solve(target, C, cols)
    msg = bytes_from_bits(x)
    assert checksum(msg) == target, "verification failed — check byte order / chunk length / checksum variant"
    return msg

if __name__ == "__main__":
    # Example: find a 4-byte input whose CRC32 equals the ASCII bytes "my_c"
    target = b"my_c"
    preimage = find_preimage(target)
    print(preimage.hex())
```

## Multi-chunk inputs

If the binary splits your input into N fixed-size chunks and checks each
chunk's checksum against a different target (e.g. 16 bytes of password split
into four 4-byte chunks, each checked against 4 target bytes), solve each
chunk independently with `find_preimage` and concatenate the results — the
chunks are independent linear systems.

## Always verify against the real binary

After computing the preimage, feed it to the actual target binary/service
before trusting it — confirm byte order (big vs little endian extraction of
the checksum), chunk length, and checksum variant (CRC32 vs CRC32C vs Adler32
vs a custom polynomial) all match by checking the assertion passes AND the
real program accepts it.
