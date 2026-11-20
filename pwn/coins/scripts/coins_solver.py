#!/usr/bin/env python3
"""
Solve the 'coins' challenge.

Mechanic (from disassembly):
  - Program prints starting balance (mmap base) and flag price = balance + OFFSET.
  - Win shellcode (open /flag + sendfile) sits at balance + OFFSET.
  - Our input is a ROP chain of 'coin' gadget addresses executed after validation.
  - Gadgets do adc/sub on r8..r15. Final: quarter(lea rax,[base]) ; cent(add rax,r8) ; shilling(jmp rax)
    => jumps to base + r8. We need r8 == OFFSET (the price offset).
  - Validation requires: every 8-byte value is a known coin gadget address, and the
    LAST value equals the 'shilling' (jmp rax) gadget. Then stc;ret starts the chain.
  - After validation CF=1, so the FIRST adc gadget executed adds an extra +1.

Gadget denominations (PIE offsets; add pie_base at runtime — but chain uses absolute
addresses, so we must leak pie base... see note below).

NOTE ON ADDRESSES: the binary is PIE. The ROP chain needs ABSOLUTE gadget addresses,
which require knowing the PIE base. The 'starting balance' printed is the mmap base
(= pie_base + 0x4000). So pie_base = balance - 0x4000. All gadget addresses = pie_base + off.
"""

from pwn import remote, context, p64
import time, re

context.log_level = 'error'
HOST = "coins-a265f2d26226.chall.nnsc.tf"; PORT = 1337

# coin gadget PIE offsets and their effect
# name: (offset, ('adc'/'sub', reg, const_or_reg))
COINS = {
    'croeseid':    (0x142e, ('adc', 8, 1)),
    'daric':       (0x1433, ('adc', 9, 2)),
    'siglos':      (0x1438, ('adc', 10, 4)),
    'karshapana':  (0x143d, ('adc', 11, 8)),
    'tetradrachm': (0x1442, ('adc', 12, 0x10)),
    'stater':      (0x1447, ('adc', 13, 0x20)),
    'obol':        (0x144c, ('adc', 14, 0x40)),
    'lepton':      (0x1451, ('adc', 15, 0x80)),
    'aureus':      (0x1459, ('adc', 8, 0x100)),
    'solidus':     (0x1461, ('adc', 9, 0x200)),
    'denarius':    (0x1469, ('adc', 10, 0x400)),
    'antoninianus':(0x1471, ('adc', 11, 0x800)),
    'sestertius':  (0x1479, ('adc', 12, 0x1000)),
    'florin':      (0x1481, ('adc', 13, 0x2000)),
    'sequin':      (0x1489, ('adc', 14, 0x4000)),
    'tremissis':   (0x1491, ('adc', 15, 0x8000)),
    'dinar':       (0x1499, ('adc', 8, 0x10000)),
    'dirham':      (0x14a1, ('adc', 8, 0x20000)),
    'scudo':       (0x14a9, ('adc', 8, 0x40000)),
    'thaler':      (0x14b1, ('adc', 8, 0x80000)),
    'real':        (0x14b9, ('adc', 9, 0x20000)),
    'piloncitos':  (0x14c1, ('adc', 10, 0x40000)),
    'koban':       (0x14c9, ('adc', 11, 0x80000)),
    'loonie':      (0x14d1, ('sub', 8, 9)),
    'krugerrand':  (0x14d5, ('sub', 8, 10)),
    'sovereign':   (0x14d9, ('sub', 8, 11)),
    'drachma':     (0x14dd, ('sub', 8, 12)),
    'penny':       (0x14e1, ('sub', 8, 13)),
    'nickel':      (0x14e5, ('sub', 8, 14)),
    'dime':        (0x14e9, ('sub', 8, 15)),
    'quarter':     (0x14ed, ('lea',)),   # lea rax,[base]
    'cent':        (0x14f5, ('add_rax_r8',)),
    'shilling':    (0x14f9, ('jmp',)),
}

# denominations per register that ADD to that register
REG_DENOMS = {
    8:  [1, 0x100, 0x10000, 0x20000, 0x40000, 0x80000],
    9:  [2, 0x200, 0x20000],
    10: [4, 0x400, 0x40000],
    11: [8, 0x800, 0x80000],
    12: [0x10, 0x1000],
    13: [0x20, 0x2000],
    14: [0x40, 0x4000],
    15: [0x80, 0x8000],
}
# map (reg, const) -> coin name
DENOM_COIN = {}
for nm,(off,eff) in COINS.items():
    if eff[0]=='adc':
        DENOM_COIN[(eff[1], eff[2])] = nm
SUB_COIN = {}   # reg -> coin that does sub r8, reg
for nm,(off,eff) in COINS.items():
    if eff[0]=='sub':
        SUB_COIN[eff[2]] = nm

