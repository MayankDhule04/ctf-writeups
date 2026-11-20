# CTF Folder Cleanup Plan (Phase 1 — report only, nothing deleted/moved)

**Scope scanned:** `c:\Users\mayan\OneDrive\Desktop\ctf`
**Size:** ~31,805 files, ~11.8 GB. **Git:** no `.git` repo anywhere — safe to restructure, nothing to preserve.
**This file is the only thing I created.** No deletions or moves have happened.

## How I analyzed (and confidence caveats)
- Built a full file/extension/size inventory and a per-folder listing.
- Regex-scanned all text files (skipping tool-env/package trees) for brace-wrapped flags; cross-referenced writeups/`*_SOLUTION.md`/`flag.txt` as the source of truth for "solved".
- **I did NOT execute any scripts.** So for a given challenge's pile of near-identical solver scripts, I can tell you *that* it was solved (confirmed flag in a writeup), but I usually **cannot prove which exact `.py` produced it**. Those go in UNSURE, not a guess.
- Because there are ~1,900 loose scripts and ~27k files inside tool/venv trees, the DELETE list groups by directory/glob with a reason per group rather than one line per each of 31k files. Before any Phase 2 deletion I'll expand the groups to an explicit file list for you.

## Distinct flag formats found (exact prefixes, as-is)
`CIT{...}` · `SpaceCTF{...}` · `TDHT{...}` · `PINK{...}` (and platform format `PP{...}`) · `Kaal{...}` · `tUp{...}` · `CTF{...}` · `FLAG{...}` / `flag{...}` · `ctf{name:token}` (blockchain) · `IATCQ{...}` / `IATCQ26{...}` · `CTFCROW{...}` · `TRACECTF{...}` (⚠ all seen values are challenge decoys) · `ctf7{...}` · `spooky{...}`

---

# KEEP — grouped by event / challenge

> For each I list the confirmed flag(s) and the core files. "Source of truth" = the writeup/flag file to keep; associated solver scripts are addressed in the DELETE/UNSURE sections.

## Event: CIT CTF  (format `CIT{...}`) — SOLVED (many)
Confirmed flags found in notes:
- `CIT{55T1_R3m0t3_C0d3_3x3cut1on}`, `CIT{Wh@t_in_th3_w0rld_i$_th1s_l@ngu@g3}`, `CIT{H1dd3n_D1r5_3v3rywh3r3}`, `CIT{M@ss_@ssignm3nt_Pr1v3sc}`, `CIT{m0j0_eng4g3d}`, `CIT{b9486c74c779db5194d6508bebbee72b}`
- OSINT: `CIT{Howell_Mill_Road_Atlanta_GA}`, `CIT{Union_Avenue_New_Haven_CT}`, `CIT{Vincenzo_Peruggia}` (Louvre), `CIT{we_can_only_see_a_short_distance_ahead}` (Rotor-Rooter)
Source-of-truth docs to KEEP: `CIT_SOLVED_CHALLENGES.txt`, `CIT_CTF_STATUS.md`, `CURRENT_CTF_STATUS.md`, `ROTOR_ROOTER_SOLUTION.md`, `LOUVRE_HEIST_COMPLETE_INFO.md`, `CURATORS_EXIT_SUMMARY.md`, `GOOBER_ANALYSIS.md`, `INTERN_PORTAL_SUMMARY.md`, `SIGNUP_ENJOY_SUMMARY.md`, `DOG_BARKING_ANALYSIS.md`, `I_CANT_HEAR_YOU_README.md`, `STARWARS_CHALLENGE_SUMMARY.md`.

## Event: SpaceCTF / Game-of-Thrones  (format `SpaceCTF{...}`) — SOLVED (several)
- `SpaceCTF{lannisters_always_pay_their_HHCLZW}` (Iron Bank)
- `SpaceCTF{valar_morghulis_face_no_man_2ZD66Q}` (Faceless Verifier)
- `SpaceCTF{the_watch_holds_the_line_5YRB2A}`, `SpaceCTF{three_links_of_the_maesters_chain}`
KEEP docs: `IRON_BANK_HEIST_SOLUTION.md`, `FACELESS_VERIFIER_COMPLETE_SOLUTION.md`, `SPACECTF_SUMMARY.md`, `COSMIC_NOISE_SOLUTION.md`, `MAESTERS_CODEX_ANALYSIS.md` (Maesters looks only partially solved — see UNSURE).

