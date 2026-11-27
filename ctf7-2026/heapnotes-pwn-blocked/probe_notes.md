# FEAT-001 Probing Findings — heapnotes-pwn

Target: `nc 91.99.207.116 16273` (plain TCP). No PIE, Partial RELRO, glibc 2.35
(stated by challenge). No binary file is available; all findings below are from
live protocol probing. Full raw transcripts: `transcript.txt` (appended in
sections, in chronological order) and ad-hoc one-off scripts
(`probe.py`, `probe2.py`) used to generate them.

## Banner / menu (reconfirmed)

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

## 1. `add` (option 1) — idx bounds

Prompt sequence: `idx: ` -> integer -> `size: ` -> integer -> `data: ` -> exactly
`size` raw bytes (confirmed earlier during planning; still holds).

- Valid idx range: **0–15 inclusive (16 slots total, N=16)**.
  - idx 0..15 all accepted (`ok`).
  - idx 16, 31, 32, 63, 64, -1, 99, 1000 all rejected with `bad idx`.
- So the note table is a fixed array of 16 slots, each presumably holding a
  pointer + size + a freed flag.

## 2. `add` (option 1) — size bounds

- size `0`, `-1`, `-8` -> `bad size` (zero and negative rejected).
- size `1` through **`1280`** (0x500) -> accepted, `data: ` prompt appears,
  exactly that many raw bytes are read, returns `ok`.
- size `1281` and anything above (1300, 1390, 1400, 1500, 2000, 3000, 4000,
  4080, 4088, 4095, 4096, 65536) -> `bad size`.
- **Exact upper bound confirmed by binary search: max size = 1280 bytes
  (inclusive), first rejected value = 1281.** 1280 = 0x500, not a standard
  malloc chunk-size constant, so this is very likely an explicit
  `if (size <= 0 || size > 1280) { "bad size" }` check in the add handler
  rather than a glibc-chunk-derived limit. This means a straight
  oversized-write-via-`add` heap overflow is NOT available — size is
  strictly bounds-checked and the raw read never writes past the requested
  allocation at add time.
- Note: an early, hastier probing pass showed inconsistent results for sizes
  in the 1024–1390 range (same size sometimes "ok", sometimes "bad size")
  purely because the probe script's `recv()` calls weren't waiting long
  enough for the full multi-piece response — this was a client-side bug, not
  server non-determinism. Re-tested with a proper buffering loop and results
  are now 100% consistent across repeats (verified 5x per size at 1024, 1300,
  1400).

## 3. `free` (option 2)

Prompt sequence: `idx: ` -> integer -> `ok\n` (or error) -> menu.

- Freeing a valid, currently-allocated idx -> `ok`.
- **Freeing the same idx a second time (double-free) is explicitly rejected:
  `already free\n`.** So the manager tracks a per-slot "freed" boolean and
  checks it in the `free` handler — a raw double-free-via-`free` is NOT
  available as a primitive.
- Freeing an out-of-range idx (e.g. 99) -> `bad idx` (same bounds check as
  add).

## 4. `edit` (option 3)

Prompt sequence: `idx: ` -> integer -> `data: ` (no size re-prompt) -> exactly
the ORIGINAL add-time `size` bytes are read, then `ok`.

- Edit reuses the size recorded at add time; it does not ask for a new size
  and sending more bytes than the original size does not get fully consumed
  into the buffer (tested: added idx0 with size=8, then on edit sent 16
  bytes — server read the first 8 directly into the chunk and returned `ok`
  immediately; the extra 8 bytes were left unread in the socket, which then
  got consumed by the next command token, desyncing our own probe script's
  parsing until we reconnected). So **edit cannot be used to overflow past
  the original allocation size** — this is a straight fixed-length
  overwrite, not an overflow primitive.
- **Edit explicitly checks the same per-slot "freed" flag that `free` sets:
  calling edit on a freed idx returns `bad idx` immediately (no `data: `
  prompt), confirmed by sending `3\n` -> `0\n` on a freed idx0 and getting
  `bad idx` directly.** So there is NO UAF-write primitive via `edit`.

## 5. `show` (option 4) — UAF READ CONFIRMED

Prompt sequence: `idx: ` -> integer -> raw content bytes + `\n` -> menu.

- Show on a live, non-freed idx returns exactly the stored content, as
  previously confirmed.
