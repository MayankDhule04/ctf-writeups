---
inclusion: always
---

# Proven CTF Techniques (mined from MayankDhule04/ctf-writeups, 16+ events, ~180 writeups)

This supersedes generic research-based playbooks where they conflict — these are
techniques that were actually used to capture real flags across this player's
history, not secondary-source guesses.

## Web — confirmed real-flag techniques

- **SSTI filter bypass via Python MRO traversal** (Flask/Jinja2, "admin-panel"):
  when `{{config}}` / `{{__import__(...)}}` are blocked, enumerate
  `''.__class__.__mro__[1].__subclasses__()` and index into it to reach
  `subprocess.Popen` or similar, then `.__init__.__globals__['sys'].modules['os']`
  or `['__builtins__']['__import__']('os')` to reach `os.environ`. The exact
  subclass index varies by Python version — enumerate and try several.
- **JWT algorithm confusion, RS256→HS256** ("faceless-verifier"): when a server
  accepts either alg and verifies with the same key material, fetch the RS256
  public key, then sign a new token with `alg: HS256` using the **public key
  PEM string itself (including trailing newline) as the HMAC secret**. Confirm
  whether the key rotates per-connection — if so, fetch + forge + submit in the
  same TCP session.
- **JWT `nbf` (not-before) set far in the future** ("kagegate"): a token issued
  "for later" that isn't valid yet is a sign the real exploit is either (a)
  cracking the HS256 secret to re-sign without the claim, or (b) finding an
  endpoint that leaks the secret — don't assume brute-forcing rockyou.txt
  against the raw JWT is the intended path if 50+ attempts fail; look harder
  for a leak first.
- **SQL injection, classic auth bypass + UNION enumeration** ("iron-bank-heist"):
  `' OR '1'='1` for auth bypass, then `UNION SELECT name, sql FROM sqlite_master--`
  to enumerate schema, then targeted `UNION SELECT` against discovered tables.
  Don't assume a themed/story hint ("ancient software", "a friend left a phrase")
  is the real vector if plain SQLi works — test the obvious injection first.
- **robots.txt → backup archive → credentials → FAKE flag trap**
  ("admin-panel"): a discoverable `robots.txt` leading to a zip with
  credentials that log in and show a flag-shaped string is a documented decoy
  pattern in this player's history (`flag{not_the_real_one_nice_try}`) — the
  real vulnerability (SSTI in this case) is usually a separate, less obvious
  field. Don't stop at the first flag-shaped string that required real effort
  to reach.
- **LFI via unsanitized image/file path parameter** ("shopping"): when an app
  loads files via `?path=` or similar without validation, don't only try
  `/etc/passwd`/`/flag.txt` — this player's real flag was at `/etc/flag.txt`,
  an unusual location. Try the full standard LFI flag-location list, not just
  the first few obvious guesses.
- **Command injection via shell metacharacters in a "ping"-style utility**
  ("dont-ping-the-cat"): test `;`, `&&`, `|`, and raw newline as separators;
  flag locations to check include `/tmp/flag.txt` specifically, not just root
  or webroot.
- **Git history recovery via GraphQL `userContentEdits`** ("ghost"/IATCQ OSINT):
  a GitHub issue whose visible body was edited/scrubbed still has its full
  edit history recoverable via the GraphQL API (`userContentEdits { diff }`)
  even when the unauthenticated REST/web history view 404s. Requires a token.
- **Commit `.patch` URL trick to recover a real email from a GitHub commit**:
  `GET https://github.com/{user}/{repo}/commit/{sha}.patch` returns the
  commit's `From:` header with the author's real email, even when the profile
  hides it.
- **TOCTOU / race condition via artificially slowing the main thread**
  ("postviewer"): if a race window is too narrow to win reliably, deliberately
  burden the main process with large postMessage payloads (`new
  Uint8Array(3e7)` sent repeatedly) to widen the window — this converts an
  unreliable race into a near-100%-reliable one. Combine with predicting
  `Math.random()` from leaked values when a salt/token is derived from it.