def plan_r8(price):
    """
    Build r8 == price.
    Strategy: For each bit set in price, add denomination 2^bit to the register that owns it.
    Registers other than r8 are then subtracted from r8 -> but that gives negative.
    Instead: overshoot r8, then subtract other regs.

    Cleaner approach: we want r8 = price. We can only ADD to r8 via r8-denoms, and
    SUBTRACT other regs from r8. So:
        r8 = (sum of chosen r8 denoms) - (r9val + r10val + ... )
    Set:
        - Put bits of price that r8 owns (bits 0,8,16,17,18,19) directly into r8.
        - For bits owned by other registers, we can't add to r8. Instead, overshoot:
          add a big r8 denom, then subtract the complement built in other regs.

    Simplest robust method:
      Let target = price.
      Choose A (built only from r8 denoms) >= price such that (A - price) can be built
      as a sum of non-r8 register values (each register can hold sum of its denoms).
      Then r8 = A - sum(other regs) = price.

    But easier: build A = price rounded up using r8 denoms, and correction = A - price
    using other registers. Since r8 has denom 1, we can fine tune... but only limited +1.

    Let me use a direct bit approach:
      price bits -> assign each set bit to its owning register.
      r8 gets its bits directly (added).
      For a non-r8 register rN that ends with value V (sum of price bits it owns),
      we need to ADD V to r8. Since only sub is available, do:
          add (V) to r8 via ... not possible directly.
      => Instead, we add V to rN, and add V again to r8 by using r8's denoms? Only if r8 owns those bits.

    FINAL WORKING STRATEGY (overshoot + subtract):
      r8 = S8 - (r9+r10+...+r15)
      We want this = price.
      Put price's bits into a temporary big value using ALL registers' denoms so every
      bit is representable. Then:
        - bits owned by r8 -> add to r8 (contributes +).
        - bits owned by rN (N!=8) -> add to rN, which we then SUBTRACT (contributes -).
      That gives r8 = (r8 bits) - (other bits) != price.

      To fix signs: we want everything +. Use the identity for other-register bits:
        We can represent a needed value W (for non-r8 bits) by:
          add (W + K) to r8   [using r8 denoms, if possible]  minus K in rN
        This is getting complicated. Instead use a clean number-theoretic construction:

      OBSERVE: r8 denominations include 1, 0x100, 0x10000, 0x20000, 0x40000, 0x80000.
      With just 1 and 0x100 we can make any value 0..0xffff by repetition? 0xff * (+1) = 255 max
      for low byte, plus 0xff*(+0x100) for next byte. That's up to 255 gadgets. Too many.

    BEST: use subtraction to cover the bits r8 lacks.
      r8 lacks direct denoms for bits 1..7 (values 2,4,8,0x10,0x20,0x40,0x80) and
      bits 9..15 (0x200..0x8000). Those are owned by r9..r15.
      Trick: r8 = (r8-owned big value) - (r9..r15 values), choosing the big value so the
      subtraction yields exactly price.

      Let low = price & 0xff (bits0-7), etc. This is hard by hand; do a small BFS/greedy.
    """
    # We'll use a constructive method:
    # Represent price = sum over registers of (value we ADD to that register),
    # where for r8 we ADD directly (positive), for others we build the value and SUBTRACT
    # (negative). To make all contributions positive, we instead compute:
    #
    #   r8_final = R8_add - (R9 + R10 + ... + R15)
    #
    # We want r8_final = price.
    # Freedom: choose R8_add and each RN (each is a sum of that reg's denominations, with
    #          repetition allowed).
    #
    # Set all RN = 0 (don't use them) and R8_add = price IF price is representable by r8
    # denoms with few coins. r8 denoms: 1,0x100,0x10000,0x20000,0x40000,0x80000.
    # price up to 0xfffd8. Representing arbitrary price with these needs many +1/+0x100.
    #
    # Instead: use ALL registers to represent price bit-by-bit, then transfer.
    # Transfer non-r8 register values into r8 by OVERSHOOTING:
    #   For a non-r8 register holding value V, we want +V in r8. Equivalent to:
    #     r8 += (2^64 - V) then it wraps? No.
    #
    # Simplest that WORKS within gadget budget:
    #   Use r8's own denoms for bits {0,8,16,17,18,19}.
    #   For every other bit b (owned by rN), we can synthesize +2^b into r8 as:
    #       (2^b) = (next_r8_denom) - (stuff)   -- messy.
    #
    # Given time, use the OVERSHOOT-AND-SUBTRACT with a clean formula:
    #   Let need = price.
    #   Build r8 up using its denominations greedily to a value A >= price,
    #   where A - price is expressible as sum of non-r8 denominations (each reg summed then subtracted).
    #   Because non-r8 denoms cover all of bits 1..7 and 9..15 (values 2,4,...,0x8000) and
    #   also 0x20000,0x40000,0x80000, the correction A-price can be built if we pick A wisely.
    #
    # Concretely: choose A = price with bits{1..7,9..15} cleared and rounded so that the
    # cleared bits become the correction. i.e.
    #   A = price with all non-r8-owned bits FORCED, correction = A - price = those bits.
    # r8-owned bit positions: 0,8,16,17,18,19. Non-owned within 0..19: 1-7,9-15 (values 2..0x80, 0x200..0x8000).
    # bits >=20 don't occur (price < 0x100000).
    #
    # Plan:
    #   R8_add = (price restricted to r8-owned bits) + (correction using r8 denoms to cover the rest)
    # Ugh. Let's do the truly simple thing:
    #   A = price + C, where C = sum of non-r8-owned bits' complement... 
    #
    # DIRECT: r8 = A - B, want = price.
    #   Let B = sum of non-r8-owned bits present in price? No.
    #
    # I'll just do: put EVERY set bit of price into its owning register (adc).
    #   Then r8 holds sum of its owned set bits = P8.
    #   Other registers hold their owned set bits, values Vn.
    #   We need to ADD sum(Vn) to r8. Since only 'sub r8,rN' exists, we instead:
    #     negate each Vn by building (2^64 - Vn)? not feasible.
    #
    # FINAL DECISION: use r8 denoms 1 and 0x100 etc. AND the sub gadgets to reach the
    # exact value with a small ILP. Just brute force a short combo with a BFS over
    # (r8 value) using operations, limited depth. price < 0x100000 (20 bits).
    raise NotImplementedError

if __name__ == "__main__":
    print("scaffold only")
