# HSM-lite / vault-signer — Ed25519 Key Recovery via Nonce Reuse

**Flag:** `ctf7{one_nonce_two_pubkeys_zero_secrets}`

## Target

`http://91.99.207.116:16311/` — "HSM-lite signing service (Corvid Labs release
pipeline)", holding one Ed25519 key (`vault-signer`). Endpoints:

- `GET /api/keys` — lists public keys
- `POST /api/sign` — `{"key_id", "message"|"message_hex", "public_key"?}`
- `GET /api/vault/challenge` — fresh `VAULT-RELEASE` message to authorize
- `POST /api/vault/release` — `{"challenge", "signature"}` → vault contents

The service explicitly refuses to sign any message containing the literal
string `VAULT-RELEASE`, and documents that the `public_key` parameter on
`/api/sign` is an optional caller-supplied shortcut "to skip the scalar
multiplication," checked only for being a valid curve point.

## Vulnerability

Standard EdDSA (RFC 8032) computes a signature over message `M` with secret
scalar `s` and public key `A = s·B` as:

```
r = SHA512(prefix || M)        (deterministic nonce, prefix from expanded secret key)
R = r·B
h = SHA512(R || A || M) mod L
S = r + h·s mod L
signature = R || S
```

HSM-lite's "throughput optimization" lets the caller supply `A` directly
instead of the server recomputing it from its own key material. The server
does not verify that the supplied `A` actually equals `s·B` — it only checks
that it decodes to a valid point. Critically, **the nonce `r` is derived only
from the secret key and the message `M`, never from `A`.** That means signing
the *same* message twice with two different caller-chosen public keys yields
two signatures that share the same `R`, but different `S`:

```
S1 = r + H(R || A1 || M)·s  (mod L)
S2 = r + H(R || A2 || M)·s  (mod L)
```

Two linear equations, two unknowns (`r`, `s`). This is solvable directly for
`s`, the server's actual secret scalar — a full private-key recovery, not a
one-shot forgery.

This is the textbook Ed25519 "key substitution via nonce reuse" failure: any
sign API that lets a caller choose the `A` that is hashed into the signature,
while reusing a message-derived (not `A`-derived) nonce, leaks the private
key after only two signing queries.

## Exploit (see `solve.py`)

1. `GET /api/keys` → `vault-signer` public key `A_real =
   6b7ddc24f2e3fda29f93eab60207a7e6156c08605d60ceff84753dba0324fd79`.
2. Generate a throwaway Ed25519 keypair locally; take its public key `A_atk`.
3. `POST /api/sign` the *same* probe message twice:
   - once with `public_key = A_real` (or omitted — same result)
   - once with `public_key = A_atk`
   Confirm both signatures share the same `R` (first 32 bytes) — this
   confirms the nonce is independent of `A`.
4. Compute `h1 = SHA512(R||A_real||M) mod L`, `h2 = SHA512(R||A_atk||M) mod L`.
   Solve `s = (S1 - S2) * inverse(h1 - h2) mod L`.
5. Sanity-check by computing `s·B` with a pure-Python Ed25519 point
   multiplication and confirming it equals `A_real` exactly. It does.
6. `GET /api/vault/challenge` for a fresh, in-window `VAULT-RELEASE` message.
7. Forge a signature **locally** (HSM-lite is never asked to sign the literal
   `VAULT-RELEASE` string, so its policy filter is never even hit): pick a
   fresh random `r'`, compute `R' = r'·B`, `h' = SHA512(R'||A_real||M) mod L`,
   `S' = r' + h'·s mod L`.
8. Verify the forged signature locally against `A_real` with
   `cryptography`'s standard Ed25519 verifier (passes).
9. `POST /api/vault/release` with `{"challenge", "signature"}` →
   `{"ok": true, "vault": {"flag": "ctf7{one_nonce_two_pubkeys_zero_secrets}"}}`.

## Why the "never signs VAULT-RELEASE" policy didn't matter

The policy filter only inspects what HSM-lite is *asked* to sign. Because
step 4 above recovers the raw secret scalar, the attacker signs the final
`VAULT-RELEASE` challenge entirely offline, bypassing HSM-lite (and its
filter) completely for that final step. The two queries actually sent to
`/api/sign` used an innocuous probe message, never the word `VAULT-RELEASE`.

## Files

- `solve.py` — full, runnable end-to-end exploit (key recovery + forgery +
  vault release), reproducible against the live service.
- `pylibs/` — local `pip install --target` of `requests`, `cryptography`,
  `pynacl` used to run the exploit (`PYTHONPATH=./pylibs python3 solve.py`).