- **Challenge source code ≠ deployed app** ("who-is-he"): if the provided
  source (e.g. a Ruby/Sinatra backend with an obvious command-injection bug)
  doesn't match what's actually running at the given URL, the URL is probably
  a CTF platform frontend, not the challenge instance — look for how to spawn/
  reach the actual per-team instance before assuming the source is unrelated
  or the exploit doesn't apply.

## Pwn — confirmed real techniques

- **RSA Hamming-weight (popcount) oracle attack**: when a remote oracle leaks
  only `popcount(x^d mod n)` for a chosen ciphertext `x`, recover the
  plaintext via repeated doubling: query `hw(2^i * c mod n)` for increasing i;
  `hw` unchanged between steps means no modular wraparound occurred (plaintext
  doubled cleanly), `hw` changed means a wraparound occurred. The wrap/no-wrap
  sequence directly encodes the binary expansion of `m/n`. Reconstruct via
  `m = round(n * sum(w_i * 2^-(i+1))) + 1`, then probe nearby candidates (± a
  few integers) and flip ambiguous bit positions to handle the ~7% edge case
  where a wrap doesn't change the Hamming weight.
- **"Flag format string" leftovers are not real flags**: several entries in
  this archive (`0x{ins.address:x}`, `t_{i+1}`, `in_{i}`) are literal
  unevaluated Python f-string/format placeholders captured by an
  over-eager flag-regex scan, not real captured flags — always sanity-check
  that an extracted "flag" doesn't still contain `{variable_name}`-style
  template syntax before treating it as solved.
- **Handout README "local testing" flags are not real flags either**
  (`NNS{local}` appeared verbatim in multiple challenge-provided READMEs as
  the instructions for seeding a LOCAL test flag file before running the
  binary — this is infrastructure for local testing, never the actual
  server-side flag).

## Crypto — confirmed real techniques

- **Weakened stream cipher + known plaintext → keystream recovery**
  ("numerology", Google CTF): a custom cipher based on a standard primitive
  but with reduced rounds (e.g. ChaCha20 run for 1 round instead of 20) is a
  deliberately weakened variant — with a known key/plaintext and many
  ciphertext samples differing only by nonce/counter, brute-force the counter
  (often small, e.g. 32-bit) to recover the keystream, then decrypt everything
  sharing that keystream.
- **Weak Argon2/bcrypt parameters are the whole vulnerability**: a hash
  challenge literally named around its own weakness (e.g. "Hash of Weakness")
  with abnormally low memory/time cost parameters (m=1024 instead of 65536,
  t=2 instead of 3+) is cracked with hashcat/John directly — don't assume a
  structural cryptanalytic attack is needed when the parameters themselves
  are the bug. Use the correct hashcat mode for the hash type (e.g. `-m 10900`
  for Argon2) rather than a slow custom Python cracker.
- **Custom bigram-to-base36 "twin" encoding** (DOME CTF "twin-encoding"):
  recognize when ciphertext length is a clean multiple of 3 and consists only
  of base-36 characters — this is characteristic of "2 ASCII chars packed into
  a 3-char base-36 group" schemes (96×96=9216 states fit in base36^3=46656).
  Decode each 3-char chunk as `int(chunk, 36)`, then `c1 = chr(32 + val//96)`,
  `c2 = chr(32 + val%96)`.
- **Merkle-tree/proof-based challenges**: when a proof format contains fully
  attacker-controlled sibling hashes (not independently derivable), suspect
  the verification only checks internal path consistency, not whether the
  claimed leaf value is plausible — this class of bug is common in "deposit
  small, prove large" style challenges, though confirming the exact bypass
  requires testing the live server's specific `verify()` behavior rather than
  assuming from source alone.

## Forensics / Audio-Stego — a recurring, strong category for this player

- **WAV header lies about bit depth** ("i-cant-hear-you"): header declares
  16-bit PCM but `block_align`/`byte_rate` fields prove it's actually 8-bit —
  players/analysis tools misinterpret pairs of 8-bit samples as single 16-bit
  samples, producing garbled static. Fix by rewriting the `bits_per_sample`
  field (byte offset 34) to match the real depth, then re-analyze.
