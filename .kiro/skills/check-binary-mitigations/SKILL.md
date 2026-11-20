---
name: check-binary-mitigations
description: Check a binary's security mitigations (NX, RELRO, PIE, stack canary, stripped status, architecture) before attempting any reverse engineering or exploitation. Use when starting analysis of an ELF/PE binary for a pwn or reversing CTF challenge, or when deciding which exploitation technique is viable.
---

## Why this comes first

The mitigations enabled on a binary determine which exploitation techniques
are even possible. Skipping this step leads to wasted time attempting
ret2libc on a binary with full RELRO+PIE+canary, or hand-rolling shellcode
injection on a binary where NX makes that a dead end from the start.

## No `checksec` binary available? Derive it manually

If the `checksec` / `checksec.sh` tool isn't installed, get the same
information directly:

```bash
file <binary>                      # architecture, stripped?, PIE (shared object) vs. no-PIE (executable)
readelf -h <binary>                # ELF header: Type DYN=PIE, EXEC=no PIE
readelf -d <binary> | grep -i bind_now   # BIND_NOW present = full RELRO
readelf -l <binary> | grep GNU_RELRO     # GNU_RELRO segment present = partial RELRO at least
readelf -d <binary> | grep -i flags      # look for NOW flag too
objdump -d <binary> | grep -m1 "__stack_chk_fail\|stack_chk"  # canary present if this symbol is referenced
readelf -h <binary> | grep "Type:"       # EXEC vs DYN again, cross-check
```

Quick interpretation table:

| Check | How to tell | Impact |
|---|---|---|
| **PIE** | `readelf -h` Type is `DYN` | Base address randomized; need an info leak before using any hardcoded address |
| **NX** | `readelf -l` has a `GNU_STACK` segment without the `E` (execute) flag | Can't execute shellcode on the stack directly — need ROP/ret2libc |
| **Stack canary** | `__stack_chk_fail` referenced; `fs:0x28`/`fs:[0x28]` loaded near function prologue | Simple stack buffer overflows need a canary leak/bypass first |
| **RELRO (full)** | `BIND_NOW` flag present | GOT is read-only after startup — GOT overwrite attacks don't work |
| **RELRO (partial/none)** | `GNU_RELRO` segment present but no `BIND_NOW` | GOT overwrite may still be viable |
| **Stripped** | `file` says "stripped"; `nm` shows no symbols | No function names — expect to work from raw addresses/disassembly; a decompiler (Ghidra/Cutter) pays off disproportionately here |

## What to do with the result

- **No canary + no PIE + no NX**: classic stack smashing, straightforward shellcode injection.
- **NX, no canary, no PIE**: ROP chain to `system()`/`execve()`, addresses are fixed.
- **NX + PIE, no canary**: need an info leak (format string, buffer over-read) to defeat ASLR before building the ROP chain.
- **Canary present**: need to leak or brute-force the canary (fork-based brute force works if the binary forks per connection) before a classic stack overflow works; or look for a bug that bypasses the canary check entirely (e.g. overwriting a saved pointer before the canary in memory, not past it).
- **Full RELRO**: GOT hijacking is closed — look at other write-what-where targets (stack return address, function pointers in writable memory, `.fini_array`/`.init_array` if not protected).
- **Stripped binary with embedded second-stage payload** (check for `memfd_create`, `mmap`+jump patterns, or an `fexecve` string): this is the "Matryoshka" / nested-binary-stage pattern seen across multiple independent CTFs. Hand off to the `nested-stage-binary-decrypt` skill once confirmed.

## Then proceed to

- If it's primarily a logic/reversing puzzle (not memory corruption): decompile with Ghidra or radare2/Cutter rather than hand-tracing raw `objdump -d` output — faster and far fewer transcription errors on anything beyond a trivial function.
- If it's pwn/exploitation: set up `pwntools` immediately (`from pwn import *`), targeting either the local binary (`process(...)`) or the remote service (`remote(host, port)`), so the exploit script works against both without modification.
