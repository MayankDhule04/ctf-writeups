"""Recover key via meet-in-the-middle for ROUNDS=1, identity SBOX/PERM (encrypt.py defaults)."""
from hashlib import md5

BLOCK_SIZE = 16

kp_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
kp_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])


def main():
    # fun(k, pt) = xor(pt, md5(k)) when SBOX=id, PERM=id, ROUNDS=1
    forward = {}
    for i in range(256**3):
        k1 = bytes([i >> 16, (i >> 8) & 0xFF, i & 0xFF])
        h = md5(k1).digest()
        inter = xor(kp_pt, h)
        forward[inter] = k1

    for i in range(256**3):
        k2 = bytes([i >> 16, (i >> 8) & 0xFF, i & 0xFF])
        h = md5(k2).digest()
        inter = xor(kp_ct, h)
        if inter in forward:
            k1 = forward[inter]
            # verify
            mid = xor(kp_pt, md5(k1).digest())
            ct = xor(mid, md5(k2).digest())
            if ct == kp_ct:
                print("FOUND")
                print("k1 =", k1, repr(k1))
                print("k2 =", k2, repr(k2))
                print("full key =", (k1 + k2).hex())
                # decrypt flag: inverse of encrypt is fun^-1(k1) ∘ fun^-1(k2) = same XOR ops
                x = xor(flag_ct, md5(k2).digest())
                pt = xor(x, md5(k1).digest())
                print("flag_pt hex:", pt.hex())
                print("flag ascii:", pt)
                try:
                    s = pt.decode("utf-8")
                    print("utf-8:", s)
                except UnicodeDecodeError:
                    pass
                return
    print("not found")


if __name__ == "__main__":
    main()
