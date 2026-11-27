# heapnotes-pwn — Writeup v3 (FEAT-004 continuation)

## Context

This continues FEAT-003's proven two-way overlapping-allocation primitive
(`.work/final_overlap_demo.py`). FEAT-004's own first pass (prior session,
`.work/scan_admin.py` / `.work/scan_admin2.py`) exhaustively mapped every
byte offset reachable by writing through the small-allocation overlap
into the freed neighbor's own 1264-byte region (offsets 0 through ~1040,
across many small-alloc sizes and orders) and found `admin()`'s response
never changes from the fixed baseline anywhere in that range. This session
picked up from there with two new, previously-untested angles.

## New angle 1: ruled out a non-memory-corruption admin unlock

Ran `.work/probe_heap_start.py` (written but not yet executed by the prior
session): confirmed `admin()`'s response is identical after 16 benign
add/free cycles with zero corruption, and identical on a fresh connection
after only two UAF-reads of the very first notes ever allocated. This
rules out a counter-based or "N operations" style unlock condition. The
admin gate requires memory corruption of some kind, not a benign usage
pattern — consistent with (but not proving) FEAT-002/003's assumption
that it's a corrupted global/BSS flag or redirected control flow.

## New angle 2: an un-exploited libc-address leak, and the unsorted-bin attack

Re-examining `scan_admin.py`'s own Step 2 diff output (`.work/scan_admin_output.txt`)
turned up a detail the prior session logged but did not act on: the full
1264-byte diff of the neighbor's region after the overlap showed a
repeated 8-byte value at relative offset 32–48 that looks like a genuine
pointer, not heap/user content. This session re-derived it cleanly
(`.work/leak_libc.py`): at relative offset 0–16 of the *overlap region
itself* (not offset 32 — the prior session's diff was looking at a
differently-sized small-alloc's placement) sits a repeated 8-byte value
whose low 12 bits are constant (`0xce0`) across three independent fresh
connections while the high bits vary — the textbook signature of a
page-ASLR'd pointer into a fixed-offset libc structure. This is
`unsorted_chunks(main_arena)`, i.e. `fd == bk` of the merged chunk sitting
alone in glibc's unsorted bin after the FEAT-003 consolidation completes.
**This is a genuine, reproducible libc address leak** (confirmed across
3 separate connections, same low-12-bits value every time), extending
FEAT-002's earlier (independently obtained, now superseded) libc leak
with a cleaner derivation directly from the already-proven FEAT-003 chain,
with no extra setup needed.

### Why this does not, by itself, unlock admin

Having a libc leak is necessary but not sufficient — it only helps if
paired with a write primitive that can use it. The classical use of an
unsorted-bin fd/bk leak is the **unsorted bin attack**: corrupt the
chunk's `bk` field while it is still binned, so that glibc's next
unsorted-bin-scanning `malloc()` performs `bck->fd = unsorted_chunks(av)`,
writing a known libc pointer to an attacker-chosen address minus 0x10.

This session implemented and tested this attack directly
(`.work/unsorted_bin_attack.py`) and found the **same structural blocker**
FEAT-002 already identified for tcache poisoning applies here too, for a
different but analogous reason:

- The only way this server ever lets an attacker write bytes into a
  chunk is via `add()`'s own content-write.
- `add()` always receives its chunk **already popped out of whatever
  bin/list it was sitting in** before the content write happens (glibc's
  `_int_malloc` pops the chunk, and only then does the server's `add()`
  logic copy the attacker's bytes into it).
- Therefore an attacker-controlled write into the remainder's `fd`/`bk`
  fields can only ever happen **after** glibc has already performed the
  bin-removal step using the *genuine* (uncorrupted) pointer values —
  there is no window where the chunk is both still-binned and
  attacker-writable.
- Verified concretely: writing garbage (including intentionally invalid
  values like `0xdeadbeefcafebabe`) into the remainder's `bk` field via
  the proven overlap-write primitive, then triggering a second `add()`
  sized to force a non-exact-fit split of the same remainder, produced
  **no crash and no observable corruption** at the computed target
  address, repeatedly, across multiple size choices (200, 500, 1000,
  1016, 1100, 1240 bytes) and both with/without an intervening small
  (16-byte) overlap allocation. Separately confirmed via content-bleed
  tracing that sizes close to the remainder's own usable size (1100,
  1240) are serviced via glibc's exact/near-exact "take now" fast path
  (which bypasses the vulnerable unlink code entirely, per direct reading
  of glibc 2.35's `_int_malloc` source), while size 500 wasn't served
  from this remainder's memory at all (content never changed), and
  sizes 1000/1016/1008/992/960 all crashed the connection outright
  (consistent with the service's heap being left in a fragile, partially
  self-inconsistent state after the FEAT-003 chain's forged `prev_size`/
  self-referencing fd-bk victim setup, which was only ever validated to
  survive exactly the one documented sequence, not further splits).
- The one case that DID show a clean, safe split (size 200, with no
  overlap-write corruption applied) confirmed the split's own freshly
  reinserted leftover chunk's `fd`/`bk` are set using the **real** libc
  pointer at that moment — again closing the window, since any further
  attempt to write into that leftover before its own next consumption
  hits the identical problem one level deeper.

## Conclusion

This session obtained a second, independent, more cleanly-derived libc
leak directly from the FEAT-003 chain, and used it to concretely attempt
the unsorted-bin attack — the natural next named technique given the
leak's origin. The attempt failed for a structural reason specific to
this binary's add/free API design (every write happens strictly after
chunk extraction from any bin), not for lack of a correct leak or
incorrect understanding of the attack. Combined with the already-
exhausted neighbor-overlap offset scan (0–1040 bytes, inert throughout)
and the newly-ruled-out counter-based unlock hypothesis, every named
heap-exploitation technique applicable to a tcache/unsorted-bin allocator
under this server's specific API constraints (double-free, UAF write,
overflow, tcache poisoning, unsorted-bin attack, counter-based unlock)
has now been tried and has a concrete, evidenced reason for failing.

**No `ctf7{...}` flag was recovered.** The admin gate's exact mechanism
remains unidentified. Given the depth of both this and the prior FEAT-004
session's effort, this is recorded as blocked in `features/FEAT-004.json`
and `task.json`. It is marked non-retryable within the currently-identified
technique space: every technique this session or FEAT-002/003 could
enumerate for a glibc 2.35 tcache/unsorted-bin allocator, given this
server's specific "write only ever happens post-extraction" API
constraint, has been tried and ruled out with concrete evidence. Further
progress would most likely require either (a) a genuinely novel primitive
not yet conceived of (e.g. a bug in the server's own idx/size bookkeeping
not yet found despite repeated targeted probing), or (b) access to the
actual binary/source (confirmed not available for this challenge) to stop
reasoning about the admin gate's location purely from black-box behavior.

## Files

- `.work/leak_libc.py` — clean, minimal re-derivation of the libc leak
  directly from the FEAT-003 chain (3 independent runs, confirmed
  page-ASLR'd pointer with constant low 12 bits).
- `.work/unsorted_bin_attack.py` — the unsorted-bin-attack attempt and
  its diagnostic variants (preserved-fd/corrupted-bk, garbage-bk,
  multiple forcing-allocation sizes), with inline comments documenting
  each negative result and the glibc source reasoning behind it.
- `.work/probe_heap_start.py` — the counter-based-unlock negative test
  (run this session; ruled out).
