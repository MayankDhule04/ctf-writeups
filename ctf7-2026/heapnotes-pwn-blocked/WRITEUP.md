# heapnotes-pwn — Writeup (FEAT-002)

## Target

`nc 91.99.207.116 16273` — plain TCP, no PIE, Partial RELRO, glibc 2.35
(stated by the challenge). No binary file was ever provided or found;
every fact below comes from live interaction with the running service.

## Protocol (from FEAT-001, re-confirmed, unchanged)

```
== noted ==
1) add
2) free
3) edit
4) show
5) admin
0) exit
>
```

- **add**: `idx` (0–15) → `size` (1–1280 inclusive) → exactly `size` raw
  bytes → `ok`.
- **free**: `idx` → `ok`, or `already free` on a double-free attempt, or
  `bad idx` out of range. Tracks a per-slot freed flag.
- **edit**: `idx` → exactly the *original* add-time `size` raw bytes →
  `ok`. Checks the same freed flag as `free` and returns `bad idx`
  immediately if the slot is freed — no UAF write.
- **show**: `idx` → exactly `size` raw bytes + `\n`. Does **not** check
  the freed flag — this is the one confirmed use-after-free primitive.
- **admin**: on a fresh/uncorrupted connection, immediately prints
  `[admin] no action configured` with no further prompt.
- **exit**: `bye`, closes the socket.

## Primitive confirmed in FEAT-001

`show` on a freed-but-not-reallocated idx returns live bytes straight
from the dangling heap pointer — a genuine use-after-free **READ**.
`free()` writes glibc's tcache safe-linked `fd`+`key` metadata into the
first 16 bytes of the chunk; everything past that is still the
original user content.

## What this feature (FEAT-002) found beyond FEAT-001

All of the following were tested empirically against the live remote
service (not assumed), using Python socket scripts built on FEAT-001's
helpers. Full session transcripts are embedded as comments/outputs in
the probe scripts kept under `.work/` in this task directory.

### 1. Tcache LIFO reuse and chunk aliasing — confirmed, but read-only

Freeing two same-size notes (`idx0`, `idx1`) and then adding two more
notes of the same size (`idx2`, `idx3`) shows exact LIFO reuse: `idx2`
gets `idx1`'s old chunk and `idx3` gets `idx0`'s old chunk. Using the
UAF-read primitive, `show(idx0)` after this sequence returns `idx3`'s
live content and vice versa — the dangling pointers truly alias live
memory. This is a stronger demonstration of the UAF read (it can leak
*any* subsequently-added live note's content via an older, freed idx
of the same size), but it is still strictly read-only: `edit` on the
freed idx (`idx0`/`idx1`) remains blocked by the freed-flag check, so
there's no way to write into the aliased chunk through the freed idx.

### 2. Unsorted-bin exact-size reuse and a genuine libc leak

Requests above `tcache_max` (empirically found between 1032 and 1040
bytes, consistent with glibc's default `0x410`-byte tcache chunk-size
ceiling) are **not** tracked by tcache. Freeing such a chunk — as long
as it isn't adjacent to the heap's top chunk (achieved by allocating a
second large note *after* it) — inserts it into the **unsorted bin**
instead. Unsorted-bin `fd`/`bk` pointers are **not** safe-link-mangled
(mangling is tcache-only), so `show` on the freed idx leaks a raw
pointer: `fd == bk == unsorted_chunks(main_arena)`, i.e. a fixed offset
into `main_arena` inside libc itself.

To turn this into a libc base, this session downloaded Ubuntu 22.04's
real `libc6_2.35-0ubuntu3.18_amd64` package and its matching
`libc6-dbg` package directly from `security.ubuntu.com` (open internet
access was available), extracted the DWARF debug info for `struct
malloc_state`, and confirmed:

- `main_arena` symbol offset in that libc build: `0x21ac80`
- `offsetof(malloc_state, bins)`: `0x70`
- `unsorted_chunks(av)` (the fd/bk value when exactly one chunk sits in
  an otherwise-empty unsorted bin) = `&bins[0] - 16` = `main_arena + 0x60`

So `libc_base = leak - (0x21ac80 + 0x60)`. Running this against the
live remote service repeatedly gives a **page-aligned** result every
time (`exploit.py`'s output confirms `libc_base & 0xfff == 0`), which
is strong, reproducible confirmation that this leak and offset
arithmetic are correct for the real remote glibc build.

This is a genuine capability beyond FEAT-001 (a libc base leak, not
just an opaque heap-metadata leak), but a leak alone does not unlock
the admin gate.

### 3. Searched for a write primitive — none found

Every known technique that would turn the leak into control was tried
against the live service and failed for a structural reason specific
to this binary's implementation, not a missing idea:

- **tcache fd-pointer poisoning**: requires writing a forged pointer
  into a chunk's `fd` field *while that chunk is still sitting unpopped
  in the tcache freelist*. The only way this service ever lets you
  write chunk content is via `add()`, and `add()` always **pops** the
  chunk off the freelist and hands it to the caller *before* any user
  bytes are written. There is no code path that writes into a chunk
  that is still in a freelist — so an attacker can never control what
  a *future* `add()` call will receive. Verified by reasoning through
  glibc's `tcache_get()` (which already advances the freelist head
  before returning the chunk) and confirmed consistent with every
  probe above.
