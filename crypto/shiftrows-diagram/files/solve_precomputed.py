"""Precompute md5(k); MITM via sorting + two-pointer merge on 128-bit mids."""
import numpy as np
from hashlib import md5

BLOCK = 16
N = 256**3
kp_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
kp_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")


def xor16(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def pack_row_u128(row):
    hi = int.from_bytes(bytes(row[:8]), "big")
    lo = int.from_bytes(bytes(row[8:]), "big")
    return hi, lo


def rows_to_hi_lo(arr):
    """arr shape (N, 16) uint8 -> hi, lo as uint64 arrays"""
    hi = np.zeros(N, dtype=np.uint64)
    lo = np.zeros(N, dtype=np.uint64)
    for c in range(8):
        hi |= arr[:, c].astype(np.uint64) << (56 - 8 * c)
    for c in range(8):
        lo |= arr[:, c + 8].astype(np.uint64) << (56 - 8 * c)
    return hi, lo


def mitm_xor_double():
    print("precompute md5 for all 3-byte keys...", flush=True)
    rks = np.empty((N, 16), dtype=np.uint8)
    for i in range(N):
        k = bytes([i >> 16, (i >> 8) & 255, i & 255])
        rks[i] = np.frombuffer(md5(k).digest(), dtype=np.uint8)

    pt = np.frombuffer(kp_pt, dtype=np.uint8)
    ct = np.frombuffer(kp_ct, dtype=np.uint8)

    mids_fwd = rks ^ pt
    mids_bwd = rks ^ ct

    print("pack + sort forward/backward mids...", flush=True)
    hf, lf = rows_to_hi_lo(mids_fwd)
    hb, lb = rows_to_hi_lo(mids_bwd)
    order_f = np.lexsort((lf, hf))
    order_b = np.lexsort((lb, hb))

    print("two-pointer merge...", flush=True)
    i = j = 0
    while i < N and j < N:
        a = (hf[order_f[i]], lf[order_f[i]])
        b = (hb[order_b[j]], lb[order_b[j]])
        if a < b:
            i += 1
        elif a > b:
            j += 1
        else:
            idx = int(order_f[i])
            jdx = int(order_b[j])
            if np.array_equal(mids_fwd[idx], mids_bwd[jdx]):
                k1 = bytes([idx >> 16, (idx >> 8) & 255, idx & 255])
                k2 = bytes([jdx >> 16, (jdx >> 8) & 255, jdx & 255])
                rk1 = bytes(rks[idx])
                rk2 = bytes(rks[jdx])
                if xor16(xor16(kp_pt, rk1), rk2) != kp_ct:
                    i += 1
                    j += 1
                    continue
                print(f"FOUND id/id XOR k1={k1.hex()} k2={k2.hex()}")
                ft = np.frombuffer(flag_ct, dtype=np.uint8)
                pt_flag = bytes(rks[jdx] ^ (rks[idx] ^ ft))
                print("flag", pt_flag)
                print(pt_flag.decode("utf-8", errors="replace"))
                return True
            i += 1
            j += 1
    print("no identity-xor solution")
    return False


if __name__ == "__main__":
    mitm_xor_double()
