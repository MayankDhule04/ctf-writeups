"""Try 3-byte key: k1=key[:3], k2=key[3:]==b'' => round2 uses md5(b'')."""
from hashlib import md5

BLOCK = 16
kp_pt = bytes.fromhex("c91ca824783e91dc41a856162bcfaebc")
kp_ct = bytes.fromhex("25c4ceee22c0529b19c2b51886fed24c")
flag_ct = bytes.fromhex("adee3839c59e972f2b2e96440f0002d0")


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def inv_sbox_from(sbox):
    inv = [0] * 256
    for i, v in enumerate(sbox):
        inv[v] = i
    return bytes(inv)


def fun(pt, rk, sbox, perm):
    state = bytearray(xor(pt, rk))
    for i in range(BLOCK):
        state[i] = sbox[state[i]]
    new = bytearray(BLOCK)
    for i in range(BLOCK):
        new[i] = state[perm[i]]
    return bytes(new)


def fun_inv(ct, rk, inv_sbox, perm):
    inv_map = [0] * BLOCK
    for i in range(BLOCK):
        inv_map[perm[i]] = i
    b = bytearray(BLOCK)
    for j in range(BLOCK):
        b[j] = ct[inv_map[j]]
    a = bytearray(inv_sbox[b[i]] for i in range(BLOCK))
    return xor(bytes(a), rk)


def encrypt(key, pt, rounds, sbox, perm):
    k1, k2 = key[:3], key[3:]
    inv = inv_sbox_from(sbox)
    x = pt
    for _ in range(rounds):
        rk = md5(k1).digest()
        x = fun(x, rk, sbox, perm)
    for _ in range(rounds):
        rk = md5(k2).digest()
        x = fun(x, rk, sbox, perm)
    return x


def try_empty_k2(rounds, sbox, perm, name):
    """k2 empty: only k1 contributes; encrypt uses fun(md5(''), fun(k1,...)) for 1 round each?"""
    inv = inv_sbox_from(sbox)
    rk_empty = md5(b"").digest()
    # inner = F_k1(P); C = F_empty(inner) with k2 empty
    inner_needed = fun_inv(kp_ct, rk_empty, inv, perm)
    for i in range(256**3):
        k1 = bytes([i >> 16, (i >> 8) & 255, i & 255])
        rk1 = md5(k1).digest()
        mid = fun(kp_pt, rk1, sbox, perm)
        if mid != inner_needed:
            continue
        outer = fun(mid, rk_empty, sbox, perm)
        if outer == kp_ct:
            print(f"[{name}] 3-byte key k1={k1!r} k2=b''")
            x = fun_inv(flag_ct, rk_empty, inv, perm)
            pt = fun_inv(x, rk1, inv, perm)
            print("flag", pt)
            return True
    return False


def try_empty_k1(rounds, sbox, perm, name):
    rk_empty = md5(b"").digest()
    inv = inv_sbox_from(sbox)
    inner_needed = fun_inv(kp_ct, rk_empty, inv, perm)
    for i in range(256**3):
        k2 = bytes([i >> 16, (i >> 8) & 255, i & 255])
        rk2 = md5(k2).digest()
        mid = fun(kp_pt, rk2, sbox, perm)
        if mid != inner_needed:
            continue
        outer = fun(mid, rk_empty, sbox, perm)
        if outer == kp_ct:
            print(f"[{name}] k1=b'' k2={k2!r}")
            return True
    return False


def main():
    identity_sbox = bytes(range(256))
    identity_perm = list(range(16))
    print("try empty k2, identity", try_empty_k2(1, identity_sbox, identity_perm, "id"))
    print("try empty k1, identity", try_empty_k1(1, identity_sbox, identity_perm, "id"))


if __name__ == "__main__":
    main()
