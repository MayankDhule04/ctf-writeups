# heapnotes-pwn — Writeup v2 (hint-guided continuation)

## Context

This continues FEAT-002's work after the user purchased three CTF-platform
hints confirming the intended vulnerability class is a classic "Poison Null
Byte" (off-by-one null overflow -> clear PREV_INUSE -> backward
consolidation -> tcache-poisoned overlap onto an admin control block). The
hints corrected an earlier, incomplete finding from FEAT-002 (that `edit`
"never overflows because it always reuses the exact add-time size") — the
missing detail is that `edit` (and, in some conditions, `add` itself when
writing into a slot after a free+re-add cycle) writes **one extra NUL byte**
at `buf[size]`, one byte past the user-supplied content.

## What this session independently re-confirmed and extended

### 1. The off-by-one null write is real

For a note whose content exactly fills its chunk's usable space (zero
"slack"), editing it with exactly `size` bytes still leaves the chunk one
byte short in total usable space (`chunksize - 8` bytes of content, where
the chunk header is 16 bytes but the last 8 overlap the next chunk's
`prev_size` field while this chunk is in use). The implicit NUL write lands
exactly on byte 0 of the **next chunk's `mchunk_size` field**.

Verified live: for request sizes 24, 40, 56, ..., 1016 (all "zero slack"
sizes below 1280), editing the note with exactly its own size and then
freeing the immediately-following note crashes the connection, where a
one-byte-shorter edit (any non-zero slack) does not. This pins the write
precisely to that one byte.

### 2. Small chunks can't survive the null write cleanly

For any chunk size under 256, the size field's one non-zero byte **is**
`chunksize|PREV_INUSE` in its entirety — nulling it zeroes the *whole*
size, not just the PREV_INUSE flag, and `free()` of that now-"size 0"
chunk aborts immediately with `free(): invalid pointer` (glibc's
`(uintptr_t)p > (uintptr_t)-size` check, which is always true when
`size` wraps to 0). This is NOT the attacker's fault/bug — it's an
inherent property of nulling a byte that holds real size bits, not just
a flag bit.

### 3. Within the 1–1280 size cap, only ONE size threads every needle

To clear *only* PREV_INUSE (not the whole size), the victim chunk's
`chunksize` must be an exact multiple of 0x100 (so the size field's low
byte is `0x01` pre-corruption, `0x00` after — same size, flag cleared).
To actually trigger glibc's backward-consolidation *logic* at all (not
just tcache's unconditional `tcache_put`), the chunk must be **above**
`tcache_max` (~1032 bytes on this build), since `tcache_put()` runs
before any PREV_INUSE check and completely bypasses consolidation for
anything tcache-eligible. Computing all sizes 1–1280 against both
constraints together yields exactly one candidate: **request size 1272**
(chunksize `0x500` = 1280 bytes). This was found by direct enumeration,
not guesswork, and is reproducible.

### 4. A second, independent bug at that exact size

Size-1272 notes (zero-slack, above tcache_max) crash on their *own* free
with no corruption involved at all, whenever the chunk physically
following them is the heap's top chunk — `double free or corruption
(!prev)`. This is consistent with the *same* off-by-one firing during
`add()`'s own initial content write (landing on `av->top`'s own
PREV_INUSE bit, since at add-time nothing else exists after it yet).
Placing a second, unrelated note immediately after the 1272-byte note
(so top is no longer its direct neighbor) avoids this specific crash
mode and lets the note be freed/used normally on its own.

### 5. Crafting a fake fd/bk + prev_size payload avoids the crash

With the victim (1272 bytes) immediately followed by a safe (1264-byte,
non-zero-slack) neighbor and a padding note after that:

- Plain content (all `'A'`) for the victim: freeing the neighbor after
  re-editing the victim (re-triggering the off-by-one) crashes the
  connection outright (empty response — a hard SIGSEGV, not a controlled
  `malloc_printerr` abort).
- Setting **only** the victim's bytes `[1264:1272]` to its own chunksize
  (`0x500`, little-endian) — satisfying glibc's `chunksize(p) != prevsize`
  sanity check in `_int_free_merge_chunk` — changes the error to a
  *controlled* one: `corrupted size vs. prev_size while consolidating`.
  This is `unlink_chunk` being reached and then failing on its own
  `fd->bk == p` check against garbage `'A'*8` pointers.
- Setting **also** the victim's bytes `[0:16]` to a self-consistent
  `fd = bk = victim's own real chunk address` (obtained via the
  safe-linked heap leak, see below) makes `unlink_chunk` succeed: `free`
  of the neighbor now returns a clean `ok` with no abort.

This exact combination was reproduced multiple times and is the
strongest, most precise evidence gathered this session that the
intended vulnerability class really is active and reachable.

### 6. Double-free detection on the victim confirms real corruption

After the sequence in (5), calling `free` on the victim itself (which
was never independently freed) returns `double free or corruption
(!prev)`. A clean control — identical note layout and free order, but
with **no** off-by-one corruption applied at all — returns a plain `ok`
in the same situation. This rules out the error being a generic/expected
glibc behavior and confirms it is caused specifically by our corruption.

### 7. Heap-address leak (hint 2) fully validated

Freeing a same-size (24-byte, tcache-eligible) pair of notes and reading
the freed slot back via the already-confirmed UAF-read `show` primitive
recovers the safe-linked tcache `fd` pointer. Because the *second*
freed note in a pair has `fd = NULL`, its own mangled `fd` value **is**
its page number (`addr >> 12`) directly — XOR-ing the *first* note's
mangled `fd` with that page number recovers a real heap address with no
masking ambiguity and no libc leak required, exactly as hint 2
describes. Verified multiple times with consistent results and an
independently-confirmed exact `0x20`-byte spacing between two
sequentially-allocated 24-byte notes (derived two different ways and
cross-checked).