- **Spectrogram text steganography is this archive's single most common
  stego pattern** ("i-cant-hear-you", "dog-barking" — both WAV, both
  confirmed via unusually narrow dominant-frequency bands e.g. ~495Hz,
  "~500Hz" is not natural ambient/animal sound, it's synthesized tone
  encoding). Generate a spectrogram (`scipy`/`matplotlib` specgram, multiple
  NFFT values: 512 for time resolution, 2048 balanced, 4096 for frequency
  resolution) and visually inspect the 3000-8000 Hz band specifically for
  horizontal bands forming letter shapes. A challenge name like "I Can't Hear
  You" or "dogs were trying to tell me something" is itself the hint pointing
  at "look, don't listen."
- **DTMF/Morse/SSTV are all real candidate encodings for "weird audio" CTFs**
  ("wiretap") — detect DTMF tones via the Goertzel algorithm; if the detected
  sequence doesn't decode cleanly as phone digits, try reinterpreting the same
  digit sequence as Morse (common informal mapping: one digit = dot, another
  = dash, separator digit = letter break) before assuming the detection itself
  is wrong.
- **Memory/disk timestamp correlation across evidence files** ("asterion",
  flag format embeds a literal timestamp `flag{2245GMT}`) — some forensics
  challenges want you to derive and report an exact time, not a hidden string;
  don't assume every forensics flag is a hidden/encoded secret.

## OSINT — confirmed real techniques

- **Real-world historical research can BE the solve** ("louvre-heist" /
  "curators-exit"): some OSINT challenges are genuinely about researching real
  historical facts (e.g. the 1911 Mona Lisa theft, thief Vincenzo Peruggia) —
  don't over-rotate to "there must be a hidden technical trick," sometimes
  the ground truth really is in historical record and the remaining work is
  finding the right document/password tied to those facts.
- **Social media handle pivoting across platforms** ("ghost"): a burner
  handle discovered on one platform (GitHub) often has the same or a
  near-identical handle on another (SoundCloud, Instagram) — check handle
  variants (`phantom.actual.98` → `phantom-actual-98`) across platforms
  systematically rather than assuming a dead end after one miss.
- **A server's HTTP response headers can themselves be the flag body**
  ("ghost" — the `ETag` header literally was the flag content once the
  correct server address was found via decoded OSINT breadcrumbs). Always
  check full response headers (`Server`, `ETag`, `Last-Modified`, custom
  `X-*` headers), not just the response body, once you've located a
  challenge-relevant endpoint.

## Decoy awareness — specific confirmed patterns from this archive

- Challenge-planted decoy flags that look real but are explicitly
  acknowledged traps once hit: `TRACECTF{n1c3_try_but_y0u_n33d_m0r3_th4n_cl1ck5}`
  and similar self-aware "nice try" strings (love/TRACECTF challenge) —
  recognize the self-referential "nice try" / "not the real one" phrasing
  pattern itself as confirmation of a decoy, independent of format.
  `flag{not_the_real_one_nice_try}` is explicit about it.
  `CTF{TestFlag_0000...}` / similar `TestFlag`/`local`/`example`-named
  placeholders inside a challenge's own source/handout are the challenge's
  OWN local-testing scaffolding, not the real answer, even when they match
  the exact expected flag format and regex.
- A time-windowed challenge with no viable bypass after exhausting the
  standard vulnerability classes (LFI/SSRF/SQLi/command-injection/SSTI/XXE/
  deserialization/race-condition — all tested in "love" with zero success)
  really can mean the time-window IS the entire mechanism, with no shortcut —
  don't keep searching for a bypass indefinitely once a thorough pass across
  standard classes has failed; the correct move may just be "wait for the
  window and send the right request then."

## This player's own reusable tooling (`tools/ctf-tool`)

A mature Python CLI (`ctf_tool`) already exists in this player's archive
covering auto-detecting crypto/web/forensics/stego/misc solvers (XOR brute
force single+multi-byte, JWT decode/crack/forge/alg-none, SQLi/SSTI testing,
LSB stego across channels/bitplanes, QR repair, DTMF/morse audio decode,
Bacon cipher, and more) with a shared `FlagDetector` across all modules.
Prefer reusing/extending this tool over writing one-off solver scripts from
scratch when the task matches one of its existing categories.
