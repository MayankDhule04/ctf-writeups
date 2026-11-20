#!/usr/bin/env python3
"""
Planner: given target price (0 <= price < 0x100000), produce a sequence of coin
operations (by name) that leaves r8 == price, using:
  - adc gadgets: add denom to a register (r8..r15). (carry from initial stc adds +1 to FIRST adc)
  - sub gadgets: r8 -= rN  (N in 9..15), each usable once per appearance.

Construction:
  r8 = A - sum(Bn)  where
    A   = value added directly to r8 using r8-owned denoms {1,0x100,0x10000,0x20000,0x40000,0x80000}
    Bn  = value in register n (9..15), each built from that register's denoms, subtracted once.

  We want A - sum(Bn) = price.

  Choose to represent price with NON-NEGATIVE digits so no borrow needed:
    Idea: set A = price with the "hard" bits rounded UP to r8-owned positions, and let
    the subtracted registers remove the overshoot.

  Simplest fully-general method that works and is short enough (<=28 coins):
    Work bit by bit is messy; instead use this identity per non-r8 register:
       We can ADD value V to r8 by:  r8 += D (an r8 denom >= V aligned) ; build (D - V) in reg ; sub.
    But cross-register borrows complicate.

  Cleanest: use a SINGLE big r8 denom to overshoot, subtract the difference spread over regs.
    Let A be the smallest value using r8 denoms with A >= price AND (A - price) representable
    by non-r8 registers (i.e. (A-price) has no bit 0, 8, or 16 set... those are r8-only).
    But we ADD bits 0/8/16 of price to r8 directly, so the subtracted difference must avoid them.

  Let me split price into:
    hi = bits {0,8,16} of price       -> added to r8 directly (denoms 1,0x100,0x10000)
    rest = price - hi                 -> only bits in {1-7,9-15,17-19}, all owned by r9..r15
  Now I need r8 += rest as well, but rest's bits are non-r8. Use overshoot:
    Add to r8 an r8-denom block 'A2' that is >= rest and whose (A2 - rest) is also only
    non-{0,8,16} bits. Choose A2 as the sum of r8 denoms {0x20000,0x40000,0x80000} needed to
    exceed rest, then subtract (A2 - rest) via non-r8 registers.
    (A2 uses only bits 17,18,19 which are non-{0,8,16}; rest uses bits 1-7,9-15,17-19;
     A2 - rest may borrow into... but bits 0,8,16 of (A2-rest): since neither A2 nor rest has
     bits 0/8/16, the difference could still generate them via borrow. So verify.)

  To avoid borrow headaches, do it byte-cleanly:
    Represent rest in base where each "digit region" is handled by one register.
    Actually simplest: since we can REPEAT denominations, build each non-r8 bit directly in its
    register (adc), then move to r8 by overshoot per register:
       For register n holding Vn (the bits of price it owns), add SAME amount to r8 via r8 denom
       and subtract... no, r8 can't make Vn generally.

  === PRACTICAL SOLUTION ===
  Use TWO's complement over the subtract: r8 = A - B, pick B = (A - price).
  Let A = round price UP to a multiple of 0x100000? No, keep A small.
  Let A = price + B. Choose B to be any value we can build in the non-r8 registers,
  AND A must be buildable from r8 denoms.
  r8 denoms can build any multiple structure of {1,0x100,0x10000,0x20000,0x40000,0x80000}.
  With repetition, r8 can build: c0*1 + c1*0x100 + c2*0x10000 + c3*0x20000 + c4*0x40000 + c5*0x80000.
  That's arbitrary in bits 0-7 (via c0 up to 255), bits 8-15 (via c1), bits 16-19 (via c2..c5).
  So r8 ALONE can build ANY value 0..0xfffff using digit counts:
     c0 = A & 0xff                      (that many 'croeseid' +1)  -> up to 255 coins!! too many
  Repetition count too high.

  So we cannot brute with +1. Need the other registers for the low/mid bits with FEW coins.

  KEY: each bit 2^b is available as a single adc gadget on some register. So to build value X
  (X < 2^20) we need popcount(X) adc gadgets total (one per set bit), each on the owning register.
  Then we must SUM these registers into r8. r8's own bits are already summed in r8. The others
  are in separate registers and can only be SUBTRACTED.

  Trick to turn subtraction into addition: use the relation
     r8 = (2^k) - ((2^k) - price)  for suitable k, where BOTH terms are built with single-bit coins?
  (2^k) is one coin (if k in r8-owned {0,8,16,17,18,19}) or needs building.
  ((2^k) - price) has ~k bits set (lots of coins). Not great.

  === THE INTENDED TRICK (carry chain) ===
  adc uses the carry flag. If we add denominations to a register and cause 64-bit overflow,
  carry propagates to the NEXT adc gadget. But values are tiny; no natural overflow.
  HOWEVER the FIRST adc after 'stc' gets +1. That's the only carry interaction.

  Given the difficulty, the intended solution likely: build r8 = price using popcount(price)
  single-bit coins across registers, then a chain of 'sub r8, rN' — but that needs ADD.

  Let me reconsider: maybe r8 should be built as the NEGATION and base is chosen so base - X works.
  Re-examine final gadgets: quarter = lea rax,[rip+0x532]; cent = add rax, r8; shilling = jmp rax.
  base = pie+0x1a26. target = pie + 0x4000 + price. So need r8 = price + (0x4000-0x1a26)=price+0x25da.
  Wait — earlier the SERVER said price = balance + OFFSET and balance = mmap base = pie+0x4000.
  And target(win) = mmap_base + r12 = balance + r12. The server's OFFSET == r12.
  So we need base + r8 = balance + r12 = (pie+0x4000) + OFFSET.
  base = pie + 0x1a26. => r8 = 0x4000 - 0x1a26 + OFFSET = 0x25da + OFFSET.
  So r8_target = OFFSET + 0x25da. (OFFSET is the printed price offset.)
"""

