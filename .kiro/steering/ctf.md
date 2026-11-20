# CTF Working Agreement

This workspace is a CTF scratchpad. Read this before helping with any challenge.

## First thing, every new challenge

1. **Ask for / confirm the flag format** before doing anything else (e.g. `flag{...}`,
   `CTF{...}`, `myevent{...}`). If the user gives one, register it:
   - add it to `ctf-tool/flag_formats.json`, and
   - pass it via `--flag-regex` on tool runs.
   Do not assume a format. A wrong format wastes the whole hunt.
2. **Read the actual challenge** (prompt, source, provided files) before writing code.
   Most CTF challenges are solved by understanding the specific mechanism, not by
   brute-forcing every technique.
3. State the challenge category (crypto / web / pwn / rev / forensics / stego / misc /
   osint) and the single most likely attack path before touching tools.

## Tool inventory (use these, don't reinvent)

There is a real package at `ctf-tool/`. Run it as `python -m ctf_tool.cli <cmd>` from
inside `ctf-tool/`. Key commands:

- `flagfind <dir|file>` — recursive flag hunt (plain/hex/base64 + strings). **Run this
  first when files drop.** Add `--flag-regex` for the event's format.
- `triage <dir|file>` — structured evidence report (type, entropy, magic, strings,
  urls, nc hosts, hashes, b64 blobs, category hints). Does NOT solve. Feeds reasoning.
- `crypto xor|b64|vigenere|hash|caesar|analyze`
- `forensics strings|scan|extract|memory|apk`
- `web recon|dirbust|jwt|sqli|ssti|login-brute`
- `stego image|audio|qr`
- `misc morse|bacon|graph|coords`

Global flags: `--flag-regex PATTERN`, `--output file.json`.

## The hybrid loop (tool gathers facts, I reason, tool verifies)

Do NOT brute-force every technique. Follow this loop instead:

1. `flagfind` — catch trivial/plaintext flags in one shot.
2. If nothing, `triage` — get the structured evidence report and actually read it.
3. **Reason over the evidence:** name the category and the single most likely mechanism.
   Signals to use:
   - high entropy (~7.5+) → encrypted/compressed, look for the key/scheme, don't brute XOR.
   - long base64/hex blobs + low entropy → encoding/classical crypto.
   - source files present (.py/.js/.php/.rb) → the bug is in the code; read it.
   - urls / nc hosts → web or remote pwn; recon the service.
   - image/audio → stego; check metadata/LSB/spectrogram before anything exotic.
4. Run the **one** specific `ctf-tool` subcommand that matches, or write a single
   targeted `solve_<name>.py` for that mechanism.
5. Verify the result against the confirmed flag format before declaring success.
6. If it fails twice, go back to step 3 with a different hypothesis — do not tweak-loop.

The speed comes from step 3 (picking the right attack), not from running more attacks.

## Discipline rules (this repo has ~300 dead one-off scripts — do not add to the pile)

- **One working solver per challenge.** Name it `solve_<challenge>.py`. Edit it in place;
  do not create `_final`, `_ultimate`, `_nuclear`, `_desperate`, `_v2` variants.
- **If an approach fails twice, stop and diagnose.** Re-read the challenge, question the
  assumption, and try a fundamentally different track. Do not tweak-and-retry in a loop.
- **No fake automation.** Blindly trying base64/ROT13/caesar/XOR in sequence only catches
  trivial challenges. Reach for a technique because the challenge points to it.
- **Always verify a flag** against the confirmed format before declaring victory.
- Prefer running an existing `ctf-tool` command over writing a fresh script.

## Environment

- OS: Windows, shell: cmd/powershell. Use `;` not `&&` to chain in PowerShell.
- Python 3.13 is available. Long-running things (servers, `nc` sessions, watchers) should
  be started by the user in their own terminal, not blocked on here.
- Challenge downloads tend to land as folders / zips at the workspace root.

## When stuck

Say so plainly and lay out the 2–3 most plausible next tracks with reasoning, rather than
generating more scripts. Ask for the challenge description or any hint text if it hasn't
been shared.
