# housevm writeup

**Flag:** `ctf7{h4nd_r0ll3d_vm_s3lf_d3crypt1ng_d4t4_d3p3nd3nt_0ps_r3v3rs3d}`
The "word" is the 58-byte inner string `h4nd_r0ll3d_vm_s3lf_d3crypt1ng_d4t4_d3p3nd3nt_0ps_r3v3rs3d`.
`./housevm` prints `Correct` (rc=0) for the full flag on stdin.

## Mechanism (main at 0x4016e0)
1. `ptrace(PTRACE_TRACEME)` (wrapper 0x41aaf0). Success selects key `0x5b1f2e3d4c6a7988`. Failure (a tracer is attached) selects the wrong key `0x85b290d28694c336`, so the program decrypts to garbage under a debugger.
2. 0xc00 bytes at 0x47f7e8 are XORed with a splitmix64 keystream (0x401ba0, seeded with that key, 8 bytes per step). The result is 1024 three-byte instructions `(op, a, b)`.
3. The input line must be 64 bytes: `ctf7{` + 58 bytes + `}`. The 58 inner bytes are zero-padded to 64.
4. Cipher (0x401dd0): CBC-like over 4 blocks of 16 bytes. The IV is at 0x47f7d4. For each block, state = plaintext ^ previous ciphertext (IV for the first block). The VM program (0x401c90) runs 16 times over the state, and the state is the ciphertext block.
5. The 64-byte result is compared (0x401070) to the constant at 0x4803ee.
6. The functions at 0x401ea0 and 0x401f00 and the "ctf7{}" strings in libc are decoys. They are never used in the check.

## VM (state = 16 bytes, `a` = pred<<4 | dst)
| op | meaning |
|---|---|
| 0, 10 | nop |
| 1 / 12 | s[dst] += b (12 only if s[pred]&1) |
| 2 / 13 | s[dst] ^= b (13 conditional) |
| 3 / 15 | s[dst] = rol(s[dst], b) (15 conditional) |
| 4 | s[dst] -= b |
| 5 / 14 | swap s[dst], s[b&15] (14 conditional) |
| 6 | s[dst] += s[b&15] |
| 7 | s[dst] ^= s[b&15] |
| 8 | s[dst] *= (b\|1) |
| 9 | s[dst] = ror(s[dst], b) |
| 11 | s[dst] = rol(s[dst], s[b&15]) |

## Derivation
Every op is invertible. For conditional ops, `solve.py` checks whether the op was applied by testing the predicate bit before and after, and it found no ambiguous cases. It runs the rounds in reverse, 16 times per block, then un-CBCs against the target. The result is the ASCII word plus 6 zero bytes, which confirms the derivation.

Scripts: `solve.py` (run from this directory).
