# movement / "clockmaker" — Reversing writeup (UNSOLVED, flag rejected)

**Status: the derived winding was verified against the local binary
(`./movement` prints "Correct") but was REJECTED by the CTF platform.**
This writeup documents the full reverse-engineering method — which is solid
and reusable — and the specific pitfall that likely explains the rejection,
so future attempts (or future similar challenges) don't repeat the mistake.

## Challenge prompt (paraphrased)

> A master clockmaker died leaving one last mechanism — a sealed brass
> movement that conjugates its state, turns a single gear, and conjugates it
> back, over and over, tens of thousands of times... Speak a winding to it
> and it will tell you whether the bells move... Find the winding it was
> built to accept.

Flag format expected: `ctf7{...}`, 59 bytes total (`ctf7{` + 53-byte body + `}`).

## Binary facts

- ELF64, non-PIE, stripped, entry `0x401a40`. Real `main` at `0x401740`
  (not the more obviously-reached `0x403190`, which is only called
  conditionally).
- Input is read via `fgets` on stdin (NOT argv — an argv-as-filepath theory
  was tested and disproved early).
- Prefix/suffix (`ctf7{` / `}`) and total length are validated with plain
  byte comparisons *before* the crypto path runs; only the 53-byte **body**
  (zero-padded to 64 bytes = 2×32-byte blocks) is fed into the cipher.

## The cipher (fully reverse-engineered and verified byte-exact)

Per-round pipeline, run **0xc365 (50021) times per 32-byte block**, CBC-chained
across the two blocks with a fixed 32-byte IV baked into `.rodata`:

```
sub1  = FWD_SBOX[state[i]]           for each byte i   (forward substitution)
perm  = GF2_LinearLayer(sub1)        (see below — affine, not purely linear)
state'= INV_SBOX[perm[i]]            for each byte i   (inverse substitution)
```

`FWD_SBOX`/`INV_SBOX` are true inverse 256-byte permutation tables; extracted
directly from live memory via ptrace and verified `INV_SBOX[FWD_SBOX[x]]==x`
for all x.

### The linear layer is AFFINE, not linear — this was the hard part

For output bit `i` in 0..255:
```
word_idx = i >> 6          # which of the 4 64-bit words (0..3)
bitpos   = i & 63          # x86 SHR/SHL r64,cl masks cl to 0-63, so this is exact
acc      = XOR over k=0..3 of ( popcount64(state_word[k] & matrix_row_i_word[k]) & 1 )
bit      = ( (WHITEN_WORDS[word_idx] >> bitpos) ^ acc ) & 1
out_word[word_idx] |= bit << bitpos
```

`MATRIX` is a static 256×32-byte table (one 32-byte "row" per output bit).
`WHITEN` is a **separate static 32-byte constant** — critically, it is NOT
the pre-round state (that was the wrong hypothesis for a while) — it is a
fixed buffer passed into every call of the round function for the entire
block, unchanged across all 50021 rounds. This makes the layer **affine**:
`output = (M · state) XOR WHITEN`, where `M` is a 256×256 matrix over GF(2).

### Inverting it (no brute force needed)

Since this is a fixed, keyless, invertible affine bijection:

1. Build `M` as a 256×256 bit matrix directly from `MATRIX` (row `i`, bit `j`
   = `(MATRIX[i*32 + j/8] >> (j%8)) & 1`).
2. Invert `M` over GF(2) via standard Gaussian elimination (bit-packed into
   Python big-ints — 256-bit rows, XOR-based row reduction; confirmed full
   rank / invertible).
3. Inverse round: `perm = FWD_SBOX[sub2[i]]` (undo INV_SBOX) →
   `sub1 = Minv · (perm XOR WHITEN)` → `state = INV_SBOX[sub1[i]]` (undo
   FWD_SBOX).
4. Un-chain CBC: `block2_plain = decrypt(ct_block2) XOR ct_block1`,
   `block1_plain = decrypt(ct_block1) XOR IV`.

This is fast: ~0.00024s/round in pure Python (no numpy available in the
analysis sandbox) using big-int bitmasks for the GF(2) matvec — about 24s
total for 2 blocks × 50021 rounds. See `scripts/cipher3.py`.

Running this against the extracted 64-byte target ciphertext produced:

```
th3_cl0ck_ch1m3d_but_f0r_th3_wr0ng_h0ur_d0_n0t_subm1t
```

