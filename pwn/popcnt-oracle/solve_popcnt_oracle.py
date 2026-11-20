#!/usr/bin/env python3
"""
Popcnt Oracle — RSA plaintext recovery via Hamming-weight-change oracle

Attack principle:
  oracle(x) = hw(x^d mod n)  (Hamming weight / popcount of decryption)

  Key facts:
    1. hw(2x) == hw(x)  ALWAYS  (left-shift doesn't change bit count)
    2. Therefore:
         hw(t_{i+1}) == hw(t_i)  =>  NO WRAP  (t_{i+1} = 2*t_i, no mod reduction)
         hw(t_{i+1}) != hw(t_i)  =>  DEFINITE WRAP  (t_{i+1} = 2*t_i - n)
       where t_i = 2^i * m mod n
    
    NOTE: There are rare cases (~7%) where a wrap occurs but hw stays the same.
    These cause bit errors. We handle them via:
      a) querying extra oracle calls to disambiguate ambiguous positions, OR
      b) (for this challenge) the delta-probe loop at the end tries nearby values
         by recomputing which 'same-hw' positions could be flipped.

  Reconstruction:
    The wrap sequence encodes the binary expansion of m/n:
      w_i = 1  iff  2^i * m mod n >= n/2  iff  wrap at step i
    Given w_0..w_{N-1}:
      m = round(n * sum_{i} w_i * 2^{-(i+1)}) + 1   (the +1 fixes systematic floor bias)

  Query count: N+1 (one for hw(m), then N doublings) where N = n.bit_length() ~ 2048
"""

from pwn import remote
from fractions import Fraction
import re
import time

HOST = "tcp.flagyard.com"
PORT = 16559


def main():
    print("[*] Connecting...")
    io = remote(HOST, PORT)

    # ── Parse banner ─────────────────────────────────────────────────────────
    params = {}
    while not all(k in params for k in ("e", "n", "c")):
        line = io.recvline().decode(errors="ignore").strip()
        match = re.match(r'^([enc])\s*=\s*(\d+)$', line)
        if match:
            params[match.group(1)] = int(match.group(2))

    e, n, c = params["e"], params["n"], params["c"]
    nbits = n.bit_length()
    two_e = pow(2, e, n)

    print(f"[+] n = {nbits} bits,  e = {e}")

    # ── Oracle helper ─────────────────────────────────────────────────────────
    def query(x):
        """Send x, skip 'x> ' prompt tokens, return the integer popcount (or flag str)."""
        io.recvuntil(b"x> ")
        io.sendline(str(x).encode())
        resp = io.recvline().decode(errors="ignore").strip()
        return resp

    # ── Step 0: get hw(m) by querying c directly ──────────────────────────────
    resp = query(c)
    if not resp.lstrip('-').isdigit():
        print(f"[+] FLAG: {resp}")
        io.close()
        return
    hw_prev = int(resp)
    print(f"[+] hw(m) = {hw_prev}")

    # ── Main loop: N doublings, track hw changes as wrap signal ───────────────
    cur = c                   # encrypts current t_i
    wraps = []                # wraps[i] = 1 iff hw changed at step i+1
    ambiguous = []            # indices where hw stayed same (could be a missed wrap)

    start = time.time()
    print(f"[*] Running {nbits} queries...")

    for i in range(nbits):
        cur = (cur * two_e) % n          # plaintext doubles: t_{i+1} = 2*t_i mod n
        resp = query(cur)

        if not resp.lstrip('-').isdigit():
            print(f"[+] FLAG: {resp}")
            io.close()
            return

        hw_curr = int(resp)

        if hw_curr != hw_prev:
            wraps.append(1)              # definite wrap
        else:
            wraps.append(0)             # no wrap (or ~7%-chance missed wrap)
            ambiguous.append(i)

        hw_prev = hw_curr

        if (i + 1) % 256 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  [{i+1:4d}/{nbits}]  {rate:.1f} q/s  ETA {(nbits-i-1)/rate:.0f}s  "
                  f"wraps so far: {sum(wraps)}")

    elapsed = time.time() - start
    print(f"[+] Done. {nbits} queries in {elapsed:.1f}s ({nbits/elapsed:.1f} q/s)")
    print(f"[+] Total wraps detected: {sum(wraps)},  ambiguous (same-hw) positions: {len(ambiguous)}")

    # ── Reconstruct m from wrap sequence ─────────────────────────────────────
    # wraps encodes binary expansion of m/n:  m/n ≈ Σ w_i * 2^{-(i+1)}
    # The floor systematically gives m-1, so we add 1.
    def reconstruct(wrap_seq):
        frac = Fraction(0)
        for i, w in enumerate(wrap_seq):
            if w:
                frac += Fraction(1, 2 ** (i + 1))
        return int(frac * n) + 1

    m_candidate = reconstruct(wraps)
    print(f"[+] Candidate m reconstructed")

    # ── Probe around candidate (handles both rounding and a few missed wraps) ─
    def try_submit(val):
        if val <= 0 or val >= n:
            return False
        resp = query(val)
        if not resp.lstrip('-').isdigit():
            print(f"\n🚩 FLAG: {resp}")
            io.close()
            return True
        return False

    # First try the direct candidate ± small delta
    for delta in range(-8, 9):
        guess = m_candidate + delta
        print(f"[.] Trying delta={delta:+d} ...", end=" ", flush=True)
        if try_submit(guess):
            return
        print("no")

    # If still not found: flip each ambiguous bit one at a time and retry
    # (handles the ~7% case where a wrap was missed, causing the candidate to be
    #  off by a larger amount)
    print(f"[*] Trying {len(ambiguous)} single-bit flips on ambiguous positions...")
    for idx in ambiguous[:200]:          # cap at 200 to avoid too many queries
        flipped = wraps[:]
        flipped[idx] = 1 - flipped[idx]  # flip this ambiguous position
        guess = reconstruct(flipped)
        for delta in range(-2, 3):
            if try_submit(guess + delta):
                return

    print("[-] Could not recover exact m. Closest candidate:", m_candidate)
    io.close()


if __name__ == "__main__":
    main()