- **Unsorted-bin attack** (classically used to corrupt
  `main_arena.top` via a chunk's `bk` field before it's consumed): same
  structural blocker as above — no write-while-still-binned primitive.
- **Double-free via `free()`**: blocked (`already free`), confirmed in
  FEAT-001 and re-confirmed here even across chunk-reuse chains (e.g.
  freeing `idx0`, having `idx1` legitimately reuse its chunk, then
  trying to free `idx0` again still correctly returns `already free`
  — the per-idx flag is tracked independently of the underlying
  chunk's reuse history).
- **UAF write via `edit`**: blocked — `edit` checks the same freed flag
  as `free` and refuses with `bad idx` on any freed idx, even when
  that idx's old chunk has since been reused by a different live idx.
- **Heap/buffer overflow via `add`/`edit`**: `add` enforces a hard,
  deterministic `1 ≤ size ≤ 1280` bound (binary-searched and confirmed
  in FEAT-001); `edit` always reads back exactly the original add-time
  size, never more, even when more bytes are sent (the extra bytes are
  simply left unconsumed in the socket). No scanf-level integer
  overflow bug was found either: sizes like `2147483647`, `2^32`,
  `2^64-1`, and negative values are all rejected with `bad size`.
- **idx bounds bypass**: tried negative values, huge values, hex/octal
  literal forms (`0x10`, `007`) — the index check is a strict,
  symmetric `0 ≤ idx ≤ 15` with no parsing quirk found.
- **Admin-gate-by-content heuristics**: tried writing literal strings
  `"admin"`/`"ADMIN"`, all-zero and all-`0xff` patterns into note 0,
  and tried calling `admin` with all 16 slots live, then with all 16
  freed. No change in behavior in any case — the gate is not a simple
  "does note 0 contain a magic string" check reachable without memory
  corruption.
- **Tcache/chunk-size-class aliasing** (two different requested sizes
  landing in the same glibc chunk-size bucket, e.g. request sizes 17
  and 24 both using a 0x20 chunk): confirmed this sharing happens, but
  `show` always returns exactly the *requesting* idx's own original
  size, never the larger neighboring size, so there's no accidental
  over-read/over-write leak through this path either.
- **Unused (never-`add`ed) slot**: `show`/`edit`/`free` on a slot that
  was never allocated all return `bad idx` outright (not even a UAF
  read), consistent with the manager defaulting an unused slot's
  pointer to NULL/treating it as already-freed, and checking that
  before dereferencing.

## Conclusion

The admin gate almost certainly is flipped by corrupting a global flag
or redirecting control flow via a GOT overwrite (the challenge's No
PIE / Partial RELRO hints point exactly at this), and this session
obtained a genuine, reproducible libc base leak that would be a
necessary ingredient for such an attack. However, after exhaustively
retesting every documented heap-exploitation technique applicable to a
tcache/unsorted-bin-based allocator (tcache poisoning, unsorted-bin
attack, double-free, UAF write, overflow, integer overflow, and
several non-standard chunk-aliasing variations) against the live
remote service, **no primitive was found that can write attacker-
controlled data into any memory the attacker does not already
legitimately own**. Every write path (`add`, `edit`) is strictly
bounds- and ownership-checked in a way that specifically closes off
the usual tcache-poisoning timing window (writes only ever happen
*after* a chunk has already been popped off the freelist and handed to
the caller, never before).

**No flag was recovered.** `exploit.py` demonstrates the libc leak
honestly and reports this blocker rather than fabricating a result —
see its run output in `solve_output.txt`. This is recorded as a
blocked (but documented, with a concrete leaked capability) outcome in
`features/FEAT-002.json`.

## Files

- `exploit.py` — runs the libc-leak primitive against the real remote
  service and clearly reports that no flag was obtained, with the
  reasoning above summarized inline.
- `solve_output.txt` — actual captured output of a real run of
  `exploit.py` against `91.99.207.116:16273`, confirming the leak is
  reproducible and page-aligned, and confirming no flag string
  appeared.
- `.work/probe_*.py` — the additional probing scripts used to test the
  tcache-aliasing, unsorted-bin, idx/size-boundary, and admin-content
  hypotheses described above.