## Event: "TDHT" CTF  (format `TDHT{...}`) — SOLVED (several)
- `TDHT{Cg6NjRspE4DBCHqHmMaMtTijSi946ica}`, `TDHT{k03pzlXhPjBS3yy1DFVRT5Mz7A}` (Don't Ping the Cat L1/L2)
- `TDHT{SmlChucIb58jz7n1Md52Y1YmQp}` (Shopping), `TDHT{RA5uhZNprW6DnDCjOFpIIlGJk5}` (status page), `TDHT{yHp5EbnVbGrfiJsBPHtM9Ovh}` (NBT Needle), `TDHT{0afd0b1a5b46ab26f4929ac9a92e9f170945}` (Shopping L2), `TDHT{9b50dac4fee96a5cd4e5b4f2a9c3d66f7a4e}` (Switch It Up)
KEEP docs: `writeups\` (NBT_Needle, Shopping_L2, Switch_It_Up, 03_status_page, Spectral_Override, Temporal_Paradox), `DONT_PING_CAT_SOLUTION.md`, `DONT_PING_CAT_L2_SOLUTION.md`, `SHOPPING_SOLUTION.md`.
Note: **Stolen Schematics** (TDHT) appears **UNSOLVED** — every `STOLEN_*` file holds only `TDHT{...template...}` (see DELETE/UNSURE).

## Event: PINK / Platypwn  (format `PINK{...}`, platform `PP{...}`) — SOLVED (several) + ACTIVE
- `PINK{NiNeTyNiNeQwErTzEs}` (`1337_flag.txt`), `PINK{Th3_J0urn3y_m4y_n3v3r_3nd!!}` (`journey_flag.txt`), `PINK{just_4_s1mpl3_pr0gr4m_1_wr0t3_0n_my_n3w_c4lcul4t0r}` (`calculator_tns\flag.txt`), `PINK{fLAg_tnS_calc}` (`tns2_flag.txt`)
KEEP folders/files: `calculator_tns\`, `tns2_xml\`, `TnsTools\` (a real sub-project w/ its own LICENSE+pyproject), `pink_hq\`, `Kosaken.txt`, `PremiumRequired\`, `solve_pie.py`, `solve_poly.py`, `solve_susnumbers.py`, `solve_kosaken.py`, and **`fs-enc\` (ACTIVE challenge — do not touch)**.

## Event: Blockchain  (format `ctf{name:token}`) — SOLVED
- `ctf{control-door:Iygpt5IjNu5uq5mItgc}`, `ctf{escrow-ledger:yczeUQmpw7YX4EwJpC}`, `ctf{ghost-in-the-machine:6WMEJ37TYcz}`, `ctf{masters-door:KkrmZQYCUL5et0tSqwH}`, `ctf{ghost-3:D7l28tH9BjmeHhKpoOlj0WyX}`, `ctf{whispers:tLiQN499qb3mUWYY1AElkHf}`
KEEP docs: `NIGHTFALL_CONTROL_HUB_WRITEUP.md`, `EV037_GHOST_IN_THE_LEDGER_WRITEUP.md`, `TWIN_ENCODING_WRITEUP.md`.

## Event: IATCQ  (formats `IATCQ{...}`, `IATCQ26{...}`) — SOLVED (custom VM + others)
- `IATCQ{AAAAAAAAAAAAAAAAAAAA:25HJ}` (`custom_vm\FOUND_KEY.txt`), `IATCQ{LF6BWCR2VNU0RIFD7CMM5VQBCO}` (`writeups\Spectral_Override`), `IATCQ26{...}` (GHOST — see UNSURE, looks partial)
KEEP: `custom_vm\` (challenge `prog.bin`/`disasm.txt` + `FOUND_KEY.txt`/`MITM_KEY.txt`), `GHOST_WRITEUP.md`.

## Event: Calypso  (format `tUp{...}`) — SOLVED
- `tUp{cactus777}` (`CALYPSO_FINAL_SOLUTION.txt`, `CALYPSO_SOLUTION.md`, `ARGON2_SOLUTION.md`, `argon2_hash.txt`). KEEP those.

## Challenge: crypto-numerology  (format `CTF{...}`) — SOLVED
- Real flag `CTF{w3_aRe_g0Nn@_ge7_MY_FuncKee_monkey_!!}` (in `CTF_PROGRESS_SUMMARY.md`).
- KEEP the challenge folder `5b0d78bf...e6365\crypto-numerology\` (chall source + readme). ⚠ `…\crypto-numerology\flag.txt = CTF{TestFlag_0000…}` is the **challenge's placeholder**, not the real flag — keep with the challenge but don't mistake it for the answer.

## Event: CTFCROW  (format `CTFCROW{...}`) — SOLVED
- `CTFCROW{TRUST_THE_MANIFEST}` (`challenge\…\recovery_manifest.txt`), `CTFCROW{LOOK_AT_STREAM_7}` (`footprint_flag.py`).
- KEEP: `chakra_story_ctf (1)\` (story/tools), `challenge\` (chakra evidence: `chakra_memory.raw`, `chakra_traffic.pcapng`, `damaged_archive.7z`, `fragment_03.dd`, `spider_eye.png`).

## Self-contained challenge source folders worth KEEPING (challenge assets, small)
`web_who-is-he\` (Ruby web), `a-massive-problem\` (Flask IDOR), `temporary-destruction\`, `web-postviewer5-ff\` + its hash-named twin, `Phishtofortune\` (xlsm macro), `vulcan\` (Vulcan-script OSINT), `glassbottle\`, `calculator_tns\`, pwn handouts (`handout_biggest_binary\`, `handout_hugebinary2\`, `handout_make_a_wish\`, `notjson\`, `pwn_*_extracted\`, `sudo_rust_handout\`, `cold-beacon-chall\`, `frankenstein\`), `primecalc\prime-calc\` (source only — see DELETE for the dmtcp checkpoints), `forgotten-tenant-stage3-bundle\`, `sscit_frag\`, `asterion_evidence\`.

## Your own tooling worth KEEPING
`ctf-tool\` (your real package + tests), `TnsTools\`, `docker\` (ctfbox), `.kiro\steering\ctf.md`.

---

# DELETE candidates

### A. Non-CTF bulk / third-party tool trees / caches  (biggest win: ~5+ GB, ~27k files)
- `mission-git-hackss\hexstrike-ai\` — cloned 3rd-party tool **with a full Python venv** (`hexstrike_env\Lib\site-packages\…`). This is the bulk of the 27,613 files. Reason: external tool + virtualenv, re-installable, not your work. *(The rest of `mission-git-hackss\` is a SECOND solver graveyard — see UNSURE; I'm not blanket-deleting it.)*
- All `__pycache__\` dirs and `*.pyc` (5,249 files) — Python bytecode cache.
- `chrome156_driver\` (chromedriver 24 MB), `tools\ffdec\` + `tools\ffdec.zip` (Flash decompiler, 36 MB) — re-downloadable third-party tools.
- `steghide_bin\` (empty dir), root `__pycache__\`.

### B. Large downloaded archives / heavy assets for UNSOLVED or concluded-dead challenges (~8 GB)
- `DrownInMemory\` (409 MB UE5 game) + `Drown-in-Memory_Windows.zip` (266 MB) + `Abyss_unpack\` (221 MB extracted game assets) — "Drown in Memory"; concluded not locally solvable. Reason: huge game install/extraction, no flag/writeup.
- `dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img` (1.99 GB) — mobile disk image, no confirmed flag/writeup for "dome ctf".
- `spooked2.lime` (1.07 GB) — LiME memory dump, no solve found.
- `the-model-knows\model\model.safetensors` (988 MB) + `the-model-knows-dist-spooky.zip` (874 MB) — LLM-model challenge, no confirmed flag. (Keep the tiny `chat.py`/`extract.py` if you want the approach; drop the model weights.)
- `gogogo.journey` (75 MB), `journey_payload.bin` (37 MB) — the PINK "Journey" flag is already saved (`journey_flag.txt`); these are the heavy intermediate assets.
- `rockyou.txt` (140 MB, appears twice) — standard wordlist, re-downloadable.
- Big audio/image intermediates already reduced to a flag: `beep_beep_boop.wav`, `cassette.wav`, `detailed_spectrogram.png`, `greek_*.png` (several 10–46 MB), `greek_contours.png` — regenerable scratch renders.

### C. Exact duplicates (keep one copy)
- `mission-git-hackss\challenge_final.onnx` + ` 2.onnx` + ` (1/2/3).onnx` — 5 copies of the same 43 MB model.
- `mission-git-hackss\game\game.exe` + `game_patched.exe` + `game_direct_flag.exe` + `game_collision_patched.exe` — 4× 37 MB.
- `mission-git-hackss\disk1_extracted\…\Disk2.001` vs `mission-git-hackss\disk_files\Disk2` — same 1.57 GB image twice.
- `Temporal_Paradox\Temporal Paradox\gateway_snapshot.img` vs `…\fresh\Temporal Paradox\gateway_snapshot.img` — 100 MB twice (and a `Temporal Paradox` empty dir).
- `KaalRaj.apk` at root **and** in `mission-git-hackss\` — same 15.5 MB apk.
- `greetings` / `greetings.zip` duplicated in `mission-git-hackss\greetings*`.
- `challenge_CnK3cCB\` vs `challenge_CnK3cCB (1)\`; `chakra_story_ctf (1)\` (the `(1)` are copy-paste dupes); `control_git_dump\` vs `control_git_full\` (same `.env`/`config.py`); `popcnt_oracle.tar.gz` vs `popcnt_oracle_extracted\`; standalone `glassbottle\` vs `nosocomephobia\extracted\glassbottle\`.
- `primecalc\` dmtcp checkpoints (`*.dmtcp`, `build\out\ckpt_*`) — multi-MB process snapshots, regenerable from `prime-calc\` source.

### D. Solver "graveyard" — abandoned duplicate attempt scripts (root level)
These are clusters of near-identical attempts where the challenge is already captured by a writeup/flag file (KEEP section). Recommendation: **keep the single working solver per challenge, delete the rest.** ⚠ I have not executed them, so *which* single script is the keeper is listed in UNSURE — do not delete a whole cluster until we pick the keeper. Clusters and counts:
- `signal_*.py` (~55), `sirens_*.py`/`clean_siren*`/`clean_flag_hunter`/`clean_focused_solver` (~58), `westeros_*.py` (~29), `love_*.py` (~31) + `love_simple\attack*/decode*` (LOVE is UNSOLVED — see UNSURE/decoys), `dragonstone_*`/`iron_bank_*`/`faceless_*`/`maesters_*`/`shield_of_achilles*` (SpaceCTF, ~40), `kagegate_*` (~11), `equator_*` (~10), `merkurated_*` (~8), `numerology_*` (~12 — crypto-numerology, solved), `stolen_*`/`STOLEN_*` (~30 — UNSOLVED templates), `admin_panel_*` (~36), `postviewer_*` (web, several), `apk_*`/`kaalraj_*`/`raj_*`/`two_body_one_soul*`/`one_soul_two_body*`/`construct_flag_from_parts*`/`find_real_flag*` (KaalRaj — UNSOLVED, see UNSURE), `greek_*`/`sstv_*`/`ocr_spectrogram`/`read_spectrogram` (audio), `vinsmoke_*`, `dog_*`/`ping_*`/`dont_ping_cat*`.
- Generic brute/scratch scripts with no single owner challenge: `ultimate_*`, `nuclear_option.py`, `final_desperate_attempt.py`, `exhaustive_*`, `try_*`, `brute_*`, `massive_xor_decrypt.py`, `smart_xor_search.py`, `exhaustive_xor.py`, `deep_analysis.py`, `master_key_finder.py`, `ultimate_key_finder.py`, `incomplete_crypto_solver.py`, etc. — classic "throw everything" attempts.

### E. Your abandoned "autonomous AI solver" meta-project (contains only FAKE example flags)
`ctf_master_solver.py`, `ctf_ai_solver.py`, `autonomous_ctf_solver.py`, `auto_solver.py`, `ctf_solver.py`, `solve_ctf.py`, `test_solver.py`, `setup_solver.sh`, `setup_solver.ps1`, `auto_solve_crackme.sh`, `solvers\` (6 generic `*_solver.py`), and the guide docs `AUTONOMOUS_SOLVER_GUIDE.md`, `CTF_SOLVER_README.md`, `QUICK_START.md`, `ULTIMATE_CTF_GUIDE.md`, `USAGE_GUIDE.md`, `CTF_TOOLS_SUMMARY.md`, `README.md` (root — has placeholder flags). Reason: generic scaffolding whose only "flags" are templates like `CTF{b4s3_64_d3c0d3d}`, `CTF{example_flag}`. **Confirm**: delete, or move to a separate `tools/` repo? (Overlaps with your real `ctf-tool\`.)

### F. Obvious scratch / empty
- Empty dirs: `Temporal Paradox` (space variant), `steghide_bin`, `equator\` (single `solve.py` dup of root), `Temporal_Paradox` vs `Temporal_Paradox\Temporal Paradox` nesting.
- `*_utf8.txt` / `*_out.txt` paired debug dumps in `new challeneg\`, `Temporal_Paradox\`, `dome ctf\` — script stdout captures.
- `.DS_Store` files (macOS cruft) sprinkled in `Phishtofortune\`, etc.

---

# DECOY files that were PART OF a challenge's bait (NOT your scripts)
- `love_simple\output.txt` and every `TRACECTF{...}` value — the **LOVE** challenge planted these as misdirection: `TRACECTF{HTML_c0mm3nts_4r3_ju5t_d1str4ct10ns}`, `TRACECTF{n1c3_try_but_y0u_n33d_m0r3_th4n_cl1ck5}`, `TRACECTF{s0urc3_c0d3_w0nt_s4v3_y0u_n0w}`, `TRACECTF{j4v4scr1pt_1s_n0t_th3_s0lut10n}`, `TRACECTF{HTML_m3t4_t4gs_4r3_n0t_th3_4nsw3r}`, `TRACECTF{c0ns0l3_l0gs_4r3_f0r_d3bugg1ng_n0t_fl4gs}`. These are fake-flag bait; the real LOVE flag was never captured.
- `flag{not_the_real_one_nice_try}` (admin-panel challenge) — planted decoy string.
- Challenge-provided placeholder flag files (keep WITH their challenge source, but they are not answers): `…\crypto-numerology\flag.txt = CTF{TestFlag_000…}`, `web_who-is-he\flag.txt`, `secret-backup\flag.txt`.

---

# UNSURE — need your call / can't verify

1. **Which exact script is the "working" one** in each graveyard cluster (Section D). I didn't run them; for solved challenges the writeup is the real record, so most/all scripts in a cluster are likely redundant, but I won't delete the whole cluster blind. If you want, I can try to execute the most-likely keeper per cluster to confirm before deleting.
2. **`mission-git-hackss\`** (minus the hexstrike venv) — a second large pile of your scripts (`ABSOLUTE_FINAL_NUCLEAR_HACK.py`, `absolute_final_kaalchakra.py`, game exes, onnx, disk images, KaalRaj.apk, audio). Looks like an earlier dumping ground. Keep any writeups, delete env+dupes — but I want your OK before touching it since it's large and clearly held real attempts.
3. **KaalRaj / Kaalchakra (`Kaal{...}`)** — appears **UNSOLVED**: `ALL_KAALRAJ_FLAGS.txt` / `KAALRAJ_FLAGS_TO_TRY.txt` / `westeros_all_flags.txt` hold *dozens* of candidate flags with no confirmed winner. Delete the brute-force candidate lists, or keep the APK (`KaalRaj.apk`) + one analysis for later?
4. **Stolen Schematics (TDHT)** — UNSOLVED (only templates). Keep recon notes or drop entirely?
5. **sirens / signal / greek-audio / vinsmoke** clusters — big script piles but I found **no confirming writeup or non-template flag**. Solved or abandoned? (`ctf7{SSTV_decode}`-style values in `flag_variations.py` look like guesses, not a confirmed flag.)
6. **Maesters Codex (SpaceCTF)** and **GHOST (`IATCQ26`)** — writeups contain mostly templates / partials; may be only partially solved.
7. **`dome ctf\`**, **`the-model-knows\`**, **`Temporal_Paradox\`**, **`primecalc\`**, **`Phishtofortune\`**, **`vulcan\`** — challenge sources present but I didn't find a clear flag; keep as "attempted/unsolved" sources, or are some solved elsewhere?
8. **pwn handout binaries** (`chal`, `no-win`, `hello`, `coins`, `greetings`, `sudobutgood`, `frankenstein`, `cold-beacon`) — commit the binaries (common for pwn writeups) or gitignore them? Per your rules I'll ask before deciding.
9. **`pp2026-vpn.conf`** (in `~\Downloads`, currently open) — contains your live WireGuard **private key**. Do NOT commit this to GitHub. It's outside the folder, but flagging it so it doesn't get dragged in.

---

# Proposed Phase 2 structure (for after you approve)
```
<event>/<challenge>/
   README.md     # exact flag + technique category + how the kept script solves it
   files/        # original challenge assets
   solve.py      # the one working solver, renamed clearly
```
Events would be: `cit-ctf/`, `spacectf-got/`, `tdht/`, `pink-platypwn/`, `blockchain/`, `iatcq/`, `calypso/`, `ctfcrow-chakra/`, plus `pwn-handouts/`, `unsolved/`, and `tools/` (ctf-tool, TnsTools, docker). Root `README.md` index + `.gitignore` (venvs, `__pycache__`, `*.pyc`, `.DS_Store`, large images/dumps/zips, `*-vpn.conf`).

**Nothing will be deleted or moved until you approve.** Tell me:
- OK to proceed, and your answers to the UNSURE items (esp. #1 keeper-verification, #2 mission-git-hackss, #8 commit-binaries-or-not)?
- Should the Section E "autonomous solver" project be deleted or kept as tooling?
