# Rampart gate controller — UDS security access (Black Hat India 2026 CTF)

**Status: UNSOLVED.** This documents the full reverse-engineering done so
far (protocol, firmware key-derivation algorithm, verified real seed/key
pairs) and the specific point it's blocked on, so a future attempt
doesn't have to redo the recon.

## Prompt (paraphrased)

Eight "Rampart" gate controllers guard a wall. Each controller holds a
"master release code" readable only after unlocking UDS security access
(SID `0x27`). One controller (Millrace / NW-02) is on the bench with its
GW-4 CAN gateway attached, reachable as a raw TCP console
(`ncat --ssl <host> 443`). The same host:port also serves an HTTP "fleet
console" (signin, firmware downloads, candump capture browser). Read the
master release code off the bench controller.

## Protocol (from `/docs`, fully documented by the challenge itself)

- Transport: ISO 15765-2 (ISO-TP) over classic 8-byte CAN frames, normal
  addressing. Request ID `0x7A0` (physical) / `0x7DF` (functional),
  response ID `0x7A8`.
- Console syntax mirrors `cansend`/`candump`: `<id>#<data>` sends a frame,
  `filter`, `mode log|dump`, `reset`, `quit`.
- UDS services in play: `10` (diagnostic session control — need extended
  session `10 03`), `3E` (tester present, keeps session alive), `27`
  (security access: `27 01` seed request, `27 02` key response), `22`
  (read data by identifier).
- Target: `D1F0` = "Master release code... Level 1" protected DID.
- Security access timing rules: 10 s lockout after power-on before any
  seed request; seeds at most one per 500 ms; each seed accepts exactly
  one key; 3 wrong keys → NRC `36` + another 15 s lockout (not cleared by
  `reset`).
- **Release notes for firmware 3.2.0** state explicitly: *"the key routine
  is now keyed by the site provisioning record (`sa_l1`) that the site
  controller writes to the gateway at every boot. It is no longer
  compiled into the image... each settlement gets its own record."*

## Artifacts obtained from the fleet console

Signed in with any callsign (`POST /signin`, "any callsign works on the
bench network"), then downloaded via `/downloads/*`:

- `rampartd` — the gateway firmware binary (stripped x86-64 ELF).
- `candump-2026-11-18_062842.log` — a real capture from a prior service
  visit on the same bench controller, including several successful
  security-access seed/key exchanges.
- `RELEASE-NOTES.txt` — confirms the `sa_l1` provisioning-record design
  above.

## Reversing the key algorithm (`rampartd`, stripped, no symbols)

Traced from the provisioning-file parser (`fopen("/tmp/state/rampart.prov")`,
line-by-line `fgets`, matching the literal prefix `"sa_l1="`, then
`strtoull(..., 16)` — parsed as one 64-bit value, split into two 32-bit
globals at runtime: the **low** 32 bits and **high** 32 bits of `sa_l1`).
Found the only other code reading those two globals — the actual
seed→key verification routine — and transcribed it instruction-by-
instruction into Python/C:

```c
static const uint32_t TABLE[6] = {
    0x9e3779b9u, 0x7f4a7c15u, 0xf39cc060u,
    0x5cedc834u, 0xb1a83721u, 0x2f2e1e8bu
};
static const uint32_t MUL_CONST = 0x2c1b3c6du;

uint32_t compute_key(uint32_t seed, uint32_t lo, uint32_t hi) {
    uint32_t eax = seed ^ lo;
    uint32_t ecx = hi - 1u - seed;
    for (int i = 0; i < 6; i++) {
        uint32_t edx = eax * eax;
        edx |= 5u;
        edx += eax;
        uint32_t e2 = TABLE[i] + edx;
        e2 ^= ecx;
        ecx = e2 * MUL_CONST;
        uint32_t shl = (e2 << 7) ^ hi;
        ecx += shl;
        eax = lo + ecx * 8u;
        eax ^= edx;
    }
    uint32_t lo2 = (lo + lo) ^ ecx;
    return eax ^ lo2;
}
```

(a 6-round custom hash/MAC, golden-ratio-style round constants, keyed by
the 64-bit `(lo, hi)` provisioning secret — not a standard/named
algorithm.)

## Ground-truth seed/key pairs extracted from the candump capture

```
grep -E "can0 7A0|can0 7A8" candump-2026-11-18_062842.log
```

Parsing the `67 01 <seed>` / `27 02 <key>` exchanges gives 5 real pairs
from this exact bench controller (one of them, for seed `95E7C9FE`, was
rejected by the controller with NRC `35` — per the release notes, that
was an **old (3.1-algorithm) Service Tool build's first, wrong-algorithm
guess**, not a valid pair, and was excluded):

```
seed=D55A6C60 key=14C6F953
seed=93670AC6 key=9B08666F
seed=ED318559 key=A9F3F925
seed=7DE5E946 key=6E45C36F
```

Verified the `compute_key()` transcription against single-32-bit-half
brute force (confirmed `lo=0`/`hi` alone and `hi=0`/`lo` alone both fail
to satisfy all 4 pairs simultaneously — any apparent single-pair match
found this way is a 1-in-2^32 coincidence, not the real secret) — the
transcription itself is very likely correct, but the real `sa_l1` has
non-trivial values in both halves.

## Where it's blocked

`sa_l1` is a genuine 64-bit secret with (as far as reverse engineering
shows) no algebraic shortcut: both halves mix nonlinearly into every
round via multiply/shift/xor, with no round whose output depends on only
one half given a known seed. A full 64-bit brute force (even highly
optimized C doing ~10^8-10^9 checks/sec) is many orders of magnitude out
of reach (~2^64 ≈ 1.8×10^19 candidates). No weaker side channel (seed
predictability, provisioning-value reuse, a debug/default fallback value
in the binary, an alternate unprotected path to `D1F0`) was found either.

Open question for a future attempt: does the SAME `sa_l1` the capture
used still apply to a fresh live connection ("every console connection is
its own power-on of the controller" strongly suggests it might be
re-randomized per connection, which would make recovering the historical
capture's secret pointless regardless of brute-force feasibility) — this
was never confirmed either way. Also hit an unexplained, inconsistent
TCP/TLS demultiplexing issue on this challenge's port 443 (sometimes
routes to the raw gateway console, sometimes to the HTTP fleet console,
for byte-identical client requests) that intermittently blocked live
interaction entirely during this attempt.
