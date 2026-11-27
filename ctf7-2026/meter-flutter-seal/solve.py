#!/usr/bin/env python3
"""meter.apk seal: PARTIAL solver.

Reimplements every primitive recovered from libapp.so (Dart 3.13.4 AOT) and
the Java MethodChannel side, plus the app's own MATCH check. The full flag
cannot be printed yet: the 24 hex chars in the middle depend on the runtime
event history and the widget-tree ("dependency graph") snapshot, and that
part of the app is not fully modelled. See WRITEUP.md.

Run: python3 solve.py
"""
M = 0xFFFFFFFF

# --- flag frame, Fye closure 0x201ab4 -> 0x201c08 -------------------------
PREFIX_ENC = [0xc6, 0xbe, 0x89, 0x23, 0x42, 0x3a, 0xe6, 0xd8, 0xa8, 0x9c, 0x73,
              0x59, 0x0f, 0xe5, 0xd2, 0x8f, 0x92, 0x68, 0x5e, 0x14, 0xe1, 0xf1]
PREFIX = ''.join(chr(k ^ ((37 * i + 0xa5) & 0xff)) for i, k in enumerate(PREFIX_ENC))
SEAL_FNV_TARGET = 0xEE2B5244  # 0x201b54: FNV-1a32(hex) must equal this -> "MATCH"


def fnv1a(data, h=2166136261):
    for b in data:
        h = ((h ^ b) * 16777619) & M
    return h


def flag_from_hex(s):
    return PREFIX + s + '}'


def is_real_seal(s):
    return fnv1a(s.encode()) == SEAL_FNV_TARGET


# --- Java side (classes.dex) ----------------------------------------------
def java_l(pkg='com.northfield.meter'):
    """MainActivity.l(): channel method 'a1'."""
    v = 1196573008
    for i, ch in enumerate(pkg):
        v ^= (ord(ch) << ((i % 4) * 8)) & M
        v = ((v << 5) | (v >> 27)) & M
        v ^= (-1640531527 * i) & M
    v = (v ^ (v >> 16)) & M
    v = (v * 73244475) & M
    return v ^ (v >> 16)


A1 = java_l()            # 0x4148b2. Dart fallback if the channel fails: 0x3a587694
A2_FALLBACK = 0x5e6f7081  # Dart fallback when 'a2' fails


def java_a2(x):
    v = (A1 ^ x) & M
    v ^= v >> 15
    v = (v * 739982445) & M
    v ^= v >> 12
    v = (v * 695872825) & M
    return v ^ (v >> 15)


# --- Dart state mixer, 0x1d59f8 (checked against unicorn emulation) -------
def step(S, kind, a, b, c):
    h = (kind * 2654435761 + a * 2246822507 + b * 3266489909 + c) & M
    h = (h ^ (h >> 16)) & M
    h = (h * 0x45d9f3b) & M
    h = (h ^ (h >> 16)) & M
    h = (h * 0x45d9f3b) & M
    h = (h ^ (h >> 16)) & M
    x2, x5, x6, x8 = h & 0xff, (h >> 8) & 0xff, (h >> 16) & 0xff, (h >> 24) & 0xff
    sh = lambda i: (h >> (8 * (i & 3))) & 0xff
    op = (S[(h >> 5) % 12] ^ x2) & 7
    if op == 0:
        for i in range(12):
            S[i] ^= (sh(i) + i * 29) & 0xff
    elif op == 1:
        r = h % 11 + 1
        c0 = S[:]
        for i in range(12):
            S[i] = c0[(i + r) % 12]
    elif op == 2:
        m = x5 | 1
        for i in range(12):
            S[i] = (S[i] + i * m + x2) & 0xff
    elif op == 3:
        for i in range(6):
            S[i], S[11 - i] = S[11 - i], S[i]
        for i in range(12):
            S[i] ^= x6
    elif op == 4:
        for i in range(12):
            v = ((S[i] ^ x2) * 215 + 0x3b) & 0xff
            S[i] = ((v >> 4) | (v << 4)) & 0xff
    elif op == 5:
        c0 = S[:]
        for i in range(12):
            S[i] = (c0[i] + c0[(i + 1) % 12] + x8) & 0xff
    elif op == 6:
        r = (h & 7) | 1
        for i in range(12):
            S[i] = (((S[i] << r) | (S[i] >> (8 - r))) & 0xff) ^ x5
    else:
        for i in range(6):
            S[i] ^= ((S[i + 6] * 7 + x2) ^ (i * 90 + 0x3c)) & 0xff
        for i in range(6):
            S[i + 6] ^= ((S[i] * 5 + x5) ^ (i * 51 + 0x1b)) & 0xff
    for i in range(12):
        S[i] = (S[i] + (S[(i + 1) % 12] ^ sh(i))) & 0xff


class Tracker:
    """tfa / static late final Cj."""

    def __init__(self, a1):
        self.bytes = [(((a1 >> (8 * (i & 3))) & 0xff) ^ ((23 * i + 0x4f) & 0xff)) for i in range(12)]
        self.counter = 0
        self.f13 = self.f1b = self.f23 = 0
        self.record(1, 0, 0)          # 0x3069f4 tail

    def record(self, kind, a, b=0):    # 0x1d593c
        step(self.bytes, kind, a & M, b & M, self.counter)
        self.counter += 1


def candidate(a1, a2_source):
    """Dump (Fye 0x2012d8) with no recorded pointer events, as modelled."""
    cj = Tracker(a1)
    buf, c = cj.bytes[:], cj.counter
    step(buf, 22, cj.f13 ^ cj.f1b, cj.f23, c)
    h = fnv1a(bytes(buf) + bytes(12))          # 0x20175c over the 24-byte array
    a2 = a2_source(h)
    step(buf, 20, a2, 0, c + 1)
    return ''.join('%02x' % (buf[i] ^ ((a2 >> (8 * (i & 3))) & 0xff)) for i in range(12))


if __name__ == '__main__':
    print('flag prefix (decoded from libapp.so):', PREFIX)
    print('MATCH target FNV-1a32:', hex(SEAL_FNV_TARGET))
    found = None
    for a1 in (A1, 0x3a587694):
        for name, src in (('java_a2', java_a2), ('dart_fallback_a2', lambda h: A2_FALLBACK)):
            s = candidate(a1, src)
            ok = is_real_seal(s)
            print('a1=%#x %-17s %s %s' % (a1, name, s, 'MATCH' if ok else 'drift'))
            if ok:
                found = s
    if found:
        print(flag_from_hex(found))
    else:
        print('NO MATCH: seal not reproduced; flag is', PREFIX + '<24 hex>}')
