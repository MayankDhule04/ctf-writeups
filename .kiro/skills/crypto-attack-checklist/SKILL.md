---
name: crypto-attack-checklist
description: Walk a systematic decision tree of named cryptographic attacks (RSA, block ciphers, hashing/MAC, Diffie-Hellman, ECDSA) before writing custom cryptanalysis code. Use when facing a CTF crypto challenge involving RSA, AES/DES block ciphers, hash-based MACs, key exchange, or digital signatures.
---

## Why checklist-first

Nearly every CTF crypto challenge is an instance of a named, previously
catalogued attack (see Crypton: github.com/ashutosh1206/Crypton for the full
reference with explanations per attack). Writing custom math from scratch
before ruling out the standard attack list wastes time on problems that have
a known, often tool-automated solution.

## Step 0 — always try first, costs nothing

- Run the ciphertext/data through CyberChef's "Magic" wand — catches trivial
  stacked encodings (base64-of-hex-of-rot13, etc.) immediately.
- Check if the "encryption" is actually just an encoding (base32/58/62/85,
  URL-encoding) rather than real cryptography.

## RSA — check inputs for these conditions in order

1. **Small/known e** (e=3, e=65537 with small message) → direct root attack / low-exponent attack.
2. **p and q close in value** → Fermat's factorization.
3. **p-1 or q-1 has small prime factors** → Pollard's p-1.
4. **Same ciphertext, same n, two different e** → common modulus attack.
5. **Two different n sharing one prime factor** → common prime attack (gcd(n1, n2)).
6. **d is small** (d < N^0.25) → Wiener's attack; a variant handles d a few bits above that bound.
7. **High bits of p or a stereotyped message known** → Coppersmith's attack.
8. **Same message, same e, different n, broadcast to multiple recipients** → Hastad's broadcast attack (CRT).
9. **Two related (not identical) messages under the same n** → Franklin-Reiter related message attack.
10. **An oracle that leaks only the least significant bit of decryption** → LSB oracle attack to recover the full plaintext bit by bit.
11. **PKCS#1 v1.5 signatures with e=3** → Bleichenbacher's e=3 forgery.
12. Tool shortcut: feed `n`, `e`, and ciphertext to **RsaCtfTool** — it automates most of the above and will name which attack succeeded.

## Block ciphers (AES/DES/etc.)

1. **Identify the mode first**: ECB shows repeated ciphertext blocks for repeated plaintext blocks (visually obvious on image data); CBC/CTR/GCM don't.
2. **ECB**: byte-at-a-time decryption if you can prepend/append to a secret before encryption; detectable via repeated block fingerprinting.
3. **CBC**: bit-flipping attack if the IV or a prior block is attacker-influenced (classic "become admin" cookie attacks); padding oracle attack if the server leaks padding-validity (even via timing); byte-at-a-time decryption is also possible in CBC with more setup than ECB.
4. **CTR**: bit-flipping works directly since CTR is a stream cipher (XOR with keystream) — flipping a ciphertext bit flips the same plaintext bit.
5. **GCM / any mode with nonce**: check for nonce reuse across multiple messages — reused nonce in GCM breaks authentication entirely (the "forbidden attack") and can leak the authentication key.
6. **Unknown multi-byte XOR key** (not a real block cipher, just XOR): use **XORTool** for key-length detection and frequency-based key recovery, or do manual frequency analysis if the plaintext is known to be English/structured text (e.g. JSON, source code).

## Hashing / MACs

1. **Naive `H(key || message)` MAC construction with MD5/SHA1/SHA256**: vulnerable to **hash length-extension** — use **Hash Extender** to forge a valid MAC for `message || padding || attacker_data` without knowing the key.
2. **CBC-MAC**: two different messages can be forced to the same MAC (CBC-MAC forgery) if message lengths/structure allow it.
3. **"Password is a checksum of your input" pattern** (CRC32, Adler32, or any linear/near-linear checksum used as an equality gate): this is NOT a hash to brute-force — it's linear over GF(2) for fixed-length input and can be inverted algebraically. Hand off to the `invert-linear-checksum` skill instead of brute-forcing or guessing.

## Diffie-Hellman / ECDSA / discrete log

1. **Small subgroup confinement**: if the group order has small factors and the exchange doesn't validate the received public value is in the full-order subgroup, you can force a weak shared secret.
2. **Invalid curve point attack** (ECDH specifically): sending a point not actually on the curve can leak information about the private key if the implementation doesn't validate curve membership.
3. **ECDSA nonce (k) reuse across two signatures**: this completely breaks ECDSA — the private key is recoverable algebraically from two signatures sharing the same k. Always check this first for any ECDSA challenge presenting multiple signatures.
4. **Small/smooth group order for discrete log**: Pohlig-Hellman reduces the problem to several small discrete logs (solvable by brute force) combined via CRT. Baby-step-giant-step or Pollard's rho for a moderate-sized prime order group where Pohlig-Hellman doesn't apply.

## Confirmed-working patterns from real solves (not just theory)

- **Weakened standard primitive + known plaintext**: a custom cipher based on
  a real algorithm but deliberately weakened (e.g. ChaCha20 run for 1 round
  instead of 20) is a known-plaintext keystream-recovery target — with a
  known key/plaintext and many ciphertext samples differing only by
  nonce/counter, brute-force the counter (often small, e.g. 32-bit) to
  recover the keystream.
- **Weak Argon2/bcrypt/scrypt parameters ARE the whole vulnerability**: if a
  hash challenge has abnormally low cost parameters (e.g. Argon2 m=1024
  instead of 65536, t=2 instead of 3+), don't look for a structural
  cryptanalytic attack — just crack it directly with hashcat using the
  correct mode (`-m 10900` for Argon2) and a real wordlist (rockyou.txt).
  Python crackers are ~1000x slower than hashcat; don't hand-roll one first.
- **Bigram-to-baseN packing schemes**: ciphertext whose length is a clean
  multiple of 3 and uses only base-36 characters is characteristic of "2
  ASCII chars packed into a 3-char base-36 group" (96×96=9216 states fit in
  36³=46656). Decode each 3-char chunk as `int(chunk,36)`, then
  `c1=chr(32+val//96)`, `c2=chr(32+val%96)`.

## When nothing above fits

Only then consider: is this a genuinely novel/custom cryptosystem the
challenge invented? If so, read the actual encryption routine (source or
decompiled) fully before attempting an attack — custom ciphers are usually
breakable specifically BECAUSE of a flaw the challenge author introduced
deliberately (a weak PRNG, a reused key, a predictable IV), not because of
a generic cryptanalytic technique.