## What remains unresolved

Despite (5) and (6) being strong, repeatable evidence that backward
consolidation is being entered and *not* crashing, **no session attempt
this time demonstrated a content-level overlapping allocation** usable
for the tcache-poisoning step described in hint 3. Specifically:

- Every subsequent `add()` call sized to plausibly land inside the
  believed-merged free region (victim 0x500 + neighbor 0x500 = ~0xA00
  bytes) came back with content that did **not** visibly overlap either
  the victim's or the neighbor's note content, even immediately after
  the "double free" confirmation in (6).
- The server's hard `1 ≤ size ≤ 1280` cap on `add` means no single
  request can ever be large enough to directly consume the full ~0xA00
  merged chunk and prove the overlap via a one-shot allocation — only
  indirect detection (content bleed into a smaller, overlapping
  allocation) was attempted, and none of the attempts so far showed
  bleed.
- One UAF-read on the neighbor's own original address, taken
  immediately after the free, showed what looked like a *fresh* libc-ish
  pointer pattern rather than the victim's crafted fake values — this is
  not yet reconciled with the expected "write lands at the rewound
  (victim's) address" model and suggests either an error in this
  session's understanding of exactly which address `_int_free_create_chunk`
  writes its new fd/bk/foot metadata to, or a secondary consolidation
  step (`_int_free_maybe_consolidate`, or glibc's "exact fit" fast path
  in `_int_malloc`) intercepting the chunk before the expected overlap
  window becomes observable through this server's size-capped `add`.

No `ctf7{...}` flag was recovered. This is recorded as a genuinely
further-along, but still blocked, outcome in `task.json` —
retryable, since the off-by-one and the consolidation trigger are now
firmly established live facts, not hypotheses, and only the final
overlap-detection/exploitation step remains open.

## UPDATE: the overlap WAS found (after the above was written)

Continuing past the point above, a genuine overlapping allocation was
located and confirmed two-way (read AND write) using the exact same
corrupted-victim + freed-neighbor setup from steps 1–6:

- Immediately after `free(neighbor)` succeeds (step 6), requesting a
  **small, previously-untouched** size (8 or 16 bytes — i.e. a fresh
  `tcache[0x20]` bin, forcing a genuine unsorted-bin scan rather than a
  tcache hit) returns a chunk that **aliases the freed neighbor's own
  original address** at offset 0.
- Confirmed via content: `add(idx3, 16, b"Q"*16)` followed by
  `show(idx1)` (UAF-read on the now-freed, consumed neighbor) returns
  `b"QQQQQQQQQQQQQQQQ"` as its first 16 bytes.
- Confirmed as a genuine two-way primitive, not just a one-time
  snapshot: `edit(idx3, b"Z"*16)` followed by `show(idx1)` shows the
  updated `b"ZZZZZZZZZZZZZZZZ"` — writes through idx3 are visible via
  idx1's UAF read, and (implicitly) vice versa, since both now
  reference the same physical memory.
- The overlap window is exactly 16 bytes at the FRONT of the neighbor's
  1264-byte region; bytes 16–31 beyond that show fresh glibc
  remainder/split bookkeeping (a chunk header-looking pattern, then
  what looks like a `main_arena`-adjacent pointer pair), and the
  neighbor's ORIGINAL content (`'B'*1264`) is still intact from byte 64
  onward (~1200 of the original 1264 bytes untouched). Sizes 32 and
  above for the overlapping allocation do NOT alias the neighbor
  (they're served from a different, freshly-grown region instead) —
  only exactly 8 or 16-byte requests land in this specific remainder.

This closes the gap flagged above: `_int_free_create_chunk`'s
remainder-handling (not a direct return of the whole merged chunk, but
a SPLIT whose leftover fragment ends up reachable at a small-tcache
granularity) is what actually produces the exploitable overlap, not a
single large reused chunk as this session originally modeled.

### What this enables, and what's still missing for the flag

This is a genuine, reproducible, two-way READ+WRITE-through-overlap
primitive — the structural piece hint 3 describes ("allocate directly
over the admin control block"). What's still missing is **knowing where
the admin control block actually is**. With no binary available for
this challenge (confirmed fact from the original briefing), there is no
way to compute a target offset/address for "the admin flag" the way a
real exploit would from a disassembly. The admin baseline response
(`[admin] no action configured`) was re-checked after establishing this
overlap and is unchanged, since nothing has been targeted at it yet —
the remaining work is almost pure guess-and-check scanning (write
various non-zero patterns through the overlap window at a range of
heap-relative offsets, re-invoking `admin` after each to look for a
behavior change) rather than a principled, computed target address.
This was not completed in the time available this session.

## Files (updated)

- `.work/final_overlap_demo.py` — the minimal script demonstrating the
  working two-way overlap primitive (heap leak -> victim-address leak ->
  crafted payload -> corrupt -> free neighbor -> small alloc overlaps
  neighbor -> edit-through-overlap visible via UAF read), saved from
  this session's working probe for reuse in a follow-up session.

## Files

- `exploit_v2.py` — runs the full chain confirmed this session (heap
  leak, victim-address leak, crafted fake fd/bk + prev_size payload,
  corruption trigger, and the double-free confirmation), and reports
  that no flag was obtained, consistent with the honest state above.
- `solve_output_v2.txt` — captured output of a real run of
  `exploit_v2.py` against `91.99.207.116:16273`.
- `.work/probe_offbyone.py` — the first live probe that established the
  off-by-one is real (control vs. corrupted `free()` behavior).