# denominations
R8_DENOMS   = [1, 0x100, 0x10000, 0x20000, 0x40000, 0x80000]
OWN = {  # bit -> register that owns 2^bit
    0:8, 8:8, 16:8, 17:8, 18:8, 19:8,   # r8 owns these bits (as single coins)
    1:9, 9:9, 17:9,                      # note 17 also r9 (0x20000) & r8 (0x20000)
}
# Build a definitive bit->coin map using single-coin denominations:
BIT_COIN = {}
COIN_EFF = {
    'croeseid':(8,1),'daric':(9,2),'siglos':(10,4),'karshapana':(11,8),
    'tetradrachm':(12,0x10),'stater':(13,0x20),'obol':(14,0x40),'lepton':(15,0x80),
    'aureus':(8,0x100),'solidus':(9,0x200),'denarius':(10,0x400),'antoninianus':(11,0x800),
    'sestertius':(12,0x1000),'florin':(13,0x2000),'sequin':(14,0x4000),'tremissis':(15,0x8000),
    'dinar':(8,0x10000),'dirham':(8,0x20000),'scudo':(8,0x40000),'thaler':(8,0x80000),
    'real':(9,0x20000),'piloncitos':(10,0x40000),'koban':(11,0x80000),
}
# pick one coin per bit value, preferring r8 so it's directly added
val_to_coins = {}
for nm,(reg,val) in COIN_EFF.items():
    val_to_coins.setdefault(val, []).append((reg,nm))

def coin_for_value(val, prefer_reg=None):
    opts = val_to_coins[val]
    if prefer_reg is not None:
        for reg,nm in opts:
            if reg==prefer_reg: return reg,nm
    return opts[0]

print("value -> coins:")
for v in sorted(val_to_coins):
    print(hex(v), val_to_coins[v])
