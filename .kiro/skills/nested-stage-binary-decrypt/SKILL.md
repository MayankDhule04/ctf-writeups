---
name: nested-stage-binary-decrypt
description: Analyze and decrypt a binary that unpacks and executes an embedded encrypted payload at runtime (memfd_create+fexecve or mmap+jump pattern), recovering the inner "stage2" binary for further analysis. Use when a reversing CTF binary's strings include memfd_create, fexecve, or similar self-unpacking indicators, or when the challenge is explicitly themed as nested/packed/multi-stage (e.g. named "Matryoshka" or similar).
---

## Recognizing the pattern

This is a recurring CTF template (observed independently across multiple
events) where an outer binary decrypts an embedded blob and executes it
without writing it to a normal file on disk. Telltale signs in `strings`
output or imports:

- `memfd_create` — creates an anonymous, in-memory file descriptor
- `fexecve` — executes a program from an already-open file descriptor
- Alternative pattern: `mmap` with `PROT_EXEC`, followed by a computed jump
  (less common, more advanced)
- A suspiciously high-entropy region in `.data`/`.rodata` that is clearly not
  normal program data (much larger than the rest of the binary's static data)

## Step-by-step recovery process

1. **Confirm the pattern** with `strings -n 6 <binary> | grep -iE 'fexecve|memfd_create|stage'` and check imports/PLT entries for these symbols.

2. **Disassemble the relevant function** (`objdump -d -M intel <binary>` if
   no decompiler is available; Ghidra/radare2 if one is — strongly prefer a
   decompiler here since the decrypt loop logic needs to be read precisely):
   ```
   grep -n "memfd_create\|fexecve\|call.*write" disasm.txt
   ```
   Trace backward from the `memfd_create`/`write`/`fexecve` call sequence to
   find the loop that populates the buffer being written — that loop is the
   decryption routine.

3. **Identify the exact embedded blob location and length** from the ELF
   section headers (`readelf -S <binary>`) and the disassembly's references
   to a length variable (often a `DWORD` near the blob holding its size) and
   a pointer to the blob's start address. Map the virtual address to a file
   offset using the containing section's `Address`/`Offset` pair (usually
   1:1 for `.data` in a non-relocated ELF, but verify — don't assume).

4. **Reimplement the decrypt loop in Python**, reading the disassembly
   instruction-by-instruction. Common patterns seen in practice:
   - A simple XOR with a repeating key.
   - An LCG (linear congruential generator): `seed = seed * MULTIPLIER (mod 2^32)`, with the output byte derived from shifting/XORing parts of the seed with the ciphertext byte. Watch carefully for which bits of the running state get extracted (e.g. `>> 16`, `>> 24`, XOR with `dh`/a specific byte of the register) — small mistakes here silently produce garbage that LOOKS like it should be right but isn't; re-verify against the real binary's behavior rather than trusting a single hand-trace.
   - RC4 or another standard stream cipher dressed up with a custom key schedule.

5. **Extract the ciphertext bytes** directly from the outer binary's file
   bytes at the computed offset/length, run your reimplemented decrypt
   function, and check the result starts with `\x7fELF` (or `MZ` for PE) to
   confirm success before proceeding.

6. **Analyze the recovered inner binary independently** — treat it as a
   fresh binary needing its own `check-binary-mitigations` pass and its own
   category routing (it may itself contain ANOTHER nested stage — check
   again for `memfd_create`/`fexecve` strings in the newly recovered binary
   before assuming you've reached the bottom).

7. **If the inner binary implements its own "password" or equality check**
   that looks like a checksum rather than a literal string comparison
   (e.g. your input is split into chunks and some transform is applied
   before comparing against a fixed string), stop and check whether that
   transform is CRC32 or similar before assuming the literal displayed
   string IS the required input — hand off to `invert-linear-checksum` if so.
   A visible, readable string sitting right next to the comparison logic can
   be the actual target of a checksum comparison, not the literal password —
   verify by testing the literal string against the real binary first; if it
   fails, that's the signal the comparison involves a transform.

## Common mistake to avoid

Don't assume a "4 bytes read as a native-endian integer, then written back
out as 4 bytes via a right-shift sequence" operation is a no-op passthrough
just because the shifts appear to reconstruct the original byte order —
check carefully whether a function call sits BETWEEN the read and the
write-back; that call is very likely the actual transform (e.g. a CRC32 over
each chunk) and skipping past it as "probably just a format conversion"
leads directly to the false conclusion that a password must match literally
when it actually needs to produce a specific checksum output instead.