i.e. candidate winding `ctf7{th3_cl0ck_ch1m3d_but_f0r_th3_wr0ng_h0ur_d0_n0t_subm1t}`.
**The local unpatched binary (verified matching SHA-256 against a fresh
re-download from the original source) printed "Correct" for this string,
reproducibly, across multiple real-time-separated runs. The platform
rejected it anyway.**

## The pitfall: the binary has an anti-ptrace self-check

While dynamically extracting ground truth (S-boxes, matrix, whitening
constant, target ciphertext, per-round I/O) via a hand-rolled Python ptrace
debugger (no gdb/strace available in the sandbox), the binary was found to
call:

```asm
mov $0x65, %eax      ; 0x65 = 101 = ptrace syscall number
xor %edi, %edi       ; PTRACE_TRACEME = 0
syscall
; result in rax -> stored, tested later with `test %r9,%r9; cmovs ...`
```

This is the classic **self-`PTRACE_TRACEME` anti-debug trick**: a process
that is already being traced cannot successfully call
`ptrace(PTRACE_TRACEME, ...)` again — the syscall fails (`-EPERM`), and the
binary uses that failure as a traced/not-traced signal, conditionally
XORing a time-derived seed value (`^ 0x2aa`) before it feeds into a
downstream table/hash-generation routine.

**This was initially suspected as the direct cause of the wrong flag**
(i.e. "I extracted the tables while traced, so I got decoy tables"). That
hypothesis was tested and **disproved**: `fwd_sbox`, `inv_sbox`, `matrix`,
the whitening constant, and the target ciphertext came back byte-identical
whether the anti-ptrace `cmovs` branch was neutralized (NOPed) or not. The
seed value affected by the anti-debug check feeds a different, apparently
unrelated 32-byte scratch buffer (used in decoding an embedded
`__vdso_clock_gettime` string for a vDSO lookup), not the cipher tables
themselves.

**So the anti-debug trick is real and worth detecting/patching on principle
(see `scripts/ptrace_check_anti_debug.py` for how to read the live
`ptrace()` return value and the seed it feeds), but it was NOT the actual
reason this flag was rejected.** The true root cause is still unknown.
Candidates not yet ruled out:
- A second, distinct valid-ciphertext comparison path not yet found in the
  disassembly (only one `memcmp`-equivalent call was located and confirmed
  singular/strict via its `cmovne` success/failure branch).
- The decrypted text itself being an intentional in-band decoy — i.e. the
  cipher model is correct, the target ciphertext decrypts to the string
  above, the LOCAL binary accepts it (meaning the local comparison target
  really does equal `encrypt(this string)`), but the platform's *actual*
  deployed instance might use a *different* target ciphertext than the one
  baked into this particular downloaded copy (no evidence found for this —
  re-downloading via the original link produced a byte-identical SHA-256,
  arguing against per-instance personalization, but this was only checked
  once).
- A flag-format mismatch unrelated to the cipher (wrapper text/casing) that
  was never confirmed with the platform.

## Lessons for future challenges (see also the repo's
`.kiro/steering/ctf-proven-techniques.md` "Reversing" section)

1. **Detect self-`ptrace(PTRACE_TRACEME,...)` anti-debug checks early** —
   grep disassembly/strings for the raw syscall number `0x65`/`101` near a
   `xor edi,edi` / zero-arg pattern, not just library-level `TracerPid`
   reads. Patch the conditional branch that consumes its result (here: NOP
   the `cmovs` at the use site) so dynamic analysis reflects native
   behavior — then **independently verify** that doing so doesn't change
   the specific artifacts you care about (it didn't, here, but that had to
   be proven, not assumed).
2. **A "Correct"/success signal from the target binary itself is necessary
   but not sufficient** when a platform-hosted scoring system is involved —
   always get platform confirmation before concluding a challenge is solved.
3. When a decrypted/recovered string reads as a taunt ("do not submit",
   "wrong gear", "nice try") — per this repo's existing decoy-awareness
   notes — treat it as a decoy signal, **but don't assume the whole
   derivation path is wrong** just because of that; in this case the crypto
   model was independently proven byte-exact against ptrace ground truth
   and the local binary's own gate accepted the taunting string as correct.
   The taunt and local success can both be real at the same time, pointing
   at an incomplete understanding of the comparison/delivery mechanism
   rather than a broken cipher model.
