# Cross-session notes (from the Kiro chat session that reviewed this repo)

These are corrections/additions discovered by comparing this repo's
CLEANUP_PLAN.md / solved-status against flags actually captured in a
separate live chat session with Kiro, for the same player.

## Correction: `cloud/forgotten-tenant` is marked unsolved here, but IS solved

This repo's README lists `cloud/forgotten-tenant` as "unsolved" and its
folder only contains the forensic bundle (cloudtrail JSONs, handoff note),
no solved flag. In a separate chat session (same TVX CTF), this exact
challenge ("tvx-forgotten-tenant") was fully solved:

- Flag: `TVX{6N8at90xLFvdgyma648o}`
- Technique: credentials from a `.docx` (zip→`word/document.xml`) → AWS
  `sts get-caller-identity` → discovered a retained `legacy-migration-role`
  with an `sts:ExternalId` condition whose value was split across two
  artifacts (a tag `audit-ext-id-prefix=fthK52` + a ticket's redacted-suffix
  note `ycGCAX`) → reassembled ExternalId `fthK52ycGCAX` → assumed that role
  → found an overly broad inline `sts:AssumeRole` statement
  (`Resource: arn:...:role/tvx-forgotten-tenant-*`) letting it pivot into a
  SecOps `incident-response-role` → that role could `s3:GetObject` only on
  the exact key pattern `case-*/handoff-*/evidence.json` (no `ListBucket`) →
  the forensic bundle in this repo's `cloud/forgotten-tenant/files/` (the
  CloudTrail JSONs across two days + the handoff note) gives the exact case
  folder (`case-ab5396cd`, from the 03-14 trail's manifest upload) and
  handoff code (`RYII91T48V`, named explicitly in the handoff note and
  visible in the 03-15 trail's PutObject sub-path) that must be stitched
  together to form the real S3 key:
  `case-ab5396cd/handoff-RYII91T48V/evidence.json`.

**Action**: update this repo's README/status for `cloud/forgotten-tenant` to
SOLVED with the flag and technique above, and consider adding a
`solve_forgotten_tenant.py` reconstructing the AWS CLI steps.

## Confirmed duplicate flag value across two different-looking challenges

`blockchain/ghost-in-the-ledger` (EV-037, "Ghost in the Ledger 1",
`dome.ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}`) and a separately-tracked
challenge referred to as "EV-039 / Ghost 3" in the other session's notes
resolve to the **exact same flag string**. This suggests either:
(a) EV-037 and EV-039 are the same underlying challenge/evidence reached via
two different case briefs, or (b) one of the two case numbers was
mislabeled during note-taking in one of the two sessions. Worth
double-checking against the actual CTF scoreboard/platform if those points
haven't both been claimed yet — claiming the same flag under two different
challenge IDs may or may not award points twice depending on the platform.

## Independently solved CTFs not represented in this repo at all

The other chat session also fully solved challenges from **Platypwn 2026**
(a separate HPI-hosted CTF, flag format `PP{...}`) including:
- Matryoshka (rev, nested XOR/LCG-encrypted stage2 + CRC32 password-check
  inversion): `PP{th3r3_1s_4_b1n4ry_1n_my_b1n4ry?!}`
- Hold Your Horses (web, TOCTOU — bet placed with headers sent before body,
  body withheld until the race outcome is known): exploit built and
  verified, live submission pending user's own VPN-connected run.

These aren't in this repo and may be worth adding as a new `platypwn/` event
folder if the player wants this repo to be the complete archive going
forward.
