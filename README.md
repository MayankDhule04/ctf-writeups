# CTF Writeups & Solvers

A cleaned-up archive of CTF challenges I worked on, organized by event. Each challenge
folder holds the flag + solve method (`README.md`), original assets (`files/`), and the
working solver where one exists.

> Housekeeping: `_UNSORTED/` holds files I couldn't confidently attribute (pending manual
> triage); `_CLEANUP_TRASH/` holds everything removed during cleanup (safe to delete once
> reviewed). Both are git-ignored.

## Events

| Event | Categories | Challenges | Notes |
|---|---|---|---|
| `blockchain/` | blockchain | 3 | Smart-contract challenges (ctf{name:token}). |
| `calypso/` | crypto | 0 | Argon2 password recovery (tUp{cactus777}). |
| `cit-ctf/` | web / OSINT / forensics | 13 | CIT CTF — many solved (CIT{...}). |
| `cloud/` | cloud | 1 | AWS CloudTrail incident analysis. |
| `crypto/` | crypto | 3 | Cryptography challenges. |
| `ctfcrow/` | forensics | 3 | CTFCROW / Chakra story — memory & traffic forensics. |
| `forensics/` | forensics | 1 | File/image forensics. |
| `iatcq/` | rev | 2 | IATCQ — custom VM reversing. |
| `osint/` | osint | 5 | OSINT / geolocation / document challenges. |
| `pink-platypwn/` | rev / crypto / misc | 6 | PINK / Platypwn (TI-Nspire, emoji, calculators). |
| `pwn/` | pwn | 12 | Binary exploitation handouts. |
| `spacectf-got/` | web / crypto / stego | 7 | SpaceCTF, Game-of-Thrones themed. |
| `spooky-halloween/` | stego / rev / misc | 4 | Halloween 'spooky' themed event. |
| `tdht/` | web / forensics / audio | 4 | TDHT CTF. |
| `tools/` | tooling | 3 | My reusable tooling (ctf-tool, TnsTools, docker ctfbox). |
| `unsolved/` | mixed | 14 | Unsolved or abandoned attempts, kept for reference. Includes `movement-clockmaker/` — custom block cipher fully reverse-engineered & inverted, but platform rejected the derived flag. |
| `web/` | web | 10 | Web exploitation (JWT/OAuth/SSTI/IDOR/XSS). |

## Flag formats seen

`CIT{}` · `SpaceCTF{}` · `TDHT{}` · `PINK{}`/`PP{}` · `Kaal{}` · `tUp{}` · `CTF{}` · `ctf{name:token}` · `IATCQ{}`/`IATCQ26{}` · `CTFCROW{}` · `spooky{}` · `ctf7{}` · `TRACECTF{}` (decoys).
