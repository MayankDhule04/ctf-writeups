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

## Second independent corroboration: EV-037 / "EV-039 Ghost 3" are the same flag

A separate later session (DOME CTF "Operation Nightfall", ACT 4 "Ghost in
the Ledger") independently reached the exact same flag
(`dome.ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}`) via the exact same technique
(JWK header-injection forging an admin JWT, then BOLA + view-parameter mass
assignment against `POST /api/v1/transactions/TX-9f2b6a1e4c7d8035`) while
referring to it as "EV-039 (Ghost 3, 100pts)" rather than "EV-037". This
confirms the repo's existing note above that these are the same underlying
challenge reached via two differently-numbered case briefs — not a
coincidence or mislabeling in only one session. Treat `EV-037` and
`EV-039`/"Ghost 3" as the same challenge/flag across all notes.

That same later session left two further DOME CTF ACT 4 evidence refs open,
not yet represented anywhere in this repo (`unsolved/dome-ctf/` predates
this investigation thread):

- **EV-038 ("Ghost 2", 200pts)** — "identity behind Kage via forgotten
  services + recovered artifacts." Not solved; no concrete lead captured
  beyond the name.
- **EV-037 ("Ghost 1", 200pts, "first key / a secret that opens doors")**
  — ambiguous whether this is actually distinct from the
  `blockchain/ghost-in-the-ledger` EV-037 already solved in this repo, or a
  different evidence ref that happens to share the same case number across
  sessions. Needs disambiguation against the live platform/scoreboard.

Open recon leads from that session for whoever picks EV-037/038 back up:
- `audit.hackthe.website` ("The Console") has a 21st hidden service named
  `research-agent` in its services registry (registry reports 21 rows
  synced, but `/api/v1/services` only returns 20 after filtering to
  `visibility=public`).
- `POST /api/v1/audit/search?filter=` queues an async export job (returns
  `job_id: exp-...`).
- `POST /api/internal/export-job` requires a header
  `X-Nightfall-Hub-Signature` whose derivation was never found — ~700 HMAC
  candidate constructions were tried (ops API key
  `ops-svc-7f3c9a2e5d81b4c6`, JWKS modulus, `kid`, issuer, service names,
  build id `a1b2c3d`; sha1/256/384/512/md5; hex/b64/b64url; multiple payload
  shapes) plus JWT-JWK-injection and raw-RSA signature variants — all
  rejected `401 stage:signature`.
- A `.git` leak was found on a *different* host, `control.hackthe.website`
  (`/.git/config`, `/.git/HEAD`, `/.git/logs/HEAD`, `/.git/index` all `200`;
  `packed-refs` 404s). Repo: "ops service configuration for control door",
  2 commits. Yields `API_KEY=ops-svc-7f3c9a2e5d81b4c6` and
  `TOTP_SECRET=JBSWY3DPEHPK3PXP` — but this is confirmed to be the
  **already-known ACT3 ops credential**, not a new secret, and does NOT
  contain the audit host's hub-signature secret. No equivalent git/source
  leak exists on the audit host itself (all checked, all 404 even with a
  forged admin cookie).
- No `export-worker`/`research` vhost was ever found reachable — the
  signature-gated export pipeline's actual target service remains
  unlocated.

## New unsolved challenge added: `unsolved/movement-clockmaker/`

A separate CTF ("ctf7"-branded, per in-binary flag format `ctf7{...}`)
reverse-engineering challenge, "clockmaker" (binary name `movement`), was
fully analyzed in a later session: a custom keyless block cipher (S-box
substitution + GF(2) *affine* permutation layer, 50021 rounds, CBC-chained)
was completely reverse-engineered and algebraically inverted (no brute
force) via a hand-rolled ptrace debugger. The derived winding
`ctf7{th3_cl0ck_ch1m3d_but_f0r_th3_wr0ng_h0ur_d0_n0t_subm1t}` was verified
against a fresh hash-matched redownload of the original binary (prints
"Correct" reproducibly) but was **rejected by the CTF platform** — root
cause unresolved (ruled out: per-instance binary personalization, an
anti-ptrace-induced wrong-table bug). See
`unsolved/movement-clockmaker/MOVEMENT_CLOCKMAKER_WRITEUP.md` for the full
method, which is independently reusable for future custom-cipher reversing
challenges regardless of this specific flag's fate.