- **Show on a freed idx does NOT check the freed flag and still returns data
  from the (now-freed) underlying heap chunk — this is a confirmed
  use-after-free READ primitive.** Unlike `add`/`edit`/`free`, the `show`
  handler apparently reads directly through the stored pointer without ever
  consulting the per-slot freed boolean.

  Example (24-byte note, content `'E'*24`, freed, then shown again without
  re-adding):
  ```
  show idx0 BEFORE free -> b'EEEEEEEEEEEEEEEEEEEEEEEE\n...'
  free idx0               -> b'ok\n...'
  show idx0 AFTER free  -> b'-$\x03\x00\x00\x00\x00\x00\x9a#\x03\x85\x1b\x85.\x92EEEEEEEE\n...'
  ```
  The leaked 24 bytes split as: 8 bytes that change on every repeated
  trial (consistent with a heap/libc pointer — looks like a tcache
  **safe-linked** `fd` pointer, since safe-linking XORs the real pointer
  with `(address_of_chunk >> 12)`, which combined with No-PIE heap base
  randomization explains why trial-to-trial values differ while high bytes
  stay `0x00`), then 8 more bytes that look like a `key`/second pointer
  field, followed by the leftover 8 bytes of the original `'EEEEEEEE'`
  content (the last third of the 24-byte buffer, since the first 16 bytes
  got overwritten by the tcache free-list metadata written into the chunk
  by `free()`, and the manager's `show` just dumps all `size` bytes
  verbatim from the chunk regardless of what's currently stored there).

  Repeating this 3x on fresh connections (`probe2.py`, Section 10) shows the
  first 8 bytes change every time (heap ASLR / safe-linking), consistent
  with a real pointer leak rather than a static/stale buffer artifact:
  ```
  trial0: b9 81 00 00 00 00 00 00 ...
  trial1: e5 59 02 00 00 00 00 00 ...
  trial2: 0d 12 02 00 00 00 00 00 ...  (two-note variant)
  ```

- Freeing TWO notes of the same size (idx0 and idx1, both 24 bytes) and
  showing both via UAF read shows idx0's leaked "fd"-like field differs from
  idx1's but idx1's trailing `key`-like 8 bytes (`\x1d4\xcf]Jgr5`) MATCH
  idx0's trailing field exactly in that trial — consistent with tcache's
  `key` field being set to the same per-tcache-struct value for chunks freed
  into the same bin in the same connection (glibc 2.35 tcache double-free
  detection `key` field, which is per-`tcache_perthread_struct`, i.e. per
  connection/process here, not per-chunk) — further evidence this leak really
  is tcache freelist metadata, not garbage.

- Re-adding into a previously-freed idx (`add` again on idx0 after it was
  freed) works normally and clears the UAF window for that idx (the slot's
  freed flag is reset and `show` returns the newly-written content again) —
  so the UAF read window only exists between `free` and the next `add` that
  reuses that exact idx.

## 6. `admin` (option 5) and `exit` (option 0)

- On a completely fresh connection (no notes touched at all), `admin`
  immediately prints `[admin] no action configured\n` then the menu — no
  further prompts, reconfirmed.
- `exit` sends `bye\n` and closes the connection (no further prompts),
  confirmed.

## Summary / viable primitive for FEAT-002

- **No raw double-free** (free() checks a per-slot freed flag).
- **No edit-based overflow** (edit reuses the exact original size, and also
  respects the freed flag, so no UAF write via edit either).
- **No add-based oversized write** (add has a hard, consistent `size <= 1280`
  bound enforced server-side).
- **Confirmed UAF READ primitive via `show` on a freed-but-not-reallocated
  idx.** This leaks live heap/tcache metadata (looks like safe-linked `fd`
  pointer + `key` field) directly into the connection, which is a strong
  starting point for leaking a heap address (to compute the heap base, since
  No PIE + safe-linking means `fd_mangled = (freed_chunk_addr >> 12) ^
  real_fd`, and `real_fd` is itself a heap address inside the same mapping,
  letting a solver recover the heap base with just arithmetic — no separate
  libc leak needed for that part).
- Since there is no UAF **write** via the note API itself, FEAT-002's path to
  the admin gate most likely needs one of:
  1. A secondary primitive not yet probed in FEAT-001 (e.g. whether `add`
     can be made to allocate a chunk that overlaps a still-live note's
     memory by manipulating tcache's freelist via this read-only leak —
     e.g. use the leaked `fd` value together with safe-linking math to
     predict what idx/size combination would cause a *future* `add` to be
     handed back a chunk at a chosen address), combined with the already
     fixed, small idx/size space (16 slots, size<=1280) to reason about tcache
     bin reuse order (LIFO) deterministically.
  2. Determining whether the admin-check variable lives in a heap chunk
     reachable by controlling tcache bin reuse, or in a global/bss variable
     near the note table that might be corrupted by some adjacency not yet
     tested (e.g. does the note struct array itself live on the heap near
     an admin flag, discoverable by leaking enough forward bytes via a
     larger note's UAF read).
  This exploration is explicitly FEAT-002's job, not FEAT-001's — this
  feature's scope was limited to establishing ground truth about the
  primitives, which is now done.

## Confirmed facts recap (for FEAT-002 to build on)

| Item | Value |
|---|---|
| Max notes / idx range | 0–15 (16 slots) |
| Size bounds for add | 1 to 1280 inclusive; 0, negative, and >1280 rejected with `bad size` |
| Double-free via `free` | Blocked (`already free`) |
| UAF write via `edit` | Blocked (`bad idx` on freed slot) |
| UAF read via `show` | **Confirmed working** — leaks tcache fd/key metadata + leftover old content |
| Overflow via oversized add/edit | Not possible (size strictly bounds-checked, edit reuses fixed size) |
| admin baseline (fresh conn) | `[admin] no action configured` |
