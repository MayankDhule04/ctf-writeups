---
name: ctf-triage
description: First-pass triage of a downloaded CTF challenge asset (zip, binary, pcap, disk/memory image, or unknown file). Use when a CTF challenge file has just been downloaded and needs to be identified and routed to the right category workflow, or when a CTF organizer has hidden decoy strings/files meant to mislead automated solvers.
---

## When to use this

Run this immediately after downloading any CTF challenge asset, before doing
any deep analysis. The goal is to spend 30 seconds identifying what you're
actually looking at instead of guessing from the challenge category label
alone (challenge titles and categories are frequently misleading on purpose).

## Steps

1. **Identify real file type**, ignoring the extension:
   ```
   file <asset>
   ```
   If it reports something unexpected (e.g. a ".png" that's actually a RAR
   archive, or a ".txt" that's an ELF binary), the mismatch itself is often
   the first hint.

2. **If it's an archive** (zip/rar/7z/tar/gzip):
   - Extract with the matching tool. RAR5 often needs the real `unrar`
     binary (apt's `unrar-free` cannot read RAR5) — download the official
     static binary from rarlab.com if `unrar` isn't present.
   - List contents before extracting blindly; look for nested archives
     (archives inside archives are a common multi-stage pattern).

3. **If it's a binary** (ELF/PE/Mach-O): hand off to the
   `check-binary-mitigations` skill before any reversing/pwn attempt.

4. **If it's a document format that's secretly a zip** (`.docx`, `.xlsx`,
   `.pptx`, `.odt`, `.epub`, `.jar`, `.apk`): `unzip` it directly — credentials,
   flags, and hints are frequently hidden in `word/document.xml`,
   `[Content_Types].xml`, or embedded media inside these containers.

5. **If it's an image**: check `file`, then EXIF/XMP/PNG-text chunks
   (`exiftool`, or read all PNG ancillary chunks directly — `tEXt`, `zTXt`,
   `iTXt`, `eXIf`), then LSB/stego tools (`zsteg` for PNG/BMP, `steghide` for
   JPEG, `binwalk` for embedded files of any kind). Don't stop at the first
   hit — organizers routinely stack multiple techniques in one file.

6. **If it's network capture** (pcap/pcapng): use `scapy` (`PcapNgReader`) or
   Wireshark. Separate synthetic decoy traffic from the real signal by
   timestamp precision — decoy/background traffic is frequently generated on
   round-second/minute/hour boundaries, while the actual injected event has
   genuine sub-second jitter. Reassemble TCP streams for bodies, not just
   headers, before concluding data isn't there.

7. **If it's a disk/memory image**: identify the exact format before
   reaching for a tool. Memory dumps are sometimes wrapped as ELF core dumps
   (QEMU/virsh `--memory-only` style) that Volatility 3's native ELF layer
   handles directly. Disk triage images may be AccessData `AD1` (check for
   the `ADSEGMENTEDFILE`/`ADLOGICALIMAGE` magic bytes) rather than a raw or
   E01 image — standard tools (Autopsy/TSK) have weak AD1 support; a Python
   parser (e.g. `pyad1`) may need patching for single-segment images but is
   more reliable than fighting a GUI tool's partial support.

## Decoy awareness (the most important step)

CTF organizers plant obvious, loudly-named strings and files specifically to
catch automated/AI solvers who grab the first flag-shaped string they find.
Known real-world patterns:
- A `FLAG{...}`/`PP{...}`/`TVX{...}`-shaped string sitting in plaintext next
  to a comment like "don't use AI" or "nice try."
- A second, more deeply-buried flag-shaped string that is *also* a decoy,
  layered specifically to catch solvers who got suspicious of the first one.
- Noise files that are byte-identical copies with trivial differences, or a
  pile of near-identical filenames (`cache_0001.log` ... `cache_0449.log`)
  designed to waste grep/analysis time — these usually ARE pure noise, but
  verify by sampling a few rather than assuming from the pattern alone.

**Rule: never trust a candidate flag until you can explain which mechanism in
the challenge actually produced it** (the decryption routine ran, the auth
bypass worked, the persistence mechanism fired) — not just "it matched the
format and looked prominent."

## Output

After triage, state plainly: the real file type(s) found, which category
workflow this routes to (crypto/pwn/rev/forensics/web/stego/blockchain/osint),
and any decoys spotted so they're not revisited later.
