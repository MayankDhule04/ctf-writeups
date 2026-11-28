MASK = 0xFFFFFFFF

TABLE = [0x9e3779b9, 0x7f4a7c15, 0xf39cc060, 0x5cedc834, 0xb1a83721, 0x2f2e1e8b]
MUL_CONST = 0x2c1b3c6d

def compute_key(seed: int, sa_l1_lo: int, sa_l1_hi: int) -> int:
    seed &= MASK
    lo = sa_l1_lo & MASK
    hi = sa_l1_hi & MASK

    eax = (seed ^ lo) & MASK
    ecx = ((hi - 1 - seed) & MASK)

    for i in range(6):
        edx = eax
        edx = (edx * eax) & MASK          # edx = eax * eax
        edx = (edx | 5) & MASK
        edx = (edx + eax) & MASK
        eax2 = TABLE[i]
        eax2 = (eax2 + edx) & MASK
        eax2 = (eax2 ^ ecx) & MASK
        ecx = (eax2 * MUL_CONST) & MASK
        eax2_shl = (eax2 << 7) & MASK
        eax2_shl = (eax2_shl ^ hi) & MASK
        ecx = (ecx + eax2_shl) & MASK
        eax = (lo + ecx * 8) & MASK
        eax = (eax ^ edx) & MASK

    lo2 = (lo + lo) & MASK
    lo2 = (lo2 ^ ecx) & MASK
    final = (eax ^ lo2) & MASK
    return final

if __name__ == "__main__":
    # test pairs extracted from the real candump capture (seed, key), both as 32-bit hex ints
    pairs = [
        (0xD55A6C60, 0x14C6F953),
        (0x93670AC6, 0x9B08666F),
        (0xED318559, 0xA9F3F925),
        (0x7DE5E946, 0x6E45C36F),
    ]
    # we don't know sa_l1 yet -- this is just the function; testing requires the real sa_l1.
    print("keygen loaded, TABLE=", [hex(t) for t in TABLE])
